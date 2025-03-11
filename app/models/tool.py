from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel



class ToolSchemaBase(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    type: str
    options: Optional[Dict[str, Any]]
    return_direct: bool = False
    org_id: Optional[str] = None
    toolkit_id: Optional[UUID] = None

class CreateToolSchema(ToolSchemaBase):
    ...

class UpdateToolSchema(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    return_direct: Optional[bool] = False
    icon: Optional[str] = None
    options: Optional[Dict[str, Any]]
    toolkit_id: Optional[UUID]

class ToolSchema(ToolSchemaBase):
    """Tool"""
    id: UUID
    created_at: datetime
    updated_at: datetime


from fastapi import Query

class ToolFilter(BaseModel):
    org_id: Optional[str] = Query(None)
    toolkit_id: Optional[str] = Query(None)

class ToolRunRequest(BaseModel):
    inputs: Dict[str, Any]

class ToolRunResponse(BaseModel):
    outputs: Any