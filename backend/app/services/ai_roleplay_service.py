"""
AI 角色扮演服务
支持多轮对话、角色预设、情感识别等功能
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from enum import Enum
from dataclasses import dataclass, field

from app.core.config import settings
from app.core.logging import logger

# 导入 OpenAI 服务
from app.services.openai_service import OpenAIService, CHARACTER_PRESETS


class RoleCategory(Enum):
    """角色类别"""
    BUSINESS = "business"           # 商务
    CREATIVE = "creative"           # 创意
    TECHNICAL = "technical"         # 技术
    ENTERTAINMENT = "entertainment" # 娱乐
    CUSTOM = "custom"               # 自定义


@dataclass
class Message:
    """对话消息"""
    role: str  # system, user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AICharacter:
    """AI 角色定义"""
    id: str
    name: str
    category: RoleCategory
    description: str
    avatar_url: Optional[str] = None
    system_prompt: str = ""
    personality_traits: List[str] = field(default_factory=list)
    speaking_style: str = ""
    knowledge_domains: List[str] = field(default_factory=list)
    welcome_message: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class ConversationSession:
    """对话会话"""
    id: str
    character_id: str
    user_id: Optional[str]
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息"""
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        self.updated_at = datetime.utcnow()
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """获取适合API调用的消息格式"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    def get_last_n_messages(self, n: int = 10) -> List[Message]:
        """获取最近n条消息"""
        return self.messages[-n:]


# 扩展角色预设
EXTENDED_CHARACTERS = {
    "investor": AICharacter(
        id="investor",
        name="投资大佬",
        category=RoleCategory.BUSINESS,
        description="资深风险投资家，擅长项目评估和商业分析",
        system_prompt=CHARACTER_PRESETS["investor"]["prompt"],
        personality_traits=["犀利", "直接", "专业", "经验丰富"],
        speaking_style="直截了当，一针见血，善于发现项目关键问题",
        knowledge_domains=["风险投资", "商业模式", "市场分析", "融资策略"],
        welcome_message="你好，我是投资界的老兵。把你的项目讲给我听听，我会给你最诚实的反馈。",
        model="gpt-4o",
        temperature=0.6
    ),
    "marketing_guru": AICharacter(
        id="marketing_guru",
        name="营销鬼才",
        category=RoleCategory.CREATIVE,
        description="创意营销专家，擅长 viral 营销和品牌策划",
        system_prompt=CHARACTER_PRESETS["marketing_guru"]["prompt"],
        personality_traits=["创意", "热情", "洞察力强", "网感好"],
        speaking_style="充满激情，喜欢用案例说明，紧跟潮流",
        knowledge_domains=["品牌营销", "社交媒体", "内容营销", "增长黑客"],
        welcome_message="哈喽！我是营销界的脑洞担当。想让你的产品火遍全网？来聊聊！",
        model="gpt-4o-mini",
        temperature=0.9
    ),
    "product_manager": AICharacter(
        id="product_manager",
        name="产品军师",
        category=RoleCategory.TECHNICAL,
        description="资深产品经理，擅长产品规划和用户体验设计",
        system_prompt=CHARACTER_PRESETS["product_manager"]["prompt"],
        personality_traits=["理性", "细心", "用户导向", "数据驱动"],
        speaking_style="逻辑清晰，注重细节，善于用数据说话",
        knowledge_domains=["产品设计", "用户研究", "需求分析", "项目管理"],
        welcome_message="你好，我是产品军师。让我们一起打磨你的产品，让它更懂用户。",
        model="gpt-4o-mini",
        temperature=0.7
    ),
    "storyteller": AICharacter(
        id="storyteller",
        name="品牌故事家",
        category=RoleCategory.CREATIVE,
        description="擅长用故事打动人心的品牌叙事专家",
        system_prompt=CHARACTER_PRESETS["storyteller"]["prompt"],
        personality_traits=["感性", "细腻", "富有想象力", "共情力强"],
        speaking_style="温暖动人，善用比喻和场景描述",
        knowledge_domains=["品牌故事", "叙事策略", "情感营销", "内容创作"],
        welcome_message="嗨，我是故事讲述者。每个品牌都有独特的故事，让我帮你找到它。",
        model="gpt-4o",
        temperature=0.8
    ),
    "sales_expert": AICharacter(
        id="sales_expert",
        name="销冠导师",
        category=RoleCategory.BUSINESS,
        description="销售冠军，擅长客户沟通和成交技巧",
        system_prompt=CHARACTER_PRESETS["sales_expert"]["prompt"],
        personality_traits=["自信", "亲和", "说服力", "应变能力强"],
        speaking_style="热情洋溢，善于提问引导，注重结果",
        knowledge_domains=["销售技巧", "客户心理", "谈判策略", "CRM管理"],
        welcome_message="你好！我是销冠导师。销售是一门艺术，让我教你如何让成交变得轻松自然。",
        model="gpt-4o-mini",
        temperature=0.75
    ),
    "tech_expert": AICharacter(
        id="tech_expert",
        name="技术极客",
        category=RoleCategory.TECHNICAL,
        description="全栈技术专家，熟悉各种技术栈和架构设计",
        system_prompt="""你是一位经验丰富的全栈技术专家，擅长：
