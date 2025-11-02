---
title: lukhas_context
slug: adapters.lukhas_context
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-24
constellation_stars: "⚛️ Anchor · 🛡️ Watch · ✦ Trail"
related_modules: "bio_adapter, governance_adapter, creative_adapter, bridge_adapter, memory_adapter"
manifests: "../node_contract.py, ../matriz_node_v1.json"
links: "bio_adapter.py, governance_adapter.py, creative_adapter.py, bridge_adapter.py"
contracts: "[MatrizNode, BioAdapter, GovernanceAdapter, MatrizMessage, MatrizResult]"
domain: integration
stars: "[Skill]"
status: active
tier: T2
updated: 2025-10-24
version: 1.0.0
contract_version: 1.0.0
type: documentation
---
# MATRIZ Adapters Module
## MatrizNode Adapters for External Service Integration & Specialized Processing

*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

**Module**: matriz/adapters
**Purpose**: MatrizNode-based adapters for external service integrations and specialized cognitive processing
**Lane**: L2 (Integration) + Labs (Experimental)
**Language**: Python
**Contract**: Implements FROZEN v1.0.0 [node_contract.py](../node_contract.py:1) MatrizNode interface
**Last Updated**: 2025-10-24

---

## Module Overview

The MATRIZ adapters module provides **MatrizNode-based adapters** that bridge MATRIZ cognitive processing with external services, specialized domains, and LUKHAS subsystems. All adapters implement the [node_contract.py](../node_contract.py:190) MatrizNode interface with complete Guardian system integration.

### Key MATRIZ Adapter Components

#### **Specialized Cognitive Adapters** (MatrizNode implementations)
- **BioAdapter** ([bio_adapter.py:1](bio_adapter.py:1)): MatrizNode for biological pattern processing
- **GovernanceAdapter** ([governance_adapter.py:1](governance_adapter.py:1)): MatrizNode for ethics and governance validation
- **CreativeAdapter** ([creative_adapter.py:1](creative_adapter.py:1)): MatrizNode for creative generation with bounds
- **BridgeAdapter** ([bridge_adapter.py:1](bridge_adapter.py:1)): MatrizNode for cross-system communication
- **MemoryAdapter** ([memory_adapter.py:1](memory_adapter.py:1)): MatrizNode for memory fold operations

#### **Legacy Integration Adapters**
- **ServiceAdapter** (ABC): Base class for external service adapters (legacy L2)
- **Cloud Consolidation Service**: Unified cloud storage management
- **Gmail Headers Adapter**: Email metadata access with privacy protection
- **Google Drive Adapter**: Drive file and folder management
- **Dropbox Adapter**: Dropbox integration with metadata-first approach

### MATRIZ Adapter Contract

All MATRIZ adapters implement [MatrizNode](../node_contract.py:190) with:

1. **MatrizMessage Input**: Process GLYPH-identified messages with topic and payload
2. **MatrizResult Output**: Return ok, reasons, payload, trace, and guardian_log
3. **Deterministic Processing**: Identical inputs produce identical outputs
4. **Guardian Integration**: All operations validated by Guardian system
5. **Complete Provenance**: Full trace of processing with cognitive DNA

---

## Architecture

### Base Adapter Interface

```python
from adapters import ServiceAdapter, ResourceMetadata, ResourceContent

class ServiceAdapter(ABC):
    """Base adapter with capability validation"""

    @abstractmethod
    async def list_resources(self, parent_id: Optional[str]) -> list[ResourceMetadata]:
        """List resources (metadata only)"""

    @abstractmethod
    async def get_content(self, resource_id: str) -> ResourceContent:
        """Get resource content (requires content-level capability)"""
```

### Data Models

**ResourceMetadata**: Standard metadata structure
- id, name, type, size, timestamps
- owner, sharing permissions, tags
- parent_id, mime_type, url

**ResourceContent**: Content structure (requires elevated capabilities)
- metadata: ResourceMetadata
- content: bytes (raw data)
- encoding, content_type

**SearchQuery**: Common search interface
- query: str
- filters: dict
- limit, offset for pagination

---

## Available Adapters

### 1. Gmail Headers Adapter
**Location**: `adapters/gmail_headers/`
**Purpose**: Email metadata access with privacy protection
**Capabilities**: Read email headers without content access
**Security**: Metadata-only, no email body access by default

```python
from adapters.gmail_headers import GmailHeadersAdapter

adapter = GmailHeadersAdapter(capability_token)
headers = await adapter.list_resources()  # Email metadata only
```

### 2. Google Drive Adapter
**Location**: `adapters/drive/`
**Purpose**: Google Drive file and folder management
**Capabilities**: List, search, metadata access, content download (escalated)

```python
from adapters.drive import GoogleDriveAdapter

adapter = GoogleDriveAdapter(capability_token)
files = await adapter.list_resources(parent_id="root")
content = await adapter.get_content(file_id)  # Requires content capability
```

