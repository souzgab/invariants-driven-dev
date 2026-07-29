---
name: harness-bootstrap
description: A guided, interactive Grill-Me interview skill to construct a Context Harness (AGENTS.md, STATUS.md, DECISIONS.md, update_harness.py) in any repository.
---

# Harness Bootstrap Skill

Guide the developer through constructing a minimal, production-grade **Context Harness** for their repository using a step-by-step interactive interview (Grill-Me protocol).

---

## 🧭 Protocol & Execution Flow

### Phase 1: Automated Codebase Inspection (No User Questions Yet)

Before asking the user any questions, inspect the repository to build initial context:

1. **Detect Stack & Project Info**:
   - Inspect manifest files and lockfiles:
     - Python: `pyproject.toml`, `setup.py`, `requirements.txt`, `uv.lock`, `poetry.lock`, `Pipfile.lock`
     - Node/JS/TS: `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `package-lock.json`, `tsconfig.json`
     - Rust/Go/Java/C++/Make: `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `Makefile`
   - Identify package runners and execution wrappers (`uv run`, `poetry run`, `pnpm`, `bun`, `npm`, `cargo`, `make`, etc.).
   - Identify primary language, frameworks (FastAPI, Express, Angular, React, Next.js, etc.), and existing test setups (`pytest`, `vitest`, `jest`, `cargo test`, etc.).
2. **Domain Invariant Scanning & Rule Suggestions**:
   - **Python Stack**: Check for key libraries:
     - `fastapi` / `pydantic`: Suggest invariant *"Strict Pydantic schemas with explicit field validations; no `Model(**dict)` mass assignment in external API clients."*
     - `ta-lib` / `pandas`: Suggest invariant *"Cast series to `.astype(float)` before TA-Lib calculations; enforce NaN warmup guards before threshold checks."*
     - `ccxt` / exchange clients: Suggest invariant *"Enforce read-only API client permission checks (refuse execution if trade/withdraw permissions are enabled)."*
     - General Python: Suggest invariant *"Centralized exception handling; domain errors must never be suppressed as neutral values silently."*
   - **JS/TS Stack**: Check for key libraries/frameworks:
     - `@angular/core` / Signals: Suggest invariant *"State updates managed via Signals; preserve immutability in signal state changes."*
     - `i18n` / Translation maps: Suggest invariant *"Dual-key requirement (pt-BR / en-US) for all newly introduced UI labels."*
     - General Frontend: Suggest invariant *"No direct DOM mutation outside framework lifecycle; strict model mapping on API responses."*
3. **Fact-First Disk Manifest Baseline**:
   - Record all observed manifests, lockfiles, runners, TS configs, build scripts, and test configs on disk.
   - Establish disk evidence as the source of truth to prevent user memory errors from producing inaccurate harness configs.
4. **Detect Existing Context**:
   - Check if any `README.md`, `CONTRIBUTING.md`, or architecture docs exist.
   - Check git status (`git branch`, `git log -n 5`).

---

### Phase 2: Sequential Grill-Me Interview

Ask the user questions **strictly one at a time**. Never output a laundry list of questions. For every question, present a sensible `(Recommended)` option based on standard engineering best practices and the codebase inspection.

#### Question 0: Repository Topology Selection
> Choose the repository architecture for context & status management:
> - **Option A: Standalone Repo** (Self-contained codebase with local `docs/STATUS.md`, `docs/DECISIONS.md`, and `AGENTS.md`).
> - **Option B: User/Global Config Pointer** (Lightweight repository pointing to user-level global configuration like `~/.config/AGENTS.md` or `~/.claude/CLAUDE.md`).
> - **Option C: Central Workspace / Mono-repo Pointer** (Repository pointing to a parent mono-repo or central project status hub).
>
> **Recommended Option**: Infer Standalone Repo unless existing files or docs reference global config or a parent workspace.

#### Question 1: Non-Negotiables & Rules of the System
> Ask the user to clarify 2-3 core rules or invariants that can never be broken (e.g., "no unhandled NaN values in financial indicators", "no lookahead bias in backtests", "no direct production database writes without approval").
>
> **Recommended Option**: Present the automated Domain Invariant Suggestions detected during Phase 1 inspection (e.g., FastAPI Pydantic non-dict assignment, TA-Lib warmup NaN guards, CCXT read-only gate, or Angular Signals immutability and i18n dual-key requirements).

