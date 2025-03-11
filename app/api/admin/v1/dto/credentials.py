from typing import Optional
from pydantic import BaseModel
from fastapi import Query



class CredentialsFilter(BaseModel):
    q: Optional[str] = Query(None)
    org_id: Optional[str] = Query(None)
    type: Optional[str] = Query(None)