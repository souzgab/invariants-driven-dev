# AGENTS.md — <Nome do Projeto>

> Fonte canônica de instruções de projeto, agnóstica de ferramenta. Lida por
> qualquer agente/CLI que suporte a convenção `AGENTS.md` (Claude Code, Cursor,
> Aider, Codex CLI, GitHub Copilot coding agent, etc.). Se existirem apontadores de
> compatibilidade como `CLAUDE.md`, `GEMINI.md`, etc. neste repo, eles são apenas
> redirecionadores de compatibilidade — este arquivo (`AGENTS.md`) é a fonte única da verdade.

Convenções **extraídas do código existente**. Não são aspiracionais: descrevem o que
o repo já faz hoje. Ao escrever código novo, siga estes padrões; ao divergir,
registre em [docs/DECISIONS.md](docs/DECISIONS.md).

**Antes de qualquer coisa, leia [docs/STATUS.md](docs/STATUS.md)** — é o "você está
aqui": branch atual, o que está em andamento, próxima ação concreta. Este arquivo
(AGENTS.md) é convenção estável; STATUS.md é o estado vivo que muda a cada sessão.

---

## Stack

<!-- Linguagem, framework, libs principais, infra de deploy. -->

## Layout

<!-- Árvore de diretórios com uma linha de anotação por pasta relevante. -->

## Convenções de código

<!-- Nomenclatura, docstrings, imports, padrões de async/threading, etc. -->

## Convenções não-negociáveis

<!-- Regras que corrompem o sistema se quebradas — a seção mais valiosa deste
     arquivo. Cada regra aqui deveria, idealmente, ter uma verificação
     correspondente no linter de conformidade (ver docs/06-linter-de-conformidade.md). -->

## O que NÃO fazer

<!-- Armadilhas conhecidas, específicas deste projeto — coisas que já foram
     tentadas e deram errado, ou áreas sensíveis (dinheiro, dados de produção)
     que não devem ser tocadas sem pedido explícito. -->

## Testes

<!-- Como rodar, o que é gate real vs. o que é só smoke test que sempre "passa". -->

## Comandos

```bash
# Run
# Test
# Lint
```

## Política de Comandos (COMMAND_POLICY)

Toda ação ou comando no repositório segue uma das três categorias de permissão (ver `docs/07-sinapse-viva-e-politica-de-comandos.md`):

- **`auto`**: Comandos read-only ou de verificação segura. O agente pode disparar autonomamente (ex: `pytest -q`, `git status`, `ritual status`).
- **`confirm`**: Comandos que consomem recursos (LLM, APIs) ou alteram estados locais. Exigem confirmação explícita do operador antes de disparar (ex: `ritual sintetizar`, `npm run build`).
- **`never`**: Comandos de alta sensibilidade ou tomada de decisão humana. Estritamente proibidos de serem disparados pelo agente via chat/ferramentas (ex: `ritual decidir`, `ritual fechar`, `git push --force`, `deploy prod`).

---

## Manutenção e Fluxo do Harness

Este projeto utiliza um harness de contexto de-biasado e sustentação automática.
Convenções gerais: este arquivo. Estado vivo: [docs/STATUS.md](docs/STATUS.md).
Decisões: [docs/DECISIONS.md](docs/DECISIONS.md). Medição de sinais/vereditos (opcional para repositórios não-quantitativos): [docs/EVIDENCE.md](docs/EVIDENCE.md).

### Topologias do Repositório

O harness suporta três arquiteturas de integração:
- **Standalone**: Repositório autônomo contendo todos os artefatos (`STATUS.md`, `DECISIONS.md`, `AGENTS.md`) localmente em `docs/` ou na raiz.
- **Pointer**: Repositório leve cujos arquivos servem como ponteiros para um repositório canônico/irmão.
- **Vault-Integrated**: O repositório reflete/integra seu estado vivo e decisões em um vault central externo (ex: Obsidian), mantendo specs de código em `docs/specs/` ou `docs/sdd/`.

> **Nota sobre `EVIDENCE.md`**: O arquivo `docs/EVIDENCE.md` é **opcional**, aplicável a repositórios quantitativos/preditivos que expõem sinais/scores. Repositórios não-quantitativos/não-preditivos podem omiti-lo.

Ao finalizar qualquer sessão de trabalho com mudanças materiais, execute:
```bash
python scripts/update_harness.py
```
O script atualiza `.agents/STATUS_VIVO.json` com o estado atual da branch, último
commit e arquivos modificados. Este JSON é a fonte dinâmica compacta de contexto
para agentes em cold-start — leia-o ANTES de `STATUS.md` para obter o snapshot mais
recente do projeto.

## Harness — Nível 1 (ativo) e gate

Este repo está no **Nível 1** do harness: scaffolding de contexto leve, sem
automação de risco.

**Ativo (Nível 1):**
- `AGENTS.md` — este arquivo, convenções reais, fonte canônica
- `docs/STATUS.md` — estado vivo: o que está feito, em andamento, próxima ação
- `docs/DECISIONS.md` — log de decisões (append-only)
- `docs/EVIDENCE.md` — status de medição por sinal/veredito exibido (opcional para repositórios não-quantitativos)
- Specs de implementação com requisitos testáveis (`docs/specs/` ou equivalente)
- Suíte de validação empírica já existente (não framework novo)

**🔒 Travado por gate (Nível 2+), NÃO fazer sem aprovação explícita do dono:**
- Configurar CI / pipelines / hooks de pré-commit
- Introduzir framework de teste novo ou escrever suíte estrutural nova
- Refatorar código fora do escopo de uma spec já aprovada
- Merge em branch de produção sem aprovação explícita, fase a fase
- Mudar threshold/peso/cálculo de qualquer sinal com veredito em `EVIDENCE.md` sem
  rodar e commitar a comparação antes/depois

Trabalho de Nível 1 = documentar, manter os artefatos acima atualizados, e
implementar specs já especificadas respeitando os gates delas. Mudança de código
fora de spec só com pedido direto e escopado.
