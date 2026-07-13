# Caso real: harness do Olympo

Origem deste protocolo. Repositório `zuss-enterprise/olympo`, branch
`validacao-calibracao` (a mais atualizada no momento da extração, 2026-07-13) —
backend Python/FastAPI de análise técnica de cripto, com uma frente paralela de
validação empírica de sinais/indicadores.

## Estrutura de arquivos como implementada

```
olympo/
├── AGENTS.md                    convenções + seção "Harness — Nível 1 e gate"
├── CLAUDE.md                    apontador de compatibilidade → AGENTS.md
├── HARNESS.md                   documento explicando a arquitetura do harness em si
├── .agents/
│   └── STATUS_VIVO.json         snapshot gerado por scripts/update_harness.py
├── .harness/
│   └── compact_summary.md       resumo manual obsoleto (ver anti-padrão, docs/anti-padroes.md)
├── docs/
│   ├── STATUS.md                 estado vivo — ~2.5k tokens estimados
│   ├── DECISIONS.md              D-001 a D-050+ — ~15.1k tokens estimados
│   ├── EVIDENCE.md               ~5.6k tokens estimados
│   ├── ANALISE-CODIGO.md         análise crítica de código, lente de decisão pessoal
│   ├── archive/
│   │   ├── STATUS_ARCHIVE.md     ~70KB de histórico de sessões antigas
│   │   └── DECISIONS_ARCHIVE.md  ~60KB de decisões antigas
│   ├── sdd/
│   │   ├── SDD-01-estrutura-e-sinal.md
│   │   ├── SDD-02-evidencia-medida.md
│   │   ├── SDD-03-divergencia-rsi-pivot-fix.md
│   │   ├── SDD-04-derivativos-funding-oi-liquidacoes.md
│   │   └── SDD-05-operar-futuros.md
│   └── reviews/                  reviews de sessão anteriores
├── scripts/
│   ├── update_harness.py         sustentação dinâmica (ver templates/update_harness.py)
│   ├── osma_indexer.py           indexação inicial (Tier 1/3 do OSMA)
│   ├── osma_watcher.py           daemon de reindexação incremental
│   ├── osma_mcp.py               servidor MCP local (FastMCP)
│   └── osma_linter.py            linter de conformidade AST (5 regras)
└── tests/
    └── calibration/               suíte de validação empírica walk-forward causal
        ├── validate_signal_discrimination.py
        └── validate_pattern_thresholds.py
```

## `AGENTS.md` — o que ficou registrado como não-negociável

Extraído do código real (`app/internal/`), não aspiracional:

- TA-Lib sempre com `.astype(float)` antes de calcular — biblioteca falha/silencia
  com dtype errado.
- Guard de NaN antes de `.iloc[-1]` de qualquer indicador (indicador em warm-up é
  `NaN`, não zero).
- Sem lookahead — cálculo em `t` só usa dados até `t`; backtest determinístico
  (`random_seed` + `offline_mode`), reprodutível byte-a-byte.
- Thresholds nomeados em `config.py::Settings`, nunca mágicos inline.
- Exceção sempre logada com contexto e levantada específica — nunca engolida.
- Toda mudança em cálculo/score exibido roda a suíte de calibração antes e depois,
  os dois outputs commitados.
- `docs/EVIDENCE.md` é a fonte única de status de medição — sinal novo em qualquer
  superfície exige linha lá antes de produção.

E a seção "O que NÃO fazer", com item explícito: não tocar `routers/payments.py`
nem integração Firebase/Firestore sem pedir (dinheiro real + anti-replay) — exemplo
de como uma regra de "área sensível" fica registrada como parte do harness, não só
como comentário perdido no código.

## O ciclo de sustentação em ação

`STATUS_VIVO.json` real, gerado no dia da extração:

```json
{
  "generated_at": "2026-07-13T03:57:31.660139Z",
  "branch": "validacao-calibracao",
  "last_commit": {
    "hash": "5a7fdab",
    "message": "feat(harness): implement and test OSMA Quantitative Linter (D-049) ...",
    "date": "2026-07-13 00:51:36 -0300"
  },
  "active_sdd": "SDD-01-estrutura-e-sinal.md",
  "recent_decisions": ["D-049", "D-048", "D-047"],
  "harness_token_estimate": {
    "AGENTS.md": "~3.6k",
    "STATUS.md": "~2.5k",
    "DECISIONS.md": "~15.1k",
    "EVIDENCE.md": "~5.6k",
    "total": "~26.8k"
  }
}
```

## O anti-padrão real que motivou o ciclo dinâmico

`.harness/compact_summary.md`, escrito manualmente numa sessão de 2026-07-04, foi
marcado obsoleto no próprio arquivo assim que ficou claro o problema:

> "Este arquivo era um resumo de compactação de uma sessão de 2026-07-04 e ficou
> desatualizado no mesmo dia (dizia que SDD-01 R6/R7 não tinham começado — ambos
> foram implementados e commitados depois). Fonte de estado atual: docs/STATUS.md
> (sempre)."

Esse incidente concreto é o motivo pelo qual `scripts/update_harness.py` existe —
gerar o snapshot por máquina, não por memória de sessão.

## Gate de evidência em ação: dois casos de rebaixamento de veredito

1. **Smart Money scanner (D-040 invalidando D-029):** o veredito original
   `com-edge` nunca tinha teste de significância — só observação de que a direção
   batia em 4 células. Um Welch t-test rodado depois deu p=0,34/0,48 (bear
   24h/72h) e p=0,25/0,30 (bull 24h/72h) — nenhuma célula significativa nem sem
   correção de múltiplas comparações. Rebaixado para `sem-edge`.
2. **Open Interest divergence (D-050):** hipótese única pré-registrada, testada em
   nível de evento de mercado não-sobreposto nos 3 regimes (bear/bull/lateral).
   Resultado: p bruto 0,53/0,53/0,16, direção inconsistente entre regimes (bear e
   lateral concordam com a hipótese, bull inverte). Veredito: `sem-edge`.

Ambos os casos mostram o padrão-alvo: veredito com método nomeado, N, p-valor, e —
quando aplicável — a decisão anterior explicitamente invalidada em vez de
silenciosamente sobrescrita.

## Níveis declarados

`AGENTS.md` do Olympo fecha com a seção "Harness — Nível 1 (ativo) e gate", listando
literalmente o que está ativo (os arquivos acima + `tests/calibration/`) e o que
está trancado (CI/pipelines, framework de teste novo, refactor fora de SDD aprovada,
merge em `master` sem aprovação fase a fase, mudança de threshold de calibração sem
bateria antes/depois commitada).

## O que não foi generalizado neste protocolo

A camada OSMA (memória semântica local) e o linter de conformidade específico do
Olympo (`osma_linter.py`, 5 regras de TA/quant) são component específicos de
domínio — o protocolo genérico (`../docs/04-memoria-semantica-osma.md` e
`../docs/06-linter-de-conformidade.md`) descreve a estrutura reutilizável, sem
copiar as regras específicas de análise técnica de cripto, que não se aplicam fora
desse domínio.
