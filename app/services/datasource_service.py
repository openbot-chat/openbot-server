from uuid import UUID
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException
from repositories.sqlalchemy.datasource_repository import DatasourceRepository
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.document_repository import DocumentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from api.dependencies.repository import make_repository
from models.datasource import *
from models.document import *
from schemas.pagination import CursorParams, CursorPage
from api.dependencies.file_storage import create_file_storage
import logging
import click
from core.file_storage.file_storage_manager import FileStorageManager
from celery_app import celery_app



class DatasourceService:
    def __init__(
        self, 
        document_repository: DocumentRepository = Depends(make_repository(DocumentRepository)),
        repository: DatasourceRepository = Depends(make_repository(DatasourceRepository)),
        datastore_repository: DatastoreRepository = Depends(make_repository(DatastoreRepository)),
        credentials_repository: CredentialsRepository = Depends(make_repository(CredentialsRepository)),
        file_storage_manager: FileStorageManager = Depends(create_file_storage),
    ):
        self.repository = repository
        self.document_repository = document_repository
        self.datastore_repository = datastore_repository
        self.credentials_repository = credentials_repository
        self.file_storage_manager = file_storage_manager

    async def create(self, in_schema: CreateDatasourceSchema) -> DatasourceSchema:
        datasource = await self.repository.create(in_schema)
        celery_app.send_task('load_datasource_task', args=[datasource.dict()])
        return datasource

    async def get_by_id(self, id: UUID) -> Optional[DatasourceSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdateDatasourceSchema) -> DatasourceSchema:
        print("ddd: ", data)
        datasource = await self.repository.update_by_id(id, data)

        if data.options is not None:
            task = celery_app.send_task('load_datasource_task', args=[datasource.dict()])
            logging.info(click.style(f"send task load_datasource_task, id: {task}", fg="green"))
        return datasource
  
    async def sync(self, id: UUID) -> DatasourceSchema:
        datasource = await self.repository.update_by_id(
            id, 
            UpdateDatasourceSchema(
                status="pending",
            )
        )

        # TODO 检查配额

        task = celery_app.send_task('load_datasource_task', args=[datasource.dict()])
        logging.info(click.style(f"send task load_datasource_task, id: {task}", fg="green"))
        return datasource

    async def delete_by_id(self, id: UUID) -> DatasourceSchema:
        datasource = await self.repository.delete_by_id(id)
        if not datasource:
            raise HTTPException(status_code=404, detail="Datasource not found")

        datastore = await self.datastore_repository.get_by_id(datasource.datastore_id)
        if not datastore:
            raise Exception("Datastore not found")

        # 有可能很多，通过异步任务来删除
        celery_app.send_task('delete_datasources_task', args=[[datasource.dict()]])
      
        return datasource

    async def bulk_delete(self, ids: List[str]) -> int:
        datasources = await self.repository.delete_by_ids(ids)

        # 有可能很多，通过异步任务来删除
        datasources_dict = [d.dict() for d in datasources]
        celery_app.send_task('delete_datasources_task', args=[datasources_dict])

        return len(datasources)

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[DatasourceSchema]:
        return await self.repository.paginate1(filter, params=params)
  
    async def count(self, filter: Dict[str, Any]) -> int:
        return await self.repository.count1(filter)

    # TODO 这里不需要 向量搜索
    async def list_documents(self, datasource_id: UUID, params: CursorParams) -> CursorPage[DocumentSchema]:
        _filter = {
            "datasource_id": datasource_id,
        }

        return await self.document_repository.paginate1(_filter, params=params)

    async def query_one(
        self,
        filter: Dict[str, Any],
    ) -> Optional[DatasourceSchema]:
        return await self.repository.query_one(filter)