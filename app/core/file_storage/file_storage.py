from abc import ABC, abstractmethod
from typing import Any, BinaryIO
from models.credentials import CredentialsSchemaBase


class FileStorage(ABC):
    def __init__(self, credentials: CredentialsSchemaBase):
        self.credentials = credentials

    @abstractmethod
    async def put_object(self, key: str, fileobj: BinaryIO, **kwargs: Any):
        ...

    @abstractmethod
    async def delete_object(self, key: str):
        ...
    
    @abstractmethod
    async def get_object(self, key: str) -> bytes:
        ...

    @abstractmethod
    async def download_fileobj(self, key: str, file: Any):
        ...

    @abstractmethod
    async def list_objects(self, prefix: str, max_keys:int=20):
        ...

    @abstractmethod
    async def generate_presigned_url(self, key: str, client_method: str = 'put_object', expires_in: int=900) -> str:
        ...