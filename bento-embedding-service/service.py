import bentoml
from sentence_transformers import SentenceTransformer

class EmbedRequest(bentoml.IODescriptor):
    text: str
    
class EmbedResponse(bentoml.IODescriptor):
    embedding: list[float]

@bentoml.service(resources={"cpu": "1"})
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @bentoml.api(input_spec=EmbedRequest, output_spec=EmbedResponse)
    def embed(self, body: EmbedRequest) -> EmbedResponse:
        embedding = self.model.encode([body.text])[0].tolist()
        return EmbedResponse(embedding=embedding)
