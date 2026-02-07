"""
视频生成模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoPlatform(str, Enum):
    YOUTUBE = "youtube"
    BILIBILI = "bilibili"
    DOUYIN = "douyin"
    XIAOHONGSHU = "xiaohongshu"


class VideoScriptScene(BaseModel):
    scene_number: int
    duration: int
    visual_description: str
    narration: str
    subtitle: str


class VideoScript(BaseModel):
    title: str
    total_duration: int
    target_platform: VideoPlatform
    scenes: List[VideoScriptScene]
    background_music_suggestion: Optional[str] = None


class VideoStyle(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    URGENT = "urgent"
    EMOTIONAL = "emotional"


class VideoGenerationBase(BaseModel):
    product_name: str
    product_description: str
    key_features: List[str] = Field(default_factory=list)
    script_style: VideoStyle = VideoStyle.PROFESSIONAL
    target_duration: int = Field(default=60, ge=30, le=180)
    target_platform: VideoPlatform = VideoPlatform.YOUTUBE
    include_subtitles: bool = True
    voice_style: Optional[str] = None


class VideoGenerationCreate(VideoGenerationBase):
    product_id: str


class VideoGenerationInDB(VideoGenerationBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    product_id: Optional[str] = None
    status: VideoStatus = VideoStatus.PENDING
    script: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class VideoGeneration(BaseModel):
    id: str
    user_id: str
    product_id: Optional[str]
    product_name: str
    product_description: str
    key_features: List[str]
    script_style: VideoStyle
    target_duration: int
    target_platform: VideoPlatform
    include_subtitles: bool
    voice_style: Optional[str]
    status: VideoStatus
    script: Optional[Dict[str, Any]]
    audio_url: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
