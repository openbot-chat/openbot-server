from pydantic import BaseModel
from typing import List
from uuid import UUID

class MemberInput(BaseModel):
    user_id: UUID
    role: str

class AddMemberRequest(BaseModel):
    members: List[MemberInput]