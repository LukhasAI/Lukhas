---
title: lukhas_context
slug: memory.lukhas_context
owner: T4
lane: labs
star: "✦ Trail Star"
stability: experimental
last_reviewed: 2025-10-24
constellation_stars: "✦ Trail · ⚛️ Anchor · 🛡️ Watch"
related_modules: "matriz, guardian, identity, consciousness"
manifests: "module.manifest.json"
links: "../matriz/node_contract.py, ../matriz/core/memory_system.py"
contracts: "[MemoryFold, MatrizMessage, CognitiveMemory]"
domain: memory, storage, persistence
stars: "[Trail]"
status: active
tier: T2
updated: 2025-10-24
version: 1.0.0
---
# Memory System - ✦ Trail Star
## Fold-Based Memory & MATRIZ Cognitive Persistence

*Trail Star of Constellation Framework - Memory persistence for all MATRIZ cognitive operations*

---

## Memory System Overview

**Memory Module Location**: [memory/](.)

The Memory system is the **fold-based memory persistence and cognitive state management layer** for the entire LUKHAS ecosystem. Every MATRIZ cognitive operation involving MEMORY GLYPH uses fold-based storage, ensuring complete provenance tracking and temporal relationship preservation.

### **Trail Star Integration** ✦

- **Purpose**: Fold-based memory persistence, cognitive DNA storage, and temporal relationship tracking
- **Architecture**: Sanctum Vault protection with memory fold hierarchy and MATRIZ Memory stage coordination
- **Integration**: MATRIZ Memory stage storage, Guardian audit trail persistence, ΛiD-scoped memory access
- **Contract**: Stores MatrizResult traces and cognitive DNA per [node_contract.py](../matriz/node_contract.py:1)

### **System Scope**

- **Lane**: Labs (Experimental) → L2 (Integration)
- **Storage**: Fold-based hierarchy, encrypted at rest, temporal indexing
- **MATRIZ Integration**: Required for MEMORY GLYPH operations and cognitive DNA persistence
- **Constellation Role**: Trail Star ✦ - Memory and persistence foundation

---

## Core Memory Components

### **1. Memory Folds - Hierarchical Storage**

**Purpose**: Hierarchical fold-based memory storage with temporal relationships

**Fold Structure:**
```python
from memory import MemoryFold, create_memory_fold
from matriz.node_contract import MatrizMessage, MatrizResult

# Create memory fold for cognitive session
session_fold = create_memory_fold(
    fold_name="cognitive_session_20251024",
    fold_type="SESSION",
    parent_fold=None,  # Root fold
    metadata={
        "session_id": "session_abc123",
        "user_lambda_id": "user_12345_lambda_xyz",
        "start_time": "2025-10-24T10:00:00Z"
    }
)

# Store MATRIZ result in fold
result_stored = session_fold.store_matriz_result(
    msg_id="550e8400-e29b-41d4-a716-446655440000",
    result=MatrizResult(
        ok=True,
        reasons=["Cognitive processing complete"],
        payload={"result": "success"},
        trace={
            "node": "math-node",
            "processing_ms": 42,
            "cognitive_dna": {...}
        },
        guardian_log=["Guardian validated", "Processing approved"]
    ),
    temporal_links=[
        {"type": "FOLLOWS", "target_msg_id": "prev_msg_id"}
    ],
    causal_links=[
        {"type": "CAUSED_BY", "target_msg_id": "prev_msg_id"}
    ]
)
```

**Fold Hierarchy:**
```
Root Fold
├── Session Fold (cognitive_session_20251024)
│   ├── Memory Fold (working_memory)
│   │   ├── MEMORY GLYPH results
│   │   └── Temporal relationships
│   ├── Reasoning Fold (reasoning_chain)
│   │   ├── THOUGHT GLYPH results
│   │   └── Causal relationships
│   └── Decision Fold (decisions)
│       ├── DECISION GLYPH results
│       └── Intent relationships
└── Archive Fold (historical_sessions)
    └── Compressed session folds
```

### **2. Cognitive DNA Persistence**

**Purpose**: Store complete cognitive DNA and provenance traces

