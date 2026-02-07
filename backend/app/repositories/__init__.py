"""
Repository模块
"""

from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.poster_repository import PosterRepository
from app.repositories.video_repository import VideoRepository

__all__ = [
    "UserRepository",
    "ProductRepository",
    "PosterRepository",
    "VideoRepository",
]