- 系统架构设计
- 技术选型分析
- 代码审查和优化
- 新技术趋势评估

请用专业但易懂的方式回答技术问题，提供具体的代码示例和最佳实践。""",
        personality_traits=["严谨", "好奇心强", "开源精神", "持续学习"],
        speaking_style="技术细节清晰，善用类比解释复杂概念",
        knowledge_domains=["系统架构", "前后端开发", "云服务", "AI/ML"],
        welcome_message="Hey，我是技术极客。有什么技术难题？从架构到代码，我们都可以聊聊。",
        model="gpt-4o",
        temperature=0.6
    ),
    "startup_mentor": AICharacter(
        id="startup_mentor",
        name="创业导师",
        category=RoleCategory.BUSINESS,
        description="连续创业者，帮助初创公司从0到1",
        system_prompt="""你是一位成功的连续创业者和创业导师，曾经创办过多家公司。
你擅长：
- 创业早期策略
- 团队建设
- 融资路演
- 产品市场匹配(PMF)

请用实战经验丰富、务实的风格提供建议，分享真实的创业故事和教训。""",
        personality_traits=["务实", "坚韧", "乐观", "经验丰富"],
        speaking_style="真诚直接，喜欢用案例和经验分享",
        knowledge_domains=["创业战略", "团队管理", "融资技巧", "产品迭代"],
        welcome_message="创业者你好！创业是一场马拉松，我会陪你一起跑到终点。有什么想聊的？",
        model="gpt-4o",
        temperature=0.75
    ),
    "content_creator": AICharacter(
        id="content_creator",
        name="内容创作者",
        category=RoleCategory.CREATIVE,
        description="自媒体达人，精通各类平台内容创作",
        system_prompt="""你是一位成功的内容创作者，在多个社交媒体平台都有大量粉丝。
你擅长：
- 爆款内容创作
- 个人IP打造
- 多平台运营
- 粉丝互动策略

