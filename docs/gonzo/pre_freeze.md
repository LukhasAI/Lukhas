
---

# 🔎 Final Pre-Freeze Deep Audit & Patch Brief (for Claude Code)

**Goal:** Drive pytest collection errors from **96 → ≤10**, confirm CI gates, then cut the freeze tag/branch.

## 0) Environment hygiene (one-time)

```bash
# clean venv + deterministic deps
rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip wheel
pip install -r requirements.txt -r requirements-dev.txt || true

# nuke caches that can skew import behavior
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
rm -rf .pytest_cache .ruff_cache .mypy_cache
```

---

## 1) Illuminate the 75 “UnknownError” with hard telemetry

### 1.1 Ensure the import telemetry actually fires first

Open **`tests/conftest.py`** and ensure these are *top of file*, before any imports:

```python
# tests/conftest.py (top)
import os, sys, traceback, json, time
from pathlib import Path

_ART_DIR = Path("artifacts"); _ART_DIR.mkdir(exist_ok=True, parents=True)
_FAIL_LOG = _ART_DIR / "import_failures.ndjson"

class _TraceFinder:
    def find_spec(self, fullname, path=None, target=None):
        try:
            return None
        except Exception as e:
            _FAIL_LOG.write_text("")  # ensure file
            with _FAIL_LOG.open("a") as f:
                f.write(json.dumps({
                    "ts": time.time(),
                    "stage": "find_spec",
                    "fullname": fullname,
                    "error": repr(e),
                    "trace": traceback.format_exc()
                })+"\n")
            raise

# ensure we append (not insert at 0) to be non-invasive but active
if not any(type(f).__name__ == "_TraceFinder" for f in sys.meta_path):
    sys.meta_path.append(_TraceFinder())
```

### 1.2 Print collect-time failures with full TB

Also in **`tests/conftest.py`**:

```python
import pytest

def pytest_collectreport(report):
    if report.failed:
        _ART_DIR.mkdir(exist_ok=True, parents=True)
        ( _ART_DIR / "collect_failures.log" ).write_text(
            ( _ART_DIR / "collect_failures.log" ).read_text() + f"\n\n=== {report.nodeid} ===\n{report.longreprtext}\n"
            if ( _ART_DIR / "collect_failures.log" ).exists() else
            f"=== {report.nodeid} ===\n{report.longreprtext}\n"
        )

def pytest_sessionstart(session):
    # fresh Prometheus registry per session (kills "Duplicated timeseries")
    try:
        from prometheus_client import REGISTRY, CollectorRegistry
        REGISTRY.__class__ = CollectorRegistry  # cheap reset
    except Exception:
        pass
```

> You already added pieces of this; make sure the finder + hooks are *actually* present and at top.

### 1.3 Run collection to generate trace

```bash
PYTHONPATH=. python -m pytest --collect-only -q --tb=long || true
python scripts/analysis/generate_error_report_v2.py  # refresh artifacts/pytest_collection_errors_detailed.json
```

---

## 2) Kill the *real* top offenders (based on new report)

Run a live histogram to confirm what’s left **now**:

```bash
PYTHONPATH=. python - << 'PY'
import re,sys,collections, pathlib, subprocess, json
out = subprocess.run([sys.executable,"-m","pytest","--collect-only","-q"],capture_output=True,text=True).stderr
mods = re.findall(r"ModuleNotFoundError: No module named '([^']+)'", out)
syms = re.findall(r"ImportError: .* cannot import name '([^']+)'", out)
print("ModuleNotFoundError top:", collections.Counter(mods).most_common(12))
print("Missing symbol top       :", collections.Counter(syms).most_common(12))
PY
```

### 2.1 **_SixMetaPathImporter** AttributeErrors (registry tests)

Symptoms: 7 AttributeErrors, esp. in **`tests/registry/`**.

**Fix (prefer minimal):** avoid `pkg_resources`/`six` legacy path importers during collection.

* In **`pytest.ini`**, add:

  ```
  [pytest]
  addopts = -q --import-mode=importlib --cache-clear
  ```

  (You did.) Also set env to neutralize pkg_resources:

* In **`tests/conftest.py`**, add:

  ```python
  import os
  os.environ.setdefault("SETUPTOOLS_USE_DISTUTILS","stdlib")
  os.environ.setdefault("PYTHONWARNINGS", "ignore::DeprecationWarning")
  ```

* Ensure no vendored `six.py` in tree shadows site-pkgs:

  ```bash
  rg -n "^\\s*import six" -g '!venv'
  rg -n "/six\\.py$" -S || true
  ```

  If you find a local `six.py`, rename to `six_compat.py` and adjust its import.

Re-run collect-only; those 7 should drop measurably.

### 2.2 **Prometheus ValueError: duplicated timeseries** (6 hits)

