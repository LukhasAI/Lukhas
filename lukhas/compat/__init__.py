# lukhas/compat/__init__.py
"""
Compatibility alias loader for legacy imports during the labs->prod migration.

Maps legacy root packages to current locations at import-time and records usage.

Usage:
  from lukhas.compat import install as _install_aliases
  _install_aliases()  # (done in tests/conftest.py)

Telemetry:
  - Counts alias hits by legacy fullname.
  - Writes JSON to LUKHAS_COMPAT_HITS_FILE, default: docs/audits/compat_alias_hits.json
  - Enforcement knobs via env:
      LUKHAS_COMPAT_ENFORCE = "0"|"1"  (if "1", raise ImportError on alias use)
"""
from __future__ import annotations

import atexit
import importlib
import importlib.abc
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Dict

# Map of legacy root → new root
ALIASES: Dict[str, str] = {
    # lanes
    "labs": "labs",  # Keep candidate for now (not renamed to labs yet)
    # legacy top-levels → canonical
    "lukhas.tools": "lukhas.tools",
    "lukhas.governance": "lukhas.governance",
    "lukhas.memory": "lukhas.memory",
    "lukhas.ledger": "lukhas.ledger",
    # uppercase package from tests
    "MATRIZ": "MATRIZ",  # ensure MATRIZ is a real package with __init__.py
}

# metrics
_hits: Dict[str, int] = {}
_enforce = os.getenv("LUKHAS_COMPAT_ENFORCE", "0") == "1"
_outfile = Path(os.getenv("LUKHAS_COMPAT_HITS_FILE", "docs/audits/compat_alias_hits.json"))


def _record(fullname: str):
    _hits[fullname] = _hits.get(fullname, 0) + 1


class _AliasLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def _map(self, fullname: str) -> str | None:
        parts = fullname.split(".")
        root = parts[0]
        if root in ALIASES:
            mapped = ".".join([ALIASES[root]] + parts[1:])
            # Don't map if it's the same (prevents infinite recursion)
            if mapped == fullname:
                return None
            return mapped
        return None

    # Finder
    def find_spec(self, fullname, path=None, target=None):
        mapped = self._map(fullname)
        if not mapped:
            return None

        # Temporarily remove ourselves from meta_path to avoid recursion
        # when finding the mapped spec
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(mapped)
        except Exception:
            spec = None
        finally:
            # Always re-insert ourselves at the front
            if self not in sys.meta_path:
                sys.meta_path.insert(0, self)

        if spec:
            # make this loader execute the module to rewrite its dict
            spec.loader = self
            spec._lukhas_alias_fullname = fullname  # type: ignore
            spec._lukhas_alias_mapped = mapped  # type: ignore
            return spec
        return None

    # Loader
    def create_module(self, spec):  # pragma: no cover
        return None  # default module creation

    def exec_module(self, module):
        fullname = getattr(module.__spec__, "_lukhas_alias_fullname", None)
        mapped = getattr(module.__spec__, "_lukhas_alias_mapped", None)
        if not fullname or not mapped:
            return
        if _enforce:
            raise ImportError(
                f"Lukhas compat alias blocked: {fullname} → {mapped} "
                f"(set LUKHAS_COMPAT_ENFORCE=0 to allow during migration)"
            )
        real = importlib.import_module(mapped)
        module.__dict__.update(real.__dict__)
        _record(fullname)


_installed = False
_loader = _AliasLoader()


def install():
    """Install the alias loader once."""
    global _installed
    if _installed:
        return
    sys.meta_path.insert(0, _loader)
    _installed = True


def _write_hits():
    try:
        _outfile.parent.mkdir(parents=True, exist_ok=True)
        _outfile.write_text(json.dumps(_hits, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        pass


atexit.register(_write_hits)
