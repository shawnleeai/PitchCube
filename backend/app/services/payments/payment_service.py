"""
支付服务 - 支持Stripe和支付宝
"""

import os
import uuid
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    ALIPAY = "alipay"


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    description: str
    price_monthly: int
    price_yearly: int
    currency: str = "cny"
    features: list
    limits: dict
    is_popular: bool = False


PLANS = {
    PlanType.FREE: SubscriptionPlan(
        id="free",
        name="免费版",
        description="适合个人试用",
        price_monthly=0,
        price_yearly=0,
        features=["每月5张海报", "1个视频", "基础模板", "720p导出"],
        limits={
            "posters_per_month": 5,
            "videos_per_month": 1,
            "max_resolution": "720p",
            "team_members": 1,
        },
    ),
    PlanType.PRO: SubscriptionPlan(
        id="pro",
        name="专业版",
        description="适合创作者和专业团队",
        price_monthly=2990,
        price_yearly=29900,
        features=[
            "无限海报生成",
            "20个视频/月",
            "高级模板",
            "4K导出",
            "去水印",
            "优先支持",
        ],
        limits={
            "posters_per_month": -1,
            "videos_per_month": 20,
            "max_resolution": "4K",
            "remove_watermark": True,
            "team_members": 1,
        },
        is_popular=True,
    ),
    PlanType.TEAM: SubscriptionPlan(
        id="team",
        name="团队版",
        description="适合团队协作",
        price_monthly=9990,
        price_yearly=99900,
        features=[
            "无限生成",
            "无限视频",
            "全部模板",
            "4K导出",
            "团队协作",
            "API访问",
            "专属客服",
        ],
        limits={
            "posters_per_month": -1,
            "videos_per_month": -1,
            "max_resolution": "4K",
            "remove_watermark": True,
            "team_members": 5,
            "api_access": True,
        },
    ),
}


