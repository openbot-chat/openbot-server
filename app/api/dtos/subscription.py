from typing import Optional
from pydantic import BaseModel
from models.subscription import Plan


class CheckoutDTO(BaseModel):
    # 指定价格
    price_id: Optional[str] = None
    # 支付成功后返回的地址
    success_url: str
    # 取消支付后返回的地址
    cancel_url: Optional[str] = None


class CheckoutResultDTO(BaseModel):
    # 支付链接，前端重定向到该链接进行支付
    url: str


class UpgradeDTO(BaseModel):
    # 变更到该计划
    plan: Plan
    # 指定价格
    price_id: Optional[str] = None
    # 支付成功后返回的地址
    success_url: str
    # 取消支付后返回的地址
    cancel_url: Optional[str] = None


class UpgradeResultDTO(BaseModel):
    # 支付链接，前端重定向到该链接进行支付
    url: Optional[str] = None
    # 变更到该计划
    plan: Plan
