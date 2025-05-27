FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY app/ /app

RUN uv sync --verbose

EXPOSE 8000

CMD ["uv", "run", "app.py"]
