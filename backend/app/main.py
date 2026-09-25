import os

import psycopg
from fastapi import FastAPI
from qdrant_client import QdrantClient

from app.ws import router as ws_router

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@postgres:5432/app")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

# root_path="/api" faz o Swagger/OpenAPI funcionarem por trás do nginx (prefixo /api).
app = FastAPI(title="AI Assistant API", root_path="/api")


@app.get("/")
def root():
    return {"service": "ai-assistant-backend", "status": "ok"}


app.include_router(ws_router)


@app.get("/health")
def health():
    """Verifica a conectividade com Postgres e Qdrant."""
    status = {"api": "ok", "postgres": "unknown", "qdrant": "unknown"}

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        status["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001
        status["postgres"] = f"error: {exc}"

    try:
        client = QdrantClient(url=QDRANT_URL, timeout=3)
        client.get_collections()
        status["qdrant"] = "ok"
    except Exception as exc:  # noqa: BLE001
        status["qdrant"] = f"error: {exc}"

    return status
