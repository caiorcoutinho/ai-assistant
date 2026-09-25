from functools import lru_cache

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.llm import get_llm
from app.agent.tools import TOOLS

SYSTEM_PROMPT = "Você é um assistente prestativo."

# Memória da conversa por thread_id (em processo: some ao reiniciar o backend).
checkpointer = InMemorySaver()


def build_agent(checkpointer=None):
    """Cria o agente (grafo LangGraph). Uso: agent.invoke({"messages": [("user", "oi")]})."""
    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


@lru_cache(maxsize=1)
def get_agent():
    """Agente compartilhado; o histórico de cada conversa é isolado por thread_id."""
    return build_agent(checkpointer=checkpointer)
