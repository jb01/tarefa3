# Análise Arquitetural do Projeto

**Data:** 2026-09-12  
**Escopo:** Análise técnica da arquitetura atual com base estrita no código-fonte existente no repositório.

---

## 1. Estrutura Atual do Projeto

O projeto é estruturado como um monolito web enxuto em Python utilizando o framework Flask e o banco de dados relacional embarcado SQLite.

### 1.1. Principais Arquivos e Módulos

| Arquivo / Diretório | Responsabilidade |
| :--- | :--- |
| [`app.py`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py) | **Controlador principal e rotas web.** Contém a factory da aplicação (`create_app`), gerenciamento de contexto de conexão com o banco por requisição (`g.db`), decoradores de autorização (`admin_required`, `login_required`), função utilitária de validação (`validate_username`) e os manipuladores de requisição HTTP (`/`, `/register`, `/welcome`, `/logout`). |
| [`db.py`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/db.py) | **Infraestrutura de banco de dados e bootstrap.** Define a constante DDL `SCHEMA_SQL`, a função de conexão de baixo nível `get_db_connection` e a rotina de inicialização/idempotência `init_db` que cria a tabela `users` e o administrador inicial caso não existam. |
| [`templates/`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/templates) | **Camada de apresentação (Jinja2).** Renderiza as interfaces HTML: `base.html` (layout base e mensagens flash), `login.html` (formulário de login com botões OK e Limpar), `register.html` (cadastro de novos usuários comuns) e `welcome.html` (boas-vindas para usuários comuns). |
| [`static/style.css`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/static/style.css) | **Estilização.** Fornece estilos CSS para botões, caixas de formulário e alertas de feedback. |
| [`tests/test_app.py`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/tests/test_app.py) | **Suíte de testes automatizados (pytest).** Contém fixtures de aplicação/cliente de teste com banco isolado e classes de teste (`TestDatabaseAndBootstrap`, `TestAuthenticationFlow`, `TestUserRegistrationAndPrivileges`, `TestCommonUserFlowAndAccessControl`). |
| [`requirements.txt`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/requirements.txt) | **Dependências externas.** Declaração explícita de `Flask`, `Werkzeug` e `pytest`. |
| [`pytest.ini`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/pytest.ini) | **Configuração de execução de testes.** Define `pythonpath = .` e diretório de testes. |

### 1.2. Banco de Dados Envolvido

- **Motor:** SQLite3 (`sqlite3` da biblioteca padrão do Python).
- **Tabela única (`users`):**
  - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
  - `username` (`TEXT NOT NULL UNIQUE`)
  - `password_hash` (`TEXT NOT NULL`)
  - `is_admin` (`INTEGER NOT NULL DEFAULT 0`)
  - `created_at` (`TIMESTAMP DEFAULT CURRENT_TIMESTAMP`)

---

## 2. Dependências entre os Módulos

```text
tests/test_app.py ─────────┐
    │                      │
    ▼                      ▼
  app.py ──────────────► db.py ───► sqlite3 / werkzeug
    │                      │
    ▼                      ▼
templates/             SQLite (app.db)
```

### 2.1. Fluxo de Chamadas e Módulos
- **Quem chama quem:**
  - `app.py` importa e chama `init_db` (na inicialização em `create_app`, linha 45) e `get_db_connection` (em `get_db`, linha 50).
  - `app.py` renderiza os templates em `templates/` através das funções `render_template` do Flask.
  - `tests/test_app.py` importa `create_app` de `app.py` e `get_db_connection`, `init_db` de `db.py`.
- **Dependência do Flask:**
  - Apenas [`app.py`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py) depende diretamente do framework Flask (`Flask`, `request`, `session`, `g`, `render_template`, `redirect`, `url_for`, `flash`, `abort`).
  - [`db.py`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/db.py) **não depende** do Flask; utiliza apenas `sqlite3`, `os` e `werkzeug.security`.
- **Acesso direto ao SQLite:**
  - `db.py`: executa `SCHEMA_SQL` e queries de bootstrap em `init_db` (linhas 43-53).
  - `app.py`: executa queries SQL diretamente nas rotas `login` (linhas 101-105) e `register` (linhas 156 e 164-167).
