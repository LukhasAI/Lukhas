#!/usr/bin/env python3
"""
Codemod legacy imports to canonical lukhas.* paths using LibCST when available.

Dry-run by default: outputs docs/audits/codemod_preview.csv with proposed edits.
Use --apply to write changes in-place.

Examples:
  python3 scripts/codemod_imports.py --roots lukhas labs core MATRIZ tests packages tools
  python3 scripts/codemod_imports.py --apply --roots lukhas labs core MATRIZ tests packages tools

Config (optional):
  --config configs/legacy_imports.yml
"""
from __future__ import annotations

import argparse
import ast
import csv
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

HAS_LIBCST = True

try:
    import libcst as cst
    import libcst.matchers as m
except ImportError:
    HAS_LIBCST = False
    cst = None  # type: ignore[assignment]
    m = None  # type: ignore[assignment]

try:
    import yaml
except ImportError:  # pragma: no cover - fallback path when PyYAML missing.
    yaml = None  # type: ignore[assignment]

DEFAULT_MAP = {
    "candidate": "labs",
    "tools": "tools",
    "governance": "governance",
    "memory": "memory",
    "ledger": "ledger",
    "lucas": "lukhas",
    "Lucas": "lukhas",
    "LUCAS": "lukhas",
}

ALLOWLIST_DEFAULT = {"lukhas/compat", "tests/conftest.py"}

PY_GLOB = "**/*.py"
EXCLUDE_DIRS = {".git","venv",".venv","node_modules","dist","build","__pycache__",
                ".mypy_cache",".ruff_cache",".pytest_cache",".tox",".idea",".vscode"}

def load_cfg(path: str|None):
    if not path:
        return DEFAULT_MAP, ALLOWLIST_DEFAULT
    p = Path(path)
    if not p.exists():
        return DEFAULT_MAP, ALLOWLIST_DEFAULT
    if yaml is not None:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        mapping = data.get("map", {}) or {}
        allow = set(data.get("allowlist", []) or [])
    else:
        mapping = {}
        allow = set()
        current: str | None = None
        for raw_line in p.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith(":"):
                key = line[:-1].strip()
                current = key if key in {"map", "allowlist"} else None
                continue
            if current == "map" and ":" in line:
                key, value = line.split(":", 1)
                clean_key = key.strip()
                clean_val = value.strip().strip('"').strip("'")
                if clean_key:
                    mapping[clean_key] = clean_val
            elif current == "allowlist" and line.startswith("-"):
                candidate_path = line[1:].strip().strip('"').strip("'")
                if candidate_path:
                    allow.add(candidate_path)
    # merge defaults (cfg overrides default keys)
    merged = DEFAULT_MAP.copy()
    merged.update(mapping)
    return merged, allow or ALLOWLIST_DEFAULT

def root_ok(p: Path)->bool:
    return all(seg not in EXCLUDE_DIRS for seg in p.parts)

def rewrite_root(name: str, mapping: dict[str,str]) -> str|None:
    # If name begins with any legacy root, replace that segment
    parts = name.split(".")
    if not parts:
        return None
    root = parts[0]
    if root in mapping:
        new_root = mapping[root]
        new_name = ".".join([new_root, *parts[1:]])
        return new_name
    return None

