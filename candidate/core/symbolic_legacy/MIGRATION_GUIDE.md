---
status: wip
type: documentation
---
# 🔄 Symbolic System Migration Guide

**Date: 2025-07-27**

## Overview

The LUKHAS Symbolic System has been consolidated from various locations across the codebase into a centralized `lukhas/symbolic/` directory. This improves organization, reduces duplication, and makes the symbolic system easier to maintain and extend.

## Import Changes

### Old Import Paths → New Import Paths

```python
# Symbolic Utilities
OLD: from lukhas.core.utils.symbolic_utils import tier_label
NEW: from lukhas.symbolic.utils import tier_label

# Bio-Symbolic
OLD: from lukhas.bio.symbolic.bio_symbolic import BioSymbolic
NEW: from lukhas.symbolic.bio.bio_symbolic import BioSymbolic

# Neural-Symbolic
OLD: from lukhas.core.integration.neural_symbolic_bridge import NeuralSymbolicBridge
NEW: from lukhas.symbolic.neural.neural_symbolic_bridge import NeuralSymbolicBridge

# Drift Tracking
OLD: from lukhas.core.symbolic.drift.symbolic_drift_tracker import DriftTracker
NEW: from lukhas.symbolic.drift.symbolic_drift_tracker import DriftTracker

# Trace Logging
OLD: from lukhas.trace.symbolic_trace_logger import SymbolicTraceLogger
NEW: from lukhas.symbolic.trace.symbolic_trace_logger import SymbolicTraceLogger
```

## Files Affected

The following files need their imports updated:
- `lukhas/creativity/dream/visualization/dream_log_viewer.py`
- `lukhas/creativity/dream_systems/dream_log_viewer.py`
- `lukhas/identity/backend/dream_engine/dream_log_viewer.py`
- `lukhas/core/interfaces/lukhas_as_agent/sys/nias/dream_log_viewer.py`
- `lukhas/core/interfaces/lukhas_as_agent/sys/nias/lukhas_voice_narrator.py`
- `lukhas/core/interfaces/lukhas_as_agent/streamlit/components/replay_graphs.py`
- `lukhas/core/interfaces/logic/context/context_builder.py`
- `lukhas/core/interfaces/ui/components/replay_graphs.py`
- `lukhas/voice/lukhas_voice_narrator.py`

## Quick Fix Script

To update all imports automatically:

```bash
# Update symbolic_utils imports
find lukhas/ -name "*.py" -type f -exec sed -i 's/from lukhas.core.utils.symbolic_utils/from lukhas.symbolic.utils/g' {} +
find lukhas/ -name "*.py" -type f -exec sed -i 's/import lukhas.core.utils.symbolic_utils/import lukhas.symbolic.utils.symbolic_utils/g' {} +

# Update bio symbolic imports
find lukhas/ -name "*.py" -type f -exec sed -i 's/from lukhas.bio.symbolic\./from lukhas.symbolic.bio./g' {} +

# Update neural symbolic imports
find lukhas/ -name "*.py" -type f -exec sed -i 's/from lukhas.core.integration.neural_symbolic/from lukhas.symbolic.neural.neural_symbolic/g' {} +
```

## Backwards Compatibility

For a transition period, you can add compatibility imports in your modules:

```python
# Temporary compatibility layer
try:
    from lukhas.symbolic.utils import tier_label
except ImportError:
    from lukhas.core.utils.symbolic_utils import tier_label
```

## Benefits of Consolidation

1. **Single Source of Truth** - All symbolic utilities in one location
2. **Better Organization** - Clear subdirectory structure by function
3. **Easier Discovery** - Developers can find all symbolic tools in one place
4. **Reduced Duplication** - No more scattered symbolic utilities
5. **Enhanced Integration** - Easier to build new symbolic features

## New Features Available

With consolidation, new integrated features are available:
- Unified symbolic vocabulary system
- Integrated drift tracking across all symbolic types
- Bio-quantum symbolic representations
- Neural-symbolic fusion capabilities

## Support

For questions about the migration:
1. Check the main README at `lukhas/symbolic/README.md`
2. Review the consolidated code structure
3. Contact the LUKHAS AI team

---

*"Unity in symbols, clarity in purpose"* - LUKHAS Symbolic System
