

import abc
import logging
from uuid import uuid4, UUID

from fastapi import HTTPException

from typing import Generic, TypeVar, Type, Optional, List, Any, Union, Dict
from schemas.base import BaseSchema
from sqlalchemy import func, delete, inspect
from sqlalchemy.engine import Result
from sqlalchemy.orm import InstrumentedAttribute, noload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, Delete
from fastapi_pagination import set_page
from fastapi_pagination.api import resolve_params
from fastapi_pagination.ext.sqlalchemy import paginate
from schemas.pagination import CursorParams, CursorPage

from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db.base_entity import MultiTenantBase 
from api.context import get_global_org_id
from datetime import datetime

logger = logging.getLogger(__name__)


IN_SCHEMA = TypeVar("IN_SCHEMA", bound=BaseSchema)
SCHEMA = TypeVar("SCHEMA", bound=BaseSchema)
PARTIAL_UPDATE_SCHEMA = TypeVar("PARTIAL_UPDATE_SCHEMA", bound=BaseSchema)
TABLE = TypeVar("TABLE")


_INSERT_FUNC = {
    "sqlite": sqlite_insert,
    "postgresql": postgres_insert,
    "mysql": mysql_insert,
}


def count_query(query: Select, *, use_subquery: bool = True) -> Select:
    query = query.order_by(None).options(noload("*"))

    if use_subquery:
        return select(func.count()).select_from(query.subquery())

    return query.with_only_columns(  # noqa: PIE804
        func.count(),
        **{"maintain_column_froms": True},
    )

def fill(entity: Any, replace_dict: bool = False, **kwargs: Any) -> Any:
    for key, value in kwargs.items():
        if not hasattr(entity, key):
            raise AttributeError(f"Entity `{entity.__class__.__name__}` has no attribute `{key}`")
        # If the value is a dict, set value for each key one by one, as we want to update only the keys that are in
        # `value` and not override the whole dict.
        if isinstance(value, dict) and not replace_dict:
            dict_col = getattr(entity, key) or {}
            dict_col.update(value)
            value = dict_col
        setattr(entity, key, value)
    return entity


