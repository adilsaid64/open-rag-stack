import requests
import uuid
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue

from .config import QDRANT_URL, COLLECTION_NAME, BENTOML_MODEL_URL, BENTOML_EMBEDDING_URL
from .utils import logger

class RAGPipeline:
    def __init__(self, embedding_url: str = BENTOML_EMBEDDING_URL, model_url: str = BENTOML_MODEL_URL, collection_name: str = COLLECTION_NAME, qdrant_url : str = QDRANT_URL):
        self.qdrant_url = qdrant_url
        self.model_url = model_url
        self.embedding_url = embedding_url
        self.qdrant = QdrantClient(host=self.qdrant_url.split('//')[-1].split(':')[0], port=int(self.qdrant_url.split(':')[-1]))
        self.collection_name = collection_name
    
        self._ensure_collection()

    def _ensure_collection(self):
        if self.collection_name not in [c.name for c in self.qdrant.get_collections().collections]:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.qdrant.recreate_collection(
                collection_name=self.collection_name,
                vectors_config={"size": 384, "distance": "Cosine"}
            )

    def get_embedding(self, text: str):
        response = requests.post(f"{self.embedding_url}/embed", json={"body": {"text": text}})
        response.raise_for_status()
        return response.json()["embedding"]
    
    def ingest(self, text: str, metadata: Optional[dict] = None):
        embedding = self.get_embedding(text)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text, **(metadata or {})}
        )
        self.qdrant.upsert(collection_name=self.collection_name, points=[point])
        logger.info(f"Ingested document into {self.collection_name}")

    def retrieve(self, query: str, top_k: int = 3):
        embedding = self.get_embedding(query)
        hits = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=top_k
        )
        return [hit.payload["text"] for hit in hits]

    def generate(self, question: str, context: str):
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        response = requests.post(f"{self.model_url}/generate", json={"body": {"prompt": prompt, "max_tokens": 128}})
        response.raise_for_status()
        return response.json().get("response", "")

    def query(self, question: str, top_k: int = 3):
        contexts = self.retrieve(question, top_k=top_k)
        context = "\n".join(contexts)
        answer = self.generate(question, context)
        return answer 