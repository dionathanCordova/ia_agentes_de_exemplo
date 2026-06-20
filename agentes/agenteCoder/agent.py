from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import BuildInCodeExecutor

search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description='Você e um agente especializado em busca que busca na web de informacoes via Google Search.',
    instruction="""
        Você e um agente especializado em busca que busca na web de informacoes via Google Search.
        Use a ferramenta google_search para buscar as informacoes.
    """,
    tools=[google_search],
    code_executor=BuildInCodeExecutor(),
)

code_executor = Agent(
    model='gemini-2.5-flash',
    name='code_executor',
    description='Você e um agente especializado em executar codigo.',
    instruction="""
        Você e um agente especializado em executar codigo.
        Use a ferramenta code_executor para executar o codigo.
    """,
    code_executor=BuildInCodeExecutor(),
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Você e um agente raiz que orquesta os outros agentes.',
    instruction="""
        Você e um agente raiz que orquesta os outros agentes.
        Use os outros agentes para buscar as informacoes.
        Nunca invente informacoes, sempre use as ferramentas disponiveis para buscar as informacoes, caso não tenha as informacoes, diga que não tem as informacoes.
    """,
    tools=[AgentTool(agent=search_agent), AgentTool(agent=code_executor)],
    code_executor=BuildInCodeExecutor(),
)
