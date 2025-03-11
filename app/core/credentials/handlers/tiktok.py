from models.credentials import CredentialsSchemaBase
from typing import Dict, Any, Optional
from core.credentials.credentials_handler import CredentialsHandler
import aiohttp
import time

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


class TiktokAuth(CredentialsHandler):
    async def pre_authenticate(self, credentials: CredentialsSchemaBase) -> Dict[str, Any]:
        client_key = credentials.data.get("client_key")
        client_secret = credentials.data.get("client_secret")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }

        data = {
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, data=data, headers=headers) as response:
                result = await response.json()
                """
                "access_token": "clt.a3fb80fcb790e1e92502eba123f274f1CC7RPNBqVcZQLO30WyMiE3RyhPov",
                "expires_in": 7200,
                "token_type": "Bearer"
                """
                now = time.time()
                data = {
                    "create_time": int(now),
                }
                data.update(result)
                print("token result: ", result)
                return result
        

    async def authenticate(
        self,
		    credentials: CredentialsSchemaBase,
		    options: Optional[Dict[str, Any]],
	) -> Dict[str, Any]:
        access_token = credentials.data.get("access_token", None)
        if not access_token:
            # TODO AuthException()
            raise Exception("access_token not found")

        create_time = credentials.data.get("create_time", None)
        if not create_time:
            # TODO AuthException()
            raise Exception("create_time not found")

        expires_in = credentials.data.get("expires_in", None)
        if not expires_in:
            expires_in = 7200

        now = time.time()

        if int(now) - expires_in >= create_time:
            raise Exception("access_token expires, need pre_authenticate")


        new_options = options.copy() if options is not None else {}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        old_headers = new_options.get("headers", {})
        headers.update(old_headers)

        return new_options