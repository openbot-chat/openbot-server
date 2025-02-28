from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import SecurityScopes
from security.auth0.auth import Auth0, Auth0HTTPBearer
# from api.context import global_org_id



from config import (
  AUTH0_DOMAIN,
  AUTH0_AUDIENCE,
)

auth = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_AUDIENCE, scopes={})



async def validate_auth0(request: Request):
    credfunc = Auth0HTTPBearer()
    creds = None
    try:
        creds = await credfunc(request)
    except Exception:
        ...

    user = await auth.get_user(
        security_scopes=SecurityScopes(),
        creds= creds
    )

    """
    if user.org_id is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Org must be provided",
            },
        )

    global_org_id.set(user.org_id)
    """

    request.state.user = user



# 集中处理认证，便于动态替换，后面要在网关集中认证
class Auth0Middleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
    await validate_auth0(request)
    return await call_next(request)