"""
数据模型模块
"""

from app.models.user import User, UserCreate, UserUpdate, UserInDB
from app.models.product import Product, ProductCreate, ProductUpdate
from app.models.poster import PosterGeneration, PosterTemplate
from app.models.video import VideoGeneration, VideoScript
from app.models.voice import VoiceGeneration
from app.models.ip import IPGeneration, IPConcept
from app.models.team import Team, TeamMember, TeamRole
from app.models.analytics import AnalyticsEvent, ABTest

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "PosterGeneration",
    "PosterTemplate",
    "VideoGeneration",
    "VideoScript",
    "VoiceGeneration",
    "IPGeneration",
    "IPConcept",
    "Team",
    "TeamMember",
    "TeamRole",
    "AnalyticsEvent",
    "ABTest",
]
