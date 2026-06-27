# Referência: Arquitetura MVC Alvo (Fase 3)

A arquitetura para a qual você refatora. MVC aqui significa uma arquitetura de backend em
camadas: uma camada HTTP fina (Views/Routes) delegando para a lógica de negócio
(Controllers), que usa acesso a dados (Models), com configuração e preocupações
transversais empurradas para as bordas. Seja pragmático — o objetivo são camadas
separadas e testáveis, não cerimônia.

## As camadas e sua responsabilidade única

```
            requisição HTTP
                 │
   ┌─────────────▼─────────────┐
   │  Views / Routes           │  mapeiam URL+método → uma função de controller.
   │  (camada HTTP fina)       │  parseiam params, chamam o controller, moldam a resposta HTTP.
   └─────────────┬─────────────┘  SEM regras de negócio, SEM SQL aqui.
                 │
   ┌─────────────▼─────────────┐
   │  Controllers              │  os casos de uso / lógica de negócio. orquestram models,
   │  (lógica de negócio)      │  aplicam regras, calculam, decidem. idealmente agnósticos de framework.
   └─────────────┬─────────────┘  SEM objetos request/response, SEM strings de SQL cru.
                 │
   ┌─────────────▼─────────────┐
   │  Models                   │  apenas acesso a dados. queries, persistência, o formato
   │  (dados)                  │  da entidade. um módulo por entidade de domínio.
   └─────────────┬─────────────┘  SEM HTTP, SEM política de negócio.
                 │
            Banco de dados

   Transversais (ficam ao lado das camadas):
   • config/        configuração & segredos, lidos do ambiente
   • middlewares/   tratamento de erros central, auth, logging, CORS
   • services/      efeitos colaterais isolados (email/SMS/push), gateways externos
   • app entry      composition root: monta config, conecta models→controllers→routes
```

### Models — *apenas dados*
- Um módulo por entidade (`produto_model.py`, `user_model.js`, …).
- Toda a persistência mora aqui: queries (parametrizadas!), inserts, updates, deletes.
- Retornam dados simples (dicts/objetos), não respostas HTTP.
- Sem política de negócio (um model busca um pedido; ele não decide faixas de desconto).

### Controllers — *lógica de negócio / casos de uso*
- Um controller por área de domínio (`produto_controller`, `pedido_controller`).
- Recebem entradas simples, aplicam regras (política de validação, totais, checagem de
  estoque, conta de relatório), chamam um ou mais models, retornam resultados simples ou
  lançam erros de domínio.
- Devem ser testáveis sem subir o framework web. Evite tocar `request`/`res` diretamente;
  deixe a View passar os dados parseados e moldar a resposta.

### Views / Routes — *camada HTTP fina*
- Mapeiam rotas para controllers (Flask Blueprints / `add_url_rule`; Express `Router`).
- Extraem path/query/body, entregam os valores parseados a um controller, traduzem o
  resultado (ou erro) do controller em um status code + JSON. Mantenha os handlers com
  poucas linhas.
- **Preserve as URLs, métodos e formatos de resposta originais** — isto é uma refatoração.

### config/ — *sem hardcoding*
- Leia segredos e parâmetros de variáveis de ambiente com defaults sensatos para dev
  (`os.environ.get("SECRET_KEY", ...)`, `process.env.PORT`).
- Nunca comite segredos reais. `DEBUG`/`PORT`/caminho do DB/chaves vêm todos daqui.

### middlewares/ — *preocupações transversais*
- Um tratador de erros central, para que controllers/models possam lançar e o middleware
  transforme num erro JSON consistente + status apropriado. Substitui o `try/except 500`
  por rota.
- Também é o lar dos guards de auth, do logging de requisição e da configuração de CORS.

### services/ — *efeitos colaterais isolados*
- Email/SMS/push, gateways de pagamento, log de auditoria. Os controllers chamam uma
  interface de service; o efeito colateral é mockável e não polui as regras de negócio.

### app entry — *composition root*
- O único lugar que sabe como tudo é conectado: carrega config, inicializa o DB/app,
  registra middlewares, monta as rotas. Fino e declarativo.

## Estrutura alvo canônica

Adapte os nomes às convenções da linguagem, mas mantenha as responsabilidades.

**Python / Flask**
```
src/
├── config/
│   └── settings.py          # config baseada em env, sem segredos no código
├── models/
│   ├── produto_model.py
│   ├── usuario_model.py
│   └── pedido_model.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── views/
│   └── routes.py            # Blueprint(s): URL → controller
├── middlewares/
│   └── error_handler.py
├── services/
│   └── notification_service.py
├── database.py              # factory de conexão/sessão
└── app.py                   # composition root / create_app()
```

**Node / Express**
```
src/
├── config/
│   └── index.js             # config baseada em process.env
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   └── enrollmentModel.js
├── controllers/
│   └── checkoutController.js
├── routes/                  # = a camada "views" para uma API
│   └── index.js
├── middlewares/
│   └── errorHandler.js
├── services/
│   └── paymentService.js
├── db.js                    # conexão + helpers promisificados
└── app.js                   # composition root
```

## Regras de bolso (use para posicionar qualquer pedaço de código)

1. **Fala com o banco de dados?** → Model.
2. **É uma regra de negócio / decisão / cálculo?** → Controller.
3. **Lê a request ou escreve a resposta / status?** → View/Route.
4. **É um segredo ou parâmetro de ambiente?** → config.
5. **É um efeito colateral externo (email, gateway, log)?** → service.
6. **É formatação de erro / auth / logging para toda requisição?** → middleware.

Se uma função responde "sim" a mais de uma dessas, ela está misturando camadas — separe.

## Quando o projeto já tem camadas (ex.: task-manager)

Não destrua uma estrutura que funciona. Melhore em direção às regras acima:
- Mova a lógica de negócio dos handlers de rota para controllers; as rotas ficam finas.
- Puxe a lógica duplicada (ex.: a checagem repetida de "atrasada") para um método de
  model/entidade ou um controller, e reutilize.
- Extraia config e segredos do `app.py` para `config/`.
- Adicione um tratador de erros central; substitua `except:` pelados/falhas silenciosas.
- Corrija vazamentos de responsabilidade nos models (ex.: um `to_dict()` que expõe o hash
  da senha).
- Só reestruture onde isso remove um achado real — preserve as partes que já obedecem as
  regras.

## Definição de pronto

- Cada camada tem uma responsabilidade; sem SQL nas rotas, sem regras de negócio nos
  models.
- Config e segredos externalizados; nada sensível no código.
- Um tratador de erros central; respostas de erro consistentes.
- Um ponto de entrada claro que apenas conecta as coisas.
- **Mesma API pública de antes**, e a app inicia e responde.
