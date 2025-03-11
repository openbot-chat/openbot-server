import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional, Type
from datetime import datetime

import pytest
import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy import inspect, desc, JSON, String, Integer, inspect, select, Column
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, InstrumentedAttribute, mapped_column


from db.base_entity import TimestampedBase
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.base import BaseSchema
from uuid import UUID



class TestEntity(TimestampedBase):
    __tablename__ = "test_entities"
    str_col: Mapped[Optional[str]] = mapped_column()
    int_col: Mapped[Optional[int]] = mapped_column()
    external_id: Mapped[Optional[str]] = mapped_column(unique=True)
    dict_col: Mapped[Optional[Dict[str, Any]]] = mapped_column(MutableDict.as_mutable(JSON))

    __upsertable_columns__ = {"str_col", "int_col", "dict_col"}

class TestSchemaBase(BaseSchema):
    str_col: Optional[str] = None
    int_col: Optional[int] = None
    external_id: Optional[str] = None
    dict_col: Optional[Dict[str, Any]] = None

class CreateTestSchema(TestSchemaBase):
    ...

class UpdateTestSchema(CreateTestSchema):
    ...

class TestSchema(TestSchemaBase):
    id: UUID
    updated_at: Optional[datetime]
    created_at: Optional[datetime]



class TestEntityRepository(BaseRepository[
    CreateTestSchema,
    UpdateTestSchema,
    TestSchema,
    TestEntity,
]):
    @property
    def _table(self) -> Type[TestEntity]:
        return TestEntity

    @property
    def _schema(self) -> Type[TestSchema]:
        return TestSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(TestEntity.created_at)


@pytest_asyncio.fixture(autouse=True)
async def configure_model_table(connection: "AsyncConnection"):
    await connection.run_sync(TestEntity.__table__.create)

    yield TestEntity

    try:
        await connection.run_sync(TestEntity.__table__.drop)
    except Exception as e:
        print(e)
        pass

@pytest.mark.asyncio
class TestBaseRepository:
    async def test_create(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        entity = await repo.create(
            CreateTestSchema(
                str_col="unit-test",
                int_col=1,
            ),
            autocommit=True,
        )

        assert isinstance(entity.id, UUID)
        assert entity.id is not None
        assert entity.str_col == "unit-test"
        assert entity.int_col == 1
        assert entity.created_at == entity.updated_at

    async def test_database_model_read_by(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        await repo.create(
            CreateTestSchema(
                str_col="unit-test",
                int_col=1,
            ),
            autocommit=True,
        )
        model = await repo.query_one(str_col="unit-test")
        assert model.id is not None
        assert model.str_col == "unit-test"
        assert model.int_col == 1

    async def test_database_model_read(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        model = await repo.create(
            CreateTestSchema(
                str_col="unit-test",
                int_col=1,
            ),
            autocommit=True,
        )
        model = await repo.get_by_id(model.id)
        assert model.id is not None
        assert model.str_col == "unit-test"
        assert model.int_col == 1
    
    async def test_database_model_update(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        model = await repo.create(
            CreateTestSchema(
                str_col="unit-test",
                int_col=1,
                dict_col={"a": 1, "b": 2, "c": 3},
            ),
            autocommit=True,
        )

        model = await repo.update_by_id(
            model.id,
            UpdateTestSchema(
                str_col="unit-test-2", 
                int_col=2, 
                dict_col={"a": 10},
            ), 
            autocommit=True,
        )
        assert model.str_col == "unit-test-2"
        assert model.int_col == 2
        assert model.dict_col == {"a": 10, "b": 2, "c": 3}

        model = await repo.update_by_id(
            model.id, 
            UpdateTestSchema(
                str_col="unit-test-2", 
                int_col=2, 
                dict_col={"a": 10}, 
            ),
            replace_dict=True,
            autocommit=True,
        )
        assert model.str_col == "unit-test-2"
        assert model.int_col == 2
        assert model.dict_col == {"a": 10}

    async def test_database_model_upsert(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        model = await repo.create( 
            CreateTestSchema(
                str_col="unit-test", 
                int_col=1, 
                dict_col={"a": 10, "b": 2, "c": 3},
                external_id="12345",
            ),
            autocommit=True,
        )
        await asyncio.sleep(1)

        model = await repo.upsert(
            UpdateTestSchema(str_col="unit-test-updated", int_col=2, dict_col={"a": 10}, external_id=model.external_id),
            constraints=[TestEntity.external_id],
            autocommit=True,
        )
        assert model.str_col == "unit-test-updated"
        assert model.int_col == 2
        assert model.dict_col == {"a": 10}

    async def test_database_model_upsert_updated_at(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        model = await repo.create(
            CreateTestSchema(
                str_col="unit-test", int_col=1, external_id="12345", 
            ),
            autocommit=True,
        )
        updated_at = model.updated_at
        await asyncio.sleep(1)

        model = await repo.upsert(
            UpdateTestSchema(str_col="unit-test-updated", int_col=2, external_id=model.external_id),
            constraints=[TestEntity.external_id],
            autocommit=True,
        )

        assert model.updated_at > updated_at

    async def test_database_model_delete(self, db: "AsyncSession"):
        repo = TestEntityRepository(db_session=db)
        model = await repo.create(CreateTestSchema(str_col="unit-test", int_col=1), autocommit=True)
        model = await repo.delete_by_id(model.id)
        assert (await db.execute(select(TestEntity).filter_by(id=model.id))).scalar_one_or_none() is None