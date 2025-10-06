---
status: wip
type: documentation
---
# LUKHAS FIXPLAN OPPORTUNITY

Phase 0 — Build the map before the fix

Goal: turn 10k+ warnings into a small set of intentional actions.

Agent: “Code Atlas” (call graph + intent miner)

Prompt (paste to Codex):

Role: Build a Code Atlas for the Lukhas repo.
Output a single JSON file reports/code_atlas.json with:
	•	functions/classes: file, line, signature, docstring summary
	•	incoming calls (callers) and outgoing calls (callees)
	•	references by name-only (strings, getattr) where static analysis is fuzzy
	•	flags: {“unused_param”, “unused_func”, “unused_class”, “mutable_default”, “dangling_task”, “datetime_naive”}
	•	intent clues: harvest from docstrings, comments, TODOs, README, design docs (paths containing /docs/, README, DESIGN)
	•	module roles: orchestrator, integration, adapter, domain model, test helper (heuristic)

Save per-rule indices:
	•	reports/idx_ARG002.json, reports/idx_ARG001.json, reports/idx_RUF006.json, reports/idx_B904.json, etc.
Acceptance: JSON validates, and every entry links back to a real file:line.

This “atlas” lets other agents decide whether to wire, keep, or delete.

⸻

Phase 1 — Convert top rules into product improvements (not just lint fixes)

Below: each rule → what to do when it hints something missing, plus exact agent prompts.

1) ARG002 / ARG001 (unused args) → Interface truthing

Heuristic:
	•	If function/method is an override / callback / protocol → keep param, rename to _param and document contract.
	•	If docstring or name implies planned use (e.g., timeout, ctx, trace_id) → instrument now (logging/telemetry/propagation), or thread it to callee.
	•	If no intent and no callers → deprecate or delete (open a ticket if uncertain).

Agent: “Interface Surgeon”

For every ARG002/ARG001 entry in reports/idx_ARG002.json and idx_ARG001.json:
	•	Decide: {“protocol_param”, “telemetry_param”, “plumbing_param”, “dead_param”}
	•	Actions:
	•	protocol_param: rename to _name, add docstring note “kept for interface compatibility”, add # noqa: ARG002.
	•	telemetry_param (e.g., ctx, trace_id, user_id): propagate to downstream calls if present, or attach to structured logging at entrypoint.
	•	plumbing_param (e.g., timeout, retries, session): thread to underlying I/O call where available; if absent, add TODO with clear signature of intended downstream.
	•	dead_param: remove and update callers; if public API, mark deprecated and schedule removal.
	•	Keep diffs minimal; generate reports/arg_fixes.md with a table of decisions.
Acceptance: compile succeeds; no new F821; unit tests (if any) still pass.

2) F821 (undefined name) → Missing imports vs Missing objects

Heuristic:
	•	If symbol exists elsewhere → add explicit import at top (avoid import *).
	•	If not found but docstring/reference suggests intended module → add a stub with NotImplementedError and TODO only if the feature is referenced by callers.
	•	If totally speculative → do not create; open a design TODO entry.

Agent: “Symbol Resolver”

For each F821:
	•	Search the repo for definition; if found, add explicit import with module qualifier.
	•	If missing but there are clear intent clues (docstrings, comments, file names): create a minimal stub in the appropriate module (raising NotImplementedError) and wire import.
	•	If no clues: add # TODO(gonzo): define or remove and skip.
Acceptance: F821 count drops; new stubs are < 50 lines and documented with a one-line rationale.

3) E402 (import not at top) → Initialization policy

Heuristic:
	•	Move imports up unless they intentionally gate optional heavy deps or environment binding.
	•	If intentional late import → leave in place with # noqa: E402 + “why”.

Agent: “Import Arbiter”

For each E402:
	•	If import has side effects or is optional/heavy (detected by module name hints or comments), keep it in place and annotate # noqa: E402 — intentional late import (reason).
	•	Else move to top. Preserve lazy import pattern for optional deps (def fn(): import x; ...) when needed.
Acceptance: E402 falls sharply, and any non-moved import has a one-line rationale.

4) RUF006 (asyncio dangling task) → Reliability hardening

This one is a product improvement: un-awaited tasks leak and cause nondeterminism.

Patterns to fix:
	•	Capture and await tasks in the right lifecycle.
	•	Or shield & track them; add graceful shutdown to cancel and gather.
	•	Replace fire-and-forget with background task manager (e.g., per module).

Agent: “Async Guardian”

For every RUF006:
	•	Replace fire-and-forget asyncio.create_task() with:
	•	stored handle in a registry; add shutdown() routine to await asyncio.gather(*tasks, return_exceptions=True).
	•	or await immediately when required by control flow.
	•	Add tests (or doctests) demonstrating clean shutdown without pending tasks.
Acceptance: no RUF006; adding pytest -k async shows no pending task warnings.

5) E501 (line too long) → Signal, not ceremony

Treat as formatting at the end unless lines block review. If long strings are user-visible messages, wrap with parentheses; for URLs/constants, allow exceeding or store in config.

Agent: “Formatter”

Apply non-semantic wraps; avoid backslashes; don’t alter f-string semantics. If a line is a URL or regex, consider # noqa: E501 with short rationale.

6) Q000 / I001 / UP006 / W292 / W293 → Mechanical entropy drop

These are safe autofixes; they reduce noise so your reviewers can focus on real changes.

Agent: “Autofix Bot”
Commands:

.venv/bin/ruff check . --select=UP006,Q000,I001,W292,W293,SIM102,F841,RUF013,UP015,RUF010 --fix

Acceptance: only mechanical edits; re-run compile.

