from fastapi.requests import Request
from typing import Any
from redis.asyncio import Redis 

def get_redis(request: Request) -> Redis:
    return request.app.state.redis