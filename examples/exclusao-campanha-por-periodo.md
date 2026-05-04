---
unit_of_work: Campanha
operation: excluirCampanhaPorPeriodo
tier: 1
status: example_retroactive
authors: [retroativo - reconstrução do incidente]
last_updated: 2026-05-04
related_specs: [campanha.md]
---

# Exemplo retroativo: Exclusão de campanha por período

> Esta é a spec que **deveria ter existido** antes do incidente que motivou
> este protocolo. Reconstruída com base no comportamento errado observado.
> Serve como exemplo canônico de spec Tier 1 bem formulada.

## O que aconteceu (incidente real)

- Pedido vago: "implementar exclusão de campanha por período"
- IA gerou: lógica que apagava registros desde que `id != null`
- Comportamento real: apagaria **toda** campanha da loja, em qualquer período
- Bonus bug estrutural: mesma lógica duplicada em dois services diferentes
- Detecção: revisão manual profunda antes de subir
- Quase-incidente. Não chegou em produção.

## A spec que teria prevenido

---

## 1. Identificação

- **Unit of Work**: Campanha
- **Operação**: `excluirCampanhaPorPeriodo(lojaId: Long, periodo: Periodo)`
- **Trigger**: endpoint REST autenticado (admin)
- **Resumo**: Remove (ou marca como excluídas) as campanhas de UMA loja específica que estão totalmente contidas em UM período específico. Operação destrutiva. Auditada.

## 2. Pré-condições

- [ ] `lojaId` corresponde a loja existente e ativa
- [ ] `periodo.inicio` <= `periodo.fim`
- [ ] `periodo.inicio` >= `Hoje - retencaoMaxima` (não permite excluir além da retenção)
- [ ] Usuário tem perfil `ADMIN_CAMPANHA`
- [ ] Nenhuma campanha no escopo está em status APURACAO_EM_ANDAMENTO

## 3. Efeito

- Identifica conjunto C = { campanhas onde `lojaId == L` E `periodo da campanha ⊆ periodo argumento` }
- Marca cada campanha em C como `EXCLUIDA` (soft delete) — NÃO hard delete
- Cria registro em `CampanhaAuditLog` para cada campanha excluída, com:
  - usuário que disparou
  - timestamp
  - período argumento
  - lojaId
  - lista de campanhaIds afetadas
- Publica evento `CampanhaExcluida` em SQS, **uma vez**, com lista consolidada

## 4. Invariantes — CRÍTICO

### 4.1 Escopo de filtro
- Campanhas de **outras lojas** (lojaId ≠ L): count e conteúdo permanecem inalterados.
- Campanhas da loja L em **outros períodos** (período fora de P): count e conteúdo permanecem inalterados.
- Campanhas da loja L que **cruzam fronteira** do período P (parcialmente em P, parcialmente fora): **NÃO são afetadas**. Decisão: só exclui campanhas totalmente contidas em P.

### 4.2 Entidades relacionadas
- **Apuração** das campanhas excluídas: **preserva**. Apurações já FINAL não somem.
- **Histórico de pontos** já creditado: **preserva integralmente**. Pontos já dados ao usuário não são revertidos por essa operação.
- **Parametrização** das campanhas excluídas: **preserva**. Auditoria.
- Vínculo Campanha-Loja: marca como inativo, **não remove**. Auditoria preservada.

### 4.3 Conservação
- `count(Campanha onde status ≠ EXCLUIDA)` antes - count(Campanha onde status ≠ EXCLUIDA) depois = `|C|`
- `count(Campanha total no banco)` antes = depois (soft delete)
- `count(CampanhaAuditLog)` depois = antes + `|C|`
- `sum(Historico.pontos)` antes = depois (não muda nada)

### 4.4 Efeitos colaterais externos
- **NÃO** dispara notificação ao usuário final (admin operation, não comunicada).
- **NÃO** chama nenhuma API parceira.
- Publica EXATAMENTE 1 evento em SQS (não 1 por campanha — consolidado).

## 5. Casos limite

| Cenário | Comportamento |
|---|---|
| `|C| == 0` (nada para excluir) | No-op. Não erro. **NÃO** gera audit log. **NÃO** publica evento SQS. |
| Campanha em status APURACAO_EM_ANDAMENTO | Aborta a operação inteira (transação). Mensagem: "X campanhas em apuração ativa, aguarde finalização". |
| Período fora da retenção | Erro `OutOfRetentionRange`. |
| Período inválido (inicio > fim) | Erro `InvalidPeriodRange`. |
| Loja inativa ou inexistente | Erro `InvalidStore`. |
| Operação chamada 2x com mesmo input | Segunda chamada: `|C|` agora é zero (já estão EXCLUIDA), no-op. Idempotente. |
| Concorrência: 2 admins disparam simultâneo | Lock pessimista por `lojaId`. Segundo espera. |
| Falha de banco no meio | Rollback total. Sem efeito parcial. |

## 6. Decisões pendentes

> Nenhuma — esta é a spec exemplo, completa.

Em uso real, esta seção bloquearia desenvolvimento se houvesse `[DECIDIR]`.

## 7. Notas de contexto

- Esta operação é Tier 1 por destruir dado (mesmo via soft delete) e por afetar relacionamento com Apuração / Histórico.
- O bug original aconteceu porque:
  - **Spec ausente**: pedido foi "implementar exclusão por período". A IA inferiu o que queria.
  - **Invariantes implícitas**: ninguém escreveu "outras lojas / outros períodos não podem ser afetados".
  - **Teste fraco**: existia teste verificando que campanhas de P sumiam, mas não que campanhas de outros períodos permaneciam.
  - **Código defensivo sem critério**: `if (id != null)` foi inventado pela IA como "salvaguarda" e virou o bug.

---

## Como esta spec teria prevenido o incidente

| Mecanismo | O que pegaria |
|---|---|
| Pré-condição "período válido" | Bug não relacionado, mas filtra entrada lixo |
| Invariante 4.1 explícita | Forçaria teste que provasse que outros períodos / outras lojas permanecem |
| Invariante 4.3 (conservação) | Teste contagem-antes vs contagem-depois pegaria a discrepância imediatamente |
| Caso limite "|C| == 0" | Forçaria pensar no que define o conjunto C — exato ponto onde a IA errou |
| Anti-padrão "código defensivo sem critério" | Auditor LLM marcaria `if (id != null)` como suspeito |

Qualquer **uma** das proteções acima teria pegado o bug. Defesa em profundidade.
