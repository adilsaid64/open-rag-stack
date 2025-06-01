from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class IngestRequest(BaseModel):
    """..."""

    text: str
    metadata: Optional[dict] = None


class IngestResponse(BaseModel):
    """..."""

    status: str


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
