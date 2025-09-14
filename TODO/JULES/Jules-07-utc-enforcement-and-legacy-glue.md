# Jules-07 — UTC enforcement & legacy glue (batch)

Priority: HIGH

Files:
- candidate/bio/oscillator.py
- candidate/bio/qi.py
- candidate/bio/awareness.py
- candidate/core/symbolic_legacy/colony_tag_propagation.py
- candidate/core/bootstrap.py
- candidate/core/constellation_alignment_system.py
- candidate/core/integrator.py
- candidate/core/colonies/temporal_colony.py
- candidate/core/quantum_financial/quantum_financial_consciousness_engine.py

Goal
- Implement UTC helper and use it across specified files, add dynamic import fallbacks in legacy glue, guard optional deps, and provide small improvements to temporal colony and quantum financial stubs.

Steps (high-level)
1. Add `utc_now()` helper in `candidate/utils/time.py` or similar, returning tz-aware UTC datetimes.
2. Replace `datetime.now()` calls in listed bio files with `utc_now()` and ensure tz-aware math.
3. In `colony_tag_propagation.py`, add dynamic import fallback (try/except import) and a minimal `Tag` class with basic fields.
4. In bootstrap/constellation_alignment_system.py, add try/except guards for optional imports like streamlit and annotate with `# nosec` or `# noqa` if necessary, with a short comment explaining retention.
5. In `integrator.py`, add a shim/try-except fallback for CORE imports and a small integration test `python -m candidate.core.integrator` that returns gracefully.
6. Add `replace` and `append_many` methods to `temporal_colony.py` and tests that validate state mutations.
7. Replace randoms in quantum financial engine with seeded deterministic placeholders and dataclass-based responses.

Acceptance
- utc_now() used across files and tests compare tz-aware datetimes.
- Dynamic import fallbacks prevent import errors and Tag class exists.
- `python -m candidate.core.integrator` runs without ImportError.
- Temporal colony operations tested.
- Quantum financial functions return typed dataclasses and deterministic outputs.

Notes
- This is a larger batch of small fixes; split into smaller PRs if needed.
