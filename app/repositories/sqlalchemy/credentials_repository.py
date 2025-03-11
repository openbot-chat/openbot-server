from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from schemas.pagination import CursorParams, CursorPage

from repositories.sqlalchemy.credentials import Credentials
from repositories.sqlalchemy.base_repository import BaseRepository


from models.credentials import (
    CreateCredentialsSchema,
    UpdateCredentialsSchema,
    CredentialsSchema,
)

class CredentialsRepository(BaseRepository[
    CreateCredentialsSchema,
    UpdateCredentialsSchema,
    CredentialsSchema,
    Credentials,
]):
    @property
    def _table(self) -> Type[Credentials]:
        return Credentials

    @property
    def _schema(self) -> Type[CredentialsSchema]:
        return CredentialsSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Credentials.created_at)


    async def query(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[CredentialsSchema]:
        query = select(self._table).order_by(self._table.created_at.desc())
        if 'q' in filter:
            query = query.where(
                Credentials.name.ilike(f"%{filter['q']}%"),
            )
  
        if 'type' in filter:
            query = query.where(
                Credentials.type == filter['type'],
            )

        if 'org_id' in filter:
            query = query.where(
                Credentials.org_id == filter['org_id'],
            )

        return await super().paginate(query, params)

    async def count1(
      self,
      filter: Dict[str, Any],
    ) -> int:
        query = select(self._table)
        if 'type' in filter:
            query = query.where(
                Credentials.type == filter['type'],
            )

        if 'org_id' in filter:
            query = query.where(
                Credentials.org_id == filter['org_id'],
            )

        return await super().count(query)
