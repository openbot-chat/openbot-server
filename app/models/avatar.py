from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema

class AvatarSchemaBase(BaseSchema):
    type: str
    provider: str
    thumbnail: str
    # identifier: str
    options: Optional[Dict[str, Any]]
    creator_id: Optional[str]
    private: Optional[bool] = False


class CreateAvatarSchema(AvatarSchemaBase):
  ...

class UpdateAvatarSchema(BaseSchema):
    type: Optional[str]
    provider: Optional[str]
    thumbnail: Optional[str]
    # identifier: str
    options: Optional[Dict[str, Any]]
    creator_id: Optional[str]
    private: Optional[bool] = False


class AvatarSchema(AvatarSchemaBase):
  id: UUID
  created_at: datetime
  updated_at: datetime