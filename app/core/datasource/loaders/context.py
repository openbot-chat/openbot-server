from pydantic import BaseModel
from core.file_storage.file_storage_manager import FileStorageManager
from models.datastore import DatastoreSchema
from repositories.sqlalchemy.document_repository import DocumentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from vectorstore import Document
from typing import List
from vectorstore import Document
from vectorstore.models import Document
from uuid import uuid4, UUID
import logging
import click
import io
import json
import os
from models.document import CreateDocumentSchema
from models.credentials import CredentialsSchemaBase
from models.datasource import DatasourceSchema
from vectorstore.datastore_manager import DatastoreManager
from config import (
    DEFAULT_QDRANT_OPTIONS
)


class LoaderContext(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    datastore: DatastoreSchema
    datasource: DatasourceSchema
    document_repository: DocumentRepository
    credentials_repository: CredentialsRepository
    file_storage_manager: FileStorageManager
    
    async def save(self, documents: List[Document]):
        for document in documents:
            document.id = document.id or str(uuid4())

        # get datastore options
        options = None
        if self.datastore.options is not None:
            credentialsId = str(self.datastore.options.get('credentials_id'))
            credentials = await self.credentials_repository.get_by_id(UUID(hex=credentialsId))
            if credentials is not None:
                options = credentials.data
                logging.info(f"choose custom datastore, provider: {self.datastore.provider}, options: {options}")


        if options is None:
            options = DEFAULT_QDRANT_OPTIONS
            logging.info(f"choose default datastore, provider: {self.datastore.provider}, options: {options}")

        vectorstore = DatastoreManager.get(self.datastore.provider, options)


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


        for i in range(0, len(documents), 16):
            sub_docs = documents[i : i + 16]
            # 目前为止，datastore_id 使用的没有分隔符的uuid
            doc_id_2_chunks = await vectorstore.upsert(self.datastore.collection_name, sub_docs)
            logging.info(click.style(f'upsert documents success, {i}-{i+16}:{len(documents)}, ids: {doc_id_2_chunks.keys()}', fg='green'))


            # Add to File Storage    
  
            # add to s3
            for document in sub_docs:
                chunks = doc_id_2_chunks.get(document.id)
                if not chunks:
                    logging.warn(click.style(f'document {document.id} upsert failed', fg="yellow"))
                    continue

                key = f"datastores/{self.datasource.datastore_id}/{self.datasource.id}/{document.id}.json"
                file_data = {
                    "text": document.text
                }

                await file_storage.put_object(
                    key=key,
                    fileobj=io.BytesIO(json.dumps(file_data).encode('utf-8')),
                )
                logging.info(click.style(f'after upload document to file storage, key: {key}, datasource: {self.datasource.id}, document: {document.id}', fg="green"));
            # end add to file storage

        
            # upsert documents to db
            for document in sub_docs:
                chunks = doc_id_2_chunks.get(document.id)
                if not chunks:
                    logging.warn(click.style(f'document {document.id} upsert failed', fg="yellow"))
                    continue

                key = f"datastores/{self.datasource.datastore_id}/{self.datasource.id}/{document.id}.json"

                metadata = document.metadata or {}
                metadata.update({
                    "chunks": len(chunks),
                    "file_path": key,
                    "size": len(document.text), # 这里是文本的大小
                })

                # add to database
                await self.document_repository.create(CreateDocumentSchema(
                    id=UUID(document.id),
                    datasource_id=self.datasource.id,
                    org_id=self.datasource.org_id,
                    metadata_=metadata,
                ))
                logging.info(click.style(f'document {document.id} {UUID(document.id)} upsert to db success', fg="green"))
            #end upsert documents to db
        # end chunks