---
unit_of_work: Historico
operation: <múltiplas — mapa da UoW>
tier: 1
status: draft
authors: []
last_updated: 2026-05-04
related_specs: [campanha.md, apuracao.md]
---

# Spec: Unit of Work — Histórico

> Mapa da UoW. Ao implementar operação, copie `templates/invariants.md`.

## Princípio fundamental

Histórico é **append-only** por padrão. Toda operação que parece "alterar histórico"
na verdade **adiciona** um registro de compensação ou ajuste, e preserva o original.

Se uma operação Tier 1 desta UoW propõe DELETE ou UPDATE direto em registro de
histórico, é **bandeira vermelha** — provavelmente há erro de modelagem.

## Operações Tier 1 conhecidas

- [ ] **`registrarCredito` / `registrarDebito`** — append. Tier 1 (financeiro).
- [ ] **`compensarRegistro`** — adiciona registro de compensação. Tier 1.
- [ ] **`expurgarHistorico`** (LGPD / retenção) — Tier 1 destrutivo, requer aprovação especial. [DECIDIR — existe?]
- [ ] `consultarHistorico` — Tier 3 (leitura).
- [ ] `consolidarPeriodo` — agrega registros, gera snapshot. Tier 1 se afeta saldo apresentado. [DECIDIR]

## Invariantes globais

### Append-only
- Nenhuma operação remove registro de histórico, exceto `expurgarHistorico` (se existir).
- Nenhuma operação **modifica** registro de histórico existente. Correção é via novo registro de compensação.

### Conservação financeira (auditoria)
- Saldo de pontos do usuário = soma de todos os registros (créditos - débitos - compensações). Em qualquer momento, recalcular do zero deve dar o mesmo valor que o saldo cacheado.
- Soma global de pontos no sistema = sum(créditos) - sum(débitos). Invariante de fechamento.

### Rastreabilidade
- Todo registro tem origem identificável: apuracaoId, campanhaId, ou operacaoManualId.
- Compensação tem referência ao registro original que está compensando.
- Auditoria: usuário/sistema que disparou + timestamp + motivo.

### Independência de outras UoWs
- Excluir uma Campanha **nunca** remove registro de Histórico associado.
- Excluir uma Apuração **nunca** remove registro de Histórico já creditado.

## Mapa de cenários perigosos

| Cenário | Comportamento esperado | Risco se errado |
|---|---|---|
| Reapuração detecta crédito a menos | Adiciona registro de complemento positivo | Duplicação de pontos |
| Reapuração detecta crédito a mais | Adiciona registro de débito de compensação | Saldo negativo? [DECIDIR] |
| Campanha excluída tinha apuração FINAL | Histórico **preservado**, mesmo sem campanha | Perda de auditoria |
| Usuário resgatou pontos, depois reapuração reduz crédito | [DECIDIR — política de saldo negativo / compensação futura] | Disputa com cliente |

## Decisões pendentes

- [ ] Política de saldo negativo: permite ou bloqueia compensação se zera saldo?
- [ ] Janela de compensação retroativa máxima
- [ ] Operação de expurgo (LGPD) existe? Quem aprova?
- [ ] Snapshot/consolidação de período: apaga registros antigos ou só agrega para leitura?

## Notas de contexto

- Histórico é **dado de auditoria**. Bug que apaga histórico = potencial problema regulatório (Bacen, LGPD).
- O incidente de referência (exclusão de campanha apagando histórico) era cenário onde Histórico **não foi protegido** — ainda que não fosse direto, a cascata acidental afetaria.
