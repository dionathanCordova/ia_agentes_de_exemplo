import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agentes.operador_conta.agent import root_agent as operador_conta_agente
from google.adk.apps import App
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "agentes" / "operador_conta" / ".env")
app = FastAPI(title="Api para consumo de agentes")

adk_app = App(
    root_agent = operador_conta_agente,
    name = operador_conta_agente.name
)

session_service = InMemorySessionService()

runner = Runner(
    app=adk_app, 
    session_service=session_service
)

class MessageRequest(BaseModel):
    message: str
    sessao_id: str | None = None

AGENTE_TIMEOUT_SEGUNDOS = 30

async def _executar_agente(sessao_id: str, conteudo: types.Content) -> str | None:
    resposta = None

    async for event in runner.run_async(
        user_id="user-1",
        session_id=sessao_id,
        new_message=conteudo
    ):
        if event.is_final_response() and event.content and event.content.parts:
            resposta = event.content.parts[0].text

    return resposta

@app.post("/messages")
async def receive_messages(request: MessageRequest):
    sessao = await session_service.create_session(
        app_name=adk_app.name,
        user_id="user-1"
    ) if not request.sessao_id else \
        await session_service.get_session(
            session_id=request.sessao_id,
            app_name=adk_app.name,
            user_id="user-1"
        )

    if not sessao:
        raise ValueError("Sessão inexistente")

    conteudo = types.Content(
        role="user",
        parts=[types.Part.from_text(text=request.message)]
    )

    try:
        resposta = await asyncio.wait_for(
            _executar_agente(sessao.id, conteudo),
            timeout=AGENTE_TIMEOUT_SEGUNDOS
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Tempo limite excedido ao consultar o agente")

    return {"resposta": resposta, "sessao_id": sessao.id}