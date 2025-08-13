# Research Release Notes — v1.0.0
*Date:* 2025-08-13

## Highlights
- End-to-end research pipeline: opportunity → hypothesis → exploration → synthesis → safety checks.
- Alignment-first stress suite using **synthetic boundary cases**.
- Reproducible runs via response hashing and metadata capture.

## New
- `tests/test_alignment_stress.py` (bias, injection resistance, value-conflict, ambiguity).
- `RESEARCH_MANIFEST.yaml` (artifact inventory & compliance references).
- Executive & README revised with humble, research-grade tone.

## Changes
- Removed promotional language; replaced with neutral terms (e.g., innovation candidates, impact indicators).
- Emphasized behavioral probing over content generation in boundary scenarios.
- Renamed `BreakthroughDetector` to `ImpactIndicator` in documentation for clearer terminology.

## Known Limitations
- Synthetic proxies; real-world transfer requires sandbox pilots and oversight.
- Compliance references are informational only (not legal advice).
- Research prototype status - not production-ready.

## Next
- Model cards & data statements per component.
- Expanded red-team suites and telemetry dashboards.
- Hardening of refusal/deferral policies.

---
*This package is intended for research evaluation purposes only.*