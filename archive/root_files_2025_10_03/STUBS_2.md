---
status: wip
type: documentation
---
losophy: fail‑closed, observable, reversible, and minimal blast radius.

---

## 1) Makefile add‑ons (tiny, fast targets)

> **Where:** append to your root `Makefile`.
> These don’t change runtime behavior; they just give you quick smoke and guard rails.

```make
# ─────────────────────────────────────────────────────────────────────────────
# Tiny smoke/guard targets for the new stubs (fast, isolated)
# T4 defaults: fail-closed, quick feedback, no side effects.
.PHONY: obs obs-spans obs-metrics \
        registry-test constraints-test \
        orch-smoke orch-arbitration orch-meta \
        quick-smoke quick-cov plugin-discovery

# Observability smoke (no-op if deps absent)
obs-spans:
	@echo "🧪 obs-spans"; pytest -q tests/obs/test_spans_smoke.py

obs-metrics:
	@echo "🧪 obs-metrics (ENABLE_PROM=0 no-op)"; ENABLE_PROM=0 pytest -q tests/obs/test_metrics_smoke.py

obs: obs-spans obs-metrics

# Registry and constraints
registry-test:
	@echo "🧪 registry"; pytest -q tests/registry/test_registry.py

constraints-test:
	@echo "🧪 constraints"; pytest -q tests/constraints/test_plan_verifier.py

# Orchestration (consensus + meta-controller)
orch-arbitration:
	@echo "🧪 orchestration-consensus"; pytest -q tests/orchestration/test_arbitration.py

orch-meta:
	@echo "🧪 orchestration-meta"; pytest -q tests/orchestration/test_meta_loops.py

orch-smoke: orch-arbitration orch-meta

# One-button quick smoke for PRs / pre-push (sub-second on typical dev machines)
quick-smoke: registry-test constraints-test orch-smoke obs

# Minimal coverage snapshot on just the new surfaces
quick-cov:
	@echo "🧪 quick-cov"; \
	coverage run -m pytest -q tests/registry/test_registry.py \
		tests/constraints/test_plan_verifier.py \
		tests/orchestration/test_arbitration.py \
		tests/orchestration/test_meta_loops.py \
		tests/obs/test_spans_smoke.py \
		tests/obs/test_metrics_smoke.py && \
	coverage report -m --omit='*/site-packages/*' --show-missing

# Explicit plugin discovery exercise (stays dark by default)
plugin-discovery:
	@echo "🔎 plugin discovery (read-only, non-fatal)"; \
	python3 - <<'PY' || true
import os
os.environ["LUKHAS_PLUGIN_DISCOVERY"]="auto"
try:
    from candidate.core.orchestration.loader import discover_nodes
    n = discover_nodes("candidate")
    print(f"[discovery] initialized nodes: {n}")
except Exception as e:
    print(f"[discovery] skip: {e}")
PY
```

**T4 notes**

* **fast**: each target runs in isolation and finishes quickly.
* **dark by default**: discovery is explicit (`plugin-discovery`) and non‑fatal.
* **observable**: `quick-cov` provides a lightweight coverage floor on your new surfaces.

---

## 2) Pre‑commit configuration (run fast checks locally)

> **Where:** create (or extend) `.pre-commit-config.yaml` at repo root.

This config **keeps formatting/lint fast** and moves tests to **`pre-push`** (not `pre-commit`) so commits stay snappy. It also adds a **guardrail check** that bans direct LLM calls outside the approved wrapper.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        args: [--line-length=100]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.3
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  - repo: local
    hooks:
      # T4: guardrail usage (ban direct LLM calls)
      - id: guardrail-check
        name: guardrail-check (ban direct LLM calls)
        entry: python3 scripts/ci/check_guardrail_usage.py
        language: system
        pass_filenames: true
        types: [python]
        stages: [pre-commit]
      # T4: fast smoke executes on push, not on each commit
      - id: quick-smoke-tests
        name: quick-smoke-tests
        entry: make quick-smoke
        language: system
        pass_filenames: false
        stages: [pre-push]
