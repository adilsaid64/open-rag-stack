## What is this?

A **production-oriented** playground for building and serving **Retrieval-Augmented Generation0 (RAG)** systems.

## Why?

Designed to explore and apply best practices in **MLOps** and **LLMOps**, focusing on modular, observable, and scalable RAG system deployment.

## What's Included?


![rag-system](assets/rag-system.drawio.png)

- **FastAPI** orchestrator with `/ingest` and `/query` endpoints
- **BentoML** services for embeddings and generation
- **Qdrant** as the vector database for retrieval
- **MLflow** for experiment tracking
- **Prometheus** for monitoring core RAG metrics and model endpoints
- **Grafana** for visualising scraped metrics
- **Streamlit** app to interact with the system
- **MongoDB** for tracking user interaction and model outputs for model evaluation

## Evaluation

User queries and model responses are stored together in MongoDB. This includes the question the user asked, the documents retrieved, and the models response.

This data enables offline performance evaluation using tools like Ragas, helping assess the quality and relevance of responses based on retrieval fidelity, factual grounding, and answer coherence.

Key evaluation criteria include:
- Retrieval Precision – Are the retrieved documents relevant to the query?
- Groundedness – Is the model’s answer supported by retrieved content?
- Factual Consistency – Does the response reflect the source documents accurately?
- Completeness – Does the answer fully address the original question?

Evaluation runs are registered inside MLflow, allowing you to:

- Track evaluation metrics over time
- Compare performance across different model versions or retrieval strategies

## Observability

This system includes end-to-end observability using Prometheus for metrics collection and Grafana for visualisation.

**Key Metrics tracked:**
- Ingestion latency
- Query processing time
- Model response health
- Vector search performance
- User interaction events

 **Example Dashboard**
<p float="left">
  <img src="assets/grafana-1.png" width="45%" />
  <img src="assets/grafana-2.png" width="45%" />
</p>

The dashboard offers visibility into system performance and model behavior during both ingestion and query stages.

It can also be extended to include the metrics provided from the BentoML endpoints.

## Goals

- Apply real-world deployment principles to RAG
- Track and monitor performance with Prometheus
- Structure services for modularity and scaling
