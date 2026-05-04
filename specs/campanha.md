---
unit_of_work: Campanha
operation: <múltiplas — esta spec é AGREGADA da UoW. Quebrar por operação ao implementar.>
tier: 1
status: draft
authors: []
last_updated: 2026-05-04
related_specs: [apuracao.md, historico.md, parametrizacao.md]
---

# Spec: Unit of Work — Campanha

> **Nota**: este arquivo é um **mapa da UoW**, não a spec de uma operação única.
> Ao implementar cada operação, COPIE o template `templates/invariants.md` e
> preencha individualmente. Use este arquivo como referência cruzada.

## Operações Tier 1 conhecidas nesta UoW

- [ ] `criarCampanha` — geralmente Tier 2 (criação não destrói); avaliar se há cascata
- [ ] **`excluirCampanhaPorPeriodo`** — Tier 1 (incidente real, ver `examples/exclusao-campanha-por-periodo.md`)
- [ ] **`excluirCampanha` (individual)** — Tier 1
- [ ] **`encerrarCampanha`** / mudança de status para finalizada — Tier 1 se dispara apuração ou bloqueia novos eventos
- [ ] **`aplicarCampanhaEmLote` (CSV → SQS)** — Tier 1 (lote)
- [ ] `atualizarCampanha` — Tier 2 ou 1 dependendo dos campos editáveis [DECIDIR]
- [ ] `vincularLojaACampanha` / `desvincularLoja` — Tier 1 se altera apuração corrente

## Invariantes globais da UoW (aplicam a TODAS operações Tier 1)

Estas invariantes são herdadas por toda operação que toca Campanha. Spec individual
pode adicionar mais, mas não pode violar estas.

### Conservação
- Total de campanhas no sistema só muda em criação ou exclusão **explícita**. Nunca como efeito colateral.
- Toda operação que altera Campanha gera registro em `CampanhaAuditLog`.

### Histórico
- Apurações já concluídas (status FINAL) **nunca** são removidas como efeito de mudança em Campanha. [DECIDIR — confirmar com tech lead]
- Histórico de pontuação derivado de campanha encerrada **nunca** é removido. [DECIDIR]

### Escopo de exclusão / modificação
- Operação que filtra por loja jamais afeta dados de outras lojas.
- Operação que filtra por período jamais afeta dados de outros períodos.
- Operação que filtra por status jamais afeta dados de outros status.

### Efeitos externos
- Mudança em campanha que afeta usuário final só dispara notificação se a operação for explicitamente `comunicar=true`. [DECIDIR — política atual?]

## Entidades relacionadas (mapa de cascata)

| Entidade | Relação com Campanha | Cascata em exclusão | Cascata em encerramento |
|---|---|---|---|
| Loja | N:N (uma campanha tem N lojas) | [DECIDIR] | [DECIDIR] |
| Apuração | 1:N | [DECIDIR — preserva histórica?] | gera apuração final |
| Histórico de pontos | 1:N (via apuração) | **Nunca cascata** [confirmar] | preserva |
| Parametrização | 1:1 ou 1:N | [DECIDIR] | preserva |
| CampanhaAuditLog | 1:N | preserva (auditoria) | preserva |

## Decisões pendentes (consolidado)

Bloqueia implementação até resolver com tech lead:

- [ ] Política de exclusão: hard delete ou soft delete?
- [ ] Apuração de campanha excluída: preserva histórica ou remove?
- [ ] Campanha que cruza fronteira de período: comportamento?
- [ ] Vínculo de loja: remoção retroativa afeta apuração já calculada?
- [ ] Política de comunicação ao usuário em exclusão / encerramento

## Notas de contexto

- Incidente de referência: exclusão por período apagou histórico de campanha de loja. Detalhado em `examples/exclusao-campanha-por-periodo.md`.
- Volume estimado: <preencher — quantas campanhas / mês / loja em média>
- Pico de operação: parametrização mensal via CSV → SQS
