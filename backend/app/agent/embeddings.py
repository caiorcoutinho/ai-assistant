from langchain.embeddings import init_embeddings
from langchain_core.embeddings import Embeddings

from app.agent.config import EMBEDDING_MODEL


def _nvidia(model: str) -> Embeddings:
    from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

    return NVIDIAEmbeddings(model=model)


# Providers que o init_embeddings do LangChain não cobre. Para adicionar um, basta registrar aqui.
_CUSTOM_PROVIDERS = {"nvidia": _nvidia}


def get_embeddings() -> Embeddings:
    """Embeddings agnósticos de provider, escolhidos por EMBEDDING_MODEL ("provider:model")."""
    if not EMBEDDING_MODEL:
        raise RuntimeError('EMBEDDING_MODEL não definido (ex.: "nvidia:nvidia/nv-embed-v1").')

    provider, _, model = EMBEDDING_MODEL.partition(":")
    if provider in _CUSTOM_PROVIDERS:
        return _CUSTOM_PROVIDERS[provider](model)
    return init_embeddings(EMBEDDING_MODEL)
