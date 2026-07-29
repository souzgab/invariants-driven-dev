# Context Harness

Protocolo para manter agentes de IA (Claude Code, Cursor, Codex, OpenHands, Antigravity, humanos)
alinhados ao estado real de um projeto ao longo de muitas sessões, sem depender da
memória do agente e sem estourar a janela de contexto.

Extraído e generalizado a partir do harness de contexto construído no projeto
[Olympo](https://github.com/zuss-enterprise/olympo) (branch `validacao-calibracao`),
onde sustentou dezenas de sessões de trabalho quantitativo (SDDs, validação de
calibração, medição de edge) sem scope drift nem retrabalho por esquecimento de
decisões já tomadas. Ver [`examples/olympo-case-study.md`](examples/olympo-case-study.md)
para o caso real, com números.

---

## ⚡ Replicação Rápida (Skill `harness-bootstrap`)

Para construir o harness em qualquer repositório de forma 100% guiada e em menos de 5 minutos, instale a skill interativa [`templates/skills/harness-bootstrap.md`](templates/skills/harness-bootstrap.md) no seu agente e execute:

```bash
/harness-bootstrap
```

A skill aplica o protocolo **Grill-Me** (entrevista sequencial uma pergunta por vez, com opções `(Recomendado)`):
1. Inspeciona a stack e a estrutura do repositório autonomamente.
2. Pergunta apenas o essencial (regras não-negociáveis, gates de maturidade, política de comandos).
3. Cria os artefatos (`AGENTS.md`, `STATUS.md`, `DECISIONS.md`, `update_harness.py`, `CLAUDE.md`, `GEMINI.md`).
4. Inicializa o estado com `STATUS_VIVO.json`.

---

## Problema que resolve

Todo cold-start de agente de IA em um projeto maduro enfrenta o mesmo dilema:

- Jogar o repo inteiro no prompt → estoura contexto, "lost in the middle", custo alto.
- Confiar na memória do agente entre sessões → não existe; cada sessão começa do zero.
- Confiar num resumo qualquer → fica desatualizado no mesmo dia e engana mais do que
  ajuda (ver [`docs/anti-padroes.md`](docs/anti-padroes.md), "resumo de compactação").

O sintoma observável é **scope drift**: o agente refaz trabalho já feito, reverte
decisões já tomadas e registradas, ou alucina o "porquê" de uma escolha de arquitetura
porque nunca teve acesso barato à razão real.

## Princípio central: Artefatos sobre Memória

> **Separe o Estado Executável (código) do Estado Cognitivo (contexto) em arquivos
> versionados, estruturados, e leia-os na ordem certa antes de agir.**

Isso não é documentação de projeto genérica — é *scaffolding de contexto* com uma
regra de leitura específica e um orçamento de tokens explícito. Quatro artefatos
cobrem o essencial:

| Arquivo | Papel | Muda a cada... |
|---|---|---|
| `STATUS.md` | Estado vivo: onde o projeto está, o que está em andamento, próxima ação concreta | sessão de trabalho |
| `DECISIONS.md` | Log **append-only** de decisões de arquitetura/design (D-001, D-002, ...) | decisão tomada |
| `AGENTS.md` | Convenções de código **extraídas do código existente**, não aspiracionais | raramente (é a camada estável) |
| `EVIDENCE.md` (opcional, específico de domínio) | Fonte única de veredito medido por comportamento/sinal do sistema | medição nova ou remedição |

Regra de ordem de leitura para qualquer agente em cold-start: **`STATUS.md` primeiro**
("você está aqui"), depois `AGENTS.md` (convenções estáveis), `DECISIONS.md` e
`EVIDENCE.md` sob demanda (grep pelo tópico, não leitura integral).

Ponteiros leves como [`templates/CLAUDE.md`](templates/CLAUDE.md) e [`templates/GEMINI.md`](templates/GEMINI.md) redirecionam diferentes ferramentas de IA diretamente para o `AGENTS.md` sem duplicação.

Detalhe de cada arquivo e por que a separação importa:
[`docs/01-framework-artefatos-sobre-memoria.md`](docs/01-framework-artefatos-sobre-memoria.md).

## Sustentação dinâmica (evita que o harness minta)

Resumos escritos à mão apodrecem no mesmo dia em que são escritos — aconteceu
literalmente no caso de origem (ver anti-padrão "resumo de compactação" acima). A
solução não é escrever resumos melhores, é **parar de escrever resumo nenhum à mão**:
um script determinístico extrai o estado direto do `git log` e dos próprios arquivos
do harness, e escreve um JSON de boot rápido.

```bash
python scripts/update_harness.py
# ✅ .agents/STATUS_VIVO.json atualizado
#    Branch: <branch atual>
#    Último commit: <hash> — <mensagem>
#    Tokens do harness: ~XXk
```

`STATUS_VIVO.json` é consumido **antes** de `STATUS.md` no cold-start — é o snapshot
mais recente, gerado por máquina, não por memória de sessão anterior. Template pronto
em [`templates/update_harness.py`](templates/update_harness.py); detalhe do ciclo em
[`docs/02-ciclo-de-sustentacao-dinamica.md`](docs/02-ciclo-de-sustentacao-dinamica.md).

## Orçamento de tokens explícito

O harness ativo tem um teto (no caso de origem, **~21-27k tokens** somando os 4
arquivos). Quando um arquivo cresce demais:

1. Sessões antigas de `STATUS.md` são compactadas para `docs/archive/STATUS_ARCHIVE.md`.
2. Decisões antigas de `DECISIONS.md` vão para `docs/archive/DECISIONS_ARCHIVE.md`.
3. O arquivo ativo mantém só o resumo vivo + um link `## Histórico completo` apontando
   pro archive.

O script de sustentação (`update_harness.py`) reporta a estimativa de tokens a cada
rodada — se o número não está visível, o teto não está sendo vigiado.

## Níveis de maturidade e gate

O harness não é tudo-ou-nada. Ele tem níveis, e subir de nível é uma decisão
explícita do dono do projeto, não algo que o agente decide sozinho:

- **Nível 1 (scaffolding, sem automação):** os 4 arquivos + specs de implementação
  com aceite testável (`docs/sdd/` no caso de origem) + suíte de validação empírica
  que já existia. Sem CI, sem pre-commit hook, sem framework de teste novo.
- **Nível 2+ (gated, exige aprovação explícita):** CI/pipelines, hooks de pré-commit,
  framework de teste novo, refactor fora do escopo de uma spec já aprovada, merge em
  branch de produção sem aprovação fase a fase.

A lista do que está **travado** deve estar escrita no próprio `AGENTS.md` — não como
regra abstrata, mas como checklist literal que qualquer agente lê antes de agir.
Detalhe: [`docs/03-niveis-de-maturidade-e-gate.md`](docs/03-niveis-de-maturidade-e-gate.md).

## Sinapse Viva & Política de Execução de Comandos (`COMMAND_POLICY`)

Para evitar que o agente execute comandos perigosos, caros ou destrutivos sem autorização, o ecossistema registra uma política explícita de execução:
- `auto`: Comandos seguros/read-only (ex: `pytest`, `git status`).
- `confirm`: Comandos que alteram estado ou usam recursos (ex: `sintetizar`, `build`).
- `never`: Ações sensíveis estritamente vedadas ao agente (ex: `decidir`, `git push --force`).

Detalhe: [`docs/07-sinapse-viva-e-politica-de-comandos.md`](docs/07-sinapse-viva-e-politica-de-comandos.md).

## Camada opcional: gate de evidência para sistemas que fazem afirmações

Se o projeto expõe algum tipo de veredito/score/sinal ao usuário final (não é
exclusivo de trading — vale para qualquer "o sistema recomenda X"), vale a pena um
quinto artefato: `EVIDENCE.md`. Regra única: **nenhum elemento com formato de
veredito aparece em nenhuma superfície sem uma linha em `EVIDENCE.md` que o
sustente**, com status num enum fechado (ex. `sem-medicao | sem-edge |
edge-condicional | com-edge | amostra-insuficiente`) e artefato que prove.
Mudar o cálculo de algo já exibido exige re-medição da linha correspondente antes do
merge. Ver [`templates/EVIDENCE.md`](templates/EVIDENCE.md) e
[`docs/05-gate-de-evidencia.md`](docs/05-gate-de-evidencia.md).

## Camada opcional avançada: memória semântica local (OSMA)

Para projetos grandes o suficiente para que "onde isso está implementado?" vire
gargalo, uma camada de indexação local em 4 tiers resolve sem depender de indexação
em nuvem:

```
Tier 1 (Semantic)    → embeddings locais (ex. LanceDB + SentenceTransformers)
Tier 2 (Topological) → repomap simplificado injetado no prompt
Tier 3 (Structural)  → grafo de AST local (ex. SQLite ou LadybugDB) — imports, classes, funções
Tier 4 (Active)      → cache dos diffs/arquivos salvos mais recentes
```

Exposta a agentes via um servidor MCP local (`search_codebase`,
`get_file_dependencies`, `get_codebase_repomap`), com um watcher debounced que
reindexa arquivos salvos. Isto é **estritamente opcional** e só compensa o custo de
manutenção quando o repo já é grande — não é ponto de partida. Detalhe:
[`docs/04-memoria-semantica-osma.md`](docs/04-memoria-semantica-osma.md).

## Linter de conformidade como guarda de regressão do harness

Regras não-negociáveis registradas em `AGENTS.md` (ex.: "todo indicador precisa de
guard de NaN antes de comparar com threshold", "nunca lookahead") tendem a ser
violadas silenciosamente por código novo se ninguém as verifica automaticamente. Um
linter estático baseado em AST, com uma classe de verificação por regra registrada,
fecha esse loop: toda vez que uma regra nova entra em `AGENTS.md`, uma verificação
correspondente entra no linter no mesmo commit. Ver
[`docs/06-linter-de-conformidade.md`](docs/06-linter-de-conformidade.md).

## Como adotar em um projeto novo

1. **Modo Automático (Skill)**: Execute `/harness-bootstrap` com a Skill [`templates/skills/harness-bootstrap.md`](templates/skills/harness-bootstrap.md) carregada no seu agente.
2. **Modo Manual**:
   - Crie os 4 arquivos na raiz (`AGENTS.md`) e em `docs/` (`STATUS.md`, `DECISIONS.md`), usando os templates em [`templates/`](templates/).
   - Crie os ponteiros [`CLAUDE.md`](templates/CLAUDE.md) e [`GEMINI.md`](templates/GEMINI.md).
   - Preencha `STATUS.md` com o estado real hoje.
   - Preencha `AGENTS.md` com convenções **extraídas do código já escrito**.
   - Registre a primeira decisão em `DECISIONS.md` (D-001).
   - Copie `scripts/update_harness.py` e rode-o ao final de cada sessão.
   - Escreva a seção "Nível 1 (ativo) / Nível 2+ (gated)" no fim do `AGENTS.md`.

## Relação com o protocolo de Invariantes deste repo

Este protocolo e o [Invariants-Driven Development](../README.md) (a raiz deste repo)
resolvem riscos diferentes e complementares no mesmo domínio — desenvolvimento
assistido por IA:

- **Invariants-Driven Development** trava o *"o que esta operação não pode tocar"*
  para uma única unidade de trabalho de alto risco (uma spec, uma PR).
- **Context Harness** trava o *"o agente sabe onde o projeto está e por que decisões
  passadas foram tomadas"* ao longo de toda a vida do projeto, sessão após sessão.

Um projeto Tier 1 (segundo os critérios de `guides/01-quando-usar.md`) se beneficia
dos dois ao mesmo tempo: harness para não perder contexto entre sessões, invariantes
para a unidade de trabalho de risco específica dentro de uma dessas sessões.
