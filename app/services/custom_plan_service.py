from uuid import UUID
from typing import Optional, Dict, Any, List
from fastapi import Depends
from repositories.sqlalchemy.custom_plan_repository import CustomPlanRepository
from api.dependencies.repository import make_repository
from models.custom_plan import *
from models.document import *
from schemas.pagination import CursorParams, CursorPage



class CustomPlanService:
    def __init__(
        self, 
        repository: CustomPlanRepository = Depends(make_repository(CustomPlanRepository)),
    ):
        self.repository = repository

    async def create(self, in_schema: CreateCustomPlanSchema) -> CustomPlanSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[CustomPlanSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_org_id(self, org_id: str) -> Optional[CustomPlanSchema]:
        return await self.repository.query_one({"org_id": org_id})

    async def get_by_external_id(self, external_id: str) -> Optional[CustomPlanSchema]:
        return await self.repository.query_one({"external_id": external_id})

    async def update_by_id(self, id: UUID, data: UpdateCustomPlanSchema) -> CustomPlanSchema:
        return await self.repository.update_by_id(id, data)
  
    async def delete_by_id(self, id: UUID) -> CustomPlanSchema:
        return await self.repository.delete_by_id(id)

    async def paginate(self, params: Optional[CursorParams] = None) -> CursorPage[CustomPlanSchema]:
        return await self.repository.paginate(params=params)
  
    async def query_one(
        self,
        filter: Dict[str, Any],
    ) -> Optional[CustomPlanSchema]:
        return await self.repository.query_one(filter)