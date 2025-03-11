from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.pagination import CursorParams, CursorPage
from models.datasource import *
from models.document import *
from models.api import BulkDeleteRequest, BulkDeleteResponse
from services.datasource_service import DatasourceService
from uuid import UUID
from typing import Optional
from api.dtos.datasource import *



router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=DatasourceDTO, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_datasource(
    datasource: CreateDatasourceDTO,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    model = await datasource_service.create(CreateDatasourceSchema(**datasource.dict()))
    return DatasourceDTO(**model.dict())

@router.get("/{datasource_id}", response_model=Optional[DatasourceDTO], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_datasource(
    datasource_id: UUID,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    datasource = await datasource_service.get_by_id(datasource_id)
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    return DatasourceDTO(**datasource.dict())

@router.patch("/{datasource_id}", response_model=DatasourceDTO, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_datasource(
    datasource_id: UUID,
    req: UpdateDatasourceDTO,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    model = await datasource_service.update_by_id(datasource_id, UpdateDatasourceSchema(**req.dict()))
    return DatasourceDTO(**model.dict())

@router.delete("/{datasource_id}", status_code=204)
async def delete_a_datasource(
    datasource_id: UUID,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    await datasource_service.delete_by_id(datasource_id)

@router.post("/{datasource_id}/sync", status_code=200, response_model=DatasourceDTO, response_model_exclude_none=True, response_model_exclude_unset=True)
async def sync_a_datasource(
    datasource_id: UUID,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    model = await datasource_service.sync(datasource_id)
    return DatasourceDTO(**model.dict())

@router.post("/bulk-delete", status_code=200, response_model=BulkDeleteResponse)
async def bulk_delete_datasources(
    req: BulkDeleteRequest,
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    count = await datasource_service.bulk_delete(req.ids)
    return BulkDeleteResponse(count=count)

@router.get("", response_model=CursorPage, response_model_exclude_none=True, response_model_exclude_unset=True)
async def list_datasources(
    params: CursorParams = Depends(),
    datastore_id: UUID = Query(...),
    status: Optional[List[str]] = Query(None),
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    """获取 datasources 列表"""
    filter = {}
    filter['datastore_id'] = datastore_id
    if status is not None:
        filter['status'] = status

    print('datastore_id: ', datastore_id)

    page = await datasource_service.paginate(filter, params=params)
    return CursorPage[DatasourceDTO](
        items = [DatasourceDTO(**item.dict()) for item in page.items],
        params=params,
        next_page=page.next_page,
        previous_page=page.previous_page,
        total=page.total,
    )
    
@router.get("/{datasource_id}/documents", response_model=CursorPage[DocumentSchema], response_model_exclude_unset=True)
async def list_documents(
    datasource_id: UUID,
    params: CursorParams = Depends(),
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    """获取 documents 列表"""
    return await datasource_service.list_documents(datasource_id, params)