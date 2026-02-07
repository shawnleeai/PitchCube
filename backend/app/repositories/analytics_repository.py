"""
Analytics Repository
"""

from typing import Optional, List
from datetime import datetime, timedelta
from app.db.mongodb import db
from app.models.analytics import AnalyticsEvent, ABTest, ABTestCreate


class AnalyticsRepository:
    """数据分析数据访问层"""

    collection_name = "analytics_events"
    ab_tests_collection = "ab_tests"

    @property
    def collection(self):
        return db.db[self.collection_name]

    @property
    def ab_tests(self):
        return db.db[self.ab_tests_collection]

    async def track_event(self, event: AnalyticsEvent) -> None:
        """记录事件"""
        event_dict = event.model_dump()
        event_dict.pop("id", None)
        await self.collection.insert_one(event_dict)

    async def get_user_events(
        self,
        user_id: str,
        event_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100,
    ) -> List[dict]:
        """用户事件列表"""
        query = {"user_id": user_id}
        if event_type:
            query["event_type"] = event_type
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def count_events(
        self, event_type: str = None, user_id: str = None, start_date: datetime = None
    ) -> int:
        """事件计数"""
        query = {}
        if event_type:
            query["event_type"] = event_type
        if user_id:
            query["user_id"] = user_id
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        return await self.collection.count_documents(query)

    async def get_generation_stats(self, user_id: str) -> dict:
        """用户生成统计"""
        pipeline = [
            {"$match": {"user_id": user_id, "event_type": "generation_complete"}},
            {"$group": {"_id": "$generation_type", "count": {"$sum": 1}}},
        ]
        results = await self.collection.aggregate(pipeline).to_list(length=10)

        stats = {
            "poster_count": 0,
            "video_count": 0,
            "voice_count": 0,
            "ip_count": 0,
            "total": 0,
        }
        for r in results:
            gen_type = r["_id"]
            count = r["count"]
            stats[gen_type + "_count"] = count
            stats["total"] += count

        return stats

    async def get_daily_stats(self, days: int = 7) -> List[dict]:
        """每日统计"""
        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                    },
                    "events": {"$sum": 1},
                    "generations": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$event_type", "generation_complete"]},
                                1,
                                0,
                            ]
                        }
                    },
                }
            },
            {"$sort": {"_id": 1}},
        ]
        results = await self.collection.aggregate(pipeline).to_list(length=days)
        return results

    async def create_ab_test(self, test: ABTestCreate, user_id: str) -> dict:
        """创建A/B测试"""
        from bson import ObjectId

        test_dict = test.model_dump()
        test_dict["user_id"] = user_id
        test_dict["status"] = "draft"
        test_dict["results"] = {}
        test_dict["id"] = str(ObjectId())
        test_dict["created_at"] = datetime.utcnow()
        test_dict["updated_at"] = datetime.utcnow()

        await self.ab_tests.insert_one(test_dict)
        test_dict.pop("_id", None)
        return test_dict

    async def get_ab_test(self, test_id: str) -> Optional[dict]:
        doc = await self.ab_tests.find_one({"id": test_id})
        if doc:
            doc.pop("_id", None)
            return doc
        return None

    async def list_ab_tests(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[dict]:
        cursor = (
            self.ab_tests.find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop("_id", None)
        return docs
