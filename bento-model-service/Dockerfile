FROM ghcr.io/astral-sh/uv:debian-slim

RUN apt-get update && apt-get install -y git && apt-get clean

WORKDIR /app

COPY . /app

RUN uv sync --verbose

RUN uv run bentoml build

EXPOSE 3000

CMD ["uv" ,"run", "bentoml", "serve", "generation_service:latest", "--port", "3000"]
