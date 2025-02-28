from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema
from .plan import Plan
from .subscription import SubscriptionStatus


class OrgSchemaBase(BaseSchema):
    name: str
    icon: Optional[str]


class CreateOrgSchema(OrgSchemaBase):
    ...


class UpdateOrgSchema(BaseSchema):
    name: Optional[str] = None
    plan: Optional[Plan] = None
    payment_customer_id: Optional[str] = None
    icon: Optional[str] = None


class OrgSchema(OrgSchemaBase):
    """Org"""

    id: UUID
    plan: Plan = Plan.FREE
    payment_customer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # members: Optional[List["OrgMemberSchema"]]