**MATRIZ Integration:**
```python
from memory import store_cognitive_dna, retrieve_cognitive_dna
from matriz.node_contract import MatrizMessage, MatrizResult

# Store cognitive DNA after MATRIZ processing
def handle(msg: MatrizMessage) -> MatrizResult:
    # Process MATRIZ message
    result = process_matriz_message(msg)

    # Store cognitive DNA in memory fold
    dna_stored = store_cognitive_dna(
        msg_id=str(msg.msg_id),
        glyph=msg.glyph,
        result=result,
        cognitive_dna={
            "processing_nodes": ["math-node", "validator-node"],
            "temporal_sequence": [
                {"node": "math-node", "ts": "2025-10-24T10:00:00.100Z"},
                {"node": "validator-node", "ts": "2025-10-24T10:00:00.142Z"}
            ],
            "causal_chain": [
                {"from": "query", "to": "math-node", "type": "TRIGGERS"},
                {"from": "math-node", "to": "validator-node", "type": "VALIDATES"}
            ],
            "guardian_validations": [
                {"node": "math-node", "decision": "approved"},
                {"node": "validator-node", "decision": "approved"}
            ]
        },
        fold_name="cognitive_session_20251024"
    )

    # Add DNA storage to trace
    result.trace["cognitive_dna_stored"] = True
    result.trace["fold_name"] = "cognitive_session_20251024"

    return result

# Retrieve cognitive DNA for analysis
dna_retrieved = retrieve_cognitive_dna(
    msg_id="550e8400-e29b-41d4-a716-446655440000",
    fold_name="cognitive_session_20251024"
)
```

### **3. Temporal & Causal Relationships**

**Purpose**: Track temporal sequence and causal relationships between cognitive operations

**Relationship Types:**
```python
from memory import TemporalLink, CausalLink, create_relationship

# Temporal relationships (time-based ordering)
temporal_link = TemporalLink(
    source_msg_id="550e8400-e29b-41d4-a716-446655440000",
    target_msg_id="660e9511-f30c-52e5-b827-557766551111",
    relationship="FOLLOWS",  # source FOLLOWS target
    timestamp="2025-10-24T10:00:00.200Z"
)

# Causal relationships (cause-effect)
causal_link = CausalLink(
    source_msg_id="550e8400-e29b-41d4-a716-446655440000",
    target_msg_id="660e9511-f30c-52e5-b827-557766551111",
    relationship="CAUSED_BY",  # source CAUSED_BY target
    confidence=0.95,
    reasoning="Math operation result triggered validation"
)

# Store relationships in memory fold
create_relationship(
    fold_name="cognitive_session_20251024",
    temporal_links=[temporal_link],
    causal_links=[causal_link]
)
```

**Relationship Graph:**
```
Cognitive DNA Relationship Graph:
    Query Input
        │
        ├─[TEMPORAL: FOLLOWS]─→ Math Processing
        └─[CAUSAL: TRIGGERS]──→ Math Processing
                                    │
                                    ├─[TEMPORAL: FOLLOWS]─→ Validation
                                    └─[CAUSAL: VALIDATES]──→ Validation
                                                                │
                                                                └─[TEMPORAL: FOLLOWS]─→ Decision
```

### **4. ΛiD-Scoped Memory Access**

**Purpose**: Identity-scoped memory access with ΛiD authentication

**Access Control:**
```python
from memory import access_memory_fold_with_lambda_id
from identity import lambda_id_authenticate

# ΛiD-authenticated memory access
def access_user_memory(lambda_id: str, fold_name: str):
    # Authenticate ΛiD
    auth_result = lambda_id_authenticate(
        lambda_id=lambda_id,
        credentials={"access_token": "bearer_xyz"},
        required_scopes=["memory:read"]
    )

    if not auth_result.success:
        raise PermissionError(f"ΛiD authentication failed: {auth_result.reason}")

    # Access memory fold with ΛiD scope
    memory_fold = access_memory_fold_with_lambda_id(
        fold_name=fold_name,
        lambda_id=lambda_id,
        access_mode="read"
    )

    # Retrieve results with ΛiD scope
    results = memory_fold.retrieve_results(
        filter_by_lambda_id=lambda_id,
        time_range={"start": "2025-10-24T00:00:00Z", "end": "2025-10-24T23:59:59Z"}
    )

    return results
```

**Scope Enforcement:**
- **USER scope**: Access own memory folds only
- **SERVICE scope**: Access service-specific memory folds
- **ADMIN scope**: Access all memory folds (Guardian-approved)

### **5. Sanctum Vault Protection**

**Purpose**: Encrypted memory storage with Sanctum Vault security

**Vault Integration:**
```python
from memory.sanctum import SanctumVault, encrypt_memory_fold

# Create Sanctum Vault for memory protection
vault = SanctumVault(
    vault_name="cognitive_memory_vault",
    encryption_key="vault_key_xyz",
    access_policy="strict"
)

# Store memory fold in Sanctum Vault
encrypted_fold = encrypt_memory_fold(
    fold=session_fold,
    vault=vault,
    encryption_method="AES-256-GCM"
)

# Retrieve from Sanctum Vault (requires authentication)
decrypted_fold = vault.retrieve_fold(
    fold_id=encrypted_fold.id,
    lambda_id="user_12345_lambda_xyz",
    decryption_key="vault_key_xyz"
)
```

