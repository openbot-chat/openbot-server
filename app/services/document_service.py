from uuid import UUID
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException
from repositories.sqlalchemy.document_repository import DocumentRepository
from repositories.sqlalchemy.datasource_repository import DatasourceRepository
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from api.dependencies.repository import make_repository
from models import document as document_schemas
from models.credentials import *
from schemas.pagination import CursorParams, CursorPage
from api.dependencies.file_storage import create_file_storage
from core.file_storage.file_storage_manager import FileStorageManager
from celery_app import celery_app
import vectorstore
from vectorstore import DatastoreManager
import os
import json
import logging
import io
import click
from config import (
  DEFAULT_QDRANT_OPTIONS
)


class DocumentService:
    def __init__(
        self, 
        repository: DocumentRepository = Depends(make_repository(DocumentRepository)),
        datasource_repository: DatasourceRepository = Depends(make_repository(DatasourceRepository)),
        datastore_repository: DatastoreRepository = Depends(make_repository(DatastoreRepository)),
        credentials_repository: DatastoreRepository = Depends(make_repository(CredentialsRepository)),
        file_storage_manager: FileStorageManager = Depends(create_file_storage),
    ):
        self.repository = repository
        self.datasource_repository = datasource_repository
        self.datastore_repository = datastore_repository
        self.credentials_repository = credentials_repository
        self.file_storage_manager = file_storage_manager

    async def create(self, in_schema: document_schemas.CreateDocumentSchema) -> document_schemas.DocumentSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[document_schemas.DocumentSchema]:
        document = await self.repository.get_by_id(id)
        if document is None: return None

        if document.metadata_ is not None:
            key = document.metadata_.get("file_path")
            if key is not None:
                file_storage = self.file_storage_manager.load("s3", CredentialsSchemaBase(
                    type="aws",
                    name="aws s3",
                    data={
                        "region": os.getenv("S3_REGION"),
                        "use_ssl": os.getenv("S3_SSL"),
                        "endpoint": os.getenv("S3_ENDPOINT"),
                        "bucket": os.getenv("S3_BUCKET"),
                        "secret_key": os.getenv("S3_SECRET_KEY"),
                        "access_key": os.getenv("S3_ACCESS_KEY"),
                    },
                ))

                content = await file_storage.get_object(key)
                obj = json.loads(content.decode())
                document.text = obj['text']
        
        return document

    async def update_by_id(self, id: UUID, data: document_schemas.UpdateDocumentSchema) -> document_schemas.DocumentSchema: 
        text = data.text
        del data.text
        document = await self.repository.update_by_id(id, data)
        
        datasource = await self.datasource_repository.get_by_id(document.datasource_id)
        if not datasource:
            raise Exception('Datasource not found')
      
        datastore = await self.datastore_repository.get_by_id(datasource.datastore_id)
        if not datastore:
            raise Exception('Datastore not found')

        if text is not None:
            # TODO 1. 如果修改了内容，要上传文件
            file_storage = self.file_storage_manager.load("s3", CredentialsSchemaBase(
                type="aws",
                name="aws s3",
                data={
                    "region": os.getenv("S3_REGION"),
                    "use_ssl": os.getenv("S3_SSL"),
                    "endpoint": os.getenv("S3_ENDPOINT"),
                    "bucket": os.getenv("S3_BUCKET"),
                    "secret_key": os.getenv("S3_SECRET_KEY"),
                    "access_key": os.getenv("S3_ACCESS_KEY"),
                },
            ))

            file_data = {
              "text": text,
            }

            key = f"datastores/{datasource.datastore_id}/{datasource.id}/{document.id}.json"
        
            await file_storage.put_object(
                key=key,
                fileobj=io.BytesIO(json.dumps(file_data).encode('utf-8')),
            )
            logging.info(click.style(f"text updated, upload file: {key}", fg="green"))

            print('data.text: ', text)
            doc = vectorstore.Document(
                id=str(document.id),
                text=text,
                metadata={
                    **(document.metadata_ or {}),
                    "source_id": str(datasource.id),
                }
            )

            # 2. 更新 向量文档
            # get datastore options
            options = None
            if datastore.options is not None:
                credentialsId = str(datastore.options.get('credentials_id'))
                credentials = await self.credentials_repository.get_by_id(UUID(hex=credentialsId))
                if credentials is not None:
                    options = credentials.data
                    logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")


            if options is None:
                options = DEFAULT_QDRANT_OPTIONS
                logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

            _vectorstore = DatastoreManager.get(datastore.provider, options)

            doc_id_2_chunks = await _vectorstore.upsert(datastore.collection_name, [doc])
            logging.info(click.style(f'upsert document success, id: {doc_id_2_chunks.keys()}', fg='green'))

        return document



    async def delete_by_id(self, id: UUID) -> document_schemas.DocumentSchema:
        document = await self.repository.delete_by_id(id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 删除文件

        # 删除 vectorstore
        
        return document

    async def bulk_delete(self, ids: List[str]) -> int:
        documents = await self.repository.delete_by_ids(ids)

        # may be huge number of documents, async task to delete
        document_dict = [d.dict() for d in documents]

        # TODO Delete file

        # TODO Delete vectorstore

        return len(documents)

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[document_schemas.DocumentSchema]:        
        return await self.repository.paginate1(filter, params=params)
  
    async def count(self, filter: Dict[str, Any]) -> int:
        return await self.repository.count1(filter)