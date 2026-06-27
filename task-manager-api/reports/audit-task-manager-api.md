================================
RELATÓRIO DE AUDITORIA ARQUITETURAL
================================
Projeto: task-manager-api
Stack:   Python 3 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1)
Arquivos: 15 .py analisados | ~660 linhas de código

## Resumo
CRITICAL: 2 | HIGH: 3 | MEDIUM: 6 | LOW: 3   (14 achados)

## Achados

### [CRITICAL] Segredos / Credenciais hardcoded (AP-02)
Arquivo: app.py:13, services/notification_service.py:9-10
Descrição: `SECRET_KEY` literal no código — `app.config['SECRET_KEY'] = 'super-secret-key-123'`.
           E credenciais de e-mail em texto plano no `NotificationService`:
           `self.email_user = 'taskmanager@gmail.com'` / `self.email_password = 'senha123'`.
Impacto: Qualquer pessoa com acesso ao repositório (ou ao histórico do git) é dona da chave
         de sessão e da conta de e-mail. Segredos commitados vazam para sempre.
Recomendação: Externalizar para variáveis de ambiente (`os.environ` / `python-dotenv`, já no
         manifesto). Playbook: "Externalizar a configuração".

### [CRITICAL] Hash de senha fraco (MD5) + senha serializada na resposta (AP-04)
Arquivo: models/user.py:29 e models/user.py:32 (MD5); models/user.py:21 (vazamento)
Descrição: Senhas com `hashlib.md5(pwd.encode()).hexdigest()` — sem salt, criptograficamente
           quebrado. Pior: `to_dict()` retorna `'password': self.password`, e esse dict é
           devolvido em `create_user` (routes/user_routes.py:85) e no `login`
           (routes/user_routes.py:209), expondo o hash da senha em respostas da API.
Impacto: Um vazamento do banco (ou simplesmente chamar `/login`) expõe os hashes; MD5 é
         reversível em escala via rainbow tables. Bypass trivial de autenticação.
Recomendação: Trocar para `bcrypt`/`argon2` (ou `hashlib.scrypt`) com salt e nunca serializar
         o campo `password`. Playbook: "Fazer hash de segredos corretamente".

### [HIGH] Modo debug ligado / servidor de desenvolvimento exposto (AP-06)
Arquivo: app.py:34
Descrição: `app.run(debug=True, host='0.0.0.0', port=5000)` — debug ativo e bind em todas as
           interfaces, fixo no código.
Impacto: O modo debug do Flask expõe o console interativo Werkzeug (execução de código remota)
         e stack traces a qualquer cliente na rede.
Recomendação: Ler `FLASK_DEBUG`/`HOST`/`PORT` do ambiente; debug `False` por padrão.
         Playbook: "Externalizar a configuração".

### [HIGH] Fat Controller — lógica de negócio na camada HTTP (AP-07)
Arquivo: routes/report_routes.py:12-101 (summary_report), routes/report_routes.py:103-155
         (user_report), routes/task_routes.py:273-299 (task_stats),
         routes/task_routes.py:240-271 (search_tasks)
Descrição: Os handlers de rota fazem todo o trabalho: 12+ queries, contagem manual por
           status/prioridade em loop, cálculo de `completion_rate`, montagem de relatórios e
           produtividade por usuário — tudo dentro do handler HTTP. Não existe camada de
           controllers/casos de uso.
Impacto: A regra de negócio não pode ser testada nem reutilizada sem subir o HTTP; cada
         relatório é um monólito de difícil manutenção.
Recomendação: Extrair para `controllers/` (TaskController, UserController, ReportController,
         CategoryController) e deixar as rotas finas. Playbook: "Extrair lógica de negócio
         para controllers".

### [HIGH] Sem separação de responsabilidades / serialização duplicada nas rotas (AP-08)
Arquivo: routes/task_routes.py:16-59 e routes/user_routes.py:162-181
Descrição: As rotas remontam o dicionário da task campo-a-campo manualmente em vez de usar
           `Task.to_dict()`, duplicando a lógica de serialização que já existe no model.
           Models também concentram validação + formatação; queries e regras moram nas rotas.
