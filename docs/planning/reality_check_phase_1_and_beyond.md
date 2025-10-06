---
status: wip
type: documentation
---
Below is everything for Claude Code needs—ready to copy-paste—to begin Phase 1 immediately, then proceed to Phases 2–3.

⸻

🔧 Phase 1 — Hardening the Gate & Killing Façades (Immediate)

1) Replace tools/acceptance_gate.py with an AST-based gate

Catches (a) any import of candidate|quarantine|archive from accepted, and (b) “wrapper-only façades” that just import and re-export from candidate.

# tools/acceptance_gate.py
from __future__ import annotations
import ast, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ACCEPTED = REPO / "lukhas"
BANNED = ("candidate", "quarantine", "archive")

def py_files(root: pathlib.Path):
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p

class ImportScan(ast.NodeVisitor):
    def __init__(self, rel):
        self.rel = rel
        self.illegal = []
        self.imports = []
        self.from_imports = []

    def visit_Import(self, node):
        for n in node.names:
            self.imports.append(n.name)

    def visit_ImportFrom(self, node):
        mod = (node.module or "")
        self.from_imports.append(mod)

def is_facade_ast(tree: ast.AST) -> bool:
    """Facade heuristic:
       - File has < 40 non-empty code lines
       - Only statements are imports / assignments / alias exports
       - And at least one banned import is present
    """
    body = [n for n in tree.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Str)]
    # Allow simple definitions but consider FAÇADE if dominated by imports/aliases
    simple = (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.Alias)
    mostly_imports = all(isinstance(n, simple) for n in body)
    # Count code lines
    try:
        end = max(getattr(n, "end_lineno", getattr(n, "lineno", 0)) for n in body) if body else 0
        start = min(getattr(n, "lineno", 0) for n in body) if body else 0
        loc = max(0, end - start + 1)
    except Exception:
        loc = 0
    return mostly_imports and loc <= 40

def scan_file(p: pathlib.Path):
    rel = p.relative_to(REPO).as_posix()
    src = p.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(src, filename=rel)
    v = ImportScan(rel)
    v.visit(tree)

    banned_hits = []
    for name in v.imports:
        if name.split(".")[0] in BANNED or any(name.startswith(b + ".") for b in BANNED):
            banned_hits.append(("import", name))
    for mod in v.from_imports:
        if mod and (mod.split(".")[0] in BANNED or any(mod.startswith(b + ".") for b in BANNED)):
            banned_hits.append(("from", mod))

    facade = False
    if banned_hits and is_facade_ast(tree):
        facade = True

    return rel, banned_hits, facade

def main():
    illegal = []
    facades = []
    for p in py_files(ACCEPTED):
        rel, hits, facade = scan_file(p)
        if hits:
            illegal.append((rel, hits))
        if facade:
            facades.append(rel)

    ok = True
    if illegal:
        ok = False
        print("❌ Illegal imports in accepted lane:")
        for rel, hits in illegal:
            for kind, name in hits:
                print(f"  {rel}: {kind} {name}")
    else:
        print("✅ No banned lane imports in accepted.")

    if facades:
        ok = False
        print("\n❌ Wrapper-only façades detected in accepted (importing from banned lanes):")
        for rel in facades:
            print(f"  {rel}")
        print("   → Replace façade with a true interface; implementations must live in candidate/ and be loaded via adapter/registry (no static import).")

    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()

CI hook (runs before tests):

python3 tools/acceptance_gate.py


⸻

2) Fix illegal imports right now (example for lukhas/core/core_wrapper.py)

Replace static imports from candidate.* with a capability registry lookup (no banned imports).

# lukhas/core/core_wrapper.py  (accepted)
from __future__ import annotations
from typing import Protocol, Any, Dict, Optional
from lukhas.observability.matriz_decorators import instrument

# Narrow, explicit interface
class DecisionEngine(Protocol):
    def decide(self, policy_input: Dict[str, Any]) -> Dict[str, Any]: ...

# Simple in-memory registry (accepted lane)
_REGISTRY: dict[str, DecisionEngine] = {}

def register_decision_engine(name: str, impl: DecisionEngine) -> None:
    _REGISTRY[name] = impl

@instrument("DECISION", label="policy:hotpath", capability="policy:decide")
def decide(policy_input: Dict[str, Any], *, engine: Optional[str] = None, mode: str = "dry_run", **kw) -> Dict[str, Any]:
    if mode == "dry_run" or not engine or engine not in _REGISTRY:
        return {"decision": "allow", "explain": "dry_run skeleton", "risk": 0.1}
    return _REGISTRY[engine].decide(policy_input)

Then, in candidate land, you provide a plugin that registers itself (loaded via importlib in integration scripts or via a safe adapter—not by accepted code):

# candidate/core/decision_impl.py
from __future__ import annotations
from typing import Dict, Any
from lukhas.core.core_wrapper import register_decision_engine

