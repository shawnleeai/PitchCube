"""
AI 角色扮演 API
支持多角色对话、场景化交流
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.ai_roleplay_service import (
    ai_roleplay_service,
    chat_with_character,
    get_available_characters,
    ConversationSession,
    RoleCategory
)

router = APIRouter()

# WebSocket 连接管理
class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


# ============== Pydantic 模型 ==============

class CharacterInfo(BaseModel):
    id: str
    name: str
    category: str
    description: str
    personality_traits: List[str]
    speaking_style: str
    knowledge_domains: List[str]
    welcome_message: str


class CharacterCategory(BaseModel):
    id: str
    name: str
    description: str
    characters: List[CharacterInfo]


class CreateSessionRequest(BaseModel):
    character_id: str = Field(..., description="角色ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="对话上下文信息")


class CreateSessionResponse(BaseModel):
    session_id: str
    character_id: str
    character_name: str
    welcome_message: str
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息")
    session_id: Optional[str] = Field(default=None, description="会话ID（首次对话可不传）")
    character_id: Optional[str] = Field(default=None, description="角色ID（新会话时需要）")


class ChatResponse(BaseModel):
    session_id: str
    character_id: str
    character_name: str
    user_message: str
    assistant_message: str
    timestamp: datetime
    message_count: int


class SessionHistoryResponse(BaseModel):
    session_id: str
    character_id: str
    character_name: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class CustomCharacterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    description: str = Field(..., max_length=500, description="角色描述")
    system_prompt: str = Field(..., min_length=10, max_length=4000, description="系统提示词")
    personality_traits: List[str] = Field(default_factory=list, description="性格特点")
    speaking_style: str = Field(default="", description="说话风格")
    knowledge_domains: List[str] = Field(default_factory=list, description="知识领域")
    welcome_message: str = Field(default="", description="欢迎语")
    model: str = Field(default="gpt-4o-mini", description="使用的模型")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")


# ============== API 路由 ==============

@router.get("/characters", response_model=List[CharacterInfo])
async def list_characters(category: Optional[str] = None):
    """
    获取可用的AI角色列表
    
    Query 参数:
    - category: 类别过滤 (business/creative/technical/entertainment)
    """
    characters = ai_roleplay_service.list_characters()
    
    if category:
        try:
            cat_enum = RoleCategory(category)
            characters = [c for c in characters if c.category == cat_enum]
        except ValueError:
            pass
    
    return [
        CharacterInfo(
            id=c.id,
            name=c.name,
            category=c.category.value,
            description=c.description,
            personality_traits=c.personality_traits,
            speaking_style=c.speaking_style,
            knowledge_domains=c.knowledge_domains,
            welcome_message=c.welcome_message
        )
        for c in characters
    ]


@router.get("/characters/categories", response_model=List[CharacterCategory])
async def list_characters_by_category():
    """按类别分组获取角色"""
    chars_by_cat = ai_roleplay_service.get_characters_by_category()
    
    category_names = {
        "business": "商务专家",
        "creative": "创意大师",
        "technical": "技术专家",
        "entertainment": "娱乐互动",
        "custom": "自定义"
    }
    
    category_descriptions = {
        "business": "商务、销售、投资领域的专业顾问",
        "creative": "营销、内容创作、品牌策划专家",
        "technical": "技术架构、产品开发专业指导",
        "entertainment": "轻松娱乐、陪伴对话",
        "custom": "用户自定义角色"
    }
    
    result = []
    for cat_id, characters in chars_by_cat.items():
        result.append(CharacterCategory(
            id=cat_id,
            name=category_names.get(cat_id, cat_id),
            description=category_descriptions.get(cat_id, ""),
            characters=[
                CharacterInfo(
                    id=c.id,
                    name=c.name,
                    category=c.category.value,
                    description=c.description,
                    personality_traits=c.personality_traits,
                    speaking_style=c.speaking_style,
                    knowledge_domains=c.knowledge_domains,
                    welcome_message=c.welcome_message
                )
                for c in characters
            ]
        ))
    
    return result


@router.get("/characters/{character_id}", response_model=CharacterInfo)
async def get_character(character_id: str):
    """获取单个角色详情"""
    character = ai_roleplay_service.get_character(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    
    return CharacterInfo(
        id=character.id,
        name=character.name,
        category=character.category.value,
        description=character.description,
        personality_traits=character.personality_traits,
        speaking_style=character.speaking_style,
        knowledge_domains=character.knowledge_domains,
        welcome_message=character.welcome_message
    )


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    创建新的对话会话
    
    创建成功后会返回 welcome_message，可直接展示给用户
    """
    session = ai_roleplay_service.create_session(
        character_id=request.character_id,
        user_id=request.user_id,
        context=request.context
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {request.character_id} not found"
        )
    
    character = ai_roleplay_service.get_character(request.character_id)
    
    return CreateSessionResponse(
        session_id=session.id,
        character_id=request.character_id,
        character_name=character.name,
        welcome_message=character.welcome_message if character else "",
        created_at=session.created_at
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    与AI角色对话
    
    如果提供了 session_id，继续现有对话；
    如果没有 session_id 但提供了 character_id，自动创建新会话。
    """
    if not request.session_id and not request.character_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either session_id or character_id must be provided"
        )
    
    # 如果没有 session_id，创建新会话
    session_id = request.session_id
    character_id = request.character_id
    
    if not session_id:
        session = ai_roleplay_service.create_session(character_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found"
            )
        session_id = session.id
    
    # 发送消息
    result = await ai_roleplay_service.send_message(session_id, request.message)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return ChatResponse(
        session_id=result["session_id"],
        character_id=result["character_id"],
        character_name=result["character_name"],
        user_message=result["user_message"],
        assistant_message=result["assistant_message"],
        timestamp=datetime.fromisoformat(result["timestamp"]),
        message_count=result["message_count"]
    )


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """获取会话历史记录"""
    session = ai_roleplay_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    character = ai_roleplay_service.get_character(session.character_id)
    
    return SessionHistoryResponse(
        session_id=session.id,
        character_id=session.character_id,
        character_name=character.name if character else "Unknown",
        messages=[
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.messages
        ],
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """清空会话历史（保留角色设定）"""
    success = ai_roleplay_service.clear_session_history(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return {"message": "Session history cleared", "session_id": session_id}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = ai_roleplay_service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return {"message": "Session deleted", "session_id": session_id}


@router.post("/characters/custom", response_model=CharacterInfo)
async def create_custom_character(request: CustomCharacterRequest):
    """
    创建自定义角色
    
    允许用户创建自己的AI角色，设置独特的性格和功能
    """
    try:
        category = RoleCategory.CUSTOM
    except:
        category = RoleCategory.CUSTOM
    
    character = ai_roleplay_service.create_custom_character(
        name=request.name,
        description=request.description,
        system_prompt=request.system_prompt,
        category=category,
        personality_traits=request.personality_traits,
        speaking_style=request.speaking_style,
        knowledge_domains=request.knowledge_domains,
        welcome_message=request.welcome_message,
        model=request.model,
        temperature=request.temperature
    )
    
    return CharacterInfo(
        id=character.id,
        name=character.name,
        category=character.category.value,
        description=character.description,
        personality_traits=character.personality_traits,
        speaking_style=character.speaking_style,
        knowledge_domains=character.knowledge_domains,
        welcome_message=character.welcome_message
    )


# ============== WebSocket 实时对话 ==============

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket 实时对话
    
    支持打字机效果的实时回复
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            
            # 发送消息并获取回复
            result = await ai_roleplay_service.send_message(session_id, user_message)
            
            if "error" in result:
                await manager.send_message(
                    json.dumps({"type": "error", "message": result["error"]}),
                    session_id
                )
            else:
                # 模拟打字机效果，逐字发送
                response = result["assistant_message"]
                
                # 先发送开始标记
                await manager.send_message(
                    json.dumps({
                        "type": "start",
                        "character_name": result["character_name"]
                    }),
                    session_id
                )
                
                # 逐段发送（按句子分割）
                import re
                sentences = re.split(r'([。！？.!?]+)', response)
                current_text = ""
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
                    current_text += sentence + punctuation
                    
                    await manager.send_message(
                        json.dumps({
                            "type": "chunk",
                            "content": sentence + punctuation,
                            "full_text": current_text
                        }),
                        session_id
                    )
                    
                    # 添加短暂延迟模拟打字效果
                    import asyncio
                    await asyncio.sleep(0.1)
                
                # 发送完成标记
                await manager.send_message(
                    json.dumps({
                        "type": "end",
                        "full_text": response,
                        "timestamp": result["timestamp"]
                    }),
                    session_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


@router.get("/health")
async def health_check():
    """角色扮演服务健康检查"""
    characters = ai_roleplay_service.list_characters()
    
    return {
        "available": len(characters) > 0,
        "character_count": len(characters),
        "categories": list(set(c.category.value for c in characters)),
        "openai_configured": settings.OPENAI_API_KEY is not None
    }
