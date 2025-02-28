import json
from uuid import UUID

from typing import List, Dict, Any
from pydantic import parse_obj_as
from fastapi import Depends, HTTPException, status

from config import PAYMENT_PLAN
from api.dependencies.repository import make_repository
from api.dependencies.payment import xpay
from models.plan import Plan, PlanSchema, PriceSchema
from models.org import OrgSchema, UpdateOrgSchema
from models.subscription import (
    SubscriptionStatus,
    SubscriptionSchema,
    CreateSubscriptionSchema,
    UpgradeSubscriptionSchema,
    UpdateSubscriptionSchema,
)
from repositories.sqlalchemy.org_repository import OrgRepository
from datetime import datetime


class SubscriptionService:
    def __init__(
        self,
        org_repository: OrgRepository = Depends(make_repository(OrgRepository)),
    ) -> None:
        config_name = PAYMENT_PLAN if PAYMENT_PLAN else "plans.json"
        with open(f"configs/{config_name}") as file:
            self.plans = parse_obj_as(List[PlanSchema], json.load(file))
        self.org_repository = org_repository

    async def list_all_plans(self) -> List[PlanSchema]:
        """获取所有订阅计划"""
        return self.plans

    async def get_plan_by_price_id(self, price_id: str) -> PlanSchema | None:
        """查询价格对应的订阅计划"""
        for plan in self.plans:
            if plan.prices is None:
                continue
            for price in plan.prices:
                if price.price_id == price_id:
                    return plan
        return None

    async def get_price_by_price_id(self, price_id: str) -> PriceSchema | None:
        """查询价格对应的价格信息"""
        for plan in self.plans:
            if plan.prices is None:
                continue
            for price in plan.prices:
                if price.price_id == price_id:
                    return price
        return None

    async def create(self, create_subscription: CreateSubscriptionSchema) -> SubscriptionSchema:
        """创建新的订阅"""
        # 检查计划是否存在
        plan_schema = next((x for x in self.plans if x.slug == create_subscription.plan), None)
        if plan_schema is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "unknown plan"}
            )
        # 计划必须要有订阅价格
        if plan_schema.prices is None or len(plan_schema.prices) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "plan has no price"}
            )
        # 检查订阅的价格是否存在
        price_schema: PriceSchema | None = None
        if create_subscription.price_id is not None:
            price_schema = next(
                (x for x in plan_schema.prices if x.price_id == create_subscription.price_id), None
            )
        else:
            price_schema = plan_schema.prices[0]
        if price_schema is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "invalid price_id"}
            )
        # 检查租户是否存在
        org = await self.org_repository.get_by_id(create_subscription.owner)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail={"error": "org not found"}
            )

        # 如果租户已经订阅过，要调用更新接口来变更计划
        if org.plan != Plan.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "subscription already exists. to upgrade or downgrade, please update subscription instead"
                },
            )

        # 如果需要到支付网关进行结算，就生成支付信息
        if create_subscription.metadata is not None:
            needs_checkout = create_subscription.metadata.get("needs_checkout")
            if needs_checkout is not None and bool(needs_checkout) is True:
                return await self._checkout(
                    org=org,
                    plan=plan_schema,
                    price=price_schema,
                    extra=create_subscription.metadata,
                )

        # 不需要结算，直接更新租户订阅的计划
        await self.org_repository.update_by_id(
            org.id,
            UpdateOrgSchema(plan=create_subscription.plan),
        )
        return SubscriptionSchema(
            owner=create_subscription.owner,
            plan=create_subscription.plan,
            price_id=create_subscription.price_id,
            status=SubscriptionStatus.ACTIVE,
            metadata=create_subscription.metadata,
        )

    async def delete_by_owner(self, owner: UUID):
        """删除订阅"""
        await self.org_repository.update_by_id(owner, UpdateOrgSchema(plan=Plan.FREE))

    async def update(self, update_subscription: UpdateSubscriptionSchema) -> SubscriptionSchema:
        """更新订阅信息"""
        # 检查租户是否存在
        org = await self.org_repository.get_by_id(update_subscription.owner)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail={"error": "org not found"}
            )
        # 直接更新
        await self.org_repository.update_by_id(
            org.id,
            UpdateOrgSchema(plan=update_subscription.plan),
        )
        return SubscriptionSchema(
            owner=org.id,
            plan=update_subscription.plan,
            status=update_subscription.status,
        )

    async def upgrade(self, upgrade_subscription: UpgradeSubscriptionSchema) -> SubscriptionSchema:
        """变更订阅计划"""
        # 检查新的计划是否存在
        new_plan_schema = next((x for x in self.plans if x.slug == upgrade_subscription.plan), None)
        if new_plan_schema is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "unknown plan"}
            )
        new_plan = new_plan_schema.slug
        # 新计划必须要有订阅价格
        if new_plan_schema.prices is None or len(new_plan_schema.prices) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "plan has no price"}
            )
        # 检查变更的价格是否存在
        new_price_schema: PriceSchema | None = None
        if upgrade_subscription.price_id is not None:
            new_price_schema = next(
                (x for x in new_plan_schema.prices if x.price_id == upgrade_subscription.price_id),
                None,
            )
        else:
            new_price_schema = new_plan_schema.prices[0]
        if new_price_schema is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "invalid price_id"}
            )
        new_price_id = new_price_schema.price_id
        # 检查租户是否存在
        org = await self.org_repository.get_by_id(upgrade_subscription.owner)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail={"error": "org not found"}
            )
        # 之前订阅过，所以肯定要有 payment_customer_id
        if org.payment_customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "org has no payment customer"},
            )

        # 从支付网关获取当前的订阅
        subscription_list_result = xpay.Subscription.list(
            customer=org.payment_customer_id, status="active", limit=1
        )
        subscription_list = subscription_list_result.data
        subscription = subscription_list[0] if len(subscription_list) > 0 else None

        # 当前没有订阅，就发起一个新的订阅支付
        if subscription is None:
            return await self._checkout(
                org=org,
                plan=new_plan_schema,
                price=new_price_schema,
                extra=upgrade_subscription.metadata or {},
            )

        # 当前订阅存在，通过 price_id 来判断是哪个计划
        if len(subscription.get("items").data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "no subscription item"},
            )
        subscription_item = subscription.get("items").data[0]
        current_price_id = subscription_item.price.id
        current_plan_schema = await self.get_plan_by_price_id(current_price_id)
        if current_plan_schema is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "subscription item plan error"},
            )
        current_plan = current_plan_schema.slug

        # 计划没有变化，直接报错
        if current_plan == new_plan and current_price_id == new_price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "new plan remains the same"},
            )

        # 判断是升级还是降级
        plan_orders = [Plan.FREE, Plan.STARTER, Plan.PRO, Plan.ENTERPRISE]  # 升级的顺序
        upgrade = plan_orders.index(new_plan) >= plan_orders.index(current_plan)

        # 调用支付网关更新订阅
        subscription = xpay.Subscription.modify(
            id=subscription.id,
            items=[{"id": subscription_item.id, "price": new_price_id, "quantity": 1}],
            # 如果是升级就自动扣款，如果是降级就生成均摊
            proration_behavior="always_invoice" if upgrade else "create_prorations",
        )
        cancel_at = (
            datetime.fromtimestamp(subscription.get("cancel_at"))
            if subscription.get("cancel_at") is not None
            else None
        )
        # 网关更新成功，直接更新本地
        # 这里有几种情况
        # 1. 变更后扣费成功了, 状态是 active
        # 2. 变更后扣费失败了, 状态是 past_due, 后续如果扣费成功变成 active, 最终失败进入 canceled 或者 unpaid
        # 无论哪一种情况，都认为订阅已经更新了
        await self.org_repository.update_by_id(org.id, UpdateOrgSchema(plan=new_plan))
        return SubscriptionSchema(
            owner=org.id,
            plan=new_plan,
            price_id=new_price_schema.price_id,
            cancel_at=cancel_at,
            status=SubscriptionStatus(subscription.status),
        )

    async def get_by_owner(self, owner: str) -> SubscriptionSchema | None:
        # 检查租户是否存在
        org = await self.org_repository.get_by_id(owner)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail={"error": "org not found"}
            )
        if org.payment_customer_id is None:
            return None
        # 从支付网关获取当前的订阅
        subscription_list_result = xpay.Subscription.list(customer=org.payment_customer_id)
        subscription_list = subscription_list_result.data
        subscription_list.sort(key=lambda x: x.created)
        subscription = next(
            (x for x in subscription_list if x.status == "active" or x.status == "past_due"), None
        )
        if subscription is None:
            return None
        # 通过 price_id 来判断是哪个计划
        if len(subscription.get("items").data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "no subscription item"},
            )
        subscription_item = subscription.get("items").data[0]
        price_id = subscription_item.price.id
        plan_schema = await self.get_plan_by_price_id(price_id=price_id)
        price_schema = await self.get_price_by_price_id(price_id=price_id)
        if plan_schema is None or price_schema is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "subscription item plan error"},
            )
        # 返回订阅信息
        cancel_at = (
            datetime.fromtimestamp(subscription.get("cancel_at"))
            if subscription.get("cancel_at") is not None
            else None
        )
        start_at = (
            datetime.fromtimestamp(subscription.get("current_period_start"))
            if subscription.get("current_period_start") is not None
            else None
        )
        end_at = (
            datetime.fromtimestamp(subscription.get("current_period_end"))
            if subscription.get("current_period_end") is not None
            else None
        )
        return SubscriptionSchema(
            owner=UUID(owner),
            plan=plan_schema.slug,
            price_id=price_id,
            start_at=start_at,
            end_at=end_at,
            cancel_at=cancel_at,
            status=SubscriptionStatus(subscription.status),
            is_yearly=price_schema.is_yearly,
        )

    async def get_portal_by_owner(self, owner: str) -> str | None:
        # 检查租户是否存在
        org = await self.org_repository.get_by_id(owner)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail={"error": "org not found"}
            )
        if org.payment_customer_id is None:
            return None
        portal_session = xpay.billing_portal.Session.create(customer=org.payment_customer_id)
        return portal_session.url

    async def _checkout(
        self, org: OrgSchema, plan: PlanSchema, price: PriceSchema, extra: Dict[str, Any]
    ) -> SubscriptionSchema:
        """发起订阅支付结算"""
        # 需要在支付网关创建一个和租户关联的支付客户
        payment_customer_id = org.payment_customer_id
        if payment_customer_id is None:
            payment_customer = xpay.Customer.create(metadata={"org_id": str(org.id)})
            payment_customer_id = payment_customer.id
            await self.org_repository.update_by_id(
                org.id, UpdateOrgSchema(payment_customer_id=payment_customer_id)
            )

        success_url = extra.get("success_url")
        cancel_url = extra.get("cancel_url")
        if success_url is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "checkout needs success_url"},
            )
        cancel_url = str(cancel_url) if cancel_url is not None else ""

        # 在支付网关创建结算会话
        checkout_session = xpay.checkout.Session.create(
            customer=payment_customer_id,
            mode="subscription",
            currency=price.currency,
            line_items=[{"price": price.price_id, "quantity": 1}],
            metadata={
                "org_id": str(org.id),
                "plan": plan.slug.name,
                "price_id": price.price_id,
            },
            success_url=success_url,
            cancel_url=cancel_url,
            # allow_promotion_codes=True,
            # customer_update={"address": "auto", "name": "never"},
            # billing_address_collection="required"
            # automatic_tax={"enabled": True},
        )
        if checkout_session.url is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "create subscription checkout session error"},
            )
        return SubscriptionSchema(
            owner=org.id,
            plan=plan.slug,
            price_id=price.price_id,
            metadata={"url": checkout_session.url},
            status=SubscriptionStatus.INCOMPLETE,
        )
