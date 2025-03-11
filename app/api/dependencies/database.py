from db.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from api.context import get_global_org_id


async def get_superuser_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Dependency
async def get_db_session() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        try:
            org_id = get_global_org_id()
            query = text(f"SET app.current_org='{org_id}';")
            await session.execute(text("SET SESSION ROLE tenant_user;"))
            await session.execute(query)
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.execute(text("RESET ROLE;"))
            await session.commit()
            pass