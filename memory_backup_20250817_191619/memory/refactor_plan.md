# Memory System Refactoring Plan

## 📂 Target Structure

```
memory/
├── fold_engine.py        # Memory folding and recursive integration
├── drift_tracker.py      # DriftScore and symbolic entropy monitoring
├── lineage_mapper.py     # Lineage trace and collapse hash tracking
├── core.py               # Unified interface importing the above
├── __init__.py           # Package exports
├── MEMORY_OVERVIEW.md    # Documentation
└── tests/
    └── test_unified_memory.py
```

## 🔧 Refactoring Steps

### Step 1: Extract Fold Engine

**From:** `unified_memory_system.py`
**To:** `memory/fold_engine.py`

```python
# memory/fold_engine.py
"""Memory folding and recursive integration engine."""

from typing import Dict, Any, Optional, List
import numpy as np
from dataclasses import dataclass

@dataclass
class FoldedMemory:
    vector: np.ndarray
    metadata: Dict[str, Any]
    fold_depth: int
    timestamp: float

class MemoryFoldEngine:
    """Handles memory folding operations."""
    
    def fold_in(self, experience: Dict[str, Any], context: Dict[str, Any]) -> FoldedMemory:
        """Fold experience into compressed memory representation."""
        pass
    
    def fold_out(self, memory: FoldedMemory, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Reconstruct experience from folded memory."""
        pass
    
    def merge_folds(self, memories: List[FoldedMemory]) -> FoldedMemory:
        """Merge multiple folded memories."""
        pass
```

### Step 2: Extract Drift Tracker

**From:** `unified_memory_system.py`
**To:** `memory/drift_tracker.py`

```python
# memory/drift_tracker.py
"""Drift score calculation and entropy monitoring."""

from typing import Tuple, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class DriftMetrics:
    score: float
    entropy: float
    stability: float
    time_delta: float

class DriftTracker:
    """Monitors semantic drift in memory vectors."""
    
    def calculate_drift(self, 
                       original: np.ndarray, 
                       current: np.ndarray,
                       time_delta: float) -> DriftMetrics:
        """Calculate drift between memory states."""
        pass
    
    def calculate_entropy(self, vector: np.ndarray) -> float:
        """Calculate symbolic entropy of memory vector."""
        pass
    
    def predict_collapse(self, metrics: DriftMetrics) -> float:
        """Predict probability of memory collapse."""
        pass
```

### Step 3: Extract Lineage Mapper

**From:** `unified_memory_system.py`
**To:** `memory/lineage_mapper.py`

```python
# memory/lineage_mapper.py
"""Memory lineage tracking and collapse management."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class CollapseEvent:
    collapse_hash: str
    parent_hashes: List[str]
    drift_score: float
    timestamp: float
    metadata: Dict[str, Any]

class LineageMapper:
    """Tracks memory lineage and collapse events."""
    
    def record_collapse(self, 
                       parent_memories: List[str],
                       drift_score: float,
                       metadata: Dict[str, Any]) -> CollapseEvent:
        """Record a memory collapse event."""
        pass
    
    def get_lineage(self, memory_hash: str) -> List[CollapseEvent]:
        """Get full lineage trace for a memory."""
        pass
    
    def find_common_ancestor(self, hash1: str, hash2: str) -> Optional[str]:
        """Find common ancestor between two memories."""
        pass
```

### Step 4: Create Unified Core

**To:** `memory/core.py`

```python
# memory/core.py
"""Unified memory system interface."""

from typing import Dict, Any, Optional, List
from .fold_engine import MemoryFoldEngine, FoldedMemory
from .drift_tracker import DriftTracker, DriftMetrics
from .lineage_mapper import LineageMapper, CollapseEvent

class MemoryCore:
    """Unified interface for LUKHAS memory system."""
    
    def __init__(self, 
                 agent_id: str,
                 enable_drift: bool = True,
                 collapse_threshold: float = 0.7):
        self.agent_id = agent_id
        self.fold_engine = MemoryFoldEngine()
        self.drift_tracker = DriftTracker() if enable_drift else None
        self.lineage_mapper = LineageMapper()
        self.collapse_threshold = collapse_threshold
        
    def store(self, experience: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Store experience in memory system."""
        # 1. Fold the experience
        folded = self.fold_engine.fold_in(experience, context)
        
        # 2. Check for drift if enabled
        if self.drift_tracker:
            # Implementation here
            pass
            
        # 3. Record in lineage
        # Implementation here
        
        return memory_id
    
    def retrieve(self, memory_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and reconstruct memory."""
        pass
    
    def search_similar(self, query: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar memories."""
        pass
```

### Step 5: Update Package Exports

**To:** `memory/__init__.py`

```python
# memory/__init__.py
"""LUKHAS Memory System."""

from .core import MemoryCore
from .fold_engine import MemoryFoldEngine, FoldedMemory
from .drift_tracker import DriftTracker, DriftMetrics
from .lineage_mapper import LineageMapper, CollapseEvent

__all__ = [
    'MemoryCore',
    'MemoryFoldEngine', 
    'FoldedMemory',
    'DriftTracker',
    'DriftMetrics',
    'LineageMapper',
    'CollapseEvent'
]
```

## 🔄 Migration Steps

1. **Backup Current State**
   ```bash
   cp memory/unified_memory_system.py memory/unified_memory_system.py.bak
   ```

2. **Create New Structure**
   ```bash
   touch memory/{fold_engine,drift_tracker,lineage_mapper,core}.py
   ```

3. **Extract Components**
   - Move folding-related classes/functions → `fold_engine.py`
   - Move drift-related classes/functions → `drift_tracker.py`
   - Move lineage-related classes/functions → `lineage_mapper.py`
   - Create unified interface in `core.py`

4. **Update Imports**
   ```python
   # Old
   from memory.unified_memory_system import MemoryFold
   
   # New
   from memory import MemoryCore
   # or
   from memory.fold_engine import MemoryFoldEngine
   ```

5. **Test Each Component**
   ```bash
   pytest memory/tests/test_fold_engine.py
   pytest memory/tests/test_drift_tracker.py
   pytest memory/tests/test_lineage_mapper.py
   pytest memory/tests/test_unified_memory.py
   ```

## 📊 Import Mapping

| Old Import | New Import |
|------------|------------|
| `from memory.unified_memory_system import HybridMemoryFold` | `from memory.fold_engine import MemoryFoldEngine` |
| `from memory.unified_memory_system import DriftScore` | `from memory.drift_tracker import DriftTracker` |
| `from memory.unified_memory_system import CollapseHash` | `from memory.lineage_mapper import LineageMapper` |
| `from memory.unified_memory_system import *` | `from memory import MemoryCore` |

## ✅ Success Criteria

- [ ] All tests pass
- [ ] No circular imports
- [ ] Each file < 500 lines
- [ ] Clear separation of concerns
- [ ] Backwards compatibility maintained
- [ ] API documentation updated