FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY . /app

RUN uv sync --verbose

EXPOSE 5000

CMD ["uv" ,"run", "mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "mysql+pymysql://mlflow:mlflow@mysql:3306/mlflow", "--default-artifact-root", "s3://mlflow/"]
