from pydantic import BaseModel

class CreateMessageDTO(BaseModel):
    type: str
    text: str
