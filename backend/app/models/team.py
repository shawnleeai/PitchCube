"""
团队协作模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class TeamRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class TeamMemberBase(BaseModel):
    user_id: str
    role: TeamRole = TeamRole.VIEWER
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None
    joined_at: Optional[datetime] = None


class TeamMemberCreate(BaseModel):
    email: str
    role: TeamRole = TeamRole.VIEWER


class TeamMemberInDB(TeamMemberBase):
    user_id: str
    team_id: str
    joined_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TeamMember(BaseModel):
    user_id: str
    team_id: str
    role: TeamRole
    invited_at: datetime
    invited_by: Optional[str]
    joined_at: Optional[datetime]
    username: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class TeamInDB(TeamBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    owner_id: str
    member_count: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Team(TeamBase):
    id: str
    owner_id: str
    member_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CollaborationSession(BaseModel):
    id: str
    project_id: str
    project_type: str
    created_by: str
    participants: List[str]
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
