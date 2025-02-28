from sqlalchemy import Column, Text, String, JSON
from db.base_entity import MultiTenantBase, TimestampedBase

class Credentials(MultiTenantBase, TimestampedBase):
  __tablename__ = "credentials"

  name = Column(String, nullable=False)
  type = Column(String, nullable=False)
  data = Column(JSON, nullable=True)