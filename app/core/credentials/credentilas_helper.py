from typing import Union, Dict, Any, Optional
from models.credentials import CredentialsSchemaBase
from .credentials_handler import CredentialsHandler

from .handlers.http_header_auth import HttpHeaderAuth
from .handlers.tiktok import TiktokAuth
import aiohttp
from yarl import URL
import time


credential_handlers: Dict[str, CredentialsHandler] = {
    "http_header_auth": HttpHeaderAuth(),
    "tiktok": TiktokAuth(),
}



class CredentialsHelper:
    @classmethod
    async def pre_authenticate(
        cls,
        credentials: CredentialsSchemaBase
    ) -> Dict[str, Any]:
        credential_handler = credential_handlers.get(credentials.type)
        if not credential_handler:
            raise Exception(f"Credentials not found for type {credentials.type}")

        return await credential_handler.pre_authenticate(credentials)

    @classmethod
    async def authenticate(
        cls,
        credentials: CredentialsSchemaBase,
        options: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        credential_handler = credential_handlers.get(credentials.type)
        if not credential_handler:
            raise Exception(f"Credentials not found for type {credentials.type}")

        return await credential_handler.authenticate(credentials, options)


    @classmethod
    async def request(
        cls,
        method: str, 
        url: Union[str, URL], 
        credentials: Optional[CredentialsSchemaBase] = None,
        **kwargs: Any
    ):
        new_kwargs = kwargs
        if credentials is not None:
            create_time = credentials.data.get("create_time", None)
            if create_time is not None:
                expires_in = credentials.data.get("expires_in", 7200)
                now = time.time()
            
                # 需要重新 pre_authenticate
                if int(now) - expires_in > create_time:
                    options = await CredentialsHelper.pre_authenticate(credentials)
                    credentials.data.update(options)
           
            new_kwargs = await CredentialsHelper.authenticate(credentials, kwargs)

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **new_kwargs) as response:
                return response.json()