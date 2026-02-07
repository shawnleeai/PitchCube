"""
数据分析模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    GENERATION_START = "generation_start"
    GENERATION_COMPLETE = "generation_complete"
    GENERATION_FAIL = "generation_fail"
    DOWNLOAD = "download"
    SHARE = "share"
    LOGIN = "login"
    SIGNUP = "signup"


class GenerationType(str, Enum):
    POSTER = "poster"
    VIDEO = "video"
    VOICE = "voice"
    IP = "ip"


class AnalyticsEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: Optional[str] = None
    event_type: EventType
    generation_type: Optional[GenerationType] = None
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ABTestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ABTestVariant(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource_ids: List[str]
    weight: int


class ABTestBase(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: str
    variants: List[ABTestVariant]
    target_metric: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ABTestCreate(ABTestBase):
    pass


class ABTestInDB(ABTestBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    status: ABTestStatus = ABTestStatus.DRAFT
    results: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ABTest(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    test_type: str
    variants: List[ABTestVariant]
    target_metric: str
    status: ABTestStatus
    results: Dict[str, Any]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_generations: int
    poster_count: int
    video_count: int
    voice_count: int
    ip_count: int
    total_downloads: int
    favorite_template: Optional[str] = None
    most_used_platform: Optional[str] = None


class AnalyticsSummary(BaseModel):
    total_users: int
    total_generations: int
    total_downloads: int
    generation_breakdown: Dict[str, int]
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
