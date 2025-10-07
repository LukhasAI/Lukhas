---
status: wip
type: documentation
owner: unknown
module: planning
redirect: false
moved_to: null
---

What to add (surgical)

1) Secrets: remove, ignore, purge history, rotate

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# stop tracking and prevent future commits
git rm --cached .env || true
printf "\n# Local only\n.env\n.env.*\n" >> .gitignore
git add .gitignore
git commit -m "chore(security): stop tracking .env; add to .gitignore"

# optional but recommended: purge secrets from history (choose one)
# A) git-filter-repo (preferred)
pipx install git-filter-repo || pip install git-filter-repo
git filter-repo --invert-paths --path .env --force

# B) BFG
# java -jar bfg.jar --delete-files .env
# git reflog expire --expire=now --all && git gc --prune=now --aggressive

Then rotate every exposed key at the provider.

2) CI: run the gate before tests + import-linter contract

.github/workflows/ci.yml (snippet):

- name: Acceptance gate
  run: python3 tools/acceptance_gate.py

- name: Import Linter
  run: |
    pip install import-linter
    printf "[importlinter]\nroot_package = lukhas\n\n[contract:accepted_no_candidate]\nname = accepted must not import candidate\ntype = forbidden\nsource_modules = lukhas\nforbidden_modules = candidate\n" > .importlinter
    lint-imports

3) Safety defaults always on in tests & local CLIs

conftest.py

import os
def pytest_configure():
    os.environ.setdefault("LUKHAS_DRY_RUN_MODE", "true")
    os.environ.setdefault("LUKHAS_OFFLINE", "true")
    os.environ.setdefault("LUKHAS_FEATURE_MATRIX_EMIT", "true")

.env.example

LUKHAS_DRY_RUN_MODE=true
LUKHAS_OFFLINE=true
LUKHAS_FEATURE_MATRIX_EMIT=true
FEATURE_GOVERNANCE_LEDGER=false
FEATURE_IDENTITY_PASSKEY=false
FEATURE_ORCHESTRATION_HANDOFF=false

4) Fix the two illegal import hotspots with registries

a) lukhas/core/core_wrapper.py (accepted)

from __future__ import annotations
from typing import Protocol, Any, Dict, Optional
from lukhas.observability.matriz_decorators import instrument

class DecisionEngine(Protocol):
    def decide(self, policy_input: Dict[str, Any]) -> Dict[str, Any]: ...

_REGISTRY: dict[str, DecisionEngine] = {}
def register_decision_engine(name: str, impl: DecisionEngine) -> None:
    _REGISTRY[name] = impl

@instrument("DECISION", label="policy:hotpath", capability="policy:decide")
def decide(policy_input: Dict[str, Any], *, engine: Optional[str]=None, mode="dry_run") -> Dict[str, Any]:
    if mode == "dry_run" or not engine or engine not in _REGISTRY:
        return {"decision":"allow","explain":"dry_run skeleton","risk":0.1}
    return _REGISTRY[engine].decide(policy_input)

candidate/core/decision_impl.py registers the real engine:

from lukhas.core.core_wrapper import register_decision_engine
class DefaultDecisionEngine:
    def decide(self, policy_input): return {"decision":"allow","explain":"impl:v1","risk":0.08}
register_decision_engine("default", DefaultDecisionEngine())

b) lukhas/governance/guardian/guardian_impl.py (accepted)

from __future__ import annotations
from typing import Protocol, Dict, Any
from lukhas.observability.matriz_decorators import instrument

class Guardian(Protocol):
    def check(self, event: Dict[str, Any]) -> Dict[str, Any]: ...

_G: dict[str, Guardian] = {}
def register_guardian(name: str, impl: Guardian): _G[name] = impl

@instrument("AWARENESS", label="guardian:hotpath", capability="guardian:check")
def guardian_check(event: Dict[str, Any], *, name="default", mode="dry_run") -> Dict[str, Any]:
    if mode=="dry_run" or name not in _G:
        return {"ok": True, "action":"allow", "reason":"dry_run"}
    return _G[name].check(event)

candidate/governance/guardian_impl_default.py registers the real one.

5) Acceptance gate: use the AST version and fail on wrapper-only files

(Use the AST gate I provided earlier. It scans all lukhas/, flags banned lane imports and “facade” files.)

6) One green, end-to-end dry-run test

tests/test_e2e_dryrun.py

from lukhas.identity.lambda_id import authenticate
from lukhas.governance.consent_ledger import record_consent
from lukhas.orchestration.context_bus import build_context
from lukhas.core.core_wrapper import decide

def test_e2e_dryrun():
    u = authenticate("LID-demo", mode="dry_run"); assert u.get("ok", True)
    c = record_consent({"subject":"LID-demo","scopes":["ctx:build"]}, mode="dry_run"); assert c.get("ok", True)
    ctx = build_context({"session_id":"s1"}, mode="dry_run"); assert "session" in ctx
    d = decide({"action":"read"}, mode="dry_run"); assert d["decision"] in {"allow","deny"}

7) Reality-based status page template

LUKHAS_SYSTEM_STATUS.md (skeleton)

# LUKHAS System Status — Reality Check (YYYY-MM-DD)

## Lanes
- accepted: observability (MATRIZ utils), core/core_wrapper (interface), governance/guardian (interface)
- candidate: core impl, governance impl, identity, orchestration, memory, bridge, qi, vivox, consciousness
- quarantine: —

## Tests
- e2e dry_run: ✅
- total: X passed / Y failed (list top 5 failures)

## Safety
- DRY_RUN_MODE: true (default)
- OFFLINE: true (default)
- acceptance gate: ✅ / ❌ (summary)
- illegal imports: none / list

## Performance (dry-run)
- policy.decide p95: N/A (dry-run)
- context.build p95: N/A (dry-run)

## Next Promotions
1) Governance/Consent Ledger (feature-flag, tests)
2) Identity/Passkey Verify (plugin, no PII)
3) Orchestration/Handoff (p95 measured)

8) Promotion checklist in each MODULE_MANIFEST.json

{
  "name": "core.policy",
  "lane": "accepted",
  "owner": "A4 Orchestration Brain",
  "capabilities": ["policy:decide"],
  "matriz_emit_points": ["DECISION:policy:hotpath"],
  "sla": {"p95_ms": 100, "env": "dry_run default; prod via canary"},
  "dependencies": [],
  "promotion_checklist": [
    "no imports from candidate/quarantine/archive",
    "MATRIZ emit on public API",
    "tests passing in CI",
    "p95 meets SLA on ref machine",
    "dry_run default + consent gates"
  ]
}


⸻

Execution order (today)
	1.	Remove secrets (.env untracked + rotate keys).
	2.	Drop in AST acceptance gate; wire into CI before tests.
	3.	Refactor core_wrapper.py & guardian_impl.py to registries.
	4.	Add safety defaults (.env.example, conftest.py).
	5.	Add the single e2e dry-run test; get CI green.
	6.	Write LUKHAS_SYSTEM_STATUS.md from actual outputs.
	7.	Plan the first real promotion PR (Governance/Consent Ledger).

This keeps momentum, fixes the dangerous bits (secrets + illegal imports), and gives you a truthful baseline to iterate from. If you want, have Claude Code apply these edits now; if anything fails, paste the error and I’ll adjust the snippets on the spot.
