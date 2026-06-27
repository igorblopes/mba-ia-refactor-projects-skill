# Referência: Template do Relatório de Auditoria (Fase 2)

A saída da Fase 2 usa **exatamente** esta estrutura, para que os relatórios sejam
comparáveis entre projetos e fáceis de salvar em `reports/`. Imprima no console; quando o
usuário quiser persistir, grave o mesmo conteúdo em `reports/audit-project-<n>.md`.

## Regras

- O cabeçalho traz o nome do projeto, a stack detectada, a contagem de arquivos e o LOC
  aproximado.
- Um **Resumo** de uma linha com a contagem por severidade.
- **Achados ordenados CRITICAL → HIGH → MEDIUM → LOW.**
- Todo achado tem: uma tag de severidade + título, um `Arquivo: <caminho>:<linha(s)>`
  exato, uma `Descrição`, um `Impacto` e uma `Recomendação`. Nenhum achado sem
  arquivo:linha.
- **APIs deprecated:** se a stack tiver, reporte-as como achados (AP-16). Se **não**
  tiver nenhuma relevante, declare isso explicitamente antes do `Total` (ex.: uma linha
  `> APIs deprecated: nenhuma relevante detectada`), para deixar claro que a verificação
  foi feita.
- Um rodapé de **Total**.

## Template

```
================================
RELATÓRIO DE AUDITORIA ARQUITETURAL
================================
Projeto: <nome-da-pasta-do-projeto>
Stack:   <Linguagem> + <versão do Framework>
Arquivos: <N> analisados | ~<LOC> linhas de código

## Resumo
CRITICAL: <c> | HIGH: <h> | MEDIUM: <m> | LOW: <l>

## Achados

### [CRITICAL] <Título do anti-pattern (AP-id)>
Arquivo: <caminho>:<linha ou intervalo>
Descrição: <qual é a ocorrência concreta — cite o código problemático>
Impacto: <por que dói na prática>
Recomendação: <a correção específica / receita do playbook>

### [CRITICAL] <próximo achado>
Arquivo: ...
Descrição: ...
Impacto: ...
Recomendação: ...

### [HIGH] <título>
Arquivo: ...
Descrição: ...
Impacto: ...
Recomendação: ...

### [MEDIUM] <título>
Arquivo: ...
...

### [LOW] <título>
Arquivo: ...
...

================================
Total: <N> achados
================================
```

## Exemplo preenchido (uma entrada)

```
### [CRITICAL] SQL Injection (AP-03)
Arquivo: models.py:28
Descrição: Query montada por concatenação de string —
           cursor.execute("SELECT * FROM produtos WHERE id = " + str(id)).
           O mesmo padrão se repete em login_usuario (models.py:109-111),
           onde email/senha são concatenados direto no SQL.
Impacto: Bypass de autenticação e exfiltração total de dados via entrada
         maliciosa (ex.: ' OR '1'='1). Toda query de produto/usuário/pedido
         é explorável.
Recomendação: Usar queries parametrizadas — cursor.execute(
         "SELECT * FROM produtos WHERE id = ?", (id,)). Veja o playbook
         "Parametrizar toda query".
```

## Depois de imprimir o relatório

Encerre o relatório e então emita o portão de confirmação ao pé da letra e **aguarde**:

```
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

Não modifique nenhum arquivo até o usuário responder sim.
