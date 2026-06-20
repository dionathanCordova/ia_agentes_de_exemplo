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


# Criando googleAdk Agentes

Primeiro passo deve ser instalar alguns pacotes muito importentes que são eles:

- uv ( gerenciador de pacotes )
    
    $ curl -LsSf https://astral.sh/uv/install.sh | sh
    
    Com esse gerenciador de pacotes podemos instalar varias dependencias como pandas, duckdb, etc.
    
     uv add pandas ( instalando dependencias ) ou  uv add duckdb
    
    Para executar um arquivo: uv run main.py
    
- Google adk ( Agent Development Kit )
    
    uv add google-adk ou pip install google-adk
    

Iniciando um projeto de criação

- $ python -m venv nome_projeto ( iniciando um ambiente virtual )
- $  source .venv/bin/activate ( ativando o ambiente virtual )
- $ adk create <nome_agente> ( iniciando a criacao do agente )
- $ adk web ( sobe o browser para interagir com o agente )



### Rodar api de interação com agentes

### (1(api = pasta), 2(api arquivo), 3(app = instancia do app no arquivo api.py))
$ uv run uvicorn api.api:app --reload

