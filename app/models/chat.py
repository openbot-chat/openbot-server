from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List




class ChatUser(BaseModel):
    id: Optional[str] = None
    guest: Optional[bool] = True
    name: Optional[str] = None


class Media(BaseModel):
    url: str

class Voice(Media):
    duration: Optional[int] = None

class Image(Media):
    ...

class Video(Media):
    ...

class File(Media):
    ...

class ChatMessage(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = "text"
    text: Optional[str] = None
    voice: Optional[Voice] = None
    images: Optional[List[Image]] = None
    video: Optional[Video] = None
    files: Optional[List[File]] = None
    delta: Optional[str] = None
    role: Optional[str] = "human"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    from_user: Optional[ChatUser] = Field(None)
    to: Optional[ChatUser] = None
    sent_at: Optional[int] = None
    conversation_id: str
    streaming: Optional[bool] = False

class LLMMessage(BaseModel):
    conversation_id: Optional[str] = None
    role: str = "human"
    text: str