if HAS_LIBCST:
    class ImportRewriter(cst.CSTTransformer):
        def __init__(self, mapping: dict[str,str]):
            self.mapping = mapping
            self.changes: list[tuple[str,str]] = []  # (old, new)

        def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
            names = []
            changed = False
            for alias in updated.names:
                if m.matches(alias, m.ImportAlias(name=m.Attribute() | m.Name())):
                    # Handle both Attribute and Name nodes
                    if hasattr(alias.name, 'code'):
                        full = alias.name.code
                    else:
                        full = cst.Module([]).code_for_node(alias.name)
                    new = rewrite_root(full, self.mapping)
                    if new and new != full:
                        names.append(alias.with_changes(name=cst.parse_expression(new)))
                        self.changes.append((full, new))
                        changed = True
                    else:
                        names.append(alias)
                else:
                    names.append(alias)
            return updated.with_changes(names=tuple(names)) if changed else updated

        def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
            # from X.Y import Z
            if updated.module is None:
                return updated
            # Handle both Attribute and Name nodes
            if hasattr(updated.module, 'code'):
                full = updated.module.code
            else:
                full = cst.Module([]).code_for_node(updated.module)
            new = rewrite_root(full, self.mapping)
            if new and new != full:
                self.changes.append((full, new))
                return updated.with_changes(module=cst.parse_expression(new))
            return updated

        def leave_SimpleString(self, original: cst.SimpleString, updated: cst.SimpleString):
            # Opportunistic: importlib.import_module("tools.scripts") literals
            text = original.evaluated_value
            if isinstance(text, str):
                new = None
                for legacy, canonical in self.mapping.items():
                    # match at start of dotted path in string
                    if re.match(rf"^{re.escape(legacy)}(\.|$)", text):
                        new = re.sub(rf"^{re.escape(legacy)}", canonical, text)
                        break
                if new and new != text:
                    self.changes.append((text, new))
                    # Preserve original quoting style including prefixes
                    old_val = updated.value
                    prefix = ''
                    quote_start = 0
                    for i, c in enumerate(old_val):
                        if c in ('"', "'"):
                            prefix = old_val[:i]
                            quote_start = i
                            break
                    quote_char = old_val[quote_start]
                    escaped = new.replace("\\", "\\\\").replace(quote_char, f"\\{quote_char}")
                    new_val = f"{prefix}{quote_char}{escaped}{quote_char}"
                    return updated.with_changes(value=new_val)
            return updated


@dataclass
class Replacement:
    start: int
    end: int
    new_text: str


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for line in text.splitlines(keepends=True):
        total += len(line)
        offsets.append(total)
    return offsets


def _abs_index(offsets: list[int], lineno: int, col: int) -> int:
    return offsets[lineno - 1] + col


def _preserve_quotes(original: str, new_body: str) -> str:
    prefix = ""
    idx = 0
    while idx < len(original) and original[idx] not in {'"', "'"}:
        prefix += original[idx]
        idx += 1
    quote_part = original[idx:]
    if quote_part.startswith("\"\"\"") or quote_part.startswith("'''"):
        quote = quote_part[:3]
        closing = quote_part[-3:]
        return f"{prefix}{quote}{new_body}{closing}"
    if quote_part.startswith(("\"", "'")):
        quote = quote_part[0]
        return f"{prefix}{quote}{new_body}{quote}"
    return repr(new_body)


def _rewrite_literal_value(value: str, mapping: dict[str, str]) -> tuple[str | None, str | None]:
    for legacy, canonical in mapping.items():
        if value == legacy or value.startswith(f"{legacy}."):
            new_value = f"{canonical}{value[len(legacy):]}"
            return value, new_value
    return None, None


