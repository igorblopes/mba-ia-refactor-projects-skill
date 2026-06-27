# Referência: Catálogo de Anti-Patterns (Fase 2)

O conhecimento de detecção da skill. Cada entrada tem um **nome**, uma **severidade**,
**sinais de detecção** concretos (neutros de linguagem, mais exemplos em Python/Flask e
Node/Express), o **porquê importa** e um **ponteiro de correção** para o playbook de
refatoração. Percorra o código entrada por entrada; para cada ocorrência, registre um
`arquivo:linha` exato.

A severidade é atribuída pela escala abaixo (do enunciado do desafio). Na dúvida,
classifique pelo *impacto*, não por quão fácil é a correção.

| Severidade | Significado |
|---|---|
| **CRITICAL** | Falha de segurança ou de arquitetura: vaza segredos, permite injection/RCE, ou uma God Class misturando DB + lógica + roteamento. Quebra a correção ou a segurança. |
| **HIGH** | Forte violação de MVC/SOLID que mutila a manutenibilidade/testabilidade: lógica de negócio presa em controllers, forte acoplamento sem DI, estado global mutável. |
| **MEDIUM** | Problemas de padronização, duplicação ou performance moderada: queries N+1, validação ausente, erros engolidos, middleware mal usado. |
| **LOW** | Legibilidade: magic numbers, nomes ruins, código morto, prints de debug esquecidos. |

## Índice rápido

| # | Anti-pattern | Severidade |
|---|---|---|
| AP-01 | God Class / God Module (Classe Deus) | CRITICAL |
| AP-02 | Segredos / Credenciais hardcoded | CRITICAL |
| AP-03 | SQL Injection (queries montadas com string) | CRITICAL |
| AP-04 | Senha em texto plano ou hash fraco | CRITICAL |
| AP-05 | Endpoint de execução arbitrária de código/SQL | CRITICAL |
| AP-06 | Modo debug / erros verbosos em produção | HIGH |
| AP-07 | Fat Controller — lógica de negócio na camada HTTP | HIGH |
| AP-08 | Sem separação de responsabilidades (camadas misturadas) | HIGH |
| AP-09 | Estado global mutável / forte acoplamento, sem DI | HIGH |
| AP-10 | Efeitos colaterais misturados na lógica de negócio | HIGH |
| AP-11 | Callback hell / fluxo assíncrono sem estrutura | HIGH |
| AP-12 | Queries N+1 | MEDIUM |
| AP-13 | Validação de entrada ausente / inconsistente | MEDIUM |
| AP-14 | Código duplicado (violação de DRY) | MEDIUM |
| AP-15 | Erros engolidos / sem tratamento de erros central | MEDIUM |
| AP-16 | APIs deprecated / obsoletas | MEDIUM |
| AP-17 | Integridade de dados ignorada (registros órfãos, sem transação) | MEDIUM |
| AP-18 | Magic numbers & magic strings | LOW |
| AP-19 | Nomenclatura ruim | LOW |
| AP-20 | Código morto, imports não usados, prints de debug | LOW |

---

## CRITICAL

### AP-01 — God Class / God Module (Classe Deus)
**Sinais:** um único arquivo ou classe concentra várias responsabilidades não
relacionadas — conexão/init de DB **e** SQL **e** regras de negócio **e** roteamento **e**
formatação.
- Flask: um `models.py` que executa queries *e* valida *e* formata respostas; um `app.py`
  que também contém lógica de negócio.
- Express: uma classe chamada `AppManager` / `*Manager` cujos métodos fazem `initDb()`,
  `setupRoutes()`, processamento de pagamento e logging.
**Por quê:** impossível testar ou mudar em isolamento; cada edição arrisca tudo; a dívida
arquitetural mais cara de todas. → Playbook: *Quebrar o God object*.

### AP-02 — Segredos / Credenciais hardcoded
**Sinais:** senhas, API keys, tokens, `SECRET_KEY` literais no código.
- `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
- `paymentGatewayKey: "pk_live_..."`, `dbPass: "..."`, `email_password = 'senha123'`
- Um segredo devolvido na resposta de um endpoint (`"secret_key": ...` no `/health`).
**Por quê:** qualquer um com acesso ao repo é dono da produção; chaves no histórico do git
vazam para sempre. → Playbook: *Externalizar a configuração*.

### AP-03 — SQL Injection (queries montadas com string)
**Sinais:** SQL montado por concatenação/interpolação de string com entrada do usuário em
vez de binding de parâmetros.
- Python: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`,
  `"... WHERE email = '" + email + "'"`, f-strings dentro do `execute`.
- Node: `db.run("... WHERE id = " + id)`, SQL com template-literal e `${...}`.
**Por quê:** bypass de autenticação, roubo e destruição de dados. O bug crítico clássico.
→ Playbook: *Parametrizar toda query*.

