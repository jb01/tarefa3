# MADR — Decisão Arquitetural: Modularização Interna de Persistência (Alternativa B)

- **Status:** Aceita
- **Data:** 2026-09-12
- **Decisão:** Modularização interna entre `app.py` e `db.py` (Alternativa B)
- **Substitui:** `docs/adr/0001-python-flask-sqlite.md`

## Contexto

A primeira versão da aplicação consolidou a arquitetura monolítica enxuta utilizando Python, Flask e SQLite. No entanto, a análise arquitetural identificou pontos de acoplamento direto:
1. Consultas SQL inline embutidas diretamente dentro dos manipuladores de rota em `app.py` (`login` e `register`).
2. Duplicação na verificação de unicidade no fluxo de cadastro.
3. Impossibilidade de reutilizar operações de consulta a usuários fora do ciclo de requisição HTTP do Flask.

Foram avaliadas três alternativas:
- **A) Manter como está:** manter SQL inline nas rotas.
- **B) Pequena modularização interna:** extrair funções de consulta e inserção para `db.py`, mantendo a aplicação em apenas dois arquivos sem novas dependências.
- **C) Extrair serviço independente:** criar uma API/serviço separado (descartada por *overengineering*).

## Decisão

Adotar a **Alternativa B (Modularização Interna)**:

1. **Camada de Dados (`db.py`):**
   - Centralizar todas as operações de banco de dados (`get_user_by_username`, `create_user`) em `db.py`.
   - Manter a inicialização e conexão com o SQLite no mesmo módulo.
   - Tratar exceções de integridade (`sqlite3.IntegrityError`) de forma limpa.

2. **Camada Web (`app.py`):**
   - As rotas `login` e `register` deixam de executar queries SQL literais via cursor e passam a invocar as funções especializadas de `db.py`.
   - `app.py` foca exclusivamente em parsing HTTP, validações de requisição, controle de sessão e renderização de templates.

3. **Preservação de Escopo:**
   - Não adicionar ORMs, Repositories abstratos, DTOs ou microserviços.
   - Manter a estrutura de arquivos simples (`app.py`, `db.py`, `templates/`, `static/`, `tests/`).

## Consequências

### Positivas
- **Alta coesão:** cada módulo tem uma responsabilidade única e clara.
- **Baixo acoplamento:** rotas HTTP desacopladas de comandos SQL diretos.
- **Maior facilidade de manutenção:** alterações no schema ou queries afetam apenas `db.py`.
- **Zero complexidade acidental:** nenhuma dependência externa adicionada.
- **100% de compatibilidade:** preserva todos os contratos e passa em todos os testes automatizados existentes.

### Negativas
- Nenhuma desvantagem técnica para o escopo do projeto.

