================================
RELATÓRIO DE AUDITORIA ARQUITETURAL
================================
Projeto: ecommerce-api-legacy (na verdade um LMS com checkout)
Stack:   JavaScript (Node.js) + Express ^4.18.2 | SQLite (sqlite3 ^5.1.6, em memória)
Arquivos: 3 analisados (src/app.js, src/AppManager.js, src/utils.js) | ~180 linhas de código
Data:    2026-06-27

## Resumo
CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 3

## Achados

### [CRITICAL] God Class / God Module (AP-01)
Arquivo: src/AppManager.js:4-141
Descrição: A classe `AppManager` concentra responsabilidades não relacionadas: abre a
           conexão de DB no `constructor` (linha 7), cria schema + seeds em `initDb()`
           (10-23), e em `setupRoutes()` (25-138) faz roteamento HTTP + regras de negócio
           (decisão de pagamento, matrícula) + acesso a dados (SQL) + logging/auditoria —
           tudo num só lugar.
Impacto: Impossível testar ou alterar qualquer camada em isolamento; cada edição arrisca
         toda a aplicação. É a dívida arquitetural mais cara.
Recomendação: Quebrar o God object em camadas Model/Controller/View (Playbook: "Quebrar o
         God object").

### [CRITICAL] Segredos / Credenciais hardcoded (AP-02)
Arquivo: src/utils.js:1-7
Descrição: Credenciais de produção literais no código: `dbUser: "admin_master"`,
           `dbPass: "senha_super_secreta_prod_123"`,
           `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser`. A chave do gateway
           ainda é impressa no console em src/AppManager.js:45.
Impacto: Qualquer um com acesso ao repo (ou ao histórico do git) é dono da produção e da
         chave de pagamento real (`pk_live_`). Chaves no git vazam para sempre.
Recomendação: Externalizar config para variáveis de ambiente; nunca logar segredos
         (Playbook: "Externalizar a configuração").

### [CRITICAL] Hash de senha caseiro / quebrado + senha em texto plano (AP-04)
Arquivo: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Descrição: `badCrypto()` é um "hash" caseiro: concatena base64 num loop e trunca para 10
           chars — não-criptográfico, sem salt, com colisões enormes. O seed insere a
           senha em texto plano '123' (linha 18). No checkout, usuários sem senha recebem
           o default "123456" (linha 68).
Impacto: Um vazamento do DB expõe/quebra trivialmente as senhas; truncar para 10 chars
         torna o espaço de busca minúsculo. Contas comprometidas em massa.
Recomendação: Usar bcrypt/argon2/scrypt com salt; nunca aceitar senha default silenciosa;
         nunca serializar senha em respostas (Playbook: "Fazer hash de segredos
         corretamente").

### [CRITICAL] Endpoints administrativos/destrutivos sem autenticação (AP-05)
Arquivo: src/AppManager.js:80, src/AppManager.js:131-137
Descrição: `GET /api/admin/financial-report` expõe todo o faturamento, nomes e e-mails de
           alunos sem qualquer auth (linha 80). `DELETE /api/users/:id` permite que
           qualquer um apague qualquer usuário sem auth (linha 131).
Impacto: Exposição total de dados financeiros/PII e destruição de dados por qualquer
         chamador anônimo.
Recomendação: Proteger endpoints sensíveis atrás de autenticação/autorização (middleware
         de auth) (Playbook: "Remover ou proteger endpoints perigosos").

### [HIGH] Fat Controller — lógica de negócio na camada HTTP (AP-07)
Arquivo: src/AppManager.js:43-64, src/AppManager.js:80-129
Descrição: O handler de checkout decide aprovação de pagamento (`cc.startsWith("4")`), cria
           matrícula e pagamento inline. O handler de relatório monta todo o agregado
           financeiro dentro do callback HTTP.
Impacto: A regra de negócio não pode ser reutilizada nem testada sem HTTP; é a violação
         central de MVC.
Recomendação: Extrair para controllers/casos de uso (Playbook: "Extrair lógica de negócio
         para controllers").

### [HIGH] Sem separação de responsabilidades (AP-08)
Arquivo: src/AppManager.js:28-138
Descrição: Cada handler lê a request, executa SQL, aplica regras e formata a resposta na
           mesma função. Não há camada de dados nem de domínio.
Impacto: Sem fronteiras de camada não há onde testar, trocar ou reutilizar.
Recomendação: Introduzir camadas Model / Controller / View (Playbook: "Introduzir
         camadas").

### [HIGH] Estado global mutável / sem DI (AP-09)
Arquivo: src/utils.js:9-15, src/utils.js:10
Descrição: `globalCache = {}` e `totalRevenue = 0` são singletons mutáveis no nível de
           módulo; `logAndCache` muta `globalCache` entre requisições. A conexão de DB é
           compartilhada via `self = this` (src/AppManager.js:26) em vez de injetada.
Impacto: Estado compartilhado oculto causa condições de corrida e impede injetar fakes em
         testes.
Recomendação: Injeção de dependência; eliminar estado global mutável (Playbook: "Injeção
         de dependência").

### [HIGH] Efeitos colaterais misturados na lógica de negócio (AP-10)
Arquivo: src/AppManager.js:45, src/AppManager.js:57-59
Descrição: `console.log` do número do cartão (45), INSERT de `audit_logs` enterrado dentro
           do callback de checkout (57) e `logAndCache(...)` (59) misturados ao fluxo de
           matrícula.
Impacto: Acopla regras de negócio a canais de log/auditoria; impossível testar a regra sem
         disparar o efeito; vaza PAN do cartão no log.
Recomendação: Isolar efeitos colaterais atrás de um service (Playbook: "Isolar efeitos
         colaterais").

### [HIGH] Callback hell / fluxo assíncrono sem estrutura (AP-11)
Arquivo: src/AppManager.js:37-77, src/AppManager.js:86-127
Descrição: Checkout aninha callbacks 5 níveis (`res.send` em vários pontos); usa
           `self = this` (26). O relatório coordena queries paralelas com contadores
           manuais `coursesPending`/`enrPending` (86-122).
Impacto: Ilegível, propenso a `res` duplicado e erros perdidos.
Recomendação: Achatar com async/await + camada de dados promisificada (Playbook: "Achatar
         o assíncrono").

### [MEDIUM] Queries N+1 (AP-12)
Arquivo: src/AppManager.js:89-127
Descrição: Para cada curso consulta `enrollments`; para cada matrícula consulta `users` e
           `payments` — uma query por linha dentro de loops aninhados.
Impacto: Um relatório vira centenas de idas e voltas ao DB; escala péssimo.
Recomendação: Substituir por JOIN / query agregada (Playbook: "Substituir N+1 por um
         join").

### [MEDIUM] Validação de entrada ausente / inconsistente (AP-13)
Arquivo: src/AppManager.js:35, src/AppManager.js:131-132
Descrição: O checkout valida só `u,e,cid,cc` (35) — não valida formato de e-mail, formato
           do cartão nem a senha. `DELETE /api/users/:id` não valida se `id` é numérico.
Impacto: Dados-lixo, 500s e comportamento inconsistente.
Recomendação: Validar na fronteira (Playbook: "Validar na fronteira").

### [MEDIUM] Erros engolidos / sem tratamento central (AP-15)
Arquivo: src/AppManager.js:133-136, src/AppManager.js:92, src/AppManager.js:104-106
Descrição: O `DELETE` ignora `err` e sempre responde sucesso (133-135). Callbacks internos
           do relatório ignoram `err` (92, 104, 106). Cada handler reimplementa formatação
           de erro; não há error handler global.
Impacto: Falhas somem silenciosamente; sem ponto único para logar/formatar.
Recomendação: Middleware central de tratamento de erros (Playbook: "Centralizar tratamento
         de erros").

### [MEDIUM] APIs deprecated / só-callback (AP-16)
Arquivo: src/AppManager.js:1, src/AppManager.js:37-133
Descrição: `sqlite3.verbose()` deixado em produção (só para debug). Toda a camada de DB usa
           a API só-por-callback onde há equivalentes promisificados (util.promisify /
           node:sqlite).
Impacto: Verbose vaza detalhes em prod; APIs legadas dificultam manutenção e async limpo.
Recomendação: Remover `verbose()` em prod; promisificar o driver e usar async/await
         (Playbook: "Modernizar chamadas deprecated").
> Express está OK: já usa `express.json()` (não há body-parser externo). Não há uso de
> `var` nem de `crypto.createCipher`.

### [MEDIUM] Integridade de dados ignorada (AP-17)
Arquivo: src/AppManager.js:131-137, src/AppManager.js:50-57
Descrição: O `DELETE` de usuário deixa `enrollments`/`payments` órfãos — o próprio código
           admite: "as matrículas e pagamentos ficaram sujos no banco" (135). O checkout
           faz 3 INSERTs (enrollment, payment, audit) sem transação (50, 54, 57): uma
           falha no meio deixa dados pela metade.
Impacto: Corrupção silenciosa de dados.
Recomendação: Envolver escritas múltiplas em transação; cascatear/bloquear deletes
         (Playbook: "Transação + cascade").

### [LOW] Magic numbers & magic strings (AP-18)
Arquivo: src/AppManager.js:47, src/AppManager.js:68, src/utils.js:19
Descrição: Regra de pagamento `cc.startsWith("4")` e status "PAID"/"DENIED" como literais
           soltos (47); senha default "123456" (68); loop 10000 em `badCrypto` (19).
Impacto: Intenção oculta; valores divergem entre cópias.
Recomendação: Nomear constantes/enums (Playbook: "Nomear constantes").

### [LOW] Nomenclatura ruim (AP-19)
Arquivo: src/AppManager.js:29-33
Descrição: Variáveis de uma letra para objetos de domínio: `u, e, p, cid, cc` (usuário,
           e-mail, senha, courseId, cartão).
Impacto: O leitor precisa decodificar o código.
Recomendação: Renomear para a intenção (Playbook: "Renomear para a intenção").

### [LOW] Código morto / imports não usados / prints de debug (AP-20)
Arquivo: src/AppManager.js:2, src/utils.js:10, src/utils.js:25
Descrição: `totalRevenue` é importado em AppManager (2) e exportado (25), mas nunca lido
           nem atualizado. `console.log` usado como logging (utils 13, app 13,
           AppManager 45).
Impacto: Ruído que esconde a lógica real.
Recomendação: Apagar código morto; usar um logger (Playbook: "Apagar código morto").

================================
Total: 17 achados
================================

## Nota de verificação
- SQL Injection (AP-03): verificado e NÃO presente. Todas as queries usam binding de
  parâmetros (`?`). Não reportado para evitar achado falso (evidência acima de opinião).
- APIs deprecated: detectadas e reportadas em AP-16 (sqlite3.verbose, API só-callback).

## Baseline (contrato externo a preservar na Fase 3)
- POST /api/checkout (cartão começa com "4") -> 200 {"msg":"Sucesso","enrollment_id":N}
- POST /api/checkout (cartão não começa com "4") -> 400 texto "Pagamento recusado"
- POST /api/checkout (campos faltando)         -> 400 texto "Bad Request"
- POST /api/checkout (curso inexistente/inativo)-> 404 texto "Curso não encontrado"
- GET  /api/admin/financial-report -> 200 [{course, revenue, students:[{student, paid}]}]
- DELETE /api/users/:id            -> 200 texto de confirmação
