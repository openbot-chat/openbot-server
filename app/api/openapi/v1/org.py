from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from services.org_service import OrgService
from models.org import OrgSchema, CreateOrgSchema, UpdateOrgSchema
from models.org_member import OrgMemberSchema, CreateOrgMemberSchema
from api.dtos.org import AddMemberRequest
from api.dtos.org_member import OrgMemberDTO
from api.dtos.user import MinifiedUser
from uuid import UUID
from schemas.pagination import CursorParams, CursorPage

router = APIRouter()



@router.post("", status_code=201, response_model=OrgSchema)
async def create_a_org(
    request: Request,
    org: CreateOrgSchema,
    org_service: OrgService = Depends(OrgService),
):
    return await org_service.create(org)

@router.patch("/{org_id}", status_code=201, response_model=OrgSchema)
async def update_a_org(
    request: Request,
    org_id: UUID,
    data: UpdateOrgSchema,
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    if member.role != "ADMIN":
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await org_service.update_by_id(org_id, data)


@router.get("/{org_id}", status_code=200, response_model=Optional[OrgSchema])
async def get_a_org(
    request: Request,
    org_id: UUID,
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})
    
    return await org_service.get_by_id(org_id)


@router.delete("/{org_id}", status_code=201, response_model=OrgSchema)
async def delete_a_org(
    request: Request,
    org_id: UUID,
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await org_service.delete_by_id(org_id)


@router.post("/{org_id}/members", status_code=201, response_model=List[OrgMemberSchema])
async def add_members(
    request: Request,
    org_id: UUID,
    req: AddMemberRequest,
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    if member.role != "ADMIN":
        raise HTTPException(status_code=401, detail={'error': 'no permission'})        

    members = [CreateOrgMemberSchema(org_id=org_id, user_id=member.user_id, role=member.role) for member in req.members]
    return await org_service.add_members(members)

@router.delete("/{org_id}/members", status_code=201, response_model=List[OrgMemberSchema])
async def remove_members(
    request: Request,
    org_id: UUID,
    ids: List[str],
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    if member.role != "ADMIN":
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await org_service.remove_members(org_id, ids)

@router.get("/{org_id}/members/{user_id}", status_code=201, response_model=Optional[OrgMemberSchema])
async def get_member(
    request: Request,
    org_id: UUID,
    user_id: UUID,
    org_service: OrgService = Depends(OrgService),
):
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await org_service.get_member(org_id, user_id)


@router.get("", response_model=CursorPage[OrgSchema], response_model_exclude_unset=True)
async def list(
    request: Request,
    params: CursorParams = Depends(),
    org_service: OrgService = Depends(OrgService),
):
    filter = {
        "user_id": request.state.api_key.user_id
    }
    return await org_service.paginate(filter, params=params)

@router.get("/{org_id}", response_model=CursorPage[OrgMemberDTO], response_model_exclude_unset=True)
async def list_members(
    request: Request,
    org_id: UUID,
    params: CursorParams = Depends(),
    org_service: OrgService = Depends(OrgService),
):
    """获取 members 列表"""
    member = await org_service.get_member(org_id, request.state.api_key.user_id)
    if member is None:
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    page = await org_service.list_members(org_id, params=params)

    new_items = [
        OrgMemberDTO(
            id=item.id,
            user_id=item.user.id,
            user=MinifiedUser(
                id=item.user.id,
                name=item.user.name,
                avatar=item.user.avatar,
            ),
            role=item.role,
            org_id=item.org_id,
        ) 
        for item in page.items
    ]

    return CursorPage[OrgMemberDTO](
        items=new_items,
        params=params,
        next_page=page.next_page,
        previous_page=page.previous_page,
    )