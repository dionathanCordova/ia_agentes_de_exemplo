Criação de agente

1 - Iniciar um projeto uv init . ( uv é um gerenciador de pacotes )
    # efetuar a instalação caso nao possua: curl -LsSf https://astral.sh/uv/install.sh | sh
    # verificar a versão 
    # outros comandos interessantes
        uv add pandas ( instalando dependencias )
        ou
        uv add duckdb
        Executar um script: uv run main.py



## dependencias
google-adk===2.2.0

#### Run projetoc
adk run .<file>

### rodando pela interface do adk
adk web ./agentes --reload_agents