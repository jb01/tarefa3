# AGENTS.md

## 1. Objetivo do projeto

Este repositório contém uma aplicação web pequena para autenticação e cadastro de usuários.

Escopo funcional:

- Página inicial com:
  - campo de usuário;
  - campo de senha;
  - botão **OK**;
  - botão **Limpar**.
- Banco de dados SQLite.
- Aplicação desenvolvida em Python.
- Usuário administrador inicial:
  - usuário: `admin`
  - senha inicial: `admin`
- O administrador inicial deve ser criado automaticamente e persistido no banco de dados na inicialização da aplicação, caso ainda não exista.
- Ao autenticar como administrador, abrir a página de cadastro de usuários.
- Usuários cadastrados pelo administrador são sempre usuários comuns, nunca administradores.
- Ao autenticar como usuário comum, abrir apenas uma página de boas-vindas.
- Não existe tela de gerenciamento/listagem administrativa de usuários.
- Não existe funcionalidade para exclusão de usuários.

## 2. Stack definida

Use, salvo decisão arquitetural posterior aprovada:

- Python 3;
- Flask;
- SQLite;
- biblioteca padrão `sqlite3` ou uma camada mínima de acesso compatível com SQLite;
- Werkzeug para geração e verificação de hash de senha;
- `pytest` para testes automatizados.

Evite adicionar dependências sem necessidade. Toda nova dependência deve ter justificativa objetiva.

## 3. Regras obrigatórias para o agente

### 3.1. Trabalhar apenas dentro do escopo

Implemente somente o necessário para os requisitos definidos neste repositório.

Não adicionar, sem solicitação explícita:

- recuperação de senha;
- alteração de senha;
- exclusão de usuário;
- gerenciamento de perfis;
- múltiplos níveis administrativos;
- painel administrativo;
- API REST;
- cadastro público;
- e-mail;
- autenticação social;
- recursos não descritos nos requisitos.

Se identificar uma melhoria fora do escopo, apenas informe como sugestão. Não a implemente sem aprovação.

### 3.2. Antes de alterar código

Antes de uma mudança relevante:

1. leia este `AGENTS.md`, ADRs, Specs, `README.md`;
2. inspecione a estrutura atual do repositório;
3. identifique os arquivos que serão alterados;
4. preserve código existente que não precise ser modificado;
5. escolha a solução mais simples que atenda ao requisito.

### 3.3. Segurança de senha

Nunca persista senhas de usuários em texto puro.

O usuário inicial deve possuir as credenciais funcionais:

- login: `admin`
- senha: `admin`

Porém, no banco SQLite, a senha deve ser armazenada como hash seguro.

O bootstrap do banco deve:

1. criar as tabelas necessárias quando não existirem;
2. verificar se o usuário `admin` já existe;
3. inserir o administrador inicial somente quando ele ainda não existir;
4. não recriar, duplicar ou sobrescrever o administrador a cada inicialização.

### 3.4. Regra para usuários criados pelo administrador

Todo usuário criado pela tela de cadastro deve ser obrigatoriamente um usuário comum.

A interface não deve permitir escolher o papel/role do novo usuário.

A aplicação não deve aceitar que o fluxo normal de cadastro crie outro administrador.

### 3.5. Validações mínimas

O cadastro deve, no mínimo:

- exigir nome de usuário;
- exigir senha;
- impedir nome de usuário duplicado;
- informar o resultado do cadastro de forma compreensível;
- armazenar a senha com hash.

O login deve:

- validar usuário e senha;
- distinguir administrador de usuário comum;
- rejeitar credenciais inválidas sem expor informação sensível.

## 4. Fluxos obrigatórios

### 4.1. Login

Página inicial:

- campo `usuário`;
- campo `senha`;
- botão `OK`;
- botão `Limpar`.

Comportamento:

- `OK`: tenta autenticar;
- `Limpar`: limpa os dois campos;
- login inválido: permanece no fluxo de login e apresenta mensagem de erro adequada.

### 4.2. Login do administrador

Com:

- usuário: `admin`;
- senha: `admin`;

o sistema deve autenticar o administrador e direcioná-lo para a página de cadastro de usuários.

### 4.3. Cadastro

Na página acessível ao administrador:

- permitir cadastrar usuário e senha;
- todo novo usuário deve ser criado como usuário comum;
- não incluir exclusão;
- não incluir gerenciamento/listagem geral de usuários, salvo algum elemento estritamente necessário para confirmar o cadastro.