### 3. Dropbox Adapter
**Location**: `adapters/dropbox/`
**Purpose**: Dropbox integration with metadata-first approach
**Capabilities**: File listing, metadata, content access (escalated)

```python
from adapters.dropbox import DropboxAdapter

adapter = DropboxAdapter(capability_token)
files = await adapter.list_resources()
```

### 4. Cloud Consolidation Service
**Location**: `adapters/cloud_consolidation.py`
**Purpose**: Unified cloud storage management across providers
**Features**: Duplicate detection, consolidation planning, cross-cloud operations

**Entrypoints**:
- `CloudConsolidationService`
- `ConsolidationPlan`
- `ConsolidationRequest`
- `ConsolidationResponse`
- `DuplicateGroup`
- `ExecutePlanRequest`

```python
from adapters.cloud_consolidation import CloudConsolidationService

service = CloudConsolidationService()
plan = await service.analyze_duplicates()
response = await service.execute_plan(plan)
```

---

## Security & Compliance

### Capability Token System
- All operations require valid capability tokens
- Scopes: `metadata:read`, `content:read`, `write`, `delete`
- Tokens validated before any external API calls
- Automatic token refresh and expiry handling

### Privacy Protection
- **Metadata-First**: Default operations use metadata only
- **Content Escalation**: Explicit capability required for content access
- **Audit Logging**: All operations logged with user, timestamp, resource
- **Guardian Integration**: Ethics validation for sensitive operations

### Constellation Framework Integration
- **⚛️ Anchor Star (Identity)**: OAuth2 token management with ΛID
- **🛡️ Watch Star (Guardian)**: Capability validation and ethics checks
- **✦ Trail Star (Memory)**: Audit trail storage in memory folds

---

## Technical Details

### Runtime Configuration (from manifest)
- **Language**: Python
- **Lane**: L2 (Integration)
- **Team**: Core
- **Code Owners**: @lukhas-core

### Module Entrypoints
```python
from adapters import (
    ServiceAdapter,           # Base adapter interface
    OperationResult,         # Operation result wrapper
    ResourceContent,         # Content with metadata
    ResourceMetadata,        # Resource metadata
    SearchQuery,             # Search query structure
    WatchRequest,            # Watch/subscribe request
)

from adapters.cloud_consolidation import (
    CloudConsolidationService,
    ConsolidationPlan,
    ConsolidationRequest,
    ConsolidationResponse,
    DuplicateGroup,
    ExecutePlanRequest,
)
```

### Module Structure
```
adapters/
├── __init__.py                    # Base adapter interfaces
├── cloud_consolidation.py         # Cloud consolidation service
├── gmail_headers/                 # Gmail adapter
│   └── __init__.py
├── drive/                         # Google Drive adapter
│   └── __init__.py
├── dropbox/                       # Dropbox adapter
│   └── __init__.py
├── config/                        # Configuration
│   ├── config.yaml
│   ├── environment.yaml
│   └── logging.yaml
├── docs/                          # Documentation
│   ├── README.md
│   ├── api.md
│   ├── architecture.md
│   └── troubleshooting.md
└── tests/                         # Test suites
    ├── conftest.py
    ├── test_adapters_unit.py
    └── test_adapters_integration.py
```

---

## Development Guidelines

### 1. Adding New Adapters
```python
from adapters import ServiceAdapter, ResourceMetadata

class MyServiceAdapter(ServiceAdapter):
    def __init__(self, capability_token: str):
        self._validate_token(capability_token)
        super().__init__()

    async def list_resources(self, parent_id: Optional[str]) -> list[ResourceMetadata]:
        # Implement metadata listing
        pass

    async def get_content(self, resource_id: str) -> ResourceContent:
        # Require content capability
        self._require_capability("content:read")
        # Fetch and return content
        pass
```

### 2. Capability Validation
- Always validate tokens before external calls
- Use `_require_capability(scope)` for privileged operations
- Log all capability checks for audit trail

### 3. Error Handling
- Graceful degradation for network failures
- Clear error messages for capability denials
- Retry logic with exponential backoff

### 4. Testing
- Unit tests: Mock external APIs, test adapter logic
- Integration tests: Test against real services (with test accounts)
- Security tests: Verify capability enforcement

---

## Performance & Quality

### Performance Targets
- **Metadata Operations**: <500ms p95
- **Content Operations**: <2s p95 (dependent on content size)
- **Caching**: Metadata cached for 5 minutes
- **Batch Operations**: Support for bulk metadata retrieval

### Quality Gates (L2 Lane)
- ✅ Capability token validation for all operations
- ✅ Complete audit trail logging
- ✅ Unit and integration test coverage
- ✅ Security scanning and vulnerability checks
- ✅ Documentation completeness

---

## Documentation

- **README**: [adapters/docs/README.md](docs/README.md)
- **API Reference**: [adapters/docs/api.md](docs/api.md)
- **Architecture**: [adapters/docs/architecture.md](docs/architecture.md)
- **Troubleshooting**: [adapters/docs/troubleshooting.md](docs/troubleshooting.md)
- **Tests**: [adapters/tests/README.md](tests/README.md)
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#adapters)

