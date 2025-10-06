---
status: wip
type: documentation
---
# LUKHAS Test Suite — T4 Upgrade (Execution Plan for Claude)

**Tone:** tight, surgical, fearless. This is the **single source of truth** for tests. Use it to drive automated changes and PRs. For complete copy‑paste file bodies, see **`docs/gonzo/LUKHAS_Test_Suite—Add_ons.md`**.

---

## Phase 0: Determinism & Policy (10 min)
Lock the universe first.

- **pytest.ini (drop‑in)**
  ```ini
  [pytest]
  addopts = -q -ra -s --maxfail=1 --strict-markers --durations=10
  filterwarnings = error
  markers =
      tier1: critical core systems
      tier2: integration & orchestration
      tier3: supporting modules
      tier4: experimental/research
      matriz: MATRIZ-focused tests
      golden: uses golden artifacts
      smoke: lightweight health checks
      quarantine: flaky or known-bad (runs, blocks if fails twice)
      slow: long-running
  ```
- **Determinism env** (CI + `make test-*`): `TZ=UTC PYTHONHASHSEED=0 NUMBA_DISABLE_JIT=1`.
- **Bold:** unmarked tests **fail collection** (ownership required). See Add‑ons → *spec_lint.py*.

---

## Phase 1: Infra Stabilization (1–2h)
Fix infra, not behavior.

- **Core fixtures (drop‑in)** `tests/conftest.py`
  ```python
  import os, sys, pathlib, sqlite3, pytest
  REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
  if str(REPO_ROOT) not in sys.path:
      sys.path.insert(0, str(REPO_ROOT))
  @pytest.fixture(scope="function")
  def module_path():
      return REPO_ROOT
  @pytest.fixture(scope="function")
  def sqlite_db(tmp_path):
      db = tmp_path / "test.db"
      conn = sqlite3.connect(db)
      conn.execute("PRAGMA foreign_keys=ON;")
      try:
          yield conn
      finally:
          conn.close()
  # Quarantine bookkeeping
  def pytest_runtest_makereport(item, call):
      if "quarantine" in item.keywords and call.when == "call" and call.excinfo:
          item._quarantine_fail = getattr(item, "_quarantine_fail", 0) + 1
  ```
- **Logger hygiene:** use `getLogger(__name__)` only; forbid root logger in tests via lint rule.
- **Artifacts:** `reports/tests/infra/collection.json`, `reports/tests/infra/timings.json` (Add‑ons → *flake_sentinel.py* can collect timings/outcomes).

---

## Phase 2: Branching & Safety (30 min)
- Create `feat/test-consolidation-clean`.
- WIP cap **2 PRs** + `tests-only` label; CI ensures PRs only touch `tests*/`, `pytest.ini`, `conftest.py`, `ops/fixtures/`.

---

## Phase 3: Gap Analysis (1h)
- **Coverage scan**
  ```bash
  pytest --cov=lukhas --cov=MATRIZ --cov-branch \
         --cov-report=xml:reports/tests/cov.xml \
         --cov-report=term-missing
  ```
- **Priority matrix** → `reports/tests/priority_matrix.csv` (from coverage + module criticality). See Add‑ons → *coverage_gate.py* (also stores/ratchets per‑module baselines).

> **Contract‑first:** refuse new tests where package lacks `CONTRACT.md` **and** a matching spec. See Add‑ons → *contract_check.py*.

---

## Phase 4: Creation Roadmap (2h)
- **Spec template** `tests/specs/SPEC_TEMPLATE.yaml` (canonical in Add‑ons).
- **Spec stubs generator** (JSON‑driven from `LUKHAS_ARCHITECTURE_MASTER.json`).
- **Work queues** `reports/tests/queues/tier1.csv`, `tier2.csv`, …
- **Goldens:** each MATRIZ/identity/orchestration route has ≥1 golden JSON + validator (Add‑ons → *validate_golden.py*).

---

## Phase 5: Infra Enhancements (1h)
- **Parallelism:** `-n auto --dist loadgroup` for Tier‑2/3; Tier‑1 serial unless marked safe.
- **Timeouts:** `pytest-timeout` `--timeout=20`; use `@pytest.mark.slow(timeout=120)` for long tests.
- **Perf budget:** fail if total `durations` > 300s (env‑tunable).
- **Mutation seed:** weekly `mutmut` lane for top‑10 Tier‑1 functions (report‑only). Add‑ons provides `pyproject.toml` snippet.

---

## Success Metrics
- **Immediate:** 0 collection errors; deterministic DB tests; ≥95% tier‑marked; suite ≤4 min (warn at 6).
- **Strategic:** Tier‑1 ≥85% line / 70% branch; ≥1 golden per public API; flake rate <0.5%; coverage never decreases on touched modules.

---

## Risk Mitigation
- `@pytest.mark.serial` for fragile concurrency.
- Enforce absolute imports (ruff TID252); fail illegal relatives.
- Per‑test timing budgets; auto‑issue on >2× drift (Add‑ons → *flake_sentinel.py*).
- **Anti‑fake tests:** reject `assert True/False`, bare `except: pass`, empty tests (implement in pre‑commit/CI).

---

## Make targets (drop‑in)
```make
.PHONY: test-tier1 test-all test-fast test-report test-clean spec-lint contract-check specs-sync test-goldens

test-clean:
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + || true

test-tier1:
	@TZ=UTC PYTHONHASHSEED=0 pytest -m "tier1 and not quarantine" --cov=lukhas --cov=MATRIZ --cov-branch --cov-report=xml:reports/tests/cov.xml

test-all:
	@TZ=UTC PYTHONHASHSEED=0 pytest -m "not quarantine" --cov=lukhas --cov=MATRIZ --cov-branch --cov-report=xml:reports/tests/cov.xml

test-fast:
	@TZ=UTC PYTHONHASHSEED=0 pytest -m "smoke or tier1" -q

test-report:
	@python3 - <<'PY'
import xml.etree.ElementTree as ET; p='reports/tests/cov.xml'
try:
 t=ET.parse(p).getroot(); print('Coverage line-rate:', t.attrib.get('line-rate','?'))
except Exception as e:
 print('No coverage report yet:', e)
PY

spec-lint:
	@python3 tools/tests/spec_lint.py tests/specs

contract-check:
	@python3 tools/tests/contract_check.py $${BASE_REF:-origin/main}

specs-sync:
	@python3 tools/tests/specs_sync.py

test-goldens:
	@python3 tools/tests/validate_golden.py
```

---

## Where to be courageous
- Reject unmarked tests; quarantine is **visible debt** (auto‑file issue w/ failing seed).
- Prefer **contracts + goldens** over mocks for core domain; mock only external I/O.

---

### Pointers to Add‑ons Pack
- `tools/tests/spec_lint.py`
- `tools/tests/contract_check.py`
- `tools/tests/specs_sync.py`
- `tools/tests/validate_golden.py`
- `tools/tests/flake_sentinel.py`
- `tools/tests/coverage_gate.py`
- `tests/specs/SPEC_TEMPLATE.yaml`
- `pyproject.toml` → `[tool.mutmut]` section