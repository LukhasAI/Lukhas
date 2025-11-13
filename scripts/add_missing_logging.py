#!/usr/bin/env python3
"""
Detect `logging` usage without an import and insert `import logging`.
Idempotent and conservative: checks AST and avoids files already importing logging.
Skips release_artifacts and .git directories.
"""
import ast
from pathlib import Path

ROOT = Path(".")
EXCLUDE = ("release_artifacts", ".git", "__pycache__")

def file_uses_logging(path):
    try:
        src = path.read_text(encoding="utf-8")
    except Exception:
        return False
    try:
        tree = ast.parse(src)
    except Exception:
        return False
    has_import = any(isinstance(n, ast.Import) and any(alias.name == "logging" for alias in n.names) for n in tree.body)
    has_from = any(isinstance(n, ast.ImportFrom) and n.module == "logging" for n in tree.body)
    uses_logging = any(isinstance(n, ast.Attribute) and getattr(n.value, "id", "") == "logging" for n in ast.walk(tree))
    return uses_logging and not (has_import or has_from)

def insert_import(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and (lines[insert_at].startswith('"""') or lines[insert_at].startswith("'''")):
        dq = lines[insert_at][:3]
        for i in range(insert_at + 1, len(lines)):
            if lines[i].strip().endswith(dq):
                insert_at = i + 1
                break
    lines.insert(insert_at, "import logging")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ADD LOGGING] {path}")

def main():
    count = 0
    for p in ROOT.rglob("*.py"):
        s = str(p)
        if any(ex in s for ex in EXCLUDE):
            continue
        try:
            if file_uses_logging(p):
                insert_import(p)
                count += 1
        except Exception as e:
            print(f"skip {p}: {e}")
    print(f"Inserted logging import into {count} file(s).")

if __name__ == "__main__":
    main()
