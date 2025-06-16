from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class IngestRequest(BaseModel):
    """Request model for ingesting documents"""

    text: str
    metadata: Optional[dict] = None


class IngestResponse(BaseModel):
    """Response model for document ingestion"""

    status: str
    metadata: Optional[dict] = None


class QueryRequest(BaseModel):
    """..."""

    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    """..."""

    answer: str


class RequestLog(BaseModel):
    """..."""

    question: str
    top_k: int
    contexts: list[Any]  # need to fix any
    answer: str
    timestamp: datetime