### AP-04 — Senha em texto plano ou hash fraco
**Sinais:** senhas armazenadas como estão, ou com algoritmo quebrado.
- `INSERT INTO usuarios (... senha ...) VALUES ('" + senha + "')"` (texto plano).
- `hashlib.md5(pwd.encode())` / `sha1` (criptograficamente quebrados, sem salt).
- Um "hash" caseiro (`badCrypto` em loop de base64).
- Senhas retornadas em respostas da API / `to_dict()`.
**Por quê:** um vazamento do DB expõe a senha real de todo usuário; MD5/SHA1 são
reversíveis em escala. → Playbook: *Fazer hash de segredos corretamente*
(bcrypt/argon2/scrypt) e nunca serializá-los.

### AP-05 — Endpoint de execução arbitrária de código / SQL
**Sinais:** uma rota que executa SQL ou shell fornecido pelo chamador, ou uma operação
admin destrutiva sem autenticação.
- `/admin/query` que executa `request.json["sql"]` literalmente.
- `/admin/reset-db` apagando todas as tabelas sem autenticação.
**Por quê:** tomada remota do banco / servidor. → Playbook: *Remover ou proteger endpoints
perigosos* (apagar, ou colocar atrás de auth + uma allow-list fixa).

---

## HIGH

### AP-06 — Modo debug / erros verbosos em produção
**Sinais:** `DEBUG = True`, `app.run(debug=True)`, stack traces devolvidos ao cliente,
texto cru da exceção nas respostas (`return jsonify({"erro": str(e)})`).
**Por quê:** o modo debug expõe um console interativo e internals a atacantes; erros crus
vazam schema e caminhos. → Playbook: *Externalizar a configuração* + *Centralizar o
tratamento de erros*.

### AP-07 — Fat Controller — lógica de negócio na camada HTTP
**Sinais:** handlers de rota que calculam totais, decidem por regras de negócio, montam
relatórios ou falam direto com o DB em vez de delegar.
- Rota Flask fazendo conta de estoque, faixas de desconto ou montando um relatório inline.
- Handler Express aninhando chamadas ao DB e calculando faturamento dentro do callback da
  requisição.
**Por quê:** a violação central de MVC — a lógica não pode ser reutilizada nem testada sem
HTTP. → Playbook: *Extrair lógica de negócio para controllers/casos de uso*.

### AP-08 — Sem separação de responsabilidades (camadas misturadas)
**Sinais:** a mesma função lê a request, consulta o DB, aplica regras e formata a resposta;
SQL de acesso a dados morando em arquivos de rota; "models" que também validam e formatam.
**Por quê:** sem fronteira de camada não há lugar para testar, trocar ou reutilizar.
→ Playbook: *Introduzir camadas Model / Controller / View*.

### AP-09 — Estado global mutável / forte acoplamento, sem DI
**Sinais:** singletons mutáveis no nível de módulo; uma conexão global compartilhada;
variáveis de módulo `globalCache`, `totalRevenue` mutadas entre requisições; componentes
que dão `new` ou importam suas dependências diretamente em vez de recebê-las.
- `db_connection = None` global reutilizado em todo lugar.
- `let globalCache = {}` mutado pelos handlers.
**Por quê:** estado compartilhado oculto causa condições de corrida e torna tudo intestável
(você não consegue injetar um fake). → Playbook: *Injeção de dependência / passar os
colaboradores*.

### AP-10 — Efeitos colaterais misturados na lógica de negócio
**Sinais:** enviar email/SMS/push, gravar logs de auditoria ou imprimir notificações
inline dentro de um fluxo de criação/atualização.
- `print("ENVIANDO EMAIL: ...")` / `print("ENVIANDO SMS: ...")` dentro de `criar_pedido`.
- Um INSERT de log de auditoria enterrado dentro do callback de checkout.
**Por quê:** acopla regras de negócio aos canais de entrega; não dá para testar a regra sem
disparar o efeito colateral. → Playbook: *Isolar efeitos colaterais atrás de um service*.

### AP-11 — Callback hell / fluxo assíncrono sem estrutura
**Sinais (especialmente Node):** callbacks profundamente aninhados; coordenação manual via
"contador de pendências" de queries paralelas; `self = this` para driblar escopo; resposta
enviada de dentro de cinco callbacks aninhados.
**Por quê:** ilegível, propenso a erros, `res.send` duplicado, erros perdidos. → Playbook:
*Achatar o assíncrono com async/await + uma camada de dados*.

---

## MEDIUM

### AP-12 — Queries N+1
**Sinais:** uma query dentro de um loop sobre os resultados de outra query.
- Python: `for row in pedidos: cursor.execute("SELECT ... WHERE pedido_id = " + id)` e
  depois mais uma query por item.
- ORM: `for u in users: Task.query.filter_by(user_id=u.id)` dentro de um loop de relatório.
**Por quê:** transforma um relatório em centenas de idas e voltas; escala péssimo.
→ Playbook: *Substituir N+1 por um join / query em lote / eager load*.

### AP-13 — Validação de entrada ausente / inconsistente
**Sinais:** rotas que confiam em `request.get_json()` sem checar campos obrigatórios,
tipos ou faixas; conversão numérica/de data sem caminho de erro; validação presente em uma
rota mas ausente na irmã.
**Por quê:** dados-lixo, 500s e brechas de segurança. → Playbook: *Validar na fronteira*.

