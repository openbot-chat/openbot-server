from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.pagination import CursorParams, CursorPage
from models import document as document_schemas
from models.api import BulkDeleteRequest, BulkDeleteResponse
from services.document_service import DocumentService
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user
from uuid import UUID


router = APIRouter()

@router.post("", status_code=201, response_model=document_schemas.DocumentSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_document(
    document: document_schemas.CreateDocumentSchema,
    document_service: DocumentService = Depends(DocumentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await document_service.create(document)

@router.get("/{document_id}", response_model=document_schemas.DocumentSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_document(
    document_id: UUID,
    document_service: DocumentService = Depends(DocumentService),
    user: Auth0User = Depends(get_auth_user),
):
    document = await document_service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.patch("/{document_id}", response_model=document_schemas.DocumentSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_document(
    document_id: UUID,
    data: document_schemas.UpdateDocumentSchema,
    document_service: DocumentService = Depends(DocumentService),
    user: Auth0User = Depends(get_auth_user),
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

@router.get("", response_model=CursorPage[document_schemas.DocumentSchema], response_model_exclude_unset=True)
async def list_documents(
    params: CursorParams = Depends(),
    datasource_id: Optional[UUID] = Query(None),
    document_service: DocumentService = Depends(DocumentService),
    user: Auth0User = Depends(get_auth_user),
):
    """获取 documents 列表"""
    filter: Dict[str, Any] = {}
    if datasource_id is not None:
        filter['datasource_id'] = datasource_id

    return await document_service.paginate(filter, params=params)