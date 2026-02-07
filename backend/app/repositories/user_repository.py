"""
用户Repository
"""

from typing import Optional, List
from datetime import datetime
from app.db.mongodb import db
from app.models.user import User, UserCreate, UserUpdate, UserInDB


class UserRepository:
    """用户数据访问层"""

    collection_name = "users"

    @property
    def collection(self):
        return db.db[self.collection_name]

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"id": user_id})
        if doc:
            doc.pop("_id", None)
            return UserInDB(**doc)
        return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"email": email})
        if doc:
            doc.pop("_id", None)
            return UserInDB(**doc)
        return None

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"username": username})
        if doc:
            doc.pop("_id", None)
            return UserInDB(**doc)
        return None

    async def create(self, user: UserCreate) -> UserInDB:
        """创建用户"""
        user_dict = user.model_dump()
        user_dict["hashed_password"] = user_dict.pop("password")
        user_dict.pop("confirm_password", None)
        user_dict["id"] = user_dict.get("id") or self._generate_id()

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id

        user_dict.pop("_id", None)
        return UserInDB(**user_dict)

    async def update(self, user_id: str, update_data: UserUpdate) -> Optional[UserInDB]:
        """更新用户"""
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            await self.collection.update_one({"id": user_id}, {"$set": update_dict})
            return await self.get_by_id(user_id)
        return await self.get_by_id(user_id)

    async def update_login_time(self, user_id: str) -> None:
        """更新最后登录时间"""
        await self.collection.update_one(
            {"id": user_id}, {"$set": {"last_login_at": datetime.utcnow()}}
        )

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    async def list_users(
        self, skip: int = 0, limit: int = 100, is_active: bool = None
    ) -> List[UserInDB]:
        """用户列表"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active

        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc.pop("_id", None)

        return [UserInDB(**doc) for doc in docs]

    async def count(self, query: dict = None) -> int:
        return await self.collection.count_documents(query or {})

    def _generate_id(self) -> str:
        from bson import ObjectId

        return str(ObjectId())
