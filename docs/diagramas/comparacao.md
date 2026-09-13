# Comparação das versões do diagrama arquitetural

## Versão 1

A versão 1 apresenta:

- Usuários administrador e comum.
- Aplicação Flask como um contêiner principal.
- Módulos internos `app.py` e `db.py`.
- Banco SQLite e tabela `users`.
- Rotas, funções, tecnologias, protocolos e detalhes de implementação.

**Benefícios:**

- É bastante detalhada.
- Relaciona diretamente a arquitetura ao código-fonte.
- Explica claramente os fluxos de autenticação e cadastro.

**Problemas:**

- Mistura níveis diferentes do modelo C4.
- Representa módulos internos como se fossem contêineres.
- Exibe detalhes de implementação que pertencem mais a diagramas de componentes ou à documentação técnica.
- Pode sugerir que `app.py` e `db.py` são unidades executáveis separadas.

## Versão 2

A versão 2 apresenta somente os elementos arquiteturais principais:

- Administrador e usuário comum.
- Aplicação web Flask.
- Banco de dados SQLite.
- Relações entre usuários, aplicação e banco.
- Responsabilidades principais de cada contêiner.
- Limites do sistema e tecnologias utilizadas.

**Benefícios:**

- Está mais alinhada ao nível 2 do modelo C4.
- Representa corretamente a aplicação Flask e o SQLite como os dois contêineres principais.
- Evita confundir módulos, rotas e tabelas com contêineres.
- É mais simples, legível e adequada para comunicação arquitetural.
- Explica corretamente que o SQLite é embarcado e não representa um servidor separado.

**Problemas:**

- Contém menos detalhes sobre rotas, funções internas e estrutura da tabela.
- Não substitui a documentação técnica ou um diagrama de componentes quando esses detalhes forem necessários.

## Comparação

A versão 1 é melhor como documentação de implementação e visão interna do sistema. Entretanto, para um diagrama C4 Container, ela possui excesso de detalhes e mistura conceitos de diferentes níveis arquiteturais.

A versão 2 é mais correta conceitualmente, pois mostra os contêineres reais em execução: a aplicação Flask e o banco SQLite. Também representa melhor os limites do sistema e mantém o foco nas responsabilidades e relações arquiteturais.

## Sugestão de decisão

A versão 2 deve ser adotada como o diagrama arquitetural oficial de nível C4 Container.

Ela representa melhor a arquitetura atual porque mantém o nível de abstração adequado e não trata `app.py`, `db.py`, rotas ou tabelas como contêineres independentes. Os detalhes presentes na versão 1 podem ser preservados como documentação complementar ou servir de base para um futuro diagrama de componentes.