def _fallback_replacements(src: str, mapping: dict[str, str]) -> tuple[list[Replacement], list[tuple[str, str]]]:
    # ΛTAG: import_codemod_fallback - deterministic fallback when LibCST is unavailable.
    replacements: list[Replacement] = []
    changes: list[tuple[str, str]] = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return replacements, changes

    offsets = _line_offsets(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                old = alias.name
                new = rewrite_root(old, mapping)
                if not new or new == old:
                    continue
                segment = ast.get_source_segment(src, alias)
                if segment is None:
                    continue
                suffix = f" as {alias.asname}" if alias.asname else ""
                replacement_text = f"{new}{suffix}"
                if alias.lineno is None or alias.col_offset is None:
                    continue
                if alias.end_lineno is None or alias.end_col_offset is None:
                    continue
                start = _abs_index(offsets, alias.lineno, alias.col_offset)
                end = _abs_index(offsets, alias.end_lineno, alias.end_col_offset)
                replacements.append(Replacement(start, end, replacement_text))
                changes.append((old, new))
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            new = rewrite_root(node.module, mapping)
            if not new or new == node.module:
                continue
            segment = ast.get_source_segment(src, node)
            if segment is None:
                continue
            idx = segment.find(node.module)
            if idx == -1:
                # TODO(codex): Handle exotic formatting if encountered.
                continue
            base = _abs_index(offsets, node.lineno, node.col_offset)
            start = base + idx
            end = start + len(node.module)
            replacements.append(Replacement(start, end, new))
            changes.append((node.module, new))
        elif isinstance(node, ast.Call):
            if not node.args:
                continue
            arg0 = node.args[0]
            if not isinstance(arg0, ast.Constant) or not isinstance(arg0.value, str):
                continue
            func = node.func
            func_name = None
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                func_name = f"{func.value.id}.{func.attr}"
            elif isinstance(func, ast.Name):
                func_name = func.id
            if func_name not in {"importlib.import_module", "import_module"}:
                continue
            old_val, new_val = _rewrite_literal_value(arg0.value, mapping)
            if not new_val or new_val == old_val:
                continue
            literal_src = ast.get_source_segment(src, arg0)
            if literal_src is None:
                continue
            new_literal = _preserve_quotes(literal_src, new_val)
            start = _abs_index(offsets, arg0.lineno, arg0.col_offset)
            end = _abs_index(offsets, arg0.end_lineno, arg0.end_col_offset)
            replacements.append(Replacement(start, end, new_literal))
            changes.append((old_val, new_val))

    replacements.sort(key=lambda r: r.start)
    # merge replacements into non-overlapping order by applying from end
    merged: list[Replacement] = []
    last_end = -1
    for rep in replacements:
        if rep.start < last_end:
            # overlapping replacement - skip to keep deterministic output
            continue
        merged.append(rep)
        last_end = rep.end

    return merged, changes


def _apply_replacements(src: str, replacements: Iterable[Replacement]) -> str:
    new_src = src
    for rep in sorted(replacements, key=lambda r: r.start, reverse=True):
        new_src = new_src[:rep.start] + rep.new_text + new_src[rep.end:]
    return new_src


def process_file(path: Path, mapping: dict[str,str], apply: bool):
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        print(f"[codemod] skipping missing file: {path}")
        return [], False
    if HAS_LIBCST:
        try:
            mod = cst.parse_module(src)
        except Exception:
            return [], False  # skip unparsable
        tr = ImportRewriter(mapping)
        new_mod = mod.visit(tr)
        changed = bool(tr.changes)
        if changed and apply:
            path.write_text(new_mod.code, encoding="utf-8")
        return tr.changes, changed

    replacements, changes = _fallback_replacements(src, mapping)
    changed = bool(replacements)
    if changed and apply:
        path.write_text(_apply_replacements(src, replacements), encoding="utf-8")
    return changes, changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["lukhas","labs","core","MATRIZ","tests","packages","tools"])
    ap.add_argument("--config", default="configs/legacy_imports.yml")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default="docs/audits/codemod_preview.csv")
    args = ap.parse_args()

    mapping, _allow = load_cfg(args.config)
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    changed_files = 0
    for root in args.roots:
        base = Path(root)
        if not base.exists():
            continue
        for p in base.rglob(PY_GLOB):
            if not root_ok(p):
                continue
            changes, changed = process_file(p, mapping, args.apply)
            if changes:
                changed_files += 1 if changed else 0
                for old, new in changes:
                    rows.append({"path": str(p), "from": old, "to": new})

    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path","from","to"])
        w.writeheader()
        w.writerows(rows)

    print(f"[codemod] wrote {outp} with {len(rows)} proposed edits"
          f"{' (APPLIED)' if args.apply else ' (DRY-RUN)'}")
    print(f"[codemod] files changed: {changed_files}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
