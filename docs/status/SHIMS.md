---
status: wip
type: documentation
owner: unknown
module: status
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# LUKHAS AI Compatibility Shims
Generated: 2025-08-12T19:31:35.511732

## Active Shims (39)

These files provide backward compatibility during migration:

- `bio/bio_engine/__init__.py`
- `bio/bio_hub/__init__.py`
- `bio/bio_utilities/__init__.py`
- `bio_core/__init__.py`
- `bio_core/__init__.py`
- `bio_core/bio_symbolic/__init__.py`
- `bio_optimization_adapter/__init__.py`
- `bio_orchestrator/__init__.py`
- `bio_orchestrator/__init__.py`
- `bio_quantum_radar_integration/__init__.py`
- `bio_quantum_radar_integration/__init__.py`
- `bio_symbolic/__init__.py`
- `bio_symbolic/__init__.py`
- `bridge/adapter.py`
- `core/glyph.py`
- `core/glyph/__init__.py`
- `governance/guardian.py`
- `governance/guardian/__init__.py`
- `identity/core.py`
- `identity/core/__init__.py`
- `memory/causal.py`
- `memory/colonies.py`
- `memory/compression.py`
- `memory/dna_helix.py`
- `memory/episodic.py`
- `memory/episodic/__init__.py`
- `memory/fold_manager.py`
- `memory/fold_manager/__init__.py`
- `memory/fold_system.py`
- `memory/hippocampal.py`
- `memory/memory_consolidation.py`
- `memory/memory_consolidation/__init__.py`
- `orchestration/brain.py`
- `qim/__init__.py`
- `qim/__init__.py`
- `universal_language/__init__.py`
- `universal_language/__init__.py`
- `vivox/__init__.py`
- `vivox/__init__.py`

## Deprecation Schedule

All shims will be removed on **2025-11-01**

## Usage

Old imports will continue working but show deprecation warnings:

```python
# Old import (shows warning)
from bio_core import BioEngine

# New import (recommended)
from lukhas.accepted.bio import BioEngine
```

## Testing

Run tests with deprecation warnings visible:
```bash
python -W default::DeprecationWarning -m pytest
```
