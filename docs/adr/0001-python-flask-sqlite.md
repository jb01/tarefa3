# MADR — Arquitetura inicial da aplicação de usuários

- **Status:** Aceita
- **Data:** 2026-09-12
- **Decisão:** Python + Flask + SQLite
- **Escopo:** aplicação web local/simples para autenticação e cadastro de usuários

## Contexto

O projeto precisa implementar um fluxo pequeno de autenticação com dois tipos de usuário:

1. administrador inicial;
2. usuário comum.

O administrador inicial possui as credenciais funcionais `admin/admin` e, após autenticação, acessa uma tela para cadastrar usuários comuns.

Usuários comuns, após autenticação, acessam somente uma página de boas-vindas.

O sistema não precisa de:

- exclusão de usuários;
- tela de gerenciamento de usuários;
- cadastro público;
- múltiplos administradores pelo fluxo normal;
- API separada.

A solução deve utilizar Python e SQLite e permanecer simples de executar, entender e testar.

## Decisão

Será utilizada uma arquitetura web monolítica pequena composta por:

- **Python 3** como linguagem;
- **Flask** como framework HTTP e de renderização das páginas;
- **Jinja2**, fornecido pelo Flask, para templates HTML;
- **SQLite** como banco de dados local;
- **Werkzeug** para geração e validação de hash de senha;
- **sessão do Flask** para manter o estado de autenticação;
- **pytest** para testes automatizados.

A aplicação será organizada em camadas/módulos simples, evitando abstrações desnecessárias.

Estrutura sugerida:

```text
project/
├── app.py
├── db.py
├── schema.sql              # opcional
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── register.html
│   └── welcome.html
├── static/
│   └── style.css           # opcional
├── tests/
│   └── test_app.py
├── instance/
│   └── app.db              # gerado em runtime
├── AGENTS.md
└── docs/
    └── adr/
        └── 0001-python-flask-sqlite.md
```

A estrutura final pode variar ligeiramente, desde que preserve a simplicidade.

## Modelo de dados

Tabela mínima:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);
```

Opcionalmente pode existir `created_at`, caso isso não aumente desnecessariamente a complexidade.

### Administrador inicial

Na inicialização do banco:

1. criar a tabela `users` se ela ainda não existir;
2. consultar a existência de `username = 'admin'`;
3. se não existir, inserir:
   - `username = 'admin'`;
   - hash correspondente à senha inicial `admin`;
   - `is_admin = 1`;
4. se já existir, não alterar o registro.

A senha literal `admin` não deve ser salva em texto puro no SQLite.

## Fluxos

### Login

Rota sugerida:

```text
GET/POST /
```

A página apresenta:

- usuário;
- senha;
- botão OK;
- botão Limpar.

No `POST`:

1. buscar o usuário;
2. validar a senha contra o hash;
3. se inválida, apresentar erro;
4. se válida, registrar a identidade na sessão;
5. verificar `is_admin`.

### Administrador

Após autenticação:

```text
/register
```

A rota de cadastro deve exigir sessão autenticada e privilégio administrativo.

O formulário recebe:

- nome do usuário;
- senha.

O backend define obrigatoriamente:

```text
is_admin = 0
```

O cliente não deve enviar nem escolher o papel do novo usuário.

### Usuário comum

Após autenticação:

```text
/welcome
```

A página mostra somente uma mensagem de boas-vindas e não oferece funções administrativas.

## Autorização

Autenticação e autorização são responsabilidades separadas.

Estar autenticado não é suficiente para acessar `/register`.

A rota administrativa deve validar explicitamente que o usuário atual é administrador.

Usuários comuns que tentarem acessar diretamente uma rota administrativa devem ser bloqueados ou redirecionados.

## Tratamento de senha

As senhas serão processadas com funções de hash de senha do Werkzeug, por exemplo:

```python
generate_password_hash(...)
check_password_hash(...)
```

Motivo: mesmo em um projeto pequeno, armazenar senhas em texto puro introduz um risco desnecessário e não simplifica significativamente a implementação.

## Persistência

O SQLite será suficiente porque:

- o projeto é pequeno;
- não há requisito de alta concorrência;
- não há necessidade atual de servidor de banco separado;
- simplifica instalação e testes;
- permite persistência real entre reinicializações.

O arquivo de banco gerado em runtime não precisa ser versionado no Git. O esquema e o código de bootstrap devem ser versionados.

## Testabilidade

A aplicação deve permitir criar um banco SQLite temporário durante testes.

Os testes devem validar pelo menos:

- bootstrap do banco;
- criação única do administrador;
- login do administrador;
- falha de autenticação;
- cadastro de usuário comum;
- unicidade de nome de usuário;
- login de usuário comum;
- autorização das rotas;
- redirecionamentos esperados.

## Alternativas consideradas

### Django

Não escolhido neste momento.

Vantagens:

- autenticação e ORM completos;
- painel administrativo;
- estrutura robusta.

Desvantagens para este escopo:

- maior complexidade;
- oferece muito mais infraestrutura do que o necessário;
- o painel administrativo e o sistema completo de usuários não são requisitos.

### FastAPI

Não escolhido neste momento.

É excelente para APIs, mas este projeto é centrado em páginas HTML simples com formulários e sessão. Flask reduz a quantidade de infraestrutura necessária.

### SQLAlchemy

Pode ser adotado futuramente, mas não é obrigatório para a primeira versão.

Para uma única tabela e operações simples, `sqlite3` mantém a solução pequena. Caso o modelo de dados cresça, uma nova decisão arquitetural pode avaliar a adoção de ORM.

## Consequências

### Positivas

- baixa complexidade operacional;
- poucas dependências;
- fácil execução local;
- fácil criação de testes;
- persistência simples;
- separação clara entre administrador e usuário comum;
- possibilidade de evolução futura.

### Negativas

- SQLite não é a melhor opção para alta concorrência;
- a solução inicial terá recursos de autenticação mais simples que frameworks completos;
- mudanças futuras de escala podem exigir migração do banco e maior estruturação.

## Restrições arquiteturais

A primeira versão não deve introduzir:

- microserviços;
- frontend SPA;
- banco externo;
- containers como requisito obrigatório;
- ORM sem necessidade comprovada;
- API REST separada;
- sistema complexo de permissões.

Qualquer mudança relevante nesta decisão deve gerar um novo ADR ou atualização explicitamente aprovada.
