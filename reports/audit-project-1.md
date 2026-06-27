================================
RELATÓRIO DE AUDITORIA ARQUITETURAL
================================
Projeto:  code-smells-project
Stack:    Python 3 + Flask 3.1.1 (flask-cors 5.0.1, sqlite3)
Arquivos: 4 analisados | ~784 linhas de código

## Resumo
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 3

## Achados

### [CRITICAL] SQL Injection generalizado (AP-03)
Arquivo: models.py:28, 47-49, 57-60, 68, 92, 109-111, 126-128, 140, 148-151, 155-166, 174, 188, 192, 220, 224, 280, 289-297
Descrição: Praticamente toda query é montada por concatenação de string com entrada do usuário.
           Ex.: cursor.execute("SELECT * FROM produtos WHERE id = " + str(id)) (models.py:28);
           login com "... WHERE email = '" + email + "' AND senha = '" + senha + "'" (models.py:109-111);
           busca com LIKE '%" + termo + "%' (models.py:291).
Impacto: Bypass de autenticação (' OR '1'='1' --), exfiltração e destruição total do banco.
         Toda entidade é explorável.
Recomendação: Parametrizar 100% das queries com placeholders ? e tuplas de parâmetros.
              Playbook "Parametrizar toda query".

### [CRITICAL] Endpoint de execução arbitrária de SQL + reset sem auth (AP-05)
Arquivo: app.py:59-78 (/admin/query), app.py:47-57 (/admin/reset-db)
Descrição: /admin/query executa request.json["sql"] literalmente (cursor.execute(query));
           /admin/reset-db apaga itens_pedido, pedidos, produtos, usuarios — ambos sem autenticação.
Impacto: Tomada remota completa do banco e wipe destrutivo por qualquer cliente anônimo
         (RCE-equivalente sobre os dados).
Recomendação: Remover ambos os endpoints; se um reset for necessário em dev, colocá-lo
              atrás de auth + flag de ambiente. Playbook "Remover ou proteger endpoints perigosos".

### [CRITICAL] Senhas em texto plano e expostas na API (AP-04)
Arquivo: database.py:76-78, models.py:126-128, models.py:109-111, models.py:83, models.py:99
Descrição: Seed grava senhas literais ("admin123", "123456"); criar_usuario faz
           INSERT ... VALUES ('... senha ...') em texto plano; login compara texto plano;
           e get_todos_usuarios/get_usuario_por_id retornam o campo senha na resposta JSON.
Impacto: Um vazamento expõe a senha real de todos; pior, a API já entrega as senhas em /usuarios.
Recomendação: Hash com bcrypt/argon2/scrypt na escrita, comparar hash no login e nunca
              serializar senha. Playbook "Fazer hash de segredos corretamente".

### [CRITICAL] Segredos hardcoded e vazados na resposta (AP-02)
Arquivo: app.py:7, controllers.py:289
Descrição: SECRET_KEY = "minha-chave-super-secreta-123" fixo no código e o mesmo segredo é
           devolvido no payload de /health ("secret_key": "minha-chave-super-secreta-123").
Impacto: Qualquer um com acesso ao repo (ou ao /health) controla a sessão/segurança da app;
         segredo fica eterno no histórico do git.
Recomendação: Ler de variável de ambiente (os.environ), remover do /health.
              Playbook "Externalizar a configuração".

### [CRITICAL] God Module — models.py mistura dados + regra + formatação (AP-01)
Arquivo: models.py:1-315 (núcleo: criar_pedido 133-169, relatorio_vendas 235-273)
Descrição: O models.py faz acesso a dados E regra de negócio (cálculo de total/estoque em
           criar_pedido; faixas de desconto em relatorio_vendas:256-262) E formatação de
           resposta (montagem dos dicts). É uma camada de "model" que decide o negócio inteiro.
Impacto: Impossível testar ou alterar regra sem tocar acesso a dados; cada edição arrisca tudo.
Recomendação: Separar acesso a dados (models) de casos de uso (controllers).
              Playbook "Quebrar o God object" + "Introduzir camadas".

### [HIGH] Modo debug ligado em produção + exceções cruas ao cliente (AP-06)
Arquivo: app.py:8, app.py:88, e return jsonify({"erro": str(e)}) em todos os handlers
         (ex.: controllers.py:12, 62, 96, 126, 165, 186, 220, 255, 292)
Descrição: DEBUG = True e app.run(debug=True); toda exceção retorna str(e) ao cliente.
Impacto: Console interativo do Werkzeug exposto a atacantes; mensagens cruas vazam schema e caminhos.
Recomendação: DEBUG via ambiente (default off); resposta de erro genérica.
              Playbook "Externalizar config" + "Centralizar tratamento de erros".

### [HIGH] Efeitos colaterais embutidos na lógica (AP-10)
Arquivo: controllers.py:208-210, controllers.py:247-250
Descrição: criar_pedido dispara print("ENVIANDO EMAIL/SMS/PUSH ...") e atualizar_status_pedido
           imprime notificações de aprovação/cancelamento inline no fluxo HTTP.
Impacto: Acopla regra de negócio aos canais de entrega; impossível testar a regra sem disparar o efeito.
Recomendação: Isolar atrás de um service de notificação (interface), chamado pelo controller.
              Playbook "Isolar efeitos colaterais".

### [HIGH] Sem separação real de responsabilidades (AP-08)
Arquivo: controllers.py:264-290 (health_check acessa o DB direto), app.py:47-78 (lógica/DB inline no entrypoint)
Descrição: health_check abre cursor e roda SQL direto, furando a camada de models; o app.py
           contém handlers com acesso a banco. As fronteiras existem só no nome.
Impacto: Não há lugar único para testar/trocar/reutilizar; mudanças vazam entre camadas.
Recomendação: Views finas -> controllers (caso de uso) -> models (dados).
              Playbook "Introduzir camadas M/C/V".

### [HIGH] Estado global mutável compartilhado entre threads (AP-09)
Arquivo: database.py:4-11
Descrição: db_connection = None é um singleton global mutável reutilizado em todo lugar,
           com check_same_thread=False.
Impacto: Conexão SQLite única compartilhada entre requisições/threads -> condições de corrida
         e estado intestável (não dá para injetar fake).
Recomendação: Conexão por requisição (flask.g / factory) e injeção de dependência.
              Playbook "Injeção de dependência".

### [HIGH] Fat Controller / lógica fora de lugar (AP-07)
Arquivo: controllers.py:43-54, controllers.py:242, controllers.py:264-290
Descrição: Regras de domínio espalhadas na camada HTTP: whitelist de categorias e validações
           de negócio embutidas no handler, lista de status válidos como literal, health_check
           montando relatório de contagens via SQL direto.
Impacto: Regra não reutilizável nem testável sem HTTP; duplicação entre rotas irmãs.
Recomendação: Mover regras/validação de domínio para os controllers/casos de uso; manter views finas.
              Playbook "Extrair lógica de negócio".

### [MEDIUM] Queries N+1 na listagem de pedidos (AP-12)
Arquivo: models.py:187-199, models.py:219-231
Descrição: Para cada pedido roda-se uma query de itens e, por item, mais uma query para o
           nome do produto (3 níveis de loop+query).
Impacto: Um relatório com N pedidos e M itens vira centenas de idas ao banco; escala péssimo.
Recomendação: Substituir por JOIN único / consulta em lote. Playbook "Substituir N+1 por join".

### [MEDIUM] Integridade de dados sem transação nem cascata (AP-17)
Arquivo: models.py:133-169, models.py:65-70
Descrição: criar_pedido faz múltiplos INSERT/UPDATE (pedido, itens, baixa de estoque) sem
           transação/rollback — falha no meio deixa dados pela metade; deletar_produto apaga
           sem tratar itens_pedido órfãos; sem FKs.
Impacto: Corrupção silenciosa: estoque baixado sem pedido completo, itens órfãos.
Recomendação: Envolver escritas múltiplas numa transação com rollback; cascatear/bloquear deletes.
              Playbook "Envolver escritas numa transação".

### [MEDIUM] Validação ausente/inconsistente entre rotas (AP-13)
Arquivo: controllers.py:167-176, controllers.py:237-240, controllers.py:64-90
Descrição: login e atualizar_status_pedido chamam request.get_json().get(...) sem checar corpo
           nulo (-> 500); atualizar_produto omite as checagens de tamanho de nome e categoria
           que criar_produto tem; criar_usuario não valida formato de email.
Impacto: 500s evitáveis e dados-lixo; regras divergem entre rotas irmãs.
Recomendação: Validar na fronteira de forma consistente (helper/esquema compartilhado).
              Playbook "Validar na fronteira".

### [MEDIUM] Código duplicado (violação de DRY) (AP-14)
Arquivo: models.py:12-21/31-40/304-313 (map produto), 79-86/95-102 (map usuário),
         187-200 ~ 219-232 (pedido+itens), controllers.py:28-50 ~ 72-90
Descrição: Mapeamento linha->dict de produto repetido 3x, de usuário 2x; o bloco "pedido com
           itens" é praticamente idêntico em get_pedidos_usuario e get_todos_pedidos;
           validações de produto copiadas entre criar/atualizar.
Impacto: Correções precisam ser feitas N vezes e divergem.
Recomendação: Extrair helpers de serialização/validação compartilhados.
              Playbook "Extrair helper/método de model".

### [MEDIUM] Erros engolidos, sem tratamento central (AP-15)
Arquivo: todos os try/except Exception dos controllers (ex.: controllers.py:10, 21, 60, 95,
         125, 164, 185, 218, 254, 291)
Descrição: Cada handler reimplementa o mesmo except Exception as e: return
           jsonify({"erro": str(e)}), 500; não há @app.errorhandler global.
Impacto: Formatação inconsistente, vazamento de detalhes e nenhum ponto único de log.
Recomendação: Centralizar via error handlers/middleware. Playbook "Centralizar tratamento de erros".

### [LOW] Magic numbers & magic strings (AP-18)
Arquivo: models.py:257-262, controllers.py:52, controllers.py:242
Descrição: Limiares/taxas de desconto 10000/5000/1000 e 0.1/0.05/0.02 soltos; lista de
           categorias e de status válidos como literais inline; porta 5000.
Impacto: Intenção oculta e valores que divergem entre cópias.
Recomendação: Nomear constantes/enums em config. Playbook "Nomear constantes".

### [LOW] Código morto, import não usado e print como log (AP-20)
Arquivo: models.py:2 (import sqlite3 não usado), print(...) como logging em controllers.py:8,
         11, 57, 106, 161, 179, 208-210, 248-250; app.py:56, 83-86
Descrição: Import morto; dezenas de print usados como logging de aplicação.
Impacto: Ruído que esconde a lógica; sem níveis/saída estruturada de log.
Recomendação: Remover import morto; trocar print por logging. Playbook "Apagar código morto; usar logger".

### [LOW] Nomenclatura ruim / sombreamento de builtin (AP-19)
Arquivo: models.py:24, 28, 43, 54, 65, 89, 92; controllers.py:14, 64, 98; cursor2/cursor3 em models.py:187-193
Descrição: Parâmetro id sombreia o builtin em quase todas as funções; cursores numerados
           cursor2/cursor3 em vez de nomes com intenção.
Impacto: Leitor precisa decodificar; sombrear builtin é fonte de bugs sutis.
Recomendação: Renomear (produto_id, usuario_id, cursores nomeados). Playbook "Renomear para a intenção".

> APIs deprecated: nenhuma relevante detectada nesta stack (sem datetime.utcnow,
> before_first_request, md5/sha1 para hash, ou jsonify por caminho legado).

================================
Total: 18 achados  (CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 3)
================================
