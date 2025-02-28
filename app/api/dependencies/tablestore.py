from fastapi.requests import Request
# from tablestore.client import OTSClient
from typing import Any

# OTSClient
def get_client(request: Request) -> Any:
  return None
  # return request.app.state.tablestore_client