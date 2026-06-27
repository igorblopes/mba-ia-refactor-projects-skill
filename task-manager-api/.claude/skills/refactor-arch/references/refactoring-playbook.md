# Referência: Playbook de Refatoração (Fase 3)

Receitas concretas antes/depois — uma família por anti-pattern. Aplique a receita que zera
cada achado do relatório. Os exemplos são em Python/Flask e Node/Express; o *formato* da
transformação é o mesmo em qualquer linguagem. Sempre preserve o comportamento externo:
mesmas rotas, mesmos métodos, mesmo JSON de resposta.

## Índice

1. [Externalizar a configuração](#r1) (AP-02, AP-06)
2. [Parametrizar toda query](#r2) (AP-03)
3. [Fazer hash de segredos corretamente](#r3) (AP-04)
4. [Remover ou proteger endpoints perigosos](#r4) (AP-05)
5. [Quebrar o God object em camadas](#r5) (AP-01, AP-08)
6. [Extrair lógica de negócio para controllers](#r6) (AP-07)
7. [Injeção de dependência no lugar de estado global](#r7) (AP-09)
8. [Isolar efeitos colaterais atrás de um service](#r8) (AP-10)
9. [Achatar o assíncrono com async/await](#r9) (AP-11)
10. [Substituir N+1 por um join / query em lote](#r10) (AP-12)
11. [Validar na fronteira](#r11) (AP-13)
12. [Centralizar o tratamento de erros](#r12) (AP-15)
13. [Modernizar APIs deprecated](#r13) (AP-16)
14. [Envolver escritas múltiplas numa transação](#r14) (AP-17)
15. [Nomear valores mágicos; matar código morto](#r15) (AP-18, AP-20)
16. [Extrair helper compartilhado (DRY)](#r16) (AP-14)
17. [Renomear para a intenção](#r17) (AP-19)

---

<a name="r1"></a>
## 1. Externalizar a configuração (AP-02, AP-06)
Tire segredos e parâmetros de ambiente do código para variáveis de ambiente, com defaults
de dev.

**Antes (Flask)**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**Depois — `config/settings.py`**
```python
import os
class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
settings = Settings()
```
**Antes (Node)** — `utils.js` com literais `dbPass`, `paymentGatewayKey`.
**Depois — `config/index.js`**
```js
module.exports = {
  port: process.env.PORT || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  db: { user: process.env.DB_USER, pass: process.env.DB_PASS },
};
```
Nunca devolva segredos por um endpoint. Forneça um `.env.example` documentando as chaves.

<a name="r2"></a>
## 2. Parametrizar toda query (AP-03)
Faça binding de parâmetros; nunca concatene entrada do usuário no SQL.

**Antes**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```
**Filtros dinâmicos** — monte a cláusula com placeholders, junte os params numa lista:
```python
clauses, params = ["1=1"], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)"); params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    clauses.append("categoria = ?"); params.append(categoria)
cursor.execute("SELECT * FROM produtos WHERE " + " AND ".join(clauses), params)
```
Node também usa placeholders `?`: `db.get("SELECT * FROM users WHERE email = ?", [email], cb)`.

<a name="r3"></a>
## 3. Fazer hash de segredos corretamente (AP-04)
Troque texto plano / MD5 / hash caseiro por um hash de senha de verdade, e pare de
serializar o hash.

**Antes**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()   # quebrado
# to_dict() retorna 'password': self.password           # vaza o hash
```
**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)
# to_dict() NÃO deve incluir password
```
Node: `const bcrypt = require("bcrypt"); const hash = await bcrypt.hash(pwd, 10);`
(se adicionar dependência for indesejável, use no mínimo `crypto.scrypt` com um salt —
nunca o loop de base64 do `badCrypto`).

<a name="r4"></a>
## 4. Remover ou proteger endpoints perigosos (AP-05)
Apague rotas de SQL-arbitrário/wipe-admin, ou coloque-as atrás de autenticação e uma
allow-list fixa.

**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])   # RCE no banco
```
**Depois:** remova o endpoint por completo. Se uma operação de manutenção for realmente
necessária, exponha uma operação nomeada *específica* atrás de auth (ex.: um `reset`
autenticado que chama um método de model bem definido) — nunca SQL cru vindo da request.

<a name="r5"></a>
## 5. Quebrar o God object em camadas (AP-01, AP-08)
Fatie o mega-arquivo/classe pelas regras de camada: SQL → models, regras → controllers,
HTTP → rotas.

**Antes** — `AppManager` faz `initDb()`, `setupRoutes()`, pagamento e logging numa única
classe; ou um `models.py` com SQL + validação + formatação para cada entidade.

**Depois** — separe por responsabilidade e entidade:
```
models/userModel.js        # SQL de usuários
models/courseModel.js      # SQL de cursos
controllers/checkoutController.js  # o caso de uso de checkout
routes/index.js            # POST /api/checkout → controller
db.js                      # conexão + run/get/all promisificados
```
Cada novo módulo importa só o que precisa. O ponto de entrada conecta tudo.

<a name="r6"></a>
## 6. Extrair lógica de negócio para controllers (AP-07)
Tire cálculos, regras de decisão e orquestração de DB de dentro do handler HTTP.

**Antes (rota/handler Flask)**
```python
def relatorio_vendas():
    # totais, faixas de desconto (10000/5000/1000), ticket médio — tudo inline + SQL
```
**Depois**
```python
# controllers/relatorio_controller.py
def gerar_relatorio_vendas():
    stats = pedido_model.aggregate_sales()        # dados vindos do model
    desconto = _discount_for(stats["faturamento"]) # regra de negócio, testável em unidade
    return {**stats, "desconto_aplicavel": round(desconto, 2), ...}

# views/routes.py  (fino)
@bp.route("/relatorios/vendas")
def relatorio_vendas():
    return jsonify({"dados": relatorio_controller.gerar_relatorio_vendas(), "sucesso": True})
```
A rota agora tem poucas linhas; a regra mora onde pode ser testada sem HTTP.

<a name="r7"></a>
## 7. Injeção de dependência no lugar de estado global (AP-09)
Passe os colaboradores em vez de recorrer a globais mutáveis no nível de módulo.

**Antes**
```python
db_connection = None              # global de módulo, compartilhado em todo lugar
def get_db():
    global db_connection
    ...
```
```js
let globalCache = {};             // mutado entre requisições
```
**Depois:** crie a conexão/sessão no composition root e injete-a; controllers recebem seu
model, models recebem a conexão. Substitua o `globalCache` ad-hoc por um cache/service
passado. Isso torna cada unidade substituível por um fake nos testes.

<a name="r8"></a>
## 8. Isolar efeitos colaterais atrás de um service (AP-10)
Mova email/SMS/push/auditoria para fora do fluxo de negócio.

**Antes**
```python
print("ENVIANDO EMAIL: Pedido criado ...")
print("ENVIANDO SMS: ...")          # dentro de criar_pedido
```
**Depois**
```python
# services/notification_service.py
class NotificationService:
    def order_created(self, pedido_id, usuario_id): ...  # email/SMS/push moram aqui

# o controller chama o service; a regra não conhece o canal
notifications.order_created(resultado["pedido_id"], usuario_id)
```
Agora a regra de criação de pedido pode ser testada sem disparar notificações, e os canais
podem mudar sem tocar na lógica de negócio.

<a name="r9"></a>
## 9. Achatar o assíncrono com async/await (AP-11)
Troque callbacks aninhados e "contadores de pendência" manuais por chamadas com await numa
camada de dados.

**Antes (Express)** — cinco callbacks `db.run/get` aninhados, `self = this`, `res` enviado
do mais interno; um contador `coursesPending--` coordenando queries paralelas.
**Depois** — promisifique o driver uma vez, depois:
```js
// db.js
const run = (sql, p=[]) => new Promise((res, rej) =>
  db.run(sql, p, function (e) { e ? rej(e) : res(this); }));
const get = (sql, p=[]) => new Promise((res, rej) =>
  db.get(sql, p, (e, r) => e ? rej(e) : res(r)));
const all = (sql, p=[]) => new Promise((res, rej) =>
  db.all(sql, p, (e, r) => e ? rej(e) : res(r)));

// controller
async function checkout(input) {
  const course = await courseModel.findActive(input.courseId);
  if (!course) throw new NotFound("Curso não encontrado");
  const user = await userModel.findOrCreate(input);
  const enrollment = await enrollmentModel.create(user.id, course.id);
  await paymentModel.create(enrollment.id, course.price, status);
  return { enrollment_id: enrollment.id };
}
```
Linear, propaga erros, sem envio duplicado.

<a name="r10"></a>
## 10. Substituir N+1 por um join / query em lote (AP-12)
Colapse queries por linha numa única query baseada em conjunto.

**Antes**
```python
for row in pedidos:                       # 1 query
    itens = q("SELECT * FROM itens_pedido WHERE pedido_id = " + id)   # N
    for item in itens:
        nome = q("SELECT nome FROM produtos WHERE id = " + pid)       # N*M
```
**Depois** — um JOIN, depois agrupe em memória:
```python
rows = cursor.execute("""
    SELECT p.id AS pedido_id, ip.produto_id, pr.nome, ip.quantidade, ip.preco_unitario
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
""").fetchall()
# agrupe as linhas por pedido_id no mesmo formato de resposta
```
Versão ORM: use um join/eager-load (`joinedload`) ou uma única query agregada em vez de
fazer loop de `Model.query.get(...)` por linha.

<a name="r11"></a>
## 11. Validar na fronteira (AP-13)
Valide campos obrigatórios, tipos e faixas uma vez, de forma consistente, antes da lógica
de negócio.

**Antes** — `if "nome" not in dados` ad-hoc repetido por rota, algumas rotas sem nenhum.
**Depois** — um pequeno validador (ou uma lib de schema como marshmallow/pydantic/zod):
```python
def validate_produto(data):
    errors = []
    if not data.get("nome") or not (2 <= len(data["nome"]) <= 200): errors.append("nome inválido")
    if data.get("preco", -1) < 0: errors.append("preço inválido")
    if errors: raise ValidationError(errors)
    return {"nome": data["nome"], "preco": data["preco"], ...}
```
A rota chama o validador, o controller confia na entrada limpa.

<a name="r12"></a>
## 12. Centralizar o tratamento de erros (AP-15)
Um handler transforma erros lançados em JSON consistente; as rotas param de reimplementar
500s.

**Antes** — cada handler envolto em `try/except` devolvendo `jsonify({"erro": str(e)})`,
`except:` pelado engolindo falhas.
**Depois (Flask)**
```python
# middlewares/error_handler.py
class AppError(Exception):
    def __init__(self, message, status=400): self.message, self.status = message, status
def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app(e): return jsonify({"erro": e.message, "sucesso": False}), e.status
    @app.errorhandler(404)
    def _nf(e): return jsonify({"erro": "Não encontrado"}), 404
    @app.errorhandler(Exception)
    def _500(e): app.logger.exception(e); return jsonify({"erro": "Erro interno"}), 500
```
**Depois (Express)**
```js
function errorHandler(err, req, res, next) {
  const status = err.status || 500;
  if (status === 500) console.error(err);
  res.status(status).json({ error: err.publicMessage || "Erro interno" });
}
app.use(errorHandler); // montado por último
```
Controllers/models apenas `raise`/`throw`; o middleware formata e loga.

<a name="r13"></a>
## 13. Modernizar APIs deprecated (AP-16)
Troque chamadas obsoletas pelo equivalente moderno (veja a tabela do catálogo para a lista
completa).

```python
# Antes                                   # Depois
datetime.datetime.utcnow()                datetime.now(datetime.UTC)
Model.query.get(id)                       db.session.get(Model, id)
hashlib.md5(pwd.encode()).hexdigest()     generate_password_hash(pwd)
```
```js
// Antes                                  // Depois
app.use(bodyParser.json())                app.use(express.json())
sqlite3.verbose()  // em prod             // remova
```

<a name="r14"></a>
## 14. Envolver escritas múltiplas numa transação (AP-17)
Torne escritas de múltiplos comandos atômicas e trate os filhos no delete.

**Antes** — a criação de pedido insere pedido, itens e decrementa estoque sem transação;
apagar um usuário deixa "matrículas e pagamentos sujos no banco".
**Depois**
```python
try:
    cursor.execute("BEGIN")
    pedido_id = pedido_model.insert(usuario_id, total)
    for item in itens: item_model.insert(pedido_id, item); produto_model.decrement_stock(...)
    db.commit()
except Exception:
    db.rollback(); raise
```
No delete, cascateie ou bloqueie: remova as linhas dependentes na mesma transação, ou
rejeite o delete enquanto houver filhos.

<a name="r15"></a>
## 15. Nomear valores mágicos; matar código morto (AP-18, AP-20)
Promova literais soltos a constantes/enums nomeados; apague imports não usados, blocos
comentados e debug com `print`/`console.log` (use um logger).

**Antes**
```python
if faturamento > 10000: desconto = faturamento * 0.1
import os, sys, json   # não usados
print("Listando produtos")
```
**Depois**
```python
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
def _discount_for(total):
    for threshold, rate in DISCOUNT_TIERS:
        if total > threshold: return total * rate
    return 0
# remova imports não usados; troque os prints por logging.getLogger(__name__).info(...)
```

<a name="r16"></a>
## 16. Extrair helper compartilhado (DRY) (AP-14)
Promova um bloco copiado-colado a um único helper ou método de entidade e reutilize-o.

**Antes** — a mesma checagem de "atrasada" repetida em várias rotas:
```python
# em get_tasks, get_task, get_user_tasks, summary_report... (o mesmo if aninhado 4x)
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            overdue = True
```
**Depois** — uma única fonte de verdade no model, reutilizada em todo lugar:
```python
# models/task.py
def is_overdue(self):
    return bool(self.due_date and self.due_date < datetime.utcnow()
                and self.status not in ('done', 'cancelled'))

# nas rotas/controllers
data["overdue"] = task.is_overdue()
```
Uma correção, um único lugar; o comportamento não diverge mais entre as cópias. O mesmo
vale para o mapeamento linha→dict duplicado (centralize num `to_dict()`/serializer) e para
validações repetidas (extraia um validador — veja a receita 11).

<a name="r17"></a>
## 17. Renomear para a intenção (AP-19)
Troque nomes crípticos por nomes que revelam a intenção; o leitor deixa de precisar
decodificar o código.

**Antes (Express)**
```js
let u = req.body.usr;    let e = req.body.eml;   let p = req.body.pwd;
let cid = req.body.c_id;  let cc = req.body.card;
```
**Depois**
```js
const { usr: nome, eml: email, pwd: senha, c_id: cursoId, card: cartao } = req.body;
```
Vale também para `cursor`/`cursor2`/`cursor3` (use nomes por finalidade, ex.: `cur_itens`,
`cur_produto`) e para `p1..p5` num relatório (use `prioridade_critica`, `prioridade_alta`,
…). Nomes claros reduzem a carga de leitura e os erros.

---

## Sequência de uma refatoração

1. **Baseline:** suba a app e registre quais endpoints respondem (o "antes").
2. **Esqueleto** das pastas MVC (receita 5) e `config/` (receita 1).
3. **Mova o acesso a dados** para os models, parametrizando no caminho (receita 2).
4. **Mova a lógica de negócio** para os controllers; isole efeitos colaterais e validação
   (receitas 6, 8, 11); corrija N+1 e transações (receitas 10, 14).
5. **Afine as rotas** e conecte-as aos controllers; adicione o middleware de erro
   (receita 12).
6. **Passe de segurança & modernização:** segredos, hash de senha, endpoints perigosos,
   APIs deprecated (receitas 1, 3, 4, 13).
7. **Limpeza:** constantes e código morto (receita 15).
8. **Validação:** suba de novo, sonde os mesmos endpoints, confirme paridade com a
   baseline.
