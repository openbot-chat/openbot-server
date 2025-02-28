from pydantic import BaseModel
from .user import MinifiedUser
from uuid import UUID


class OrgMemberDTO(BaseModel):
    id: UUID
    role: str
    org_id: UUID
    # org: OrgSchema
    user: MinifiedUser
    user_id: UUID