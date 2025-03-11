from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from repositories.sqlalchemy.document import Document
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.document import (
    CreateDocumentSchema,
    UpdateDocumentSchema,
    DocumentSchema,
)

class DocumentRepository(BaseRepository[
    CreateDocumentSchema,
    UpdateDocumentSchema,
    DocumentSchema,
    Document,
]):
    @property
    def _table(self) -> Type[Document]:
        return Document

    @property
    def _schema(self) -> Type[DocumentSchema]:
        return DocumentSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Document.created_at)
  
    async def paginate1(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[DocumentSchema]:
        query = select(self._table).order_by(self._table.created_at.desc())
        if 'datasource_id' in filter:
            query = query.where(
                Document.datasource_id == filter['datasource_id'],
            )
        return await super().paginate(query, params)

    async def count1(
        self,
        filter: Dict[str, Any],
    ) -> int:
        query = select(self._table)
        if 'datasource_id' in filter:
            query = query.where(
                Document.datasource_id == filter['datasource_id'],
            )

        return await super().count(query)