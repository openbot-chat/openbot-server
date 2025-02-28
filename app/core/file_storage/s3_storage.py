from .file_storage import FileStorage
from aiobotocore.session import get_session
from aiobotocore.response import StreamingBody
from aiobotocore.config import AioConfig
from typing import BinaryIO
from typing import Any
from models.credentials import CredentialsSchemaBase


class S3Storage(FileStorage):
    def __init__(self, credentials: CredentialsSchemaBase):
        super().__init__(credentials)
        if credentials.data is not None:
          self.bucket = credentials.data.get("bucket")
          self.region = credentials.data.get("region") 
          self.use_ssl = credentials.data.get("use_ssl") == True
          self.endpoint = credentials.data.get("endpoint")
          self.secret_key = credentials.data.get("secret_key")
          self.access_key = credentials.data.get("access_key")

    def create_client(self):
        session = get_session()
        return session.create_client(
            's3',
            region_name=self.region,
            aws_secret_access_key=self.secret_key,
            aws_access_key_id=self.access_key,
            config=AioConfig(signature_version='s3v4'),
        )

    async def put_object(self, key: str, fileobj: BinaryIO, **kwargs: Any):
        async with self.create_client() as client:
            resp = await client.put_object(Bucket=self.bucket, Key=key, Body=fileobj)
        return resp

    async def delete_object(self, key: str):
        async with self.create_client() as client:
            resp = await client.delete_object(Bucket=self.bucket, Key=key)
        return resp

    async def get_object(self, key: str) -> bytes:
        async with self.create_client() as client:
            resp = await client.get_object(Bucket=self.bucket, Key=key)
            async with resp["Body"] as stream:
                return await stream.read()

    async def download_fileobj(self, key: str, file: Any):
        async with self.create_client() as client:
            resp = await client.get_object(Bucket=self.bucket, Key=key)
            async for chunk in resp["Body"].iter_chunks():
                await file.write(chunk)


    async def list_objects(self, prefix: str, max_keys=20):
        async with self.create_client() as client:
            paginator = client.get_paginator('list_objects')
            async for result in paginator.paginate(Bucket=self.bucket, Prefix=prefix, MaxKeys=max_keys):
                print('paginator.paginate result: ', result)
                yield result

    async def generate_presigned_url(self, key: str, client_method: str = 'put_object', expires_in: int=900) -> str:
        async with self.create_client() as client:
            url = await client.generate_presigned_url(
                client_method,
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                },
                ExpiresIn=expires_in,
            )

            return url