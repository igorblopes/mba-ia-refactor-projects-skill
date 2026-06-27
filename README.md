# Criação de Skills — Refatoração Arquitetural Automatizada

O projeto tem o objetivo de criar uma skill, agnostica a linguagem, para que identifique, catalogue e realize a refatoração de projetos legados.


## Análise Manual dos Projetos

### PROJETO: code-smells-project

**CRITICAL ou HIGH:**
- Key Hardcoded: Classe app.py tem a chave SECRET_KEY como hardcoded, expondo a credencial.

**MEDIUM:**
- Logica dentro de Controller: Na Classe controllers.py, método criar_produto, possui lógica para validar os campos que vem no request dados.
- Forte Acoplamento em Models: Na Classe models.py, na primeira linha, é importado o método get_db, diretamente do arquivo de database, sem injeção de dependencia, causando forte acoplamento.

**LOW:**
- Nomes de variaveis ruins: No arquivo models.py, no método relatorio_vendas, temos as variáveis "pendentes", "aprovados" e "cancelados". Poderia ter nomes mais claros, sendo que o proprio metodo trabalha com pedidos e faturamento, podendo confundir o que significa as variáveis. Precisa entender o fluxo para entender que os nomes são referencias aos status dos pedidos.
- Dificuldade de legibilidade: No arquivo models.py, no método get_todos_pedidos, temos as variaveis "cursor" e "cursor2", poderia ter nomes mais significativos para entender do que se trata. Temos no mesmo método um for dentro do outro, poderia ter sido criado um método para ser transformado o dado do banco de dados em um objeto de retorno para abstrair o conteúdo que o método realiza.
---

### PROJETO: ecommerce-api-legacy

**CRITICAL ou HIGH:**
- Expondo credenciais: No arquivo AppManager.js, no método initDb, ao fazer ao criar os usuários está expondo suas senhas de forma aberta, sem criptografia, em texto plano.

**MEDIUM:**
- Falta de injeção de dependencia: No arquivo AppManager.js, no método setupRoutes, está sendo usado um método chamado logAndCache, que apenas está sendo importado de outro método.
- Gargalos em banco de dados: No arquivo AppManager.js, no método setupRoutes, está sendo encadeado várias chamadas no banco de dados, uma atrás do outro. Uma query melhor poderia resolver com apenas uma chamada no DB.

**LOW:**
- Nomes de variaveis ruins: No arquivo AppManager.js, no método setupRoutes, está sendo criado algumas variaveis no inicio do método com os seguintes nomes que não tem significado "u", "e", "p", "cid" e "cc".
- Melhoria de legibilidade: No arquivo AppManager.js, no método setupRoutes, está sendo feito tudo em um mesmo local, setando rotas, lógicas e acesso ao banco de dados, fica muito complexo para entender e realizar manutenções.
---

### PROJETO: task-manager-api

**CRITICAL ou HIGH:**
- Expondo crendenciais: Em notification_service.py, no método __init__, com o email e senha em texto plano, sem injeção de um local seguro.

**MEDIUM:**
- Duplicação de código: No arquivo user_routes.py, no método create_user, está sendo validado os parametros dos campos de request. Poderia ser criado um método auxiliar ou decorators para abstrair a logica de validação dos campos.
- Falta de padronização: Nos arquivos models/task.py e models/user.py os metodos to_dict, estao criando de forma diferentes a saida. Uma ja criando o objeto e devolvendo ele logo em seguida, no outro criando o objeto vazio depois vai preenchendo cada campo.

**LOW:**
- Melhorias de legibilidade: Os arquivos de routes estao utilizando validacao de objetos dentro dos metodos que declaram as rotas, dificultando o entendimento do que aquela rota faz. Poderia ser abstraido em outras camadas para segregar os objetivos.
- Nomeclatura: No arquivo report_routes.py, no método summary_report, existem variaveis com nomes não claros do que são, como "p1", "p2", "p3", "p4". Poderia ter o nome completo ou objetivo daquela variável, nomes não claros faz com que as pessoas precisem ler mais código para entender o que faz aquelas variáveis.


## Construção da Skill

### Decisões de design

