"""
协作空间 API - 团队实时协作管理
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from app.core.logging import logger
from app.db.mongodb import db

router = APIRouter()


class CollaborationRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectType(str, Enum):
    POSTER = "poster"
    VIDEO = "video"
    IP = "ip"
    VOICE = "voice"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# ============ 数据模型 ============


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    project_type: ProjectType
    team_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    content: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    project_type: ProjectType
    status: ProjectStatus
    owner_id: str
    team_id: Optional[str]
    content: Dict[str, Any]
    version: int
    collaborators: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    members: List[Dict[str, Any]]
    projects: List[str]
    created_at: datetime


class InviteRequest(BaseModel):
    email: str
    role: CollaborationRole = CollaborationRole.EDITOR


class CollaborationSession(BaseModel):
    id: str
    project_id: str
    user_id: str
    username: str
    cursor_position: Optional[Dict[str, Any]] = None
    joined_at: datetime


# ============ WebSocket 管理 ============


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.user_sessions: Dict[str, str] = {}

    async def connect(
        self, websocket: WebSocket, project_id: str, user_id: str, username: str
    ):
        await websocket.accept()

        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}

        self.active_connections[project_id][user_id] = {
            "websocket": websocket,
            "username": username,
            "cursor": None,
            "last_activity": datetime.utcnow(),
        }

        self.user_sessions[id(websocket)] = project_id

        await self.broadcast_project_update(
            project_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "username": username,
                "active_users": self.get_active_users_list(project_id),
            },
        )

        logger.info(f"User {username} joined project {project_id}")

    def disconnect(
        self, websocket: WebSocket, project_id: str, user_id: str, username: str
    ):
        if (
            project_id in self.active_connections
            and user_id in self.active_connections[project_id]
        ):
            del self.active_connections[project_id][user_id]

            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

        self.user_sessions.pop(id(websocket), None)

    async def broadcast_to_project(
        self, project_id: str, message: dict, exclude_user: str = None
    ):
        if project_id in self.active_connections:
            connections_to_remove = []

            for user_id, connection in self.active_connections[project_id].items():
                if user_id != exclude_user:
                    try:
                        await connection["websocket"].send_json(message)
                    except Exception as e:
                        logger.error(f"Broadcast error: {e}")
                        connections_to_remove.append(user_id)

            for user_id in connections_to_remove:
                if user_id in self.active_connections[project_id]:
                    del self.active_connections[project_id][user_id]

    async def broadcast_project_update(self, project_id: str, update: dict):
        await self.broadcast_to_project(
            project_id,
            {
                "type": "project_update",
                "timestamp": datetime.utcnow().isoformat(),
                **update,
            },
        )

    def get_active_users_list(self, project_id: str) -> List[Dict[str, str]]:
        if project_id in self.active_connections:
            return [
                {
                    "user_id": user_id,
                    "username": conn["username"],
                    "cursor": conn["cursor"],
                    "last_activity": conn["last_activity"].isoformat(),
                }
                for user_id, conn in self.active_connections[project_id].items()
            ]
        return []

    @property
    def total_connections(self) -> int:
        return sum(len(connections) for connections in self.active_connections.values())


manager = ConnectionManager()


# ============ API 端点 ============


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 20, user_id: str = "user_123"):
    """获取用户的项目列表"""
    logger.info(f"获取项目列表: user={user_id}")

    if db.connected:
        cursor = (
            db.db.projects.find(
                {
                    "$or": [{"owner_id": user_id}, {"collaborators.user_id": user_id}],
                    "is_active": True,
                }
            )
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )

        projects = []
        async for doc in cursor:
            doc.pop("_id", None)
            projects.append(ProjectResponse(**doc))

        return projects
    else:
        return []


@router.post(
    "/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED
)
async def create_project(project_data: ProjectCreate, user_id: str = "user_123"):
    """创建新项目"""
    logger.info(f"创建项目: {project_data.name}")

    project = {
        "id": f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "name": project_data.name,
        "description": project_data.description,
        "project_type": project_data.project_type.value,
        "status": ProjectStatus.DRAFT.value,
        "owner_id": user_id,
        "team_id": project_data.team_id,
        "content": {},
        "version": 1,
        "collaborators": [],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.projects.insert_one(project)
        logger.info(f"项目已保存: {project['id']}")
    else:
        logger.warning("数据库未连接，项目仅保存在内存中")

    return ProjectResponse(**project)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """获取项目详情"""
    logger.info(f"获取项目: {project_id}")

    if db.connected:
        project = await db.db.projects.find_one({"id": project_id, "is_active": True})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在"
            )
        project.pop("_id", None)
        return ProjectResponse(**project)
    else:
        return ProjectResponse(
            id=project_id,
            name="演示项目",
            description="这是一个演示项目",
            project_type=ProjectType.POSTER,
            status=ProjectStatus.DRAFT,
            owner_id="user_123",
            team_id=None,
            content={},
            version=1,
            collaborators=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, update_data: ProjectUpdate, user_id: str = "user_123"
):
    """更新项目"""
    logger.info(f"更新项目: {project_id}")

    if db.connected:
        project = await db.db.projects.find_one({"id": project_id, "is_active": True})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在"
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            update_dict["version"] = project.get("version", 1) + 1

            await db.db.projects.update_one({"id": project_id}, {"$set": update_dict})

            await manager.broadcast_project_update(
                project_id,
                {
                    "action": "project_updated",
                    "user_id": user_id,
                    "changes": update_dict,
                },
            )

        updated = await db.db.projects.find_one({"id": project_id})
        updated.pop("_id", None)
        return ProjectResponse(**updated)
    else:
        return ProjectResponse(
            id=project_id,
            name=update_data.name or "演示项目",
            description=update_data.description,
            project_type=ProjectType.POSTER,
            status=update_data.status or ProjectStatus.DRAFT,
            owner_id=user_id,
            team_id=None,
            content=update_data.content or {},
            version=1,
            collaborators=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user_id: str = "user_123"):
    """删除项目（软删除）"""
    logger.info(f"删除项目: {project_id}")

    if db.connected:
        await db.db.projects.update_one(
            {"id": project_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
        )

    return {"message": "项目已删除", "project_id": project_id}


@router.get("/projects/{project_id}/collaborators")
async def get_collaborators(project_id: str):
    """获取项目协作者列表"""
    active_users = manager.get_active_users_list(project_id)
    return {"active_users": active_users, "total": len(active_users)}


@router.post("/projects/{project_id}/invite")
async def invite_collaborator(
    project_id: str, request: InviteRequest, user_id: str = "user_123"
):
    """邀请协作者"""
    logger.info(f"邀请协作者到项目 {project_id}: {request.email}")

    return {"message": "邀请已发送", "email": request.email, "role": request.role.value}


# ============ WebSocket 端点 ============


@router.websocket("/ws/collab/{project_id}")
async def websocket_collab(
    websocket: WebSocket,
    project_id: str,
    user_id: str = "user_123",
    username: str = "Anonymous",
):
    """WebSocket 协作端点"""
    await manager.connect(websocket, project_id, user_id, username)

    try:
        while True:
            data = await websocket.re_json()
            msg_type = data.get("type")

            if msg_type == "cursor_move":
                if (
                    project_id in manager.active_connections
                    and user_id in manager.active_connections[project_id]
                ):
                    manager.active_connections[project_id][user_id]["cursor"] = (
                        data.get("position")
                    )
                    manager.active_connections[project_id][user_id]["last_activity"] = (
                        datetime.utcnow()
                    )

                    await manager.broadcast_to_project(
                        project_id,
                        {
                            "type": "cursor_update",
                            "user_id": user_id,
                            "username": username,
                            "position": data.get("position"),
                        },
                        exclude_user=user_id,
                    )

            elif msg_type == "content_change":
                await manager.broadcast_project_update(
                    project_id,
                    {
                        "action": "content_changed",
                        "user_id": user_id,
                        "username": username,
                        "changes": data.get("changes", {}),
                        "version": data.get("version", 1),
                    },
                )

            elif msg_type == "lock_region":
                await manager.broadcast_project_update(
                    project_id,
                    {
                        "action": "region_locked",
                        "user_id": user_id,
                        "region": data.get("region"),
                    },
                )

            elif msg_type == "unlock_region":
                await manager.broadcast_project_update(
                    project_id,
                    {
                        "action": "region_unlocked",
                        "user_id": user_id,
                        "region": data.get("region"),
                    },
                )

            elif msg_type == "chat_message":
                await manager.broadcast_to_project(
                    project_id,
                    {
                        "type": "chat",
                        "user_id": user_id,
                        "username": username,
                        "message": data.get("message"),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id, user_id, username)
        await manager.broadcast_project_update(
            project_id, {"type": "user_left", "user_id": user_id, "username": username}
        )


# ============ 团队管理 ============


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(user_id: str = "user_123"):
    """获取团队列表"""
    if db.connected:
        cursor = db.db.teams.find({"members.user_id": user_id})
        teams = []
        async for doc in cursor:
            doc.pop("_id", None)
            teams.append(TeamResponse(**doc))
        return teams
    return []


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team_data: TeamCreate, user_id: str = "user_123"):
    """创建团队"""
    team = {
        "id": f"team_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "name": team_data.name,
        "description": team_data.description,
        "owner_id": user_id,
        "members": [
            {"user_id": user_id, "role": "owner", "joined_at": datetime.utcnow()}
        ],
        "projects": [],
        "created_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.teams.insert_one(team)

    return TeamResponse(**team)


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str):
    """获取团队详情"""
    if db.connected:
        team = await db.db.teams.find_one({"id": team_id})
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
            )
        team.pop("_id", None)
        return TeamResponse(**team)

    return TeamResponse(
        id=team_id,
        name="演示团队",
        description="这是一个演示团队",
        owner_id="user_123",
        members=[],
        projects=[],
        created_at=datetime.utcnow(),
    )


@router.post("/teams/{team_id}/members")
async def add_team_member(team_id: str, request: InviteRequest):
    """添加团队成员"""
    return {"message": "成员已添加", "email": request.email, "role": request.role.value}
