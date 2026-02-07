"""
海报增强 API - 集成 AI 图像生成
使用 Stability AI 生成高质量海报背景
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.stability_service import StabilityAI

router = APIRouter()

# 任务存储
enhancement_tasks: dict = {}


class PosterEnhancementRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    product_description: str = Field(..., min_length=10, max_length=1000)
    style: str = Field(default="modern tech", description="风格: modern tech/minimalist/vibrant/professional")
    color_scheme: Optional[str] = Field(None, description="配色方案，如 'blue and purple'")
    include_text: bool = Field(default=True, description="是否在图像上添加产品文字")


class PosterEnhancementResponse(BaseModel):
    id: str
    status: str
    product_name: str
    style: str
    image_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


def get_stability_service():
    """获取 Stability AI 服务实例"""
    if not settings.STABILITY_API_KEY:
        return None
    try:
        return StabilityAI()
    except Exception as e:
        logger.error(f"Failed to initialize Stability AI: {e}")
        return None


@router.post("/enhance", response_model=PosterEnhancementResponse, status_code=status.HTTP_202_ACCEPTED)
async def enhance_poster(
    request: PosterEnhancementRequest,
    background_tasks: BackgroundTasks,
):
    """
    AI 增强海报生成
    
    使用 Stability AI 生成高质量的海报背景图像
    """
    # 检查服务是否可用
    stability = get_stability_service()
    if not stability:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stability AI service not configured. Please set STABILITY_API_KEY."
        )
    
    # 生成任务ID
    task_id = f"poster_enhance_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # 初始化任务状态
    enhancement_tasks[task_id] = {
        "id": task_id,
        "status": "processing",
        "product_name": request.product_name,
        "style": request.style,
        "image_url": None,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "error_message": None,
    }
    
    logger.info(f"Poster enhancement started: {task_id} - {request.product_name}")
    
    # 后台执行生成
    background_tasks.add_task(
        process_poster_enhancement,
        task_id,
        request
    )
    
    return PosterEnhancementResponse(
        id=task_id,
        status="processing",
        product_name=request.product_name,
        style=request.style,
        created_at=datetime.utcnow(),
    )


async def process_poster_enhancement(task_id: str, request: PosterEnhancementRequest):
    """后台处理海报增强"""
    try:
        stability = get_stability_service()
        if not stability:
            raise Exception("Stability AI service not available")
        
        # 生成 AI 背景
        image_data = await stability.enhance_poster(
            product_name=request.product_name,
            description=request.product_description,
            style=request.style,
            color_scheme=request.color_scheme
        )
        
        # 保存图像文件
        filename = f"{task_id}.png"
        output_dir = Path("generated")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        filepath.write_bytes(image_data)
        
        # 更新任务状态
        enhancement_tasks[task_id].update({
            "status": "completed",
            "image_url": f"/download/{filename}",
            "completed_at": datetime.utcnow(),
        })
        
        logger.info(f"Poster enhancement completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Poster enhancement failed: {task_id} - {e}")
        enhancement_tasks[task_id].update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.utcnow(),
        })


@router.get("/enhancements/{task_id}", response_model=PosterEnhancementResponse)
async def get_enhancement_status(task_id: str):
    """查询海报增强任务状态"""
    task = enhancement_tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement task {task_id} not found"
        )
    
    return PosterEnhancementResponse(**task)


@router.get("/enhancements", response_model=list[PosterEnhancementResponse])
async def list_enhancements(limit: int = 10, offset: int = 0):
    """获取海报增强历史列表"""
    tasks = list(enhancement_tasks.values())
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    paginated = tasks[offset:offset + limit]
    return [PosterEnhancementResponse(**task) for task in paginated]


@router.get("/styles")
async def get_enhancement_styles():
    """获取可用的海报增强风格"""
    return [
        {
            "id": "modern tech",
            "name": "现代科技",
            "description": "简洁现代的科技风格，适合SaaS产品",
            "example_colors": ["#0ea5e9", "#6366f1", "#8b5cf6"]
        },
        {
            "id": "minimalist",
            "name": "极简主义",
            "description": "干净简约的设计，突出产品本身",
            "example_colors": ["#18181b", "#71717a", "#f4f4f5"]
        },
        {
            "id": "vibrant",
            "name": "活力创意",
            "description": "色彩鲜艳，充满活力和创意感",
            "example_colors": ["#f97316", "#ec4899", "#ef4444"]
        },
        {
            "id": "professional",
            "name": "专业商务",
            "description": "稳重的商务风格，适合企业产品",
            "example_colors": ["#1e40af", "#3b82f6", "#60a5fa"]
        },
    ]


@router.get("/health")
async def health_check():
    """海报增强服务健康检查"""
    stability = get_stability_service()
    return {
        "available": stability is not None,
        "api_configured": settings.STABILITY_API_KEY is not None
    }