class BaseRepository(
    Generic[IN_SCHEMA, PARTIAL_UPDATE_SCHEMA, SCHEMA, TABLE]
):
    def __init__(self, db_session: AsyncSession, *args, **kwargs) -> None:
        self._db_session: AsyncSession = db_session

    @property
    @abc.abstractmethod
    def _table(self) -> Type[TABLE]:
        ...

    @property
    @abc.abstractmethod
    def _schema(self) -> Type[SCHEMA]:
        ...

    @property
    @abc.abstractmethod
    def _order_by(self) -> Optional[InstrumentedAttribute]:
        ...

    async def create(
        self, 
        in_schema: IN_SCHEMA,
        autocommit: bool = True,
    ) -> SCHEMA:
        data = in_schema.dict(by_alias=True)
        if 'id' in data:
            #id = data.get('id')
            #del data['id']
            id = data.pop('id')
        else:
            id = uuid4()

        if issubclass(self._table, MultiTenantBase):
            if 'org_id' not in data:
                data['org_id'] = get_global_org_id()

        entry = self._table(id=id, **data)
        self._db_session.add(entry)
        if autocommit:
            await self._db_session.commit()
      
            """
            其中，session是一个AsyncSession对象，instance是要刷新的实体对象。
        refresh方法的作用包括：
        重新加载实体对象的属性值：调用refresh方法后，会从数据库中重新加载实体对象的属性值，并覆盖当前对象的属性值。
        撤销对实体对象的修改：如果在调用refresh方法之前对实体对象进行了修改，调用refresh方法后，这些修改将被撤销，实体对象的属性值将恢复为数据库中的最新值。
        需要注意的是，refresh方法会向数据库发送一条查询语句，以获取最新的属性值。因此，在调用refresh方法之前，需要确保实体对象已经在数据库中存在，并且与数据库中的数据保持同步
            """
            await self._db_session.refresh(entry)

        return self._schema.from_orm(entry)


    async def create_many(
        self, 
        in_schemas: List[IN_SCHEMA],
        autocommit: bool = True,
    ) -> List[SCHEMA]:
        datas = []

        for in_schema in in_schemas:
            data = in_schema.dict(by_alias=True)
            if 'id' in data:
                id = data.pop('id')
            else:
                id = uuid4()

            if issubclass(self._table, MultiTenantBase):
                data['org_id'] = get_global_org_id()
            
            datas.append(data)

        entries = [self._table(id=id, **data) for data in datas]
        self._db_session.add_all(entries)
        await self._db_session.flush()
        if autocommit:
            await self._db_session.commit()
      
            for entry in entries:
                await self._db_session.refresh(entry)

        return [self._schema.from_orm(entry) for entry in entries]

    async def upsert(
        self, 
        in_schema: PARTIAL_UPDATE_SCHEMA,
        constraints: List["InstrumentedAttribute[Any]"],
        autocommit: bool = True,
    ) -> SCHEMA:
        upserted = await self.upsert_many([in_schema], constraints, autocommit)
        return upserted[0]

    async def upsert_many(
        self,
        objects: List[PARTIAL_UPDATE_SCHEMA],
        constraints: List["InstrumentedAttribute[Any]"],
        autocommit: bool = True,
    ) -> List[SCHEMA]:
        if len(objects) == 0:
            raise ValueError("Cannot upsert empty list of objects")
        values = [obj.dict(by_alias=True) for obj in objects]

        # Try to insert all objects
        insert_stmt = _INSERT_FUNC[self._db_session.bind.dialect.name](self._table).values(values)

        # On conflict, update the columns that are upsertable (defined in `Entity.__upsertable_columns__`)
        columns_to_update = {column: getattr(insert_stmt.excluded, column) for column in self._table.__upsertable_columns__}
        # onupdate for `updated_at` is not working. We need to force a new value on update
        if hasattr(self._table, "updated_at"):
            columns_to_update["updated_at"] = datetime.utcnow()
        upsert_stmt = (
            insert_stmt.on_conflict_do_update(index_elements=constraints, set_=columns_to_update)
            .returning(self._table)
            .execution_options(populate_existing=True)
        )

        result = await self._db_session.execute(upsert_stmt)
        entries = result.scalars().all()
        if autocommit:
            await self._db_session.commit()
            for entry in entries:
                await self._db_session.refresh(entry)

        return [self._schema.from_orm(entry) for entry in entries]

    async def get_by_id(self, entry_id: Union[UUID, str]) -> Optional[SCHEMA]:
        entry = await self._db_session.get(self._table, entry_id)
        if not entry:
            return None

        return self._schema.from_orm(entry)

    async def get_by_ids(self, ids: List[Union[UUID, str]]) -> List[SCHEMA]:        
        response = await self._db_session.execute(
            select(self._table).where(
                self._table.id.in_(ids)
            )
        )
        entries = response.scalars().all()
        return [self._schema.from_orm(entry) for entry in entries]

    async def query_one(self, **params: Any) -> Optional[SCHEMA]:
        result = await self._db_session.execute(
            select(self._table).filter_by(**params),
        )

        entry = result.scalars().unique().one_or_none()

        return self._schema.from_orm(entry)

    async def update_by_id(
        self, 
        entry_id: Any, 
        in_data: PARTIAL_UPDATE_SCHEMA,
        autocommit: bool = True,
        replace_dict: bool = True, # XXX 为 False 时 不更新，很奇怪
    ) -> SCHEMA:
        entry = await self._db_session.get(self._table, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Object not found")

        fill(entry, replace_dict=replace_dict, **in_data.dict(exclude_unset=True, by_alias=True))

        print('update agent: ', entry.__dict__)

        self._db_session.add(entry)
        if autocommit:
            await self._db_session.commit()

        return self._schema.from_orm(entry)

    async def delete_by_id(self, entry_id: Union[UUID, str], autocommit: bool = True) -> SCHEMA:
        entry = await self._db_session.get(self._table, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Object not found")
        await self._db_session.delete(entry)
        await self._db_session.flush()

        if autocommit:
            await self._db_session.commit()

        return self._schema.from_orm(entry)

    async def delete_by_ids(self, ids: List[Any]):
        instances: list[TABLE] = []

        if False: #self._db_session.bind.dialect.delete_executemany_returning:
            instances.extend(
                await self._db_session.scalars(
                    delete(self._table).where(getattr(self._table, 'id').in_(ids)).returning(self._table)
                )
            )
        else:
            instances.extend(
                await self._db_session.scalars(
                    select(self._table).where(getattr(self._table, 'id').in_(ids))
                )
            )
            await self._db_session.execute(
                delete(self._table).where(getattr(self._table, 'id').in_(ids))
            )

        # await self._db_session.flush()
        await self._db_session.commit()
        #for instance in instances:
        #    self._db_session.expunge(instance)

        return [self._schema.from_orm(entry) for entry in instances]

    async def delete_many(self, filter: Dict[str, Any]):
        def build_filter(query: Delete, filter: Dict[str, Any]):
            for k, v in filter.items():
                query = query.where(getattr(self._table, k) == v)
            return query

        result = await self._db_session.scalars(
            build_filter(delete(self._table), filter).returning(self._table.id)
        )

        await self._db_session.flush()
        return list(result)
  
    # 目前只处理了游标分页
    async def paginate(
        self,
        query: Optional[Select] = None,
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[SCHEMA]:
        set_page(CursorPage)

        params = resolve_params(params)

        if query is None:
            query = select(self._table)
      
        if self._order_by is not None: 
            query = query.order_by(self._order_by)

        page = await paginate(self._db_session, query, params)

        # [await self._db_session.refresh(item) for item in page.items]

        p = CursorPage[SCHEMA](
            items=[self._schema.from_orm(item) for item in page.items],
            params=params,
            # current_page=page.current_page,
            # current_page_backwards=page.current_page_backwards,
            next_page=page.next_page,
            previous_page=page.previous_page,
        )

        if params.need_total:
            p.total = await self.count(query)

        return p

    async def count(self, query: Optional[Select] = None) -> int:
        if query is None:
            query = select(self._table)

        return await self._db_session.scalar(count_query(query))