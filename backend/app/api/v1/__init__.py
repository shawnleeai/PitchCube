"""
API v1 Router
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    posters,
    products,
    users,
    videos,
    health,
    voice,
    collaboration,
    analytics,
    batch,
)
from app.api.v1 import ai_images, ai_videos, ai_roleplay, chinese_ai

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["Health"])
# 使用增强版认证路由（支持邮件验证、密码重置）
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
# 使用增强版产品路由（支持 GitHub 导入、完整 CRUD）
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(posters.router, prefix="/posters", tags=["Posters"])
router.include_router(videos.router, prefix="/videos", tags=["Videos"])
router.include_router(voice.router, prefix="/voice", tags=["Voice"])
# 协作空间路由
router.include_router(collaboration.router, prefix="/collab", tags=["Collaboration"])
# 数据魔镜路由
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
# 批量生成路由
router.include_router(batch.router, prefix="", tags=["Batch"])

# AI 服务路由
router.include_router(ai_images.router, prefix="/ai/images", tags=["AI Images"])
router.include_router(ai_videos.router, prefix="/ai/videos", tags=["AI Videos"])
router.include_router(ai_roleplay.router, prefix="/ai/roleplay", tags=["AI Roleplay"])

# 国产 AI 服务路由 (Minimax + StepFun)
router.include_router(chinese_ai.router, prefix="/chinese-ai", tags=["Chinese AI"])