- **Localização dos Mecanismos de Autenticação, Autorização e Cadastro:**
  - **Autenticação:** [`app.py:login`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L83-L128) valida o hash da senha via `check_password_hash` e grava a identidade em `session['user_id']`, `session['username']` e `session['is_admin']`.
  - **Autorização:** [`app.py:admin_required`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L60-L70) e [`app.py:login_required`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L72-L80) inspecionam o cookie de sessão do Flask para conceder ou negar acesso (abortando com `403` ou redirecionando para login).
  - **Regras de Cadastro:** [`app.py:register`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L130-L175) e [`app.py:validate_username`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L22-L26) validam tamanho/espaços, forçam `is_admin = 0` e geram hash de senha via `generate_password_hash`.

---

## 3. Pontos de Acoplamento

1. **Código HTTP e Persistência Misturados nas Rotas:**
   - Em [`app.py:login`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L83-L128) e [`app.py:register`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L130-L175), a mesma função trata a extração dos parâmetros de `request.form`, instancia o cursor SQL, formula a query SQL diretamente em texto (`SELECT ...`, `INSERT ...`), controla a transação (`db.commit()`), manipula mensagens de sessão (`flash`) e retorna respostas HTML/redirecionamento.
2. **Regras de Negócio Inseridas nas Rotas:**
   - A decisão de definir `is_admin = 0` para novos cadastros (linha 165 de `app.py`) e a regra de hashing seguro de senhas estão escritas diretamente dentro do corpo da função da rota Flask, em vez de estarem em funções de modelo/serviço.
3. **Dependência de Globais de Contexto do Flask (`g` e `session`):**
   - A função `get_db()` em `app.py` (linhas 47-51) depende explicitamente do objeto `flask.g`. Isso significa que operações de persistência feitas a partir de `app.py` não podem ser executadas fora do ciclo de vida de uma requisição Flask ativa.
4. **Duplicações e Redundâncias:**
   - Na rota `register` (linhas 156-173 de `app.py`), há uma checagem prévia de unicidade com `SELECT id FROM users WHERE username = ?` e, em seguida, um bloco `try/except sqlite3.IntegrityError` na inserção, tratando a mesma regra de negócio (unicidade) em dois pontos consecutivos na mesma função.

---

## 4. Contratos Existentes

### 4.1. Funções e Assinaturas

- `validate_username(username: str | None) -> tuple[bool, str | None]` ([`app.py:22`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L22))
  - Entrada: string do username ou `None`.
  - Saída: tupla `(is_valid: bool, error_message: str | None)`.
- `create_app(test_config: dict | None = None) -> Flask` ([`app.py:29`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L29))
  - Entrada: dicionário opcional de configurações (ex: `TESTING`, `DATABASE`).
  - Saída: instância configurada do aplicativo Flask.
