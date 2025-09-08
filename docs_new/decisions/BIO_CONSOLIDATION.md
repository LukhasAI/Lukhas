---
title: Bio Consolidation
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["architecture", "testing", "adr"]
facets:
  layer: ["orchestration"]
  domain: ["symbolic", "quantum", "bio"]
  audience: ["dev"]
---

# Bio Module Consolidation Report
Generated: 2025-08-12T19:38:03.087780

## Summary
- Files Merged: 7
- Files Archived: 77
- Conflicts Found: 5

## Merged Modules
- `lukhas/accepted/bio/__init__.py`
- `lukhas/accepted/bio/oscillator.py`
- `lukhas/accepted/bio/symbolic.py`
- `lukhas/accepted/bio/quantum.py`
- `lukhas/accepted/bio/voice.py`
- `lukhas/accepted/bio/awareness.py`
- `lukhas/accepted/bio/adapters.py`

## Conflicts Requiring Resolution
- class: `OscillationType` in 1 files
- class: `CristaOptimizer` in 1 files
- function: `get_bio_symbol` in 1 files
- function: `get_bio_message` in 1 files
- function: `format_bio_log` in 1 files

## Next Steps
1. Run canary tests: `pytest tests/canary/test_bio_consolidation.py`
2. Review conflicts and implement actual logic
3. Update imports in dependent modules
4. Remove archived files after validation
