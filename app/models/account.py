from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema

class AccountSchemaBase(BaseSchema):
    user_id: UUID
    type: str
    provider: str
    providerAccountId: str
    refresh_token: Optional[str]
    access_token: Optional[str]
    expires_at: Optional[int]
    token_type: Optional[str]
    scope: Optional[str]
    id_token: Optional[str]
    session_state: Optional[str]
    oauth_token_secret: Optional[str]
    oauth_token: Optional[str]
    refresh_token_expires_in: Optional[int]

class CreateAccountSchema(AccountSchemaBase):
    ...

class UpdateAccountSchema(AccountSchemaBase):
    ...

class AccountSchema(AccountSchemaBase):
    """Account"""
    id: UUID
    created_at: datetime
    updated_at: datetime