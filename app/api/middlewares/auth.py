from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from api.dependencies.database import get_superuser_session
from repositories.sqlalchemy.api_key_repository import ApiKeyRepository
from repositories.sqlalchemy.api_key import ApiKey
from models.api_key import ApiKeySchema

from api.context import global_org_id
from config import GATEWAY_API_KEY
from .auth0 import validate_auth0



async def validate_api_gateway_apikey(request: Request):
    gateway_api_key = request.headers.get('x-gateway-api-key')
    if gateway_api_key != GATEWAY_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Api key not valid"
        )





async def validate_and_get_api_token(request: Request) -> Optional[ApiKeySchema]:
    """
    Validate and get API token.
    """
    credfunc = HTTPBearer()
    creds = await credfunc(request)
    print('creds: ', creds.scheme, creds.credentials)

    if creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail={
            'error': f'auth scheme need to be bearer, but found {creds.scheme}'
        })

    api_key = None
    # async with get_superuser_session() as db_session:
    async for db_session in get_superuser_session():
        api_key_repository = ApiKeyRepository(db_session)
        api_key = await api_key_repository.get_by_token(creds.credentials)
    
    if not api_key:
        raise HTTPException(status_code=401, detail={'error': 'api_key not found'})
    return ApiKeySchema.from_orm(api_key)


# 集中处理认证，便于动态替换，后面要在网关集中认证
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            # webhooks
            if request.url.path.startswith("/web/v1/webhook"):
                pass
            # backend invoke
            elif request.url.path.startswith("/admin"):
                await validate_api_gateway_apikey(request)  
                request_org_id = request.headers.get('X-Org-Id')
                if request_org_id is not None:
                    global_org_id.set(request_org_id)
            # TODO web invoke
            #elif request.url.path.startswith("/web"):
            #    await validate_auth0(request)
            # openapi invoke
            elif request.url.path.startswith("/openapi"):
                request.state.api_key = await validate_and_get_api_token(request)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={'error': e.detail })
        except Exception as e:
            raise e

        return await call_next(request)