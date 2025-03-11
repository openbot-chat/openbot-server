from typing import Optional
from fastapi import Request
from security.auth0.auth import Auth0User

def get_auth_user(request: Request) -> Optional[Auth0User]:
    if not hasattr(request.state, 'user'):
        return None

    return request.state.user


def get_org_id(request: Request) -> Optional[str]:
    header_org_id = request.headers.get('x-org-id')
    query_org_id = request.query_params.get('org_id')
    return header_org_id or query_org_id