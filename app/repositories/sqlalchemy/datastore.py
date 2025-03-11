from sqlalchemy import Column, Text, String, JSON
from db.base_entity import MultiTenantBase, TimestampedBase

class Datastore(MultiTenantBase, TimestampedBase):
    __tablename__ = "datastores"

    name_for_model = Column(String, nullable=False)
    description_for_model = Column(Text, nullable=False)
    provider = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    collection_name = Column(String, nullable=False)