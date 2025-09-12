from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path


def find_missing_imports(roots: Iterable[Path]) -> list[dict]:
    pat = re.compile(r"^\s*(from|import)\s+([A-Za-z0-9_\.]+)")
    missing: list[dict] = []
    for root in roots:
        for p in root.rglob("*.py"):
            try:
                text = p.read_text(errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                m = pat.match(line)
                if not m:
                    continue
                mod = m.group(2)
                top = mod.split(".")[0]
                if top not in {"lukhas", "candidate", "serve", "enterprise"}:
                    continue
                # Resolve module path heuristically
                mod_path = Path(*mod.split("."))
                if not (mod_path.with_suffix(".py").exists() or mod_path.exists()):
                    missing.append(
                        {
                            "file": str(p),
                            "line": i,
                            "import": mod,
                        }
                    )
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Static import audit for local packages")
    ap.add_argument(
        "--roots",
        nargs="*",
        default=["lukhas", "serve", "enterprise", "candidate"],
        help="Root dirs",
    )
    ap.add_argument("--out", default="reports/audit/static_imports.json", help="Output JSON path")
    args = ap.parse_args()

    roots = [Path(r) for r in args.roots]
    missing = find_missing_imports(roots)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"missing_count": len(missing), "missing": missing}, indent=2))
    print(f"Static import audit: {len(missing)} potential missing imports. Report: {out_path}")
    return 0 if len(missing) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
