from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
from db.base_entity import MultiTenantBase, TimestampedBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship



class Document(MultiTenantBase, TimestampedBase):
  __tablename__ = "documents"

  last_sync = Column(DateTime(), nullable=True)
  datasource_id = Column(UUID(as_uuid=True), ForeignKey('datasources.id'), nullable=False)
  datasource = relationship('Datasource', foreign_keys=[datasource_id], lazy="select")
  # 'metadata' is reserved by SQLAlchemy, hence the '_'
  metadata_ = Column("metadata", JSON, nullable=True)