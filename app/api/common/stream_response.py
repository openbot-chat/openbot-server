import logging
from typing import Callable, Awaitable, Union, Any
from fastapi.responses import StreamingResponse as _StreamingResponse
from starlette.types import Send
import json
import traceback


class StreamingResponse(_StreamingResponse):
    def __init__(self, generate: Callable[[Send], Awaitable[Any]], **kwargs: Any):
        super().__init__(content=iter(()), **kwargs)
        self.generate = generate
  
    async def stream_response(self, send: Send) -> None:
        print('stream_response', send)
        await send(
        {
            "type": "http.response.start",
            "status": self.status_code,
            "headers": self.raw_headers,
        })

        async def send_chunk(chunk: Union[str, bytes]):
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        try:
            outputs = await self.generate(send_chunk)
            if self.background is not None:
                self.background.kwargs["outputs"] = outputs
        except Exception as e:
            print('stream_response error: ', traceback.format_exc())
            
            if self.background is not None:
                self.background.kwargs["outputs"] = str(e)
            msg = {
                "delta": str(e),
            }
            await send({
                "type": "http.response.body",
                "body": f"data: {json.dumps(msg)}\n\n",
                "more_body": False,
            })
            return

        await send({"type": "http.response.body", "body": b"[DONE]\n\n", "more_body": False})
