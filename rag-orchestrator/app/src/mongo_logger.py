from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient

from .schema import QueryRequest, RequestLog


class MongoLogger:
    def __init__(
        self, uri="mongodb://mongo:27017", db_name="rag_logs", collection="requests"
    ):
        self.client = MongoClient(uri)
        self.collection = self.client[db_name][collection]

    def log_request(
        self, request: QueryRequest, contexts: list[dict[str, Any]], answer: str
    ) -> None:
        log_entry = RequestLog(
            question=request.question,
            top_k=request.top_k,
            contexts=contexts,
            answer=answer,
            timestamp=datetime.now(timezone.utc),
        )
        self.collection.insert_one(log_entry.model_dump())
