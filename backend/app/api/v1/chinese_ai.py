"""
国产 AI 服务统一 API
支持 Minimax (稀宇科技) 和 StepFun (阶跃星辰)
方便比较和切换不同的国产 AI 服务
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.ai_service_manager import ai_service_manager
from app.services.minimax_service import MinimaxLLM, MinimaxTTS
from app.services.stepfun_service import StepFunLLM

router = APIRouter()


# ============== Pydantic 模型 ==============

class TextGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="提示词")
    provider: str = Field(default="auto", description="提供商: auto/stepfun/minimax")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2000, ge=100, le=4000)


class TextGenerationResponse(BaseModel):
    provider: str
    content: str
    model: str
    timestamp: datetime


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="文本内容")
    voice: str = Field(..., description="音色ID")
    provider: str = Field(default="auto", description="提供商: auto/stepfun/minimax")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class TTSVoice(BaseModel):
    id: str
    name: str
    gender: str
    style: str
    description: str
    provider: str


class ProviderComparison(BaseModel):
    provider: str
    name: str
    description: str
    available: bool
    llm_models: List[str]
    tts_voices_count: int
    features: List[str]
    pricing_hint: str


class CopywritingRequest(BaseModel):
    product_name: str = Field(..., description="产品名称")
    product_description: str = Field(..., description="产品描述")
    target_audience: str = Field(default="", description="目标受众")
    style: str = Field(default="professional", description="风格")
    provider: str = Field(default="auto", description="提供商: auto/stepfun/minimax/openai")


class VideoScriptRequest(BaseModel):
    product_name: str = Field(..., description="产品名称")
    product_description: str = Field(..., description="产品描述")
    key_features: List[str] = Field(default_factory=list, description="核心功能")
    style: str = Field(default="professional", description="脚本风格")
    duration: int = Field(default=60, ge=30, le=180, description="视频时长(秒)")
    platform: str = Field(default="youtube", description="目标平台")
    provider: str = Field(default="auto", description="提供商: auto/stepfun/minimax/openai")


# ============== API 路由 ==============

@router.get("/providers", response_model=List[ProviderComparison])
async def list_chinese_providers():
    """
    获取国产 AI 服务提供商对比
    
    比较 StepFun (阶跃星辰) 和 Minimax (稀宇科技)
    """
    providers = []
    
    # StepFun
    stepfun_available = ai_service_manager.is_service_available("stepfun")
    providers.append(ProviderComparison(
        provider="stepfun",
        name="阶跃星辰 (StepFun)",
        description="国内领先的通用大模型公司，语音合成质量高",
        available=stepfun_available,
        llm_models=["step-1-8k", "step-1-32k", "step-1-128k", "step-1-256k"],
        tts_voices_count=16,
        features=["文本生成", "语音合成", "视频脚本生成"],
        pricing_hint="文本: ¥0.015/千token, 语音: ¥0.015/千字"
    ))
    
    # Minimax
    minimax_available = ai_service_manager.is_service_available("minimax")
    providers.append(ProviderComparison(
        provider="minimax",
        name="稀宇科技 (Minimax)",
        description="国内领先的 AI 公司，abab 系列大模型",
        available=minimax_available,
        llm_models=["abab6.5s-chat", "abab6.5-chat", "abab6-chat", "abab5.5s-chat"],
        tts_voices_count=14,
        features=["文本生成", "语音合成", "向量服务"],
        pricing_hint="文本: ¥0.01-0.03/千token, 语音: ¥0.02/千字"
    ))
    
    return providers


@router.post("/chat", response_model=TextGenerationResponse)
async def chat_completion(request: TextGenerationRequest):
    """
    国产 AI 对话生成
    
    支持 StepFun 和 Minimax，可指定 provider 或使用 auto 自动选择
    """
    if request.provider == "auto":
        if ai_service_manager.is_service_available("minimax"):
            request.provider = "minimax"
        elif ai_service_manager.is_service_available("stepfun"):
            request.provider = "stepfun"
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No Chinese AI service configured"
            )
    
    try:
        content = await ai_service_manager.generate_text(
            prompt=request.prompt,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        model = "unknown"
        if request.provider == "stepfun":
            model = settings.STEPFUN_LLM_MODEL
        elif request.provider == "minimax":
            model = settings.MINIMAX_LLM_MODEL
        
        return TextGenerationResponse(
            provider=request.provider,
            content=content,
            model=model,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Chinese AI chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/copywriting")
async def generate_copywriting(request: CopywritingRequest):
    """
    使用国产 AI 生成营销文案
    
    支持 StepFun 和 Minimax
    """
    try:
        result = await ai_service_manager.generate_copywriting(
            product_name=request.product_name,
            product_description=request.product_description,
            style=request.style,
            provider=request.provider
        )
        
        return {
            "provider": request.provider if request.provider != "auto" else "minimax/stepfun",
            "content": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Copywriting generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/video-script")
async def generate_video_script(request: VideoScriptRequest):
    """
    使用国产 AI 生成视频脚本
    
    支持 StepFun 和 Minimax
    """
    try:
        if request.provider == "auto":
            if ai_service_manager.is_service_available("minimax"):
                request.provider = "minimax"
            elif ai_service_manager.is_service_available("stepfun"):
                request.provider = "stepfun"
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No Chinese AI service configured"
                )
        
        if request.provider == "minimax":
            service = MinimaxLLM()
            result = await service.generate_video_script(
                product_name=request.product_name,
                product_description=request.product_description,
                key_features=request.key_features,
                style=request.style,
                duration=request.duration,
                platform=request.platform
            )
        elif request.provider == "stepfun":
            service = StepFunLLM()
            result = await service.generate_video_script(
                product_name=request.product_name,
                product_description=request.product_description,
                key_features=request.key_features,
                style=request.style,
                duration=request.duration,
                platform=request.platform
            )
        else:
            raise ValueError(f"Provider {request.provider} not supported")
        
        return {
            "provider": request.provider,
            "script": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Video script generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============== TTS 路由 ==============

@router.get("/tts/voices", response_model=List[TTSVoice])
async def list_tts_voices(provider: Optional[str] = None):
    """
    获取国产 TTS 可用音色
    
    支持 StepFun 和 Minimax 的音色
    """
    voices = []
    
    # StepFun 音色
    if provider in [None, "stepfun"] and ai_service_manager.is_service_available("stepfun"):
        stepfun_voices = [
            {"id": "zhengpaiqingnian", "name": "正派青年", "gender": "male", "style": "professional", "description": "适合商务路演、专业解说"},
            {"id": "ganliannvsheng", "name": "干练女声", "gender": "female", "style": "professional", "description": "专业干练，适合正式场合"},
            {"id": "cixingnansheng", "name": "磁性男声", "gender": "male", "style": "professional", "description": "低沉磁性，适合品牌宣传"},
            {"id": "ruyananshi", "name": "儒雅男士", "gender": "male", "style": "professional", "description": "儒雅稳重，适合文化内容"},
            {"id": "linjiajiejie", "name": "邻家姐姐", "gender": "female", "style": "casual", "description": "亲切自然，适合轻松场景"},
            {"id": "wenrounansheng", "name": "温柔男声", "gender": "male", "style": "casual", "description": "温柔体贴，适合情感内容"},
            {"id": "qinhenvsheng", "name": "亲和女声", "gender": "female", "style": "casual", "description": "亲和力强，适合客服场景"},
            {"id": "yuanqishaonv", "name": "元气少女", "gender": "female", "style": "energetic", "description": "活力四射，适合年轻产品"},
            {"id": "yuanqinansheng", "name": "元气男声", "gender": "male", "style": "energetic", "description": "元气满满，适合活泼内容"},
            {"id": "huolinvsheng", "name": "活力女声", "gender": "female", "style": "energetic", "description": "活力热情，适合营销场景"},
        ]
        for v in stepfun_voices:
            voices.append(TTSVoice(provider="stepfun", **v))
    
    # Minimax 音色
    if provider in [None, "minimax"] and ai_service_manager.is_service_available("minimax"):
        minimax_voices = [
            {"id": "male-qn-qingse", "name": "青涩青年", "gender": "male", "style": "youth", "description": "青涩自然的男声"},
            {"id": "male-qn-jingying", "name": "精英男士", "gender": "male", "style": "professional", "description": "专业稳重的男声"},
            {"id": "male-qn-badao", "name": "霸道总裁", "gender": "male", "style": "authoritative", "description": "霸气有磁性的男声"},
            {"id": "male-qn-daxuesheng", "name": "阳光大学生", "gender": "male", "style": "youth", "description": "阳光活力的男声"},
            {"id": "female-shaonv", "name": "少女", "gender": "female", "style": "youth", "description": "甜美可爱的女声"},
            {"id": "female-yujie", "name": "御姐", "gender": "female", "style": "mature", "description": "成熟魅力的女声"},
            {"id": "female-chengshu", "name": "成熟女性", "gender": "female", "style": "professional", "description": "知性专业的女声"},
            {"id": "female-tianmei", "name": "甜美女孩", "gender": "female", "style": "sweet", "description": "甜美温柔的女声"},
            {"id": "presenter_male", "name": "男主持人", "gender": "male", "style": "broadcast", "description": "标准主持腔男声"},
            {"id": "presenter_female", "name": "女主持人", "gender": "female", "style": "broadcast", "description": "标准主持腔女声"},
        ]
        for v in minimax_voices:
            voices.append(TTSVoice(provider="minimax", **v))
    
    return voices


@router.post("/tts/generate")
async def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks):
    """
    国产 AI 语音合成
    
    支持 StepFun 和 Minimax，可指定 provider 或使用 auto 自动选择
    """
    try:
        audio_data = await ai_service_manager.generate_speech(
            text=request.text,
            voice=request.voice,
            provider=request.provider,
            speed=request.speed
        )
        
        # 保存音频文件
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        output_dir = Path("generated/tts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"chinese_tts_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.mp3"
        filepath = output_dir / filename
        filepath.write_bytes(audio_data)
        
        return {
            "provider": request.provider if request.provider != "auto" else "minimax/stepfun",
            "voice": request.voice,
            "audio_url": f"/download/tts/{filename}",
            "duration_estimate": len(request.text) / 4,  # 粗略估计
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health")
async def health_check():
    """
    国产 AI 服务健康检查
    
    检查 StepFun 和 Minimax 的配置状态
    """
    return {
        "services": {
            "stepfun": {
                "configured": ai_service_manager.is_service_available("stepfun"),
                "api_key_set": settings.STEPFUN_API_KEY is not None,
            },
            "minimax": {
                "configured": ai_service_manager.is_service_available("minimax"),
                "api_key_set": settings.MINIMAX_API_KEY is not None,
                "group_id_set": settings.MINIMAX_GROUP_ID is not None,
            }
        },
        "available_providers": [
            p for p in ["stepfun", "minimax"] 
            if ai_service_manager.is_service_available(p)
        ]
    }
