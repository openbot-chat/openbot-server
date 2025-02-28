from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from models.chat import ChatMessage
from vectorstore import Document, DocumentQuery, DocumentMetadataFilter
from datetime import datetime
from .prompt import PromptSchemaBase

class BaseResponse(BaseModel):
    code: Optional[int]
    message: Optional[str]

class MessageResponse(BaseResponse):
    data: Optional[ChatMessage]

class UpsertDocumentRequest(BaseModel):
    documents: List[Document]

class UpsertDocumentResponse(BaseModel):
    ids: List[str]

class QueryDocumentRequest(BaseModel):
    queries: List[DocumentQuery]

class LoadPluginRequest(BaseModel):
    url: str

class VideoGenerationRequest(BaseModel):
    prompt: str
    source_url: str

class PredictionRequest(BaseModel):
    version: str
    input: Dict[str, Any]

class Prediction(BaseModel):
    id: str
    version: str
    urls: Dict[str, str]
    created_at: datetime
    started_at: datetime
    completed_at: datetime
    source: str # "web"
    status: str # "succeeded"


class PredictionListResponse(BaseModel):
    items: List[Prediction]
    next: Optional[str]
    previous: Optional[str]


class Model(BaseModel):
    id: str
    name: str
    url: str
    description: str

class ModelListResponse(BaseModel):
    items: List[Model]
    next: Optional[str]
    previous: Optional[str]

class DeleteRequest(BaseModel):
    ids: Optional[List[str]] = None
    filter: Optional[DocumentMetadataFilter] = None
    delete_all: Optional[bool] = False

class DeleteResponse(BaseModel):
    success: bool

class BulkDeleteRequest(BaseModel):
    ids: List[str]

class BulkDeleteResponse(BaseModel):
    count: int

class UploadLinkRequest(BaseModel):
    type: Optional[str]
    filename: str

class UploadLinkResponse(BaseModel):
    url: str

class ChainRequest(BaseModel):
    llm_config: Optional[Dict[str, Any]]
    streaming: Optional[bool] = False

class SummaryChainRequest(ChainRequest):
    chain_type: str
    documents: List[Document]
    prompt: Optional[PromptSchemaBase]
    map_prompt: Optional[PromptSchemaBase]
    combine_prompt: Optional[PromptSchemaBase]
    refine_prompt: Optional[PromptSchemaBase]
    question_prompt: Optional[PromptSchemaBase]



class ChainResponse(BaseModel):
   text: Optional[str]
   delta: Optional[str]