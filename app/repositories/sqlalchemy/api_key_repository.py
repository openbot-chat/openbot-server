from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.engine import Result

from repositories.sqlalchemy.api_key import ApiKey
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.api_key import (
    CreateApiKeySchema,
    UpdateApiKeySchema,
    ApiKeySchema,
)

class ApiKeyRepository(BaseRepository[
    CreateApiKeySchema,
    UpdateApiKeySchema,
    ApiKeySchema,
    ApiKey,
]):
    @property
    def _table(self) -> Type[ApiKey]:
        return ApiKey

    @property
    def _schema(self) -> Type[ApiKeySchema]:
        return ApiKeySchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(ApiKey.created_at)

    async def get_by_token(self, token: str) -> Optional[ApiKeySchema]:
        result: Result = await self._db_session.execute(
            select(self._table).where(
              ApiKey.token == token,
            )
        )
        entry = result.scalar()
        if not entry:
            return None

        return self._schema.from_orm(entry)

    async def paginate1(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[ApiKeySchema]:
        query = select(self._table).order_by(self._table.created_at.desc())  
        if 'user_id' in filter:
            query = query.where(
                ApiKey.user_id == filter['user_id'],
            )

        return await super().paginate(query, params)