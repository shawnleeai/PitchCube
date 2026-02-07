"""
IP生成Repository
"""

from typing import Optional, List
from datetime import datetime
from app.db.mongodb import db


class IPRepository:
    """IP形象生成数据访问层"""

    collection_name = "ip_generations"

    @property
    def collection(self):
        return db.db[self.collection_name]

    async def get_by_id(self, generation_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"id": generation_id})
        if doc:
            doc.pop("_id", None)
            return doc
        return None

    async def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100, status: str = None
    ) -> List[dict]:
        query = {"user_id": user_id}
        if status:
            query["status"] = status

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def create(self, ip_data: dict, user_id: str) -> dict:
        """创建IP生成任务"""
        from bson import ObjectId
        from app.models.ip import IPStatus

        ip_data["user_id"] = user_id
        ip_data["status"] = IPStatus.PENDING
        ip_data["id"] = str(ObjectId())
        ip_data["created_at"] = datetime.utcnow()
        ip_data["completed_at"] = None
        ip_data.pop("_id", None)

        await self.collection.insert_one(ip_data)
        return ip_data

    async def update_status(
        self,
        generation_id: str,
        status: str,
        concept: dict = None,
        image_url: str = None,
        model_3d_url: str = None,
        print_guide: dict = None,
        error_message: str = None,
    ) -> Optional[dict]:
        """更新生成状态"""
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow() if status == "completed" else None,
        }
        if concept:
            update_data["concept"] = concept
        if image_url:
            update_data["image_url"] = image_url
        if model_3d_url:
            update_data["model_3d_url"] = model_3d_url
        if print_guide:
            update_data["print_guide"] = print_guide
        if error_message:
            update_data["error_message"] = error_message

        await self.collection.update_one({"id": generation_id}, {"$set": update_data})
        return await self.get_by_id(generation_id)

    async def delete(self, generation_id: str) -> bool:
        result = await self.collection.delete_one({"id": generation_id})
        return result.deleted_count > 0
