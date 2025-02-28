from sqlalchemy import Column, String, JSON, Integer
from db.base_entity import TimestampedBase
from nanoid import generate

class ApiKey(TimestampedBase):
    __tablename__ = "api_keys"

    name = Column(String(255), nullable=False, index=True)
    options = Column(JSON, nullable=True)
    token = Column(String(255), nullable=False, index=True, unique=True)
    expires_in = Column(Integer, nullable=True)
    user_id = Column(String, nullable=False, index=True)

    @staticmethod
    def generate_api_key(prefix: str = 'openbot-'):
        return prefix + generate(size=32)