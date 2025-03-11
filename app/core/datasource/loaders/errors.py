from typing import Optional
from uuid import UUID

class DatasourceLoadError(Exception):
    datasource_id: UUID
    description: Optional[str] = None

    def __init__(
        self, 
        datasource_id: UUID, 
        description: Optional[str] = None,
    ):
        super().__init__()
        self.datasource_id = datasource_id
        if description is not None:
            self.description = description