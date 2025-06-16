import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, Summary, generate_latest
from src.lakefs_store import LakeFSLogger
from src.mongo_logger import MongoLogger
from src.rag import RAGPipeline
from src.schema import IngestRequest, IngestResponse, QueryRequest, QueryResponse
from src.utils import logger

app = FastAPI(title="RAG API", description="Retrieval-Augmented Generation API")
rag = RAGPipeline()
mongo_logger = MongoLogger()

lakefs_logger = LakeFSLogger(
    lakefs_endpoint=os.getenv("LAKEFS_ENDPOINT", "http://localhost:8000"),
    lakefs_username=os.getenv("LAKEFS_USERNAME", "LAKEFS_USERNAME"),
    lakefs_password=os.getenv("LAKEFS_PASSWORD", "LAKEFS_PASSWORD"),
    lakefs_repo=os.getenv("LAKEFS_REPO", "documents"),
)

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

CONTEXTS_RETRIEVED = Summary(
    "rag_contexts_retrieved_count", "Number of contexts retrieved per query"
)

RETRIEVAL_SCORE = Histogram(
    "rag_retrieval_score",
    "Score of retrieved contexts",
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
)

GENERATION_MODEL = "EleutherAI/gpt-neo-1.3B"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


@app.post("/ingest/")
def ingest(request: IngestRequest) -> IngestResponse:
    """Ingest a text passage into the RAG system and store it in LakeFS"""
    INGEST_COUNT.inc()

    try:
        commit_hash = lakefs_logger.store_text(request.text)

        metadata = request.metadata or {}
        metadata["lakefs_commit"] = commit_hash

        with INGEST_LATENCY.time():
            rag.split_and_ingest(
                text=request.text,
                source=metadata.get("title", "unknown"),
                metadata=metadata,
            )
        logger.info(
            f"Text passage ingested with commit hash {commit_hash}: {request.text[:30]}..."
        )
        return IngestResponse(status="ok", metadata={"lakefs_commit": commit_hash})
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

    CONTEXTS_RETRIEVED.observe(len(contexts))

    for hit in contexts:
        RETRIEVAL_SCORE.observe(hit["score"])

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
