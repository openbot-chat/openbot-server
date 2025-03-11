from typing import Optional, List
from pydantic import BaseModel



class CreatePromptDTO(BaseModel):
    name: str
    content: str
    input_variables: Optional[List[str]]