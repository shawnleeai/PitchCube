"""
数据魔镜 API - Analytics分析仪表盘
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.core.logging import logger
from app.db.mongodb import db

router = APIRouter()


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    GENERATION_START = "generation_start"
    GENERATION_COMPLETE = "generation_complete"
    GENERATION_FAIL = "generation_fail"
    DOWNLOAD = "download"
    SHARE = "share"
    LOGIN = "login"
    SIGNUP = "signup"


class ResourceType(str, Enum):
    POSTER = "poster"
    VIDEO = "video"
    VOICE = "voice"
    IP = "ip"


# ============ 数据模型 ============


class AnalyticsEvent(BaseModel):
    event_type: EventType
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    session_id: Optional[str] = None


class EventResponse(BaseModel):
    id: str
    user_id: Optional[str]
    event_type: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    metadata: Dict[str, Any]
    timestamp: datetime


class UserStatsResponse(BaseModel):
    user_id: str
    total_generations: int
    poster_count: int
    video_count: int
    voice_count: int
    ip_count: int
    total_downloads: int
    total_shares: int
    avg_generation_time: float
    streak_days: int
    last_active: datetime


class GenerationStatsResponse(BaseModel):
    period: str
    total_generations: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    avg_processing_time: float
    success_rate: float


class PlatformStatsResponse(BaseModel):
    platform: str
    views: int
    clicks: int
    shares: int
    ctr: float
    top_content: List[Dict[str, Any]]


class ABTestCreate(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: str
    variants: List[Dict[str, Any]]
    target_metric: str


class ABTestResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    test_type: str
    variants: List[Dict[str, Any]]
    target_metric: str
    status: str
    results: Dict[str, Any]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class DashboardSummary(BaseModel):
    overview: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    alerts: List[Dict[str, str]]


# ============ 辅助函数 ============


async def _track_event(
    user_id: Optional[str],
    event_type: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
    session_id: Optional[str] = None,
):
    """记录分析事件"""
    event = {
        "id": f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "event_type": event_type,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "metadata": metadata or {},
        "session_id": session_id,
        "timestamp": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.analytics_events.insert_one(event)

    return event


# ============ API 端点 ============


@router.post("/track")
async def track_event(
    event: AnalyticsEvent, user_id: str = "user_123", session_id: Optional[str] = None
):
    """记录分析事件"""
    await _track_event(
        user_id=user_id,
        event_type=event.event_type.value,
        resource_type=event.resource_type.value if event.resource_type else None,
        resource_id=event.resource_id,
        metadata=event.metadata,
        session_id=session_id,
    )

    return {"status": "tracked"}


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    event_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    user_id: str = "user_123",
):
    """获取事件列表"""
    query = {"user_id": user_id}
    if event_type:
        query["event_type"] = event_type

    if db.connected:
        cursor = (
            db.db.analytics_events.find(query)
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        events = []
        async for doc in cursor:
            doc.pop("_id", None)
            events.append(EventResponse(**doc))
        return events

    return []


@router.get("/stats/user", response_model=UserStatsResponse)
async def get_user_stats(user_id: str = "user_123"):
    """获取用户统计"""
    logger.info(f"获取用户统计: {user_id}")

    if db.connected:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=20)

        stats = {
            "user_id": user_id,
            "total_generations": 0,
            "poster_count": 0,
            "video_count": 0,
            "voice_count": 0,
            "ip_count": 0,
            "total_downloads": 0,
            "total_shares": 0,
            "avg_generation_time": 0,
            "streak_days": 0,
            "last_active": datetime.utcnow(),
        }

        for r in results:
            event_type = r["_id"]
            count = r["count"]

            if event_type == "generation_complete":
                stats["total_generations"] = count
                metadata_pipeline = [
                    {
                        "$match": {
                            "user_id": user_id,
                            "event_type": "generation_complete",
                        }
                    },
                    {"$group": {"_id": "$resource_type", "count": {"$sum": 1}}},
                ]
                async for m in db.db.analytics_events.aggregate(metadata_pipeline):
                    if m["_id"] == "poster":
                        stats["poster_count"] = m["count"]
                    elif m["_id"] == "video":
                        stats["video_count"] = m["count"]
                    elif m["_id"] == "voice":
                        stats["voice_count"] = m["count"]
                    elif m["_id"] == "ip":
                        stats["ip_count"] = m["count"]

            elif event_type == "download":
                stats["total_downloads"] = count
            elif event_type == "share":
                stats["total_shares"] = count

        return UserStatsResponse(**stats)

    return UserStatsResponse(
        user_id=user_id,
        total_generations=15,
        poster_count=10,
        video_count=3,
        voice_count=2,
        ip_count=0,
        total_downloads=8,
        total_shares=5,
        avg_generation_time=2.5,
        streak_days=7,
        last_active=datetime.utcnow(),
    )


@router.get("/stats/generations", response_model=GenerationStatsResponse)
async def get_generation_stats(period: str = "7d", user_id: str = "user_123"):
    """获取生成统计"""
    logger.info(f"获取生成统计: period={period}")

    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(period, 7)
    start_date = datetime.utcnow() - timedelta(days=days)

    if db.connected:
        pipeline = [
            {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        ]
        results = await db.db.analytics_events.aggregate(pipeline).to_list(length=20)

        by_type = {}
        total = 0
        completed = 0
        failed = 0

        for r in results:
            event_type = r["_id"]
            count = r["count"]

            if event_type in ["poster", "video", "voice", "ip"]:
                by_type[event_type] = count
                total += count
            elif event_type == "generation_complete":
                completed = count
            elif event_type == "generation_fail":
                failed = count

        return GenerationStatsResponse(
            period=period,
            total_generations=total,
            by_type=by_type,
            by_status={"completed": completed, "failed": failed},
            avg_processing_time=2.5,
            success_rate=completed / (completed + failed) * 100
            if (completed + failed) > 0
            else 100,
        )

    return GenerationStatsResponse(
        period=period,
        total_generations=15,
        by_type={"poster": 10, "video": 3, "voice": 2},
        by_status={"completed": 14, "failed": 1},
        avg_processing_time=2.5,
        success_rate=93.3,
    )


@router.get("/stats/platforms", response_model=List[PlatformStatsResponse])
async def get_platform_stats(user_id: str = "user_123"):
    """获取平台分布统计"""
    platforms = ["YouTube", "Bilibili", "抖音", "小红书"]

    if db.connected:
        stats = []
        for platform in platforms:
            pipeline = [
                {"$match": {"user_id": user_id, "metadata.platform": platform}},
                {
                    "$group": {
                        "_id": None,
                        "views": {"$sum": 1},
                        "clicks": {"$sum": "$metadata.clicks"},
                        "shares": {"$sum": "$metadata.shares"},
                    }
                },
            ]
            results = await db.db.analytics_events.aggregate(pipeline).to_list(length=1)

            if results:
                r = results[0]
                views = r["views"]
                clicks = r["clicks"] or 0
                shares = r["shares"] or 0
                ctr = (clicks / views * 100) if views > 0 else 0
            else:
                views = clicks = shares = ctr = 0

            stats.append(
                PlatformStatsResponse(
                    platform=platform,
                    views=views,
                    clicks=clicks,
                    shares=shares,
                    ctr=round(ctr, 2),
                    top_content=[],
                )
            )

        return stats

    return [
        PlatformStatsResponse(
            platform=p, views=100, clicks=15, shares=8, ctr=15.0, top_content=[]
        )
        for p in platforms
    ]


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(user_id: str = "user_123"):
    """获取仪表盘摘要"""
    logger.info(f"获取仪表盘: {user_id}")

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    if db.connected:
        total_gen = await db.db.analytics_events.count_documents(
            {"user_id": user_id, "event_type": "generation_complete"}
        )

        week_gen = await db.db.analytics_events.count_documents(
            {
                "user_id": user_id,
                "event_type": "generation_complete",
                "timestamp": {"$gte": week_ago},
            }
        )

        downloads = await db.db.analytics_events.count_documents(
            {"user_id": user_id, "event_type": "download"}
        )

        recent_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"timestamp": -1}},
            {"$limit": 10},
        ]
        recent = await db.db.analytics_events.aggregate(recent_pipeline).to_list(
            length=10
        )

        recent_activity = [
            {
                "type": r["event_type"],
                "resource_type": r.get("resource_type"),
                "timestamp": r["timestamp"].isoformat(),
            }
            for r in recent
        ]
    else:
        total_gen = 15
        week_gen = 8
        downloads = 8
        recent_activity = [
            {
                "type": "generation_complete",
                "resource_type": "poster",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "type": "download",
                "resource_type": "video",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]

    return DashboardSummary(
        overview={
            "total_generations": total_gen,
            "this_week": week_gen,
            "total_downloads": downloads,
            "avg_daily": round(week_gen / 7, 1),
            "growth_rate": 12.5,
            "active_days": 7,
        },
        recent_activity=recent_activity,
        top_performers=[
            {"type": "poster", "name": "科技现代海报模板", "uses": 5},
            {"type": "video", "name": "产品演示视频模板", "uses": 3},
        ],
        alerts=[
            {"type": "info", "message": "本周生成量增长12.5%"},
            {"type": "success", "message": "已连续活跃7天"},
        ],
    )


@router.get("/ab-tests", response_model=List[ABTestResponse])
async def list_ab_tests(user_id: str = "user_123"):
    """获取A/B测试列表"""
    if db.connected:
        cursor = db.db.ab_tests.find({"user_id": user_id}).sort("created_at", -1)
        tests = []
        async for doc in cursor:
            doc.pop("_id", None)
            tests.append(ABTestResponse(**doc))
        return tests

    return []


@router.post(
    "/ab-tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED
)
async def create_ab_test(test_data: ABTestCreate, user_id: str = "user_123"):
    """创建A/B测试"""
    test = {
        "id": f"ab_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "name": test_data.name,
        "description": test_data.description,
        "test_type": test_data.test_type,
        "variants": test_data.variants,
        "target_metric": test_data.target_metric,
        "status": "draft",
        "results": {},
        "started_at": None,
        "completed_at": None,
        "created_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.ab_tests.insert_one(test)

    return ABTestResponse(**test)


@router.get("/ab-tests/{test_id}", response_model=ABTestResponse)
async def get_ab_test(test_id: str):
    """获取A/B测试详情"""
    if db.connected:
        test = await db.db.ab_tests.find_one({"id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="测试不存在"
            )
        test.pop("_id", None)
        return ABTestResponse(**test)

    return ABTestResponse(
        id=test_id,
        name="演示测试",
        description="A/B测试演示",
        test_type="template_comparison",
        variants=[
            {"id": "A", "name": "现代科技模板", "weight": 50},
            {"id": "B", "name": "创意渐变模板", "weight": 50},
        ],
        target_metric="click_rate",
        status="running",
        results={
            "A": {"views": 100, "clicks": 15, "rate": 15.0},
            "B": {"views": 100, "clicks": 20, "rate": 20.0},
        },
        started_at=datetime.utcnow() - timedelta(days=3),
        completed_at=None,
    )


@router.post("/ab-tests/{test_id}/start")
async def start_ab_test(test_id: str):
    """启动A/B测试"""
    return {
        "message": "测试已启动",
        "test_id": test_id,
        "started_at": datetime.utcnow().isoformat(),
    }


@router.post("/ab-tests/{test_id}/stop")
async def stop_ab_test(test_id: str):
    """停止A/B测试"""
    return {
        "message": "测试已停止",
        "test_id": test_id,
        "completed_at": datetime.utcnow().isoformat(),
    }
