from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from schemas.base import BaseSchema

from .account import AccountSchema
# from .org_member import OrgMemberSchema

class UserSchemaBase(BaseSchema):
    name: str
    avatar: Optional[str]
    options: Optional[Dict[str, Any]]

class CreateUserSchema(UserSchemaBase):
    ...

class UpdateUserSchema(BaseSchema):
    name: Optional[str]
    avatar: Optional[str]
    options: Optional[Dict[str, Any]]

class UserSchema(UserSchemaBase):
    """User"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    accounts: Optional[List[AccountSchema]]
    # members: List[OrgMemberSchema]