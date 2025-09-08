---
title: Features Consolidation Complete
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "api", "security", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "memory", "bio"]
  audience: ["dev"]
---

# Features Directory Consolidation - Complete

## Summary
Successfully consolidated the features/ directory, distributing 15 subdirectories to their appropriate locations throughout the codebase.

## Changes Made

### Directory Count
- **Before**: 53 root directories
- **After**: 41 root directories
- **Reduction**: 12 directories (23% reduction)

### Consolidation Map Executed

1. **features/api/** → Removed (using FastAPI exclusively)
2. **features/config/** → `config/`
3. **features/core/** → `core/base/`
4. **features/creative_engine/** → `creativity/engines/`
5. **features/crista_optimizer/** → `bio/optimization/`
6. **features/data_manager/** → `core/data/`
7. **features/decision/** → `reasoning/decision/`
8. **features/diagnostic_engine/** → `trace/diagnostics/`
9. **features/docututor/** → `tools/documentation/`
10. **features/drift/** → `trace/drift/`
11. **features/entropy/** → `trace/entropy/`
12. **features/governance/** → `governance/features/`
13. **features/integration/** → Distributed to:
    - bio_awareness → `bio/awareness/`
    - governance → `governance/integration/`
    - meta_cognitive → `consciousness/meta_cognitive/`
    - safety → `security/safety/`
    - Others → `core/integration/`
14. **features/memory/** → `memory/`
15. **features/symbolic/** → `symbolic/features/`
16. **features/errors.py** → `core/`

### Import Updates
Updated the following imports:
- `from features.memory.memory_fold` → `from memory.memory_fold`
- `from features.integration.connectivity_engine` → `from core.integration.connectivity_engine`
- `from features.symbolic.glyphs` → `from symbolic.features.glyphs`

### Notes
- All Flask APIs removed in favor of FastAPI
- Memory files moved directly to memory/ (not memory/advanced/) as requested
- Features directory completely removed
- All active imports updated successfully

## Result
The codebase is now more organized with clearer module boundaries and better alignment with commercial API structure.
