from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Body, HTTPException, UploadFile, File, Query
from schemas.pagination import CursorParams, CursorPage
from models.datastore import *
from models.datasource import *
from models.api import UploadLinkRequest, UploadLinkResponse, UpsertDocumentRequest, UpsertDocumentResponse, QueryDocumentRequest, DeleteResponse, DeleteRequest
from services.datastore_service import DatastoreService
from services.datasource_service import DatasourceService
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user
from uuid import UUID
from vectorstore.models import DocumentQuery, DocumentQueryResult
from vectorstore.datastore_manager import DatastoreManager
from config import (
    DEFAULT_QDRANT_OPTIONS
)
from api.dtos.datasource import *


router = APIRouter()

@router.post("", status_code=201, response_model=DatastoreSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_datastore(
  datastore: CreateDatastoreSchema,
  datastore_service: DatastoreService = Depends(DatastoreService),
  user: Auth0User = Depends(get_auth_user),
):
  return await datastore_service.create(datastore)

@router.get("/{datastore_id}", response_model=Optional[DatastoreSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_datastore(
    datastore_id: UUID,
    datastore_service: DatastoreService = Depends(DatastoreService),
    user: Auth0User = Depends(get_auth_user),
):
    datastore = await datastore_service.get_by_id(datastore_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")
    return datastore


@router.patch("/{datastore_id}", response_model=DatastoreSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_datastore(
    datastore_id: UUID,
    data: UpdateDatastoreSchema,
    datastore_service: DatastoreService = Depends(DatastoreService),
    user: Auth0User = Depends(get_auth_user),
):
    return await datastore_service.update_by_id(datastore_id, data)

@router.delete("/{datastore_id}", status_code=204)
async def delete_a_datastore(
    datastore_id: UUID,
    datastore_service: DatastoreService = Depends(DatastoreService),
):
    await datastore_service.delete_by_id(datastore_id)

@router.get("", response_model=CursorPage[DatastoreSchema], response_model_exclude_unset=True)
async def list_datastores(
    org_id: str = Query(...),
    params: CursorParams = Depends(),
    datastore_service: DatastoreService = Depends(DatastoreService),
    user: Auth0User = Depends(get_auth_user),
):
    """获取 datastores 列表"""
    filter = {
        "org_id": org_id,
    }
    return await datastore_service.paginate(filter, params=params)

@router.post(
    "/{datastore_id}/upsert-file",
    response_model=UpsertDocumentResponse,
)
async def upsert_file(
    datastore_id: str,
    file: UploadFile = File(...),
    # token: HTTPAuthorizationCredentials = Depends(validate_token),
    # 只是提交任务
):
    pass
  
  
# 加载文档, 更多是用这个接口，由外部结构化数据之后，进行写入
@router.post(
    '/{datastore_id}/documents/upsert',
    response_model=UpsertDocumentResponse,
    response_model_exclude_none=True,
)
async def upsert_documents(
    datastore_id: UUID,
    request: Request,
    datastore_service: DatastoreService = Depends(DatastoreService),
    req: UpsertDocumentRequest = Body(...),
):
    datastore = await datastore_service.get_by_id(datastore_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")

    vectorstore = DatastoreManager.get(datastore.provider, datastore.options or DEFAULT_QDRANT_OPTIONS)

    result = await vectorstore.upsert(datastore.collection_name, req.documents)
    ids = result.keys()

    return UpsertDocumentResponse(ids=ids)

# 加载文档, 更多是用这个接口，由外部结构化数据之后，进行写入
@router.delete(
    '/{datastore_id}/documents',
    response_model=DeleteResponse,
    response_model_exclude_none=True,
)
async def delete_documents(
    datastore_id: UUID,
    request: Request,
    req: DeleteRequest = Body(...),
    datastore_service: DatastoreService = Depends(DatastoreService),
):
    if not (req.ids or req.filter or req.delete_all):
        raise HTTPException(
            status_code=400,
            detail="One of ids, filter, or delete_all is required",
        )
  
    datastore = await datastore_service.get_by_id(datastore_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")

    success = await request.app.state.vectorstore.delete(
        datastore.collection_name,
        ids=req.ids,
        filter=req.filter,
        delete_all=req.delete_all,
    )
    return DeleteResponse(success=success)




@router.get("/{datastore_id}/datasources/{datasource_id}", response_model=Optional[DatasourceSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_datasource(
    datastore_id: UUID,
    datasource_id: UUID,
    datasource_service: DatasourceService = Depends(DatasourceService),
    user: Auth0User = Depends(get_auth_user),
):
    return await datasource_service.query_one({
        "datastore_id": datastore_id,
        "datasource_id": datasource_id,
    })



@router.post("/{datastore_id}/datasources", response_model=DatasourceSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_datasource(
    datastore_id: UUID,
    data: CreateDatasourceSchema,
    datasource_service: DatasourceService = Depends(DatasourceService),
    datastore_service: DatastoreService = Depends(DatastoreService),
    user: Auth0User = Depends(get_auth_user),
):
    # TODO 在 datasource 保存 datastore foreign_key 的时候没有 rls 保护
    datastore = await datastore_service.get_by_id(datastore_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")

    data.datastore_id = datastore_id
    return await datasource_service.create(data)

@router.patch("/{datastore_id}/datasources/{datasource_id}", response_model=DatasourceSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_datasource(
    datastore_id: UUID,
    datasource_id: UUID,
    data: UpdateDatasourceSchema,
    datastore_service: DatastoreService = Depends(DatastoreService),
    datasource_service: DatasourceService = Depends(DatasourceService),
    user: Auth0User = Depends(get_auth_user),
):
    datasource = await datasource_service.get_by_id(datasource_id)
    if not datasource:
        raise HTTPException(status_code=400, detail="Datasource not found")
    
    if datasource.datastore_id != datastore_id:
        raise HTTPException(status_code=400, detail="Datasource not found")

    return await datasource_service.update_by_id(datasource_id, data)

@router.delete("/{datastore_id}/datasources/{datasource_id}", status_code=204)
async def delete_a_datasource(
    datastore_id: UUID,
    datasource_id: UUID,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    datasource = await datasource_service.get_by_id(datasource_id)
    if not datasource:
        raise HTTPException(status_code=400, detail="Datasource not found")
    
    if datasource.datastore_id != datastore_id:
        raise HTTPException(status_code=400, detail="Datasource not found")

    await datasource_service.delete_by_id(datasource_id)

@router.get("/{datastore_id}/datasources", response_model=CursorPage[DatasourceDTO], response_model_exclude_unset=True)
async def list_datasources(
    datastore_id: UUID,
    params: CursorParams = Depends(),
    datasource_service: DatasourceService = Depends(DatasourceService),
    user: Auth0User = Depends(get_auth_user),
):
    """获取 datasources 列表"""
    filter = {
        "datastore_id": datastore_id,
    }

    page = await datasource_service.paginate(filter, params=params)
    return CursorPage[DatasourceDTO](
        items = [DatasourceDTO(**item.dict()) for item in page.items],
        params=params,
        next_page=page.next_page,
        previous_page=page.previous_page,
        total=page.total,
    )

@router.post("/{datastore_id}/generate-upload-link", response_model=UploadLinkResponse, response_model_exclude_unset=True)
async def generate_upload_link(
    datastore_id: UUID,
    req: UploadLinkRequest = Body(...),
    datastore_service: DatastoreService = Depends(DatastoreService),
):
    """获取上传链接"""

    datastore = await datastore_service.get_by_id(datastore_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")

    key = f'datastores/{datastore.id}/{req.filename}'
    url = await datastore_service.generate_upload_link(req.type, key)
    return UploadLinkResponse(
        url=url
    )


@router.post("/{datastore_id}/query", response_model=DocumentQueryResult, response_model_exclude_unset=True)
async def query(
    datastore_id: UUID,
    query: DocumentQuery = Body(...),
    datastore_service: DatastoreService = Depends(DatastoreService),
    user: Auth0User = Depends(get_auth_user),
):
    """查询 documents"""

    return await datastore_service.query(datastore_id, query)


@router.post('/{datastore_id}/multi-query', response_model=List[DocumentQueryResult])
async def multi_query(
    datastore_id: UUID,
    request: Request,
    req: QueryDocumentRequest = Body(...),
    datastore_service: DatastoreService = Depends(DatastoreService),
):
    return await datastore_service.multi_query(datastore_id, req.queries)