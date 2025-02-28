from typing import List, Any, Dict
from celery_app import celery_app
import logging
import click
from models.datastore import DatastoreSchema
from models.datasource import DatasourceSchema, UpdateDatasourceSchema
from models.api import DocumentMetadataFilter
from core.datasource.loaders.factory import DatasourceLoaderFactory
from core.datasource.loaders.context import LoaderContext
from asyncer import runnify
from repositories.sqlalchemy.datasource_repository import DatasourceRepository
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.document_repository import DocumentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from db.celery_session import async_session
from datetime import datetime
from core.file_storage.file_storage_manager import FileStorageManager
from models.credentials import CredentialsSchemaBase
import os
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from config import (
  DEFAULT_QDRANT_OPTIONS
)
from vectorstore import DatastoreManager
from uuid import UUID


@celery_app.task(
  name="load_datasource_task",
  task_name="load_datasource_task",
  soft_time_limit=86400,
)
def load_datasource_task(data):
    return runnify(async_load_datasource_task)(data)
    

async def async_load_datasource_task(data):
    async with async_session() as db_session:
        await _async_load_datasource_task(data, db_session)

async def _async_load_datasource_task(data, db_session: AsyncSession):
    datasource_repository = DatasourceRepository(db_session=db_session)
    datastore_repository = DatastoreRepository(db_session=db_session)
    document_repository = DocumentRepository(db_session=db_session)
    credentials_repository = CredentialsRepository(db_session=db_session)
    file_storage_manager = FileStorageManager()
    try:
        datasource = DatasourceSchema.parse_obj(data)
        logging.info(click.style('Start load datasource: {}'.format(datasource), fg='green'))
        # TODO 根据 org_id 查找对应 plan 和 Usage, 检查 Usage 是否大于 plan 限制

        datastore = await datastore_repository.get_by_id(datasource.datastore_id)
        if not datastore:
            raise Exception("Datastore not found")


        # get datastore options
        options = None
        if datastore.options is not None:
            credentialsId = str(datastore.options.get('credentials_id'))
            credentials = await credentials_repository.get_by_id(UUID(hex=credentialsId))
            if credentials is not None:
                options = credentials.data
                logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")

        if options is None:
            options = DEFAULT_QDRANT_OPTIONS
            logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

        vectorstore = DatastoreManager.get(datastore.provider, options)



        context = LoaderContext(
            datastore=datastore,
            datasource=datasource,
            document_repository=document_repository,
            credentials_repository=credentials_repository,
            file_storage_manager=file_storage_manager,
        )

        # 根据 datasource type 选择不同的 DatasourceLoader
        loader = DatasourceLoaderFactory.create(datasource.type)
        if loader is None:
            # TODO 找不到 loader,  任务运行失败，要更新记录
            logging.info(click.style(f'loader {datasource.type} for datasource: {datasource.id} not found', fg='green'))
            return None

        await datasource_repository.update_by_id(datasource.id, UpdateDatasourceSchema(
            status="running",
        ))

        # 先删除 datasource 中旧的 documents
        await document_repository.delete_many({"datasource_id": datasource.id})

        r = await vectorstore.delete(
            datastore.collection_name,
            filter=DocumentMetadataFilter(
                source_id=str(datasource.id),
            ),
        )
        logging.info(click.style(f'delete old documents from vectorstore for datasource {datasource.id}, success: {r}', fg='green'))


        # upsert vectorstore
        await loader.load(context)

        await datasource_repository.update_by_id(datasource.id, UpdateDatasourceSchema(
            status="synced",
            last_sync=datetime.now(),
        ))

        logging.info(click.style(f'{datasource.id}: datasource runned successfully', fg="green"));
    except Exception:
        logging.error(click.style(f'{datasource.id}: datasource load error', fg="red"))
        print(traceback.format_exc())

        await datasource_repository.update_by_id(datasource.id, UpdateDatasourceSchema(
            status="error",
        ))





@celery_app.task(
  name="delete_datasources_task",
  task_name="delete_datasources_task",
  soft_time_limit=86400,
)
def delete_datasources_task(data: List[Any]):
    return runnify(async_delete_datasources_task)(data)

