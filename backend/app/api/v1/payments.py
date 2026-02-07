"""
支付API路由
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.services.payments.payment_service import payment_service, PLANS, PlanType

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class AlipayOrderRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"


class AlipayOrderResponse(BaseModel):
    pay_url: str
    out_trade_no: str


@router.get("/plans")
async def get_plans():
    """获取所有订阅计划"""
    plans = payment_service.get_all_plans()
    return {
        "plans": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price_monthly": p.price_monthly,
                "price_yearly": p.price_yearly,
                "currency": p.currency,
                "features": p.features,
                "limits": p.limits,
                "is_popular": p.is_popular,
            }
            for p in plans
        ]
    }


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str):
    """获取指定计划"""
    plan = payment_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
        )
    return plan


@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(request: CheckoutRequest, user_id: str = "demo_user"):
    """创建Stripe Checkout会话"""
    try:
        result = await payment_service.create_stripe_checkout(
            user_id=user_id,
            plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
        )
        return CheckoutResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/create-alipay-order", response_model=AlipayOrderResponse)
async def create_alipay_order(request: AlipayOrderRequest, user_id: str = "demo_user"):
    """创建支付宝订单"""
    try:
        result = await payment_service.create_alipay_order(
            user_id=user_id,
            plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
        )
        return AlipayOrderResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/subscription")
async def get_subscription(user_id: str = "demo_user"):
    """获取用户订阅状态"""
    subscription = await payment_service.get_user_subscription(user_id)
    return subscription


@router.post("/cancel")
async def cancel_subscription(user_id: str = "demo_user"):
    """取消订阅"""
    success = await payment_service.cancel_subscription(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel",
        )
    return {"status": "cancelled"}


@router.post("/webhook/stripe")
async def stripe_webhook(payload: bytes, x_stripe_signature: str = None):
    """Stripe Webhook"""
    signature = x_stripe_signature or ""
    result = await payment_service.handle_stripe_webhook(payload, signature)
    return result
