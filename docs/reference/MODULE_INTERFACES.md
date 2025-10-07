---
status: wip
type: documentation
owner: unknown
module: reference
redirect: false
moved_to: null
---

# 📚 LUKHAS  Module Interfaces & Contracts

## Overview

This document defines the interfaces and contracts between LUKHAS  modules, establishing clear boundaries and communication protocols for the system's components.

## Table of Contents

1. [Core Module Interfaces](#core-module-interfaces)
2. [Memory System Interfaces](#memory-system-interfaces)
3. [Consciousness Interfaces](#consciousness-interfaces)
4. [Guardian System Interfaces](#guardian-system-interfaces)
5. [Communication Protocols](#communication-protocols)
6. [Dependency Injection](#dependency-injection)
7. [Error Handling Contracts](#error-handling-contracts)
8. [Performance Contracts](#performance-contracts)

---

## Core Module Interfaces

### 🔌 CoreInterface

The base interface that all core modules must implement:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.common import GLYPHToken

class CoreInterface(ABC):
    """Abstract interface for core modules"""

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data through the module.

        Args:
            data: Input data dictionary

        Returns:
            Dict[str, Any]: Processed output

        Raises:
            ValidationError: If input data is invalid
            ProcessingError: If processing fails
        """
        pass

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """
        Handle GLYPH token communication.

        Args:
            token: Input GLYPH token

        Returns:
            GLYPHToken: Response token
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get module status.

        Returns:
            Dict containing:
            - operational: bool
            - health_score: float (0.0-1.0)
            - last_update: timestamp
            - metrics: Dict[str, Any]
        """
        pass
```

### 🎯 Contract Requirements

1. **Initialization**: All modules must be initializable with minimal configuration
2. **Async-First**: All operations must be async-compatible
3. **GLYPH Support**: Must handle GLYPH token communication
4. **Status Reporting**: Must provide real-time status information
5. **Error Handling**: Must use standard exception hierarchy

---

## Memory System Interfaces

### 🧠 MemoryInterface

```python
from enum import Enum

class MemoryType(Enum):
    """Memory type enumeration"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"

class MemoryInterface(ABC):
    """Abstract interface for memory modules"""

    @abstractmethod
    async def store(self,
                   data: Any,
                   memory_type: MemoryType,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store data in memory.

        Args:
            data: Data to store
            memory_type: Type of memory
            metadata: Optional metadata

        Returns:
            str: Memory ID for retrieval

        Contract:
            - Must return unique ID
            - Must preserve data integrity
            - Must handle concurrent access
        """
        pass

    @abstractmethod
    async def retrieve(self,
                      memory_id: str,
                      include_metadata: bool = True) -> Dict[str, Any]:
        """
        Retrieve data from memory.

        Args:
            memory_id: ID of memory to retrieve
            include_metadata: Whether to include metadata

        Returns:
            Dict containing data and optional metadata

        Raises:
            MemoryNotFoundError: If memory_id doesn't exist
        """
        pass

    @abstractmethod
    async def search(self,
                    query: Dict[str, Any],
                    memory_type: Optional[MemoryType] = None,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by criteria.

        Args:
            query: Search criteria
            memory_type: Optional filter by type
            limit: Maximum results

        Returns:
            List of matching memories
        """
        pass
```

### 🧬 DNA Helix Memory Contract

```python
class DNAHelixInterface(MemoryInterface):
    """DNA Helix memory specific interface"""

    @abstractmethod
    async def calculate_drift(self, memory_id: str) -> float:
        """
        Calculate drift from origin.

        Returns:
            float: Drift score (0.0 = no drift, 1.0 = maximum drift)
        """
        pass

    @abstractmethod
    async def repair_memory(self, memory_id: str) -> bool:
        """
        Repair drifted memory.

        Returns:
            bool: True if repair successful
        """
        pass
```

---

## Consciousness Interfaces

### 🧠 ConsciousnessInterface

```python
class ConsciousnessInterface(ABC):
    """Abstract interface for consciousness modules"""

    @abstractmethod
    async def assess_awareness(self,
                             stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess awareness level for given stimulus.

        Args:
            stimulus: Input stimulus

        Returns:
            Dict containing:
            - awareness_level: float (0.0-1.0)
            - attention_focus: List[str]
            - emotional_state: Dict[str, float]
        """
        pass

    @abstractmethod
    async def make_decision(self,
                          scenario: Dict[str, Any],
                          options: List[str],
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a conscious decision.

        Args:
            scenario: Decision scenario
            options: Available options
            context: Optional context

        Returns:
            Dict containing:
            - decision: str (selected option)
            - confidence: float (0.0-1.0)
            - reasoning: List[str]
            - alternatives: List[Dict[str, float]]

        Contract:
            - Must validate all options
            - Must provide reasoning
            - Must consider ethical implications
        """
        pass

    @abstractmethod
    async def reflect(self,
                     experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on experience for learning.

        Args:
            experience: Experience to reflect on

        Returns:
            Dict containing insights and learnings
        """
        pass
```

---

## Guardian System Interfaces

### 🛡️ GuardianInterface

```python
class GuardianInterface(ABC):
    """Abstract interface for Guardian ethical system"""

    @abstractmethod
    async def validate_action(self,
                            action: Dict[str, Any],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate action against ethical framework.

        Args:
            action: Proposed action
            context: Action context

        Returns:
            Dict containing:
            - approved: bool
            - risk_level: str (low, medium, high, critical)
            - constraints: List[str]
            - reasoning: Dict[str, Any]

        Contract:
            - Must evaluate all ethical dimensions
            - Must provide clear reasoning
            - Must enforce safety constraints
        """
        pass

    @abstractmethod
    async def detect_drift(self,
                         behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect behavioral drift.

        Args:
            behavioral_data: Recent behavior patterns

        Returns:
            Dict containing:
            - drift_detected: bool
            - drift_score: float (0.0-1.0)
            - drift_type: str
            - remediation_actions: List[str]
        """
        pass
```

---

## Communication Protocols

### 📡 GLYPH Token Protocol

All inter-module communication uses GLYPH tokens:

```python
@dataclass
class GLYPHToken:
    """Standard GLYPH token for communication"""
    glyph_id: str
    symbol: GLYPHSymbol
    source: str
    target: str
    payload: Dict[str, Any]
    context: GLYPHContext
    priority: MessagePriority
    metadata: Dict[str, Any]

    def validate(self) -> bool:
        """Validate token integrity"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GLYPHToken':
        """Deserialize from dictionary"""
        pass
```

### 📬 Message Priority Contract

```python
class MessagePriority(Enum):
    LOW = "low"        # Can be processed async
    NORMAL = "normal"  # Standard processing
    HIGH = "high"      # Priority processing
    URGENT = "urgent"  # Immediate processing required
```

---

## Dependency Injection

### 💉 Service Registration Contract

All modules must register with the dependency injection system:

```python
from core.interfaces.dependency_injection import register_service

# Module registration example
class MyModule(CoreInterface):
    def __init__(self):
        # Initialize module
        pass

    async def initialize(self):
        """Async initialization"""
        # Register with DI system
        register_service("my_module", self, singleton=True)
```

### 🔗 Service Discovery Contract

```python
from core.interfaces.dependency_injection import get_service, inject

# Direct service access
memory_service = get_service("memory_service")

# Decorator-based injection
@inject(service_name="memory_service")
async def process_data(data: Dict[str, Any], memory_service=None):
    """Process data with injected memory service"""
    result = await memory_service.store(data, MemoryType.EPISODIC)
    return result
```

---

## Error Handling Contracts

### ⚠️ Exception Hierarchy

All modules must use the standard exception hierarchy:

```python
class LukhasError(Exception):
    """Base exception for all LUKHAS errors"""
    pass

class ValidationError(LukhasError):
    """Input validation errors"""
    pass

class ProcessingError(LukhasError):
    """Processing errors"""
    pass

class MemoryError(LukhasError):
    """Memory system errors"""
    pass

class GuardianViolation(LukhasError):
    """Ethical constraint violations"""
    pass
```

### 🔄 Retry Contract

Modules must implement retry logic for transient failures:

```python
@retry(max_attempts=3, backoff_factor=2.0)
async def resilient_operation():
    """Operation with automatic retry"""
    pass
```

---

## Performance Contracts

### ⚡ Response Time Requirements

| Operation Type | Maximum Response Time | Notes |
|---------------|----------------------|-------|
| GLYPH Token Processing | 100ms | Per token |
| Memory Store | 200ms | Including validation |
| Memory Retrieve | 150ms | From cache |
| Decision Making | 500ms | Simple decisions |
| Guardian Validation | 300ms | Standard validation |
| Consciousness Assessment | 400ms | Basic awareness |

### 📊 Scalability Requirements

1. **Concurrent Operations**: Support 1000+ concurrent requests
2. **Memory Efficiency**: Use no more than 100MB per module baseline
3. **CPU Efficiency**: Utilize async/await for I/O operations
4. **Batch Processing**: Support batch operations where applicable

### 🔍 Monitoring Contract

All modules must expose metrics:

```python
class ModuleMetrics:
    """Standard metrics interface"""

    @property
    def operations_per_second(self) -> float:
        """Current throughput"""
        pass

    @property
    def average_latency_ms(self) -> float:
        """Average operation latency"""
        pass

    @property
    def error_rate(self) -> float:
        """Error rate (0.0-1.0)"""
        pass

    @property
    def memory_usage_mb(self) -> float:
        """Current memory usage"""
        pass
```

---

## Module Interaction Patterns

### 🔄 Request-Response Pattern

```python
# Standard request-response
request = GLYPHToken(
    symbol=GLYPHSymbol.QUERY,
    source="module_a",
    target="module_b",
    payload={"query": "status"}
)

response = await module_b.handle_glyph(request)
```

### 📢 Publish-Subscribe Pattern

```python
# Event publication
event = GLYPHToken(
    symbol=GLYPHSymbol.EVENT,
    source="module_a",
    target="*",  # Broadcast
    payload={"event_type": "state_change"}
)

await event_bus.publish(event)
```

### 🔗 Chain of Responsibility

```python
# Processing chain
token = GLYPHToken(...)

# Process through chain
for module in processing_chain:
    token = await module.handle_glyph(token)
    if token.metadata.get("stop_processing"):
        break
```

---

## Best Practices

1. **Interface Segregation**: Keep interfaces focused and minimal
2. **Dependency Inversion**: Depend on abstractions, not implementations
3. **Single Responsibility**: Each module should have one clear purpose
4. **Open/Closed**: Open for extension, closed for modification
5. **Liskov Substitution**: Implementations must be substitutable

---

## Version Compatibility

- **Interface Version**: 1.0.0
- **Minimum Python**: 3.8+
- **Async Runtime**: asyncio
- **Serialization**: JSON/MessagePack

---

## Migration Guide

For modules upgrading to these interfaces:

1. Implement required abstract methods
2. Register with dependency injection
3. Update error handling to use standard exceptions
4. Add metrics exposure
5. Validate performance contracts

---

*Last Updated: 2025-08-03*
