from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select

from repositories.sqlalchemy.integration import Integration
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.integration import (
    CreateIntegrationSchema,
    UpdateIntegrationSchema,
    IntegrationSchema,
)

class IntegrationRepository(BaseRepository[
  CreateIntegrationSchema,
  UpdateIntegrationSchema,
  IntegrationSchema,
  Integration,
]):
    @property
    def _table(self) -> Type[Integration]:
        return Integration

    @property
    def _schema(self) -> Type[IntegrationSchema]:
        return IntegrationSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Integration.created_at)

    async def get_by_identifier(self, identifier: str) -> Optional[IntegrationSchema]:
        result = await self._db_session.execute(
            select(Integration).where(
              Integration.identifier == identifier,
            )
        )

        entry = result.scalar_one_or_none()

        if not entry:
            return None
        return self._schema.from_orm(entry)

    async def paginate1(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None,
    ) -> CursorPage[IntegrationSchema]:
        query = select(Integration).order_by(Integration.created_at.desc())

        if "catalog" in filter:
            query = query.where(Integration.catalog.in_(filter["catalog"]))

        """
        if "collection" in filter:
            query = query.where(Integration.collection == filter["collection"])
        """

        return await super().paginate(query, params)