async def async_delete_datasources_task(data: List[Any]):
    async with async_session() as db_session:
      for item in data:
        datasource = DatasourceSchema.parse_obj(item)
        await delete_datasource(datasource, db_session)

async def delete_datasource(datasource: DatasourceSchema, db_session: AsyncSession):
    logging.info(click.style('Start delete datasource: {}'.format(datasource), fg='green'))
    datastore_repository = DatastoreRepository(db_session=db_session)
    credentials_repository = CredentialsRepository(db_session=db_session)
    datastore = await datastore_repository.get_by_id(datasource.datastore_id)
    if not datastore:
      return

    # get datastore options
    options = None
    if datastore.options is not None:
        credentialsId = str(datastore.options.get('credentials_id'))
        credentials = await credentials_repository.get_by_id(UUID(hex=credentialsId))
        if credentials is not None:
            options = credentials.data
            logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")

    if options is None:
        options = DEFAULT_QDRANT_OPTIONS
        logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

    vectorstore = DatastoreManager.get(datastore.provider, options)


    # Delete from datastore

    success = await vectorstore.delete(
      datastore.collection_name,
      filter=DocumentMetadataFilter(
        source_id=str(datasource.id),
      ),
    )

    if success:
        logging.info(click.style(f"Delete Datasource {datasource.id} from vectorstore {datastore.provider} {datastore.id}, success: {success}", fg="green"))
    else:
        logging.error(click.style(f"Delete Datasource {datasource.id} from vectorstore {datastore.provider} {datastore.id}, success: {success}", fg="red"))
     

    # Add to File Storage
    credentials = CredentialsSchemaBase(
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
    )

    # Delete all cloud files

    file_storage_manager = FileStorageManager()

    key = f"datastores/{datasource.datastore_id}/{datasource.id}"
    file_storage = file_storage_manager.load("s3", credentials)
    
    async for page in file_storage.list_objects(key):
        objs = page.get('Contents', [])
        for obj in objs:
          logging.info(click.style(f'Start delete datasource: {datasource.id}, file key: {obj["Key"]}', fg='green'))
          await file_storage.delete_object(obj["Key"])

    # datasource 被删除时, 数据源下的 documents 记录会被级联删除

  



@celery_app.task(
  name="delete_datastore_task",
  task_name="delete_datastore_task",
  soft_time_limit=86400,
)
def delete_datastore_task(data: List[Any]):
    return runnify(async_delete_datastore_task)(data)

async def async_delete_datastore_task(data: Any):
    datastore = DatastoreSchema.parse_obj(data)
    async with async_session() as db_session:
        await delete_datastore(db_session, datastore)

async def delete_datastore(db_session: AsyncSession, datastore: DatastoreSchema):
    logging.info(click.style('Start delete datastore: {}'.format(datastore), fg='green'))

    credentials_repository = CredentialsRepository(db_session=db_session)

    # get datastore options
    options = None
    if datastore.options is not None:
        credentialsId = str(datastore.options.get('credentials_id'))
        credentials = await credentials_repository.get_by_id(UUID(hex=credentialsId))
        if credentials is not None:
            options = credentials.data
            logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")

    if options is None:
        options = DEFAULT_QDRANT_OPTIONS
        logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

    vectorstore = DatastoreManager.get(datastore.provider, options)

    # Delete from vectorstore
    success = vectorstore.delete_collection(datastore.collection_name)
    logging.info(click.style(f"Delete Datastore {datastore.id}, vectorstore {datastore.provider} {datastore.collection_name}, success: {success}", fg="green"))

    # Delete all cloud files
    credentials = CredentialsSchemaBase(
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
    )

    file_storage_manager = FileStorageManager()

    key = f"datastores/{datastore.id}"
    file_storage = file_storage_manager.load("s3", credentials)
    
    async for page in file_storage.list_objects(key):
        objs = page.get('Contents', [])
        for obj in objs:
            logging.info(click.style(f'Start delete file key: {obj["Key"]}', fg='green'))
            await file_storage.delete_object(obj["Key"])

    logging.info(click.style(f'Delete datastore {datastore.id} completed', fg='green'))

    # datasource 被删除时, 数据源下的 documents 记录会被级联删除