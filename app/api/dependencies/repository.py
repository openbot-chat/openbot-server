from typing import Type
from fastapi import Depends
from .database import get_db_session, get_superuser_session
from repositories.sqlalchemy.base_repository import BaseRepository

def make_repository(Repository: Type[BaseRepository], row_level_security: bool = False):
    async def get_repository_rls(db_session = Depends(get_db_session)):
        return Repository(db_session)

    async def get_repository(db_session = Depends(get_superuser_session)):
        return Repository(db_session)

    if row_level_security:
        return get_repository_rls
    else:
        return get_repository