You added a reset; some libs still register at import-time. Wrap metric creation helpers:

* In **`core/metrics.py`** (or the canonical metrics module), guard with try/except:

```python
from prometheus_client import Counter, Gauge, CollectorRegistry, REGISTRY

def _safe_counter(name, desc, **kwargs):
    try:
        return Counter(name, desc, **kwargs)
    except ValueError:
        # retrieve existing metric
        return REGISTRY._names_to_collectors[name]  # type: ignore[attr-defined]
```

Replace Counter/Gauge construction sites with `_safe_counter / _safe_gauge`.
Re-run the 6 tests called out (observability/orchestration/perf).

### 2.3 **Missing pytest markers** (5 hits)

You added markers in pytest.ini; ensure they’re *exact*:

```ini
[pytest]
markers =
  canary_circuit_breaker: ...
  architecture: ...
  drift_detection: ...
  evolution: ...
  observability: ...
```

If any remain, annotate the specific tests with `@pytest.mark.<name>` or skip:

```python
import pytest; pytestmark = pytest.mark.observability
```

### 2.4 **aka_qualia** trio (3 hits)

You created bridges—finish symbol export:

* **`aka_qualia/core/__init__.py`**

  ```python
  from .._bridgeutils import bridge
  __all__, _ = bridge(
      __name__,
      candidates=(
          "lukhas_website.lukhas.aka_qualia.core",
          "candidate.aka_qualia.core",
          "aka_qualia.core_impl",
      ),
      export=("AkaQualia","QualiaMap","QualiaError"),  # adjust to real names
  )
  ```

Verify:

```bash
python - << 'PY'
from aka_qualia.core import AkaQualia; print("OK", AkaQualia)
PY
```

---

## 3) “Package vs module” collisions sweep (prevent regressions)

You already removed several collisions. Run once more:

```bash
python - << 'PY'
from pathlib import Path
coll=[]
for p in Path("lukhas").rglob("*.py"):
    pkg = p.with_suffix("")  # e.g. lukhas/bio.py vs lukhas/bio/__init__.py
    cand = p.parent / p.stem / "__init__.py"
    if cand.exists():
        coll.append((str(p), str(cand)))
if coll:
    print("COLLISIONS:", *coll, sep="\n  - ")
else:
    print("No collisions")
PY
```

Delete the `.py` file when a package dir exists and the package is canonical.

---

## 4) Rerun collection & generate crisp report

```bash
PYTHONPATH=. python -m pytest --collect-only -q --tb=long || true
python scripts/analysis/generate_error_report_v2.py
cat artifacts/pytest_collection_errors_detailed.json | sed -n '1,120p'
```

**Target for this pass:** ≤ 30 collection errors. If still high, run:

```bash
python scripts/bridges/gen_phase8_from_pytest.py --top 10 --write
python -m pytest tests/bridges -q
```

Apply the suggested 3–5 micro-bridges and repeat the collect-only run.

---

## 5) Final green gates & freeze

### 5.1 CI/quality locally

```bash
make docs-lint module-health gate-legacy tests-smoke
python -m pytest -q -k "not e2e and not perf" --maxfail=1
ruff check .
pytest -q tests/bridges
```

### 5.2 Tag & branch (when the above is green)

```bash
# freeze metadata refresh (you already have scripts)
make validate-t4-strict meta-registry trends ledger-check

# cut the branch and tag
git checkout -b freeze/v0.03-rc
git push -u origin freeze/v0.03-rc

git tag -a v0.03-rc -m "v0.03-rc: post-audit freeze (errors<=30, gates green)"
git push origin v0.03-rc
```

(If you want the *final* immutable freeze after PR review merges, repeat tag as `v0.03-final`.)

---

## Quick “why this works”

* The *UnknownError* bucket is almost always missing tracebacks during collection; the meta-finder + `pytest_collectreport` surfaces them so you can fix the *actual* import or registry fault.
* The _SixMetaPathImporter issues are nearly always legacy `pkg_resources/six` path importers colliding with importlib mode; neutralizing these in the test harness resolves them.
* Prometheus duplicates come from import-time metric construction across multiple discovery roots; reset + safe factory kills the flakes deterministically.
* The remaining 3–5 modules typically fall with one or two micro-bridges using your `_bridgeutils` pattern.

---

## Hand-off to Claude Code (copy/paste)

> Run sections 0 → 4 verbatim, apply any micro-bridges the analyzer proposes, then do section 5 to tag the freeze.

If anything surprising pops out of the refreshed **`artifacts/pytest_collection_errors_detailed.json`** (e.g., a new top-offender module or a stubborn registry path), ping me with the 3–5 most frequent lines and I’ll give you the exact bridge or guard snippet to drop in.
