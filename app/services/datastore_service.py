import os
import logging
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from api.dependencies.repository import make_repository
from api.dependencies.file_storage import create_file_storage
from models import datastore as datastore_schemas
from models import credentials as credentials_schemas
from vectorstore import DatastoreManager
from schemas.pagination import CursorParams, CursorPage
from celery_app import celery_app
from core.file_storage.file_storage_manager import FileStorageManager
from config import (
   DEFAULT_QDRANT_OPTIONS
)
from vectorstore.models import DocumentQuery, DocumentQueryResult



class DatastoreService:
    def __init__(
        self, 
        repository: DatastoreRepository = Depends(make_repository(DatastoreRepository)),
        credentials_repository: CredentialsRepository = Depends(make_repository(CredentialsRepository)),
        file_storage_manager: FileStorageManager = Depends(create_file_storage),
    ):
        self.repository = repository
        self.credentials_repository = credentials_repository
        self.file_storage_manager = file_storage_manager

    async def create(self, in_schema: datastore_schemas.CreateDatastoreSchema) -> datastore_schemas.DatastoreSchema:
        in_schema.id = uuid4()
        collection_name = in_schema.id.hex
        in_schema.collection_name = collection_name

        # get datastore options
        options = None
        if in_schema.options is not None:
            credentialsId = str(in_schema.options.get('credentials_id'))
            credentials = await self.credentials_repository.get_by_id(UUID(hex=credentialsId))
            if credentials is not None:
                options = credentials.data
                logging.info(f"choose custom datastore, provider: {in_schema.provider}, options: {options}")


        if options is None:
            options = DEFAULT_QDRANT_OPTIONS
            logging.info(f"choose default datastore, provider: {in_schema.provider}, options: {options}")

        vectorstore = DatastoreManager.get(in_schema.provider, options)
        await vectorstore.create_collection(collection_name) # TODO 要改成异步的

        return await self.repository.create(in_schema)

    # TODO 缓存
    async def get_by_id(self, id: UUID) -> Optional[datastore_schemas.DatastoreSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: datastore_schemas.UpdateDatastoreSchema) -> datastore_schemas.DatastoreSchema:
        return await self.repository.update_by_id(id, data)
        
    async def delete_by_id(self, id: UUID) -> None:
        datastore = await self.repository.delete_by_id(id)
        # TODO 根据 provider 策略来创建集合
        logging.info(f'datastore: {datastore.collection_name}')
    
        celery_app.send_task('delete_datastore_task', args=[datastore.dict()])
        return

   
    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[datastore_schemas.DatastoreSchema]:
        return await self.repository.paginate1(filter, params=params)
  
    async def count(self) -> int:
        return await self.repository.count()
  
    async def generate_upload_link(self, type: str, key: str) -> str:
        file_storage = self.file_storage_manager.load("s3", credentials_schemas.CredentialsSchemaBase(
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

        return await file_storage.generate_presigned_url(key)

    async def _get_datastore_options(self, datastore: datastore_schemas.DatastoreSchema) -> Dict[str, Any]:
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
        return options

    async def query(self, datastore_id: UUID, query: DocumentQuery) -> DocumentQueryResult:
        datastore = await self.repository.get_by_id(datastore_id)
        if not datastore:
            raise HTTPException(status_code=404, detail={ "error": "Datastore not found" })

        # get datastore options
        options = await self._get_datastore_options(datastore)
        vectorstore = DatastoreManager.get(datastore.provider, options)

        return await vectorstore.single_query(
            datastore.collection_name, 
            query,
        )
    

    async def multi_query(self, datastore_id: UUID, queries: List[DocumentQuery]) -> List[DocumentQueryResult]:
        datastore = await self.repository.get_by_id(datastore_id)
        if not datastore:
            raise HTTPException(status_code=404, detail={ "error": "Datastore not found" })

        options = await self._get_datastore_options(datastore)
        vectorstore = DatastoreManager.get(datastore.provider, options)

        return await vectorstore.query(
            datastore.collection_name, 
            queries,
        )
        