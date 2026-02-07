"""
视频生成 API - 集成 StepFun LLM、语音合成和视频渲染
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.stepfun_service import StepFunLLM
from app.services.video_composer import video_composer

router = APIRouter()

# 任务存储
video_tasks: dict = {}


class VideoScriptScene(BaseModel):
    scene_number: int
    duration: int  # seconds
    visual_description: str
    narration: str
    subtitle: str


class VideoScript(BaseModel):
    title: str
    total_duration: int
    target_platform: str  # youtube, bilibili, douyin, xiaohongshu
    scenes: List[VideoScriptScene]
    background_music_suggestion: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    product_id: str
    product_name: str = Field(..., description="产品名称")
    product_description: str = Field(..., description="产品描述")
    key_features: List[str] = Field(default_factory=list, description="核心功能列表")
    script_style: str = Field(default="professional", description="脚本风格")
    target_duration: int = Field(default=60, ge=30, le=180)
    target_platform: str = Field(default="youtube", description="目标平台")
    include_subtitles: bool = Field(default=True)
    voice_style: Optional[str] = Field(default="professional", description="语音风格")


class VideoGenerationResponse(BaseModel):
    id: str
    status: str
    product_id: str
    script: Optional[VideoScript] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


def get_llm_service():
    """获取 LLM 服务实例"""
    if not settings.STEPFUN_API_KEY:
        return None
    try:
        return StepFunLLM()
    except Exception as e:
        logger.error(f"Failed to initialize StepFun LLM: {e}")
        return None


@router.post("/generate-script", response_model=VideoScript)
async def generate_video_script(
    product_name: str,
    product_description: str,
    key_features: List[str],
    style: str = "professional",
    duration: int = 60,
    platform: str = "youtube",
):
    """
    使用 AI 生成视频脚本

    使用 StepFun 大语言模型根据产品信息生成专业的视频脚本
    """
    llm = get_llm_service()

    if not llm:
        # 返回模拟数据作为 fallback
        return generate_mock_script(duration, platform)

    try:
        script_data = await llm.generate_video_script(
            product_name=product_name,
            product_description=product_description,
            key_features=key_features,
            style=style,
            duration=duration,
            platform=platform,
        )

        # 转换为 Pydantic 模型
        scenes = [VideoScriptScene(**scene) for scene in script_data["scenes"]]

        return VideoScript(
            title=script_data["title"],
            total_duration=script_data["total_duration"],
            target_platform=script_data["target_platform"],
            scenes=scenes,
            background_music_suggestion=script_data.get("background_music_suggestion"),
        )

    except Exception as e:
        logger.error(f"Failed to generate script with AI: {e}")
        # 降级到模拟数据
        return generate_mock_script(duration, platform)


def generate_mock_script(duration: int, platform: str) -> VideoScript:
    """生成模拟脚本（fallback）"""
    total_scenes = max(3, duration // 20)
    scenes = []

    scene_templates = [
        {
            "visual": "开场画面：产品Logo动画，背景音乐渐起",
            "narration": "想象一下，如果你能在10秒内完成原本需要数小时的工作...",
            "subtitle": "10秒完成数小时工作",
        },
        {
            "visual": "展示问题场景：忙碌的团队，堆积的设计任务",
            "narration": "传统的路演物料制作耗时耗力，让团队无法专注于核心产品。",
            "subtitle": "传统制作耗时耗力",
        },
        {
            "visual": "产品界面展示：AI自动生成海报",
            "narration": "现在，有了我们的AI驱动平台，一切都变得简单。",
            "subtitle": "AI让一切变简单",
        },
        {
            "visual": "多种物料展示：海报、视频、IP形象",
            "narration": "海报、视频、IP形象，一键生成，全程只需几分钟。",
            "subtitle": "一键生成多种物料",
        },
        {
            "visual": "用户成功案例展示",
            "narration": "已经有超过1000个团队选择我们，路演成功率提升50%。",
            "subtitle": "1000+团队的选择",
        },
    ]

    for i in range(min(total_scenes, len(scene_templates))):
        template = scene_templates[i]
        scenes.append(
            VideoScriptScene(
                scene_number=i + 1,
                duration=duration // total_scenes,
                visual_description=template["visual"],
                narration=template["narration"],
                subtitle=template["subtitle"],
            )
        )

    return VideoScript(
        title="产品路演演示视频",
        total_duration=duration,
        target_platform=platform,
        scenes=scenes,
        background_music_suggestion="科技感轻音乐",
    )


@router.post(
    "/generate",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
):
    """
    生成视频

    提交视频生成任务，包含脚本生成、语音合成、视频渲染
    """
    task_id = f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

    logger.info(f"Starting video generation: {task_id}")

    # 初始化任务状态
    video_tasks[task_id] = {
        "id": task_id,
        "status": "processing",
        "product_id": request.product_id,
        "script": None,
        "audio_url": None,
        "video_url": None,
        "thumbnail_url": None,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
    }

    # 后台执行生成
    background_tasks.add_task(process_video_generation, task_id, request)

    return VideoGenerationResponse(
        id=task_id,
        status="processing",
        product_id=request.product_id,
        created_at=datetime.utcnow(),
    )


async def process_video_generation(task_id: str, request: VideoGenerationRequest):
    """后台处理视频生成"""
    try:
        # 步骤1: 生成脚本
        logger.info(f"[{task_id}] Step 1: Generating script...")

        llm = get_llm_service()
        if llm:
            script_data = await llm.generate_video_script(
                product_name=request.product_name,
                product_description=request.product_description,
                key_features=request.key_features,
                style=request.script_style,
                duration=request.target_duration,
                platform=request.target_platform,
            )

            scenes = [VideoScriptScene(**scene) for scene in script_data["scenes"]]
            script = VideoScript(
                title=script_data["title"],
                total_duration=script_data["total_duration"],
                target_platform=script_data["target_platform"],
                scenes=scenes,
                background_music_suggestion=script_data.get(
                    "background_music_suggestion"
                ),
            )
        else:
            script = generate_mock_script(
                request.target_duration, request.target_platform
            )

        video_tasks[task_id]["script"] = script

        # 步骤2: 合成旁白语音 (如果配置了语音服务)
        logger.info(f"[{task_id}] Step 2: Generating narration audio...")
        audio_path = None

        # 尝试生成语音
        if settings.STEPFUN_API_KEY:
            try:
                from app.services.minimax_service import MinimaxTTS

                tts = MinimaxTTS()

                # 合并所有场景的旁白文本
                full_text = "\n".join(
                    [scene.narration for scene in script.scenes if scene.narration]
                )

                if full_text:
                    audio_result = await tts.generate_audio(
                        text=full_text, voice_id="zhengpaiqingnian", speed=1.0
                    )

                    if audio_result and audio_result.get("audio_url"):
                        # 下载音频文件
                        audio_url = audio_result["audio_url"]
                        if audio_url.startswith("/"):
                            audio_path = Path(
                                audio_url.replace(
                                    "/download/audios/", "generated/audios/"
                                )
                            )
                        else:
                            audio_path = (
                                Path("generated/audios") / f"{task_id}_audio.mp3"
                            )

                            import httpx

                            async with httpx.AsyncClient() as client:
                                response = await client.get(audio_url, timeout=60)
                                if response.status_code == 200:
                                    audio_path.parent.mkdir(parents=True, exist_ok=True)
                                    audio_path.write_bytes(response.content)

                logger.info(f"[{task_id}] Audio generation completed")

            except Exception as e:
                logger.warning(
                    f"[{task_id}] Audio generation failed (continuing without audio): {e}"
                )

        # 步骤3: 渲染视频
        logger.info(f"[{task_id}] Step 3: Rendering video...")

        scenes_data = [
            {
                "scene_number": scene.scene_number,
                "duration": scene.duration,
                "visual_description": scene.visual_description,
                "narration": scene.narration,
                "subtitle": scene.subtitle,
            }
            for scene in script.scenes
        ]

        video_result = await video_composer.create_simple_video(
            task_id=task_id,
            title=request.product_name,
            scenes=scenes_data,
            duration=request.target_duration,
        )

        # 如果有音频，尝试合并
        if audio_path and audio_path.exists():
            try:
                video_path = Path("generated/videos") / f"{task_id}.mp4"
                output_path = Path("generated/videos") / f"{task_id}_final.mp4"

                success = await video_composer.combine_audio_video(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=output_path,
                )

                if success:
                    video_result["video_url"] = f"/download/videos/{task_id}_final.mp4"
                    logger.info(f"[{task_id}] Audio and video combined successfully")

            except Exception as e:
                logger.warning(f"[{task_id}] Audio-video combination failed: {e}")

        # 更新完成状态
        video_tasks[task_id].update(
            {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "video_url": video_result.get("video_url"),
                "thumbnail_url": video_result.get("thumbnail_url"),
            }
        )

        logger.info(f"Video generation completed: {task_id}")

    except Exception as e:
        logger.error(f"Video generation failed: {task_id} - {e}")
        video_tasks[task_id].update(
            {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.utcnow(),
            }
        )


@router.get("/generations/{generation_id}", response_model=VideoGenerationResponse)
async def get_video_status(generation_id: str):
    """获取视频生成状态"""
    task = video_tasks.get(generation_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video generation task {generation_id} not found",
        )

    return VideoGenerationResponse(**task)


@router.get("/generations", response_model=list[VideoGenerationResponse])
async def list_video_generations(limit: int = 10, offset: int = 0):
    """获取视频生成历史列表"""
    tasks = list(video_tasks.values())
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    paginated = tasks[offset : offset + limit]
    return [VideoGenerationResponse(**task) for task in paginated]


@router.get("/templates")
async def get_video_templates():
    """获取可用的视频模板"""
    return [
        {
            "id": "product-demo",
            "name": "产品演示",
            "description": "标准产品功能演示模板",
            "duration_range": "60-120秒",
            "platforms": ["youtube", "bilibili"],
        },
        {
            "id": "pitch-deck",
            "name": "路演演示",
            "description": "投资人路演专用模板",
            "duration_range": "90-180秒",
            "platforms": ["youtube", "bilibili"],
        },
        {
            "id": "social-media",
            "name": "社交媒体",
            "description": "适合社交平台传播的短视频",
            "duration_range": "15-60秒",
            "platforms": ["douyin", "xiaohongshu", "bilibili"],
        },
        {
            "id": "app-promo",
            "name": "App推广",
            "description": "移动应用推广专用模板",
            "duration_range": "30-90秒",
            "platforms": ["douyin", "xiaohongshu"],
        },
    ]


@router.get("/health")
async def health_check():
    """视频生成服务健康检查"""
    llm = get_llm_service()
    return {
        "available": llm is not None or video_composer.ffmpeg_available,
        "llm_configured": settings.STEPFUN_API_KEY is not None,
        "ffmpeg_available": video_composer.ffmpeg_available,
        "services": {
            "script_generation": llm is not None,
            "voice_synthesis": settings.STEPFUN_API_KEY is not None,
            "video_rendering": video_composer.ffmpeg_available,
        },
    }