- `get_db_connection(db_path: str) -> sqlite3.Connection` ([`db.py:18`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/db.py#L18))
  - Entrada: caminho absoluto ou relativo para o arquivo SQLite.
  - Saída: conexão SQLite configurada com `row_factory = sqlite3.Row`.
- `init_db(db_path: str) -> None` ([`db.py:25`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/db.py#L25))
  - Entrada: caminho do banco SQLite.
  - Saída: `None` (efeito colateral: criação de tabelas e inserção idempotente do usuário `admin`).

### 4.2. Contratos de Rotas HTTP

| Rota | Métodos | Autenticação / Autorização | Entrada | Respostas / Redirecionamento |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET`, `POST` | Pública | `username`, `password` | `200` (renderiza `login.html`), `302` (para `/register` se admin, para `/welcome` se comum), `400` (campos vazios), `401` (credenciais inválidas) |
| `/register` | `GET`, `POST` | Privada (`admin_required`) | `username`, `password` | `200` (renderiza `register.html`), `302` (redireciona para `/register` pós-sucesso ou `/` se não autenticado), `400` (campos inválidos), `403` (usuário não admin), `409` (username duplicado) |
| `/welcome` | `GET` | Privada (`login_required`) | Nenhuma | `200` (renderiza `welcome.html`), `302` (para `/` se não autenticado) |
| `/logout` | `GET` | Nenhuma restrição | Nenhuma | `302` (limpa `session` e redireciona para `/`) |

---

## 5. Avaliação Objetiva

- **Coesão:**
  - *`db.py`:* **Alta.** Focado exclusivamente na inicialização de banco e conectividade SQLite.
  - *`app.py`:* **Média a Baixa.** Centraliza parsing HTTP, controle de sessão, roteamento, validação de dados e consultas SQL no mesmo arquivo.
- **Acoplamento:**
  - *Entre módulos:* **Baixo.** `db.py` é desacoplado de frameworks web; `app.py` depende apenas de duas funções exportadas por `db.py`.
  - *Entre camadas internas:* **Alto.** O código das rotas em `app.py` é fortemente acoplado à sintaxe e aos cursores do `sqlite3`.
- **Separação de Responsabilidades:**
  - A separação entre infraestrutura (`db.py`) e aplicação (`app.py`) existe, mas não há separação intermediária entre camada de apresentação e camada de acesso a dados (as rotas falam diretamente com o banco).
- **Testabilidade:**
  - **Alta.** O uso do padrão Application Factory (`create_app(test_config)`) permite injetar bancos de dados temporários por teste, possibilitando testar fluxos completos com isolamento total via `pytest` sem necessidade de mocks complexos.
- **Facilidade de Evolução:**
  - Para o escopo definido (cadastro simples e autenticação de 2 papéis), a arquitetura é fácil de manter e inspecionar. Caso novos fluxos de usuários ou regras adicionais fossem solicitados, o acoplamento de SQL nas rotas começaria a gerar repetição de código.

---

## 6. Problemas Arquiteturais Reais Identificados

Com base puramente no código existente (e sem propor padrões por preferência pessoal), identificam-se **3 problemas reais**:

1. **Mistura de Acesso SQL Direto dentro dos Controladores HTTP ([`app.py:101-105`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L101-L105) e [`app.py:156-168`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L156-L168)):**  
   As queries SQL de busca de usuário (`SELECT id, username, password_hash, is_admin FROM users WHERE username = ?`) e inserção de usuário comum estão escritas inline nas rotas. Isso impede que regras de consulta sejam reutilizadas ou testadas isoladamente sem subir o contexto HTTP do Flask.
2. **Duplicação Lógica na Verificação de Unicidade ([`app.py:156-173`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L156-L173)):**  
   A rota `/register` faz uma consulta `SELECT` prévia para checar se o username já existe e, imediatamente depois, envolve o `INSERT` em um bloco `try/except sqlite3.IntegrityError` para tratar a mesma colisão de chave única no banco. Duas checagens para o mesmo evento de erro no mesmo fluxo.
3. **Validação de Dados Dividida Assimetricamente ([`app.py:22`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L22) vs [`app.py:86-97`](file:///home/josemberg/Documentos/MESTRADO/DEV-ia/tarefa3/app.py#L86-L97)):**  
   Existe a função isolada `validate_username` usada em `/register`, mas a rota de login (`/`) implementa sua própria validação inline sem utilizar essa função ou reutilizar a mesma regra de sanitização de strings.

---

## 7. Justificativa para Extração de Novos Módulos ou Serviços

### Resposta Objetiva: **NÃO há justificativa concreta.**

**Fundamentação Técnica e de Escopo:**
- **Tamanho da Base:** O projeto inteiro possui menos de **260 linhas de código Python** distribuídas em apenas dois módulos (`app.py` com ~195 linhas e `db.py` com ~60 linhas).
- **Escopo Fechado:** Não há múltiplos modelos de domínio, listagens complexas, integrações externas, filas ou regras de negócio extensas (conforme delimitado em `AGENTS.md` e no MADR `0001-python-flask-sqlite.md`).
- **Risco de Overengineering:** A criação de camadas adicionais (como Service Layer, Repository Pattern, DTOs, Blueprints ou ORMs) aumentaria a complexidade acidental, a quantidade de arquivos e o overhead cognitivo sem trazer nenhum benefício mensurável de desempenho, manutenibilidade ou testabilidade para o escopo atual.
- **Evolução Suficiente:** Caso se deseje melhorar os pontos identificados na seção 6, basta uma reorganização pontual (ex: mover funções como `get_user_by_username` ou `create_user` para `db.py`), mantendo a estrutura simples em dois arquivos sem introduzir novas camadas conceituais.

