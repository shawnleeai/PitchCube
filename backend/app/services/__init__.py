"""
Services Module
"""

from app.services.poster_generator import PosterGenerator
from app.services.poster_renderer import poster_renderer
from app.services.stepfun_service import StepFunLLM, generate_video_script, optimize_copywriting
from app.services.stability_service import StabilityAI, enhance_poster_background

# 创建 PosterGenerator 实例
poster_generator = PosterGenerator()

__all__ = [
    "poster_generator",
    "poster_renderer",
    "StepFunLLM",
    "generate_video_script",
    "optimize_copywriting",
    "StabilityAI",
    "enhance_poster_background",
]
