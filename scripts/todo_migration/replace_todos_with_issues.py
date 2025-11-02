#!/usr/bin/env python3
"""
Replace inline TODO lines with GitHub issue links according to mapping.

Usage:
  ./replace_todos_with_issues.py --map artifacts/todo_to_issue_map.json --dry-run
  ./replace_todos_with_issues.py --map artifacts/todo_to_issue_map.json --apply

Mapping file format (json): keys are 'path:line' and values are {"issue": int, "repo": "org/repo", "title": "..."}
This script supports both relative and absolute paths; it normalizes to repo-root relative paths.
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Tuple

TODO_REGEX = re.compile(r"(?P<indent>\s*)#\s*TODO(\[.*?\])?\s*[:\-]?\s*(?P<msg>.*)$", re.IGNORECASE)


def normalize_path_key(key: str) -> Tuple[Path, int]:
    # key formats supported: path:line or /abs/path:line
    parts = key.rsplit(":", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid mapping key (expected path:line): {key}")
    path_str, line_str = parts
    try:
        line_no = int(line_str)
    except ValueError:
        raise ValueError(f"Invalid line number in mapping key: {key}")
    p = Path(path_str)
    if p.is_absolute():
        # convert to repo-relative if possible
        try:
            rel = p.relative_to(Path.cwd())
            p = rel
        except Exception:
            # leave absolute if outside repo
            pass
    return p, line_no


def backup_file(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak


def replace_in_file(path: Path, mapping: Dict[str, dict], apply: bool, log: list) -> bool:
    changed = False
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    new_lines = list(lines)
    for i, line in enumerate(lines, start=1):
        key_rel = f"{path}:{i}"
        key_abs = f"{path.resolve()}:{i}"
        # mapping might store relative or absolute keys; check both
        mapping_key = None
        if key_rel in mapping:
            mapping_key = key_rel
        elif key_abs in mapping:
            mapping_key = key_abs
        else:
            # also try repo-root relative forms
            repo_rel = os.path.relpath(path, Path.cwd())
            if f"{repo_rel}:{i}" in mapping:
                mapping_key = f"{repo_rel}:{i}"

        if mapping_key:
            entry = mapping[mapping_key]
            issue = entry.get("issue")
            repo = entry.get("repo", "").rstrip("/")
            link = f"# See: https://github.com/{repo}/issues/{issue}\n" if repo and issue else f"# See: issue/{issue}\n"
            indent_match = TODO_REGEX.match(line)
            indent = indent_match.group("indent") if indent_match else ""
            new_line = f"{indent}{link}"
            new_lines[i - 1] = new_line
            changed = True
            log.append({"file": str(path), "line": i, "issue": issue, "repo": repo, "applied": apply})

    if changed:
        if apply:
            bak = backup_file(path)
            with open(path, "w", encoding="utf-8") as fh:
                fh.writelines(new_lines)
            print(f"[APPLIED] Updated {path} (backup: {bak})")
        else:
            print(f"[DRY-RUN] Would update {path}")
    return changed


def load_mapping(mapfile: Path) -> Dict[str, dict]:
    data = json.loads(mapfile.read_text(encoding="utf-8"))
    # normalize keys to repo-relative when reasonable
    norm = {}
    for k, v in data.items():
        try:
            p, line = normalize_path_key(k)
            repo_rel = os.path.relpath(p, Path.cwd())
            # store both repo_rel and original to maximize matching chance
            norm_key_rel = f"{repo_rel}:{line}"
            norm_key_orig = f"{str(p)}:{line}"
            norm[norm_key_rel] = v
            norm[norm_key_orig] = v
        except Exception:
            # keep original if cannot normalize
            norm[k] = v
    return norm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", required=True, help="Path to mapping JSON (artifacts/todo_to_issue_map.json)")
    parser.add_argument("--apply", action="store_true", help="Actually write file modifications")
    args = parser.parse_args()

    mapfile = Path(args.map)
    if not mapfile.exists():
        raise SystemExit(f"Mapping file not found: {mapfile}")

    mapping = load_mapping(mapfile)

    # determine files from mapping
    files = sorted({k.rsplit(":", 1)[0] for k in mapping.keys()})
    log = []
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"Warning: mapped file not found: {p}")
            log.append({"file": str(p), "error": "not_found"})
            continue
        try:
            replace_in_file(p, mapping, args.apply, log)
        except Exception as e:
            print(f"Error processing {p}: {e}")
            log.append({"file": str(p), "error": str(e)})

    Path("artifacts").mkdir(exist_ok=True)
    logpath = Path("artifacts/replace_todos_log.json")
    logpath.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Wrote replace todo log to {logpath}")


if __name__ == "__main__":
    main()