class PaymentService:
    """支付服务"""

    def __init__(self):
        self.stripe_secret_key = settings.STRIPE_SECRET_KEY
        self.alipay_app_id = settings.ALIPAY_APP_ID
        self.alipay_private_key = settings.ALIPAY_PRIVATE_KEY
        self.alipay_public_key = settings.ALIPAY_PUBLIC_KEY

    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        return PLANS.get(PlanType(plan_id))

    def get_all_plans(self) -> list:
        return list(PLANS.values())

    async def create_stripe_checkout(
        self, user_id: str, plan_id: str, billing_cycle: str = "monthly"
    ) -> Dict[str, Any]:
        """创建Stripe Checkout会话"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan: {plan_id}")

        if not self.stripe_secret_key:
            return self._create_mock_checkout(plan, user_id, billing_cycle)

        try:
            import stripe

            stripe.api_key = self.stripe_secret_key

            price_key = f"price_{plan_id}_{billing_cycle}"

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "cny",
                            "product_data": {
                                "name": plan.name,
                                "description": plan.description,
                            },
                            "unit_amount": plan.price_monthly
                            if billing_cycle == "monthly"
                            else plan.price_yearly,
                            "recurring": {"interval": billing_cycle},
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/subscription/cancel",
                metadata={"user_id": user_id, "plan_id": plan_id},
            )

            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
            }

        except Exception as e:
            logger.error(f"Stripe checkout failed: {e}")
            return self._create_mock_checkout(plan, user_id, billing_cycle)

    def _create_mock_checkout(
        self, plan: SubscriptionPlan, user_id: str, billing_cycle: str
    ) -> Dict[str, Any]:
        """创建模拟Checkout（用于测试）"""
        return {
            "checkout_url": f"{settings.FRONTEND_URL}/subscription/mock-success?plan={plan.id}&user={user_id}",
            "session_id": f"mock_{uuid.uuid4().hex[:16]}",
            "note": "Mock checkout - Stripe not configured",
        }

    async def create_alipay_order(
        self, user_id: str, plan_id: str, billing_cycle: str = "monthly"
    ) -> Dict[str, Any]:
        """创建支付宝订单"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan: {plan_id}")

        if not self.alipay_app_id:
            return self._create_mock_alipay(plan, user_id)

        amount = plan.price_monthly if billing_cycle == "monthly" else plan.price_yearly
        out_trade_no = f"ALI_{uuid.uuid4().hex[:16]}"

        order_data = {
            "out_trade_no": out_trade_no,
            "total_amount": amount / 100,
            "subject": f"{plan.name} - {billing_cycle}",
            "body": f"PitchCube {plan.name} Subscription",
            "notify_url": f"{settings.API_URL}/payments/alipay/notify",
        }

        signed_params = self._sign_alipay_params(order_data)

        return {
            "pay_url": f"https://openapi.alipay.com/gateway.do?{signed_params}",
            "out_trade_no": out_trade_no,
        }

    def _create_mock_alipay(
        self, plan: SubscriptionPlan, user_id: str
    ) -> Dict[str, Any]:
        """模拟支付宝订单"""
        return {
            "pay_url": f"{settings.FRONTEND_URL}/subscription/mock-success?plan={plan.id}&user={user_id}",
            "out_trade_no": f"mock_{uuid.uuid4().hex[:16]}",
            "note": "Mock alipay - Alipay not configured",
        }

    def _sign_alipay_params(self, params: dict) -> str:
        """签名支付宝参数"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string += f"&key={self.alipay_private_key}"

        sign = (
            hmac.new(
                self.alipay_private_key.encode(), sign_string.encode(), hashlib.md5
            )
            .hexdigest()
            .upper()
        )

        return f"{sign_string}&sign={sign}"

    async def handle_stripe_webhook(
        self, payload: bytes, signature: str
    ) -> Dict[str, Any]:
        """处理Stripe Webhook"""
        if not self.stripe_secret_key:
            return {"status": "ignored", "reason": "Stripe not configured"}

        try:
            import stripe

            webhook_secret = settings.STRIPE_WEBHOOK_SECRET

            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)

            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                user_id = session.get("metadata", {}).get("user_id")
                plan_id = session.get("metadata", {}).get("plan_id")

                await self._activate_subscription(
                    user_id, plan_id, "stripe", session.get("id")
                )

                return {"status": "success", "action": "subscription_activated"}

            return {"status": "received", "type": event["type"]}

        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            return {"status": "error", "message": str(e)}

    async def _activate_subscription(
        self, user_id: str, plan_id: str, provider: str, transaction_id: str
    ):
        """激活订阅"""
        from app.db.mongodb import db

        subscription = {
            "user_id": user_id,
            "plan_id": plan_id,
            "provider": provider,
            "transaction_id": transaction_id,
            "status": "active",
            "started_at": datetime.utcnow(),
            "current_period_start": datetime.utcnow(),
        }

        await db.db.subscriptions.update_one(
            {"user_id": user_id}, {"$set": subscription}, upsert=True
        )

        logger.info(f"Subscription activated: user={user_id}, plan={plan_id}")

    async def cancel_subscription(self, user_id: str) -> bool:
        """取消订阅"""
        from app.db.mongodb import db

        result = await db.db.subscriptions.update_one(
            {"user_id": user_id, "status": "active"},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.utcnow()}},
        )

        return result.modified_count > 0

    async def get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """获取用户订阅"""
        from app.db.mongodb import db

        sub = await db.db.subscriptions.find_one(
            {"user_id": user_id, "status": "active"}
        )

        if sub:
            sub.pop("_id", None)
            plan = self.get_plan(sub.get("plan_id", "free"))
            if plan:
                sub["plan_details"] = plan.model_dump()

        return sub or {"plan_id": "free", "status": "none"}

    def check_plan_limits(
        self, subscription: Dict, resource_type: str
    ) -> Dict[str, Any]:
        """检查计划限制"""
        plan_id = subscription.get("plan_id", "free")
        plan = self.get_plan(plan_id)

        if not plan:
            plan = self.get_plan("free")

        limits = plan.limits

        if resource_type == "poster":
            current_count = subscription.get("poster_count", 0)
            limit = limits.get("posters_per_month", 5)
            return {
                "allowed": limit == -1 or current_count < limit,
                "current": current_count,
                "limit": limit,
                "reset_date": subscription.get("current_period_start"),
            }

        return {"allowed": True, "current": 0, "limit": -1}


payment_service = PaymentService()