#### Question 2: Harness Maturity Level & Gated Actions
> Define what actions the AI agent is allowed to do autonomously (Level 1) vs what requires explicit human approval (Level 2+ Gated).
>
> **Recommended Option**: Level 1 (scaffolding, writing specs, running local tests) is active. Level 2+ (CI/CD pipeline changes, adding new test frameworks, refactoring out of scope, git pushes to main/master) is strictly gated.

#### Question 3: Command Execution Safety (`COMMAND_POLICY`)
> Establish execution permission tiers for workspace commands (`auto`, `confirm`, `never`).
>
> **Recommended Option**: Read-only commands (`git status`, `pytest`, `npm test`, package runner checks like `uv run pytest` or `pnpm test`) set to `auto`. High-cost or state-modifying commands set to `confirm`. Destructive actions (`git push`, DB drop, prod deploy) set to `never`.

#### Question 4: Evidence & Verification Gate (Optional EVIDENCE.md)
> Ask if the system makes assertions, predictions, or user-facing quantitative/scoring verdicts that require statistical/empirical evidence tracking (`docs/EVIDENCE.md`).
>
> **Recommended Option**: Explicitly skip `EVIDENCE.md` creation for non-quantitative repos (frontends, CLIs, standard REST APIs, utilities). Create `EVIDENCE.md` ONLY if the repository involves trading strategies, quantitative scoring, or ML empirical model signals.

---

### 🛡️ Ambiguity & Fallback Resilience Guards

To guarantee robust execution under incomplete, conflicting, or unhelpful user input:

1. **Blank & Ambiguous Response Fallback**:
   - If the user provides a blank answer, empty string, "I don't know", "whatever", "skip", or "default", **do not halt or fail**.
   - Automatically accept the `(Recommended)` option derived during Phase 1 inspection.
2. **Fact-First Disk Manifest Override**:
   - If user answers directly contradict files detected on disk during Phase 1 (e.g., user claims "no test framework" but `pytest.ini` or `vitest.config.ts` exists; or user claims "poetry" but `uv.lock` is present on disk), **disk manifest facts override user answers**.
   - Log the discrepancy and construct `AGENTS.md` and script configs based on actual disk evidence.

---

### Phase 3: Artifact Generation

Generate the core harness files in the target repository based on the answers and topology selected:

1. **`AGENTS.md`** (Root):
   - Canonical instructions for AI agents & developers.
   - Includes Stack, Layout, Coding Conventions, Domain Invariants, "O que NÃO fazer", Maturity Level Gates, Command Policy, and Selected Repository Topology.
2. **`docs/STATUS.md`**:
   - "You are here" status file containing current active branch, completed milestones, and immediate next action (or pointer file if Pointer/Vault topology selected).
3. **`docs/DECISIONS.md`**:
   - Append-only decision log starting with `D-001: Adoption of Context Harness`.
4. **`docs/EVIDENCE.md`** (Optional):
   - Created **ONLY** if Question 4 indicates quantitative/scoring verdicts. Explicitly skipped for non-quantitative repositories.
5. **`scripts/update_harness.py`**:
   - Zero-dependency Python script (`stdlib` only) that extracts git/file metadata and writes `.agents/STATUS_VIVO.json` (with non-git fallback support).
6. **`CLAUDE.md` & `GEMINI.md`**:
   - Compatibility pointers redirecting Claude Code, Gemini CLI, and Antigravity directly to `AGENTS.md`.

---

### Phase 4: Initial Boot & Verification

Run the update script to initialize the harness status:

```bash
python scripts/update_harness.py
```

Verify that `.agents/STATUS_VIVO.json` is generated with valid metadata (git or non-git fallback) and token count estimates.

---

## 🎯 Completion Criteria

Stop interviewing when core harness artifacts are created, `update_harness.py` executes cleanly without error in git or non-git mode, and `.agents/STATUS_VIVO.json` is present.