7) PERF203 / PERF401 → Everyday performance
	•	PERF203 hoist try/except outside loops where semantics allow; if you must handle per-item, catch in a helper and count failures.
	•	PERF401 remove list() around comprehensions/iters unless the materialized list is used multiple times.

Agent: “Perf Surgeon”

Tackle candidate/core/** first; open a small perf note per change: why it’s safe.

8) B904 (raise without from) → Better debugging

Add from exc to preserve trace. This is developer experience, not just style.

Agent: “Error Contextor”

For each except X as exc: raise Y("msg"): make it raise Y("msg") from exc. If raising same exception type, raise alone is cleaner.

9) DTZ005/DTZ003 → Timezone correctness policy

Create core/timeutils.py:

from datetime import datetime, timezone
def now_utc() -> datetime: return datetime.now(tz=timezone.utc)
def utc_from_ts(ts: float) -> datetime: return datetime.fromtimestamp(ts, tz=timezone.utc)

Replace naive calls repo-wide. That’s a correctness upgrade.

Agent: “Timekeeper”

Introduce timeutils and migrate DTZ* callsites. Annotate callsites where local time is intended.

10) RUF012 (mutable class default) / B008 (call in default) → Bug preventers
	•	Replace list/dict/set defaults with field(default_factory=...) or None + init.
	•	Replace func() in default args with None + initialize in body.

Agent: “Default Detox”

Apply the two patterns consistently; add a unit test where mutation would previously leak across instances.

⸻

Phase 2 — Create what’s “missing” (only when intent is knowable)

This is where we upgrade the codebase rather than just hush the linter.

A) “Missing Wiring” detector (from ARG*/F821)
	•	If a parameter name appears in downstream callee signatures (e.g., timeout, session, trace_id) and is currently dropped → thread it through.
	•	If a parameter implies observability (ctx, request_id, user_id) and there’s logging infra → log or attach to spans/metrics.
	•	If a function is never called, but docstrings/readme describe it as a feature entrypoint → generate a minimal orchestrator callsite (behind a feature flag) and a test that exercises the path.

Agent: “Integrator”

Using reports/code_atlas.json:
	•	For each unused parameter with a name matching downstream callee params, add it to the call chain.
	•	For observability params, add structured log lines (logger.info("op", extra={...}) or your logging schema).
	•	For documented but unreferenced entrypoints, add a thin call in the relevant orchestrator module, gated by if settings.enable_<feature>:. Create a smoke test.
Safeguard: any new wiring must be behind a flag and covered by a tiny test.

B) “Missing Class” activation

If a class is unused but:
	•	Named *Manager, *Adapter, *Policy, *Strategy
	•	Has a docstring with responsibilities
Create a registration point (factory/registry) and resolve by name from orchestrator, again behind a flag. Add a test instantiating the strategy.

Agent: “Registry Builder”

Introduce a registry.py with register(name, cls) and resolve(name); auto-register classes with a ROLE attribute or decorator. Wire orchestrator to resolve when the feature flag is on.

⸻

Phase 3 — Tight loop & metrics

Make it measurable so agents don’t wander.
	•	Keep pre/post counts per bucket:
	•	.reports/ruff_SYNTAX_before.txt → after
	•	.reports/ARG_summary.md table: how many _param (protocol), how many threaded, how many removed
	•	.reports/async_guard.md listing previous RUF006 sites and their new lifecycle

Stop criteria per phase: counts don’t regress; tests pass; smoke import works.

⸻

“Do this now” — minimal commands to start
	1.	Mechanical pass:

git checkout -b chore/autofix
.venv/bin/ruff check . --select=UP006,Q000,I001,W292,W293,SIM102,F841,RUF013,UP015,RUF010 --fix
git commit -am "chore: mechanical autofixes (ruff)"

	2.	Generate the Code Atlas:

# Run the Code Atlas agent as prompted above
# Save outputs under reports/

	3.	Run three focused upgrades:

	•	Async Guardian for all RUF006 (reliability)
	•	Timekeeper for DTZ* (correctness)
	•	Interface Surgeon for ARG001/2 (API truthing)

These three produce immediate quality beyond lint.

⸻

Example transformations (concrete)

ARG002 → telemetry

# before
def save(model, request_id):  # request_id unused
    repo.put(model)

# after
def save(model, _request_id):
    repo.put(model)
    logger.info("save", extra={"model": model.id, "request_id": _request_id})

F821 → import vs stub

# before
def run():
    return normalize(x)  # F821

# after (import found)
from candidate.core.math import normalize
def run():
    return normalize(x)

# or after (no impl found but referenced in docs)
def normalize(*args, **kwargs):
    """TODO(gonzo): implement per 'Normalization step' in docs/architecture.md"""
    raise NotImplementedError("normalize is not yet implemented")

RUF006 → task lifecycle

# before
async def start():
    asyncio.create_task(worker())  # RUF006

# after
TASKS: set[asyncio.Task] = set()
async def start():
    t = asyncio.create_task(worker())
    TASKS.add(t)
    t.add_done_callback(TASKS.discard)

async def shutdown():
    if TASKS:
        await asyncio.gather(*TASKS, return_exceptions=True)

DTZ005/003 → timeutils

# before
from datetime import datetime
now = datetime.now()          # DTZ005
utc = datetime.utcnow()       # DTZ003

# after
from core.timeutils import now_utc
now = now_utc()
utc = now  # unified


⸻

Guardrails (T4 skepticism)
	•	Do not “create what’s missing” unless intent is grounded in text you wrote (docstrings/comments/README/tests) or clear naming convergence between caller/callee. Otherwise it’s invention—costly later.
	•	Feature flags for new wiring so nothing surprising hits runtime.
	•	Comment every intentional exception (noqa) with a one-liner reason. Future you will thank present you.
	•	Small, themed commits so rollbacks are easy.

⸻

