from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from repositories.sqlalchemy.custom_plan import CustomPlan
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.custom_plan import (
    CreateCustomPlanSchema,
    UpdateCustomPlanSchema,
    CustomPlanSchema,
)

class CustomPlanRepository(BaseRepository[
    CreateCustomPlanSchema,
    UpdateCustomPlanSchema,
    CustomPlanSchema,
    CustomPlan,
]):
    @property
    def _table(self) -> Type[CustomPlan]:
        return CustomPlan

    @property
    def _schema(self) -> Type[CustomPlanSchema]:
        return CustomPlanSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(CustomPlan.created_at)
  
    # 要在基类添加
    async def query_one(
        self,
        filter: Dict[str, Any],
    ) -> Optional[CustomPlanSchema]:
        query = select(self._table).order_by(self._table.created_at.desc())
        if "org_id" in filter:
            query = query.where(
                CustomPlan.org_id == filter['org_id']
            )

        if "external_id" in filter:
            query = query.where(
                CustomPlan.external_id == filter['external_id']
            )

        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None
        
        return self._schema.from_orm(entry)