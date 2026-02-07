"""
海报生成模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class PosterStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PosterStyle(str, Enum):
    TECH_MODERN = "tech-modern"
    STARTUP_BOLD = "startup-bold"
    MINIMAL_CLEAN = "minimal-clean"
    CREATIVE_GRADIENT = "creative-gradient"


class PosterTemplate(BaseModel):
    id: str
    name: str
    description: str
    style: PosterStyle
    preview_url: Optional[str] = None
    default_colors: List[str] = Field(default_factory=list)
    is_premium: bool = False


class PosterGenerationBase(BaseModel):
    product_name: str
    product_description: str
    key_features: List[str] = Field(default_factory=list)
    template_id: str = PosterStyle.TECH_MODERN
    primary_color: Optional[str] = None
    size: str = "1200x1600"


class PosterGenerationCreate(PosterGenerationBase):
    pass


class PosterGenerationInDB(PosterGenerationBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    product_id: Optional[str] = None
    status: PosterStatus = PosterStatus.PENDING
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_urls: Dict[str, str] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PosterGeneration(BaseModel):
    id: str
    user_id: str
    product_id: Optional[str]
    product_name: str
    product_description: str
    key_features: List[str]
    template_id: str
    primary_color: Optional[str]
    size: str
    status: PosterStatus
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    download_urls: Dict[str, str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
