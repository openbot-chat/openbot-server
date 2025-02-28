from enum import Enum
from typing import Optional, List
from schemas.base import BaseSchema


class Plan(Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
    LIFETIME = "LIFETIME"
    OFFERED = "OFFERED"
    CUSTOM = "CUSTOM"
    UNLIMITED = "UNLIMITED"


class FeatureType(Enum):
    QUOTA = "QUOTA"
    LOCK = "LOCK"


class PriceSchema(BaseSchema):
    """Price"""

    currency: str
    nickname: Optional[str]
    unit_amount: int
    price_id: str  # 支付网关上配置的 price id
    is_yearly: bool


class FeatureSchema(BaseSchema):
    """Feature"""

    slug: str
    name: Optional[str]
    type: FeatureType
    description: Optional[str]
    quantity: Optional[int | str]  # 数量或inf
    price: Optional[PriceSchema]


class PlanSchema(BaseSchema):
    """Plan"""

    slug: Plan
    name: Optional[str]
    features: Optional[List[FeatureSchema]]
    prices: Optional[List[PriceSchema]]
