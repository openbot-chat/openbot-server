from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import logging

logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

engine = create_async_engine(
  DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
  future=True,
  pool_size=POOL_SIZE,
  max_overflow=64,
)

async_session = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()