### 4.4. Login de usuário comum

Após autenticação válida de um usuário comum:

- direcionar para uma página de boas-vindas;
- não apresentar funções administrativas;
- não oferecer cadastro, exclusão ou gerenciamento de usuários.

## 5. Banco de dados

Use SQLite.

A modelagem mínima recomendada para usuários contém:

- `id`: chave primária;
- `username`: único e obrigatório;
- `password_hash`: obrigatório;
- `is_admin`: booleano ou inteiro equivalente, obrigatório, com valor padrão falso;
- `created_at`: opcional, caso seja útil e simples.

Regras:

- `username` deve possuir restrição de unicidade no banco;
- o administrador inicial deve ter `is_admin = true`;
- usuários cadastrados pela aplicação devem ter `is_admin = false`.

Não implemente exclusão de registros de usuários.

## 6. Testes obrigatórios

Assim que concluir cada funcionalidade ou conjunto coerente de funcionalidades, execute os testes correspondentes antes de considerar o trabalho concluído.

No mínimo, cubra:

1. criação/inicialização do banco;
2. criação automática do usuário `admin`;
3. ausência de duplicação do `admin` em reinicializações;
4. autenticação correta de `admin/admin`;
5. rejeição de senha incorreta;
6. cadastro de um usuário comum pelo administrador;
7. tentativa de cadastro de usuário duplicado;
8. autenticação de usuário comum;
9. redirecionamento do administrador para cadastro;
10. redirecionamento do usuário comum para boas-vindas;
11. bloqueio da página administrativa para usuário não administrador, se a aplicação usar sessão;
12. confirmação de que usuários criados no cadastro não recebem privilégio administrativo.

Quando aplicável, faça também um teste funcional/manual do fluxo principal.

Não declare que uma funcionalidade está concluída se os testes relevantes estiverem falhando.

## 7. Regra de commits

O agente **não possui autorização para realizar commits automaticamente**.

Antes de cada commit proposto, obrigatoriamente:

1. conclua a alteração;
2. execute os testes relevantes;
3. verifique o estado do repositório;
4. apresente ao usuário o diff completo ou, se muito extenso, um diff organizado por arquivo sem omitir alterações relevantes;
5. informe objetivamente:
   - o que foi alterado;
   - por que foi alterado;
   - quais arquivos foram modificados;
   - quais testes foram executados;
   - o resultado de cada teste;
   - riscos, limitações ou pendências conhecidas;
6. proponha uma mensagem de commit;
7. peça aprovação explícita do usuário para realizar o commit.

Somente após aprovação explícita o agente pode executar o commit correspondente.

Uma aprovação vale apenas para o commit apresentado naquele momento. Alterações adicionais exigem nova apresentação de diff e nova aprovação.

## 8. Push proibido

O agente **não pode executar `git push` em nenhuma circunstância**.

Também não deve:

- criar automações que façam push;
- alterar configuração do repositório para habilitar push automático;
- usar outra ferramenta ou mecanismo para publicar commits remotamente.

Após um commit local aprovado, pare no repositório local e informe o resultado.

O push é responsabilidade exclusiva do usuário.

## 9. Operações Git destrutivas

Não executar sem solicitação explícita do usuário:

- `git reset --hard`;
- `git clean -fd`;
- `git checkout -- <arquivo>`;
- rebase destrutivo;
- force push;
- remoção de branches;
- sobrescrita de mudanças não commitadas.

Nunca descarte alterações existentes do usuário para facilitar a implementação.

## 10. Critério de conclusão de uma tarefa

Uma tarefa só pode ser apresentada como concluída quando:

- o requisito solicitado estiver implementado;
- os testes relevantes tiverem sido executados;
- os testes estiverem passando;
- não houver erro conhecido ocultado;
- o agente tiver informado as alterações e os resultados.

Se a tarefa resultar em uma proposta de commit, aplicar também todo o procedimento da seção **Regra de commits**.

## 11. Comunicação

Se houver mais de uma solução tecnicamente válida:

- prefira a de menor complexidade;
- preserve o escopo;
- explique brevemente qualquer decisão que afete a arquitetura ou os requisitos.

Não faça mudanças arquiteturais relevantes silenciosamente.

Quando um requisito entrar em conflito com este arquivo, interrompa a implementação daquela parte, explique o conflito e solicite orientação antes de prosseguir.

