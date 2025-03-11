from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime



class DatasourceBaseDTO(BaseModel):
    class Config(BaseModel.Config):
        allow_population_by_field_name = True

    name: str
    type: str
    status: str
    last_sync: Optional[datetime]
    options: Optional[Dict[str, Any]] = {}
    metadata_: Optional[Dict[str, Any]] = Field(alias="metadata")
    documents: Optional[int] = 0
    datastore_id: UUID
    org_id: str

class CreateDatasourceDTO(BaseModel):
    class Config(BaseModel.Config):
        allow_population_by_field_name = True

    name: str
    type: str
    org_id: str
    options: Optional[Dict[str, Any]]
    metadata_: Optional[Dict[str, Any]] = Field(alias="metadata")
    datastore_id: Optional[UUID]

class UpdateDatasourceDTO(BaseModel):
    class Config(BaseModel.Config):
        allow_population_by_field_name = True

    name: Optional[str]
    options: Optional[Dict[str, Any]]
    metadata_: Optional[Dict[str, Any]] = Field(alias="metadata")

class DatasourceDTO(DatasourceBaseDTO):
    """DatasourceDTO"""
    id: UUID
    created_at: datetime
    updated_at: datetime
