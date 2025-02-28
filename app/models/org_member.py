from datetime import datetime
from uuid import UUID

from schemas.base import BaseSchema
from .user import UserSchema


class OrgMemberSchemaBase(BaseSchema):
    role: str
    org_id: UUID
    user: UserSchema
    user_id: UUID

class CreateOrgMemberSchema(BaseSchema):
    role: str
    org_id: UUID
    user_id: UUID

class UpdateOrgMemberSchema(BaseSchema):
    role: str

class OrgMemberSchema(OrgMemberSchemaBase):
    """OrgMember"""
    id: UUID
    created_at: datetime
    updated_at: datetime