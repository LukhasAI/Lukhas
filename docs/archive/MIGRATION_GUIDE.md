---
status: wip
type: documentation
owner: unknown
module: guides
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# LUKHAS AI Migration Guide
Generated: 2025-08-12T19:29:23.646267

## Import Mappings

Use these mappings to update your imports:

### Core Modules
- `bio_core` → `lukhas.accepted.bio` (deprecated: 2025-11-01)
- `bio_orchestrator` → `lukhas.accepted.bio.orchestrator` (deprecated: 2025-11-01)
- `bio_quantum_radar_integration` → `lukhas.candidate.bio.quantum` (deprecated: 2025-11-01)
- `bio_symbolic` → `lukhas.accepted.bio.symbolic` (deprecated: 2025-11-01)
- `core.glyph` → `lukhas.accepted.core.glyph` (deprecated: 2025-11-01)
- `governance.guardian` → `lukhas.accepted.governance.guardian` (deprecated: 2025-11-01)
- `identity.core` → `lukhas.accepted.identity` (deprecated: 2025-11-01)
- `memory.episodic` → `lukhas.accepted.memory.episodic` (deprecated: 2025-11-01)
- `memory.fold_manager` → `lukhas.accepted.memory.fold` (deprecated: 2025-11-01)
- `memory.memory_consolidation` → `lukhas.accepted.memory.consolidation` (deprecated: 2025-11-01)
- `qim` → `lukhas.candidate.qim` (deprecated: 2025-11-01)
- `universal_language` → `lukhas.candidate.ul` (deprecated: 2025-11-01)
- `vivox` → `lukhas.candidate.vivox` (deprecated: 2025-11-01)

### Candidate Modules (Feature-Flagged)
- `bio_quantum_radar_integration` → `lukhas.candidate.bio.quantum` (deprecated: 2025-11-01)
- `qim` → `lukhas.candidate.qim` (deprecated: 2025-11-01)
- `universal_language` → `lukhas.candidate.ul` (deprecated: 2025-11-01)
- `vivox` → `lukhas.candidate.vivox` (deprecated: 2025-11-01)

## Migration Steps

1. **Update imports** using the mappings above
2. **Run tests** to verify functionality
3. **Enable feature flags** for candidate modules as needed
4. **Remove old imports** after testing

## Compatibility Shims

All old imports will continue working until **2025-11-01** via compatibility shims.

Example shim usage:
```python
# Old import (will show deprecation warning)
from bio_core import BioEngine

# New import (recommended)
from lukhas.accepted.bio import BioEngine
```

## Feature Flags

For candidate modules, enable via environment variables:
- `UL_ENABLED=true` - Universal Language
- `VIVOX_LITE=true` - VIVOX consciousness system
- `QIM_SANDBOX=true` - Quantum-Inspired Module

## Need Help?

Check the following resources:
- `docs/ADR/ADR-0001-code-maturity-lanes.md` - Architecture decision
- `CODEOWNERS` - Module ownership
- `.github/PULL_REQUEST_TEMPLATE.md` - PR checklist
