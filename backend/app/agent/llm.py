from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.agent.config import LLM_MODEL, LLM_TEMPERATURE


def get_llm() -> BaseChatModel:
    """Chat model agnóstico de provider, escolhido por LLM_MODEL ("provider:model")."""
    if not LLM_MODEL:
        raise RuntimeError('LLM_MODEL não definido (ex.: "groq:llama-3.3-70b-versatile").')
    return init_chat_model(LLM_MODEL, temperature=LLM_TEMPERATURE)
