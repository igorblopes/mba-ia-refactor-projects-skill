# Referência: Análise do Projeto (Fase 1)

Heurísticas para detectar **linguagem**, **framework**, **banco de dados**, **domínio** e
a **arquitetura atual** de um projeto de backend desconhecido. O objetivo da Fase 1 é
acertar *o que o projeto é* antes de julgar *quão bom ele é*. A detecção é o que torna a
skill agnóstica de tecnologia: nunca presuma a stack — leia as evidências.

## Conteúdo

- [Passo 1 — Detectar linguagem & framework pelo manifesto](#passo-1)
- [Passo 2 — Detectar o banco de dados](#passo-2)
- [Passo 3 — Inferir o domínio](#passo-3)
- [Passo 4 — Mapear a arquitetura atual](#passo-4)
- [Passo 5 — Contar o que você analisou](#passo-5)
- [Cola de detecção](#cola)

---

<a name="passo-1"></a>
## Passo 1 — Detectar linguagem & framework pelo manifesto

Leia o manifesto de dependências **antes** do código-fonte. Ele é o sinal mais rápido e
confiável. Mapeie o manifesto para uma linguagem e então olhe suas dependências
declaradas para achar o framework web e sua versão.

| Arquivo de manifesto | Linguagem | Onde o framework aparece |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python | `flask`, `django`, `fastapi`, `bottle` |
| `package.json` | JavaScript / TypeScript (Node) | `express`, `koa`, `fastify`, `nestjs`, `hapi` |
| `pom.xml`, `build.gradle` | Java / Kotlin | `spring-boot`, `javalin` |
| `go.mod` | Go | `gin`, `echo`, `fiber`, `chi` |
| `composer.json` | PHP | `laravel`, `symfony`, `slim` |
| `Gemfile` | Ruby | `rails`, `sinatra` |

Leia a **versão fixada** quando houver (ex.: `flask==3.1.1`, `"express": "^4.18.2"`) e
reporte-a — a versão importa para identificar APIs deprecated na Fase 2.

Se não houver manifesto, recorra às extensões de arquivo e aos imports (`.py` +
`from flask import` ⇒ Python/Flask; `.js` + `require('express')` ⇒ Node/Express).

## Passo 2 — Detectar o banco de dados
<a name="passo-2"></a>

Procure, nesta ordem:

1. **Driver / ORM no manifesto** — `sqlite3`, `psycopg2`, `mysqlclient`,
   `flask-sqlalchemy`, `sequelize`, `mongoose`, `prisma`, `pg`, `mysql2`.
2. **Código de conexão** — `sqlite3.connect(...)`, `new sqlite3.Database(...)`,
   `createConnection(...)`, `SQLALCHEMY_DATABASE_URI`, uma connection string.
3. **Definições de schema** — comandos `CREATE TABLE ...`, classes de model do ORM
   (`class X(db.Model)`, `sequelize.define(...)`), arquivos de migração.

Extraia os **nomes de tabelas / models** — eles são a espinha dorsal tanto da inferência
de domínio (Passo 3) quanto da camada de Models que você vai criar na Fase 3. Note se o
banco é baseado em arquivo (`sqlite`), em memória (`:memory:`) ou um servidor
(Postgres/MySQL/Mongo).

## Passo 3 — Inferir o domínio
<a name="passo-3"></a>

Você normalmente não recebe uma especificação. Reconstrua o domínio a partir de três
fontes:

- **Caminhos de rota** — `/produtos`, `/pedidos`, `/checkout`, `/enrollments`, `/tasks`
  revelam os substantivos e verbos do negócio.
- **Nomes de tabelas / models** — `usuarios`, `courses`, `payments`, `categories`.
- **Identificadores & mensagens** — nomes de variáveis, strings de log, dados de seed.

Resuma o domínio em uma frase, ex.: *"API de E-commerce (produtos, pedidos, usuários)"*
ou *"LMS com fluxo de checkout/matrícula"* ou *"Gerenciador de tarefas (tasks, usuários,
categorias)"*.

> **Cuidado — o nome da pasta/repo pode enganar.** Infira o domínio pelas evidências
> internas (rotas, tabelas/models, mensagens), **nunca** pelo nome do diretório. Ex.: uma
> pasta chamada `ecommerce-api-legacy` cujas tabelas são `courses`, `enrollments`,
> `payments` e cujo log diz "LMS" é, na verdade, um **LMS** com fluxo de checkout — não um
> e-commerce de produtos. Se o nome da pasta contradiz o código, vale o código.

## Passo 4 — Mapear a arquitetura atual
<a name="passo-4"></a>

Descreva como o código está *atualmente* organizado, com honestidade. Este é o "antes"
que você vai melhorar. Posicione o projeto neste espectro:

- **Monolítico / sem camadas** — um ou poucos arquivos contendo roteamento + lógica de
  negócio + acesso a dados + config tudo misturado. (Sinal: um único `models.py` com SQL
  *e* formatação; um `app.js` que define rotas inline.)
- **God object** — uma classe/módulo que "gerencia tudo": init de DB, rotas, pagamento,
  logging. (Sinal: uma classe chamada `*Manager`, `*Service`, `*Helper` fazendo 5 tarefas
  não relacionadas.)
- **Camadas parciais** — *existem* pastas (`models/`, `routes/`, `services/`, `utils/`)
  mas as responsabilidades ainda vazam: lógica de negócio e queries de banco dentro dos
  handlers de rota, `to_dict()`s inchados, lógica duplicada entre rotas.
- **Camadas limpas** — separação clara de Model / Controller / View, config externalizada,
  tratamento de erros centralizado. (Raro na entrada; este é o seu *alvo*.)

Note o **ponto de entrada** (`app.py`, `src/app.js`, `main.go`) e o **estilo de
roteamento** (`add_url_rule`, decorators, Blueprints, `app.get(...)`, um arquivo de
router).

## Passo 5 — Contar o que você analisou
<a name="passo-5"></a>

Reporte uma contagem honesta de **arquivos-fonte analisados** e uma aproximação de
**linhas de código**. Exclua `node_modules/`, virtualenvs, `__pycache__/`, lockfiles,
`.git/`, assets gerados e a pasta da skill `.claude/`. A contagem aparece tanto no resumo
da Fase 1 quanto no cabeçalho do relatório, então precisa bater com a realidade.

**O que conta:** todo arquivo de código da(s) linguagem(ns) detectada(s) que você de fato
leu — incluindo marcadores de pacote (`__init__.py`) e scripts auxiliares (`seed.py`,
`manage.py`). Para evitar divergência, prefira derivar o número de uma listagem real do
disco (ex.: contar os arquivos `.py`/`.js` fora das pastas excluídas) em vez de estimar.
Se quiser, detalhe (ex.: *"15 arquivos `.py` (11 módulos + 4 `__init__`)"*) — o importante
é que o número total bata com o que existe no projeto.

<a name="cola"></a>
## Cola de detecção

```
Python/Flask     requirements.txt tem `flask`; `from flask import Flask`;
                 roteamento via @app.route / app.add_url_rule / Blueprint.
Python/Flask+ORM tem também `flask-sqlalchemy`; `class X(db.Model)`; SQLALCHEMY_DATABASE_URI.
Node/Express     package.json tem `express`; `require('express')` / `import express`;
                 roteamento via app.get/post/put/delete ou um express.Router().
Django           `django` nas deps; settings.py; urls.py; `models.Model`.
FastAPI          `fastapi`/`uvicorn`; `@app.get` com models Pydantic.
Banco de dados   sqlite3 / pg / mysql2 / mongoose / sqlalchemy nas deps;
                 CREATE TABLE ou classes de model definem o schema.
```

A saída desta fase alimenta a Fase 2 (quais arquivos auditar) e a Fase 3 (qual camada de
Models construir). Acerte a stack e tudo a jusante fica portável.
