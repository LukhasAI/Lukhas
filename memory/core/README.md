# Unified Memory Orchestrator

A multi-tier memory system for LUKHAS AI that mimics human memory architecture.

## Overview

The Unified Memory Orchestrator provides a comprehensive memory management system with four distinct tiers:

1. **Working Memory**: Active, fast (in-memory) storage for currently active information
2. **Episodic Memory**: Time-ordered events and experiences
3. **Semantic Memory**: Concept relationships and knowledge graphs
4. **Fold Storage**: Compressed long-term memory archives

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Unified Memory Orchestrator                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌──────────────┐                │
│  │  Working    │  │  Episodic    │                │
│  │  Memory     │──│  Memory      │                │
│  │  (< 15 min) │  │  (events)    │                │
│  └─────────────┘  └──────────────┘                │
│         │               │                          │
│         │               │                          │
│  ┌─────────────┐  ┌──────────────┐                │
│  │  Semantic   │  │  Fold        │                │
│  │  Memory     │  │  Storage     │                │
│  │  (concepts) │  │  (archives)  │                │
│  └─────────────┘  └──────────────┘                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Consolidation Process

Memory consolidation happens automatically at regular intervals:

- **Every 15 minutes**: Working Memory → Episodic Memory
  - Moves memories older than TTL to episodic storage
  - Preserves temporal context and metadata

- **Every 6 hours**: Episodic Memory → Semantic Memory + Folds
  - Extracts concepts and relationships from episodes
  - Creates compressed folds for long-term storage

- **Weekly**: Fold Compression
  - Merges and optimizes old folds
  - Reduces storage footprint

## Usage

### Initialization

```python
from memory.core import UnifiedMemoryOrchestrator, MemoryType

# Create orchestrator with custom config
config = {
    "working_memory_ttl": 15,           # Minutes
    "episodic_to_semantic_hours": 6,    # Hours
    "fold_compression_days": 7,          # Days
    "vector_dimension": 768,             # Embedding size
    "storage_path": "./memory_folds"     # Fold storage location
}

orchestrator = UnifiedMemoryOrchestrator(config=config)
```

### Storing Memories

```python
# Store in working memory
work_id = orchestrator.store(
    key="current_task",
    value="Processing user request #123",
    memory_type=MemoryType.WORKING,
    metadata={"user_id": "user123", "priority": "high"}
)

# Store episodic memory
episode_id = orchestrator.store(
    key="conversation_456",
    value="User discussed project requirements",
    memory_type=MemoryType.EPISODIC,
    metadata={
        "episode_type": "CONVERSATION",
        "participants": ["user123", "ai_agent"],
        "goals": ["gather requirements"]
    }
)

# Store semantic memory
concept_id = orchestrator.store(
    key="ml_concept",
    value="Neural networks are computational models...",
    memory_type=MemoryType.SEMANTIC,
    metadata={
        "node_type": "CONCEPT",
        "tags": ["machine-learning", "neural-networks"],
        "properties": {"domain": "AI"}
    }
)
```

### Retrieving Memories

```python
# Retrieve by ID from any tier
memory = orchestrator.retrieve("conversation_456")

# Semantic search
results = orchestrator.search_semantic(
    query="machine learning concepts",
    limit=10
)

for memory in results:
    print(f"{memory.id}: {memory.content}")
    print(f"Relevance: {memory.metadata['relevance_score']}")
```

### Manual Consolidation

```python
# Trigger consolidation manually
result = orchestrator.consolidate()

print(f"Consolidated {result.total_memories_processed} memories")
print(f"Working → Episodic: {result.working_to_episodic}")
print(f"Episodic → Semantic: {result.episodic_to_semantic}")
print(f"Episodic → Folds: {result.episodic_to_folds}")
print(f"Duration: {result.duration_seconds}s")

if result.errors:
    print(f"Errors: {result.errors}")
```

### Creating Folds

```python
from memory.core import Memory
from datetime import datetime, timezone

# Create memories to archive
memories = [
    Memory(
        id="mem_1",
        content="Historical event 1",
        memory_type=MemoryType.EPISODIC,
        tier="episodic",
        timestamp=datetime.now(timezone.utc),
        metadata={"tags": ["archived", "important"]}
    ),
    Memory(
        id="mem_2",
        content="Historical event 2",
        memory_type=MemoryType.EPISODIC,
        tier="episodic",
        timestamp=datetime.now(timezone.utc),
        metadata={"tags": ["archived"]}
    )
]

# Create compressed fold
fold_id = orchestrator.create_fold(memories)
print(f"Created fold: {fold_id}")
```

