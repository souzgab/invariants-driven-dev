# Como escrever uma spec com invariantes

A spec não é documentação narrativa. É um **contrato** que a IA consome e que o humano usa como checklist de revisão. Formato denso, sem prosa.

## Estrutura obrigatória

Toda spec tem cinco seções, nesta ordem:

```
1. Identificação    → o que é a operação, qual UoW pertence
2. Pré-condições    → o que deve ser verdade ANTES de executar
3. Efeito           → o que MUDA (pós-condição positiva)
4. Invariantes      → o que NÃO PODE mudar (pós-condição negativa)
5. Casos limite     → comportamento em entrada vazia, duplicada, fronteira
```

A seção 4 é a que protege você. Sem ela, a spec não é spec — é descrição.

## A pergunta que destrava cada seção

| Seção | Pergunta para responder |
|---|---|
| Pré-condições | "Em que estado o sistema precisa estar para essa operação fazer sentido?" |
| Efeito | "O que muda no banco / no estado quando isso roda com sucesso?" |
| **Invariantes** | **"O que essa operação NÃO PODE tocar, sob hipótese alguma?"** |
| Casos limite | "O que acontece se a entrada for vazia? duplicada? na fronteira?" |

## Heurísticas para descobrir invariantes negativas

Se você travou na seção de invariantes, use estes gatilhos:

### Gatilho 1: dimensões de filtro
Para cada filtro/critério da operação, escreva a **negação** como invariante.
- Operação filtra por loja L → invariante: "lojas ≠ L permanecem inalteradas"
- Operação filtra por período P → invariante: "registros fora de P permanecem"
- Operação filtra por status S → invariante: "registros com status ≠ S permanecem"

### Gatilho 2: agregados do mesmo domínio
Para cada entidade relacionada, decidir explicitamente: cascata, preserva, ou erro?
- Excluir Campanha → e os registros de Apuração derivados? e o Histórico?
- Resetar pontuação → e os registros de Movimentação? e os benefícios resgatados?

### Gatilho 3: contagens totais
Toda operação destrutiva ou financeira deve ter pelo menos uma invariante de **conservação**:
- "Total de campanhas no sistema = total anterior - N removidas"
- "Soma de pontos de outros usuários = soma anterior"
- "Quantidade de registros de auditoria = quantidade anterior + 1"

### Gatilho 4: efeitos colaterais externos
Para cada integração:
- "Não dispara e-mail para usuários fora do escopo"
- "Não publica em fila X"
- "Não chama API parceiro Y"

### Gatilho 5: histórico
Toda operação que toca dado mutável deve responder:
- Há registro de auditoria? Qual?
- O dado anterior é recuperável? Como?
- Quem disparou a operação fica registrado?

## Casos limite obrigatórios

Para Tier 1, sempre cobrir:

- **Entrada vazia** — operação é no-op, não erro
- **Entrada duplicada** — idempotência: rodar duas vezes = rodar uma vez
- **Fronteira de filtro** — registro exatamente na borda do período/range
- **Concorrência** — duas execuções simultâneas
- **Falha parcial** — operação aborta no meio: rollback total ou parcial?

## Marcador `[DECIDIR]`

Toda vez que ao escrever a spec você não souber a regra, **não invente**. Marque `[DECIDIR]` e bloqueie o desenvolvimento até resolver com produto / tech lead.

Exemplo:
```
- Histórico de pontuação derivado de campanhas removidas: [DECIDIR — preserva? cascata? soft delete?]
```

A IA, ao receber spec com `[DECIDIR]`, deve recusar gerar código e pedir resolução. Esse é exatamente o comportamento que faltou no incidente original — em vez de perguntar, a IA inventou `if id != null`.

## Tempo esperado

| Atividade | Tempo |
|---|---|
| Spec de operação simples (1 entidade, sem cascata) | 15-20 min |
| Spec de operação média (2-3 entidades, alguma cascata) | 30-45 min |
| Spec de operação complexa (lote, multi-agregado, integração) | 1-2h |

Se está levando >2h, provavelmente o escopo está grande demais — quebra a operação em duas.

Se está levando <10min, provavelmente está superficial — releia gatilhos 1 a 5.

## Quem escreve

| Tipo de regra | Quem decide |
|---|---|
| Pré-condições técnicas (entidade existe, etc.) | Dev |
| Efeito (o que a operação faz) | Dev + Tech Lead |
| **Invariantes** | **Dev + Tech Lead + Produto (quando regra de negócio)** |
| Casos limite | Dev (com QA opcional) |

Invariantes negativas frequentemente revelam regras de negócio que **ninguém escreveu antes**. Esse é o valor — explicitar o tácito antes que vire incidente.
