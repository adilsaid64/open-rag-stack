FROM ghcr.io/astral-sh/uv:debian-slim

RUN apt-get update && apt-get install -y git && apt-get clean

WORKDIR /app

COPY . /app

RUN uv sync --verbose

RUN bentoml build

EXPOSE 3001

CMD ["uv" ,"run", "bentoml", "serve", "service:latest", "--port", "3001"]