Impacto: Cada mudança de schema precisa ser replicada em vários lugares; as cópias divergem
         (o `get_user_tasks` já expõe campos diferentes do `to_dict`).
Recomendação: Centralizar serialização no model, mover acesso a dados para a camada de Models
         e a orquestração para controllers. Playbook: "Introduzir camadas Model/Controller/View".

### [MEDIUM] Queries N+1 (AP-12)
Arquivo: routes/task_routes.py:41-57, routes/report_routes.py:53-68, routes/report_routes.py:157-165
Descrição: No `get_tasks`, dentro do loop sobre as tasks chama-se `User.query.get(...)` e
           `Category.query.get(...)` por task. No `summary_report`, para cada usuário roda
           `Task.query.filter_by(user_id=u.id).all()`. No `get_categories`, um
           `Task.query.filter_by(...).count()` por categoria.
Impacto: Um endpoint vira dezenas/centenas de idas ao banco; escala péssimo conforme cresce a
         base.
Recomendação: Usar `joinedload`/eager loading ou uma query agregada (GROUP BY).
         Playbook: "Substituir N+1 por join/eager load".

### [MEDIUM] Código duplicado — bloco "task atrasada?" copiado 7x (AP-14)
Arquivo: models/task.py:50-60, routes/task_routes.py:30-39, routes/task_routes.py:71-80,
         routes/task_routes.py:284-287, routes/user_routes.py:171-180,
         routes/report_routes.py:34-37, routes/report_routes.py:132-135
Descrição: O mesmo `if due_date ... if status != 'done' and != 'cancelled'` aparece 7 vezes.
           `completion_rate` também é recalculado inline em 3 lugares.
Impacto: Uma correção de regra (ex.: novo status final) precisa ser feita em 7 pontos; eles
         vão divergir.
Recomendação: Usar o método único `Task.is_overdue()` (já existe) em todos os lugares e um
         helper de completion_rate. Playbook: "Extrair helper/método de model compartilhado".

### [MEDIUM] Erros engolidos / sem tratamento de erro central (AP-15)
Arquivo: routes/task_routes.py:62, routes/task_routes.py:236, routes/user_routes.py:130,
         routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207,
         routes/report_routes.py:221
Descrição: Vários `except:`/`except Exception` pelados que devolvem um 500 genérico e
           descartam o erro. Não há nenhum `@app.errorhandler` global.
Impacto: Falhas somem silenciosamente; cada handler reimplementa formatação de erro de forma
         inconsistente; impossível logar de forma central.
Recomendação: Middleware/`errorhandler` central + exceções de domínio. Playbook: "Centralizar
         tratamento de erros".

### [MEDIUM] APIs deprecated / obsoletas (AP-16)
Arquivo: `datetime.utcnow()` em models/task.py:15-16,52, models/user.py:14, app.py:24,
         routes/task_routes.py:31,285, routes/report_routes.py:35,42,45,71,133, etc.;
         `Model.query.get()` em routes/task_routes.py:67,117,158,227,
         routes/user_routes.py:29,94,135,155, routes/report_routes.py:105,192,213;
         `hashlib.md5` em models/user.py:29,32.
Descrição: `datetime.utcnow()` está deprecated no Python 3.12 -> usar `datetime.now(timezone.utc)`.
           `Model.query.get(id)` é legado no SQLAlchemy 2.0 -> `db.session.get(Model, id)`.
           `hashlib.md5` para senha é obsoleto/inseguro -> `bcrypt`/`argon2`.
Impacto: Quebram em upgrades, perdem correções de segurança e sinalizam código sem manutenção.
Recomendação: Modernizar as três famílias de chamada. Playbook: "Modernizar chamadas deprecated".

