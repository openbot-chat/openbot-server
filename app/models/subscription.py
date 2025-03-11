from typing import Optional, Dict, Any
from pydantic import Field
from uuid import UUID
from schemas.base import BaseSchema
from .plan import Plan
from enum import Enum
from datetime import datetime


class SubscriptionStatus(Enum):
    # 订阅已生效
    ACTIVE = "active"
    # 第一次订阅时, 在初次支付成功前，进入该状态
    INCOMPLETE = "incomplete"
    # 第一次订阅最终失败时进入该状态
    INCOMPLETE_EXPIRED = "incomplete_expired"
    # 试用
    TRIALING = "trialing"
    # 等待支付, 续费或者升级时，如果需要支付，但是支付失败了，进入该状态. 后续最终支付成功转为 active, 最终失败会取消订阅
    PAST_DUE = "past_due"
    # 订阅已取消
    CANCELED = "canceled"
    # 续费失败进入该状态
    UNPAID = "unpaid"


class SubscriptionSchema(BaseSchema):
    # 订阅人
    owner: UUID
    # 订阅的计划
    plan: Plan
    # 支付价格ID
    price_id: Optional[str] = None
    # 订阅状态
    status: SubscriptionStatus
    # 订阅当期开始时间
    start_at: Optional[datetime] = None
    # 订阅当期结束时间
    end_at: Optional[datetime] = None
    # 订阅将会取消的时间
    cancel_at: Optional[datetime] = None
    # 是否按年订阅
    is_yearly: Optional[bool] = None
    # 扩展信息
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CreateSubscriptionSchema(BaseSchema):
    # 订阅人
    owner: UUID
    # 订阅的计划
    plan: Plan
    # 支付价格ID
    price_id: Optional[str]
    # 扩展信息
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpgradeSubscriptionSchema(CreateSubscriptionSchema):
    ...


class UpdateSubscriptionSchema(BaseSchema):
    # 订阅人
    owner: UUID
    # 订阅的计划
    plan: Plan
    # 状态
    status: SubscriptionStatus