- **Separação "fluxo" vs. "conhecimento".** O `SKILL.md` é só o roteiro — diz **o que fazer e em que ordem** de acordo com as 3 fases. Todo o conhecimento de domínio mora em `references/`, lido sob demanda no início da fase que precisa dele. Isso mantém o `SKILL.md` enxuto e permite que as referências cresçam sem inchar o contexto. Uma tabela no topo do `SKILL.md` indica exatamente quando ler cada referência.
- **Cinco arquivos de referência, um por área de conhecimento exigida:**
  - `project-analysis.md` → heurísticas de detecção para validar linguagem, framework, banco, domínio e arquitetura.
  - `anti-patterns.md` → catálogo com sinais de detecção + severidade
  - `report-template.md` → formato fixo do relatório, um exemplo para mostrar para a skill como quero o report.
  - `mvc-guidelines.md` → a arquitetura MVC alvo e a responsabilidade de cada camada
  - `refactoring-playbook.md` → receitas de transformação antes/depois
- **Três fases sequenciais com um portão humano no meio.** A Fase 1 flui direto para a Fase 2, mas a Fase 2 **para e exige confirmação explícita** antes de tocar em qualquer arquivo. A auditoria é somente-leitura; quem decide reescrever o código é o humano e não a skill.
- **Saída padronizada e ancorada em evidência.** Banners fixos para a Fase 1 e para o relatório, e a regra de que **todo achado tem `arquivo:linha` exato** + descrição + impacto + recomendação, ordenados de CRITICAL→LOW. Isso torna os relatórios comparáveis e verificáveis.
- **Princípio "deixe rodando".** A Fase 3 obriga estabelecer uma *baseline* (subir a app e registrar quais endpoints respondem) **antes** de mudar, e revalidar boot + os mesmos endpoints **depois**, preservando o contrato público (mesmas rotas/métodos/formato de resposta).

### Quais anti-patterns incluí e por quê

Montei um catálogo de **20 anti-patterns** com siglas de AP-01 até AP-20, com severidade distribuída (**5 CRITICAL, 6 HIGH, 6 MEDIUM, 3 LOW**). Cada um foi escolhido porque aparece concretamente em pelo menos um dos 3 projetos-alvo .

- **CRITICAL** — quebram segurança ou arquitetura: God Class/Module (AP-01), credenciais hardcoded (AP-02), SQL Injection (AP-03), senha em texto plano/hash fraco (AP-04), endpoint de execução arbitrária de SQL (AP-05). *Casos reais:* `/admin/query` (projeto 1), `paymentGatewayKey` (projeto 2), `md5` (projeto 3).
- **HIGH** — violações fortes de MVC/SOLID: modo debug em produção (AP-06), fat controller (AP-07), camadas misturadas (AP-08), estado global mutável/sem DI (AP-09), efeitos colaterais na regra de negócio (AP-10), callback hell (AP-11).
- **MEDIUM** — padronização/performance: N+1 (AP-12), validação ausente (AP-13), duplicação/DRY (AP-14), erros engolidos/sem handler central (AP-15), **APIs deprecated (AP-16)**, integridade de dados/sem transação (AP-17).
- **LOW** — legibilidade: magic numbers (AP-18), nomenclatura ruim (AP-19), código morto/imports/prints (AP-20).

A **detecção de APIs deprecated (AP-16)** virou uma tabela "uso deprecated → status → substituto moderno" cobrindo `datetime.utcnow()`, `Model.query.get()`, `hashlib.md5` para senhas, `before_first_request`, `bodyParser.json()`, `sqlite3.verbose()` etc. — cada um casando com código real (ex.: 11 `utcnow()` + 16 `query.get()` no projeto 3). No playbook, garanti **uma receita de transformação para cada anti-pattern** (17 receitas com exemplos antes/depois).

### Como garanti que a skill é agnóstica de tecnologia

