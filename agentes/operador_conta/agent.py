from google.adk.agents import Agent

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

def listar_faturas(cliente_id: str):
    faturas =  [fatura for fatura in FATURAS if fatura["cliente_id"] == cliente_id]

    if len(faturas) == 0:
        return "Nenhuma fatura localizada para o id recebido"

    return faturas

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
    tools=[listar_faturas],
)
