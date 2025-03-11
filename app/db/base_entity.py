import uuid

from sqlalchemy import Column, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
# from sqlalchemy.ext.asyncio import AsyncAttrs

@as_declarative()
class TimestampedBase:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    __name__: str

    __allow_unmapped__ = True

    # so that created_at and updated_at columns can be accessed without querying the database
    __mapper_args__ = {
        "eager_defaults": True,
    }

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    

class MultiTenantBase:
    org_id = Column(String, nullable=False, index=True)




from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from db.mixins import CRUDMixin, TimestampMixin


class DatabaseEntity(DeclarativeBase, AsyncAttrs, CRUDMixin, TimestampMixin):
    __abstract__ = True

    # Required in order to access columns with server defaults or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)