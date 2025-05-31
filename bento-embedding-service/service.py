import bentoml
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


@bentoml.service(resources={"cpu": "1"})
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @bentoml.api
    def embed(self, body: EmbedRequest) -> EmbedResponse:
        embedding = self.model.encode([body.text])[0].tolist()
        return EmbedResponse(embedding=embedding)
