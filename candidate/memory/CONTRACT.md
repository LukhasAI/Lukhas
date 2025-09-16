# Memory Systems Contract

This document outlines the contracts for the core memory systems in the `candidate/memory` module. All tests written for these modules must validate these invariants.

## 1. UnifiedMemoryOrchestrator

**Path:** `candidate/memory/core/unified_memory_orchestrator.py`

### Inputs
- `encode_memory()`: `content`, `memory_type`, `tags`, `emotional_valence`, `importance`, `semantic_links`.
- `retrieve_memory()`: `query`, `memory_types`, `use_pattern_completion`, `max_results`.
- `consolidate_memory()`: `memory_id`, `force`.
- `forget_memory()`: `memory_id`, `gradual`.
- `enter_sleep_stage()`: `stage`.

### Outputs
- `encode_memory()`: Returns a unique `memory_id` (string).
- `retrieve_memory()`: Returns a list of `(MemoryTrace, relevance_score)` tuples.
- `consolidate_memory()`: Returns a boolean indicating success.
- `forget_memory()`: Returns a boolean indicating success.

### Invariants
1. **Idempotency**: Retrieving a memory should not change its state, except for access counters.
2. **State Transitions**: A memory must be in the `hippocampal_buffer` before it can be consolidated. After consolidation, it must be in the `neocortical_network`.
3. **Immutability of Consolidated Memory**: Once a memory is consolidated, its core content should not change, except through explicit reconsolidation.
4. **Capacity Limits**: The `hippocampal_buffer` and `neocortical_network` must not exceed their defined capacity. The system must handle overflow gracefully.
5. **Sleep Cycle Dependency**: Meaningful consolidation should only occur during appropriate sleep stages (NREM2, NREM3).
6. **Colony Validation**: If enabled, no memory should be encoded without successful validation from the relevant memory colonies.

## 2. AdvancedMemoryManager

**Path:** `candidate/memory/systems/memory_manager.py`

### Inputs
- `store_memory()`: `content`, `memory_type`, `priority`, `emotional_context`, `tags`, `owner_id`, `metadata`.
- `retrieve_memory()`: `memory_id`.
- `search_memories()`: `query`, `emotional_filter`, `memory_type`, `owner_id`, `limit`.
- `retrieve_by_emotion()`: `emotion`, `intensity_threshold`, `limit`.
- `consolidate_memories()`: `time_window_hours`.
- `optimize_memory_storage()`: No arguments.
- `get_related_memories()`: `memory_id`, `limit`.
- `get_memory_statistics()`: No arguments.

### Outputs
- `store_memory()`: Returns a `memory_id` (string).
- `retrieve_memory()`: Returns an optional dictionary representing the memory data.
- `search_memories()`: Returns a list of memory data dictionaries.
- `retrieve_by_emotion()`: Returns a list of memory data dictionaries.
- `consolidate_memories()`: Returns a dictionary with consolidation status.
- `optimize_memory_storage()`: Returns a dictionary with optimization report.
- `get_related_memories()`: Returns a list of related memory data dictionaries.
- `get_memory_statistics()`: Returns a dictionary of statistics.

### Invariants
1. **Dependency Inversion**: The manager must function gracefully (i.e., not crash) if its dependencies (`base_memory_manager`, `fold_engine`, `emotional_oscillator`, `qi_attention`) are `None` or are missing optional methods.
2. **Metrics Consistency**: Internal metrics (`self.metrics`) must be updated accurately after each operation (e.g., `memories_stored`, `successful_retrievals`).
3. **Data Flow**: `store_memory` must call both the base manager's `store` method and the fold engine's `add_fold` method.
4. **State Forwarding**: The manager should act as a pass-through for operations like `consolidate_memories`, forwarding the call to the `fold_engine` and returning its result.

## 3. MemoryFold

**Path:** `candidate/memory/folds/fold_engine.py`

### Inputs
- `__init__()`: `key`, `content`, `memory_type`, `priority`, `owner_id`, `timestamp_utc`.
- `retrieve()`: `tier_level`, `query_context`.
- `update()`: `new_content`, `new_priority`.
- `add_association()`: `related_key`.
- `add_tag()`: `tag`.

### Outputs
- `retrieve()`: Returns the memory content, potentially filtered based on tier level.
- `to_dict()`: Returns a dictionary representation of the fold.

### Invariants
1. **Importance Dynamics**: The `importance_score` must be recalculated upon `update`. It should increase with access frequency and associations, and decrease with time since last access.
2. **Immutability of Key**: The `key` of a `MemoryFold` must not change after initialization.
3. **Access Metadata**: `retrieve()` and `update()` must increment `access_count` and update `last_accessed_utc`.
4. **Tiered Access**: `retrieve()` must return `None` if the provided `tier_level` is lower than the memory's required tier.
5. **Drift and Reflection**: `driftScore` must be updated on changes to importance. `auto_reflect()` should only return data when a drift threshold is exceeded.