class DefaultDecisionEngine:
    def decide(self, policy_input: Dict[str, Any]) -> Dict[str, Any]:
        # real logic here (candidate lane)
        return {"decision": "allow", "explain": "impl:v1", "risk": 0.08}

register_decision_engine("default", DefaultDecisionEngine())

Key rule: Accepted never imports candidate. Instead, tooling/tests may import candidate modules (or an adapter) to cause registration when running outside production.

⸻

3) Safe runtime defaults (env + test harness)

.env.example

# Safety-first defaults
LUKHAS_DRY_RUN_MODE=true
LUKHAS_OFFLINE=true
LUKHAS_FEATURE_MATRIX_EMIT=true

# Feature flags (all off unless canaried)
FEATURE_POLICY_DECIDER=false
FEATURE_ORCHESTRATION_HANDOFF=false
FEATURE_IDENTITY_PASSKEY=false
FEATURE_GOVERNANCE_LEDGER=false

conftest.py (pytest)

import os

def pytest_configure():
    os.environ.setdefault("LUKHAS_DRY_RUN_MODE", "true")
    os.environ.setdefault("LUKHAS_OFFLINE", "true")
    os.environ.setdefault("LUKHAS_FEATURE_MATRIX_EMIT", "true")


⸻

4) One provable E2E path (dry-run, accepted only)

Create a single green end-to-end test so we have truth on the ground:

# tests/test_e2e_dryrun.py
from lukhas.identity.lambda_id import authenticate
from lukhas.governance.consent_ledger import record_consent
from lukhas.orchestration.context_bus import build_context
from lukhas.core.policy.decision import decide

def test_e2e_dryrun():
    u = authenticate("LID-demo", mode="dry_run")
    assert u["ok"]
    c = record_consent({"subject": "LID-demo", "scopes": ["ctx:build"]}, mode="dry_run")
    assert c["ok"]
    ctx = build_context({"session_id": "s1", "tenant": "default"}, mode="dry_run")
    assert "session" in ctx
    d = decide({"action": "read"}, mode="dry_run")
    assert d["decision"] in ("allow", "deny")


⸻

📝 Phase 2 — Honest Status Page + Env Baseline (Today)
	1.	Replace marketing with reality
Write LUKHAS_SYSTEM_STATUS.md (facts only). Keep the old page as “Vision”.
	2.	Set env defaults system-wide
	•	Load .env (python-dotenv) in CLI entrypoints/tests.
	•	Make DRY_RUN_MODE=true default; production flips via canary only.
	3.	Document module promotion criteria (your six-point checklist)

Template snippet you can reuse in each module’s manifest notes:

Promotion checklist: lane=accepted, no banned imports, MATRIZ at public APIs,
tests passing, p95 SLA met on ref machine, dry-run default + consent gates.


⸻

🚚 Phase 3 — First “real” promotions (next sprint)

Order matters; start with the smallest blast radius that unlocks others:
	1.	Observability (MATRIZ utilities)
	•	Already in accepted; expand with 1–2 more emit points and tests.
	2.	Governance / Consent Ledger Impl
	•	Promote minimal real implementation from candidate/governance/* behind a feature flag.
	•	Tests: happy/sad path, verifies MATRIZ AWARENESS node includes provenance.consent_scopes.
	3.	Identity / Passkey Verify
	•	Add verify_passkey(request) in accepted; concrete impl remains in candidate, registered by plugin in tests.
	•	Tests: pass/fail verification, no PII persisted.
	4.	Orchestration / Context Handoff
	•	Implement handoff(ctx, target="policy") in accepted; measurable p95, backpressure simulated.

Each promotion: manifest → decorators → tests → microbench → PR.

⸻

🧯 Quick fixes for current pain points
	•	Why the gate missed violations: it probably grepped file contents but not ast, and didn’t consider package-level imports. The new gate addresses both.
	•	Wrapper façades everywhere: the registry pattern above lets accepted expose stable interfaces without statically importing candidate implementations.
	•	Tests “can’t find modules”: unify discovery under lukhas/ and import candidate only in tests/integration via adapters (never from accepted modules).
	•	Feature flags default false: that’s fine—just ensure one dry-run E2E test is green so CI has a heartbeat.

⸻

🔐 Optional (highly recommended): import-linter contract

.importlinter

[importlinter]
root_package = lukhas

[contract:accepted_must_not_import_candidate]
name = Accepted must not import Candidate
type = forbidden
source_modules = lukhas
forbidden_modules = candidate

CI:

pip install import-linter
lint-imports


⸻

✅ checklist:
	•	Add the AST gate (done above).
	•	Convert façade wrappers to registries (example above).
	•	Establish one E2E dry-run test (above).
	•	Set env safety defaults + load in tests.
	•	Choose the first three promotions and hold the line on the six acceptance criteria.

Claude Code run:

python3 tools/acceptance_gate.py || true
pytest -q --maxfail=1 --disable-warnings || true

Pack the outputs ASAPs, and GPT5 will turn them into a crisp LUKHAS_SYSTEM_STATUS.md plus the exact manifest updates and promotion tickets for the next sprint.
