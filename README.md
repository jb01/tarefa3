# Aplicação de Autenticação e Cadastro de Usuários

Aplicação web desenvolvida em Python com Flask e SQLite para autenticação e cadastro de usuários, seguindo a arquitetura descrita em `AGENTS.md` e no MADR `docs/adr/0001-python-flask-sqlite.md`.

## Requisitos

- Python 3.10+
- Flask >= 3.0.0
- Werkzeug >= 3.0.0
- pytest >= 8.0.0

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução da Aplicação

```bash
python3 app.py
```

Acesse no navegador: `http://127.0.0.1:5000`

### Credenciais Iniciais

- **Administrador:**
  - Usuário: `admin`
  - Senha: `admin`

Ao efetuar login como administrador, você será redirecionado para a página de cadastro de usuários comuns.

- **Usuários comuns:**
  - Criados pelo administrador na tela de cadastro.
  - Ao efetuar login, são direcionados para a página de boas-vindas.

## Execução dos Testes

```bash
pytest -v
```
