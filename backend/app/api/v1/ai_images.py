"""
AI 图像生成 API
支持 DALL-E (OpenAI) 和 Stability AI
"""

import io
import base64
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.ai_service_manager import ai_service_manager

router = APIRouter()

# 任务存储
generation_tasks: dict = {}


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="图像描述")
    provider: str = Field(default="auto", description="提供商: auto/openai/stability")
    model: str = Field(default="dall-e-3", description="模型名称")
    size: str = Field(default="1024x1024", description="图像尺寸")
    quality: str = Field(default="standard", description="质量: standard/hd (仅DALL-E 3)")
    style: str = Field(default="vivid", description="风格: vivid/natural (仅DALL-E 3)")
    n: int = Field(default=1, ge=1, le=4, description="生成数量")
    negative_prompt: Optional[str] = Field(default=None, description="负面提示词（Stability）")


class ImageGenerationResponse(BaseModel):
    id: str
    status: str
    prompt: str
    provider: str
    image_urls: List[str] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ImageEditRequest(BaseModel):
    prompt: str = Field(..., description="编辑提示词")
    mask_data: Optional[str] = Field(default=None, description="遮罩图像base64（可选）")


class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    available: bool
    models: List[Dict[str, Any]]
    features: List[str]


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """获取可用的图像生成提供商"""
    providers = []
    
    # OpenAI / DALL-E
    openai_available = ai_service_manager.is_service_available("openai")
    providers.append(ProviderInfo(
        id="openai",
        name="OpenAI DALL-E",
        description="高质量AI图像生成，理解力强",
        available=openai_available,
        models=[
            {"id": "dall-e-3", "name": "DALL-E 3", "description": "最新模型，质量最高", "sizes": ["1024x1024", "1792x1024", "1024x1792"]},
            {"id": "dall-e-2", "name": "DALL-E 2", "description": "速度快，成本低", "sizes": ["256x256", "512x512", "1024x1024"]}
        ],
        features=["text_to_image", "image_variation", "image_edit"]
    ))
    
    # Stability AI
    stability_available = ai_service_manager.is_service_available("stability")
    providers.append(ProviderInfo(
        id="stability",
        name="Stability AI",
        description="开源模型，性价比高，适合批量生成",
        available=stability_available,
        models=[
            {"id": "stable-image-ultra", "name": "Stable Image Ultra", "description": "最高质量"},
            {"id": "stable-diffusion-xl", "name": "SD XL", "description": "平衡质量与速度"}
        ],
        features=["text_to_image", "image_upscale", "poster_enhancement"]
    ))
    
    return providers


@router.post("/generate", response_model=ImageGenerationResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_image(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    生成AI图像
    
    支持 DALL-E 3/2 和 Stability AI
    """
    # 检查服务可用性
    if request.provider != "auto":
        if request.provider == "openai" and not ai_service_manager.is_service_available("openai"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI service not configured"
            )
        if request.provider == "stability" and not ai_service_manager.is_service_available("stability"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stability AI service not configured"
            )
    
    # 创建任务
    task_id = f"img_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    generation_tasks[task_id] = {
        "id": task_id,
        "status": "processing",
        "prompt": request.prompt,
        "provider": request.provider,
        "image_urls": [],
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
    }
    
    # 后台生成
    background_tasks.add_task(
        process_image_generation,
        task_id,
        request
    )
    
    return ImageGenerationResponse(
        id=task_id,
        status="processing",
        prompt=request.prompt,
        provider=request.provider,
        created_at=datetime.utcnow()
    )


async def process_image_generation(task_id: str, request: ImageGenerationRequest):
    """后台处理图像生成"""
    try:
        output_dir = Path("generated/images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_urls = []
        
        # 使用 OpenAI DALL-E
        if request.provider in ["auto", "openai"] and ai_service_manager.is_service_available("openai"):
            from app.services.openai_service import OpenAIService
            
            service = OpenAIService()
            images = await service.generate_image(
                prompt=request.prompt,
                model=request.model,
                size=request.size,
                quality=request.quality,
                style=request.style,
                n=request.n
            )
            
            for i, image_data in enumerate(images):
                filename = f"{task_id}_{i}.png"
                filepath = output_dir / filename
                filepath.write_bytes(image_data)
                image_urls.append(f"/download/images/{filename}")
        
        # 使用 Stability AI
        elif request.provider in ["auto", "stability"] and ai_service_manager.is_service_available("stability"):
            from app.services.stability_service import StabilityAI
            
            service = StabilityAI()
            
            # 转换尺寸格式
            aspect_ratio = "1:1"
            if request.size == "1024x1024":
                aspect_ratio = "1:1"
            elif request.size in ["1792x1024", "1024x1792"]:
                aspect_ratio = "16:9" if request.size == "1792x1024" else "9:16"
            
            for i in range(request.n):
                image_data = await service.generate_image(
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt or "",
                    aspect_ratio=aspect_ratio,
                    output_format="png"
                )
                
                filename = f"{task_id}_{i}.png"
                filepath = output_dir / filename
                filepath.write_bytes(image_data)
                image_urls.append(f"/download/images/{filename}")
        
        else:
            raise Exception("No image generation service available")
        
        # 更新任务状态
        generation_tasks[task_id].update({
            "status": "completed",
            "image_urls": image_urls,
            "completed_at": datetime.utcnow()
        })
        
        logger.info(f"Image generation completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Image generation failed: {task_id} - {e}")
        generation_tasks[task_id].update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.utcnow()
        })


@router.get("/generations/{task_id}", response_model=ImageGenerationResponse)
async def get_generation_status(task_id: str):
    """获取图像生成任务状态"""
    task = generation_tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return ImageGenerationResponse(**task)


@router.post("/edit/{task_id}")
async def edit_image(task_id: str, request: ImageEditRequest):
    """
    编辑图像（仅 DALL-E 2 支持）
    
    需要先生成图像，然后使用task_id编辑
    """
    if not ai_service_manager.is_service_available("openai"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI service not configured"
        )
    
    # 获取原始任务
    task = generation_tasks.get(task_id)
    if not task or not task.get("image_urls"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original image not found"
        )
    
    try:
        from app.services.openai_service import OpenAIService
        
        service = OpenAIService()
        
        # 读取原始图像
        image_path = Path("generated/images") / f"{task_id}_0.png"
        image_data = image_path.read_bytes()
        
        # 处理遮罩（如果有）
        mask_data = None
        if request.mask_data:
            mask_data = base64.b64decode(request.mask_data.split(",")[-1])
        
        # 编辑图像
        edited_images = await service.edit_image(
            image_data=image_data,
            prompt=request.prompt,
            mask_data=mask_data
        )
        
        # 保存编辑后的图像
        edit_id = f"{task_id}_edit_{uuid.uuid4().hex[:4]}"
        output_dir = Path("generated/images")
        
        image_urls = []
        for i, img_data in enumerate(edited_images):
            filename = f"{edit_id}_{i}.png"
            filepath = output_dir / filename
            filepath.write_bytes(img_data)
            image_urls.append(f"/download/images/{filename}")
        
        return {
            "edit_id": edit_id,
            "original_task_id": task_id,
            "image_urls": image_urls,
            "prompt": request.prompt
        }
        
    except Exception as e:
        logger.error(f"Image edit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image edit failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """图像生成服务健康检查"""
    return {
        "available": (
            ai_service_manager.is_service_available("openai") or 
            ai_service_manager.is_service_available("stability")
        ),
        "services": {
            "openai": ai_service_manager.is_service_available("openai"),
            "stability": ai_service_manager.is_service_available("stability")
        }
    }
