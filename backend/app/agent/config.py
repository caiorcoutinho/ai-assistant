import os

# Modelos no formato "provider:model" (ex.: "groq:llama-3.3-70b-versatile").
# Trocar de provider = mudar a variável + instalar o pacote langchain-<provider>
# + definir a chave do provider (ex.: GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY).
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "")

# Qdrant (busca vetorial)
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
# Campo do payload que guarda o texto do documento.
QDRANT_TEXT_FIELD = os.getenv("QDRANT_TEXT_FIELD", "text")