- **Detecção primeiro, ação depois.** A skill nunca presume a stack: a Fase 1 lê o manifesto (`requirements.txt`/`package.json`/…) e mapeia linguagem → framework → banco. Só depois aplica o mesmo raciocínio.
- **Sinais em termos neutros + exemplos paralelos.** Cada anti-pattern e cada receita trazem o conceito de forma neutra e **exemplos lado a lado em Python/Flask e Node.js/Express**; o mesmo catálogo serve às duas stacks trocando só a sintaxe da correção.
- **Camadas MVC por responsabilidade, não por framework.** As guidelines definem Models/Controllers/Views/Routes/config/middlewares/services por responsabilidade, com a estrutura-alvo nas duas convenções (`produto_model.py` vs `userModel.js`, Blueprints vs `express.Router()`) e "regras de bolso" ("fala com o banco? → Model").
- **Nada hardcoded para um projeto.** A skill é copiada idêntica nos 3 projetos. Validei rodando Fase 1 e Fase 2 nos três (Python monolítico, Node God Object e Python com camadas parciais) — detecção e relatórios corretos em todos.
- **Tratamento do caso "camadas parciais"** (projeto 3): a skill orienta a *melhorar* a estrutura existente em vez de destruí-la, evitando acoplar a refatoração ao formato "monólito".

### Desafios encontrados

- **Armadilha de domínio pelo nome da pasta.** O projeto 2 chama-se `ecommerce-api-legacy`, mas é um **LMS** (tabelas `courses`, `enrollments`, `payments`; log "Frankenstein LMS"). *Solução:* aviso no `project-analysis.md` para inferir domínio por rotas/tabelas/mensagens, nunca pelo nome do diretório.
- **Ambiguidade na contagem de arquivos.** Frágil quando há `__init__.py` e scripts (`seed.py`). *Solução:* defini *o que conta* (todo arquivo de código da linguagem detectada, inclusive marcadores de pacote) e recomendei derivar o número de uma listagem real do disco.
- **Tensão entre "preservar endpoints" e "remover endpoints perigosos".** A Fase 3 mantém o contrato público, mas o audit manda remover `/admin/query` (RCE) e `/admin/reset-db` sem auth. *Resolução:* tratar a remoção de rotas maliciosas como correção de segurança intencional e documentá-la, mantendo intactos os endpoints legítimos.
- **Compatibilidade ao trocar o hashing de senha.** Migrar de texto plano/`md5` para hash real quebraria o login dos usuários de seed. *Solução:* a refatoração re-semeia as senhas já com hash, de modo que o login continua respondendo corretamente.
- **"Se aplicável" nas APIs deprecated.** O projeto 1 (Flask 3.1.1) não tem deprecated relevante. *Solução:* o template passa a **declarar explicitamente** quando não há deprecated, em vez de só omitir.
- **Cobertura completa do playbook.** Ao cruzar catálogo × playbook, 2 anti-patterns apontavam para receitas inexistentes (AP-14 e AP-19) — corrigido adicionando as receitas faltantes, garantindo que todo AP tem uma transformação concreta.

## Resultados

### Projeto: code-smells-project

**Execução da skill no projeto code-smells-project**

![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-1.png)
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-2.png)
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-3.png)
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-4.png)

**Solicitação da execução da Fase 3**

![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-5.png)

**Final da Refatoração**

![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-6.png)

**Comparação antes e depois**

```
Antes era todos os controlers juntos:
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-7.png)

```
Depois os controllers foram separados:
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-8.png)


---
<br>

```
Criado um middleware para validar e registrar erros:
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-9.png)

```
Antes não existia uma camada de middleware:
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-10.png)


---
<br>

```
Antes foi criado a notificação dentro dos controllers
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-11.png)

```
Agora esta sendo feito em uma camada separada
```
![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-12.png)


**Screenshots da aplicação rodando**

![Screenshot](./prints/code-smells-project/Refactor-Skill-Code-Smells-Project-Part-13.png)


### Projeto: ecommerce-api-legacy

**Execução da skill no projeto ecommerce-api-legacy**

![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-1.png)
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-2.png)
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-3.png)

**Solicitação da execução da Fase 3**

![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-4.png)

**Final da Refatoração**

![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-5.png)

**Comparação antes e depois**


```
Antes existia uma God Class 'AppManager.js' que fazia de tudo um pouco
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-6.png)

```
Depois o projeto ficou bem mais segregado e dividido:
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-7.png)


---
<br>

```
Antes existia um badCrypto para fazer o hash da senha de forma muito simplista e inseguro
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-8.png)

```
Agora temos um algoritmo melhor e com salt + scrypt para deixar mais seguro
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-9.png)


---
<br>

```
Antes era tudo junto a parte de pagamento e auditoria
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-10.png)

