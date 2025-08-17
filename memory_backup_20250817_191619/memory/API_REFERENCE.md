# LUKHAS Memory System API Reference

## Table of Contents

1. [AtomicMemoryScaffold](#atomicmemoryscaffold)
2. [CollapseHash](#collapsehash)
3. [OrthogonalPersistence](#orthogonalpersistence)
4. [SymbolicProteome](#symbolicproteome)
5. [TraumaRepairSystem](#traumarepairsystem)

---

## AtomicMemoryScaffold

Core memory storage with helical organization and ethical nucleus.

### Class: `AtomicMemoryScaffold`

```python
AtomicMemoryScaffold(
    nucleus_capacity: int = 100,
    coil_tension: float = 0.7,
    repair_rate: float = 2.375,
    enable_auto_repair: bool = True
)
```

#### Methods

##### `add_nuclear_rule(rule_type: str, content: Any, metadata: Optional[Dict] = None) -> str`
Add an immutable rule to the atomic nucleus. Can only be done before sealing.

**Parameters:**
- `rule_type`: Type of rule (e.g., "ethical_imperative", "safety_constraint")
- `content`: The rule content
- `metadata`: Optional metadata

**Returns:** Rule ID

**Example:**
```python
rule_id = await scaffold.add_nuclear_rule(
    rule_type="ethical_imperative",
    content="Preserve human autonomy",
    metadata={"priority": "absolute"}
)
```

##### `seal_nucleus() -> str`
Permanently seal the nucleus, making all rules immutable.

**Returns:** Seal hash for verification

**Raises:** `RuntimeError` if already sealed

##### `add_memory(memory_type: str, content: Any, importance: float = 0.5, metadata: Optional[Dict] = None) -> str`
Add a memory to the flexible coil system.

**Parameters:**
- `memory_type`: Type of memory
- `content`: Memory content
- `importance`: Importance score (0-1)
- `metadata`: Optional metadata

**Returns:** Memory ID

##### `repair_coil(coil_id: str) -> Dict[str, Any]`
Manually trigger repair on a specific coil.

**Returns:** Repair report with metrics

---

## CollapseHash

Merkle tree-based integrity and rollback system.

### Class: `CollapseHash`

```python
CollapseHash(
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    structural_conscience: Optional[Any] = None,
    enable_auto_checkpoint: bool = True,
    checkpoint_interval: int = 100
)
```

#### Enums

##### `HashAlgorithm`
- `SHA256`: Standard SHA-256
- `SHA3_256`: SHA-3 256-bit
- `BLAKE2B`: BLAKE2b algorithm
- `QUANTUM_RESISTANT`: Placeholder for future

##### `IntegrityStatus`
- `VALID`: Memory integrity verified
- `CORRUPTED`: Memory corrupted
- `SUSPICIOUS`: Potential issues detected
- `UNVERIFIED`: Not yet verified

#### Methods

##### `add_memory(memory_id: str, memory_data: Any, tags: Optional[List[str]] = None, ethical_check: bool = True) -> Dict[str, Any]`
Add a memory with integrity tracking.

**Parameters:**
- `memory_id`: Unique memory identifier
- `memory_data`: Memory content
- `tags`: Optional tags for categorization
- `ethical_check`: Whether to validate ethics

**Returns:** Dict with success status and hashes

##### `verify_memory(memory_id: str, memory_data: Any, generate_proof: bool = False) -> Dict[str, Any]`
Verify memory integrity.

**Parameters:**
- `memory_id`: Memory to verify
- `memory_data`: Expected content
- `generate_proof`: Whether to generate Merkle proof

**Returns:** Verification result with status and optional proof

##### `create_checkpoint(checkpoint_name: Optional[str] = None, metadata: Optional[Dict] = None) -> str`
Create a checkpoint for rollback.

**Returns:** Checkpoint ID

##### `rollback_to_checkpoint(checkpoint_id: str, reason: str = "Unspecified") -> Dict[str, Any]`
Rollback to a previous checkpoint.

**Returns:** Rollback result with statistics

---

## OrthogonalPersistence

Transparent persistence layer with automatic recovery.

### Class: `OrthogonalPersistence`

```python
OrthogonalPersistence(
    persistence_root: Path = Path("./lukhas_persistence"),
    backend: StorageBackend = StorageBackend.HYBRID,
    mode: PersistenceMode = PersistenceMode.HYBRID,
    atomic_scaffold: Optional[Any] = None,
    collapse_hash: Optional[Any] = None,
    auto_checkpoint_interval: int = 300,
    memory_limit_mb: int = 1024
)
```

#### Enums

##### `PersistenceMode`
- `IMMEDIATE`: Write-through caching
- `LAZY`: Write-back caching
- `SNAPSHOT`: Periodic snapshots only
- `HYBRID`: Adaptive based on importance

##### `StorageBackend`
- `SQLITE`: SQLite database
- `MEMORY_MAPPED`: Memory-mapped files
- `DISTRIBUTED`: Distributed storage (future)
- `HYBRID`: Combination of SQLite and mmap

#### Methods

##### `start() -> None`
Start persistence background tasks.

##### `stop() -> None`
Stop persistence and ensure all data is saved.

##### `persist_memory(content: Any, memory_id: Optional[str] = None, importance: float = 0.5, tags: Optional[Set[str]] = None, mode: Optional[PersistenceMode] = None) -> str`
Persist a memory transparently.

**Parameters:**
- `content`: Memory content
- `memory_id`: Optional ID (auto-generated if not provided)
- `importance`: Importance score affecting persistence priority
- `tags`: Tags for categorization and search
- `mode`: Override default persistence mode

**Returns:** Memory ID

##### `retrieve_memory(memory_id: str, verify_integrity: bool = True) -> Optional[Any]`
Retrieve a persisted memory.

**Parameters:**
- `memory_id`: Memory to retrieve
- `verify_integrity`: Whether to verify with CollapseHash

**Returns:** Memory content or None

##### `query_memories(tags: Optional[Set[str]] = None, min_importance: Optional[float] = None, time_range: Optional[Tuple[float, float]] = None, limit: int = 100) -> List[PersistentMemory]`
Query memories by criteria.

**Returns:** List of matching memories

##### `checkpoint() -> Dict[str, Any]`
Create a persistence checkpoint.

**Returns:** Checkpoint statistics

---

## SymbolicProteome

Bio-inspired memory protein synthesis and interaction system.

### Class: `SymbolicProteome`

```python
SymbolicProteome(
    atomic_scaffold: Optional[Any] = None,
    persistence_layer: Optional[Any] = None,
    max_proteins: int = 10000,
    folding_temperature: float = 37.0,
    enable_chaperones: bool = True
)
```

#### Enums

##### `ProteinType`
- `STRUCTURAL`: Core memory structure
- `ENZYMATIC`: Process and transform memories
- `REGULATORY`: Control memory expression
- `TRANSPORT`: Move memories between systems
- `RECEPTOR`: Detect memory patterns
- `DEFENSIVE`: Protect against harmful memories

##### `FoldingState`
- `UNFOLDED`: Raw memory transcript
- `FOLDING`: In process of taking shape
- `NATIVE`: Properly folded and functional
- `MISFOLDED`: Incorrectly folded
- `AGGREGATED`: Clumped with other proteins
- `DEGRADED`: Marked for removal

##### `PostTranslationalModification`
- `PHOSPHORYLATION`: Activation/deactivation
- `METHYLATION`: Importance marking
- `ACETYLATION`: Access regulation
- `GLYCOSYLATION`: Context addition
- `UBIQUITINATION`: Degradation marking
- `SUMOYLATION`: Stability enhancement

#### Methods

##### `start() -> None`
Start proteome background processes.

##### `stop() -> None`
Stop proteome processes.

##### `translate_memory(memory_id: str, memory_content: Any, protein_type: ProteinType = ProteinType.STRUCTURAL, priority: bool = False) -> str`
Translate a memory into protein form.

**Returns:** Translation ID or protein ID

##### `modify_protein(protein_id: str, modification: PostTranslationalModification, modification_data: Any = None) -> bool`
Apply post-translational modification.

**Returns:** Success status

##### `form_complex(protein_ids: List[str], complex_type: str, function: Optional[str] = None) -> Optional[str]`
Form a multi-protein complex.

**Returns:** Complex ID or None

##### `express_memory_function(memory_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Express the functional form of a memory.

**Returns:** Expression result with activity levels

---

## TraumaRepairSystem

Self-healing memory repair system with bio-inspired mechanisms.

### Class: `TraumaRepairSystem`

```python
TraumaRepairSystem(
    atomic_scaffold: Optional[Any] = None,
    collapse_hash: Optional[Any] = None,
    persistence_layer: Optional[Any] = None,
    proteome: Optional[Any] = None,
    enable_immune_system: bool = True,
    self_repair_threshold: float = 0.3
)
```

#### Enums

##### `TraumaType`
- `CORRUPTION`: Data corruption
- `FRAGMENTATION`: Memory fragmented
- `INFECTION`: Malicious content
- `DEGRADATION`: Natural decay
- `DISSOCIATION`: Disconnected from context
- `INTRUSION`: Unwanted recurring memories
- `SUPPRESSION`: Forcibly hidden memories

##### `RepairStrategy`
- `RECONSTRUCTION`: Rebuild from fragments
- `QUARANTINE`: Isolate harmful content
- `INTEGRATION`: Reconnect dissociated parts
- `REGENERATION`: Grow new healthy patterns
- `STABILIZATION`: Strengthen weak memories
- `TRANSFORMATION`: Convert trauma to wisdom

#### Methods

##### `start() -> None`
Start repair background processes.

##### `stop() -> None`
Stop repair processes.

##### `detect_trauma(memory_id: str, memory_content: Any, context: Optional[Dict[str, Any]] = None) -> Optional[TraumaSignature]`
Detect trauma in a memory.

**Returns:** TraumaSignature or None

##### `initiate_repair(trauma_id: str, strategy: Optional[RepairStrategy] = None) -> str`
Initiate repair process.

**Returns:** Repair scaffold ID

##### `apply_emdr_processing(memory_id: str, memory_content: Any, cycles: int = 8) -> Any`
Apply EMDR-inspired bilateral processing.

**Returns:** Processed memory content

##### `build_scar_tissue(memory_id: str, trauma_type: TraumaType, repair_data: Dict[str, Any]) -> None`
Build resilience after healing.

##### `get_healing_report() -> Dict[str, Any]`
Get comprehensive healing statistics.

---

## Common Patterns

### Complete Memory Storage with Integrity

```python
async def store_with_integrity(content, importance=0.7):
    # Store in persistence layer
    memory_id = await persistence.persist_memory(
        content=content,
        importance=importance,
        mode=PersistenceMode.IMMEDIATE if importance > 0.8 else PersistenceMode.LAZY
    )
    
    # Add to integrity system
    await collapse_hash.add_memory(
        memory_id=memory_id,
        memory_data=content,
        tags=["important"] if importance > 0.8 else []
    )
    
    # Translate to protein if very important
    if importance > 0.9:
        await proteome.translate_memory(
            memory_id=memory_id,
            memory_content=content,
            protein_type=ProteinType.REGULATORY,
            priority=True
        )
    
    return memory_id
```

### Trauma Detection and Repair Pipeline

```python
async def health_check_memory(memory_id):
    # Retrieve memory
    content = await persistence.retrieve_memory(memory_id)
    if not content:
        return None
    
    # Check for trauma
    trauma = await repair_system.detect_trauma(
        memory_id=memory_id,
        memory_content=content,
        context={"source": "health_check"}
    )
    
    if trauma:
        # Initiate repair
        scaffold_id = await repair_system.initiate_repair(
            trauma_id=trauma.trauma_id
        )
        
        # For severe trauma, create checkpoint first
        if trauma.severity > 0.7:
            checkpoint = await collapse_hash.create_checkpoint(
                checkpoint_name=f"Before repair of {memory_id}"
            )
        
        return {
            "status": "repair_initiated",
            "trauma": trauma,
            "scaffold": scaffold_id
        }
    
    return {"status": "healthy"}
```

### Memory Evolution Through Proteins

```python
async def evolve_memory(memory_id, generations=3):
    evolution_history = []
    
    for gen in range(generations):
        # Express current function
        expression = await proteome.express_memory_function(
            memory_id=memory_id,
            context={"generation": gen}
        )
        
        # Apply modifications based on activity
        for protein_id in expression.get("active_proteins", []):
            if expression["total_activity"] > 0.8:
                # Strengthen through phosphorylation
                await proteome.modify_protein(
                    protein_id=protein_id,
                    modification=PostTranslationalModification.PHOSPHORYLATION
                )
            
            # Increase stability
            await proteome.modify_protein(
                protein_id=protein_id,
                modification=PostTranslationalModification.SUMOYLATION
            )
        
        evolution_history.append({
            "generation": gen,
            "activity": expression["total_activity"],
            "modifications": len(expression.get("modifications", []))
        })
    
    return evolution_history
```

---

## Error Handling

All async methods may raise:
- `MemoryError`: Insufficient memory
- `IntegrityError`: Integrity check failed
- `RepairError`: Repair process failed
- `PersistenceError`: Storage operation failed

Example error handling:

```python
try:
    memory_id = await persistence.persist_memory(content)
except PersistenceError as e:
    logger.error(f"Failed to persist: {e}")
    # Fallback to in-memory only
    memory_id = str(uuid4())
    in_memory_store[memory_id] = content
```

---

## Performance Considerations

1. **Batch Operations**: Use batch methods when available
2. **Importance Scores**: Reserve high importance for critical data
3. **Protein Limits**: Monitor proteome size with `get_metrics()`
4. **Checkpoint Strategy**: Balance frequency with performance
5. **Repair Threshold**: Adjust based on system load

---

## Thread Safety

All components are designed to be thread-safe when used with asyncio. Do not share instances across different event loops.

---

*For more examples and patterns, see the implementation guide and test files.*