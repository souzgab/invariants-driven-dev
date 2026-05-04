---
title: Gênese do Protocolo Invariants-Driven
date: 2026-05-04
context: Conversa entre dev backend (Itaú, gamificação de concessionária) e Claude
status: referência
---

# Gênese do protocolo

> Este documento preserva o raciocínio que originou o repositório. Não é
> documentação operacional — é registro do *porquê*. Quando alguém entrar no
> repo daqui 6 meses e perguntar "por que estamos fazendo assim?", esta é a
> resposta.

## O contexto

- Projeto: gamificação de concessionárias no Itaú
- Stack: Java + JPA, várias entidades acopladas
- Ferramentas de IA em uso: Devin, Copilot, Bedrock
- Já implementado: harness engineer próprio
- Já tentado: documentação guiada com Gherkin (ineficaz)

## O problema relatado

> "Sempre que desenvolvemos em um fluxo, IA diz que está aderente, mas ao
> debulhar profundamente sempre encontro algum gap, como funções com overlap,
> chamadas que não deveriam estar sendo feitas, parece que as IAs ignoram as
> instruções ou se deixam finalizar sem realmente ter repassado o fluxo todo
> do código."

## Diagnóstico inicial (que foi recalibrado depois)

Primeira hipótese: problema é estrutural. Solução proposta:
1. ArchUnit para regras de camada
2. Auditor LLM no harness
3. Documentação refinada (formatos consumíveis por IA)

## O caso real que mudou tudo

> "O gap mais recente que peguei foi na parametrização de exclusão de campanha,
> no fim de exclusão executava a mesma lógica em duas funções diferentes em
> services diferentes. E ainda apaga algo que não deveria, existia uma regra
> que deveria apagar a campanha por período, ou seja, de um mês específico,
> na verdade apagava tudo, desde que a última campanha não tivesse id null,
> o que sempre ocorreria, por sorte pegamos esse gap, pois apagaria todo
> histórico de campanha de alguma loja"

### Análise do incidente

Dois problemas distintos no mesmo PR:

| Problema | Categoria | O que pegaria |
|---|---|---|
| Mesma lógica em duas funções/services | Estrutural (overlap) | ArchUnit, revisão de duplicação |
| Exclusão apagava tudo em vez de apagar por período | **Semântico** (regra de negócio errada) | **Nada estrutural pega isso** |

O segundo é o que quase causou desastre. Recalibração: o problema dominante
é **especificação ambígua de regra de negócio**, não estrutura.

### Reconstrução do que aconteceu na cabeça da IA

1. Recebeu pedido tipo "implementar exclusão de campanha por período"
2. Viu entidade Campanha, viu padrão JPA de delete
3. **Inferiu** que "exclusão por período" significa filtrar por período e deletar
4. Implementou um filtro defensivo (`if id != null`) que parece prudente mas é semanticamente vazio
5. Não escreveu teste que valida "campanhas de OUTROS períodos permanecem"

A falha está no passo 5. **Teste que valida o efeito desejado sem validar a
ausência de efeito colateral é onde a IA mora.**

## A virada conceitual

Mudança de enquadramento:

> **Pare de pensar em "como ensinar a IA" e comece a pensar em "como tornar
> erro impossível de passar despercebido."** A IA é falível por design. A
> solução é arquitetura de verificação, não pedagogia.

E especificamente:

> **A pergunta operacional é: "o que essa operação NÃO PODE tocar?"**
> Toda operação destrutiva precisa dessa resposta explícita antes de uma
> linha ser escrita.

## A solução: três tipos de afirmação

Para regra de negócio crítica, especificar a operação por:

```
1. Pré-condição          → o que deve ser verdade ANTES
2. Pós-condição positiva → o que MUDA
3. Pós-condição negativa → o que NÃO PODE mudar  ← onde a IA mora
```

A invariante negativa é o que a IA não escreve sozinha — e é o que protege.

## Aplicação ao caso

Spec retroativa:
- Antes: existem N campanhas de L em P
- Depois: existem 0 campanhas de L em P
- **Invariante: campanhas de L fora de P têm contagem inalterada**
- **Invariante: campanhas de qualquer loja ≠ L têm contagem inalterada**
- **Invariante: total de campanhas no sistema = total anterior - N**

