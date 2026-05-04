---
unit_of_work: Apuracao
operation: <múltiplas — mapa da UoW>
tier: 1
status: draft
authors: []
last_updated: 2026-05-04
related_specs: [campanha.md, historico.md]
---

# Spec: Unit of Work — Apuração

> Mapa da UoW. Ao implementar operação, copie `templates/invariants.md`.

## Operações Tier 1 conhecidas

- [ ] **`apurarCampanha`** — calcula resultado, gera pontos. Tier 1 (financeiro).
- [ ] **`reapurarCampanha`** / recálculo retroativo — Tier 1 (toca histórico).
- [ ] **`finalizarApuracao`** — muda status para FINAL, dispara crédito de pontos. Tier 1.
- [ ] **`reverterApuracao`** — Tier 1 (destrutivo + financeiro). [DECIDIR — operação existe? deve existir?]
- [ ] `consultarApuracao` — Tier 3 (leitura).

## Invariantes globais da UoW

### Determinismo
- Apurar a mesma campanha com os mesmos eventos de entrada **sempre** produz o mesmo resultado. Se não produz, há bug.
- Apuração depende exclusivamente de: parametrização da campanha + eventos no período + estado das lojas no período. Nunca de "agora".

### Idempotência
- Chamar `apurarCampanha` duas vezes na mesma campanha em estado IN_PROGRESS deve produzir resultado equivalente (não duplicar pontos, não duplicar registros).
- Apuração FINAL não pode ser reapurada sem operação explícita `reapurarCampanha`. [DECIDIR — confirmar]

### Conservação financeira
- Soma de pontos creditados em uma apuração = soma calculada pela parametrização. Sem desvio. Sem arredondamento implícito.
- Crédito em Histórico de pontos é gerado **uma única vez** por apuração FINAL. Reapuração ajusta via delta, não duplica.

### Imutabilidade
- Apuração com status FINAL é imutável. Mudanças requerem reapuração explícita, que gera nova versão e preserva a anterior. [DECIDIR — versionar ou substituir com auditoria?]

## Mapa de efeitos por operação

| Operação | Lê de | Escreve em | Dispara |
|---|---|---|---|
| apurarCampanha | Parametrização, Eventos, Loja | Apuração (status IN_PROGRESS) | nada |
| finalizarApuracao | Apuração | Apuração (status FINAL), Histórico | evento `ApuracaoFinalizada` em SQS |
| reapurarCampanha | Apuração FINAL anterior, Eventos | Apuração (nova versão), Histórico (delta) | evento `ApuracaoReapurada` |

## Decisões pendentes

- [ ] Versionamento de apuração reapurada: nova linha ou substituição com auditoria?
- [ ] Reapuração afeta pontos já resgatados pelo usuário? Política de compensação?
- [ ] Janela máxima para reapuração retroativa (ex: até 90 dias)?
- [ ] Apuração de campanha excluída: o que acontece?

## Notas de contexto

- Apuração é o coração financeiro da gamificação. Bug aqui = pontos errados ao usuário = problema regulatório / de imagem.
- Reapuração é caso clássico de operação Tier 1 que parece simples mas tem cascata complexa em Histórico.
