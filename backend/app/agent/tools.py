from functools import lru_cache

from langchain_core.tools import tool
from qdrant_client import QdrantClient

from app.agent.config import QDRANT_COLLECTION, QDRANT_TEXT_FIELD, QDRANT_URL
from app.agent.embeddings import get_embeddings


@lru_cache(maxsize=1)
def _qdrant() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL, timeout=10)


@tool
def echo(text: str) -> str:
    """Devolve o texto recebido. Placeholder: substitua pelas tools reais do agente."""
    return text


@tool
def buscar_documentos(query: str, limit: int = 4) -> str:
    """Busca na base de conhecimento (Qdrant) os trechos mais relevantes para a consulta.

    Use quando a pergunta depender de informações dos documentos do usuário.
    `query` deve ser uma frase de busca autocontida; `limit` é o nº de trechos (1 a 10).
    """
    limit = max(1, min(limit, 10))
    client = _qdrant()

    if not client.collection_exists(QDRANT_COLLECTION):
        return f"A coleção '{QDRANT_COLLECTION}' ainda não existe no Qdrant."

    vector = get_embeddings().embed_query(query)
    hits = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=limit,
        with_payload=True,
    ).points

    if not hits:
        return "Nenhum trecho relevante encontrado."

    trechos = []
    for i, hit in enumerate(hits, start=1):
        payload = hit.payload or {}
        texto = payload.get(QDRANT_TEXT_FIELD, "")
        fonte = payload.get("source", "desconhecida")
        trechos.append(f"[{i}] (fonte: {fonte}, score: {hit.score:.2f})\n{texto}")
    return "\n\n".join(trechos)


TOOLS = [echo, buscar_documentos]
