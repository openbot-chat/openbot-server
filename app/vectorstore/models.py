from typing import List, Optional, Dict, Any
from pydantic import BaseModel


"""
source_type: Optional[str] = None
source: Optional[str] = None
source_id: Optional[str] = None
url: Optional[str] = None
created_at: Optional[str] = None
author: Optional[str] = None
language: Optional[str] = None
description: Optional[str] = None
title: Optional[str] = None
page: Optional[int] = None
file_path: Optional[str] = None
file_name: Optional[str] = None
file_type: Optional[str] = None
"""

class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    author: Optional[str] = None
    start_date: Optional[str] = None  # any date string format
    end_date: Optional[str] = None  # any date string format

class DocumentQuery(BaseModel):
    query: str
    filter: Optional[DocumentMetadataFilter] = None
    top_k: Optional[int] = 4
    score_threshold: Optional[float] = None
    offset: int = 0

class DocumentChunkWithScore(DocumentChunk):
    score: float

class QueryWithEmbedding(DocumentQuery):
    embedding: List[float]

class DocumentQueryResult(BaseModel):
    query: str
    results: List[DocumentChunkWithScore]
