"""
WebSocket 协作服务
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from app.core.logging import logger


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_sessions: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """建立连接"""
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()

        self.active_connections[room_id].add(websocket)
        self.user_sessions[id(websocket)] = room_id

        await self.broadcast_message(
            room_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"User {user_id} joined room {room_id}")

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        """断开连接"""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

        self.user_sessions.pop(id(websocket), None)

        logger.info(f"User {user_id} left room {room_id}")

    async def broadcast_message(self, room_id: str, message: dict):
        """广播消息到房间"""
        if room_id in self.active_connections:
            connections_to_remove = []

            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Broadcast error: {e}")
                    connections_to_remove.append(connection)

            for conn in connections_to_remove:
                self.active_connections[room_id].discard(conn)

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Personal message error: {e}")

    def get_room_users(self, room_id: str) -> List[str]:
        """获取房间用户列表"""
        return []

    @property
    def room_count(self) -> int:
        return len(self.active_connections)

    @property
    def total_connections(self) -> int:
        return sum(len(connections) for connections in self.active_connections.values())


class CollaborationService:
    """协作服务"""

    def __init__(self):
        self.manager = ConnectionManager()
        self.document_state: Dict[str, dict] = {}
        self.cursors: Dict[str, dict] = {}

    async def handle_message(
        self, websocket: WebSocket, room_id: str, user_id: str, message: dict
    ):
        """处理协作消息"""
        msg_type = message.get("type")

        if msg_type == "cursor_move":
            await self.handle_cursor_move(room_id, user_id, message)
        elif msg_type == "content_update":
            await self.handle_content_update(room_id, user_id, message)
        elif msg_type == "get_state":
            await self.send_current_state(websocket, room_id)
        elif msg_type == "lock_region":
            await self.handle_lock_region(room_id, user_id, message)
        elif msg_type == "unlock_region":
            await self.handle_unlock_region(room_id, user_id, message)

    async def handle_cursor_move(self, room_id: str, user_id: str, message: dict):
        """处理光标移动"""
        self.cursors[f"{room_id}:{user_id}"] = {
            "x": message.get("x", 0),
            "y": message.get("y", 0),
            "element": message.get("element"),
        }

        await self.manager.broadcast_message(
            room_id,
            {"type": "cursor_update", "user_id": user_id, "cursors": self.cursors},
        )

    async def handle_content_update(self, room_id: str, user_id: str, message: dict):
        """处理内容更新"""
        if room_id not in self.document_state:
            self.document_state[room_id] = {}

        self.document_state[room_id].update(message.get("changes", {}))

        await self.manager.broadcast_message(
            room_id,
            {
                "type": "content_changed",
                "user_id": user_id,
                "changes": message.get("changes", {}),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def send_current_state(self, websocket: WebSocket, room_id: str):
        """发送当前状态"""
        state = self.document_state.get(room_id, {})
        cursors = {k: v for k, v in self.cursors.items() if k.startswith(room_id + ":")}

        await self.manager.send_personal_message(
            websocket,
            {
                "type": "state_sync",
                "state": state,
                "cursors": cursors,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def handle_lock_region(self, room_id: str, user_id: str, message: dict):
        """处理区域锁定"""
        region_id = message.get("region_id")

        await self.manager.broadcast_message(
            room_id,
            {
                "type": "region_locked",
                "region_id": region_id,
                "locked_by": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def handle_unlock_region(self, room_id: str, user_id: str, message: dict):
        """处理区域解锁"""
        region_id = message.get("region_id")

        await self.manager.broadcast_message(
            room_id,
            {
                "type": "region_unlocked",
                "region_id": region_id,
                "unlocked_by": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


collaboration_service = CollaborationService()


async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket 端点"""
    await collaboration_service.manager.connect(websocket, room_id, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            await collaboration_service.handle_message(
                websocket, room_id, user_id, data
            )

    except WebSocketDisconnect:
        collaboration_service.manager.disconnect(websocket, room_id, user_id)