```
Agora temos camadas separadas para fazer o pagamento e outra para fazer a auditoria
```
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-11.png)
![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-12.png)

**Screenshots da aplicação rodando**

![Screenshot](./prints/ecommerce-api-legacy/Refactor-Skill-Ecommerce-Api-Legacy-Part-13.png)




### Projeto: task-manager-api


**Execução da skill no projeto ecommerce-api-legacy**

![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-1.png)
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-2.png)
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-3.png)
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-4.png)

**Solicitação da execução da Fase 3**

![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-6.png)

**Final da Refatoração**

![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-5.png)

**Comparação antes e depois**


```
Antes eram varios itens verificados dentro dos routers
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-7.png)

```
Depois o projeto esta melhor segregado com a visao de camadas
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-8.png)


---
<br>

```
Antes os erros eram tratados nos prorios routers
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-10.png)

```
Depois o projeto ganhou um middleware para cuidar de erros
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-9.png)

---
<br>

```
Antes tinhamos nomes de variaveis nao claras e imprecisas
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-11.png)

```
Depois o projeto possui nomes de variaveis com significado, facilitando a manutencao
```
![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-12.png)


**Screenshots da aplicação rodando**

![Screenshot](./prints/task-manager-api/Refactor-Skill-Task-Manager-Api-Part-13.png)



## Como Executar

A skill `refactor-arch` roda **dentro do Claude Code**. Ela já vem copiada, idêntica, em cada
projeto (`<projeto>/.claude/skills/refactor-arch/`), então basta abrir o Claude Code na pasta
do projeto e invocar o comando `/refactor-arch`.

### Pré-requisitos

- **Claude Code** instalado e autenticado (é ele quem executa a skill).
- **Python 3.10+** com `pip` — para `code-smells-project` e `task-manager-api` (Flask).
- **Node.js 18+** com `npm` — para `ecommerce-api-legacy` (Express).
- **Git** (para clonar/versionar) e um cliente HTTP para validar os endpoints — `curl` ou a
  extensão REST Client do VS Code (os exemplos ficam em `ecommerce-api-legacy/api.http`).

> Recomendado usar um ambiente virtual nos projetos Python (`python -m venv venv` e ativar)
> antes de instalar as dependências.

### Executando a skill em cada projeto

Abra o Claude Code **na raiz do projeto** que quer refatorar e rode o comando. A skill executa
em 3 fases e **pausa na Fase 2** pedindo confirmação (`Prosseguir com a refatoração (Fase 3)? [s/n]`);
responda `s` para que ela aplique a refatoração, ou `n` para parar apenas no relatório de auditoria.

```bash
# Projeto 1 — Python/Flask
cd code-smells-project
claude            # abra o Claude Code nesta pasta e rode:
/refactor-arch

# Projeto 2 — Node.js/Express
cd ecommerce-api-legacy
claude
/refactor-arch

# Projeto 3 — Python/Flask (camadas parciais)
cd task-manager-api
claude
/refactor-arch
```

### Validando que a refatoração funcionou

A própria skill estabelece uma *baseline* (sobe a app e registra os endpoints antes de mudar) e
revalida boot + endpoints depois. Para conferir você mesmo, suba cada app refatorada e exercite
as rotas — o contrato público (mesmas rotas, métodos e formato de resposta) deve continuar idêntico.

**code-smells-project** (Flask → `http://localhost:5000`):

```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
# em outro terminal:
curl http://localhost:5000/produtos
```

**ecommerce-api-legacy** (Express → `http://localhost:3000`):

```bash
cd ecommerce-api-legacy
npm install
npm start
# valide com os exemplos de requisição em api.http (ou via curl)
```

**task-manager-api** (Flask → `http://localhost:5000`):

```bash
cd task-manager-api
pip install -r requirements.txt
cp .env.example .env     # opcional — ajuste SECRET_KEY e demais variáveis
python seed.py           # popule o banco ANTES do primeiro boot
python app.py
# em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/tasks
```

A refatoração é considerada bem-sucedida quando:

- a aplicação **inicia sem erros**;
- os **mesmos endpoints** da baseline continuam respondendo corretamente;
- **zero anti-patterns** do relatório permanecem (ou os adiados estão justificados);
- o relatório de auditoria gerado fica disponível em `reports/` para conferência.