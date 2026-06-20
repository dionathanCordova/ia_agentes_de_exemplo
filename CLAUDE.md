# CLAUDE.md — FinAgent

> Este arquivo é o **contexto central do projeto para o Claude Code**. Ele deve ser lido e respeitado em todas as interações de desenvolvimento. Atualize-o a cada fase concluída.

---

## 🧭 O que é o FinAgent?

O **FinAgent** é um agente de IA especializado em suporte à decisão financeira, construído incrementalmente ao longo de um roadmap de 8 fases. Não é um projeto isolado — é um sistema vivo que cresce a cada fase, acumulando capacidades reais de produção.

**Fase atual:** `Fase 1 — CLI Foundation`

**Stack principal:** Python 3.11+ · Anthropic SDK · Pydantic Settings · Langfuse · Rich (CLI)

> ⚠️ **Escopo:** este roadmap cobre apenas o código sob `finagent/` (Anthropic SDK puro). Qualquer outro agente no repo (ex.: `src/operador_conta`, baseado em `google-adk`) é experimento paralelo e **não conta como progresso de fase** — frameworks como ADK já resolvem na própria lib o que o roadmap pede pra construir na mão (sessão, retry, tools, MCP, multi-agente), então usá-los não exercita o aprendizado que cada fase pretende.

---

## 🗺️ Visão do Projeto por Fase

| Fase | Capacidade adicionada | Status |
|------|----------------------|--------|
| **1** | CLI multi-turn, token tracking, logging, Langfuse, retry, streaming | 🔄 Em andamento |
| **2** | Tools, function calling, prompt versionado com Langfuse | ⏳ Pendente |
| **3** | RAG sobre documentos financeiros reais, memória semântica | ⏳ Pendente |
| **3.5** | Mapeamento dos 6 Pilares: memory, tools, MCP, commands, subagents, artifacts | ⏳ Pendente |
| **4** | Reescrita como agente LangGraph com ReAct loop e Plan-and-Execute | ⏳ Pendente |
| **4.5** | Workflow SDD: CLAUDE.md → spec → plano → implementação | ⏳ Pendente |
| **5** | Servidor MCP próprio expondo pipelines de dados da empresa | ⏳ Pendente |
| **6** | Sistema multi-agente: supervisor + workers em Git Worktrees paralelos | ⏳ Pendente |
| **7** | Deploy em cloud com autoscaling, monitoramento e Text-to-SQL financeiro | ⏳ Pendente |
| **8** | Guardrails, audit trail, avaliação LLM-as-Judge e testes de segurança | ⏳ Pendente |

---

## 📁 Estrutura do Projeto (Fase 1)

```
finagent/
├── .env                    # API keys — NUNCA commitar
├── .env.example            # Template documentado de todas as variáveis
├── CLAUDE.md               # Este arquivo — contexto do projeto para Claude Code
├── pyproject.toml          # Dependências e metadados do projeto
├── README.md               # Guia de instalação e uso
├── finagent/
│   ├── __init__.py
│   ├── config.py           # pydantic-settings: carrega .env com validação de tipos
│   ├── client.py           # Wrapper do Anthropic client com retry automático
│   ├── session.py          # Gerenciamento de histórico multi-turn
│   ├── streaming.py        # Handler de streaming com coleta de métricas
│   ├── logger.py           # Logging estruturado em JSON → responses.jsonl
│   ├── observability.py    # Integração Langfuse (traces, spans, custo)
│   └── cli.py              # Entry point da CLI (comandos, loop principal)
└── tests/
    └── test_session.py     # Testes unitários do gerenciamento de histórico
```

**Regra:** Cada módulo tem **uma responsabilidade clara**. Não misture lógica de negócio com I/O, e não coloque lógica de sessão dentro do cliente HTTP.

---

## ⚙️ Como Rodar

### Pré-requisitos

- Python 3.11+
- Uma API key da Anthropic
- (Opcional) Conta no Langfuse para observabilidade

### Instalação

```bash
# Clone e entre no diretório
git clone <repo-url>
cd finagent

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -e ".[dev]"

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves
```

### Rodando a CLI

```bash
python -m finagent.cli
```

### Rodando os testes

