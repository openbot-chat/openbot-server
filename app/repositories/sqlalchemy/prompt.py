from sqlalchemy import Column, Text, String, ARRAY
from db.base_entity import TimestampedBase, MultiTenantBase



class Prompt(TimestampedBase, MultiTenantBase):
    __tablename__ = "prompts"

    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    input_variables = Column(ARRAY(String), nullable=True)