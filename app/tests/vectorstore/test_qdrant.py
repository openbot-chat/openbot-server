from langchain.document_loaders.parsers import OpenAIWhisperParser
import uuid
from typing import Any, List, Optional, Dict
from qdrant_client.http.api_client import AsyncApis

import pytest
from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
)


async_client = AsyncApis(
    host=QDRANT_URL,
    headers={
        "api-key": QDRANT_API_KEY,
    }
)


@pytest.mark.asyncio
async def test_qdrant_async():
    c = await async_client.collections_api.get_collection("memory")
    print("c: ", c)