import bentoml
from sentence_transformers import SentenceTransformer
from bentoml.io import JSON
from pydantic import BaseModel


class EmbedRequest(BaseModel):
    text: str
    
@bentoml.service(resources={"cpu": "1"})
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @bentoml.api()
    def embed(self, body: EmbedRequest):
        embedding = self.model.encode([body.text])[0].tolist()
        return {"embedding": embedding}
