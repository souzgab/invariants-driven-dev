# Níveis de Maturidade e Gate

## Por que ter níveis

Um harness completo (scaffolding + automação + memória semântica + linter) é caro
demais para começar. E automação demais, cedo demais, tira do dono do projeto o
controle sobre decisões que deveriam ser explícitas (CI, refactors, merges em
produção). A solução é declarar níveis, e travar a progressão de nível atrás de uma
decisão humana explícita — nunca uma escolha unilateral do agente.

## Nível 1 — scaffolding ativo, sem automação de risco

O que compõe o Nível 1 (ver lista completa adotável em `templates/AGENTS.md`):

- Os 4 arquivos (`AGENTS.md`, `STATUS.md`, `DECISIONS.md`, `EVIDENCE.md` se
  aplicável).
- Specs de implementação com requisitos testáveis, uma por unidade de trabalho
  (equivalente ao `docs/sdd/SDD-XX-nome.md` do caso de origem — o nome do padrão de
  arquivo não importa, o que importa é ter requisito + critério de aceite escrito
  antes do código).
- Qualquer suíte de validação empírica que **já existia antes do harness** — o
  harness documenta e usa o que existe, não impõe framework de teste novo por conta
  própria.
- O script de sustentação dinâmica (`update_harness.py`).

Trabalho de Nível 1 = documentar, manter os artefatos atualizados, implementar specs
já aprovadas respeitando os gates delas. **Mudança de código fora de uma spec só
acontece com pedido direto e escopado.**

## Nível 2+ — trancado por gate, exige aprovação explícita do dono

Itens que **não devem ser feitos por iniciativa do agente**, mesmo que pareçam
melhorias óbvias:

- Configurar CI / pipelines / hooks de pré-commit.
- Introduzir framework de teste novo (ex. adicionar `pytest` a um projeto que só
  tinha scripts ad-hoc) ou escrever suíte estrutural nova.
- Refatorar código fora do escopo de uma spec já aprovada — "limpar de passagem"
  código morto ou duplicado é Nível 2, mesmo que o agente tenha certeza que é lixo.
- Merge em branch de produção sem aprovação explícita, fase a fase.
- Mudar threshold/peso/calibração de qualquer cálculo que já tenha um veredito
  medido em `EVIDENCE.md`, sem rodar e commitar a comparação antes/depois.

## Como declarar isso no `AGENTS.md`

A lista de Nível 2 precisa estar **escrita literalmente** no `AGENTS.md` do projeto,
não implícita. Um agente que lê "Nível 1 (ativo)" e "Nível 2+ (gated)" como duas
listas concretas sabe exatamente onde para e pergunta, sem precisar inferir a partir
de contexto vago. Template de seção pronta em
[`../templates/AGENTS.md`](../templates/AGENTS.md#harness--nível-1-ativo-e-gate).

## Subir de nível

Subir de Nível 1 para Nível 2 (ex.: o dono decide que agora quer CI) é uma decisão
como qualquer outra — registra-se em `DECISIONS.md`, atualiza-se a lista no
`AGENTS.md`, e só então a automação nova passa a ser permitida por padrão.
