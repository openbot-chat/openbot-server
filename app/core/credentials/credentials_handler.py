from abc import ABC, abstractmethod
from models.credentials import CredentialsSchemaBase
from typing import Dict, Any, Optional



class CredentialsHandler(ABC):
    async def pre_authenticate(self, credentials: CredentialsSchemaBase) -> Dict[str, Any]:
        return {}
    
    @abstractmethod
    async def authenticate(
        self,
		    credentials: CredentialsSchemaBase,
		    options: Optional[Dict[str, Any]],
	) -> Dict[str, Any]:
        ...

