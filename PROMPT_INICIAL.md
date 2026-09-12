# Prompt inicial para o Agent Antigravity

Você vai implementar uma aplicação web pequena de autenticação e cadastro de usuários neste repositório.

Antes de qualquer alteração, leia integralmente o arquivo `AGENTS.md` e siga todas as regras definidas nele. Leia também o MADR/ADR de arquitetura do projeto.

## Objetivo

Construir a primeira versão funcional da aplicação usando Python, Flask e SQLite.

## Requisitos funcionais

1. A página inicial deve possuir:
   - campo de usuário;
   - campo de senha;
   - botão `OK`;
   - botão `Limpar`.

2. Deve existir um usuário administrador inicial:
   - usuário: `admin`;
   - senha inicial: `admin`.

3. O administrador inicial deve ser automaticamente persistido no SQLite caso ainda não exista.

4. A senha do administrador e as senhas dos demais usuários não podem ser armazenadas em texto puro. Use hash seguro de senha.

5. Quando o administrador fizer login com sucesso, deve ser direcionado para a página de cadastro de usuários.

6. A tela de cadastro deve permitir que o administrador crie novos usuários informando:
   - nome de usuário;
   - senha.

7. Todo usuário criado pela tela de cadastro deve ser obrigatoriamente usuário comum. Não permita que essa tela crie administradores.

8. O nome de usuário deve ser único.

9. Quando um usuário comum fizer login corretamente, deve ser direcionado para uma página simples de boas-vindas.

10. Usuários comuns não podem acessar a página de cadastro de usuários.

11. Não implementar:
    - exclusão de usuários;
    - gerenciamento de usuários;
    - alteração de papel/permissão;
    - cadastro público;
    - recuperação de senha;
    - funcionalidades fora deste escopo.

## Arquitetura

Use:

- Python 3;
- Flask;
- SQLite;
- templates HTML/Jinja;
- sessão do Flask para autenticação;
- Werkzeug para hash e verificação de senha;
- pytest para testes.

Mantenha a solução pequena e direta.

Você pode usar `sqlite3` diretamente. Não adicione ORM ou dependências extras sem necessidade real.

## Comportamento esperado do banco

Na inicialização:

1. criar o banco/tabela se necessário;
2. verificar se o usuário `admin` existe;
3. se não existir, criar `admin` com:
   - senha funcional `admin`, armazenada como hash;
   - privilégio administrativo;
4. se já existir, não duplicar nem sobrescrever esse usuário.

## Testes

Implemente e execute testes automatizados para, no mínimo:

- inicialização do banco;
- criação automática e única do administrador;
- login válido de `admin/admin`;
- login inválido;
- cadastro de usuário comum;
- impedimento de usuário duplicado;
- confirmação de que usuário cadastrado não é administrador;
- login de usuário comum;
- redirecionamento correto conforme o tipo de usuário;
- bloqueio do cadastro para usuário comum.

Depois dos testes automatizados, faça também uma verificação funcional do fluxo principal sempre que isso for possível no ambiente.

## Forma de trabalho

Primeiro:

1. inspecione o repositório;
2. informe brevemente a estrutura encontrada e o que pretende alterar;
3. implemente a solução;
4. execute os testes;
5. corrija qualquer falha encontrada;
6. apresente o resultado final.

Não aumente o escopo durante a implementação.

## Git

Obedeça rigorosamente ao procedimento definido em `AGENTS.md`.

Em especial:

- NÃO execute `git push`;
- NÃO faça commit sem aprovação explícita;
- antes de qualquer commit, apresente:
  - o diff;
  - o resumo das alterações;
  - os arquivos modificados;
  - os testes executados;
  - os resultados dos testes;
  - riscos ou pendências;
  - uma mensagem de commit sugerida;
- depois disso, peça minha aprovação para fazer o commit.

Se eu aprovar, faça apenas o commit apresentado. Não faça push.

## Critério de aceite

Considere a implementação pronta somente quando:

- todos os requisitos acima estiverem atendidos;
- os testes relevantes estiverem passando;
- o fluxo `admin/admin -> cadastro` funcionar;
- o fluxo `usuário comum -> boas-vindas` funcionar;
- usuários comuns não conseguirem acessar a área de cadastro;
- o administrador estiver persistido no SQLite sem senha em texto puro;
- nenhuma funcionalidade de exclusão ou gerenciamento de usuários tiver sido adicionada.

Comece lendo `AGENTS.md` e o ADR/MADR do projeto e então inspecione o repositório antes de modificar qualquer arquivo.
