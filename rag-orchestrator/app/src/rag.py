import uuid
from typing import Optional

import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from .config import (
    BENTOML_EMBEDDING_URL,
    BENTOML_MODEL_URL,
    COLLECTION_NAME,
    QDRANT_URL,
)
from .utils import auto_tag, chunk_text, logger


class RAGPipeline:
    def __init__(
        self,
        embedding_url: str = BENTOML_EMBEDDING_URL,
        model_url: str = BENTOML_MODEL_URL,
        collection_name: str = COLLECTION_NAME,
        qdrant_url: str = QDRANT_URL,
    ):
        self.qdrant_url = qdrant_url
        self.model_url = model_url
        self.embedding_url = embedding_url
        self.qdrant = QdrantClient(
            host=self.qdrant_url.split("//")[-1].split(":")[0],
            port=int(self.qdrant_url.split(":")[-1]),
        )
        self.collection_name = collection_name

        self._ensure_collection()

    def _ensure_collection(self):
        if self.collection_name not in [
            c.name for c in self.qdrant.get_collections().collections
        ]:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")

            self.qdrant.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384, distance=Distance(value="Cosine")
                ),
            )

    def get_embedding(self, text: str):
        response = requests.post(
            f"{self.embedding_url}/embed", json={"body": {"text": text}}
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def ingest(self, text: str, metadata: Optional[dict] = None):
        embedding = self.get_embedding(text)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text, **(metadata or {})},
        )
        self.qdrant.upsert(collection_name=self.collection_name, points=[point])
        logger.info(f"Ingested document into {self.collection_name}")

    def split_and_ingest(
        self,
        text: str,
        source: str = "unknown",
        metadata: Optional[dict] = None,
        chunk_size: int = 200,
        overlap: int = 20,
        top_n_tags: int = 3,
    ):
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        tags = auto_tag(text, top_n=top_n_tags)
        doc_id = str(uuid.uuid4())
        base_metadata = metadata or {}

        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "source": source,
                "chunk_id": i,
                "doc_id": doc_id,
                "tags": tags,
                **base_metadata,
            }
            self.ingest(chunk, metadata=chunk_metadata)

        logger.info(f"Split and ingested {len(chunks)} chunks from source: {source}")

    def retrieve(self, query: str, top_k: int = 3):
        embedding = self.get_embedding(query)
        hits = self.qdrant.search(
            collection_name=self.collection_name, query_vector=embedding, limit=top_k
        )
        return [
            {
                "text": hit.payload["text"],
                "author": hit.payload.get("author"),
                "source": hit.payload.get("source"),
                "doc_id": hit.payload.get("doc_id"),
                "chunk_id": hit.payload.get("chunk_id"),
                "tags": hit.payload.get("tags"),
                "score": hit.score,
            }
            for hit in hits
            if (hit.payload is not None) and (hit.score > 0.5)
        ]

    def generate(self, question: str, context: str):
        prompt = (
            f"Answer the question based only on the context.\n\n"
            f"Context: {context}\n"
            f"Question: {question}\n"
            f"Answer:"
        )
        response = requests.post(
            f"{self.model_url}/generate",
            json={"body": {"prompt": prompt, "max_tokens": 128}},
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def query(self, question: str, top_k: int = 3):
        hits = self.retrieve(question, top_k=top_k)
        context = "\n".join([hit["text"] for hit in hits])
        answer = self.generate(question, context)
        return answer
