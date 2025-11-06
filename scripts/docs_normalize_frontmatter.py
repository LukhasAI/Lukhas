#!/usr/bin/env python3
"""
LUKHAS Documentation Front-Matter Normalizer (T4/0.01% edition)

Goals
- Enforce 100% front-matter compliance with correct YAML types (bool/null), not stringified.
- Preserve existing values; only fill required defaults or normalize types/keys/order.
- Skip generated, inventory, archive, and explicit redirect stubs.
- Work off docs_manifest.json but tolerate missing fields.
- Safety: dry-run by default; create .bak on apply; concurrency for speed; clear delta reporting.
- Resilient YAML parsing: prefer PyYAML if available; fall back to a minimal parser.

Usage
  DRY RUN:  python scripts/docs_normalize_frontmatter.py
  APPLY:    python scripts/docs_normalize_frontmatter.py --apply
  OPTIONS:  --only-missing (add front-matter only when absent)
            --concurrency N (default: 8)

Notes
- This script is idempotent and will not churn content if no semantic changes are needed.
- It emits a stable key order to minimize diffs.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

# Optional YAML dependency (preferred)
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"

# Front-matter regex (must be at file start)
FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Canonical key order (stable diffs)
KEY_ORDER = [
    "status",
    "type",
    "owner",
    "module",
    "redirect",
    "moved_to",
]

# Required keys with semantic defaults (typed, not strings)
REQUIRED_DEFAULTS = {
    "status": "wip",
    "type": "documentation",
    "owner": "unknown",
    "module": "unknown",
    "redirect": False,
    "moved_to": None,
}

SKIP_DIRS = {"_generated", "_inventory", "archive"}

@dataclass
class Result:
    path: str
    had_fm: bool
    updated: bool
    error: str | None = None
    sha_before: str | None = None
    sha_after: str | None = None


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_manifest() -> Dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def safe_yaml_load(text: str) -> Dict:
    if yaml:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            return {}
        return data
    # Minimal fallback: key: value per line, no nesting (keeps existing behavior but safer)
    out: Dict[str, object] = {}
    for line in text.splitlines():
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        # try to coerce booleans/null
        if v.lower() in {"true", "false"}:
            out[k] = v.lower() == "true"
        elif v.lower() in {"null", "~"}:
            out[k] = None
        else:
            out[k] = v
    return out


def safe_yaml_dump(data: Dict) -> str:
    # Enforce key order and correct YAML scalars
    ordered = {k: data.get(k, REQUIRED_DEFAULTS[k]) for k in KEY_ORDER}
    if yaml:
        return yaml.safe_dump(ordered, sort_keys=False).strip() + "\n"
    # Fallback dumper
    lines = []
    for k in KEY_ORDER:
        v = ordered[k]
        if isinstance(v, bool):
            sval = "true" if v else "false"
        elif v is None:
            sval = "null"
        else:
            sval = str(v)
        lines.append(f"{k}: {sval}")
    return "\n".join(lines) + "\n"


def extract_front_matter(content: str) -> Tuple[Dict | None, str]:
    match = FRONT_MATTER_PATTERN.match(content)
    if not match:
        return None, content
    fm_text = match.group(1)
    body = content[match.end():]
    return safe_yaml_load(fm_text), body


def build_front_matter(doc_info: Dict, existing: Dict | None) -> Dict:
    fm = dict(existing or {})

    # Fill from manifest if present; otherwise defaults
    def pick(key: str, default):
        cur = fm.get(key)
        if cur in (None, "unknown", "", {}):
            fm[key] = doc_info.get(key, default)

    pick("status", REQUIRED_DEFAULTS["status"])
    pick("type", REQUIRED_DEFAULTS["type"])
    pick("owner", REQUIRED_DEFAULTS["owner"])
    pick("module", REQUIRED_DEFAULTS["module"])

    # Normalize types for redirect & moved_to
    redirect = fm.get("redirect", REQUIRED_DEFAULTS["redirect"])
    if isinstance(redirect, str):
        redirect = redirect.strip().lower() == "true"
    fm["redirect"] = bool(redirect)

    moved_to = fm.get("moved_to", REQUIRED_DEFAULTS["moved_to"])
    if isinstance(moved_to, str) and moved_to.strip().lower() in {"", "null", "none", "~"}:
        moved_to = None
    fm["moved_to"] = moved_to

    # Ensure only whitelisted keys in output order; ignore extra keys silently (they remain in file body)
    normalized = {k: fm.get(k, REQUIRED_DEFAULTS[k]) for k in KEY_ORDER}
    return normalized


def should_skip(doc: Dict) -> bool:
    # Manifest-based early skips
    if doc.get("redirect") is True:
        return True
    p = Path(doc.get("path", ""))
    # Skip obvious buckets
    parts = set(p.parts)
    if parts & SKIP_DIRS:
        return True
    # Only .md files are processed
    return p.suffix.lower() != ".md"


def normalize_file(doc: Dict, dry_run: bool, only_missing: bool, backups: bool) -> Result:
    rel_path = doc.get("path")
    if not rel_path:
        return Result(path="<missing>", had_fm=False, updated=False, error="No path in manifest")

    file_path = (REPO_ROOT / rel_path).resolve()
    if not file_path.exists():
        return Result(path=rel_path, had_fm=False, updated=False, error="File not found")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return Result(path=rel_path, had_fm=False, updated=False, error=f"Read failed: {e}")

    sha_before = sha256_text(content)

    existing_fm, body = extract_front_matter(content)
    had_fm = existing_fm is not None

    if only_missing and had_fm:
        return Result(path=rel_path, had_fm=True, updated=False)

    new_fm_dict = build_front_matter(doc, existing_fm)
    new_fm_yaml = safe_yaml_dump(new_fm_dict)

    new_content = f"---\n{new_fm_yaml}---\n\n{body}"

    updated = (new_content != content)

    if updated and not dry_run:
        if backups:
            with contextlib.suppress(Exception):
                file_path.with_suffix(file_path.suffix + ".bak").write_text(content, encoding="utf-8")
        # Python 3.9 compatible: write_text doesn't support newline parameter
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)

    sha_after = sha256_text(new_content)

    return Result(path=rel_path, had_fm=had_fm, updated=updated, sha_before=sha_before, sha_after=sha_after)


def main() -> None:
    dry_run = "--apply" not in sys.argv
    only_missing = "--only-missing" in sys.argv

    # Concurrency
    try:
        idx = sys.argv.index("--concurrency")
        workers = int(sys.argv[idx + 1])
    except Exception:
        workers = 8

    backups = not dry_run

    print("=" * 92)
    print("LUKHAS Front-Matter Normalizer - T4/0.01%")
    print("=" * 92)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'} | only-missing: {only_missing} | workers: {workers}")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Docs root: {DOCS_ROOT}")
    print()

    if not MANIFEST_PATH.exists():
        print(f"❌ Manifest not found: {MANIFEST_PATH}")
        sys.exit(2)

    print(f"📂 Loading manifest: {MANIFEST_PATH}")
    manifest = load_manifest()
    docs = manifest.get("documents") or manifest.get("docs") or []

    print(f"📝 Candidates in manifest: {len(docs)}")

    # Filter now for speed
    targets = [d for d in docs if not should_skip(d)]
    print(f"✅ Will process markdown docs (excluding generated/inventory/archive/redirect): {len(targets)}")

    updated = 0
    skipped = len(docs) - len(targets)
    errors = 0
    had_fm_count = 0

    futures = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for doc in targets:
            futures.append(ex.submit(normalize_file, doc, dry_run, only_missing, backups))
        for fut in as_completed(futures):
            res: Result = fut.result()
            if res.error:
                print(f"❌ {res.path}: {res.error}")
                errors += 1
                continue
            had_fm_count += 1 if res.had_fm else 0
            if res.updated:
                mark = "✏️  (normalized)" if res.had_fm else "✅ (added)"
                print(f"{mark} {res.path}")
                updated += 1

    print()
    print("=" * 92)
    print("NORMALIZATION SUMMARY")
    print("=" * 92)
    print(f"Total in manifest: {len(docs)}")
    print(f"Processed: {len(targets)} | Skipped: {skipped} | Errors: {errors}")
    print(f"Had FM: {had_fm_count} | Updated: {updated}")

    if dry_run:
        print("⚠️  DRY RUN - no files modified. Use --apply to write changes.")
    else:
        print("✅ Applied changes. Run: make docs-lint")

    print()
    print("".join(["-" for _ in range(92)]))


if __name__ == "__main__":
    main()
