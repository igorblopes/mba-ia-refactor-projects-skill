---
name: refactor-arch
description: >-
  Audita qualquer codebase de backend e a refatora para o padrão MVC
  (Model-View-Controller), de forma agnóstica de tecnologia. Executa em três fases
  sequenciais — Análise (detecta linguagem, framework, banco de dados e arquitetura
  atual), Auditoria (cruza o código contra um catálogo de anti-patterns, classifica os
  achados por severidade CRITICAL/HIGH/MEDIUM/LOW com arquivo:linha exatos, emite um
  relatório estruturado e PAUSA para confirmação humana) e Refatoração (reestrutura em
  camadas MVC, elimina os achados e valida que a aplicação ainda inicia e que todos os
  endpoints continuam respondendo). Use esta skill sempre que o usuário pedir para
  auditar, revisar, reestruturar, limpar, modernizar ou refatorar a arquitetura de um
  projeto, corrigir code smells / anti-patterns, separar responsabilidades / camadas,
  aplicar MVC ou SOLID, ou executar o comando "/refactor-arch" — mesmo que não citem MVC
  explicitamente. Funciona com Python/Flask, Node.js/Express e outras stacks.
---

# refactor-arch — Auditoria e Refatoração Arquitetural

Você atua como um **arquiteto de software sênior** conduzindo uma auditoria e refatoração.
Sua missão é pegar um projeto de backend desconhecido, provar que o entendeu, expor seus
problemas de arquitetura e segurança com evidências e então reestruturá-lo em uma
arquitetura **MVC** limpa — sem quebrá-lo.

A skill roda em **três fases sequenciais**. A Fase 2 **deve parar e pedir confirmação
humana** antes de modificar qualquer arquivo. Nunca pule o portão de confirmação: um
humano precisa revisar a auditoria antes de você tocar no código dele.

## Como esta skill está organizada

O `SKILL.md` (este arquivo) é o fluxo de trabalho — *o que fazer e em que ordem*. O
conhecimento de domínio fica em `references/`. Leia cada arquivo de referência no início
da fase que precisa dele; não tente segurar tudo na memória de uma vez.

| Arquivo de referência | Leia durante | O que ele fornece |
|---|---|---|
| `references/project-analysis.md` | Fase 1 | Heurísticas para detectar linguagem, framework, banco de dados, domínio e arquitetura atual |
| `references/anti-patterns.md` | Fase 2 | Catálogo de anti-patterns com sinais concretos de detecção + severidade (incl. APIs deprecated) |
| `references/report-template.md` | Fase 2 | Formato exato do relatório de auditoria |
| `references/mvc-guidelines.md` | Fase 3 | A arquitetura MVC alvo: camadas, responsabilidades e as regras |
| `references/refactoring-playbook.md` | Fase 3 | Receitas de transformação antes/depois, uma por família de anti-pattern |

O ponto central desta skill é que ela é **copiável e agnóstica de tecnologia**. Não
fixe (hardcode) nada específico de um único projeto. Detecte a stack primeiro (Fase 1) e
depois aplique o mesmo raciocínio independente da linguagem. As referências descrevem os
sinais em termos neutros de linguagem e dão exemplos em Python/Flask *e* Node.js/Express,
para que o mesmo catálogo funcione em diferentes stacks.

---

## FASE 1 — Análise do Projeto

**Objetivo:** provar que você entendeu o projeto antes de julgá-lo. Detecte a stack e
mapeie a arquitetura atual.

1. Leia `references/project-analysis.md`.
2. Liste os arquivos do projeto (ignore `node_modules/`, `venv/`, `.venv/`,
   `__pycache__/`, `.git/`, artefatos de build, lockfiles e a própria pasta da skill
   `.claude/`).
3. Leia primeiro o manifesto (`requirements.txt`, `package.json`, `pyproject.toml`,
   `pom.xml`, `go.mod`, …) para detectar **linguagem**, **framework** e **dependências**.
4. Leia cada arquivo-fonte. Identifique:
   - o **domínio** (sobre o que a app trata — infira a partir das rotas, nomes de tabelas
     e entidades),
   - o **banco de dados** e suas tabelas/models,
   - a **arquitetura atual** (quantos arquivos, existe alguma separação de camadas?),
   - o **ponto de entrada** e como as rotas são conectadas.
5. Imprima o resumo da Fase 1 **exatamente** neste formato:

```
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:     <ex.: Python>
Framework:     <ex.: Flask 3.1.1>
Dependências:  <libs principais>
Domínio:       <uma linha descrevendo o que a app faz>
Arquitetura:   <uma linha: monolítica / camadas parciais / etc.>
Arquivos:      <N> arquivos analisados
Tabelas DB:    <nomes de tabelas ou models>
================================
```

Não pare para receber input aqui — siga direto para a Fase 2.

---

## FASE 2 — Auditoria de Arquitetura

**Objetivo:** produzir achados baseados em evidências e deixar um humano aprovar antes de
qualquer mudança.

1. Leia `references/anti-patterns.md` e `references/report-template.md`.
2. Percorra o código **anti-pattern por anti-pattern**. Para cada ocorrência, capture:
   - o nome do anti-pattern e sua **severidade** (CRITICAL / HIGH / MEDIUM / LOW),
   - o **`arquivo:linha` exato** (ou intervalo de linhas) — isso é obrigatório, nunca vago,
   - uma **descrição** de uma linha da ocorrência concreta (cite o código problemático),
   - o **impacto** e uma **recomendação**.
