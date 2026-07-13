# Invariants-Driven Development

Protocolo para desenvolvimento assistido por IA em operações de **alto risco** — destrutivas, financeiras, ou que afetam histórico crítico.

## Problema que resolve

IAs (Devin, Copilot, Cursor, etc.) geram código que **parece aderente** mas viola regras de negócio implícitas. Exemplo real que motivou este repo:

> Solicitação: "implementar exclusão de campanha por período"
> IA gerou: `if (campanha.getId() != null) delete()`
> Comportamento real: apagava **todo histórico** de campanhas da loja, em qualquer período.

O problema não é a IA "ignorar instruções." O problema é que o pedido não especificou **o que a operação NÃO PODE tocar**.

## Solução em uma frase

Para operações de risco, escreve-se uma **spec com invariantes negativas explícitas** *antes* da IA gerar código. A IA recebe a spec, gera código + testes que validam cada invariante, e o humano revisa por checklist em vez de adivinhar gaps lendo lógica imperativa.

## Quando aplicar (e quando não)

| Tipo de operação | Tratamento |
|---|---|
| CRUD trivial, leitura, transformação reversível | Fluxo IA normal |
| Operação que escreve em estado compartilhado | Fluxo IA + revisão de duplicação |
| **Operação destrutiva, financeira, ou que afeta histórico** | **Spec com invariantes (este protocolo)** |

Estima-se que <10% das histórias de backlog sejam Tier 1, mas concentram 80%+ do risco de incidente sério.

## Estrutura do repo

```
.
├── README.md                         (este arquivo)
├── guides/
│   ├── 01-quando-usar.md             critérios para classificar Tier 1
│   ├── 02-como-escrever-spec.md      passo a passo do protocolo
│   ├── 03-como-revisar.md            checklist de revisão
│   └── 04-integrando-com-ia.md       prompt patterns para Devin/Copilot/Cursor
├── templates/
│   ├── invariants.md                 template principal (copie para cada UoW)
│   └── prompt-auditor.md             prompt para auditor LLM secundário
├── specs/
│   ├── campanha.md                   pré-preenchida com base na conversa
│   ├── apuracao.md                   pré-preenchida (revisar com tech lead)
│   ├── historico.md                  pré-preenchida (revisar com tech lead)
│   └── parametrizacao.md             pré-preenchida (revisar com tech lead)
├── examples/
│   └── exclusao-campanha-por-periodo.md   o caso real do incidente, retroativo
└── docs/
    └── conversations/
        └── 2026-05-04-genese-do-protocolo.md   transcript da conversa que originou isso
```

## Próximos passos

1. Leia `guides/01-quando-usar.md` e `guides/02-como-escrever-spec.md`
2. Sente com o tech lead, revise as 4 specs pré-preenchidas em `specs/`
3. Escolha **uma** operação Tier 1 do próximo sprint para piloto
4. Aplique o protocolo, mede tempo gasto e gaps prevenidos
5. Calibra o protocolo (formato, escopo) com base no piloto antes de expandir

## Princípio operacional central

> **A pergunta que destrava tudo é: "o que esta operação NÃO PODE tocar?"**
>
> Se você não consegue responder, a IA também não consegue. E vai inventar.

## Protocolo relacionado: Context Harness

Este repo reúne protocolos de disciplina para desenvolvimento assistido por IA.
Além das invariantes (acima, para uma unidade de trabalho de risco pontual), veja
[`context-harness/`](context-harness/) — protocolo para manter agentes de IA
alinhados ao estado real de um projeto ao longo de **muitas sessões**, sem depender
da memória do agente. Extraído e generalizado a partir de um harness real que
sustentou dezenas de sessões de trabalho quantitativo sem scope drift.
