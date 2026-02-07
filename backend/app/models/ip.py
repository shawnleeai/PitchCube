"""
IP形象生成模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class IPStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    "failed"


class IPStyle(str, Enum):
    CUTE = "cute"
    TECH = "tech"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMALIST = "minimalist"


class IPSize(str, Enum):
    SMALL = "5cm"
    MEDIUM = "10cm"
    LARGE = "20cm"


class IPSize(str, Enum):
    PLA = "pla"
    ABS = "abs"
    PETG = "petg"
    RESIN = "resin"


class IPConcept(BaseModel):
    name: str
    style: IPStyle
    style_name: str
    description: str
    features: List[str]
    custom_elements: List[str]
    personality: str
    color_scheme: List[str]
    story: str


class IPGenerationBase(BaseModel):
    product_name: str
    product_description: str
    style: IPStyle = IPStyle.CUTE
    custom_elements: List[str] = Field(default_factory=list)
    material: str = "pla"
    size_cm: float = 10.0


class IPGenerationCreate(IPGenerationBase):
    pass


class IPGenerationInDB(IPGenerationBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    product_id: Optional[str] = None
    status: IPStatus = IPStatus.PENDING
    concept: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    model_3d_url: Optional[str] = None
    print_guide: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class IPGeneration(BaseModel):
    id: str
    user_id: str
    product_id: Optional[str]
    product_name: str
    product_description: str
    style: IPStyle
    custom_elements: List[str]
    material: str
    size_cm: float
    status: IPStatus
    concept: Optional[Dict[str, Any]]
    image_url: Optional[str]
    model_3d_url: Optional[str]
    print_guide: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