请提供实用、可操作的内容创作建议，紧跟平台算法变化和热点趋势。""",
        personality_traits=["创意", "网感好", "勤奋", "善于观察"],
        speaking_style="轻松活泼，善用网络语言，实用主义",
        knowledge_domains=["内容创作", "平台运营", "短视频", "直播"],
        welcome_message="嗨创作者！我是你的内容搭子。想做出爆款？从选题到发布，我们聊个透！",
        model="gpt-4o-mini",
        temperature=0.85
    ),
}


class AIRoleplayService:
    """AI 角色扮演服务"""
    
    def __init__(self):
        self.characters: Dict[str, AICharacter] = {}
        self.sessions: Dict[str, ConversationSession] = {}
        self.openai_service: Optional[OpenAIService] = None
        self._init_service()
    
    def _init_service(self):
        """初始化服务"""
        try:
            self.openai_service = OpenAIService()
            logger.info("AI Roleplay service initialized with OpenAI")
        except Exception as e:
            logger.warning(f"OpenAI service not available: {e}")
        
        # 加载预设角色
        self._load_preset_characters()
    
    def _load_preset_characters(self):
        """加载预设角色"""
        for char_id, character in EXTENDED_CHARACTERS.items():
            self.characters[char_id] = character
        logger.info(f"Loaded {len(self.characters)} preset characters")
    
    def get_character(self, character_id: str) -> Optional[AICharacter]:
        """获取角色定义"""
        return self.characters.get(character_id)
    
    def list_characters(
        self,
        category: Optional[RoleCategory] = None
    ) -> List[AICharacter]:
        """列出可用角色"""
        chars = list(self.characters.values())
        if category:
            chars = [c for c in chars if c.category == category]
        return chars
    
    def get_characters_by_category(self) -> Dict[str, List[AICharacter]]:
        """按类别分组获取角色"""
        result = {}
        for cat in RoleCategory:
            chars = self.list_characters(category=cat)
            if chars:
                result[cat.value] = chars
        return result
    
    def create_custom_character(
        self,
        name: str,
        description: str,
        system_prompt: str,
        category: RoleCategory = RoleCategory.CUSTOM,
        **kwargs
    ) -> AICharacter:
        """创建自定义角色"""
        char_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        character = AICharacter(
            id=char_id,
            name=name,
            category=category,
            description=description,
            system_prompt=system_prompt,
            **kwargs
        )
        
        self.characters[char_id] = character
        return character
    
    def create_session(
        self,
        character_id: str,
        user_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Optional[ConversationSession]:
        """创建对话会话"""
        character = self.get_character(character_id)
        if not character:
            return None
        
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        session = ConversationSession(
            id=session_id,
            character_id=character_id,
            user_id=user_id,
            metadata={
                "context": context or {},
                "character_name": character.name
            }
        )
        
        # 添加系统提示词
        session.add_message("system", character.system_prompt)
        
        # 如果有欢迎消息，添加为assistant的第一条消息
        if character.welcome_message:
            session.add_message("assistant", character.welcome_message)
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    async def send_message(
        self,
        session_id: str,
        message: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        发送消息并获取回复
        
        Args:
            session_id: 会话ID
            message: 用户消息
            stream: 是否流式返回
            
        Returns:
            包含回复和会话信息的字典
        """
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        if not self.openai_service:
            return {"error": "AI service not available"}
        
        character = self.get_character(session.character_id)
        if not character:
            return {"error": "Character not found"}
        
        # 添加用户消息
        session.add_message("user", message)
        
        try:
            # 调用 OpenAI API
            # 只取最近的消息以保持上下文合理
            messages = session.get_messages_for_api()
            
            response = await self.openai_service.chat_completion(
                messages=messages,
                model=character.model,
                temperature=character.temperature,
                max_tokens=character.max_tokens
            )
            
            # 添加助手回复
            session.add_message("assistant", response)
            
            return {
                "session_id": session_id,
                "character_id": session.character_id,
                "character_name": character.name,
                "user_message": message,
                "assistant_message": response,
                "timestamp": datetime.utcnow().isoformat(),
                "message_count": len(session.messages)
            }
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return {"error": f"Failed to get AI response: {str(e)}"}
    
    async def send_message_stream(
        self,
        session_id: str,
        message: str
    ) -> AsyncGenerator[str, None]:
        """
        流式发送消息（用于打字机效果）
        
        注意：这需要 OpenAI 的流式 API 支持
        """
        # TODO: 实现流式响应
        result = await self.send_message(session_id, message)
        if "error" in result:
            yield json.dumps({"error": result["error"]})
        else:
            yield json.dumps({
                "type": "content",
                "content": result["assistant_message"]
            })
    
    def clear_session_history(self, session_id: str) -> bool:
        """清空会话历史（保留系统提示）"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # 保留系统消息
        system_msg = session.messages[0] if session.messages else None
        session.messages = [system_msg] if system_msg else []
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_history(self, session_id: str) -> Optional[List[Message]]:
        """获取会话历史"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.messages
    
    def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """获取用户的所有会话"""
        return [
            s for s in self.sessions.values()
            if s.user_id == user_id
        ]


# 全局服务实例
ai_roleplay_service = AIRoleplayService()


# 便捷函数
async def chat_with_character(
    character_id: str,
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    与AI角色对话的便捷函数
    
    Args:
        character_id: 角色ID
        message: 用户消息
        session_id: 现有会话ID（可选）
        user_id: 用户ID（可选）
        
    Returns:
        对话结果
    """
    service = ai_roleplay_service
    
    # 如果没有会话ID，创建新会话
    if not session_id:
        session = service.create_session(character_id, user_id)
        if not session:
            return {"error": f"Failed to create session for character {character_id}"}
        session_id = session.id
        
        # 如果有欢迎消息，先返回欢迎消息
        character = service.get_character(character_id)
        if character and character.welcome_message:
            return {
                "session_id": session_id,
                "character_id": character_id,
                "character_name": character.name,
                "assistant_message": character.welcome_message,
                "is_welcome": True
            }
    
    # 发送消息
    return await service.send_message(session_id, message)


def get_available_characters() -> List[Dict[str, Any]]:
    """获取可用角色列表"""
    service = ai_roleplay_service
    characters = service.list_characters()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "category": c.category.value,
            "description": c.description,
            "personality_traits": c.personality_traits,
            "speaking_style": c.speaking_style,
            "welcome_message": c.welcome_message
        }
        for c in characters
    ]
