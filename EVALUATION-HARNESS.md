# Avaliação Geral do Harness: Olympo, Pipeline e Invariants Repo

Este documento apresenta uma análise comparativa e recomendações para evolução da nossa infraestrutura de alinhamento de contexto, baseando-se nas implementações ativas do **Olympo** e **Cripto-Genesis-Pipeline**, e nos conceitos recém-introduzidos no repositório **Invariants-Driven Development** (branch `claude/harness-structure-docs-pyt004`).

---

## 📊 1. Diagnóstico do Estado Atual

### A. Olympo (Maturidade Alta)
- **O que possui:** Estrutura completa com `docs/STATUS.md`, `docs/DECISIONS.md`, `docs/EVIDENCE.md` e `AGENTS.md` locais. Possui o script `scripts/update_harness.py` que gera `.agents/STATUS_VIVO.json` e a suíte completa de calibração em `tests/calibration/`.
- **Camada Cognitiva (OSMA):** Arquitetura completa com LanceDB (semântico), SQLite (relacional/grafos) e servidor MCP local. Possui linter AST estático robusto (`osma_linter.py`).
- **Gargalos:** O setup do OSMA e LanceDB local adiciona fricção de infraestrutura (compilação binária) que às vezes pode falhar ou necessitar de re-indexação demorada.

### B. Cripto-Genesis-Pipeline (Maturidade Mista)
- **O que possui:** Arquivo `AGENTS.md` local detalhado e uma ponte de código inteligente e leve (`pipeline/osma_bridge.py`).
- **Gargalos:**
  - **Ausência de `update_harness.py`:** Não gera o arquivo `.agents/STATUS_VIVO.json` localmente.
  - **Descentralização do Contexto:** `STATUS.md` e `DECISIONS.md` residem fora do repositório, no Obsidian Vault (`Daily-Hub`). Isso impossibilita que IAs em *cold-start* leiam estes arquivos diretamente usando buscas de repositório locais padrão, a menos que tenham o caminho absoluto mapeado.
  - **Falta de Níveis de Maturidade:** O `AGENTS.md` local não estabelece explicitamente o que está bloqueado sob gates de Nível 2+.

---

## 🌟 2. O que mudou no Repo `invariants-driven-dev`

A versão consolidada no repositório de invariantes trouxe 3 grandes avanços que agregam valor imediato se portados de volta para nossos projetos:

1.  **Doutrina de Desenvolvimento Baseado em Invariantes (IDD):**
    - Formalizou o conceito de **Invariantes Negativas** ("o que a operação NÃO PODE alterar") para operações de alto risco (Tier 1).
    - Criou um template limpo (`templates/invariants.md`) e guias de auditoria adversarial com LLMs independentes.
2.  **Maturidade dos Arquivos e Orçamento de Tokens:**
    - Definiu claramente a limpeza por arquivamento (`docs/archive/`) quando o tamanho dos arquivos ultrapassa **~25k tokens** para manter o prompt enxuto e livre de atenuação (*lost in the middle*).
3.  **SQLite como Padrão de Grafos OSMA:**
    - Validou que para repositórios médios, o SQLite relacional tradicional substitui perfeitamente engines complexas de grafos (como KuzuDB) ou vetores (como LanceDB), eliminando dependências nativas problemáticas. A ponte `osma_bridge.py` criada no Pipeline é a materialização ideal desse princípio.

---

## 📈 3. Recomendações e Plano de Ação

### Recomendação 1: Adotar Invariantes Negativas nos Nossos Projetos
- **Por quê:** Olympo possui operações financeiras de alto risco (execução de ordens, cálculos de sinal, calibragem) e o Pipeline possui ingestão destrutiva/acumulativa de banco SQLite.
- **Ação:** Adicionar ao `AGENTS.md` de ambos os repositórios a seção **"Invariants-Driven Development"** instruindo os agentes a escreverem especificações de invariantes antes de codificar lógicas críticas.

### Recomendação 2: Trazer a Sustentação Dinâmica para o Pipeline
- **Por quê:** Permitir que agentes no Pipeline tenham acesso instantâneo ao `.agents/STATUS_VIVO.json` em *cold-starts*.
- **Ação:** Criar um script `scripts/update_harness.py` customizado no Pipeline que leia as informações diretamente do Obsidian Vault (`Daily-Hub/.../STATUS.md` e `DECISIONS.md`) e grave o arquivo JSON na raiz do repositório local.

### Recomendação 3: Unificar e Simplificar o OSMA no Olympo (SQLite FTS5)
- **Por quê:** Reduzir a complexidade operacional do LanceDB e dependências nativas.
- **Ação:** Substituir a engine de grafos e embeddings complexos do OSMA no Olympo pelo modelo de SQLite leve com FTS5 e busca textual aproximada (exatamente como implementado na ponte `osma_bridge.py` do Pipeline).
