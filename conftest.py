# conftest.py (ROOT) — deterministic import behavior + telemetry
from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
import traceback
from pathlib import Path

# Ensure sitecustomize runs (fixes _SixMetaPathImporter compatibility)
try:
    import sitecustomize  # noqa: F401
except ImportError:
    pass

# CRITICAL: Add repo root to sys.path so packages like bridge/, qi/, etc. are importable
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# ---- Import telemetry (turns "UnknownError" into concrete tracebacks) ----
_IMPORT_FAILS: list[tuple[str, str]] = []


def _record_import_error(fullname: str) -> None:
    """Capture last exception's full traceback."""
    _IMPORT_FAILS.append((fullname, traceback.format_exc()))


def pytest_sessionfinish(session, exitstatus):
    """Dump import failures to an artifact pytest will always show."""
    if _IMPORT_FAILS:
        p = session.config.rootpath / "artifacts"
        p.mkdir(exist_ok=True, parents=True)
        out = p / "import_failures.ndjson"
        with out.open("w", encoding="utf-8") as f:
            for name, tb in _IMPORT_FAILS:
                import json
                f.write(json.dumps({"module": name, "trace": tb}) + "\n")
        session.config.warn("C1", f"Saved import failures → {out}")


# ---- Lukhas alias hook (lukhas.* → canonical), safe & non-invasive ----
# IMPORTANT: never mutate sys.path; only implement find_spec; never intercept non-lukhas.
_LUKHAS_PREFIX = "lukhas."


class _LukhasAliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):
        if not fullname.startswith(_LUKHAS_PREFIX):
            return None
        try:
            mapped = _map_lukhas(fullname)
            if not mapped or mapped == fullname:
                return None
            return importlib.util.find_spec(mapped)
        except Exception:
            _record_import_error(fullname)
            return None


def _map_lukhas(fullname: str) -> str | None:
    """
    Centralize alias map (lukhas.* → canonical paths).
    Keep this tiny and pure (no imports of project code!).
    """
    # Core mapping table
    table = {
        "governance.schema_registry": "governance.schema_registry",
        "bio.utils": "bio.utils",
        "bio": "bio",
        "consciousness.matriz_thought_loop": "consciousness.matriz_thought_loop",
        "cognitive_core.reasoning.contradiction_integrator": "candidate.cognitive_core.reasoning.contradiction_integrator",
        "observability.advanced_metrics": "observability.advanced_metrics",
        "consciousness.enhanced_thought_engine": "consciousness.enhanced_thought_engine",
        "consciousness.types": "consciousness.types",
        "memory.backends": "memory.backends",
        "aka_qualia": "aka_qualia",
        "aka_qualia.core": "aka_qualia.core",
    }
    return table.get(fullname)


# Ensure our finder is last (don't shadow normal importers like _SixMetaPathImporter)
# Dedupe and append (not prepend) to avoid conflicts
for i, f in enumerate(list(sys.meta_path)):
    if isinstance(f, _LukhasAliasFinder):
        sys.meta_path.pop(i)
        break
sys.meta_path.append(_LukhasAliasFinder())


# ---- Prometheus duplicate timeseries guard (test-only) ----
# Many "ValueError: Duplicated timeseries" come from module import side-effects.
# Force a fresh registry per test session.
def pytest_sessionstart(session):
    """Reset Prometheus registry to avoid duplicate timeseries errors."""
    try:
        from prometheus_client import CollectorRegistry, core

        core.REGISTRY = CollectorRegistry(auto_describe=True)  # type: ignore[attr-defined]
    except Exception:
        # If prometheus_client not installed in env, skip silently
        pass


# ---- Additional test fixtures ----
import pytest


@pytest.fixture(scope="session")
def labs_root():
    """Provide path to labs (candidate) directory."""
    return repo_root / "labs"