```bash
pytest tests/ -v
```

---

## 🔐 Variáveis de Ambiente

Todas as variáveis são carregadas via `pydantic-settings` no `config.py`. O `.env` **nunca deve ser commitado**.

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `ANTHROPIC_API_KEY` | ✅ | Chave da API Anthropic |
| `LANGFUSE_PUBLIC_KEY` | ⚠️ Opcional | Chave pública do Langfuse |
| `LANGFUSE_SECRET_KEY` | ⚠️ Opcional | Chave secreta do Langfuse |
| `LANGFUSE_HOST` | ⚠️ Opcional | Host do Langfuse (padrão: cloud) |
| `DEFAULT_MODEL` | ❌ | Modelo padrão (default: `claude-haiku-4-5`) |
| `LOG_FILE_PATH` | ❌ | Caminho do log (default: `responses.jsonl`) |

---

## 💬 Comandos da CLI

| Comando | Descrição |
|---------|-----------|
| `/help` | Lista todos os comandos disponíveis |
| `/clear` | Limpa o histórico da conversa atual (sem encerrar) |
| `/history` | Exibe a conversa atual formatada |
| `/cost` | Exibe o custo total acumulado da sessão |
| `/model haiku` | Troca para `claude-haiku-4-5` em runtime |
| `/model sonnet` | Troca para `claude-sonnet-4-5` em runtime |
| `/exit` ou `/quit` | Encerra o programa |

---

## 🧠 System Prompt Base (Fase 1)

```
Você é o FinAgent, um assistente especializado em análise financeira.
Seu papel é auxiliar analistas e desenvolvedores do setor financeiro
a interpretar dados, identificar padrões e apoiar decisões baseadas em evidências.

Diretrizes:
- Sempre peça contexto antes de dar uma análise definitiva
- Sinalize quando uma resposta exigir validação com dados reais
- Nunca dê recomendações de investimento — apenas análise de dados
- Quando incerto, diga explicitamente o grau de confiança
```

> **Nota:** Este prompt vai evoluir a cada fase. Sempre versionado via Langfuse a partir da Fase 2.

---

## 🏗️ Decisões de Arquitetura

### Multi-turn: o modelo não guarda estado
O histórico de conversa é uma lista de dicts `{role, content}` que você monta localmente e envia **completa** a cada chamada. O modelo em si é stateless — a ilusão de memória vem do histórico que você injeta.

```python
# ✅ Correto
messages = session.get_history()  # lista completa
response = client.send(messages)

# ❌ Errado — não existe "continuar" uma conversa no modelo
response = client.continue_conversation(last_response)
```

### Retry: nem todo erro é igual
- **429 / 5xx** → retry com backoff exponencial: `wait = 2^attempt + random(0, 1)`, máximo 3 tentativas
- **400 (Bad Request)** → falha imediata, sem retry. Logar e exibir mensagem clara ao usuário
- **401 (Unauthorized)** → falha imediata. Provável problema com API key

### Streaming: métricas chegam no final
Durante o stream, exiba os tokens em tempo real. O bloco `usage` (input_tokens, output_tokens) só está disponível **após** o stream finalizar. Colete métricas no evento de finalização, não durante.

### Custo estimado (Fase 1)
Calcule localmente com base nos tokens retornados pelo `usage` block:

```python
# Preços aproximados (verificar sempre na docs oficial)
COST_PER_1K = {
    "claude-haiku-4-5":   {"input": 0.00025, "output": 0.00125},
    "claude-sonnet-4-5":  {"input": 0.003,   "output": 0.015},
}
```

---

## 📊 Logging e Observabilidade

