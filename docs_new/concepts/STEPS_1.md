---
title: Steps 1
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["testing", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "identity", "bio"]
  audience: ["dev"]
---

yes—let’s knock out the blockers fast. Below are surgical fixes for every failing category you posted, plus a tight Codex runbook to apply them now. I’m keeping changes minimal and low-risk.

⸻

What to fix (and how)

A) Ruff (stable lanes: lukhas/**)
	1.	RUF022 — all not sorted
File: lukhas/bio/__init__.py (line ~24)
Fix: sort the list lexicographically.

# before (example)
__all__ = ["BioCore", "bio_utils", "Symbol", "Analyzer"]

# after
__all__ = [
    "Analyzer",
    "BioCore",
    "Symbol",
    "bio_utils",
]

	2.	ANN204 — missing return type for __init__
File: lukhas/bio/core/bio_symbolic.py (line ~64)
Fix: add explicit -> None to every __init__.

class BioSymbolic:
    def __init__(self, *args: object, **kwargs: object) -> None:
        ...

	3.	DTZ005 — datetime.now() without tz
File: lukhas/bio/core/bio_symbolic.py (line ~270)
Fix: use UTC (or your project’s tz policy).

from datetime import datetime, timezone  # at top

ts = datetime.now(timezone.utc)

	4.	PLC0415 — non top-level import
File: lukhas/branding_bridge.py (line ~122)
Fix: move import(s) to the top of file; if conditional import is required, guard the usage instead of import location.

# move this to the top:
import something  # example

# if it was conditional, prefer:
try:
    import something
except ImportError:
    something = None  # and guard where used

	5.	E501 — long lines (126, 375)
File: lukhas/branding_bridge.py
Fix: wrap with parentheses; avoid backslashes.

result = some_function_call(
    arg1,
    arg2,
    "very long string that used to exceed the line length limit...",
)

	6.	ANN201 — missing return type for public function
File: lukhas/bridge/__init__.py (line ~38)
Fix: add an explicit return type (-> None if it doesn’t return, or concrete type).

def public_entry(...)-> None:
    ...


⸻

B) MyPy (type-safety)

T4 rule: fix runtime-risk first (None operations, incompatible assignments), then add minimal annotations to silence top errors.

	1.	Missing arg annotations
Files:

	•	lukhas/core/common/exceptions.py:36
	•	lukhas/identity/passkey/registry.py:6
	•	lukhas/governance/consent_ledger/registry.py:7
Fix (pattern): add minimal -> None / -> T and input types. If unsure, use Any and tighten later.

from typing import Any

def register_passkey(user_id: str, payload: dict[str, Any]) -> None:
    ...

def load_exceptions(source: str) -> dict[str, Any]:
    ...

	2.	None / float division
File: lukhas/core/common/exceptions.py:251
Fix: guard or default before dividing.

from typing import Optional

def compute_ratio(numerator: Optional[float], denom: float) -> float:
    if numerator is None:
        return 0.0  # or raise, per semantics
    return numerator / denom

Adjust names to match your function around line ~251; the key is to make the operand non-None before division and reflect that in the type hints.

	3.	Incompatible assignment (list[str] = None)
File: lukhas/governance/auth_governance_policies.py:66
Fix A (preferred): initialize to [] instead of None.
Fix B: or declare Optional[list[str]] and guard on use.

from typing import Optional

allowed_scopes: list[str] = []  # A) simplest
# OR
allowed_scopes: Optional[list[str]] = None  # B) then guard before use


⸻

`Claude Code`: apply fixes now (copy/paste in VS Code terminal)

These are localized edits—no refactors, only hygiene to get green gates.

1) Bio module: sort __all__, add __init__ return type, fix tz

# Sort __all__ (open file to edit)
code -g lukhas/bio/__init__.py:1

# BioSymbolic: add __init__ -> None and timezone-aware now()
code -g lukhas/bio/core/bio_symbolic.py:60
# add: from datetime import timezone (if not present)
# change: datetime.now() -> datetime.now(timezone.utc)
# ensure: def __init__(...)-> None

2) Branding bridge: move import & wrap long lines

code -g lukhas/branding_bridge.py:110
# Move any inner import(s) to top; replace long lines (126, 375) with a parenthesized multi-line call

3) Bridge init: add return annotation

code -g lukhas/bridge/__init__.py:30
# ensure public functions have explicit return types (-> None or concrete)

4) MyPy high-value fixes

# exceptions: add arg types and guard None division
code -g lukhas/core/common/exceptions.py:30
code -g lukhas/core/common/exceptions.py:245

# registries: add minimal annotations
code -g lukhas/identity/passkey/registry.py:1
code -g lukhas/governance/consent_ledger/registry.py:1

# governance policies: list[str] vs None
code -g lukhas/governance/auth_governance_policies.py:60

5) Re-run gates (stable lanes first)

ruff check --fix lukhas
ruff format lukhas
ruff check lukhas

mypy lukhas
pytest -q  # expect collection to proceed; errors will shrink

If pytest still errors on package imports, ensure these exist:

touch matriz/__init__.py matriz/core/__init__.py
pytest -q


⸻

Claude Code (config follow-ups after Codex runs)

Ask Claude Code to:
	1.	Adjust ruff.toml to relax ANN on non-stable lanes while keeping it for lukhas/**:

[lint.per-file-ignores]
"**/__init__.py" = ["F401","F403"]
"tests/**" = ["ANN","S101"]
"candidate/**" = ["ANN"]
"tools/**" = ["ANN"]
"enterprise/**" = ["ANN"]

	2.	Confirm DTZ policy (UTC vs local tz) and document in README “Time & TZ”.
	3.	Add minimal types-* stubs if MyPy complains (e.g., types-PyYAML) and include in dev deps.

⸻

Why this order (T4 lens)
	•	We fix runtime-risk (None ops, tz) and CI blockers first.
	•	We don’t widen diffs—only add hints/guards/annotations.
	•	We keep ANN strict in stable lanes, relax elsewhere to avoid churn; Claude codifies that in config.

⸻

Want me to proceed with a second pass?

If you confirm, I’ll give Codex a line-by-line patch pack (unified diff style) for those exact files so it can apply changes in one go and immediately re-run:

{ ruff_stable_ok, mypy_errors_count, pytest: {passed,failed,errors,skipped} }

Your call, but we can land this in under two passes.