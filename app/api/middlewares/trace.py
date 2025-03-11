from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from fastapi import Request, Response
import logging
import click
import time
from uuid import uuid4


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.req_id = uuid4()

        #if request.url.path != '/health':
        #    print(click.style(f'>> begin new request, id: {request.state.req_id}, path: {request.url.path}', fg="yellow"))

        start_time = time.monotonic()

        res = await call_next(request)

        end_time = time.monotonic()

        duration_ms = int((end_time - start_time) * 1000)

        #if request.url.path != '/health':
        #    print(click.style(f'<< end request, id: {request.state.req_id}, path: {request.url.path}, elapsed: {duration_ms}ms', fg="yellow"))

        res.headers['x-request-id'] = str(request.state.req_id)

        return res