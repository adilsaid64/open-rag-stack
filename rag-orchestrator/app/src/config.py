import os

from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
BENTOML_MODEL_URL = os.getenv("BENTOML_MODEL_URL", "http://localhost:3000")
BENTOML_EMBEDDING_URL = os.getenv("BENTOML_EMBEDDING_URL", "http://localhost:3001")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag-docs")
