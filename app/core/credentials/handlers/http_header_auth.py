from models.credentials import CredentialsSchemaBase
from typing import Dict, Any, Optional
from core.credentials.credentials_handler import CredentialsHandler


class HttpHeaderAuth(CredentialsHandler):
    async def authenticate(
        self,
		    credentials: CredentialsSchemaBase,
		    options: Optional[Dict[str, Any]],
	) -> Dict[str, Any]:
        name = str(credentials.data.get("name"))
        value = str(credentials.data.get("value"))

        headers: Dict[str, str] = {}
        headers[name] = value
        new_options = options.copy() if options is not None else {}

        old_headers = new_options.get("headers")
        if old_headers:
            headers.update(old_headers)

        new_options["headers"] = headers
        return new_options