import time
from typing import Optional

from fastapi import FastAPI, Body
from pydantic import BaseModel
import mlflow
import uvicorn

from src.rag import RAGPipeline
from src.utils import logger
from src.config import MLFLOW_TRACKING_URI, EMBEDDING_MODEL

app = FastAPI(title="RAG API", description="Retrieval-Augmented Generation API")
rag = RAGPipeline()

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

GENERATION_MODEL = "distilgpt2"  

class IngestRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

@app.post("/ingest/")
def ingest(request: IngestRequest):
    rag.ingest(request.text, request.metadata)
    logger.info(f"Document ingested: {request.text[:30]}...")
    return {"status": "ok"}

@app.post("/query/")
def query(request: QueryRequest):
    with mlflow.start_run(run_name="rag_query"):
        mlflow.log_param("question", request.question)
        mlflow.log_param("top_k", request.top_k)
        mlflow.log_param("embedding_model", EMBEDDING_MODEL)
        mlflow.log_param("generation_model", GENERATION_MODEL)

        retrieval_start = time.time()
        contexts = rag.retrieve(request.question, top_k=request.top_k)
        retrieval_time = time.time() - retrieval_start
        context = "\n".join(contexts)
        mlflow.log_text(context, "context.txt")
        mlflow.log_metric("retrieval_time", retrieval_time)

        generation_start = time.time()
        answer = rag.generate(request.question, context)
        generation_time = time.time() - generation_start
        mlflow.log_metric("generation_time", generation_time)
        mlflow.log_text(answer, "answer.txt")
    logger.info(f"Query answered: {request.question[:30]}...")
    return {"answer": answer} 


if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0", port=8888, log_level="info")