---
title: Memory Module Contract
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "architecture", "testing", "monitoring", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "memory", "guardian"]
  audience: ["dev"]
---

# 🧠 Memory Module Contract

## Overview

This document defines the detailed contract for the LUKHAS Memory System, including the DNA Helix memory architecture, fold-based storage, and unified memory orchestration.

## Module Hierarchy

```
memory/
├── core/
│   ├── unified_memory_orchestrator.py  # Main orchestrator
│   ├── interfaces.py                   # Memory interfaces
│   └── base_manager.py                 # Base memory manager
├── dna_helix/
│   ├── dna_healix.py                  # DNA helix implementation
│   └── repair_mechanisms.py           # Memory repair
├── folds/
│   ├── fold_engine.py                 # Fold-based storage
│   └── causal_chains.py              # Causal preservation
└── systems/
    ├── hippocampal/                   # Short-term memory
    └── neocortical/                   # Long-term consolidation
```

## Core Interfaces

### UnifiedMemoryOrchestrator

```python
class UnifiedMemoryOrchestrator:
    """
    Central memory coordination system.

    Responsibilities:
    - Coordinate between memory subsystems
    - Manage memory lifecycle
    - Handle consolidation between hippocampal and neocortical
    - Preserve causal chains
    """

    async def store_memory(self,
                          content: Any,
                          memory_type: MemoryType,
                          metadata: Optional[Dict[str, Any]] = None,
                          importance: float = 0.5) -> str:
        """
        Store memory with automatic classification.

        Args:
            content: Memory content
            memory_type: Type of memory
            metadata: Additional context
            importance: Priority score (0.0-1.0)

        Returns:
            str: Unique memory ID

        Contract:
            - Must validate content
            - Must assign unique ID
            - Must preserve timestamp
            - Must handle concurrent access
            - Must trigger consolidation if needed
        """

    async def retrieve_memory(self,
                            memory_id: str,
                            include_associations: bool = False) -> MemoryItem:
        """
        Retrieve memory by ID.

        Args:
            memory_id: Unique identifier
            include_associations: Include related memories

        Returns:
            MemoryItem with content and metadata

        Contract:
            - Must validate memory exists
            - Must check access permissions
            - Must update access patterns
            - Must handle cache misses gracefully
        """

    async def consolidate_memories(self,
                                 time_window: Optional[int] = None) -> ConsolidationReport:
        """
        Consolidate short-term to long-term memory.

        Args:
            time_window: Hours to consolidate (None = auto)

        Returns:
            ConsolidationReport with statistics

        Contract:
            - Must preserve important memories
            - Must maintain causal relationships
            - Must compress redundant information
            - Must be non-blocking
        """
```

### DNA Helix Memory

```python
class DNAHealixCore:
    """
    Immutable origin memory with drift detection.

    Responsibilities:
    - Store immutable origin strands
    - Detect memory drift
    - Repair corrupted memories
    - Maintain symbolic integrity
    """

    def __init__(self, origin: SymbolicStrand):
        """
        Initialize with origin strand.

        Contract:
            - Origin must be immutable after creation
            - Must generate unique helix ID
            - Must initialize drift detection
        """

    async def add_strand(self,
                        strand: SymbolicStrand,
                        bond_strength: float = 0.8) -> bool:
        """
        Add new memory strand.

        Args:
            strand: New symbolic strand
            bond_strength: Connection strength (0.0-1.0)

        Contract:
            - Must validate strand compatibility
            - Must preserve origin immutability
            - Must update drift calculations
            - Must maintain helix integrity
        """

    async def detect_drift(self) -> DriftReport:
        """
        Detect drift from origin.

        Returns:
            DriftReport with drift metrics

        Contract:
            - Must compare against immutable origin
            - Must identify drift patterns
            - Must suggest repair actions
            - Must not modify origin
        """

    async def repair_helix(self,
                          strategy: RepairStrategy = RepairStrategy.CONSERVATIVE) -> bool:
        """
        Repair drifted memories.

        Args:
            strategy: Repair approach

        Contract:
            - Must preserve origin
            - Must log all repairs
            - Must validate post-repair state
            - Must be reversible
        """
```

### Fold-Based Storage

```python
class FoldEngine:
    """
    Fold-based memory storage with causal preservation.

    Responsibilities:
    - Create memory folds
    - Preserve causal chains
    - Handle fold operations
    - Manage emotional context
    """

    async def create_fold(self,
                         memories: List[MemoryItem],
                         fold_type: FoldType = FoldType.TEMPORAL) -> Fold:
        """
        Create new memory fold.

        Args:
            memories: Memories to fold
            fold_type: Type of fold operation

        Returns:
            Fold object with preserved relationships

        Contract:
            - Must preserve all causal links
            - Must maintain temporal ordering
            - Must capture emotional context
            - Must be queryable
        """

    async def unfold(self,
                    fold_id: str,
                    depth: int = 1) -> List[MemoryItem]:
        """
        Unfold memories to specified depth.

        Args:
            fold_id: Fold identifier
            depth: Unfold depth (1 = immediate, -1 = full)

        Contract:
            - Must restore original order
            - Must preserve all metadata
            - Must handle nested folds
            - Must be memory efficient
        """
```

