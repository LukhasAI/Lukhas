# JULES_TODO — Repo audit, wiring, and heavy-lift engineering tasks

> For Jules agents (Jules-01 … Jules-05). These tasks require repo-level knowledge, multi-file refactors, instrumentation, and orchestration wiring.

## Purpose

Jules agents take on deep repo mapping, cross-module refactors, instrumentation, and audit tasks that require reasoning about architecture and multiple files. They do NOT write tests. They prepare the codebase so Claude/Codex can implement tests and targeted fixes safely.

---

## Priority buckets

1. **Critical infra & guardrails** (high) — ensure self-heal infra (guard_patch, CI, labot) is solid.
2. **Repo mapping & transparency** (high) — produce `TRANSPARENCY_SCORECARD.md`, entropy/drift radar, dependency graph.
3. **Refactors & wiring** (med) — small safe refactors, remove duplication, create stable module API boundaries.
4. **Instrumentation & observability** (med) — add OTEL spans to critical paths and ensure tests include traces.
5. **Prepare Stage B/C scaffolds** (low→med) — create refactor harnesses, bench harnesses, and mutation-aware merging.

---

## Assignments (suggested split)

### **Jules-01** — *Repo mapping & scorecard*

- Produce `docs/TRANSPARENCY_SCORECARD.md` summarizing validation status of modules (Fully Validated / Prototype / Needs Review).
- Generate `reports/repo_graph.dot` (import graph) & `reports/entropy_radar.json` (symbolic drift map).
- Commands:
  ```bash
  # basic file list + blame
  git ls-files '*.py' > reports/all_py_files.txt
  git rev-parse --abbrev-ref HEAD
  ```
- Deliverables: scorecard + graph + short README explaining methodology.

### **Jules-02** — *MATRIZ & Core refactor pilot*

- Identify 3 high-risk MATRIZ files (e.g., `ethical_reasoning_system.py`) and propose safe refactor plans: split large files into smaller modules, create clear public API surfaces.
- Create ADR(s) describing proposed changes and acceptance tests (mutation/coverage/perf).
- Deliverable: PR(s) that only add tests/placeholders & ADR, not prod logic.

### **Jules-03** — *Instrumentation & canaries*

- Add OpenTelemetry spans to `serve/main.py` middleware and to `serve/openai_routes.py`.
- Create `tests/smoke/trace_integration_test.py` that validates required spans exist in a test trace.
- Deliverable: small PR with instrumentation + tests.

### **Jules-04** — *CI hermeticity & SLSA readiness*

- Add reproducible runner recipe (poetry/uv/rye or Nix example), add SLSA metadata template (`.slsa/README.md`).
- Add `scripts/containerized-run.sh` to reproduce CI locally.
- Deliverable: CI recipe, short checklist for maintainers.

### **Jules-05** — *Governance & playbooks*

- Produce `docs/steward_process.md`: two-key rule, steward rotation, patch sizes, canary checklist, rollback automation.
- Implement `scripts/split_labot_import.sh` (see earlier script) and guard against accidental large imports.
- Deliverable: steward doc + split script PR.

---

## Quick audit commands (Jules do this first)

```bash
# basic hygiene
python3 -m pip install --upgrade pip
pip install ruff mypy pip-audit safety jq graphviz

# lint & types only changed files
git fetch origin main
git checkout main
ruff .
mypy .

# security quick check
pip-audit

# produce import graph (example)
python - <<'PY'
import modulefinder, json, sys
mf = modulefinder.ModuleFinder()
mf.run_script('serve/main.py')
print(list(mf.modules.keys())[:200])
PY
```

---

## Acceptance criteria for Jules work

* Every change is ≤ 40 LOC and ≤ 2 files for jumbo PRs (unless infra/CI).
* Each refactor includes an ADR + regression tests (or test harness).
* No direct modifications to `.lukhas/protected-files.yml` items without steward approval.
* All PRs are created as **Draft** and labelled `labot` + `jules:review`.

---

## Notes / Context

* Jules should coordinate with the steward weekly and log findings in `reports/jules-audit/`.
* Jules must export machine-readable outputs (JSON): `reports/TRANSPARENCY_SCORECARD.json`, `reports/entropy_radar.json`.
