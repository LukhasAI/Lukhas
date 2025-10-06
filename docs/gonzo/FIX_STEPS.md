---
status: wip
type: documentation
---


.venv/bin/ruff rule E402

High–impact fixes (top to bottom)

E402 — import not at top of file

Why: Imports below code can change runtime behavior and break tooling.
Safe fix: Move imports to the top unless a late import is intentional (heavy/optional deps). If intentional, document and suppress.

# ✅ Preferred
import os
def main(): ...

# ✅ Intentional late import (documented)
if TYPE_CHECKING:  # noqa: E402 - type-only
    import numpy as np

Auto-fix: Partial (Ruff won’t reorder for you).
Command: audit only, then hand-fix risky ones:

.venv/bin/ruff check . --select=E402 --output-format=concise

When keeping late imports: add # noqa: E402 with a 1-line reason.

⸻

ARG002 / ARG001 — unused method/function argument

Why: Noise; hides real issues.
Safe fix: If required by interface, prefix underscore; else remove.

def process(_request, data):  # ✅ keep signature stable
    return handle(data)

Auto-fix: Not auto-removal (risk), but underscore rename is trivial to do manually or with a small codemod.

⸻

E501 — line too long

Why: Style/readability.
Safe fix patterns (no behavior change):

# ✅ Parentheses wrapping (preferred)
result = some_function(
    long_argument_name,
    another_argument,
)

# ✅ String join via parentheses
msg = (
    "This is a very long message that "
    "we split safely across lines."
)

Config option: set line-length = 100 (or 120) in .ruff.toml.
Auto-fix: Ruff won’t wrap for you; use your formatter for final polish.

⸻

F821 — undefined name

Why: Runtime error.
Safe fix: Add the correct import, define the symbol, or guard code.

from path.to.mod import thing  # ✅
# or
thing = get_default_thing()    # ✅ when design allows
# or
if 'thing' in globals(): ...   # ✅ guard, last resort

Never “invent” APIs just to quiet the error.

⸻

PERF203 — try/except in loop (perflint)

Why: Exception machinery inside hot loops is slow.
Safe fix: Hoist try/except outside the loop if logic allows.

# ❌
for item in items:
    try:
        work(item)
    except ValueError:
        handle()

# ✅
try:
    for item in items:
        work(item)
except ValueError:
    handle()

If you need to handle per-item failures, collect failures then handle after, or keep as-is if semantics demand it (document why).

⸻

UP006 — non-PEP585 type hints

Why: Use built-ins for generics on 3.9+.
Safe fix: Dict[str, int] -> dict[str, int], List[T] -> list[T], etc.
Auto-fix: ✅ Yes.

.venv/bin/ruff check . --select=UP006 --fix

Helpful: add from __future__ import annotations at module top to ease forward refs.

⸻

W293 / W292 — whitespace on blank line / no newline at EOF

Why: Style-only but easy wins.
Auto-fix: ✅ Yes.

.venv/bin/ruff check . --select=W293,W292 --fix


⸻

Q000 — bad quotes

Why: Enforce consistent quotes.
Auto-fix: ✅ Yes (will convert to your configured style).

.venv/bin/ruff check . --select=Q000 --fix

Set in .ruff.toml:

[lint.flake8-quotes]
inline-quotes = "double"  # or "single"


⸻

PERF401 — avoid unnecessary list() calls (perflint)

Typical cases & fixes:
	•	Building a list from comprehension: list([f(x) for x in it]) → [f(x) for x in it]
	•	Building a list then iterating once: for x in list(it): → for x in it:
	•	Using list(map(...)) for data: prefer a list comp: [f(x) for x in it]
Auto-fix: Often manual (confirm intent).

⸻

SIM102 — simplify boolean return (flake8-simplify)

Why: Reduce branching.
Fix: Replace if/else that only returns booleans with a direct expression.

# ❌
if cond:
    return True
else:
    return False

# ✅
return bool(cond)
# or simply: return cond

Auto-fix: Sometimes ✅ with --fix:

.venv/bin/ruff check . --select=SIM102 --fix


⸻

RUF006 — (Ruff internal rule)

This one varies by context; don’t guess. Check it locally:

.venv/bin/ruff rule RUF006

Ruff will print the exact message + examples so you can apply the right pattern. If you paste one instance here, I’ll give you the concrete fix template.

⸻

B904 — raise from within except (flake8-bugbear)

Why: Preserve exception context for debugging.
Fix:

try:
    do()
except ValueError as exc:
    raise CustomError("bad") from exc  # ✅

Auto-fix: Usually manual.

⸻

I001 — unsorted imports

Why: Deterministic imports ordering.
Auto-fix: ✅ Yes (Ruff’s isort).

.venv/bin/ruff check . --select=I001 --fix

Configure sections in .ruff.toml if you have custom local package names:

[lint.isort]
known-first-party = ["lukhas", "candidate", "core"]


⸻

Fast, low-risk command set

Run these in phases (stop if anything regresses):

# 1) Mechanical autofixes (safe)
.venv/bin/ruff check . --select=UP006,Q000,W293,W292,I001,SIM102 --fix

# 2) PERF buckets (review diffs!)
.venv/bin/ruff check . --select=PERF203,PERF401 --output-format=concise

# 3) Address F821 surgically (imports/defs/guards)
.venv/bin/ruff check . --select=F821 --output-format=concise

# 4) E402 audit (move or document with noqa + reason)
.venv/bin/ruff check . --select=E402 --output-format=concise

# 5) Line-length is last (wrap or adjust config)

Smart config to reduce churn (.ruff.toml)

line-length = 100
target-version = "py310"

[lint]
select = ["E","F","W","B","I","UP","Q","SIM","PERF","DTZ","RUF"]
ignore = [
  # Keep these late imports where they’re intentional; suppress file-by-file instead of global, if possible.
  # "E402",
]

[lint.isort]
known-first-party = ["lukhas", "candidate", "core"]
combine-as-imports = true

[lint.flake8-quotes]
inline-quotes = "double"  # or "single"

[format]
quote-style = "double"  # or "single"

Triage order for your repo
	1.	Autofixables: UP006, Q000, W293, W292, I001, SIM102 → quick wins.
	2.	F821: fix imports/defs precisely (no invention).
	3.	E402: move imports unless documented otherwise.
	4.	PERF203/401: hoist try/except; replace list(map(...)) with list comps—case by case.
	5.	E501: wrap/format last, or bump line-length modestly.
