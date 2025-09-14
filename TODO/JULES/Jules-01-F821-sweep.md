# Jules-01 — F821 undefined names sweep

Priority: CRITICAL

Files:
- candidate/core/framework_integration.py
- candidate/qi/qi_entanglement.py
- candidate/orchestration/openai_modulated_service.py
- candidate/governance/drift_dashboard_visual.py

Goal
- Remove F821 (undefined name) errors in the four files. Add missing imports, small stubs, or guard optional dependencies.

Steps
1. Run ruff (or flake8) to list F821 occurrences for each file:
   - ruff check --select F821 <file>
2. For each undefined name:
   - If the symbol should be imported, add the import.
   - If the symbol is an optional dependency, wrap import in try/except ImportError and add a feature flag or fallback stub.
   - If the symbol is an internal helper not yet implemented, add a minimal placeholder with a TODO and raise NotImplementedError where appropriate.
3. Run ruff/flake8 again and make sure no F821 remain in those files.
4. Run a small smoke script (or pytest -k relevant) to ensure no NameError at runtime.

Commands
```
r
ruff check --select F821 candidate/core/framework_integration.py
ruff check --select F821 candidate/qi/qi_entanglement.py
ruff check --select F821 candidate/orchestration/openai_modulated_service.py
ruff check --select F821 candidate/governance/drift_dashboard_visual.py
pytest -q tests/ -k "framework_integration or qi_entanglement or openai_modulated_service or drift_dashboard"
```

Acceptance
- ruff (or flake8) reports no F821 for the four files.
- A smoke test or relevant unit test runs without NameError exceptions.

Notes
- Keep changes minimal and use feature flags for optional integrations.
- Add inline comments linking to the TODO card in `TODO/CRITICAL/critical_todos.md` when applicable.
