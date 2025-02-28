from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from fastapi import Request, Response
from api.context import global_org_id

# 集中处理认证，便于动态替换，后面要在网关集中认证
class GatewayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_org_id = request.headers.get('X-Org-Id')
        if request_org_id is not None:
            global_org_id.set(request_org_id)

        return await call_next(request)

def get_global_org_id():
    return global_org_id.get()