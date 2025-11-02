#!/usr/bin/env python3
"""
Lightweight pytest shim for environments without pytest.

Runs simple test functions in modules under a directory, supporting:
- test_*.py discovery
- functions named test_* with 0 args, or 1 arg named 'client' if the module
  defines a callable `client()` that returns a Starlette/FastAPI TestClient.

Outputs a single summary line compatible with Makefile tail parsing:
"<passed> passed, <failed> failed, <errors> errors"
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable, Optional


def _load_module_from_path(path: Path) -> ModuleType:
    name = "pytest_shim__" + "_".join(path.parts).replace(".", "_")
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_tests(root: Path) -> tuple[int, int, int]:
    passed = failed = errors = 0
    for py in sorted(root.rglob("test_*.py")):
        try:
            mod = _load_module_from_path(py)
        except Exception:
            errors += 1
            continue

        client_factory: Optional[Callable] = getattr(mod, "client", None)
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                sig = inspect.signature(obj)
                if len(sig.parameters) == 0:
                    obj()  # no-arg test
                    passed += 1
                elif len(sig.parameters) == 1 and "client" in sig.parameters and callable(client_factory):
                    cli = client_factory()
                    obj(cli)  # pass constructed client
                    passed += 1
                else:
                    # Unsupported signature without pytest; mark as failed
                    failed += 1
            except AssertionError:
                failed += 1
            except Exception:
                errors += 1
    return passed, failed, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="tests/smoke", help="Directory to discover tests")
    args = ap.parse_args()
    root = Path(args.path)
    if not root.exists():
        print("0 passed, 0 failed, 0 errors")
        return 0
    p, f, e = run_tests(root)
    print(f"{p} passed, {f} failed, {e} errors")
    return 0 if (f == 0 and e == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