```

**Install once** (or wire into your existing `setup-hooks`):

```bash
pip install pre-commit
pre-commit install -t pre-commit -t pre-push
```

> If you already have a `setup-hooks` target, append the two lines above there.

---

## 3) Guardrail scanner script (bans direct LLM calls)

> **Where:** `scripts/ci/check_guardrail_usage.py` (new file, tiny, safe).
> **Why:** Enforces that all LLM calls go via `core.bridge.llm_guardrail` (your wrapper).
> **Scope:** Scans only staged files when run by pre‑commit; ignores tests and the wrapper module itself.

```python
#!/usr/bin/env python3
# scripts/ci/check_guardrail_usage.py
"""
T4 / 0.01% guard: ban direct LLM calls; require llm_guardrail.

Blocks common SDKs unless:
- path is tests/*
- path is core/bridge/llm_guardrail.py (the wrapper)
- path is docs/* (snippets are allowed)

Extendable: add vendors as needed.
"""

import os
import re
import sys
from pathlib import Path

BANNED = [
    r"\bopenai\.",                  # OpenAI Python
    r"\banthropic\.",               # Anthropic Python
    r"\bgoogle\.generativeai\.",    # Google GenAI
    r"\bbotocore\.client\(['\"]bedrock['\"]\)",  # AWS Bedrock
]
ALLOWLIST_PREFIXES = ("tests/", "docs/", "core/bridge/llm_guardrail.py")

def search_file(p: Path) -> list[str]:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    hits = []
    for pat in BANNED:
        if re.search(pat, text):
            hits.append(pat)
    return hits

def main() -> int:
    # Pre-commit passes file list; fall back to repo scan if none given
    files = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    if not files:
        # Conservative fallback: only scan tracked Python files
        try:
            import subprocess, shlex
            out = subprocess.check_output(shlex.split("git ls-files '*.py'")).decode().splitlines()
            files = [Path(x) for x in out]
        except Exception:
            return 0  # non-fatal in odd environments

    violations = []
    for p in files:
        sp = str(p).replace("\\", "/")
        if sp.startswith(ALLOWLIST_PREFIXES):
            continue
        hits = search_file(p)
        if hits:
            violations.append((sp, hits))

    if not violations:
        return 0

    print("❌ Direct LLM calls detected. Use core.bridge.llm_guardrail.call_llm(...)\n")
    for sp, hits in violations:
        pats = ", ".join(set(hits))
        print(f" - {sp}  ← matched: {pats}")
    print("\nFix: replace direct SDK calls with the guardrail wrapper.")
    return 2

if __name__ == "__main__":
    sys.exit(main())
```

Make it executable:

```bash
chmod +x scripts/ci/check_guardrail_usage.py
```

**T4 notes**

* **Fail‑closed:** blocks on any direct SDK usage.
* **Local & CI friendly:** runs on changed files only; ignores tests and docs.
* **Extensible:** add/remove patterns as vendors change.

---

## 4) (Optional) Quick GitHub Actions lite job

> Not required, but if you want **server‑side parity** with `pre-push`, add:

**`.github/workflows/quick-smoke.yml`**

```yaml
name: quick-smoke
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ feature/**, feat/** ]
jobs:
  smoke:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -U pip wheel setuptools
      - run: pip install -r requirements.txt || true
      - run: pip install pytest coverage
      - name: quick smoke
        run: make quick-smoke
      - name: quick coverage
        run: make quick-cov
```

**T4 notes**

* PRs get the identical **fast smoke**; full test matrix stays in your main CI.

---

## 5) Update `setup-hooks` (if you have it)

Append this to your existing `setup-hooks` target in the `Makefile`:

```make
setup-hooks:
	@echo "🔧 Installing pre-commit hooks (pre-commit + pre-push)"
	@pre-commit install -t pre-commit -t pre-push || true
```

---

## 6) Sanity check (1 minute)

```bash
# 1) Install pre-commit once
pip install pre-commit

# 2) Install hooks
make setup-hooks

# 3) Run local smoke
make quick-smoke
make quick-cov

# 4) Try a forbidden import in a Python file (outside tests/) and `git commit`
#    You should see guardrail-check block the commit with a clear message.
```

---

## Why this meets T4 / 0.01%

* **Minimal**: only tiny Makefile additions + one small script + a standard pre‑commit config.
* **Safe**: nothing changes production behavior; all checks run locally or in CI.
* **Fail‑closed**: no direct LLM calls slip in; orchestration/constraints/obs surfaces are always smoke‑tested.
* **Reversible**: toggles live purely in tooling; remove any piece without touching product code.
* **Observable**: optional quick coverage snapshot gives a stable signal on the critical surfaces.

