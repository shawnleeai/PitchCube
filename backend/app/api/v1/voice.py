"""
语音解说员 API - 使用阶跃星辰 StepFun TTS
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.db.mongodb import db

# 尝试导入 StepFun TTS Skill
try:
    import sys

    sys.path.insert(
        0,
        str(
            Path(__file__).parent.parent.parent.parent.parent / "skills" / "stepfun-tts"
        ),
    )
    from stepfun_tts import (
        StepFunTTS,
        Voice,
        get_voice_recommendations,
        TTSError,
        VoiceNotFoundError,
    )

    STEPFUN_AVAILABLE = True
except ImportError:
    STEPFUN_AVAILABLE = False
    logger.warning("StepFun TTS Skill not available, voice generation will be disabled")

router = APIRouter()

# 注意：已迁移到 MongoDB，保留此变量用于向后兼容的演示模式
_voice_tasks_cache: dict = {}


# ============ 数据库操作辅助函数 ============


async def _save_voice_task(task_data: dict):
    """保存语音任务到数据库"""
    if db.connected:
        try:
            await db.db.voice_generations.insert_one(task_data)
            logger.info(f"语音生成任务已保存到数据库: {task_data['id']}")
        except Exception as e:
            logger.warning(f"保存到数据库失败，使用内存缓存: {e}")
            _voice_tasks_cache[task_data["id"]] = task_data
    else:
        _voice_tasks_cache[task_data["id"]] = task_data


async def _update_voice_task(generation_id: str, update_data: dict):
    """更新语音任务状态"""
    if db.connected:
        try:
            await db.db.voice_generations.update_one(
                {"id": generation_id}, {"$set": update_data}
            )
        except Exception as e:
            logger.warning(f"更新数据库失败: {e}")
            if generation_id in _voice_tasks_cache:
                _voice_tasks_cache[generation_id].update(update_data)
    else:
        if generation_id in _voice_tasks_cache:
            _voice_tasks_cache[generation_id].update(update_data)


async def _get_voice_task(generation_id: str) -> Optional[dict]:
    """获取语音任务"""
    if db.connected:
        try:
            task = await db.db.voice_generations.find_one({"id": generation_id})
            if task:
                task.pop("_id", None)
                return task
        except Exception as e:
            logger.warning(f"数据库查询失败: {e}")
    return _voice_tasks_cache.get(generation_id)


class VoiceGenerationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="要转换的文本")
    voice_style: str = Field(
        default="professional", description="风格: professional/casual/energetic"
    )
    voice_gender: Optional[str] = Field(
        default="female", description="性别: male/female"
    )
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")
    use_cache: bool = Field(default=True, description="是否使用缓存")


class VoiceGenerationResponse(BaseModel):
    id: str
    status: str
    text: str
    voice_id: str
    voice_name: str
    audio_url: Optional[str] = None
    duration_estimate: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str
    style: str
    description: str
    tags: List[str]


class VoiceRecommendation(BaseModel):
    scenario: str
    scenario_name: str
    description: str
    recommended_voices: List[VoiceInfo]


# 风格映射
STYLE_MAPPING = {
    "professional": "专业商务",
    "casual": "亲切自然",
    "energetic": "活力热情",
}


def get_tts_service() -> Optional[StepFunTTS]:
    """获取 TTS 服务实例"""
    if not STEPFUN_AVAILABLE:
        return None

    api_key = (
        settings.STEPFUN_API_KEY
        if hasattr(settings, "STEPFUN_API_KEY")
        else os.getenv("STEPFUN_API_KEY")
    )
    if not api_key:
        return None

    try:
        return StepFunTTS(api_key=api_key, cache_dir="./generated/voice_cache")
    except Exception as e:
        logger.error(f"Failed to initialize StepFun TTS: {e}")
        return None


@router.get("/voices", response_model=List[VoiceInfo])
async def list_voices(style: Optional[str] = None, gender: Optional[str] = None):
    """
    获取可用音色列表

    Query 参数:
    - style: 风格过滤 (professional/casual/energetic)
    - gender: 性别过滤 (male/female)
    """
    if not STEPFUN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice service is not available. Please install stepfun-tts skill.",
        )

    tts = get_tts_service()
    if not tts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="StepFun API key not configured",
        )

    voices = tts.get_voices(style=style, gender=gender)
    return [
        VoiceInfo(
            id=v.id,
            name=v.name,
            gender=v.gender,
            style=v.style,
            description=v.description,
            tags=v.tags,
        )
        for v in voices
    ]


@router.get("/recommendations", response_model=List[VoiceRecommendation])
async def get_recommendations():
    """获取场景化音色推荐"""
    if not STEPFUN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice service is not available",
        )

    scenarios = [
        ("business", "商务路演", "适合正式路演、投资人 presentation"),
        ("product", "产品介绍", "适合产品演示、功能讲解"),
        ("marketing", "营销宣传", "适合推广视频、社交媒体"),
        ("story", "故事讲述", "适合品牌故事、情感内容"),
        ("news", "新闻播报", "适合资讯播报、正式公告"),
        ("casual", "轻松休闲", "适合轻松场景、日常对话"),
    ]

    recommendations = []
    for scenario_id, scenario_name, description in scenarios:
        voices = get_voice_recommendations(scenario_id)
        recommendations.append(
            VoiceRecommendation(
                scenario=scenario_id,
                scenario_name=scenario_name,
                description=description,
                recommended_voices=[
                    VoiceInfo(
                        id=v.id,
                        name=v.name,
                        gender=v.gender,
                        style=v.style,
                        description=v.description,
                        tags=v.tags,
                    )
                    for v in voices
                ],
            )
        )

    return recommendations


@router.post(
    "/generate",
    response_model=VoiceGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_voice(
    request: VoiceGenerationRequest, background_tasks: BackgroundTasks
):
    """
    生成语音

    提交生成任务，返回任务ID，通过 /generations/{id} 查询进度
    """
    if not STEPFUN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice service is not available. Please install stepfun-tts skill.",
        )

    tts = get_tts_service()
    if not tts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="StepFun API key not configured. Please set STEPFUN_API_KEY.",
        )

    # 生成任务ID
    generation_id = (
        f"voice_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    )

    # 根据风格和性别选择音色
    voice = tts.get_voice_by_style(request.voice_style, request.voice_gender)
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No voice found for style '{request.voice_style}' and gender '{request.voice_gender}'",
        )

    # 估算时长
    duration = StepFunTTS.estimate_duration(request.text, request.speed)

    # 准备任务数据
    task_data = {
        "id": generation_id,
        "status": "processing",
        "text": request.text,
        "voice_id": voice.id,
        "voice_name": voice.name,
        "voice_style": request.voice_style,
        "voice_gender": request.voice_gender,
        "speed": request.speed,
        "audio_url": None,
        "duration_estimate": duration,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
    }

    # 保存到数据库
    await _save_voice_task(task_data)

    logger.info(f"Voice generation started: {generation_id}, voice={voice.id}")

    # 后台执行生成
    background_tasks.add_task(
        process_voice_generation, generation_id, request, voice.id
    )

    return VoiceGenerationResponse(
        id=generation_id,
        status="processing",
        text=request.text,
        voice_id=voice.id,
        voice_name=voice.name,
        duration_estimate=duration,
        created_at=datetime.utcnow(),
    )


async def process_voice_generation(
    generation_id: str, request: VoiceGenerationRequest, voice_id: str
):
    """后台处理语音生成"""
    try:
        tts = get_tts_service()
        if not tts:
            raise Exception("TTS service not available")

        # 生成语音
        audio_data = await tts.generate(
            text=request.text,
            voice=voice_id,
            speed=request.speed,
            use_cache=request.use_cache,
        )

        # 保存音频文件
        filename = f"{generation_id}.mp3"
        output_dir = Path("generated")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        filepath.write_bytes(audio_data)

        # 更新任务状态
        _voice_tasks_cache[generation_id].update(
            {
                "status": "completed",
                "audio_url": f"/download/{filename}",
                "completed_at": datetime.utcnow(),
            }
        )

        logger.info(f"Voice generation completed: {generation_id}")

    except VoiceNotFoundError as e:
        logger.error(f"Voice not found: {e}")
        generation_tasks[generation_id].update(
            {
                "status": "failed",
                "error_message": f"Voice not found: {str(e)}",
                "completed_at": datetime.utcnow(),
            }
        )
    except TTSError as e:
        logger.error(f"TTS error for {generation_id}: {e}")
        generation_tasks[generation_id].update(
            {
                "status": "failed",
                "error_message": f"语音生成失败: {str(e)}",
                "completed_at": datetime.utcnow(),
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error for {generation_id}: {e}")
        generation_tasks[generation_id].update(
            {
                "status": "failed",
                "error_message": f"服务器错误: {str(e)}",
                "completed_at": datetime.utcnow(),
            }
        )


@router.get("/generations/{generation_id}", response_model=VoiceGenerationResponse)
async def get_generation_status(generation_id: str):
    """查询生成任务状态"""
    task = _voice_tasks_cache.get(generation_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation task {generation_id} not found",
        )

    return VoiceGenerationResponse(**task)


@router.get("/generations", response_model=List[VoiceGenerationResponse])
async def list_generations(limit: int = 10, offset: int = 0):
    """获取生成历史列表"""
    tasks = list(_voice_tasks_cache.values())
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    paginated = tasks[offset : offset + limit]
    return [VoiceGenerationResponse(**task) for task in paginated]


class VoicePreviewRequest(BaseModel):
    text: str = Field(
        default="欢迎使用 PitchCube 路演魔方，让创意变成现实。",
        min_length=1,
        max_length=200,
    )
    voice_id: str = "zhengpaiqingnian"


@router.post("/preview")
async def preview_voice(request: VoicePreviewRequest):
    """
    快速预览音色效果（用于试听）

    限制200字以内，快速返回结果
    """
    if not STEPFUN_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice service is not available",
        )

    tts = get_tts_service()
    if not tts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="StepFun API key not configured",
        )

    try:
        # 直接生成，不经过任务队列
        audio_data = await tts.generate(
            text=request.text, voice=request.voice_id, use_cache=True
        )

        # 保存临时文件
        preview_id = f"preview_{uuid.uuid4().hex[:8]}"
        filename = f"{preview_id}.mp3"

        output_dir = Path("generated")
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        filepath.write_bytes(audio_data)

        duration = StepFunTTS.estimate_duration(request.text)

        return {
            "preview_id": preview_id,
            "audio_url": f"/download/{filename}",
            "duration": duration,
            "text": request.text,
            "voice_id": request.voice_id,
        }

    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview generation failed: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """语音服务健康检查"""
    tts = get_tts_service()
    return {
        "available": STEPFUN_AVAILABLE and tts is not None,
        "skill_loaded": STEPFUN_AVAILABLE,
        "api_configured": tts is not None,
    }
