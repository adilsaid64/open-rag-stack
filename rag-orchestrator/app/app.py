from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel
from src.mongo_logger import MongoLogger
from src.rag import RAGPipeline
from src.utils import logger

app = FastAPI(title="RAG API", description="Retrieval-Augmented Generation API")
rag = RAGPipeline()
mongo_logger = MongoLogger()

QUERY_COUNT = Counter("rag_query_count", "Total number of /query calls")
INGEST_COUNT = Counter("rag_ingest_count", "Total number of /ingest calls")

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds", "Time to retrieve context"
)
GENERATION_LATENCY = Histogram(
    "rag_generation_latency_seconds", "Time to generate response"
)
INGEST_LATENCY = Histogram("rag_ingest_latency_seconds", "Time to ingest documents")

RETRIEVAL_EMPTY_COUNT = Counter(
    "rag_retrieval_empty_count", "Retrieval returned no results"
)
GENERATION_FAILURES = Counter(
    "rag_generation_failures_total", "Total generation failures"
)

INGEST_FAILURES = Counter("rag_ingest_failures_total", "Total ingestion failures")

PROMPT_TOKENS = Counter("rag_tokens_prompt_total", "Tokens sent to LLM")
COMPLETION_TOKENS = Counter("rag_tokens_completion_total", "Tokens received from LLM")

GENERATION_MODEL = "EleutherAI/gpt-neo-1.3B"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


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


@app.post("/ingest/")
def ingest(request: IngestRequest) -> IngestResponse:
    """..."""
    INGEST_COUNT.inc()
    try:
        with INGEST_LATENCY.time():
            rag.split_and_ingest(
                text=request.text,
                source=(
                    request.metadata.get("title", "unknown")
                    if request.metadata
                    else "unknown"
                ),
                metadata=request.metadata,
            )
        logger.info(f"Document ingested: {request.text[:30]}...")
        return IngestResponse(status="ok")
    except Exception as e:
        logger.error(f"Ingestion Failed {e}")
        INGEST_FAILURES.inc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/query/")
def query(request: QueryRequest) -> QueryResponse:
    """..."""
    QUERY_COUNT.inc()

    with RETRIEVAL_LATENCY.time():
        contexts = rag.retrieve(request.question, top_k=request.top_k)

    if not contexts:
        RETRIEVAL_EMPTY_COUNT.inc()

    context_text = "\n".join([hit["text"] for hit in contexts])

    try:
        with GENERATION_LATENCY.time():
            answer = rag.generate(request.question, context_text)

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        GENERATION_FAILURES.inc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    logger.info(f"Query answered: {request.question[:30]}...")

    mongo_logger.log_request(
        request=request,
        contexts=contexts,
        answer=answer,
    )

    return QueryResponse(
        answer=answer,
    )


@app.get("/metrics")
def metrics():
    """..."""
    return Response(generate_latest(), media_type="text/plain")
