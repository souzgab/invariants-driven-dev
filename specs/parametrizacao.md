---
unit_of_work: Parametrizacao
operation: <múltiplas — mapa da UoW>
tier: 1
status: draft
authors: []
last_updated: 2026-05-04
related_specs: [campanha.md, apuracao.md]
---

# Spec: Unit of Work — Parametrização

> Mapa da UoW. Ao implementar operação, copie `templates/invariants.md`.

## Contexto operacional

Parametrização é o ponto de entrada mensal: **CSV → SQS → persistência**.
É operação de lote, com efeito acumulado, e parametriza o comportamento de
campanhas que serão apuradas. Erro aqui se propaga para Apuração e Histórico.

Toda operação desta UoW que processa lote (CSV/SQS) é Tier 1 por definição.

## Operações Tier 1 conhecidas

- [ ] **`processarCsvParametrizacao`** — entrada via upload, valida e enfileira.
- [ ] **`consumirMensagemParametrizacao`** (SQS handler) — persiste regra.
- [ ] **`atualizarParametrizacao`** — Tier 1 se campanha já tem apuração em andamento.
- [ ] **`removerParametrizacao`** — Tier 1 (pode invalidar apuração corrente).
- [ ] **`aplicarParametrizacaoEmLote`** (CSV → N campanhas) — Tier 1.

## Invariantes globais da UoW

### Idempotência de fila
- Consumir a mesma mensagem SQS duas vezes (entrega duplicada) **não** duplica parametrização. Mecanismo: deduplicationId ou chave natural composta.
- Reprocessar CSV idêntico produz estado equivalente, não acumulado.

### Validação total antes de efeito parcial
- CSV é validado integralmente antes de qualquer mensagem ser enviada para SQS. Invariante: ou todas as linhas são enfileiradas, ou nenhuma. **Sem efeito parcial.**
- [DECIDIR — comportamento atual? confirmar]

### Atomicidade por linha
- Cada mensagem SQS representa uma unidade de parametrização. Falha em uma mensagem não impede as outras.
- Mensagem que falha após N tentativas vai para DLQ, não é descartada silenciosamente.

### Imutabilidade durante apuração ativa
- Parametrização de campanha com apuração IN_PROGRESS **não pode** ser alterada. Operação aborta com erro explícito. [DECIDIR — política]

### Auditoria
- Toda parametrização persistida tem: arquivo de origem, linha do arquivo, hash do conteúdo, usuário que subiu CSV, timestamp.

### Conservação
- Soma de N linhas válidas no CSV = N registros de parametrização persistidos. Sem duplicação. Sem perda silenciosa.

## Pontos críticos de cada operação

### processarCsvParametrizacao

| Aspecto | Comportamento |
|---|---|
| CSV malformado | Aborta tudo. Zero efeito. |
| CSV com algumas linhas inválidas | [DECIDIR — aborta tudo ou aceita parciais com relatório?] |
| CSV duplicado (mesmo arquivo subido 2x) | [DECIDIR — detecta por hash? aceita?] |
| CSV grande (10k+ linhas) | Streaming, não carrega tudo em memória |

### consumirMensagemParametrizacao

| Aspecto | Comportamento |
|---|---|
| Mensagem duplicada (entrega at-least-once) | Detecta via chave natural, no-op se já processou |
| Mensagem para campanha inexistente | DLQ, não erro silencioso |
| Mensagem para campanha em apuração | [DECIDIR — rejeita ou enfileira para depois?] |
| Falha de banco | Não acka mensagem, retry SQS |

## Decisões pendentes

- [ ] CSV parcialmente válido: aceita parciais ou aborta tudo?
- [ ] Detecção de CSV duplicado: por hash, por nome, ou aceita sem checar?
- [ ] Atualização de parametrização durante apuração ativa: bloqueia, agenda, ou força recálculo?
- [ ] Rollback de parametrização aplicada: existe operação? Como funciona?
- [ ] Política de DLQ: alarme automático? quem monitora?

## Cenários de incidente plausíveis

Pre-mortem específico desta UoW — usar para construir invariantes adicionais:

1. **CSV com erro semântico (não sintático)**: linhas válidas estruturalmente mas com regra de negócio errada (ex: pontuação 1000x maior). Invariante: validação de range / sanidade de valores antes de enfileirar.
2. **Reprocessamento de mês passado**: alguém sobe CSV de mês anterior por engano. Invariante: período da parametrização vs período de execução, alerta se discrepante.
3. **Concorrência com apuração**: parametrização chega enquanto apuração roda. Invariante: lock ou versionamento.

## Notas de contexto

- Volume mensal: <preencher — quantas linhas / quantos CSVs / quantas lojas>
- Janela de processamento: <preencher — primeiro dia útil do mês? throughput esperado?>
- Sistema upstream que gera o CSV: <preencher — humano via planilha? sistema integrado?>
