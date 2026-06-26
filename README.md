# IA_PROJETO — Agentes com Google ADK

Projeto de agentes de IA construídos com o **Google ADK (Agent Development Kit)**, gerenciado com **uv**, e expostos via API com **FastAPI/uvicorn**.

---

## Pré-requisitos

- Python **3.12+** (versão pinada em `.python-version`)
- [uv](https://docs.astral.sh/uv/) — gerenciador de pacotes e ambientes
- Conta/API key do Google AI Studio (ou projeto no Vertex AI) para uso dos modelos Gemini

### Instalando o uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version   # confirma instalação
```

---

## Instalação do projeto

```bash
git clone <repo-url>
cd IA_PROJETO

# uv cria e gerencia o .venv automaticamente
uv sync
```

Comandos úteis do uv:

```bash
uv add <pacote> |  uv add -r ./agentes/sql_reader/requirements.txt # adiciona dependência (ex: uv add pandas)
uv remove <pacote>     # remove dependência
uv run <script.py>     # executa script dentro do venv do projeto
```

---

## Estrutura do projeto

```
IA_PROJETO/
├── agentes/
│   ├── operador_conta/
│   │   ├── __init__.py      # from . import agent
│   │   ├── agent.py         # define root_agent (Agent do ADK)
│   │   └── .env             # credenciais/config do Gemini para este agente
│   ├── agenteCoder/
│   └── data_engineer/
├── api/
│   └── api.py                # FastAPI que expõe os agentes via HTTP
├── main.py
└── pyproject.toml
```

**Convenção:** cada agente vive em sua própria pasta dentro de `agentes/`, com `__init__.py`, `agent.py` e `.env` próprios. Isso permite múltiplos agentes isolados no mesmo repo, cada um com seu modelo/config.

---

## Variáveis de ambiente

Cada agente tem seu próprio `.env` (ex: `agentes/operador_conta/.env`). Nunca commitar — já cobertos pelo `.gitignore`.

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | ✅ (se não usar Vertex) | Chave da API do Google AI Studio |
| `GOOGLE_GENAI_USE_VERTEXAI` | ❌ | `TRUE`/`FALSE` — usa Vertex AI em vez da API key direta |

---

## Criando um novo agente

1. Criar a pasta do agente:
   ```bash
   mkdir -p agentes/meu_agente
   touch agentes/meu_agente/__init__.py agentes/meu_agente/.env
   ```
   (ou usar `adk create <nome_agente>` para gerar o scaffold automaticamente)
   (ou mais completo `adk create agentes/meu_agente --model gemini-2.5-flash --api_key $GOOGLE_API_KEY`)

2. `__init__.py` deve importar o módulo do agente:
   ```python
   from . import agent
   ```

3. `agent.py` define o `root_agent`:
   ```python
   from google.adk.agents import Agent
   from google.adk.tools.function_tool import FunctionTool

   def minha_ferramenta(parametro: str) -> dict:
       """Docstring é usada pelo modelo para entender quando chamar a tool."""
       return {"status": "ok"}

   root_agent = Agent(
       model="gemini-2.5-flash",
       name="root_agent",
       description="Descrição curta do papel do agente",
       instruction="""
           Instruções de sistema do agente, em texto livre.
       """,
       tools=[
           minha_ferramenta,
           FunctionTool(minha_ferramenta, require_confirmation=True),  # exige confirmação do usuário antes de executar
       ],
   )
   ```

4. Preencher o `.env` do agente com `GOOGLE_API_KEY` (ou config Vertex).

**Notas sobre tools:**
- Funções Python simples (com type hints e docstring) já funcionam como tool.
- `FunctionTool(..., require_confirmation=True)` força o ADK a pedir confirmação do usuário antes de executar (útil para ações destrutivas/sensíveis, ex: cancelar assinatura). Dentro da função, cheque `tool_context.tool_confirmation` para saber se já foi confirmado.

---

## Rodando o agente

### Via CLI interativo do ADK

```bash
adk run agentes/<nome_agente>
```

### Via interface web do ADK

```bash
adk web ./agentes --reload_agents
```

Abre um browser para conversar com qualquer agente da pasta `agentes/`.

---

## Rodando via API (FastAPI)

A pasta `api/` expõe os agentes via endpoint HTTP (`api/api.py`, instância `app`).

```bash
uv run uvicorn api.api:app --reload --port 8001 --host 0.0.0.0
```

Sem `--host` (default `127.0.0.1`, só acessível de dentro do WSL):
```bash
uv run uvicorn api.api:app --reload --port 8001
```

> **`--host 0.0.0.0` é necessário no WSL2** — sem isso o servidor só escuta no loopback da VM do WSL e fica inacessível do Windows host (Postman/Bruno/curl no Windows). Com `0.0.0.0`, acessível tanto por `127.0.0.1` (de dentro do WSL) quanto pelo IP da VM (`ip addr show eth0`, ex: `172.30.x.x`) do lado Windows. Esse IP pode mudar a cada reboot do WSL.

### Testando o endpoint

```bash
curl -X POST http://127.0.0.1:8001/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "ola"}'
```

> No PowerShell, `curl` é alias de `Invoke-WebRequest` e **não aceita `-d`**. Use `curl.exe` (binário real) ou `Invoke-RestMethod`:
> ```powershell
> Invoke-RestMethod -Uri http://127.0.0.1:8001/messages -Method Post -Body '{"message":"ola"}' -ContentType "application/json"
> ```

Resposta esperada:
```json
{"resposta": "...", "sessao_id": "..."}
```
