from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.dependencies.auth import get_org_id
from api.dtos.subscription import CheckoutDTO, CheckoutResultDTO, UpgradeDTO, UpgradeResultDTO
from models.plan import Plan, PlanSchema
from models.subscription import (
    CreateSubscriptionSchema,
    UpgradeSubscriptionSchema,
)
from services.subscription_service import SubscriptionService

router = APIRouter()


@router.get("/plans", status_code=200, response_model=List[PlanSchema])
async def list_all_plans(
    subscription_service: SubscriptionService = Depends(SubscriptionService)
):
    """获取所有订阅计划"""
    return await subscription_service.list_all_plans()


@router.post("/plans/{plan}/checkout", status_code=200, response_model=CheckoutResultDTO)
async def checkout(
    plan: Plan,
    req: CheckoutDTO,
    org_id: Optional[UUID] = Depends(get_org_id),
    subscription_service: SubscriptionService = Depends(SubscriptionService),
):
    """发起订阅支付结算"""
    if org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "org_id required"}
        )
    if plan == Plan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "no subscription is required for free plan"},
        )
    subscription = await subscription_service.create(
        create_subscription=CreateSubscriptionSchema(
            owner=org_id,
            plan=plan,
            price_id=req.price_id,
            metadata={
                "needs_checkout": True,
                "success_url": req.success_url,
                "cancel_url": req.cancel_url,
            },
        )
    )
    if subscription.metadata is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "checkout plan error"},
        )
    if subscription.metadata.get("url") is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "checkout plan error"},
        )
    url = str(subscription.metadata.get("url"))
    return CheckoutResultDTO(url=url)


@router.post("/upgrade")
async def update(
    req: UpgradeDTO,
    org_id: Optional[UUID] = Depends(get_org_id),
    subscription_service: SubscriptionService = Depends(SubscriptionService),
):
    """变更订阅计划"""
    if org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "org_id required"}
        )
    if req.plan == Plan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "no subscription is required for free plan"},
        )
    subscription = await subscription_service.upgrade(
        upgrade_subscription=UpgradeSubscriptionSchema(
            owner=org_id,
            plan=req.plan,
            price_id=req.price_id,
            metadata={
                "success_url": req.success_url,
                "cancel_url": req.cancel_url,
            },
        )
    )
    url: str | None = None
    if subscription.metadata is not None and subscription.metadata.get("url") is not None:
        url = str(subscription.metadata.get("url"))
    return UpgradeResultDTO(url=url, plan=subscription.plan)


@router.get("")
async def get_by_org(
    org_id: str = Query(),
    subscription_service: SubscriptionService = Depends(SubscriptionService),
):
    subscription = await subscription_service.get_by_owner(org_id)
    return subscription


@router.get("/portal")
async def get_portal_url_by_org(
    org_id: str = Query(),
    subscription_service: SubscriptionService = Depends(SubscriptionService),
):
    url = await subscription_service.get_portal_by_owner(org_id)
    if url is None:
        return None
    return {"url": url}
