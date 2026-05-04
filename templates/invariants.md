---
unit_of_work: <nome da UoW, ex: Campanha>
operation: <nome da operação, ex: deletePeriodCampaigns>
tier: 1
status: draft | review | approved
authors: [<nome>, <nome>]
last_updated: YYYY-MM-DD
related_specs: []
---

# Spec: <Nome da operação>

## 1. Identificação

- **Unit of Work**: <ex: Campanha>
- **Operação**: <assinatura conceitual, ex: `deletePeriodCampaigns(lojaId, periodo)`>
- **Trigger**: <quem dispara — endpoint REST, consumidor SQS, job agendado, etc>
- **Resumo em uma frase**: <o que essa operação faz, sem ambiguidade>

## 2. Pré-condições

O que deve ser verdade ANTES da operação executar. Se alguma falhar, operação aborta antes de qualquer escrita.

- [ ] <ex: lojaId existe e está ativa>
- [ ] <ex: periodo é range válido (inicio <= fim, datas não nulas)>
- [ ] <ex: usuário que dispara tem permissão X>

## 3. Efeito (pós-condição positiva)

O que MUDA no sistema quando a operação roda com sucesso. Seja específico sobre o quê, em qual entidade, com qual filtro.

- <ex: Remove registros de Campanha onde lojaId == L E periodo ⊆ P>
- <ex: Cria registro de auditoria em CampanhaAuditLog>
- <ex: Publica evento `CampanhaExcluida` em SQS>

## 4. Invariantes (pós-condição negativa) — CRÍTICO

O que NÃO PODE mudar. Esta seção protege contra o efeito não-intencional.

> **Heurística:** para cada filtro/critério na seção Efeito, escreve a NEGAÇÃO aqui.

### 4.1 Escopo de filtro
- <ex: Campanhas de lojas ≠ L permanecem inalteradas (count e conteúdo)>
- <ex: Campanhas de L em períodos ≠ P permanecem inalteradas (count e conteúdo)>

### 4.2 Entidades relacionadas
Para cada entidade relacionada, decidir explicitamente.

- <ex: Apuração derivada de campanhas removidas: [DECIDIR — preserva? cascata? soft delete?]>
- <ex: Histórico de pontuação: preserva (auditoria de pontos não pode sumir)>
- <ex: Parametrização: preserva>

### 4.3 Conservação
Asserções de contagem total / soma global.

- <ex: Total de campanhas no sistema = total anterior - N removidas>
- <ex: Soma de pontos do Histórico = soma anterior (não muda)>
- <ex: Quantidade de registros em CampanhaAuditLog = anterior + 1>

### 4.4 Efeitos colaterais externos
- <ex: NÃO dispara notificação para usuários>
- <ex: NÃO publica em fila X>
- <ex: NÃO chama API parceiro Y>

## 5. Casos limite

Comportamento explícito em cada cenário.

| Cenário | Comportamento esperado |
|---|---|
| Nenhuma campanha no período | No-op. Não erro. Audit log NÃO é gerado. |
| Período já está fora da retenção | <ex: erro `OutOfRetentionRange`> |
| Campanha cruza fronteira do período | <ex: [DECIDIR] — exclui ou preserva?> |
| Operação chamada duas vezes (idempotência) | Segunda chamada é no-op |
| Concorrência: duas execuções simultâneas | <ex: lock pessimista em LojaId> |
| Falha parcial (erro no meio) | Rollback total da transação |

## 6. Decisões pendentes (`[DECIDIR]`)

Lista consolidada do que precisa ser resolvido com produto / tech lead **antes** da implementação começar.

- [ ] <copie aqui cada [DECIDIR] das seções acima>

> **Bloqueio**: enquanto houver itens nesta seção, IA não pode gerar código.

## 7. Notas e contexto (opcional)

Decisões arquiteturais, links para ADRs, histórico de incidentes relacionados.

---

## Checklist de aprovação

Marcar antes de mover status para `approved`:

- [ ] Todas as 5 seções preenchidas
- [ ] Pelo menos 3 invariantes negativas em 4.1-4.4
- [ ] Pelo menos 1 invariante de conservação em 4.3
- [ ] Casos limite cobrem: vazio, duplicado, fronteira, concorrência, falha parcial
- [ ] Zero `[DECIDIR]` pendentes na seção 6
- [ ] Aprovado por dev + tech lead (+ produto, se houver regra de negócio)