3. Seja específico. "Código ruim" é inútil. "SQL concatenado como string em `models.py:28`
   permite SQL injection" é acionável. Sempre ancore o achado em linhas reais que você leu.
4. Inclua detecção de **APIs deprecated / obsoletas** — sinalize chamadas obsoletas e
   nomeie o substituto moderno (veja o catálogo).
5. Ordene os achados por severidade (CRITICAL → HIGH → MEDIUM → LOW).
6. Emita o relatório usando o template em `references/report-template.md`. Busque
   completude: um projeto legado real desse tipo tem **no mínimo 5 achados** e normalmente
   muitos mais. Você precisa expor **pelo menos um CRITICAL ou HIGH**.
7. **PARE. Peça confirmação** com este prompt exato e aguarde a resposta:

```
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

   - Se o usuário responder **não** (ou qualquer coisa diferente de sim), encerre com
     elegância. O relatório já é um entregável valioso; ofereça-se para salvá-lo em
     `reports/`.
   - Só continue para a Fase 3 com um **sim** explícito (`s`, `sim`, `y` ou `yes`).

> O portão de confirmação é inegociável. A auditoria é somente-leitura; o humano é dono da
> decisão de deixar você reescrever o código dele.

---

## FASE 3 — Refatoração para MVC

**Objetivo:** reestruturar em MVC, eliminar os achados e provar que a app ainda funciona.

1. Leia `references/mvc-guidelines.md` (a arquitetura alvo) e
   `references/refactoring-playbook.md` (as receitas de transformação).
2. **Estabeleça uma baseline primeiro.** Antes de mudar qualquer coisa, rode a app do
   jeito que o README dela manda e registre que ela inicia e quais endpoints respondem.
   Você não pode afirmar "ainda funciona" sem um estado-anterior para comparar. Se a app
   não conseguir nem iniciar antes das suas mudanças, anote isso e prossiga com cuidado.
3. Construa o esqueleto MVC (adapte os nomes às convenções da linguagem — veja as
   guidelines). O alvo canônico é:

```
src/
├── config/        # configuração & segredos lidos do ambiente (sem hardcoding)
├── models/        # apenas acesso a dados — um módulo por entidade de domínio
├── controllers/   # lógica de negócio / casos de uso — orquestram models, sem cola de framework
├── views/         # camada HTTP — rotas/blueprints mapeiam URLs para controllers (finas)
├── middlewares/   # preocupações transversais: tratamento de erros central, auth, logging
└── app.py|app.js  # composition root / ponto de entrada — conecta tudo
```

4. Aplique as transformações do playbook para zerar cada achado da Fase 2. Mova SQL para
   os models, lógica de negócio para os controllers, mantenha as rotas finas, extraia a
   config, centralize o tratamento de erros, parametrize queries, faça hash de segredos,
   remova código morto/de debug e corrija APIs deprecated. **Preserve o comportamento
   externo**: mesmas rotas, mesmos métodos HTTP, mesmos formatos de resposta. Isto é uma
   refatoração, não uma reescrita do contrato.
5. Para um projeto que *já* tem alguma camada (ex.: models/ + routes/ + services/), não
   destrua tudo — **melhore** em direção às guidelines: corrija os problemas reais, mova
   responsabilidades fora de lugar e só reestruture onde isso remove um achado.
6. **Valide** e mostre o resultado:
   - inicie a app refatorada — ela precisa subir sem erros,
   - exercite os endpoints originais (os mesmos da baseline) e confirme que ainda
     respondem corretamente,
   - confirme que zero anti-patterns do relatório permanecem (ou liste os deliberadamente
     adiados, com justificativa).
7. Imprima o resumo da Fase 3:

```
================================
FASE 3: REFATORAÇÃO CONCLUÍDA
================================
Nova Estrutura do Projeto:
<árvore da nova estrutura>

Validação
  ✓ Aplicação inicia sem erros
  ✓ Todos os endpoints respondem corretamente
  ✓ Zero anti-patterns remanescentes
================================
```

### Orientações de validação

- Prefira um boot real + sondagem HTTP em vez de afirmações. Para Flask use o test client
  ou `flask run`/`python app.py`; para Express use `npm start` e faça curl nas rotas.
- Se o projeto tiver um `api.http`, um `seed.py` ou requisições de exemplo, use-os como
  checklist de endpoints.
- Se faltar uma dependência de runtime, instale-a a partir do manifesto antes de concluir
  que a app está quebrada.

---

## Princípios de operação

- **Evidência acima de opinião.** Todo achado cita uma linha que você de fato leu.
- **Confirme antes de mutar.** A Fase 2 sempre pausa. Somente-leitura até o humano liberar.
- **Preserva comportamento.** A refatoração mantém a API pública idêntica; apenas a
  estrutura interna muda.
- **Agnóstica.** Detecte primeiro, depois aja. O mesmo catálogo e o mesmo alvo MVC valem
  para Flask, Express e além — só a sintaxe das correções muda.
- **Deixe rodando.** Uma refatoração que não inicia é uma falha, por mais limpa que seja.
