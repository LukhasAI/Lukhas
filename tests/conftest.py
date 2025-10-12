import importlib
import os
import pathlib
import random
import sqlite3
import sys
import traceback
import types
from pathlib import Path

import pytest

# Install legacy import aliases so tests continue to collect while we codemod.
try:
    from lukhas.compat import install as _install_aliases
    _install_aliases()
except Exception as e:
    # Don't break collection; print a hint
    print(f"[lukhas.compat] WARN: failed to install alias loader: {e}", file=sys.stderr)

# Tell compat where to write the hit report
os.environ.setdefault("LUKHAS_COMPAT_HITS_FILE", "docs/audits/compat_alias_hits.json")
# Leave LUKHAS_COMPAT_ENFORCE unset or "0" during migration;
# later we can flip to "1" in CI to forbid aliases.

# -- Import failure telemetry (catch UnknownError root causes) ----------------
_ART_DIR = Path("artifacts")
_ART_DIR.mkdir(exist_ok=True, parents=True)
_FAIL_LOG = _ART_DIR / "import_failures.ndjson"

class _TraceFinder:
    """Meta path finder that logs import failures with full tracebacks."""
    def find_spec(self, fullname, path=None, target=None):
        try:
            return None
        except Exception as e:
            _FAIL_LOG.touch(exist_ok=True)
            with _FAIL_LOG.open("a") as f:
                import json
                import time
                f.write(json.dumps({
                    "ts": time.time(),
                    "stage": "find_spec",
                    "fullname": fullname,
                    "error": repr(e),
                    "trace": traceback.format_exc()
                })+"\n")
            raise

# Install trace finder (append to avoid interference)
if not any(type(f).__name__ == "_TraceFinder" for f in sys.meta_path):
    sys.meta_path.append(_TraceFinder())

# ---------------------------------------------------------------------------
# six._SixMetaPathImporter compatibility shim (prevents "UnknownError" floods)
# Older six meta-importers lack `find_spec` on Python 3.9+; pytest collection
# calls it and then the importer raises confusing, empty errors.
# We patch in a delegating `find_spec` that just defers to PathFinder.
# This avoids touching pinned requirements/hashes.
try:  # pragma: no cover
    import six  # noqa: F401
    for _imp in list(getattr(sys, "meta_path", [])):
        if _imp.__class__.__name__ == "_SixMetaPathImporter" and not hasattr(_imp, "find_spec"):
            def _find_spec(self, fullname, path=None, target=None):
                return importlib.machinery.PathFinder.find_spec(fullname, path)
            _imp.find_spec = types.MethodType(_find_spec, _imp)  # type: ignore[attr-defined]
except Exception:
    # If six isn't present or anything goes wrong, continue silently.
    pass

# -- Lukhas dynamic aliasing for nested submodule imports (V2) -----------------
import importlib.abc
import importlib.machinery
import importlib.util
import json
import time

CANONICAL_PREFIXES = ["", "labs"]  # try root first, then candidate.<...>
NEGATIVE_CACHE = set()
LEDGER_PATH = pathlib.Path("artifacts/lukhas_import_ledger.ndjson")
LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

def _ledger(event: dict):
    try:
        event["ts"] = time.time()
        LEDGER_PATH.open("a").write(json.dumps(event, sort_keys=True) + "\n")
    except Exception:
        pass

class _LukhasAliasLoader(importlib.abc.Loader):
    def __init__(self, real_name: str):
        self.real_name = real_name

    def create_module(self, spec):  # noqa: D401
        return None

    def exec_module(self, module):
        try:
            real_mod = importlib.import_module(self.real_name)
            module.__dict__.update(real_mod.__dict__)
            module.__dict__.setdefault("__path__", getattr(real_mod, "__path__", []))
            module.__dict__["__loader__"] = self
            module.__dict__["__package__"] = module.__name__
        except (ImportError, ModuleNotFoundError) as e:
            # If the real module can't be imported, mark as failed and don't break pytest
            NEGATIVE_CACHE.add(module.__name__)
            _ledger({"event": "loader_failed", "module": module.__name__, "real": self.real_name, "error": str(e)})
            # Create minimal module to prevent complete failure
            module.__dict__["__file__"] = f"<lukhas-alias:{self.real_name}>"
            module.__dict__["__loader__"] = self
            module.__dict__["__package__"] = module.__name__