## Data Structures

### MemoryItem

```python
@dataclass
class MemoryItem:
    """Standard memory item structure"""
    memory_id: str
    content: Any
    memory_type: MemoryType
    timestamp: datetime
    metadata: Dict[str, Any]
    importance: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    associations: List[str] = field(default_factory=list)
    emotional_context: Optional[EmotionalContext] = None
    causal_links: List[CausalLink] = field(default_factory=list)
```

### SymbolicStrand

```python
@dataclass
class SymbolicStrand:
    """DNA helix memory strand"""
    strand_id: str
    glyph_sequence: List[GLYPHToken]
    bond_pairs: List[Tuple[int, int]]
    metadata: Dict[str, Any]
    drift_vector: Optional[np.ndarray] = None
    integrity_score: float = 1.0
```

## Performance Requirements

### Response Times

| Operation | Target | Maximum |
|-----------|--------|---------|
| Store Memory | 50ms | 200ms |
| Retrieve Memory | 30ms | 150ms |
| Search Memory | 100ms | 500ms |
| Create Fold | 100ms | 300ms |
| Consolidation | 5s | 30s |
| Drift Detection | 200ms | 1s |

### Capacity Limits

- **Hippocampal Buffer**: 10,000 items
- **Neocortical Storage**: 1,000,000 items
- **Active Folds**: 1,000 concurrent
- **DNA Helixes**: 10,000 active
- **Associations per Memory**: 100 maximum

## Error Handling

### Memory-Specific Exceptions

```python
class MemoryError(LukhasError):
    """Base memory exception"""

class MemoryNotFoundError(MemoryError):
    """Memory ID not found"""

class MemoryCorruptionError(MemoryError):
    """Memory integrity compromised"""

class ConsolidationError(MemoryError):
    """Consolidation process failed"""

class FoldError(MemoryError):
    """Fold operation failed"""

class DriftError(MemoryError):
    """Excessive drift detected"""
```

### Recovery Procedures

1. **Corruption Detection**: Automatic integrity checks every 1000 operations
2. **Repair Triggers**: Drift > 0.3 triggers automatic repair
3. **Backup Strategy**: Snapshot every hour, retain 24 hours
4. **Cascade Prevention**: 99.7% cascade prevention rate required

## Integration Points

### With Consciousness

```python
# Memory provides context for decisions
context = await memory.get_relevant_context(scenario)
decision = await consciousness.make_decision(scenario, context=context)

# Consciousness creates memories
experience = await consciousness.process_experience(input_data)
memory_id = await memory.store_memory(experience, MemoryType.EPISODIC)
```

### With Guardian System

```python
# Guardian validates memory access
access_request = MemoryAccessRequest(
    memory_id=memory_id,
    requester=module_id,
    purpose="analysis"
)
validation = await guardian.validate_memory_access(access_request)
if validation.approved:
    memory = await memory.retrieve_memory(memory_id)
```

## Monitoring & Metrics

### Required Metrics

```python
class MemoryMetrics:
    total_memories: int
    hippocampal_usage: float  # 0.0-1.0
    neocortical_usage: float  # 0.0-1.0
    average_retrieval_time_ms: float
    consolidation_rate: float  # memories/hour
    drift_score: float  # 0.0-1.0
    fold_efficiency: float  # 0.0-1.0
    cache_hit_rate: float  # 0.0-1.0
```

### Health Checks

```python
async def health_check() -> HealthStatus:
    """
    Perform memory system health check.

    Checks:
    - Storage availability
    - Drift levels
    - Consolidation backlog
    - Cache performance
    - Integrity scores
    """
```

## Testing Requirements

### Unit Tests

- Memory CRUD operations
- Fold/unfold operations
- Drift detection accuracy
- Repair effectiveness
- Concurrent access handling

### Integration Tests

- Consciousness-memory interaction
- Guardian validation flow
- Multi-module memory sharing
- Consolidation under load
- Recovery procedures

### Performance Tests

- 10,000 concurrent stores
- 100,000 retrieval operations
- Consolidation of 1M memories
- Drift detection on 10K helixes

## Migration & Versioning

### Schema Version

Current: `memory_schema_v2.0`

### Backward Compatibility

- Read v1.0 memories with adapter
- Automatic migration on access
- Preserve all v1.0 metadata

### Future Compatibility

- Extensible metadata structure
- Pluggable storage backends
- Modular consolidation strategies

---

*Contract Version: 2.0.0*
*Last Updated: 2025-08-03*