**Sanctum Vault Features:**
- **Encryption at rest**: AES-256-GCM encryption
- **Access control**: ΛiD-based access with Guardian validation
- **Integrity validation**: Cryptographic checksums
- **Audit logging**: Complete access audit trail

---

## MATRIZ Memory Stage Integration

### **Memory Stage Processing Flow**

```
MATRIZ Pipeline:
MEMORY → Attention → Thought → Risk → Intent → Action
  M         A         T        R       I        A
  │
Trail ✦
Memory Fold
  │
┌─┴─────────────┐
│               │
Cognitive DNA   Temporal
Persistence     Relationships
```

### **MEMORY GLYPH Processing**

```python
from memory import MemoryProcessor, store_memory_glyph
from matriz.node_contract import MatrizMessage, MatrizResult, GLYPH

class MemoryProcessor(MatrizNode):
    """MATRIZ Memory stage processor with fold-based storage"""

    name = "memory-processor"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # 1. Validate MEMORY GLYPH
        if msg.glyph.kind != "MEMORY":
            return MatrizResult(
                ok=False,
                reasons=["MemoryProcessor only handles MEMORY GLYPH"],
                payload={},
                trace={},
                guardian_log=["Wrong GLYPH kind for MemoryProcessor"]
            )

        # 2. Extract fold context from GLYPH tags
        fold_name = msg.glyph.tags.get("fold_name", "default_session")
        lambda_id = msg.glyph.tags.get("lambda_id")

        # 3. Authenticate if ΛiD provided
        if lambda_id:
            auth_result = lambda_id_authenticate(
                lambda_id=lambda_id,
                credentials={"guardian_token": msg.guardian_token},
                required_scopes=["memory:write"]
            )

            if not auth_result.success:
                return MatrizResult(
                    ok=False,
                    reasons=["Memory write requires authentication"],
                    payload={},
                    trace={},
                    guardian_log=["ΛiD authentication failed"]
                )

        # 4. Access or create memory fold
        memory_fold = self.get_or_create_fold(
            fold_name=fold_name,
            lambda_id=lambda_id
        )

        # 5. Process MEMORY operation
        operation = msg.payload.get("operation")  # "store", "retrieve", "update"

        if operation == "store":
            result = self.store_memory(memory_fold, msg)
        elif operation == "retrieve":
            result = self.retrieve_memory(memory_fold, msg)
        elif operation == "update":
            result = self.update_memory(memory_fold, msg)
        else:
            return MatrizResult(
                ok=False,
                reasons=[f"Unknown memory operation: {operation}"],
                payload={},
                trace={},
                guardian_log=["Invalid operation"]
            )

        # 6. Store cognitive DNA for this operation
        store_cognitive_dna(
            msg_id=str(msg.msg_id),
            glyph=msg.glyph,
            result=result,
            cognitive_dna={
                "operation": operation,
                "fold_name": fold_name,
                "lambda_id": lambda_id
            },
            fold_name=fold_name
        )

        # 7. Add memory persistence to result
        result.guardian_log.append(f"Memory operation: {operation}")
        result.guardian_log.append(f"Fold: {fold_name}")
        result.trace["memory_fold"] = fold_name
        result.trace["cognitive_dna_stored"] = True

        return result
```

---

## Memory Fold Operations

### **1. Store Operation**

```python
from memory import store_in_fold

# Store MATRIZ result in memory fold
stored = store_in_fold(
    fold_name="cognitive_session_20251024",
    msg_id="550e8400-e29b-41d4-a716-446655440000",
    data={
        "glyph_kind": "MEMORY",
        "payload": {"key": "value"},
        "result": MatrizResult(...)
    },
    temporal_links=[...],
    causal_links=[...],
    ttl_hours=24  # Time-to-live: 24 hours
)
```

### **2. Retrieve Operation**

```python
from memory import retrieve_from_fold

# Retrieve by message ID
result = retrieve_from_fold(
    fold_name="cognitive_session_20251024",
    msg_id="550e8400-e29b-41d4-a716-446655440000"
)

# Retrieve by query
results = retrieve_from_fold(
    fold_name="cognitive_session_20251024",
    query={
        "glyph_kind": "MEMORY",
        "time_range": {"start": "2025-10-24T10:00:00Z", "end": "2025-10-24T11:00:00Z"},
        "lambda_id": "user_12345_lambda_xyz"
    },
    limit=100
)
```

### **3. Update Operation**

```python
from memory import update_in_fold

# Update existing memory entry
updated = update_in_fold(
    fold_name="cognitive_session_20251024",
    msg_id="550e8400-e29b-41d4-a716-446655440000",
    updates={
        "payload": {"key": "updated_value"},
        "metadata": {"updated_at": "2025-10-24T10:30:00Z"}
    }
)
```

