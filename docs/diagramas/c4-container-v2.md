# Arquitetura atual — C4 Container (nível 2)

Diagrama baseado na implementação atual de [app.py](../../app.py), [db.py](../../db.py) e na [decisão de modularização interna](../decisao-arquitetural-etapa4.md). A notação Mermaid `flowchart` representa os elementos e relações do nível C4 Container.

```mermaid
flowchart TB
    admin["Administrador<br/>[Pessoa]<br/>Autentica e cadastra usuários comuns"]
    usuario["Usuário comum<br/>[Pessoa]<br/>Autentica e acessa apenas boas-vindas"]

    subgraph sistema["Sistema de Autenticação e Cadastro de Usuários — fronteira do sistema"]
        web["Aplicação web<br/>[Container: Python 3 / Flask]<br/>Autentica, controla sessões e autorizações,<br/>cadastra usuários comuns e renderiza HTML"]
        banco[("Banco de dados de usuários<br/>[Container de persistência: SQLite 3]<br/>Arquivo local: instance/app.db<br/>Persiste usuários, hashes de senhas e indicador de administrador;<br/>garante unicidade dos nomes de usuário")]
    end

    admin -->|"Autentica e envia cadastros de usuários comuns<br/>HTTP via navegador; recebe HTML"| web
    usuario -->|"Autentica e visualiza boas-vindas<br/>HTTP via navegador; recebe HTML"| web
    web -->|"Consulta usuários e grava cadastros;<br/>inicializa o banco e cria admin se ausente<br/>SQL via sqlite3; acesso ao arquivo local"| banco

    classDef pessoa fill:#08427b,color:#fff,stroke:#052e56
    classDef container fill:#1168bd,color:#fff,stroke:#0b4884
    class admin,usuario pessoa
    class web,banco container
    style sistema fill:#f5f5f5,stroke:#666,stroke-dasharray:5 5
```

Existem dois containers dentro da fronteira: a aplicação web, unidade executável, e o banco SQLite, unidade de persistência. O SQLite é embarcado e acessado como arquivo local; sua representação não implica um servidor ou processo separado. Container C4 não implica uso de Docker.

A aplicação usa Jinja2 para renderizar HTML e Werkzeug para gerar e verificar hashes de senha. `app.py` e `db.py` integram a mesma aplicação em execução. Páginas, rotas, funções, templates e tabelas são detalhes internos e não aparecem como containers. O navegador é o meio de interação dos atores, indicado nas relações.

Após autenticação, o administrador é direcionado ao cadastro, que sempre cria usuários comuns. O usuário comum é direcionado às boas-vindas e tem o acesso ao cadastro bloqueado. A inicialização persiste o administrador inicial somente quando ele ainda não existe.
