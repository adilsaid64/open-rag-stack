## What is this?

A **production-oriented** playground for building and serving **Retrieval-Augmented Generation (RAG)** systems.

See article here: [Medium](https://medium.com/@adilsaid64/rag-in-practice-exploring-versioning-observability-and-evaluation-in-production-systems-85dc28e1d9a8)

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
- **LakeFS** for versioning ingested documents and storing commit hashes alongside embeddings to ensure traceability between source data and vectors

## Data Versioning

To ensure traceability and reproducibility, all ingested documents are versioned using LakeFS. When a document is ingested, it is committed to a LakeFS repository, and the resulting commit hash is saved alongside the document's embeddings in Qdrant.

This means every embedding can be traced back to the exact version of the document it was generated from. If documents are updated, a new commit is created — allowing you to track changes over time and maintain alignment between the vector store and source data.

## Evaluation

User queries and model responses are stored together in MongoDB. This includes the question the user asked, the documents retrieved, and the models response.

This data enables offline performance evaluation using tools like Ragas, helping assess the quality and relevance of responses based on retrieval fidelity, factual grounding, and answer coherence.

Key evaluation criteria include:
- **Retrieval Precision** – Are the retrieved documents relevant to the query?
- **Groundedness** – Is the model’s answer supported by retrieved content?
- **Factual Consistency** – Does the response reflect the source documents accurately?
- **Completeness** – Does the answer fully address the original question?

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

## Getting Started

All components are containerised with Docker and orchestrated using Docker Compose.

Run

```bash
docker-compose up --build
```

The BentoML services can take some time to spin up.

We need to setup LakeFS as an artifact store for our documents.

1. **Access the LakeFS UI**
   Visit [http://localhost:8001/](http://localhost:8001/) in your browser.

2. **Create a an Account and Store Credentials**

   ![LakeFS Credentials](assets/lakefs-setup-1.png)

   Make sure not to lose these credentials. Store them in the `.env ` of the `rag-orchestrator`

   ```
   LAKEFS_USERNAME=<your-access-key>
   LAKEFS_PASSWORD=<your-secret-key>
   ```

3. **Create a LakeFS Repo**

   Inside the LakeFS UI, create a repo to store our documents in:

   ![LakeFS Repo](assets/lakefs-setup-2.png)


## Accessing the Interfaces

Once the services are running, you can interact with the system through the following UIs:

| Service           | URL                                            | Description                                    |
| ----------------- | ---------------------------------------------- | ---------------------------------------------- |
| **Streamlit App** | [http://localhost:8501](http://localhost:8501) | Main UI to interact with the RAG system        |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | Manage artifact storage                        |
| **Grafana**       | [http://localhost:4000](http://localhost:4000) | Visualise metrics and dashboards               |
| **Prometheus**    | [http://localhost:9090](http://localhost:9090) | View raw metrics from services                 |
| **Mongo Express** | [http://localhost:8081](http://localhost:8081) | Inspect stored user interactions and outputs   |
| **MLflow UI**     | [http://localhost:5000](http://localhost:5000) | Track experiments, artifacts, and metrics      |
| **LakeFS UI**     | [http://localhost:8001](http://localhost:8001) | Manage versioned data and artifacts            |


## What I Would Change

Right now, the system follows a synchronous orchestration pattern using FastAPI and HTTP between services. 
I would at some point like to explore an event-driven design by introducing a message broker and having services publish/consume events asynchronously (maybe that would be the next project).

This system is orchestrated with Docker Compose for simplicity. However, in a real production environment, I would probably deploy it to a Kubernetes cluster. And because this was just a side project to explore RAG architecture and MLOps/LLMOps principles regarding RAG, I didn't want to deal with Kubernetes. But as everything is containerised, deploying this to a Kubernetes cluster shouldn’t be too much work.

I would also add better authentication and security with how access keys and passwords are defined. Ideally, these would be stored and retrieved from a secret manager somewhere.

Regarding MLOps/LLMOps, the current implementation doesn’t track model versioning. The models are defined within the BentoML services. Ideally, these models should be registered in MLflow’s model registry, and then BentoML uses MLflow’s model registry to build the model servers.
