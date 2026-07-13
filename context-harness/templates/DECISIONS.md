# DECISIONS — Log de Decisões

Registro **append-only** de decisões de arquitetura, design técnico e vereditos de
investigação. Nunca editar uma entrada já registrada — se uma decisão é revertida ou
invalidada, registre uma nova entrada que referencia e invalida a anterior.

IDs sequenciais únicos. Em branches paralelas, resolva colisão de ID na convergência
renumerando para manter ordem cronológica linear — nunca reaproveite um número já
usado noutro contexto.

---

## D-001

**Data:** <AAAA-MM-DD>
**Contexto:** <o que motivou a decisão — problema observado, pergunta em aberto>
**Decisão:** <o que foi decidido>
**Alternativas consideradas:** <o que mais foi cogitado, e por que foi descartado>
**Consequência:** <o que isso muda no código/processo dali pra frente>

<!--
Exemplo de invalidação de decisão anterior:

## D-050

**Contexto:** D-042 registrou veredito X com teste estatístico inválido (observações
sobrepostas).
**Decisão:** D-042 é invalidada. Novo teste, metodologia corrigida, resultado: Y.
-->
