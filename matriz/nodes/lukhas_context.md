---
title: lukhas_context
slug: nodes.lukhas_context
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-24
constellation_stars: "⚛️ Anchor · ✦ Trail · 🔬 Horizon · 🛡️ Watch"
related_modules: "fact_node, validator_node, math_node"
manifests: "../node_contract.py, ../matriz_node_v1.json"
links: "fact_node.py, validator_node.py, math_node.py"
contracts: "[MatrizNode, FactNode, ValidatorNode, MathNode]"
domain: reasoning
stars: "[Skill]"
status: active
tier: T2
updated: 2025-10-24
version: 1.0.0
contract_version: 1.0.0
---
# MATRIZ Specialized Nodes
## Domain-Specific Cognitive Processing Nodes

### Nodes Module Overview

**Nodes Module Location**: [matriz/nodes/](../nodes/)

- **Purpose**: Specialized MatrizNode implementations for domain-specific cognitive processing
- **Architecture**: Concrete node implementations extending CognitiveNode base class
- **Integration**: Pluggable nodes for MATRIZ orchestrator with dynamic registration
- **Contract**: All nodes implement FROZEN v1.0.0 [node_contract.py](../node_contract.py:190) interface

## Core Specialized Nodes

### **MathNode** ([math_node.py:1](math_node.py:1))

**Purpose**: Mathematical and arithmetic operations with complete reasoning traces

**Capabilities:**
- Arithmetic operations (add, subtract, multiply, divide)
- Algebraic equation solving with step-by-step traces
- Formula processing with symbolic manipulation
- Mathematical reasoning provenance tracking

**MatrizMessage Processing:**
```python
# Input MatrizMessage
{
    "glyph": {"kind": "DECISION", "id": "..."},
    "topic": "TREND",
    "payload": {
        "operation": "add",
        "operands": [5, 3]
    }
}

# Output MatrizResult
{
    "ok": True,
    "reasons": ["Addition computed successfully"],
    "payload": {"result": 8, "steps": ["5 + 3 = 8"]},
    "trace": {"node": "math-node", "operation": "add", "ms": 2},
    "guardian_log": ["Mathematical operation validated"]
}
```

**Integration Points:**
- **THOUGHT Stage**: Symbolic reasoning and formula processing
- **Guardian System**: Validates mathematical constraints and bounds
- **Provenance**: Complete calculation trace with intermediate steps

### **FactNode** ([fact_node.py:1](fact_node.py:1))

**Purpose**: Knowledge base operations with semantic linking

**Capabilities:**
- Knowledge retrieval from structured data stores
- Semantic relationship mapping and traversal
- Fact validation with confidence scoring
- Knowledge graph construction and querying

**MatrizMessage Processing:**
```python
# Input MatrizMessage
{
    "glyph": {"kind": "MEMORY", "id": "..."},
    "topic": "RESOURCE",
    "payload": {
        "query": "capital of France",
        "context": "geography"
    }
}

# Output MatrizResult
{
    "ok": True,
    "reasons": ["Fact retrieved with high confidence"],
    "payload": {
        "fact": "Paris",
        "confidence": 0.99,
        "sources": ["knowledge_graph"],
        "related": ["France", "European capitals"]
    },
    "trace": {"node": "fact-node", "query_type": "semantic", "ms": 15},
    "guardian_log": ["Knowledge retrieval validated", "Sources verified"]
}
```

**Integration Points:**
- **MEMORY Stage**: Knowledge persistence and retrieval
- **ATTENTION Stage**: Relevance scoring and semantic focusing
- **Guardian System**: Source verification and truth validation

### **ValidatorNode** ([validator_node.py:1](validator_node.py:1))

**Purpose**: Rule-based validation with reasoning explanation

**Capabilities:**
- Logical constraint verification
- Rule-based validation with explanation generation
- Quality assurance with improvement suggestions
- Compliance checking against defined policies

**MatrizMessage Processing:**
```python
# Input MatrizMessage
{
    "glyph": {"kind": "DECISION", "id": "..."},
    "topic": "CONTRADICTION",
    "payload": {
        "data": {"age": 25, "is_adult": False},
        "rules": ["age >= 18 implies is_adult"]
    }
}

# Output MatrizResult
{
    "ok": False,
    "reasons": [
        "Contradiction detected",
        "Rule violated: age >= 18 implies is_adult",
        "Expected is_adult=True for age=25"
    ],
    "payload": {
        "valid": False,
        "violations": [{"rule": 0, "reason": "logical_contradiction"}],
        "suggestions": ["Set is_adult to True"]
    },
    "trace": {"node": "validator-node", "rules_checked": 1, "ms": 5},
    "guardian_log": ["Validation rules applied", "Contradictions identified"]
}
```

**Integration Points:**
- **RISK Stage**: Validates safety and correctness constraints
- **Guardian System**: Enforces Constitutional AI principles
- **THOUGHT Stage**: Provides reasoning for validation failures

## Node Development Patterns

### **Creating a Custom MatrizNode**

