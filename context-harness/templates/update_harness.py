"""Update Harness
Atualiza .agents/STATUS_VIVO.json com o estado atual do projeto, extraído
direto do git e dos arquivos do harness — nunca escrito à mão.

Ver ../docs/02-ciclo-de-sustentacao-dinamica.md para o racional.
Adapte os caminhos abaixo (STATUS_PATH, DECISIONS_PATH, HARNESS_FILES,
active spec regex) à convenção do seu projeto.
"""

import os
import re
import json
import subprocess
from datetime import datetime, timezone

STATUS_PATH = "docs/STATUS.md"
DECISIONS_PATH = "docs/DECISIONS.md"
HARNESS_FILES = {
    "AGENTS.md": "AGENTS.md",
    "STATUS.md": "docs/STATUS.md",
    "DECISIONS.md": "docs/DECISIONS.md",
    "EVIDENCE.md": "docs/EVIDENCE.md",
}
# Ajuste ao padrão de nome de spec/tarefa do seu projeto (ex. "SDD-01-nome",
# "TASK-123", "RFC-04"). Deixe None para desabilitar a extração.
ACTIVE_SPEC_PATTERN = r"(SDD-\d+-[a-zA-Z0-9\-_.]+)"


def run_git_command(args):
    try:
        res = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def main():
    git_root = run_git_command(["git", "rev-parse", "--show-toplevel"])
    if not git_root:
        print("⚠️  Não foi possível detectar a raiz do git. Rode dentro de um repositório git.")
        exit(1)

    os.chdir(git_root)

    branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"

    commit_info = run_git_command(["git", "log", "-1", "--format=%h|%s|%ai"])
    last_commit = {"hash": "unknown", "message": "unknown", "date": "unknown"}
    if commit_info:
        parts = commit_info.split("|")
        if len(parts) >= 3:
            last_commit = {"hash": parts[0], "message": parts[1], "date": parts[2]}

    recent_files_output = run_git_command(["git", "log", "-5", "--name-only", "--format="])
    recent_files = []
    if recent_files_output:
        seen = set()
        for line in recent_files_output.split("\n"):
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                recent_files.append(line)

    active_spec = None
    if ACTIVE_SPEC_PATTERN and os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            match = re.search(ACTIVE_SPEC_PATTERN, f.read())
            if match:
                active_spec = match.group(1)

    recent_decisions = []
    if os.path.exists(DECISIONS_PATH):
        with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
            matches = re.findall(r"^## (D-\d+)", f.read(), re.MULTILINE)
            if matches:
                recent_decisions = list(reversed(matches))[:3]

    token_estimates = {}
    total_tokens = 0
    for name, path in HARNESS_FILES.items():
        if os.path.exists(path):
            tokens = int(os.path.getsize(path) / 4)
            token_estimates[name] = f"~{int(tokens / 100) / 10}k" if tokens >= 1000 else f"~{tokens}"
            total_tokens += tokens
        else:
            token_estimates[name] = "~0"
    token_estimates["total"] = (
        f"~{int(total_tokens / 100) / 10}k" if total_tokens >= 1000 else f"~{total_tokens}"
    )

    os.makedirs(".agents", exist_ok=True)
    status_vivo = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generated_by": "scripts/update_harness.py",
        "branch": branch,
        "last_commit": last_commit,
        "recent_files_modified": recent_files[:10],
        "active_spec": active_spec,
        "recent_decisions": recent_decisions,
        "harness_token_estimate": token_estimates,
    }

    with open(".agents/STATUS_VIVO.json", "w", encoding="utf-8") as f:
        json.dump(status_vivo, f, indent=2, ensure_ascii=False)

    print("✅ .agents/STATUS_VIVO.json atualizado")
    print(f"   Branch: {branch}")
    print(f"   Último commit: {last_commit['hash']} — {last_commit['message']}")
    print(f"   Tokens do harness: {token_estimates['total']}")


if __name__ == "__main__":
    main()
