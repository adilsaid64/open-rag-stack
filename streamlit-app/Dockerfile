FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY . /app

RUN uv sync --verbose

EXPOSE 8501

CMD ["uv" ,"run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
