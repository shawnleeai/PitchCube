"""
语音生成模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class VoiceStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceStyle(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENERGETIC = "energetic"


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class VoiceGenerationBase(BaseModel):
    text: str
    voice_style: VoiceStyle = VoiceStyle.PROFESSIONAL
    voice_gender: VoiceGender = VoiceGender.FEMALE
    voice_id: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    language: str = "zh-CN"


class VoiceGenerationCreate(VoiceGenerationBase):
    pass


class VoiceGenerationInDB(VoiceGenerationBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    product_id: Optional[str] = None
    status: VoiceStatus = VoiceStatus.PENDING
    audio_url: Optional[str] = None
    duration_estimate: float
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class VoiceGeneration(BaseModel):
    id: str
    user_id: str
    product_id: Optional[str]
    text: str
    voice_style: VoiceStyle
    voice_gender: VoiceGender
    voice_id: Optional[str]
    speed: float
    language: str
    status: VoiceStatus
    audio_url: Optional[str]
    duration_estimate: float
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: VoiceGender
    style: VoiceStyle
    description: str
    tags: List[str]
