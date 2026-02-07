"""
产品Repository
"""

from typing import Optional, List
from datetime import datetime
from app.db.mongodb import db
from app.models.product import Product, ProductCreate, ProductUpdate


class ProductRepository:
    """产品数据访问层"""

    collection_name = "products"

    @property
    def collection(self):
        return db.db[self.collection_name]

    async def get_by_id(self, product_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"id": product_id})
        if doc:
            doc.pop("_id", None)
            return doc
        return None

    async def get_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def create(self, product: ProductCreate, user_id: str) -> dict:
        """创建产品"""
        product_dict = product.model_dump()
        product_dict["user_id"] = user_id
        product_dict["poster_count"] = 0
        product_dict["video_count"] = 0

        from bson import ObjectId

        product_dict["id"] = str(ObjectId())
        product_dict["created_at"] = datetime.utcnow()
        product_dict["updated_at"] = datetime.utcnow()

        await self.collection.insert_one(product_dict)
        product_dict.pop("_id", None)
        return product_dict

    async def update(
        self, product_id: str, update_data: ProductUpdate
    ) -> Optional[dict]:
        """更新产品"""
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            await self.collection.update_one({"id": product_id}, {"$set": update_dict})
            return await self.get_by_id(product_id)
        return await self.get_by_id(product_id)

    async def delete(self, product_id: str) -> bool:
        result = await self.collection.delete_one({"id": product_id})
        return result.deleted_count > 0

    async def increment_poster_count(self, product_id: str) -> None:
        await self.collection.update_one(
            {"id": product_id}, {"$inc": {"poster_count": 1}}
        )

    async def increment_video_count(self, product_id: str) -> None:
        await self.collection.update_one(
            {"id": product_id}, {"$inc": {"video_count": 1}}
        )

    async def count_by_user(self, user_id: str) -> int:
        return await self.collection.count_documents({"user_id": user_id})
