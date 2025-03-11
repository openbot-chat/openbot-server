from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MinifiedUser(BaseModel):
    id: UUID
    name: str
    avatar: Optional[str]