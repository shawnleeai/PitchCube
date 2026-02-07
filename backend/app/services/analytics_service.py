"""
数据分析服务
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.db.mongodb import db
from app.core.logging import logger


class AnalyticsService:
    """数据分析服务"""

    async def track_event(
        self,
        user_id: Optional[str],
        event_type: str,
        generation_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None,
    ):
        """追踪事件"""
        event = {
            "user_id": user_id,
            "event_type": event_type,
            "generation_type": generation_type,
            "resource_id": resource_id,
            "metadata": metadata or {},
            "session_id": session_id,
            "timestamp": datetime.utcnow(),
        }

        try:
            await db.db.analytics_events.insert_one(event)
        except Exception as e:
            logger.error(f"Failed to track event: {e}")

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=20)

        stats = {
            "total_events": 0,
            "generation_complete": 0,
            "generation_start": 0,
            "downloads": 0,
            "shares": 0,
        }

        for r in results:
            event_type = r["_id"]
            count = r["count"]
            stats[event_type] = count
            stats["total_events"] += count

        return stats

    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """用户洞察"""
        last_30_days = datetime.utcnow() - timedelta(days=30)

        pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": last_30_days}}},
            {
                "$group": {
                    "_id": {
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp",
                            }
                        },
                        "event_type": "$event_type",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.date": 1}},
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=500)

        daily_breakdown = {}
        for r in results:
            date = r["_id"]["date"]
            event_type = r["_id"]["event_type"]
            if date not in daily_breakdown:
                daily_breakdown[date] = {}
            daily_breakdown[date][event_type] = r["count"]

        return {"daily_breakdown": daily_breakdown, "period": "30天"}

    async def get_platform_stats(self, platform: str) -> Dict[str, Any]:
        """平台统计"""
        start_of_day = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
        start_of_month = start_of_day.replace(day=1)

        stats = {}
        for period, start in [
            ("daily", start_of_day),
            ("weekly", start_of_week),
            ("monthly", start_of_month),
        ]:
            count = await db.db.analytics_events.count_documents(
                {"metadata.target_platform": platform, "timestamp": {"$gte": start}}
            )
            stats[period] = count

        return stats

    async def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """热门模板"""
        pipeline = [
            {
                "$match": {
                    "event_type": "generation_complete",
                    "generation_type": "poster",
                }
            },
            {
                "$group": {
                    "_id": "$metadata.template_id",
                    "count": {"$sum": 1},
                    "avg_processing_time": {"$avg": "$metadata.processing_time"},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=limit)

        return [
            {
                "template_id": r["_id"],
                "count": r["count"],
                "avg_time": r.get("avg_processing_time"),
            }
            for r in results
        ]

    async def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """A/B测试结果"""
        pipeline = [
            {
                "$match": {
                    "metadata.test_id": test_id,
                    "event_type": "generation_complete",
                }
            },
            {
                "$group": {
                    "_id": {
                        "variant": "$metadata.variant_id",
                        "metric": "$metadata.metric",
                    },
                    "count": {"$sum": 1},
                    "conversion_rate": {"$avg": "$metadata.converted"},
                }
            },
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=100)

        variants = {}
        for r in results:
            variant = r["_id"]["variant"]
            metric = r["_id"]["metric"]
            if variant not in variants:
                variants[variant] = {}
            variants[variant][metric] = {
                "count": r["count"],
                "rate": r.get("conversion_rate", 0),
            }

        return {"variants": variants, "test_id": test_id}


analytics_service = AnalyticsService()
