import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.agent import checkpointer, get_agent

router = APIRouter()

TOOL_RESULT_MAX_CHARS = 1000
IDLE_TIMEOUT_SECONDS = 60


def _text(content) -> str:
    """Extrai texto de `content`, que pode ser str ou lista de blocos (ex.: Anthropic)."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
        if not isinstance(block, dict) or block.get("type") == "text"
    )


def _parse_message(raw: str) -> str:
    """Aceita JSON {"message": "..."} ou texto puro."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    if isinstance(data, dict):
        return str(data.get("message", "")).strip()
    return raw.strip()


async def _run_turn(websocket: WebSocket, thread_id: str, text: str) -> None:
    """Executa uma rodada do agente, enviando os eventos ao cliente conforme chegam."""
    config = {"configurable": {"thread_id": thread_id}}
    stream = get_agent().astream(
        {"messages": [{"role": "user", "content": text}]},
        config,
        stream_mode=["messages", "updates"],
    )

    async for mode, data in stream:
        if mode == "messages":
            chunk, metadata = data
            # AIMessageChunk (streaming) ou AIMessage inteira (providers sem streaming).
            if metadata.get("langgraph_node") == "model" and isinstance(chunk, AIMessage):
                if token := _text(chunk.content):
                    await websocket.send_json({"type": "token", "content": token})
            continue

        # mode == "updates": mensagens completas de cada nó (modelo/tools).
        for update in data.values():
            if not isinstance(update, dict):
                continue
            for message in update.get("messages", []):
                if isinstance(message, AIMessage):
                    for call in message.tool_calls:
                        await websocket.send_json(
                            {"type": "tool_call", "name": call["name"], "args": call["args"]}
                        )
                elif isinstance(message, ToolMessage):
                    await websocket.send_json(
                        {
                            "type": "tool_result",
                            "name": message.name,
                            "content": _text(message.content)[:TOOL_RESULT_MAX_CHARS],
                        }
                    )

    await websocket.send_json({"type": "done"})


@router.websocket("/ws")
async def chat(websocket: WebSocket):
    """Chat com o agente.

    Cliente → servidor: JSON {"message": "..."} (ou texto puro).
    Servidor → cliente: eventos JSON, um por linha do stream:
      {"type": "token", "content": "..."}         pedaço da resposta
      {"type": "tool_call", "name", "args"}       o agente decidiu chamar uma tool
      {"type": "tool_result", "name", "content"}  resultado da tool (truncado)
      {"type": "done"}                            fim da resposta
      {"type": "error", "message": "..."}         falha na rodada (a conexão continua aberta)

    Sem mensagem do cliente por IDLE_TIMEOUT_SECONDS (fora de uma rodada do agente),
    o servidor fecha a conexão com código 1000.
    """
    await websocket.accept()
    thread_id = str(uuid.uuid4())  # uma conversa por conexão

    try:
        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), IDLE_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                await websocket.close(code=1000, reason="inatividade")
                return
            text = _parse_message(raw)
            if not text:
                continue
            try:
                await _run_turn(websocket, thread_id, text)
            except WebSocketDisconnect:
                raise
            except Exception as exc:  # noqa: BLE001
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
    finally:
        checkpointer.delete_thread(thread_id)
