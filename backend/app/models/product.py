"""
产品模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    tagline: Optional[str] = Field(None, max_length=200)
    key_features: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    category: Optional[str] = None
    website_url: Optional[str] = None
    github_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tagline: Optional[str] = None
    key_features: Optional[List[str]] = None
    target_audience: Optional[str] = None
    category: Optional[str] = None
    website_url: Optional[str] = None
    github_url: Optional[str] = None


class ProductInDB(ProductBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    poster_count: int = 0
    video_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Product(ProductBase):
    id: str
    user_id: str
    poster_count: int
    video_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductAnalysis(BaseModel):
    market_opportunity: str
    competitive_advantages: List[str]
    potential_challenges: List[str]
    target_segments: List[str]
    recommendations: List[str]