### responses.jsonl
Cada chamada gera uma linha JSON com a estrutura:

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "model": "claude-haiku-4-5",
  "tokens_in": 350,
  "tokens_out": 120,
  "cost_usd": 0.000238,
  "latency_ms": 1423,
  "prompt_summary": "Usuário perguntou sobre análise de DRE..."
}
```

### Langfuse
- **Trace por sessão:** cada sessão CLI gera um trace único
- **Span por chamada:** cada chamada ao modelo gera um span dentro do trace
- **Metadados:** model, tokens, custo, latência são enviados como metadata do span
- Se as variáveis Langfuse não estiverem configuradas, o sistema roda normalmente sem observabilidade (graceful degradation)

---

## ✅ Convenções de Código

### Geral
- **Python 3.11+** — use type hints em todas as funções públicas
- **Pydantic** para validação de configurações e modelos de dados
- **f-strings** para formatação de strings (não `.format()` nem `%`)
- **Pathlib** para manipulação de caminhos (não `os.path`)

### Nomenclatura
- Classes: `PascalCase` — ex: `FinAgentSession`, `AnthropicClient`
- Funções e variáveis: `snake_case` — ex: `get_history`, `tokens_in`
- Constantes: `UPPER_SNAKE_CASE` — ex: `MAX_RETRIES`, `DEFAULT_MODEL`
- Arquivos: `snake_case.py`

### Imports
```python
# Ordem: stdlib → third-party → local
import json
import time
from pathlib import Path

import anthropic
from pydantic_settings import BaseSettings

from finagent.config import Settings
from finagent.session import Session
```

### Tratamento de erros
- **Nunca** use `except Exception` genérico sem logar o erro original
- Erros da API Anthropic → capture `anthropic.APIError` e subclasses
- Exiba mensagens de erro amigáveis ao usuário na CLI, log técnico no arquivo

### Testes
- Um arquivo de teste por módulo: `tests/test_<modulo>.py`
- Funções de teste: `test_<comportamento_esperado>`
- Use `pytest` com fixtures para setup de dependências
- Mock do cliente Anthropic nos testes — não fazer chamadas reais na suíte de testes

---

## 🚫 O que NÃO fazer

- **Não** commitar `.env` ou qualquer arquivo com credenciais
- **Não** fazer retry em erros 400 — é um bug no código, não na rede
- **Não** armazenar state no cliente HTTP — state fica no `Session`
- **Não** misturar lógica de apresentação (CLI) com lógica de negócio
- **Não** hardcodar API keys, URLs ou modelos no código — tudo via `config.py`
- **Não** avançar para a Fase 2 sem todas as funcionalidades obrigatórias da Fase 1 implementadas e testadas

---

## 🔄 Checklist de Conclusão da Fase 1

Antes de avançar para a Fase 2, confirme:

- [ ] `.env` no `.gitignore` desde o primeiro commit
- [ ] `config.py` carrega e valida todas as variáveis com pydantic-settings
- [ ] Multi-turn funcionando corretamente (histórico completo a cada chamada)
- [ ] Comandos `/clear`, `/history`, `/cost`, `/model` implementados
- [ ] Retry automático para 429 e 5xx com backoff exponencial (max 3 tentativas)
- [ ] Erro 400 falha imediatamente sem retry
- [ ] Streaming exibindo tokens em tempo real
- [ ] Métricas exibidas após cada resposta (modelo, tokens, custo, latência)
- [ ] Logging em `responses.jsonl` com estrutura definida
- [ ] Integração Langfuse com graceful degradation se não configurada
- [ ] `test_session.py` com testes passando
- [ ] `README.md` com instruções de instalação e uso
- [ ] Este `CLAUDE.md` atualizado com qualquer decisão arquitetural tomada

---

## 📝 Histórico de Decisões

| Data | Decisão | Motivo |
|------|---------|--------|
| — | `pydantic-settings` para config | Validação de tipos + suporte nativo a `.env` |
| — | `responses.jsonl` em vez de DB | Simplicidade na Fase 1; migrar para DB na Fase 3+ se necessário |
| — | Graceful degradation para Langfuse | Langfuse é opcional; não deve bloquear o uso local |
| 2026-06-17 | `src/operador_conta` (google-adk) tratado como experimento paralelo, fora do roadmap FinAgent | ADK foi testado por custo, mas resolve internamente (sessão, retry, tools, MCP, multi-agente) o que cada fase do roadmap pede pra construir manualmente — usá-lo não conta como progresso de fase. FinAgent segue 100% Anthropic SDK conforme stack original. |

> Adicione aqui qualquer decisão arquitetural relevante tomada durante o desenvolvimento, com data e justificativa.

---

*Última atualização: Fase 1 · Gerado em início do projeto*