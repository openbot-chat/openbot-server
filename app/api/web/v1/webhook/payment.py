from fastapi import APIRouter, Request, status, HTTPException, Depends
from api.dependencies.payment import xpay
from config import PAYMENT_WEBHOOK_SECRET
from services.subscription_service import SubscriptionService
from services.org_service import OrgService
from models.subscription import (
    CreateSubscriptionSchema,
    UpdateSubscriptionSchema,
    SubscriptionStatus,
)
import logging

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(SubscriptionService),
    org_service: OrgService = Depends(OrgService),
):
    payload = (await request.body()).decode("utf-8")
    received_sig = request.headers.get("XPay-Signature", None)

    try:
        event = xpay.Webhook.construct_event(payload, received_sig, PAYMENT_WEBHOOK_SECRET)

        if event.type == "checkout.session.completed":
            # 订阅支付成功
            session = event.data.object
            org_id = session.metadata.org_id
            plan = session.metadata.plan
            price_id = session.metadata.price_id
            if org_id is not None and plan is not None and price_id is not None:
                await subscription_service.create(
                    create_subscription=CreateSubscriptionSchema(
                        owner=org_id, plan=plan, price_id=price_id
                    )
                )

        elif event.type == "customer.subscription.deleted":
            # 取消订阅
            subscription = event.data.object
            payment_customer_id = subscription.customer
            org = await org_service.query_one(
                filter={"payment_customer_id": payment_customer_id},
            )
            if not org:
                logging.warning(f"org with payment_customer_id {payment_customer_id} not found")
                return

            await subscription_service.delete_by_owner(org.id)

        elif event.type == "customer.subscription.updated":
            # 订阅更新
            subscription = event.data.object
            payment_customer_id = subscription.customer
            subscription_item = subscription.get("items").data[0]
            price_id = subscription_item.price.id
            plan_schema = await subscription_service.get_plan_by_price_id(price_id)
            if plan_schema is None:
                return
            org = await org_service.query_one(
                filter={"payment_customer_id": payment_customer_id},
            )
            if not org:
                return
            if subscription.status == "active":
                # 更新订阅，这里忽略了其他支付的中间状态，只关心最终状态
                await subscription_service.update(
                    update_subscription=UpdateSubscriptionSchema(
                        owner=org.id,
                        plan=plan_schema.slug,
                        status=SubscriptionStatus(subscription.status),
                    )
                )
            elif subscription.status == "unpaid":
                # 续费失败，也有可能进入 unpaid 状态（还可以恢复订阅）
                await subscription_service.delete_by_owner(org.id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "error while decoding event"}
        )
    except xpay.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "signature verification error"},
        )

    logging.info(
        "received payment webhook event: id={id}, type={type}".format(id=event.id, type=event.type)
    )
