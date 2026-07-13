# EVIDENCE — Confiabilidade por sinal/veredito exibido

Fonte única de status de medição por sinal/recomendação/score exibido ao usuário
final. Regra: **nenhum elemento com formato de veredito aparece em nenhuma
superfície sem medição que o sustente.** Este arquivo é essa medição. Detalhe da
metodologia: [`../docs/05-gate-de-evidencia.md`](../docs/05-gate-de-evidencia.md).

**Gate:** sinal novo em qualquer superfície exige uma linha aqui antes de ir a
produção; mudança em cálculo já exibido exige re-medição da linha correspondente.

**Enum de `status`:** `sem-medicao` · `sem-edge`/`nao-confirmado` ·
`edge-condicional[contexto]` · `com-edge`/`confirmado` · `amostra-insuficiente`.

---

## <Área/categoria de sinais>

| Sinal | Cálculo | Superfícies | Status | Artefato | Contexto testado | Veredito |
|---|---|---|---|---|---|---|
| <nome> | `<arquivo>::<função>` | <onde aparece> | `sem-medicao` | — | — | Ainda não medido. |

<!--
Exemplo de linha preenchida:

| Divergência X | `analysis.py::detect_x` | payload `.x`, badge na UI | `sem-edge` | `results_x_v2.csv` (D-038) | regime A, B, C | Testado com [método], N=..., p=... — nenhuma célula significativa. Direção inconsistente entre A e C.
-->