```python
from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult

class MyCustomNode(MatrizNode):
    """Custom cognitive processing node"""

    name = "my-custom-node"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        """
        Process MATRIZ message with domain-specific logic

        Args:
            msg: MatrizMessage with GLYPH identity, topic, and payload

        Returns:
            MatrizResult with complete trace and audit
        """
        # 1. Extract payload
        input_data = msg.payload.get("data")

        # 2. Validate with Guardian
        if not self.validate_input(input_data):
            return MatrizResult(
                ok=False,
                reasons=["Input validation failed"],
                payload={},
                trace={"node": self.name},
                guardian_log=["Guardian rejected invalid input"]
            )

        # 3. Process with domain-specific logic
        result = self.process(input_data)

        # 4. Return with complete trace
        return MatrizResult(
            ok=True,
            reasons=[f"Processed by {self.name}"],
            payload={"result": result},
            trace={
                "node": self.name,
                "msg_id": str(msg.msg_id),
                "glyph_kind": msg.glyph.kind,
                "processing_ms": 10
            },
            guardian_log=[
                f"Guardian validated {self.name}",
                f"Topic: {msg.topic}, Lane: {msg.lane}"
            ]
        )

    def validate_input(self, data) -> bool:
        """Validate input with Guardian system"""
        return data is not None

    def process(self, data):
        """Domain-specific processing logic"""
        return f"processed: {data}"
```

### **Node Registration**

Nodes are dynamically registered with the CognitiveOrchestrator:

```python
from matriz.core import CognitiveOrchestrator
from matriz.nodes import MathNode, FactNode, ValidatorNode

# Create orchestrator
orchestrator = CognitiveOrchestrator()

# Register specialized nodes
orchestrator.register_node(MathNode())
orchestrator.register_node(FactNode())
orchestrator.register_node(ValidatorNode())

# Node capabilities are automatically discovered
# Orchestrator routes messages based on GLYPH kind and topic
```

## Node Capabilities & Routing

### **Capability Declaration**

Each node declares its capabilities for automatic routing:

- **MathNode**: Handles `DECISION` GLYPH with mathematical payloads
- **FactNode**: Handles `MEMORY` and `CONTEXT` GLYPH with knowledge queries
- **ValidatorNode**: Handles `DECISION` GLYPH with validation rules

### **Topic-Based Routing**

Nodes can specify topic preferences:
- **CONTRADICTION**: ValidatorNode for constraint violations
- **RESOURCE**: FactNode for knowledge retrieval
- **TREND**: MathNode for statistical analysis
- **BREAKTHROUGH**: Creative nodes for novel insights

## Performance & Quality

### **Performance Targets**

- **Processing Latency**: <50ms p95 per node
- **Throughput**: 1000+ messages per second per node
- **Memory Efficiency**: <10MB per active node instance
- **Concurrent Nodes**: Support 100+ active nodes

### **Quality Standards**

- **Deterministic Processing**: Identical inputs produce identical outputs
- **Complete Provenance**: Full trace from input to output
- **Guardian Integration**: All operations validated
- **Error Handling**: Graceful degradation with informative error messages

## Production Readiness

**Nodes Module Status**: 70% production ready

### ✅ Completed

- [x] MathNode with arithmetic and algebraic operations
- [x] FactNode with knowledge graph integration
- [x] ValidatorNode with rule-based validation
- [x] Frozen contract v1.0.0 compliance
- [x] Dynamic registration system
- [x] Complete provenance tracking
- [x] Guardian system integration
- [x] Comprehensive unit tests

### 🔄 In Progress

- [ ] Advanced reasoning nodes (meta-cognitive capabilities)
- [ ] Distributed node processing for horizontal scaling
- [ ] Performance optimization for high-throughput scenarios

### 📋 Pending

- [ ] Production deployment configurations
- [ ] Enterprise node library expansion
- [ ] Security audit for all nodes
- [ ] Load testing and benchmarking

## Related Documentation

### **Node Contexts**

- [../lukhas_context.md](../lukhas_context.md:1) - MATRIZ cognitive engine overview
- [../core/lukhas_context.md](../core/lukhas_context.md:1) - Core orchestration and node interface
- [../adapters/lukhas_context.md](../adapters/lukhas_context.md:1) - Adapter integration patterns
- [../visualization/lukhas_context.md](../visualization/lukhas_context.md:1) - Node visualization

### **Technical Specifications**

- [../node_contract.py](../node_contract.py:1) - FROZEN v1.0.0 canonical interface
- [../matriz_node_v1.json](../matriz_node_v1.json:1) - JSON Schema v1.1 (node types)
- [../the_plan.md](../the_plan.md:1) - Implementation plan
- [../MATRIZ_AGENT_BRIEF.md](../MATRIZ_AGENT_BRIEF.md:1) - Agent contracts & KPIs

### **Integration Documentation**

- [../../audit/MATRIZ_READINESS.md](../../audit/MATRIZ_READINESS.md:1) - Production readiness
- [../../branding/MATRIZ_BRAND_GUIDE.md](../../branding/MATRIZ_BRAND_GUIDE.md:1) - Naming conventions

---

**Nodes Module**: Specialized cognitive processing | **Contract**: v1.0.0 (FROZEN MatrizNode)
**Nodes**: MathNode, FactNode, ValidatorNode | **Production**: 70% ready
**Performance**: <50ms p95 per node | **Scale**: 100+ concurrent nodes supported
