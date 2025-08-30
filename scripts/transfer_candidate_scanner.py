#!/usr/bin/env python3
"""
Scan sibling repositories in /Users/agi_dev/LOCAL-REPOS for modules that are
likely worth transferring into Lukhas or pruning (duplicates/backups).

Outputs a JSON report under reports/transfer_scan/transfer_candidates.json
with two sections: candidates_transfer and candidates_prune.

Use env LUKHAS_LOCAL_REPOS to override the base repos directory.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import sys
from pathlib import Path

THIS_REPO = Path(__file__).resolve().parents[1]
# The container directory holding sibling repos (e.g., /Users/agi_dev/LOCAL-REPOS)
DEFAULT_BASE = THIS_REPO.parent

# Heuristics/patterns to detect
TRANSFER_KEYWORDS = [
    # core endocrine + feedback + env
    "signal_bus.py",
    "homeostasis.py",
    "modulator.py",
    "feedback",
    "feedback_card",
    "card_system.py",
    "env_validator.py",
    "modulation_policy.yaml",
    # identity bridges / tiering
    "TierValidator",
    "TieredAccessControl",
    "import_bridge.py",
    "governance/identity",
    # openai integration layers
    "openai_core_service.py",
    "openai_modulated_service.py",
    # persona/voice
    "persona_manager.py",
    "voice/processor",
    "voice_processor.py",
]

PRUNE_HINTS = [
    "._cleanup_archive",
    "advanced_backups",
    "syntax_backups",
    "*.backup",
    "/archive/",
    "/quarantine/",
    "_backup",
    "deprecated",
    "unused_files",
]

DUPLICATE_CLASS_SIGNALS: list[tuple[str, str]] = [
    ("model_communication_engine.py", r"class\s+ModelCommunicationEngine\b"),
]

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv"}


def _debug_enabled() -> bool:
    return os.environ.get("LUKHAS_SCANNER_DEBUG", "").lower() in {"1", "true", "yes"}


def _dprint(msg: str) -> None:
    if _debug_enabled():
        with contextlib.suppress(Exception):
            print(msg, file=sys.stderr)


def is_text_file(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)
        return b"\0" not in chunk
    except Exception:
        return False


def count_occurrences(path: Path, pattern: str) -> int:
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return 0
    return len(re.findall(pattern, text))


def file_score_for_transfer(path: Path) -> list[str]:
    tags: list[str] = []
    lower = str(path).lower()
    for kw in TRANSFER_KEYWORDS:
        if kw in lower:
            tags.append(f"kw:{kw}")
    # simple semantic hints
    if path.name in {"cognitive_adapter.py", "brain_adapter.py", "dream_adapter.py"}:
        tags.append("adapter")
    if path.suffix in {".yaml", ".yml"} and "policy" in path.name:
        tags.append("policy")
    return tags


def file_score_for_prune(path: Path) -> list[str]:
    tags: list[str] = []
    pstr = str(path)
    for hint in PRUNE_HINTS:
        if hint in pstr:
            tags.append(f"hint:{hint}")
    # design-note .py (low code density)
    if path.suffix == ".py":
        try:
            text = path.read_text(errors="ignore")
            code_lines = sum(
                1 for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")
            )
            if (
                code_lines < 20
                and len(text) > 0
                and ("Feature:" in text or "TODO" in text or "Notes" in text)
            ):
                tags.append("low_code_density")
        except Exception:
            pass
    # duplicate class signals
    for fname, pat in DUPLICATE_CLASS_SIGNALS:
        if path.name == fname:
            n = count_occurrences(path, pat)
            if n > 1:
                tags.append(f"duplicate_class:{fname}:{n}")
    return tags


def build_current_index(root: Path) -> set:
    idx = set()
    for p in root.rglob("*"):
        if p.is_file():
            try:
                rel = p.relative_to(root)
            except Exception:
                continue
            idx.add(str(rel))
            idx.add(p.name)
    return idx


def scan_repo(repo_path: Path, current_index: set) -> dict:
    transfer: list[dict] = []
    prune: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(repo_path):
        # prune walk
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            # skip files that are within the current repository to prevent echoing
            try:
                _ = p.resolve().relative_to(THIS_REPO)
                # if relative_to succeeds, p is inside THIS_REPO -> skip
                continue
            except Exception:
                pass
            # limit to text files to avoid binaries
            if not is_text_file(p):
                continue
            tags_t = file_score_for_transfer(p)
            tags_p = file_score_for_prune(p)
            if tags_t:
                # If a similarly named artifact already exists in current repo, note it
                exists = p.name in current_index
                transfer.append(
                    {
                        "path": str(p),
                        "relname_exists_in_current": exists,
                        "reason_tags": tags_t,
                    }
                )
            if tags_p:
                prune.append(
                    {
                        "path": str(p),
                        "reason_tags": tags_p,
                    }
                )
    return {"candidates_transfer": transfer, "candidates_prune": prune}


def main() -> int:
    base = Path(os.environ.get("LUKHAS_LOCAL_REPOS", str(DEFAULT_BASE))).resolve()
    if not base.exists() or not base.is_dir():
        print(json.dumps({"error": f"Base directory not found: {base}"}, indent=2))
        return 1

    current_index = build_current_index(THIS_REPO)

    report: dict[str, dict] = {}
    _dprint(f"[scanner] Base: {base}")
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("."):
            continue
        if name == THIS_REPO.name:
            continue
        # Only scan directories that look like repos
        # Require a git repo or common Python project manifest to avoid scanning
        # container dirs
        looks_like_repo = (
            (entry / ".git").exists()
            or (entry / "pyproject.toml").exists()
            or (entry / "setup.py").exists()
            or (entry / "requirements.txt").exists()
        )
        _dprint(
            f"[scanner] Considering {entry} -> git={(entry / '.git').exists()} pyproject={(entry / 'pyproject.toml').exists()} setup={(entry / 'setup.py').exists()} req={(entry / 'requirements.txt').exists()} looks_like_repo={looks_like_repo}"
        )
        if not looks_like_repo:
            continue
        report[name] = scan_repo(entry, current_index)

    out_dir = THIS_REPO / "reports" / "transfer_scan"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "transfer_candidates.json"
    with out_path.open("w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({"ok": True, "report": str(out_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