### **4. Fold Compression & Archival**

```python
from memory import compress_fold, archive_fold

# Compress old fold to reduce storage
compressed = compress_fold(
    fold_name="cognitive_session_20251023",
    compression_algorithm="zstd",
    compression_level=9
)

# Archive to cold storage
archived = archive_fold(
    fold_name="cognitive_session_20251023",
    archive_location="s3://lukhas-memory-archive/2025/10/",
    delete_after_archive=True
)
```

---

## Constellation Framework Integration

### **Trail Star ✦ Coordination**

The Memory system (Trail Star) coordinates with other Constellation stars:

```
Memory Trail Star ✦
    │
    ├─→ Anchor Star ⚛️ (Identity)
    │   └─ ΛiD-scoped memory access
    │
    ├─→ Watch Star 🛡️ (Guardian)
    │   └─ Guardian audit trail persistence
    │
    ├─→ MATRIZ Memory Stage
    │   └─ Cognitive DNA storage
    │
    └─→ Consciousness
        └─ Memory-augmented consciousness
```

### **Memory-MATRIZ-Guardian Integration**

```python
from memory import store_with_guardian_audit
from guardian import emit_guardian_decision

# Store MATRIZ result with Guardian audit
def store_with_full_audit(msg: MatrizMessage, result: MatrizResult):
    # Guardian decision
    decision = emit_guardian_decision(
        operation="memory_storage",
        decision="approved",
        reason="Memory storage within limits",
        glyph_kind=msg.glyph.kind,
        msg_id=str(msg.msg_id),
        lane=msg.lane,
        metadata={"fold_name": "cognitive_session_20251024"}
    )

    # Store with Guardian audit
    stored = store_with_guardian_audit(
        fold_name="cognitive_session_20251024",
        msg_id=str(msg.msg_id),
        result=result,
        guardian_decision=decision,
        audit_trail={
            "guardian_decision_id": decision.id,
            "lambda_id": msg.glyph.tags.get("lambda_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    return stored
```

---

## Production Readiness

**Memory Module Status**: 75% production ready

### ✅ Completed

- [x] Fold-based memory hierarchy
- [x] Cognitive DNA persistence
- [x] Temporal and causal relationship tracking
- [x] ΛiD-scoped memory access
- [x] Sanctum Vault encryption
- [x] MATRIZ Memory stage integration
- [x] Guardian audit trail storage
- [x] Fold compression and archival
- [x] Complete provenance tracking

### 🔄 In Progress

- [ ] Distributed memory architecture
- [ ] Advanced query optimization
- [ ] Memory defragmentation
- [ ] Real-time replication

### 📋 Pending

- [ ] Comprehensive performance benchmarking
- [ ] Load testing for high-volume storage
- [ ] Disaster recovery procedures
- [ ] Enterprise backup strategies

**Performance Targets:**
- **Memory Access**: <100ms average working memory retrieval
- **Fold Operations**: <50ms for store/retrieve operations
- **Maximum Folds**: 1000 active folds per session
- **Compression**: 70% reduction for archived folds

---

## Related Documentation

### **Memory Contexts**
- [../matriz/lukhas_context.md](../matriz/lukhas_context.md:1) - MATRIZ cognitive engine
- [../matriz/core/memory_system.py](../matriz/core/memory_system.py:1) - CognitiveMemory implementation
- [../guardian/lukhas_context.md](../guardian/lukhas_context.md:1) - Guardian audit persistence
- [../identity/lukhas_context.md](../identity/lukhas_context.md:1) - ΛiD-scoped access

### **Technical Specifications**
- [../matriz/node_contract.py](../matriz/node_contract.py:1) - FROZEN v1.0.0 MatrizNode interface
- [../matriz/matriz_node_v1.json](../matriz/matriz_node_v1.json:1) - JSON Schema v1.1 (MEMORY GLYPH)
- [../audit/MATRIZ_READINESS.md](../audit/MATRIZ_READINESS.md:1) - Production readiness

### **Security Documentation**
- [../branding/MATRIZ_BRAND_GUIDE.md](../branding/MATRIZ_BRAND_GUIDE.md:1) - Official naming conventions
- [../security/lukhas_context.md](../security/lukhas_context.md:1) - Memory security architecture

---

**Memory Module**: Fold-based persistence & Sanctum Vault | **Trail Star**: ✦ Memory foundation
**Integration**: MATRIZ Memory stage | **Production**: 75% ready | **Tier**: T2
**Contract**: MEMORY GLYPH storage required | **Encryption**: AES-256-GCM at rest
