"""
User management endpoints
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.api.v1.auth import get_current_user

router = APIRouter()


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    website: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserStats(BaseModel):
    total_products: int
    total_generations: int
    poster_generations: int
    video_generations: int
    storage_used_mb: float


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    # In production, fetch from database
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        username="demo_user",
        full_name="Demo User",
        bio="A passionate developer",
        company="Startup Inc.",
        website="https://example.com",
        avatar_url=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.put("/me", response_model=UserProfile)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update current user profile."""
    # In production, update in database
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        username="demo_user",
        full_name=update_data.full_name or "Demo User",
        bio=update_data.bio,
        company=update_data.company,
        website=update_data.website,
        avatar_url=update_data.avatar_url,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user generation statistics."""
    # In production, calculate from database
    return UserStats(
        total_products=5,
        total_generations=23,
        poster_generations=15,
        video_generations=8,
        storage_used_mb=45.2,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete user account."""
    # In production:
    # 1. Delete user data
    # 2. Delete generated files
    # 3. Remove from database
    return None
