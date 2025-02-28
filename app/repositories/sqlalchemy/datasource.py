from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
from db.base_entity import MultiTenantBase, TimestampedBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship



class Datasource(MultiTenantBase, TimestampedBase):
    __tablename__ = "datasources"

    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="unsynced")
    last_sync = Column(DateTime(), nullable=True)
    datastore_id = Column(UUID(as_uuid=True), ForeignKey('datastores.id'), nullable=False)
    datastore = relationship('Datastore', foreign_keys=[datastore_id], lazy="select")

    creator_id = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)