---
status: wip
type: documentation
---
Authoritative promotion process you can hand to lock in quality control and align with the MATRIZ/T4 rules we have been building.

⸻

📜 Lane Promotion Process (candidate → lukhas)

0. Principles
	•	candidate/ = development lane (unverified, experimental, or incomplete).
	•	lukhas/ = production lane (audited, stable, directly usable by MATRIZ and downstream systems).
	•	Promotion = controlled, test-gated migration of modules.
	•	Never bypass the lane process. Copy-pasting breaks the integrity of audits, tests, and dependency tracking.

⸻

1. Selection
	•	Identify a critical module or directory (e.g., candidate/core/orchestration) that is:
	•	Frequently imported in candidate code,
	•	Functionally working,
	•	Blocking other promotions (dependency root).

⸻

2. Preparation
	•	Dependencies: Map imports inside the candidate module.
	•	Replace from core.something with from lukhas.core.something only if the dependency is already promoted.
	•	If it depends on another candidate-only module, stub or defer until that module is promoted.
	•	Documentation: Update ops/matriz.yaml to include the lane and directories under promotion.

⸻

3. Smoke Test First
	•	Before promotion, create a smoke test for the module in tests/smoke/:

def test_import_orchestration():
    import candidate.core.orchestration as orch
    assert hasattr(orch, "__file__")


	•	Run the smoke suite (pytest -q tests/smoke) and confirm it imports cleanly in candidate.

⸻

4. Promotion
	•	Copy the directory from candidate/core/<module> → lukhas/core/<module>.
	•	Do not delete candidate/ yet (safety net).
	•	Fix imports inside the promoted code to point to lukhas.core.*.
	•	Add a shim in lukhas/core/ if needed for modules that still depend on the candidate path:

# lukhas/core/orchestration.py (shim during transition)
from candidate.core.orchestration import *  # noqa



⸻

5. Post-Promotion Validation
	•	Update the smoke test to import from lukhas.core.orchestration instead of candidate.
	•	Run:

pytest -q tests/smoke


	•	If it fails, roll back or patch with minimal fixes (no rewrites).

⸻

6. Dependency Chain Handling
	•	Promote in order of dependency importance (orchestration → glyph → integration → api → neural → interfaces → monitoring → symbolic).
	•	Each time:
	1.	Verify candidate smoke test.
	2.	Promote to lukhas/.
	3.	Update imports.
	4.	Validate via smoke tests.
	5.	Commit with message:

chore(promotion): promote core/<module> from candidate → lukhas



⸻

7. Review & Lock
	•	Commit and PR for each promotion step.
	•	PR is tagged lane-promotion.
	•	Reviewer (you) confirms:
	•	Imports updated.
	•	Smoke tests pass.
	•	No candidate-only dependencies left dangling.

⸻

✅ What Claude and Github Copilot Must Do
	1.	Never bulk copy. Promote one module at a time.
	2.	Always run smoke tests before and after.
	3.	Use shims if other candidate modules still depend on the old path.
	4.	Respect ops/matriz.yaml as the source of truth.
	5.	Ask before deleting candidate code.

⸻
