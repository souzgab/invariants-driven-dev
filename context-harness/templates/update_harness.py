"""Update Harness
Atualiza .agents/STATUS_VIVO.json com o estado atual do projeto, extraído
direto do git e dos arquivos do harness — nunca escrito à mão.

Ver ../docs/02-ciclo-de-sustentacao-dinamica.md para o racional.
Adapte os caminhos abaixo (STATUS_PATH, DECISIONS_PATH, HARNESS_FILES,
active spec regex) à convenção do seu projeto.
"""

import os
import sys
import re
import json
import subprocess
from datetime import datetime, timezone

STATUS_PATH = "docs/STATUS.md"
DECISIONS_PATH = "docs/DECISIONS.md"
HARNESS_FILES = {
    "AGENTS.md": "AGENTS.md",
    "CLAUDE.md": "CLAUDE.md",
    "GEMINI.md": "GEMINI.md",
    "STATUS.md": "docs/STATUS.md",
    "DECISIONS.md": "docs/DECISIONS.md",
    "EVIDENCE.md": "docs/EVIDENCE.md",
    "STATUS_VIVO.json": ".agents/STATUS_VIVO.json",
}
# Ajuste ao padrão de nome de spec/tarefa do seu projeto (ex. "SDD-01-nome",
# "SDD-05", "TASK-123", "DEC-044", "R7", "SPEC-02"). Deixe None para desabilitar a extração.
ACTIVE_SPEC_PATTERN = r"(\b(?:SDD|TASK|DEC|SPEC|R)-?\d+(?:-[a-zA-Z0-9\-_.]+)?)"


def run_git_command(args):
    try:
        res = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=10,
        )
        return res.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def main():
    project_root = os.getcwd()
    git_root = run_git_command(["git", "rev-parse", "--show-toplevel"])

    if git_root:
        os.chdir(git_root)
        branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
        if branch in ("HEAD", "unknown"):
            detached_hash = run_git_command(["git", "rev-parse", "--short", "HEAD"])
            if detached_hash:
                branch = f"detached at {detached_hash}"

        commit_info = run_git_command(["git", "log", "-1", "--format=%h\x1f%s\x1f%ai"])
        last_commit = {"hash": "unknown", "message": "unknown", "date": "unknown"}
        if commit_info:
            parts = commit_info.split("\x1f", 2)
            if len(parts) >= 3:
                last_commit = {"hash": parts[0], "message": parts[1], "date": parts[2]}

        recent_files = []
        seen = set()

        uncommitted_output = run_git_command(["git", "status", "--porcelain"])
        if uncommitted_output:
            for line in uncommitted_output.split("\n"):
                line = line.strip()
                if line and len(line) >= 3:
                    path = line[2:].strip()
                    if " -> " in path:
                        path = path.split(" -> ")[-1]
                    path = path.strip('"')
                    if path and path not in seen:
                        seen.add(path)
                        recent_files.append(path)

        recent_files_output = run_git_command(["git", "log", "-5", "--name-only", "--format="])
        if recent_files_output:
            for line in recent_files_output.split("\n"):
                line = line.strip()
                if line and line not in seen:
                    seen.add(line)
                    recent_files.append(line)
    else:
        # Graceful non-git fallback
        branch = "non-git"
        last_commit = None
        recent_files = []
        ignore_dirs = {".git", ".venv", "node_modules", ".agents", "__pycache__", ".pytest_cache", "dist", "build"}
        file_mtimes = []
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, project_root)
                try:
                    mtime = os.path.getmtime(full_p)
                    file_mtimes.append((mtime, rel_p))
                except (OSError, IOError):
                    pass
        file_mtimes.sort(key=lambda x: x[0], reverse=True)
        recent_files = [rel_p for _, rel_p in file_mtimes[:10]]

    active_spec = None
    if ACTIVE_SPEC_PATTERN and os.path.exists(STATUS_PATH):
        try:
            with open(STATUS_PATH, "r", encoding="utf-8") as f:
                match = re.search(ACTIVE_SPEC_PATTERN, f.read())
                if match:
                    active_spec = match.group(1)
        except (OSError, IOError):
            pass

    recent_decisions = []
    if os.path.exists(DECISIONS_PATH):
        try:
            with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
                matches = re.findall(r"^## (D-\d+)", f.read(), re.MULTILINE)
                if matches:
                    recent_decisions = list(reversed(matches))[:3]
        except (OSError, IOError):
            pass

    token_estimates = {}
    total_tokens = 0
    for name, path in HARNESS_FILES.items():
        actual_path = None
        candidates = [
            path,
            os.path.join(project_root, path),
            os.path.join("templates", os.path.basename(path)),
            os.path.join(project_root, "templates", os.path.basename(path)),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                actual_path = candidate
                break

        if actual_path:
            try:
                with open(actual_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                tokens = int(len(content.encode("utf-8")) / 3.45)
                token_estimates[name] = f"~{int(tokens / 100) / 10}k" if tokens >= 1000 else f"~{tokens}"
                total_tokens += tokens
            except (OSError, IOError):
                token_estimates[name] = "~0"
        else:
            token_estimates[name] = "~0"
    token_estimates["total"] = (
        f"~{int(total_tokens / 100) / 10}k" if total_tokens >= 1000 else f"~{total_tokens}"
    )

    agents_dir = os.path.join(project_root, ".agents")
    os.makedirs(agents_dir, exist_ok=True)
    status_vivo_path = os.path.join(agents_dir, "STATUS_VIVO.json")

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

    with open(status_vivo_path, "w", encoding="utf-8") as f:
        json.dump(status_vivo, f, indent=2, ensure_ascii=False)

    print("✅ .agents/STATUS_VIVO.json atualizado")
    print(f"   Branch: {branch}")
    if last_commit:
        print(f"   Último commit: {last_commit['hash']} — {last_commit['message']}")
    else:
        print("   Último commit: null")
    print(f"   Tokens do harness: {token_estimates['total']}")


if __name__ == "__main__":
    main()