Cada invariante negativa vira teste. Revisão humana fica raso porque é
checklist (cada invariante tem teste correspondente?), não adivinhação.

## O escopo

Não aplicar em todas as histórias — vira fricção. Aplicar em **operações Tier 1**:

| Tipo de operação | Tratamento |
|---|---|
| CRUD trivial, leitura, transformação reversível | Fluxo IA normal |
| Operação que escreve em estado compartilhado | Fluxo IA + revisão de duplicação |
| **Operação destrutiva, financeira, ou que afeta histórico** | **Spec com invariantes** |

Estimativa: <10% das histórias, mas concentram 80%+ do risco.

## UoWs Tier 1 identificadas no domínio

- Campanha
- Apuração
- Histórico
- Parametrização

(Quatro specs pré-preenchidas no diretório `specs/`, para co-criação com tech lead.)

## O marcador `[DECIDIR]`

Ao escrever a spec, se não souber a regra: **não invente**, marca `[DECIDIR]`
e bloqueia desenvolvimento até resolver.

A IA, ao receber spec com `[DECIDIR]`, deve recusar gerar código e pedir
resolução. **Esse é exatamente o comportamento que faltou no incidente
original** — em vez de perguntar, a IA inventou `if id != null`.

## Os três passes de revisão

Em vez de uma revisão profunda (adivinhar gaps), três passes rasos:

1. **Spec está completa?** (sem ler código)
2. **Testes cobrem a spec?** (só testes)
3. **Código passa nos testes?** (último, mais raso)

Se passe 1 falha, devolve. Não revisa código contra spec ruim.

## Auditor LLM, recalibrado

Em vez de "encontre overlap" (estrutural), o prompt vira:

> Para cada invariante listada na spec, identifique:
> 1. Existe teste que verifica? Cite o nome.
> 2. Se não existe, escreva o teste.
> 3. O código satisfaz a invariante? Se não, aponte a linha exata.
> 4. Existe alguma invariante implícita do domínio que a spec não capturou?

O passo 4 é o valor — usa a IA como geradora de "o que mais pode dar errado",
área onde modelos são bons quando o prompt explicita a tarefa adversarial.

## Cenário de Falha (12 meses) considerado

1. **Time não adota porque "demora demais"**: se 30% das histórias viram Tier 1, vira teatro. Mitigação: começa com 3-5 operações conhecidamente perigosas.
2. **Specs viram documento desatualizado**: spec mora ao lado do código no mesmo PR; auditor recusa diff que muda código sem tocar spec.
3. **Invariantes negativas são genuinamente difíceis de enumerar**: cada incidente vira invariante nova retroativamente.

## Caso para a abordagem rejeitada (mais documentação narrativa)

Steelman honesto da posição que foi descartada:

- Documentação rica resolve onboarding humano também, não só IA
- Em domínios com regra de negócio implícita, prosa captura intenção que código não captura
- ArchUnit pega estrutura, não semântica de negócio

**Por que não prevaleceu**: o gap real foi semântico, não estrutural. A revisão
manual existente já estava aguentando os tier 2-3, mas falhou no tier 1 — e
tier 1 é onde a falha custa caro de verdade.

## Próximos passos definidos

1. Sentar com tech lead, co-criar as 4 specs (Campanha, Apuração, Histórico, Parametrização)
2. Escolher UMA operação Tier 1 do próximo sprint para piloto
3. Aplicar protocolo, medir tempo gasto e gaps prevenidos
4. Calibrar antes de expandir para o time inteiro

## Métricas de validação

Depois de 3-5 PRs Tier 1 sob o protocolo:

- Tempo total (spec + geração + revisão) vs fluxo antigo
- Gaps encontrados em revisão vs fluxo antigo
- Gaps encontrados em produção (objetivo: zero)
- Quantas vezes spec teve `[DECIDIR]` (sinal de tácito virando explícito — bom)

Se tempo total >2x e gaps em produção comparáveis, simplifica formato.
Se tempo ~1.3x e gaps em produção zerarem, está funcionando.
