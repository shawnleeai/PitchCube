"""
海报生成Repository
"""

from typing import Optional, List
from datetime import datetime
from app.db.mongodb import db
from app.models.poster import PosterGeneration, PosterGenerationCreate


class PosterRepository:
    """海报生成数据访问层"""

    collection_name = "poster_generations"

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

    async def get_by_product(self, product_id: str) -> List[dict]:
        cursor = self.collection.find({"product_id": product_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def create(self, poster: PosterGenerationCreate, user_id: str) -> dict:
        """创建海报生成任务"""
        from bson import ObjectId
        from app.models.poster import PosterStatus

        poster_dict = poster.model_dump()
        poster_dict["user_id"] = user_id
        poster_dict["status"] = PosterStatus.PENDING
        poster_dict["id"] = str(ObjectId())
        poster_dict["created_at"] = datetime.utcnow()
        poster_dict["completed_at"] = None
        poster_dict["download_urls"] = {}

        await self.collection.insert_one(poster_dict)
        poster_dict.pop("_id", None)
        return poster_dict

    async def update_status(
        self,
        generation_id: str,
        status: str,
        image_url: str = None,
        thumbnail_url: str = None,
        download_urls: dict = None,
        error_message: str = None,
    ) -> Optional[dict]:
        """更新生成状态"""
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow() if status == "completed" else None,
        }
        if image_url:
            update_data["image_url"] = image_url
        if thumbnail_url:
            update_data["thumbnail_url"] = thumbnail_url
        if download_urls:
            update_data["download_urls"] = download_urls
        if error_message:
            update_data["error_message"] = error_message

        await self.collection.update_one({"id": generation_id}, {"$set": update_data})
        return await self.get_by_id(generation_id)

    async def delete(self, generation_id: str) -> bool:
        result = await self.collection.delete_one({"id": generation_id})
        return result.deleted_count > 0

    async def count_by_user(self, user_id: str) -> int:
        return await self.collection.count_documents({"user_id": user_id})

    async def count_by_status(self, status: str) -> int:
        return await self.collection.count_documents({"status": status})