### Statistics

```python
# Get comprehensive stats
stats = orchestrator.get_stats()

print("Working Memory:", stats["working_memory"])
print("Episodic Memory:", stats["episodic_memory"])
print("Semantic Memory:", stats["semantic_memory"])
print("Vector Store:", stats["vector_store"])
print("Folds:", stats["folds"])
print("Consolidation:", stats["consolidation"])
```

## API Reference

### UnifiedMemoryOrchestrator

Main orchestrator class managing all memory tiers.

**Methods:**

- `store(key, value, memory_type, metadata=None)` → str
  - Store memory in appropriate tier
  - Returns: Memory ID

- `retrieve(key)` → Optional[Any]
  - Retrieve memory by key from any tier
  - Returns: Memory content or None

- `consolidate()` → ConsolidationResult
  - Run memory consolidation process
  - Returns: Consolidation statistics

- `search_semantic(query, limit=10)` → List[Memory]
  - Semantic similarity search
  - Returns: List of matching memories

- `create_fold(memories)` → str
  - Create compressed memory fold
  - Returns: Fold ID

- `get_stats()` → Dict[str, Any]
  - Get comprehensive statistics
  - Returns: Stats dictionary

### MemoryType Enum

Memory tier types:

- `WORKING`: Active, temporary (< 15 min)
- `EPISODIC`: Time-stamped events
- `SEMANTIC`: Concepts and relationships
- `FOLD`: Compressed archives

### Memory Dataclass

Unified memory representation.

**Fields:**
- `id`: str - Unique identifier
- `content`: Any - Memory content
- `memory_type`: MemoryType - Type of memory
- `tier`: str - Which tier it's stored in
- `timestamp`: datetime - Creation timestamp
- `metadata`: Dict[str, Any] - Additional metadata
- `importance_score`: float - Importance (0.0-1.0)
- `access_count`: int - Number of accesses
- `last_accessed`: Optional[datetime] - Last access time

### ConsolidationResult Dataclass

Results from consolidation process.

**Fields:**
- `timestamp`: datetime - When consolidation ran
- `working_to_episodic`: int - Memories moved
- `episodic_to_semantic`: int - Concepts extracted
- `episodic_to_folds`: int - Folds created
- `folds_compressed`: int - Folds compressed
- `total_memories_processed`: int - Total processed
- `duration_seconds`: float - Process duration
- `errors`: List[str] - Any errors encountered

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/unit/memory/core/test_unified_memory_orchestrator.py -v

# Run specific test class
pytest tests/unit/memory/core/test_unified_memory_orchestrator.py::TestUnifiedMemoryOrchestrator -v

# Run with coverage
pytest tests/unit/memory/core/test_unified_memory_orchestrator.py --cov=memory.core --cov-report=html
```

## Dependencies

- `numpy`: Vector operations
- `networkx`: Graph operations for semantic memory
- `sentence-transformers`: Embeddings (optional, for semantic search)

Install dependencies:

```bash
pip install numpy networkx sentence-transformers
```

## Integration

The orchestrator integrates with existing LUKHAS memory systems:

- **EpisodicMemorySystem** (`cognitive_core.memory.episodic_memory`)
- **SemanticMemoryGraph** (`cognitive_core.memory.semantic_memory`)
- **VectorMemoryStore** (`cognitive_core.memory.vector_memory`)

All existing functionality from these systems is preserved and enhanced with:
- Unified interface
- Automatic consolidation
- Cross-tier search
- Fold compression

## Performance Considerations

### Memory Usage

- Working memory is in-memory only, limit via TTL
- Episodic and semantic use vector store (configurable max size)
- Folds are disk-based, minimal memory footprint

### Scalability

- Vector operations use NumPy for efficiency
- Semantic graph uses NetworkX with efficient indexing
- Fold compression reduces long-term storage by ~75%

### Async Operations

Many operations use async/await internally:
- Episode creation and retrieval
- Semantic node operations
- Consolidation processes

The orchestrator handles async transparently via `asyncio.run()`.

## Future Enhancements

Planned improvements:

1. **Redis Integration**: Replace in-memory working storage with Redis
2. **PostgreSQL Backend**: Persistent episodic storage
3. **Advanced Compression**: Better fold compression algorithms
4. **Distributed Operation**: Multi-node memory coordination
5. **Auto-tuning**: Adaptive consolidation schedules
6. **Query Optimization**: Faster cross-tier searches

## License

Proprietary - LUKHAS AI Systems

## Contact

For questions or issues, contact the LUKHAS Core Memory Architecture Team.
