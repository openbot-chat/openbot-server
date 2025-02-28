from sqlalchemy import Column, Text, String, JSON, Boolean
from db.base_entity import TimestampedBase, MultiTenantBase

class Integration(TimestampedBase, MultiTenantBase):
  __tablename__ = "integrations"

  name = Column(String, nullable=False)
  description = Column(Text, nullable=False)
  identifier = Column(String, nullable=False)
  catalog = Column(String, nullable=False) # 代表集成的类型
  icon = Column(String, nullable=True)
  options = Column(JSON, nullable=True)
  is_public = Column(Boolean, nullable=True, default=False)