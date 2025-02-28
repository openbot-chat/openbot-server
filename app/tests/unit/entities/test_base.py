import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional, Type
from datetime import datetime
from pydantic import BaseModel
import pytest
import pytest_asyncio
from sqlalchemy import inspect, desc, JSON, String, Integer, inspect, select, Column
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, InstrumentedAttribute, mapped_column


from db.base_entity import DatabaseEntity
from repositories.sqlalchemy.base_repository import BaseRepository
from uuid import UUID



class TestEntity(DatabaseEntity):
    __tablename__ = "test_entities"
    str_col: Mapped[Optional[str]] = mapped_column()
    int_col: Mapped[Optional[int]] = mapped_column()
    external_id: Mapped[Optional[str]] = mapped_column(unique=True)
    dict_col: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    __upsertable_columns__ = {"str_col", "int_col"}


class CreateEntitySchema(BaseModel):
    str_col: str
    int_col: int
    external_id: str


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
        entity = await TestEntity.create(db, str_col="unit-test", int_col=1, autocommit=True)
        assert isinstance(entity.id, UUID)
        assert entity.id is not None
        assert entity.str_col == "unit-test"
        assert entity.int_col == 1
        assert entity.created_at == entity.updated_at

    async def test_database_model_create_without_autocommit(self, db: "AsyncSession"):
        entity = await TestEntity.create(db, autocommit=False)
        assert inspect(entity).pending

    async def test_database_model_read_by(self, db: "AsyncSession"):
        await TestEntity.create(db, str_col="unit-test", int_col=1, autocommit=True)
        entity = await TestEntity.read_by(db, str_col="unit-test")
        assert entity.id is not None
        assert entity.str_col == "unit-test"
        assert entity.int_col == 1

    async def test_database_model_read(self, db: "AsyncSession"):
        entity = await TestEntity.create(db, str_col="unit-test", int_col=1, autocommit=True)
        entity = await TestEntity.read(db, entity.id)
        assert entity.id is not None
        assert entity.str_col == "unit-test"
        assert entity.int_col == 1

    async def test_database_model_update(self, db: "AsyncSession"):
        entity = await TestEntity.create(
            db, str_col="unit-test", int_col=1, dict_col={"a": 1, "b": 2, "c": 3}, autocommit=True
        )

        entity = await entity.update(db, str_col="unit-test-2", int_col=2, dict_col={"a": 10}, autocommit=True)
        assert entity.str_col == "unit-test-2"
        assert entity.int_col == 2
        assert entity.dict_col == {"a": 10, "b": 2, "c": 3}

        entity = await entity.update(
            db, str_col="unit-test-2", int_col=2, dict_col={"a": 10}, replace_dict=True, autocommit=True
        )
        assert entity.str_col == "unit-test-2"
        assert entity.int_col == 2
        assert entity.dict_col == {"a": 10}

    async def test_database_model_upsert_many(self, db: "AsyncSession"):
        entities = []
        schemas = []
        # These ones will be updated
        for i in range(5):
            entities.append(await TestEntity.create(db, str_col=f"unit-test-{i}", int_col=i, external_id=f"external-id-{i}"))
            schemas.append(
                CreateEntitySchema(str_col=f"unit-test-{i}-updated", int_col=i * 10, external_id=f"external-id-{i}")
            )
        # This one has to be inserted
        schemas.append(
            CreateEntitySchema(str_col="unit-test-inserted", int_col=99999, external_id="external-id-inserted")
        )
        entities = await TestEntity.upsert_many(db, schemas, constraints=[TestEntity.external_id], autocommit=True)
        for i, entity in enumerate(entities[:5]):
            assert entity.str_col == f"unit-test-{i}-updated"
            assert entity.int_col == i * 10
        assert entities[-1].str_col == "unit-test-inserted"
        assert entities[-1].int_col == 99999

    async def test_database_model_upsert_many_without_objects(self, db: "AsyncSession"):
        with pytest.raises(ValueError, match="Cannot upsert empty list of objects"):
            await TestEntity.upsert_many(db, [], constraints=[TestEntity.external_id], autocommit=True)

    async def test_database_model_upsert(self, db: "AsyncSession"):
        entity = await TestEntity.create(db, str_col="unit-test", int_col=1, external_id="12345", autocommit=True)
        await asyncio.sleep(1)
        entity = await TestEntity.upsert(
            db,
            CreateEntitySchema(str_col="unit-test-updated", int_col=2, external_id=entity.external_id),
            constraints=[TestEntity.external_id],
            autocommit=True,
        )
        assert entity.str_col == "unit-test-updated"
        assert entity.int_col == 2

    async def test_database_model_upsert_updated_at(self, db: "AsyncSession"):
        entity = await TestEntity.create(db, str_col="unit-test", int_col=1, external_id="12345", autocommit=True)
        updated_at = entity.updated_at
        await asyncio.sleep(1)

        entity = await TestEntity.upsert(
            db,
            CreateEntitySchema(str_col="unit-test-updated", int_col=2, external_id=entity.external_id),
            constraints=[TestEntity.external_id],
            autocommit=True,
        )

        assert entity.updated_at > updated_at

    async def test_database_model_delete(self, db: "AsyncSession"):
        entity = await TestEntity.create(db, str_col="unit-test", int_col=1, autocommit=True)
        entity = await entity.delete(db)
        assert (await db.execute(select(TestEntity).filter_by(id=model.id))).scalar_one_or_none() is None

    async def test_database_model_delete_many(self, db: "AsyncSession"):
        for i in range(5):
            await TestEntity.create(db, str_col=f"unit-test-{i}", int_col=i, external_id=f"external-id-{i}")
        for i in range(1, 6):
            await TestEntity.create(db, str_col=f"unit-test-{i}", int_col=i * 10, external_id=f"external-id-{i * 10}")

        removed = await TestEntity.delete_many(db, params=[TestEntity.int_col < 10], autocommit=True)

        assert len(removed) == 5