---

## Related Modules

- **Identity** ([../identity/](../identity/)) - OAuth2 token management
- **Governance** ([../governance/](../governance/)) - Capability validation and ethics
- **Orchestration** ([../orchestration/](../orchestration/)) - Multi-adapter workflows
- **Security** ([../security/](../security/)) - Security policies and audit

## 🔒 MATRIZ Adapter Implementation

### **Implementing a MatrizNode Adapter**

```python
from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult, GLYPH
from uuid import uuid4
from datetime import datetime

class MyMatrizAdapter(MatrizNode):
    """Custom MATRIZ adapter implementing MatrizNode contract"""

    name = "my-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        """
        Process MATRIZ message with complete trace and audit

        Args:
            msg: MatrizMessage with GLYPH identity, topic, and payload

        Returns:
            MatrizResult with ok, reasons, payload, trace, guardian_log
        """
        # Extract payload
        input_data = msg.payload.get("data")

        # Process with your adapter logic
        result_data = self.process(input_data)

        # Return MatrizResult with complete trace
        return MatrizResult(
            ok=True,
            reasons=[f"Processed by {self.name} v{self.version}"],
            payload={"result": result_data},
            trace={
                "node": self.name,
                "msg_id": str(msg.msg_id),
                "glyph_kind": msg.glyph.kind,
                "processing_time_ms": 42
            },
            guardian_log=[
                f"Guardian validated {self.name} operation",
                f"Topic: {msg.topic}, Lane: {msg.lane}"
            ]
        )

    def process(self, data):
        """Your adapter-specific processing logic"""
        return f"processed: {data}"
```

### **MATRIZ Adapter Patterns**

#### **BioAdapter Pattern** - Biological Processing
Implements biological pattern recognition and bio-inspired algorithms:
- Processes biological data through MATRIZ cognitive pipeline
- Integrates with CANDIDATE BioHub for quantum-bio processing
- Returns biological insights with complete cognitive DNA trace

#### **GovernanceAdapter Pattern** - Ethics Validation
Ensures ethical compliance and governance constraints:
- Validates operations against Constitutional AI principles
- Integrates with Guardian system for privileged operation approval
- Provides ethics reasoning traces for auditability

#### **CreativeAdapter Pattern** - Bounded Creativity
Manages creative generation within safety bounds:
- Controls randomness and novelty within defined constraints
- Tracks creative process provenance for reproducibility
- Integrates with attention mechanisms for relevance filtering

#### **BridgeAdapter Pattern** - Cross-System Integration
Bridges MATRIZ with external systems and services:
- Translates between MATRIZ messages and external APIs
- Maintains complete audit trail across system boundaries
- Handles protocol conversion and data transformation

#### **MemoryAdapter Pattern** - Memory Fold Operations
Coordinates with LUKHAS memory fold system:
- Synchronizes MATRIZ cognitive state with memory folds
- Manages temporal and causal relationship persistence
- Enables memory-augmented cognitive processing

## 📊 Production Readiness

**Adapters Module Status**: 65% production ready

### ✅ Completed
- [x] 10+ MatrizNode adapter implementations
- [x] Frozen contract v1.0.0 compliance
- [x] Guardian system integration hooks
- [x] Complete provenance tracking
- [x] Legacy ServiceAdapter bridge maintained
- [x] Documentation and examples

### 🔄 In Progress
- [ ] Performance optimization for high-throughput adapters
- [ ] Advanced adapter composition patterns
- [ ] Distributed adapter orchestration

### 📋 Pending
- [ ] Production deployment configurations
- [ ] Enterprise adapter library expansion
- [ ] Security audit for all adapters

## 📖 Related Documentation

### **MATRIZ Adapter Contexts**
- [../lukhas_context.md](../lukhas_context.md:1) - MATRIZ cognitive engine overview
- [../core/lukhas_context.md](../core/lukhas_context.md:1) - Core node architecture
- [../visualization/lukhas_context.md](../visualization/lukhas_context.md:1) - Visualization systems

### **Technical Specifications**
- [../node_contract.py](../node_contract.py:1) - FROZEN v1.0.0 canonical interface
- [../matriz_node_v1.json](../matriz_node_v1.json:1) - JSON Schema v1.1
- [../the_plan.md](../the_plan.md:1) - Implementation plan

### **Integration Documentation**
- [../../branding/MATRIZ_BRAND_GUIDE.md](../../branding/MATRIZ_BRAND_GUIDE.md:1) - Official naming conventions
- [../../audit/MATRIZ_READINESS.md](../../audit/MATRIZ_READINESS.md:1) - Production readiness

---

**Status**: Integration Lane (L2) + Labs (Experimental)
**Contract**: v1.0.0 (FROZEN MatrizNode)
**Adapters**: 10+ specialized MatrizNode implementations
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Production**: 65% ready
**Last Updated**: 2025-10-24
