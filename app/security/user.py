from typing import Optional, List
from pydantic import BaseModel, Field

class AuthUser(BaseModel):
    id:               str = Field(..., alias='sub')
    permissions:      Optional[List[str]]
    # email:          Optional[str] = Field(None, alias=f'{auth0_rule_namespace}/email')  # type: ignore [literal-required]
    client_id:        Optional[str]
    org_id:           Optional[str]