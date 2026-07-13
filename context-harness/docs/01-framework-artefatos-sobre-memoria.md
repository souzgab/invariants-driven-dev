# Framework "Artefatos sobre Memória"

## Por que separar Estado Executável de Estado Cognitivo

Um repositório já documenta o "Estado Executável" — o código faz o que faz, e
testes/tipos garantem isso razoavelmente bem. O que falta é o **Estado Cognitivo**:
por que o código está do jeito que está, o que já foi tentado e rejeitado, o que
está em andamento agora, e qual é a próxima ação concreta. Sem um lugar dedicado
para isso, cada sessão de agente reconstrói esse contexto lendo o histórico de
commits (caro, ambíguo) ou não reconstrói (e refaz/reverte trabalho).

A separação em 4 arquivos não é arbitrária — cada um tem uma cadência de mudança e
uma pergunta que responde:

### `STATUS.md` — "onde eu estou?"

- Muda a cada sessão de trabalho material.
- Tem duas partes: um **resumo vivo**, sempre reescrito para refletir o estado atual
  (curto, no topo), e um **histórico** completo movido para um arquivo de archive
  assim que o resumo cresce demais (ver `03-niveis-de-maturidade-e-gate.md` sobre
  orçamento de tokens).
- Primeira linha de qualquer sessão nova: "branch de trabalho: X. Último marco: Y.
  Próxima ação: Z." Se essa frase não está lá, o arquivo não está cumprindo o papel.
- **Não é changelog.** Changelog é história; `STATUS.md` é "agora".

### `DECISIONS.md` — "por que foi feito assim?"

- **Append-only.** Nunca se edita uma decisão já registrada — se ela foi revertida,
  registra-se uma nova decisão que referencia e invalida a anterior (ex. "D-050
  invalida D-042: o teste original tinha observações sobrepostas").
- Cada entrada tem ID sequencial único (`D-001`, `D-002`, ...). Em times/branches
  paralelas, o IDs podem colidir — resolva na convergência renumerando para manter
  ordem cronológica linear, nunca reaproveitando um número já usado noutro contexto.
- Serve tanto para decisões de arquitetura quanto para vereditos de investigação
  ("testamos X, resultado foi sem-edge, não vale a pena perseguir").

### `AGENTS.md` — "quais são as regras daqui?"

- **Extraído do código existente, não aspiracional.** Se o código não faz X, não
  escreva "sempre fazemos X" em `AGENTS.md` — escreva o que o código realmente faz,
  e se X é desejável, registre como decisão pendente em `DECISIONS.md` ou como
  próximo passo em `STATUS.md`.
- É a camada mais estável dos quatro — muda quando uma convenção nova se cristaliza,
  não a cada sessão.
- Convém ser agnóstico de ferramenta (não "só para Claude Code") se múltiplos
  agentes/CLIs tocam o projeto — um arquivo com nome de convenção reconhecida
  (`AGENTS.md`) funciona como fonte única, com apontadores de compatibilidade
  (`CLAUDE.md`, etc.) redirecionando para ele em vez de duplicar conteúdo.
- Contém as seções "não-negociável" (regras que corrompem o sistema se quebradas) e
  "o que NÃO fazer" (lista explícita de armadilhas conhecidas) — mais valiosas que
  qualquer descrição de arquitetura, porque é o que evita repetir erro já pago uma
  vez.

### `EVIDENCE.md` — "o que já foi medido, e o que ainda é achismo?" (opcional)

Ver [`05-gate-de-evidencia.md`](05-gate-de-evidencia.md) — só se aplica a sistemas
que expõem algum tipo de veredito/recomendação/score.

## Ordem de leitura em cold-start

```
1. STATUS_VIVO.json (se existir — ver 02-ciclo-de-sustentacao-dinamica.md)
2. STATUS.md         (resumo vivo, não o histórico)
3. AGENTS.md         (convenções — ler por completo, é estável e compacto)
4. DECISIONS.md      (grep pelo tópico da tarefa atual, não leitura integral)
5. EVIDENCE.md       (se a tarefa toca algum sinal/veredito exibido)
```

Ler `DECISIONS.md`/`EVIDENCE.md` na íntegra em todo cold-start é o próprio problema
que o harness existe para evitar (token bloat). Grep dirigido pelo que a tarefa
atual precisa é o modo de uso correto.
