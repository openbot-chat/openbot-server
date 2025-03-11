from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.pagination import CursorParams, CursorPage
from models.document import *
from models.api import BulkDeleteRequest, BulkDeleteResponse
from services import (
    DocumentService,
    DatasourceService,
)
from uuid import UUID


router = APIRouter()

@router.post("", status_code=201, response_model=DocumentSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_document(
    data: CreateDocumentSchema,
    document_service: DocumentService = Depends(DocumentService),
    datasource_service: DatasourceService = Depends(DatasourceService),
):
    datasource = await datasource_service.get_by_id(data.datasource_id)
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    data.org_id = datasource.org_id
    return await document_service.create(data)

@router.get("/{document_id}", response_model=Optional[DocumentSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_document(
    document_id: UUID,
    document_service: DocumentService = Depends(DocumentService),
):
    document = await document_service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.patch("/{document_id}", response_model=DocumentSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_document(
    document_id: UUID,
    data: UpdateDocumentSchema,
    document_service: DocumentService = Depends(DocumentService),
):
    return await document_service.update_by_id(document_id, data)

@router.delete("/{document_id}", status_code=204)
async def delete_a_document(
    document_id: UUID,
    document_service: DocumentService = Depends(DocumentService),
):
  await document_service.delete_by_id(document_id)

@router.post("/bulk-delete", status_code=200, response_model=BulkDeleteResponse)
async def bulk_delete_documents(
    req: BulkDeleteRequest,
    document_service: DocumentService = Depends(DocumentService),
):
    count = await document_service.bulk_delete(req.ids)
    return BulkDeleteResponse(count=count)

@router.get("", response_model=CursorPage[DocumentSchema], response_model_exclude_unset=True)
async def list_documents(
    params: CursorParams = Depends(),
    datasource_id: Optional[UUID] = Query(None),
    document_service: DocumentService = Depends(DocumentService),
):
    """获取 documents 列表"""
    filter: Dict[str, Any] = {}
    if datasource_id is not None:
        filter['datasource_id'] = datasource_id

    return await document_service.paginate(filter, params=params)