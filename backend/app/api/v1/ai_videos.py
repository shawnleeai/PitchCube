"""
AI 视频生成 API
支持 Replicate 和 Runway ML
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.ai_service_manager import ai_service_manager
from app.services.video_generation_service import video_service_manager, VideoProvider
from app.db.mongodb import db

router = APIRouter()

# 注意：已迁移到 MongoDB，保留此变量用于向后兼容的演示模式
_video_tasks_cache: dict = {}


class TextToVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000, description="视频描述")
    provider: str = Field(default="replicate", description="提供商: replicate/runway")
    model: str = Field(default="wan-t2v", description="模型名称")
    duration: int = Field(default=5, ge=3, le=10, description="视频时长（秒）")
    resolution: str = Field(default="720p", description="分辨率: 720p/1080p")
    aspect_ratio: str = Field(default="16:9", description="宽高比: 16:9/9:16/1:1")
    negative_prompt: str = Field(
        default="blur, distortion, low quality", description="负面提示词"
    )


class ImageToVideoRequest(BaseModel):
    image_url: str = Field(..., description="输入图像URL")
    prompt: str = Field(default="", description="运动描述（可选）")
    provider: str = Field(default="replicate", description="提供商: replicate/runway")
    model: str = Field(default="wan-i2v", description="模型名称")
    duration: int = Field(default=5, ge=3, le=10, description="视频时长（秒）")
    motion_strength: int = Field(default=127, ge=0, le=255, description="运动强度")


class VideoGenerationResponse(BaseModel):
    id: str
    status: str  # processing, completed, failed
    prompt: Optional[str] = None
    provider: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: int
    resolution: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    estimated_time: int = 120  # 预估时间（秒）


class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    available: bool
    models: List[Dict[str, Any]]
    features: List[str]
    pricing_hint: str


class VideoTemplate(BaseModel):
    id: str
    name: str
    description: str
    prompt_template: str
    duration: int
    style_tags: List[str]


# ============ 数据库操作辅助函数 ============


async def _save_video_task(task_data: dict):
    """保存视频任务到数据库"""
    if db.connected:
        try:
            await db.db.video_generations.insert_one(task_data)
            logger.info(f"视频生成任务已保存到数据库: {task_data['id']}")
        except Exception as e:
            logger.warning(f"保存到数据库失败，使用内存缓存: {e}")
            _video_tasks_cache[task_data["id"]] = task_data
    else:
        _video_tasks_cache[task_data["id"]] = task_data


async def _update_video_task(task_id: str, update_data: dict):
    """更新视频任务状态"""
    if db.connected:
        try:
            await db.db.video_generations.update_one(
                {"id": task_id}, {"$set": update_data}
            )
        except Exception as e:
            logger.warning(f"更新数据库失败: {e}")
            if task_id in _video_tasks_cache:
                _video_tasks_cache[task_id].update(update_data)
    else:
        if task_id in _video_tasks_cache:
            _video_tasks_cache[task_id].update(update_data)


async def _get_video_task(task_id: str) -> Optional[dict]:
    """获取视频任务"""
    if db.connected:
        try:
            task = await db.db.video_generations.find_one({"id": task_id})
            if task:
                task.pop("_id", None)
                return task
        except Exception as e:
            logger.warning(f"数据库查询失败: {e}")
    return _video_tasks_cache.get(task_id)


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """获取可用的视频生成提供商"""
    providers = []

    # Replicate
    replicate_available = ai_service_manager.is_service_available("replicate")
    providers.append(
        ProviderInfo(
            id="replicate",
            name="Replicate",
            description="开源视频生成模型平台，支持多种SOTA模型",
            available=replicate_available,
            models=[
                {
                    "id": "wan-t2v",
                    "name": "Wan T2V",
                    "type": "text_to_video",
                    "quality": "high",
                },
                {
                    "id": "wan-i2v",
                    "name": "Wan I2V",
                    "type": "image_to_video",
                    "quality": "high",
                },
                {
                    "id": "ltx_video",
                    "name": "LTX Video",
                    "type": "text_to_video",
                    "quality": "medium",
                },
            ],
            features=["text_to_video", "image_to_video", "batch_generation"],
            pricing_hint="按生成时长计费",
        )
    )

    # Runway
    runway_available = ai_service_manager.is_service_available("runway")
    providers.append(
        ProviderInfo(
            id="runway",
            name="Runway ML",
            description="专业级视频生成和编辑平台，质量最高",
            available=runway_available,
            models=[
                {
                    "id": "gen3",
                    "name": "Gen-3 Alpha",
                    "type": "text_to_video",
                    "quality": "ultra",
                },
                {
                    "id": "gen2",
                    "name": "Gen-2",
                    "type": "text_to_video",
                    "quality": "high",
                },
            ],
            features=["text_to_video", "image_to_video", "video_editing"],
            pricing_hint="按生成秒数计费",
        )
    )

    return providers


@router.get("/templates", response_model=List[VideoTemplate])
async def list_templates():
    """获取视频生成模板"""
    return [
        VideoTemplate(
            id="product_showcase",
            name="产品展示",
            description="360度展示产品特性，适合电商和路演",
            prompt_template="Professional product showcase video, {product} rotating slowly, soft studio lighting, clean background, cinematic camera movement, high quality 4K",
            duration=5,
            style_tags=["professional", "clean", "product"],
        ),
        VideoTemplate(
            id="tech_demo",
            name="科技演示",
            description="科技感十足的动态演示",
            prompt_template="Futuristic tech demo video, holographic interface displaying {product}, neon blue and purple lighting, particle effects, cinematic motion graphics, cyberpunk aesthetic",
            duration=5,
            style_tags=["tech", "futuristic", "dynamic"],
        ),
        VideoTemplate(
            id="nature_lifestyle",
            name="自然生活",
            description="温暖自然的生活场景",
            prompt_template="Lifestyle video in nature, {product} being used in outdoor setting, golden hour lighting, peaceful atmosphere, slow cinematic motion, warm color grading",
            duration=5,
            style_tags=["lifestyle", "warm", "natural"],
        ),
        VideoTemplate(
            id="abstract_motion",
            name="抽象动态",
            description="抽象艺术风格的动态背景",
            prompt_template="Abstract motion graphics, flowing liquid forms morphing into {product}, vibrant gradients, smooth camera movement, artistic composition, loopable seamless motion",
            duration=5,
            style_tags=["abstract", "artistic", "dynamic"],
        ),
    ]


@router.post(
    "/text-to-video",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def text_to_video(request: TextToVideoRequest, background_tasks: BackgroundTasks):
    """
    文本生成视频

    将文字描述转换为视频
    """
    provider = VideoProvider(request.provider)

    if not video_service_manager.is_available(provider):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{request.provider} service not configured",
        )

    # 创建任务
    task_id = f"vid_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

    task_data = {
        "id": task_id,
        "status": "processing",
        "type": "text_to_video",
        "prompt": request.prompt,
        "provider": request.provider,
        "model": request.model,
        "video_url": None,
        "thumbnail_url": None,
        "duration": request.duration,
        "resolution": request.resolution,
        "aspect_ratio": request.aspect_ratio,
        "negative_prompt": request.negative_prompt,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
        "estimated_time": request.duration * 20,  # 预估时间
    }

    # 保存到数据库
    await _save_video_task(task_data)

    # 后台生成
    background_tasks.add_task(process_text_to_video, task_id, request)


async def process_text_to_video(task_id: str, request: TextToVideoRequest):
    """后台处理文生视频"""
    try:
        provider = VideoProvider(request.provider)
        service = video_service_manager.get_service(provider)

        result = await service.generate_video(
            prompt=request.prompt,
            model=request.model,
            duration=request.duration,
            resolution=request.resolution,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            wait_for_completion=True,
        )

        # 处理结果
        video_url = result.get("video_url")

        # 如果有视频URL，下载并保存
        if video_url and isinstance(video_url, str):
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, timeout=120.0)
                if response.status_code == 200:
                    output_dir = Path("generated/videos")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"{task_id}.mp4"
                    filepath = output_dir / filename
                    filepath.write_bytes(response.content)

                    video_url = f"/download/videos/{filename}"

        # 更新任务状态
        await _update_video_task(
            task_id,
            {
                "status": "completed",
                "video_url": video_url or result.get("video_url"),
                "thumbnail_url": f"/download/videos/{task_id}_thumb.jpg",  # 占位
                "completed_at": datetime.utcnow(),
            },
        )

        logger.info(f"Video generation completed: {task_id}")

    except Exception as e:
        logger.error(f"Video generation failed: {task_id} - {e}")
        await _update_video_task(
            task_id,
            {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.utcnow(),
            },
        )


@router.post(
    "/image-to-video",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def image_to_video(
    request: ImageToVideoRequest, background_tasks: BackgroundTasks
):
    """
    图像生成视频

    将静态图像转换为动态视频
    """
    provider = VideoProvider(request.provider)

    if not video_service_manager.is_available(provider):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{request.provider} service not configured",
        )

    task_id = (
        f"vid_img_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    )

    task_data = {
        "id": task_id,
        "status": "processing",
        "type": "image_to_video",
        "prompt": request.prompt,
        "image_url": request.image_url,
        "provider": request.provider,
        "model": request.model,
        "video_url": None,
        "thumbnail_url": request.image_url,
        "duration": request.duration,
        "resolution": "720p",
        "motion_strength": request.motion_strength,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
    }

    # 保存到数据库
    await _save_video_task(task_data)

    background_tasks.add_task(process_image_to_video, task_id, request)

    return VideoGenerationResponse(
        id=task_id,
        status="processing",
        prompt=request.prompt,
        provider=request.provider,
        duration=request.duration,
        resolution="720p",
        created_at=datetime.utcnow(),
    )


async def process_image_to_video(task_id: str, request: ImageToVideoRequest):
    """后台处理图生视频"""
    try:
        provider = VideoProvider(request.provider)
        service = video_service_manager.get_service(provider)

        result = await service.image_to_video(
            image_url=request.image_url,
            prompt=request.prompt,
            model=request.model,
            duration=request.duration,
            motion_bucket_id=request.motion_strength,
            wait_for_completion=True,
        )

        video_url = result.get("video_url")

        # 下载并保存
        if video_url and isinstance(video_url, str):
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, timeout=120.0)
                if response.status_code == 200:
                    output_dir = Path("generated/videos")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"{task_id}.mp4"
                    filepath = output_dir / filename
                    filepath.write_bytes(response.content)

                    video_url = f"/download/videos/{filename}"

        await _update_video_task(
            task_id,
            {
                "status": "completed",
                "video_url": video_url or result.get("video_url"),
                "completed_at": datetime.utcnow(),
            },
        )

        logger.info(f"Image to video completed: {task_id}")

    except Exception as e:
        logger.error(f"Image to video failed: {task_id} - {e}")
        await _update_video_task(
            task_id,
            {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.utcnow(),
            },
        )


@router.get("/generations/{task_id}", response_model=VideoGenerationResponse)
async def get_video_status(task_id: str):
    """获取视频生成任务状态"""
    task = await _get_video_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video task {task_id} not found",
        )

    return VideoGenerationResponse(**task)


@router.get("/generations", response_model=List[VideoGenerationResponse])
async def list_video_generations(limit: int = 10, offset: int = 0):
    """获取视频生成历史"""
    tasks = []

    # 优先从数据库查询
    if db.connected:
        try:
            cursor = (
                db.db.video_generations.find()
                .sort("created_at", -1)
                .skip(offset)
                .limit(limit)
            )
            async for doc in cursor:
                doc.pop("_id", None)
                tasks.append(doc)
            logger.info(f"从数据库获取了 {len(tasks)} 条视频生成记录")
        except Exception as e:
            logger.warning(f"数据库查询失败，使用缓存: {e}")

    # 如果数据库不可用或查询失败，使用内存缓存
    if not tasks:
        tasks = list(_video_tasks_cache.values())
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        tasks = tasks[offset : offset + limit]
        logger.info(f"从内存缓存获取了 {len(tasks)} 条视频生成记录")

    return [VideoGenerationResponse(**task) for task in tasks]


@router.get("/health")
async def health_check():
    """视频生成服务健康检查"""
    return {
        "available": len(video_service_manager.get_available_providers()) > 0,
        "providers": video_service_manager.get_available_providers(),
        "services": {
            "replicate": ai_service_manager.is_service_available("replicate"),
            "runway": ai_service_manager.is_service_available("runway"),
        },
    }