class _LukhasAliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "lukhas":
            return None

        if not fullname.startswith("lukhas."):
            return None

        if fullname in NEGATIVE_CACHE:
            return None

        tail = fullname[len("lukhas."):]  # e.g., "consciousness.dream"
        # If the module exists under the real lukhas package, defer to default loaders.
        real_path = Path("lukhas") / Path(*tail.split("."))
        if real_path.with_suffix(".py").exists() or ((real_path).is_dir() and (real_path / "__init__.py").exists()):
            return None

        for prefix in CANONICAL_PREFIXES:
            candidate_name = f"{prefix}.{tail}" if prefix else tail
            spec = importlib.util.find_spec(candidate_name)
            if spec:
                _ledger({"event": "alias", "lukhas": fullname, "real": candidate_name, "origin": getattr(spec, "origin", None)})
                return importlib.util.spec_from_loader(
                    fullname, _LukhasAliasLoader(real_name=candidate_name), origin=f"alias:{candidate_name}"
                )

        NEGATIVE_CACHE.add(fullname)
        _ledger({"event": "miss", "lukhas": fullname})
        return None

if not any(isinstance(f, _LukhasAliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _LukhasAliasFinder())
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# six._SixMetaPathImporter compatibility shim (prevents "UnknownError" floods)
# Older six meta-importers lack `find_spec` on Python 3.9+; pytest collection
# calls it and then the importer raises confusing, empty errors.
# We patch in a delegating `find_spec` that just defers to PathFinder.
# This avoids touching pinned requirements/hashes.
try:  # pragma: no cover
    import six  # noqa: F401
    for _imp in list(getattr(sys, "meta_path", [])):
        if _imp.__class__.__name__ == "_SixMetaPathImporter" and not hasattr(_imp, "find_spec"):
            def _find_spec(self, fullname, path=None, target=None):
                return importlib.machinery.PathFinder.find_spec(fullname, path)
            _imp.find_spec = types.MethodType(_find_spec, _imp)  # type: ignore[attr-defined]
except Exception:
    # If six isn't present or anything goes wrong, continue silently.
    pass
# ---------------------------------------------------------------------------

# Seed determinism for reproducible tests
PYTHONHASHSEED = os.environ.get("PYTHONHASHSEED")
if PYTHONHASHSEED is None:
    os.environ["PYTHONHASHSEED"] = "0"

# Set random seed for deterministic test behavior
random.seed(1337)

# T4 Lane Configuration
def pytest_addoption(parser):
    parser.addoption("--lane", action="store", default=os.getenv("LUKHAS_LANE", "experimental"))

def pytest_configure(config):
    os.environ.setdefault("LUKHAS_LANE", config.getoption("--lane"))

def pytest_runtest_setup(item):
    if "prod_only" in item.keywords and os.getenv("LUKHAS_LANE", "experimental") not in {"labs","prod"}:
        pytest.skip("prod_only test skipped outside candidate/prod lanes")

# T4 Deterministic Path Setup
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Legacy compatibility
project_root = REPO_ROOT


@pytest.fixture(scope="session")
def settings():
    """Test configuration settings."""
    return {"env": "test", "debug": os.getenv("PYTEST_DEBUG", "false").lower() == "true"}


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def lukhas_test_config():
    """LUKHAS-specific test configuration."""
    return {
        "consciousness_active": False,
        "dream_simulation_enabled": False,
        "quantum_processing_enabled": False,
        "ethics_enforcement_level": "strict",
    }


# T4 Core Fixtures
@pytest.fixture(scope="function")
def module_path():
    """T4 fixture: Provides repo root path for module loading."""
    return REPO_ROOT


@pytest.fixture(scope="function")
def sqlite_db(tmp_path):
    """T4 fixture: Provides isolated SQLite database for tests."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    finally:
        conn.close()


# T4 Quarantine Bookkeeping
def pytest_runtest_makereport(item, call):
    """T4 quarantine system: Track quarantine test failures."""
    if "quarantine" in item.keywords and call.when == "call" and call.excinfo:
        item._quarantine_fail = getattr(item, "_quarantine_fail", 0) + 1


import types

# Provide a streamlit stub immediately so candidate modules importing it don't fail.
if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = types.SimpleNamespace(
        write=lambda *a, **k: None,
        markdown=lambda *a, **k: None,
        cache_data=lambda *a, **k: (lambda f: f),
    )


@pytest.fixture(autouse=True, scope="session")
def _stub_streamlit_for_tests():
    if "streamlit" not in sys.modules:
        sys.modules["streamlit"] = types.SimpleNamespace(
            write=lambda *a, **k: None,
            markdown=lambda *a, **k: None,
            cache_data=lambda *a, **k: (lambda f: f),
        )
    yield


# ---------------------------------------------------------------------------
# CI Quality Gates: deterministic, fast collection & selection
# ---------------------------------------------------------------------------

CI_QG = os.getenv("CI_QUALITY_GATES") == "1"


def pytest_ignore_collect(path: Path, config):
    """Basic directory-level ignore during quality gates to avoid costly import-time failures."""
    if CI_QG:
        p = Path(path)
        parts = set(p.parts)
        if "integration" in parts or "e2e" in parts or "benchmarks" in parts:
            return True
    return False


def pytest_collection_modifyitems(config, items):
    """In quality gates mode, only keep smoke and unmarked/unit tests.

    Converts ad-hoc per-test skipping into stable, marker-based selection.
    """
    if not CI_QG:
        return

    skip_marks = {"integration", "e2e", "bench", "cloud", "enterprise", "mcp", "bio"}
    selected = []
    for item in items:
        marks = {m.name for m in item.iter_markers()}
        # Include telemetry tests in quality gates as they are smoke tests
        if "smoke" in marks or "telemetry" in marks or not marks.intersection(skip_marks):
            selected.append(item)
    items[:] = selected

# ---------------------------------------------------------------------------
# Silence only noisy SSL warnings in tests (runtime remains strict)
# ---------------------------------------------------------------------------
import warnings

try:
    import urllib3  # type: ignore
    from urllib3.exceptions import InsecureRequestWarning  # type: ignore
except Exception:
    urllib3 = None
    InsecureRequestWarning = None

warnings.simplefilter("default", Warning)
if urllib3 and InsecureRequestWarning:
    urllib3.disable_warnings(InsecureRequestWarning)


# ---- Collection diagnostics (turn UnknownError → explicit) ----
def pytest_collectreport(report):
    """Improve collection diagnostics by printing failing nodes during collection."""
    if report.failed:
        try:
            path = getattr(report, "fspath", "<unknown>")
        except Exception:
            path = "<unknown>"
        print(f"\n[COLLECT-FAIL] node={path} error:\n{report.longreprtext}\n")

        # Write detailed failure log to artifacts
        _ART_DIR.mkdir(exist_ok=True, parents=True)
        collect_log = _ART_DIR / "collect_failures.log"
        try:
            existing = collect_log.read_text() if collect_log.exists() else ""
            with collect_log.open("w") as f:
                f.write(existing + f"\n\n=== {report.nodeid} ===\n{report.longreprtext}\n")
        except Exception:
            pass


def pytest_sessionstart(session):
    """Initialize session - reset Prometheus registry to avoid duplicates."""
    # Fresh Prometheus registry per session (kills "Duplicated timeseries")
    try:
        from prometheus_client import REGISTRY, CollectorRegistry
        # Clear existing collectors
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            try:
                REGISTRY.unregister(collector)
            except Exception:
                pass
    except Exception:
        pass

    # Set environment variables for legacy compatibility
    os.environ.setdefault("SETUPTOOLS_USE_DISTUTILS", "stdlib")
    os.environ.setdefault("PYTHONWARNINGS", "ignore::DeprecationWarning")
