from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

FATURAS = [
    {
        "id": "fatura_001",
        "cliente_id": "cliente_123",
        "valor": 49.99,
        "data_emissao": "2026-01-01",
        "status": "paga",
    },
    {
        "id": "fatura_002",
        "cliente_id": "cliente_123",
        "valor": 149.99,
        "data_emissao": "2026-02-02",
        "status": "pendente",
    },
]

ASSINATURAS: dict[str, dict] = {
    "cliente_123": {"plano": "Pro", "status": "ativa", "renovacao": "2026-07-01"}
}

def listar_faturas(cliente_id: str) -> dict:
    faturas =  [fatura for fatura in FATURAS if fatura["cliente_id"] == cliente_id]

    if len(faturas) == 0:
        return {"status": "ok", "message": "Nenhuma fatura localizada para o id recebido"}

    return faturas


def cancelar_assinatura(cliente_id: str, tool_context: ToolContext, senha: str) -> dict:
    """
        Cancela a assinatura de um cliente com base no ID do cliente.
        Args:
            cliente_id (str): O id do cliente para o qual a assinatura deve ser cancelada.
        Returns:
            dict: Um dicionário contendo o status da operação e uma mensagem.
    """
    SENHA_SECRETA = "1234"

    if tool_context.tool_confirmation is None:
        tool_context.request_confirmation(
            hint="Você deseja realmente cancelar sua assinatura?",
            payload={"cliente_id": cliente_id, "senha": ""}
        )

        return {"status": "pending", "message": "Aguardando confirmacao do user"}
    

    if tool_context.tool_confirmation.confirmed is False:
        return {"status": "error", "message": "Cancelamento abordado pelo user"}

    if senha != SENHA_SECRETA:
        return {"status": "error", "message": "Senha incorreta"}

    assinatura = ASSINATURAS.get(cliente_id)
    if assinatura is not None:
        assinatura["status"] = "cancelada"
        return {"status": "ok", "message": "Assinatura cancelada com sucesso"}

    return {"status": "error", "message": "Assinatura não pode ser cancelada"}

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Agente raiz para o operador de conta",
    instruction="""
        Você e um agente especializado em operador de conta.
        Você é reponsável por:
        - Informar ao cliente sobre sua assinatura: o plano, status e renovação.
        - Tirar dúvidas sobre as faturas do cliente.
        - Cancelar a assinatura do cliente, se solicitado.
        O usuário precisa fornecer o id de cliente para que você possa buscar as informações corretas.
    """,
    tools=[
        listar_faturas,
        FunctionTool(cancelar_assinatura, require_confirmation=True)
    ],
)
