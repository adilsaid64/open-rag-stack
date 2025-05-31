from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from pymongo import MongoClient


class RequestLog(BaseModel):
    question: str
    top_k: int
    contexts: list[Any]
    answer: str
    timestamp: datetime


class MongoLogger:
    def __init__(
        self, uri="mongodb://mongo:27017", db_name="rag_logs", collection="requests"
    ):
        self.client = MongoClient(uri)
        self.collection = self.client[db_name][collection]

    def log_request(self, request, contexts, answer) -> None:
        log_entry = RequestLog(
            question=request.question,
            top_k=request.top_k,
            contexts=contexts,
            answer=answer,
            timestamp=datetime.now(timezone.utc),
        )
        self.collection.insert_one(log_entry.model_dump())