### [MEDIUM] Validação ausente / inconsistente (AP-13)
Arquivo: routes/task_routes.py:261 e routes/task_routes.py:264 (`int(priority)`/`int(user_id)`
         sem try/except -> 500 com input não-numérico); routes/report_routes.py:167-209
         (create/update_category não validam cor nem tamanho); helper utils/helpers.py:57-108
         (`process_task_data`) existe mas nunca é usado.
Descrição: Validação espalhada e inconsistente: rotas de task validam tamanho/faixa, mas
           categoria não valida nada; conversões numéricas em `search` sem caminho de erro;
           um validador central existe mas está morto.
Impacto: Dados-lixo entram, e querystrings inválidas derrubam a rota com 500.
Recomendação: Validar na fronteira (marshmallow, já no manifesto) de forma uniforme.
         Playbook: "Validar na fronteira".

### [MEDIUM] Integridade de dados — deletes sem cascata/transação (AP-17)
Arquivo: routes/report_routes.py:211-223 (delete_category), relações em models/task.py:20-21
Descrição: `delete_category` apaga a categoria sem tratar as tasks que a referenciam, deixando
           `category_id` órfão apontando para id inexistente. As `relationship` não definem
           `cascade`/`ondelete`. (Em contraste, `delete_user` apaga tasks manualmente —
           comportamento inconsistente.)
Impacto: FKs órfãs e corrupção silenciosa; comportamento de delete depende da rota.
Recomendação: Definir cascata/`ondelete` no model ou bloquear o delete quando há filhos,
         dentro de transação. Playbook: "Cascatear ou bloquear deletes".

### [LOW] Magic numbers & magic strings (AP-18)
Arquivo: strings de status em routes/task_routes.py:110,177, models/task.py:39, etc.;
         prioridade `1..5` em routes/task_routes.py:113,182; tamanhos `3`/`200`/`4` em
         routes/task_routes.py:96-100, routes/user_routes.py:64
Descrição: Literais de status/role/limites espalhados como strings/números soltos. Já existem
           constantes (`VALID_STATUSES`, `VALID_ROLES`, `MIN_TITLE_LENGTH`...) em
           utils/helpers.py:110-116, mas não são usadas.
Impacto: Intenção oculta; valores divergem entre cópias.
Recomendação: Centralizar em constantes/enums e referenciá-las. Playbook: "Nomear constantes".

### [LOW] Nomenclatura ruim (AP-19)
Arquivo: routes/task_routes.py:16 (`for t in tasks`), routes/report_routes.py:24-28 (`p1..p5`),
         routes/report_routes.py:55 (`for u`), seed.py:78 (`for td`), models/category.py:14 (`d = {...}`)
Descrição: Variáveis de uma letra para objetos de domínio (`t`, `u`, `c`, `td`, `cat`, `p1..p5`).
Impacto: O leitor precisa decodificar; aumenta o risco de erro em edições.
Recomendação: Renomear para a intenção (`task`, `user`, `category`). Playbook: "Renomear para
         a intenção".

### [LOW] Código morto, imports não usados e prints de debug (AP-20)
Arquivo: app.py:7 (`os, sys, json` não usados); routes/task_routes.py:7 (`json, os, sys, time`
         não usados); routes/user_routes.py:6 (`hashlib, json` não usados);
         routes/report_routes.py:8 (`json`, e `format_date` importado/não usado);
         services/notification_service.py (módulo inteiro nunca importado);
         utils/helpers.py:31-108 (várias funções mortas); `print(...)` como log em
         routes/task_routes.py:149,153,219, routes/user_routes.py:83,89,147
Descrição: Imports não usados em quase todo arquivo, um service inteiro morto, helpers nunca
           chamados e `print()` usado como logging.
Impacto: Ruído que esconde a lógica real e engana o leitor.
Recomendação: Remover código morto; usar o módulo `logging`. Playbook: "Apagar código morto;
         usar um logger".

================================
Total: 14 achados
================================

Nota: o `search_tasks` usa `.like(f'%{query}%')`, que NÃO é SQL injection — o SQLAlchemy faz
o binding do parâmetro. Por isso não foi marcado como AP-03.
