#!/usr/bin/env python3
"""
Fail if legacy import roots are present outside allowlisted paths.

Env:
  LUKHAS_LEGACY_ALLOWLIST   (comma-separated paths)
  LUKHAS_LEGACY_ROOTS       (comma-separated roots; overrides config)

Config:
  configs/legacy_imports.yml (used if present)

Exit codes:
  0: No legacy imports found outside allowlist
  2: Legacy imports detected (blocks CI)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    # Fallback if yaml not installed
    yaml = None

DEFAULT_ROOTS = ["candidate", "tools", "governance", "memory", "ledger", "lucas", "Lucas", "LUCAS"]
CFG = Path("configs/legacy_imports.yml")


def load_cfg_roots():
    if not yaml:
        return DEFAULT_ROOTS, set()
    if CFG.exists():
        try:
            data = yaml.safe_load(CFG.read_text(encoding="utf-8"))
            mp = data.get("map", {}) or {}
            return list(mp.keys()) or DEFAULT_ROOTS, set(data.get("allowlist", []) or [])
        except Exception:
            return DEFAULT_ROOTS, set()
    return DEFAULT_ROOTS, set()


def main():
    roots_env = os.getenv("LUKHAS_LEGACY_ROOTS")
    roots, allow_cfg = load_cfg_roots()
    roots = roots_env.split(",") if roots_env else roots
    allow = allow_cfg | set((os.getenv("LUKHAS_LEGACY_ALLOWLIST") or "").split(",")) - {""}

    # Build regex pattern for legacy imports
    pat = re.compile(rf"^\s*(from|import)\s+({'|'.join(map(re.escape, roots))})(\.|\s|$)")

    bad = []
    for p in Path(".").rglob("**/*.py"):
        s = str(p)
        # Skip allowlisted paths
        if any(s.startswith(a) for a in allow):
            continue
        # Skip excluded directories
        if any(
            seg
            in {
                ".git",
                "venv",
                ".venv",
                "node_modules",
                "dist",
                "build",
                "__pycache__",
                ".mypy_cache",
                ".ruff_cache",
                ".pytest_cache",
                ".tox",
            }
            for seg in p.parts
        ):
            continue
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if pat.search(line):
                    bad.append((s, i, line.strip()))
        except Exception:
            continue

    if bad:
        print("[legacy-imports] ❌ Found legacy imports outside allowlist:")
        for s, i, line in bad[:200]:
            print(f"  {s}:{i}: {line}")
        if len(bad) > 200:
            print(f"  ... and {len(bad) - 200} more")
        print(f"\n[legacy-imports] Total violations: {len(bad)}")
        print("[legacy-imports] Run: make codemod-dry  # to preview fixes")
        sys.exit(2)

    print("[legacy-imports] ✅ OK: no legacy imports outside allowlist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
