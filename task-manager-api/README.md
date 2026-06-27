# task-manager-api

API de Task Manager em Python/Flask, refatorada para uma arquitetura **MVC em camadas**
(Model / Controller / View) com configuração externalizada, tratamento de erros central e
segredos fora do código.

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional — ajuste SECRET_KEY e demais variáveis
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`)
com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso
contrário os endpoints vão retornar listas vazias.

Configuração (debug, host, porta, caminho do banco, SMTP, `SECRET_KEY`) é lida de variáveis
de ambiente — veja `.env.example`. Por padrão o debug fica **desligado**; para desenvolvimento
com reload, exporte `FLASK_DEBUG=true`.

## Estrutura

```
app.py                  # ponto de entrada — cria a app via factory
seed.py                 # popula o banco
src/
├── config/             # configuração lida do ambiente (sem segredos hardcoded)
│   └── settings.py
├── models/             # acesso a dados — um módulo por entidade
│   ├── task.py
│   ├── user.py
│   └── category.py
├── controllers/        # lógica de negócio / casos de uso
│   ├── task_controller.py
│   ├── user_controller.py
│   ├── category_controller.py
│   └── report_controller.py
├── views/              # camada HTTP fina — blueprints mapeiam URL → controller
│   ├── health_routes.py
│   ├── task_routes.py
│   ├── user_routes.py
│   ├── category_routes.py
│   └── report_routes.py
├── middlewares/        # tratamento de erros central
│   └── error_handler.py
├── services/           # efeitos colaterais isolados (e-mail)
│   └── notification_service.py
├── database.py         # instância do SQLAlchemy
├── constants.py        # constantes de domínio
├── metrics.py          # cálculos compartilhados
├── time_utils.py       # utilitário de tempo (UTC)
└── app.py              # composition root (create_app)
```

## Endpoints

`GET /` · `GET /health` ·
`GET/POST /tasks` · `GET/PUT/DELETE /tasks/<id>` · `GET /tasks/search` · `GET /tasks/stats` ·
`GET/POST /users` · `GET/PUT/DELETE /users/<id>` · `GET /users/<id>/tasks` · `POST /login` ·
`GET/POST /categories` · `PUT/DELETE /categories/<id>` ·
`GET /reports/summary` · `GET /reports/user/<id>`