### AP-14 — Código duplicado (violação de DRY)
**Sinais:** o mesmo bloco copiado-colado — ex.: o idêntico `if` aninhado "esta task está
atrasada?" repetido em quatro lugares; mapeamento linha→dict duplicado; a mesma validação
inline por rota.
**Por quê:** as correções precisam ser aplicadas N vezes; elas divergem. → Playbook:
*Extrair um helper / método de model compartilhado*.

### AP-15 — Erros engolidos / sem tratamento de erros central
**Sinais:** `try/except` que devolve um 500 genérico em todo lugar; `except:` / `catch(err){}`
pelado que esconde o erro; cada handler reimplementando a formatação de erro; nenhum error
handler global / `@app.errorhandler`.
**Por quê:** as falhas somem silenciosamente ou vazam de forma inconsistente; não há um
único lugar para logar/formatar. → Playbook: *Centralizar tratamento de erros em
middleware*.

### AP-16 — APIs deprecated / obsoletas
Sinalize chamadas obsoletas **e nomeie o substituto moderno**. Reporte a versão que a
deprecou/removeu quando possível (você leu na Fase 1).

| Uso deprecated | Status | Substituto moderno |
|---|---|---|
| `datetime.datetime.utcnow()` | Deprecated no Python 3.12 | `datetime.now(datetime.UTC)` (com timezone) |
| `hashlib.md5` / `sha1` para senhas | Inseguro | `bcrypt` / `argon2` / `hashlib.scrypt` |
| Flask `@app.before_first_request` | Removido no Flask 2.3 | código de startup numa app factory / `with app.app_context()` |
| Flask `flask.json.jsonify` via caminhos legados de `flask.json` | Mudou | `from flask import jsonify` |
| Werkzeug `BaseRequest`/`BaseResponse` | Removido | `Request`/`Response` |
| Express `app.use(bodyParser.json())` (`body-parser` externo) | Redundante desde Express 4.16 | `app.use(express.json())` |
| Premissas de tratamento de erro do Express 4 | Mudaram no Express 5 | erros async repassados automaticamente; revise os handlers |
| `sqlite3.verbose()` deixado em prod | Só para debug | remova em produção |
| Node `crypto.createCipher` | Deprecated | `crypto.createCipheriv` |
| `var` / APIs de DB só por callback onde há promises | Legado | `const`/`let` + driver promisificado/`async` |
| SQLAlchemy `Query.get()` (`Model.query.get(id)`) | Legado no SQLAlchemy 2.0 | `db.session.get(Model, id)` |

**Por quê:** APIs deprecated quebram no upgrade, perdem correções de segurança e indicam
código sem manutenção. → Playbook: *Modernizar chamadas deprecated*.

### AP-17 — Integridade de dados ignorada (registros órfãos, sem transação)
**Sinais:** apagar uma linha-pai sem tratar os filhos (o código literalmente admite
*"matrículas e pagamentos ficaram sujos no banco"*); escritas de múltiplos comandos sem
transação/rollback, de modo que uma falha no meio deixa dados pela metade; estoque
decrementado sem atomicidade.
**Por quê:** corrupção silenciosa de dados. → Playbook: *Envolver escritas múltiplas numa
transação; cascatear ou bloquear deletes*.

---

## LOW

### AP-18 — Magic numbers & magic strings
**Sinais:** literais sem explicação — limiares de desconto `10000 / 5000 / 1000`,
prioridade `1..5`, strings de status `'pending'/'aprovado'` espalhadas como literais soltos,
portas, limites.
**Por quê:** a intenção fica oculta e o valor diverge entre cópias. → Playbook: *Nomear
constantes / enums*.

### AP-19 — Nomenclatura ruim
**Sinais:** nomes de uma letra ou crípticos para valores não triviais — `u, e, p, cid, cc`
para usuário/email/senha/curso/cartão; `d`, `t`, `c` para objetos de domínio.
**Por quê:** o leitor precisa decodificar o código. → Playbook: *Renomear para a intenção*.

### AP-20 — Código morto, imports não usados, prints de debug
**Sinais:** `import os, sys, json` nunca usados; blocos comentados; `print(...)` /
`console.log(...)` usados como logging; variáveis não usadas (`totalRevenue` importado,
nunca lido).
**Por quê:** ruído que esconde a lógica real e engana o leitor. → Playbook: *Apagar código
morto; usar um logger*.

---

## Como usar este catálogo

1. Para cada anti-pattern, varra o código atrás dos seus sinais.
2. Registre cada ocorrência concreta com `arquivo:linha`, um trecho citado, impacto e
   correção.
3. Um único arquivo pode bater em várias entradas (um God Module normalmente dispara
   AP-01, AP-03, AP-12, AP-15 ao mesmo tempo) — reporte cada achado separadamente, para
   que a contagem e o relatório sejam honestos.
4. Garanta que o conjunto final tenha **≥5 achados** e **≥1 CRITICAL ou HIGH** antes de
   apresentar (entradas legadas desse tipo sempre têm).
