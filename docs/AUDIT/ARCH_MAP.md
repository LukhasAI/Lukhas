# LUKHAS AI Architecture Component Map

## Overview
This document maps all major components, services, and modules within the LUKHAS AI system, their locations, purposes, and inter-dependencies.

## Python Core Components

### Main System Entry Points
| Component | Path | Purpose | Dependencies |
|-----------|------|---------|-------------|
| **Main System** | `main.py` | Primary system controller with bootstrap | `core.bootstrap`, async services |
| **Symbolic API** | `symbolic_api.py` | Core symbolic interface server | `core.symbolic`, FastAPI |
| **Drift Audit** | `real_gpt_drift_audit.py` | GPT drift monitoring system | OpenAI API, governance |

### Core Infrastructure (`core/`)
| Component | Path | Purpose | Inbound Deps | Outbound Deps |
|-----------|------|---------|--------------|---------------|
| **GLYPH Engine** | `core/symbolic/` | Symbolic processing & graph systems | All modules | Memory, Governance |
| **Actor System** | `core/actor_system.py` | Multi-agent coordination | Orchestration | All modules |
| **Event Bus** | `core/event_bus.py` | System-wide messaging | All modules | Logging, Memory |
| **Fault Tolerance** | `core/fault_tolerance.py` | System resilience | All critical paths | Supervision |
| **Identity Integration** | `core/identity_integration.py` | Cross-system auth | Identity service | All secured modules |

### Consciousness Systems (`consciousness/`)
| Component | Path | Purpose | Key Features |
|-----------|------|---------|--------------|
| **Awareness Engine** | `consciousness/awareness/awareness_engine.py` | Attention monitoring | Bio-symbolic awareness |
| **Dream Engine** | `consciousness/dream/` | Controlled creativity simulation | OpenAI integration, parallel reality safety |
| **Creative Engine** | `consciousness/creativity/creative_engine.py` | Expression & personality | Voice integration, haiku generation |
| **Consciousness Chat API** | `api/consciousness_chat_api.py` | AI interaction layer | FastAPI endpoints, OpenAI bridge |

### Memory Architecture (`memory/`)
| Component | Path | Purpose | Storage Technology |
|-----------|------|---------|-------------------|
| **Fold System** | `memory/service.py` | Primary memory service | Cascade prevention (99.7%), 1000 fold limit |
| **Memory Manager** | `memory/memoria.py` | Memory orchestration | Causal chain preservation |
| **Quantum Manager** | `memory/quantum_manager.py` | Quantum-inspired memory | Superposition states |
| **Fold Visualizer** | `memory/visualizer.py` | Memory debugging | Graph visualization |

### Identity & Authentication (`identity/`)
| Component | Path | Purpose | Standards |
|-----------|------|---------|----------|
| **Identity API** | `identity/api.py` | Main auth service | FastAPI, WebAuthn |
| **OAuth Federation** | `identity/oauth_federation.py` | External OAuth | OIDC compliance |
| **Lambda ID Resolver** | `identity/lucas_id_resolver.py` | ΛID resolution | Trinity access control |
| **Registration System** | `identity/enhanced_registration_api.py` | User onboarding | WebAuthn bootstrap |

### Governance & Ethics (`governance/`)
| Component | Path | Purpose | Enforcement Level |
|-----------|------|---------|------------------|
| **Guardian System** | `governance/guardian_system.py` | Ethical oversight | Drift threshold: 0.15 |
| **Audit Trail** | `governance/audit_trail.py` | Compliance logging | Immutable records |
| **Compliance Monitor** | `governance/compliance_drift_monitor.py` | Real-time monitoring | Automatic intervention |

### VIVOX Consciousness (`vivox/`)
| Component | Path | Purpose | Components |
|-----------|------|---------|-----------|
| **VIVOX Core** | `vivox/consciousness/vivox_cil_core.py` | Consciousness integration | ME, MAE, CIL, SRM |
| **Emotional Regulation** | `vivox/emotional_regulation/` | Affect processing | Event integration, neuroplastic adaptation |

## FastAPI Services & Endpoints

### Primary API Services
| Service | Path | Port | Purpose |
|---------|------|------|---------|
| **Main Server** | `serve/main.py` | 8080 | Primary service hub |
| **OpenAI Routes** | `serve/openai_routes.py` | 8080 | OpenAI API compatibility |
| **Consciousness Chat** | `api/consciousness_chat_api.py` | 8080 | AI interaction endpoints |
| **Universal Language** | `api/universal_language_api.py` | 8080 | UL protocol API |
| **Identity Service** | `identity/api.py` | varies | Authentication endpoints |

### Bridge APIs (`bridge/api/`)
| Component | Purpose | Integration Points |
|-----------|---------|-------------------|
| **Unified Router** | `unified_router.py` | Cross-module routing |
| **Colony Endpoints** | `colony_endpoints.py` | Multi-agent coordination |
| **Memory API** | `memory.py` | Memory system access |
| **Dream API** | `dream.py` | Dream system control |
| **Emotion API** | `emotion.py` | Emotional state management |

## External Adapters

### Cloud Service Adapters (`adapters/`)
| Adapter | Path | Service | Capabilities |
|---------|------|---------|-------------|
| **Gmail Headers** | `adapters/gmail_headers/` | Gmail API | Metadata extraction |
| **Drive Integration** | `adapters/drive/` | Google Drive | File metadata |
| **Dropbox Connector** | `adapters/dropbox/` | Dropbox API | Cloud storage |
| **Cloud Consolidation** | `adapters/cloud_consolidation.py` | Multi-cloud | Service aggregation |

## Advanced Processing Systems

### Quantum-Inspired Components (`quantum/`)
| Component | Path | Purpose |
|-----------|------|---------|
| **Quantum Core** | `quantum_core/` | Wave function management |
| **Collapse Simulator** | `quantum_core/glyph_collapse_simulator.py` | State collapse |
| **Guardian Integration** | `quantum_core/guardian_integration.py` | Ethics overlay |

### Bio-Inspired Systems (`bio/`)
| Component | Path | Purpose |
|-----------|------|---------|
| **Bio Engine** | `bio/bio_engine/` | Biological pattern simulation |
| **Endocrine Integration** | `bio/endocrine_integration/` | Hormone-like signaling |
| **Oscillator Systems** | `bio/oscillator/` | Rhythm generation |

### Architecture Frameworks
| Framework | Path | Purpose |
|-----------|------|---------|
| **DAST** | `architectures/DAST/` | Dynamic service switching |
| **ABAS** | `architectures/ABAS/` | Proactive assistance |
| **NIAS** | `NIAS_THEORY/` | Neural Intelligence Architecture |

## Data Flow & Communication Patterns

### GLYPH-Based Messaging
- **Core Pattern**: All inter-module communication uses symbolic GLYPH tokens
- **Processing Hub**: `core/symbolic/` processes all GLYPH exchanges
- **Translation Maps**: `data/glyph_translation_map.json` maintains symbol mappings

### Context Bus Architecture
- **Event Bus**: `core/event_bus.py` handles system-wide events
- **Message Bus**: `bridge/message_bus.py` manages external communications
- **Schema Definition**: Located in respective module `__init__.py` files

### Memory Persistence
- **Primary Storage**: Fold-based system in `memory/`
- **Data Directory**: `data/` contains runtime state and metrics
- **Trace Logging**: `trace/` directory for debugging and audit trails

## Security & Compliance

### Authentication Flow
1. **WebAuthn Entry**: `identity/webauthn_bootstrap.py`
2. **ΛID Resolution**: `identity/lucas_id_resolver.py` 
3. **OAuth Federation**: `identity/oauth_federation.py`
4. **Capability Tokens**: Generated with audience+TTL caveats

### Policy Enforcement
- **Guardian System**: Real-time ethics validation (`governance/guardian_system.py`)
- **Drift Detection**: Continuous monitoring with 0.15 threshold
- **Audit Trail**: Immutable logging (`governance/audit_trail.py`)

### Input Validation
- **Bridge Validation**: `bridge/api/validation.py`
- **Schema Validation**: Per-module schema enforcement
- **Rate Limiting**: Implemented in FastAPI services

## Storage & Persistence

### Database Schemas
- **Identity Schema**: `identity/schema.sql` - User auth & profiles
- **Consent Schema**: `consent/ucg_schema.sql` - Consent ledger
- **Memory Storage**: Memory-mapped files in `memory_folds/folds.mmap`

### Configuration Storage
- **Main Config**: `lukhas_config.yaml`
- **Integration Config**: `integration_config.yaml`
- **Per-module Configs**: Individual JSON files in `config/`

## Monitoring & Observability

### Metrics Collection
| Component | Path | Purpose |
|-----------|------|---------|
| **Metrics Collector** | `monitoring/adaptive_metrics_collector.py` | Performance data |
| **Dashboard Server** | `meta_dashboard/dashboard_server.py` | Web interface |
| **Drift Metrics** | `trace/drift_metrics.py` | Ethics monitoring |

### Logging Systems
- **Trace Logger**: `bridge/trace_logger.py` - Cross-module tracing
- **Audit Logger**: `governance/audit_logger.py` - Compliance events
- **System Logs**: Standard Python logging to `lukhas.log`

## Development & Testing Infrastructure

### Testing Framework
- **Main Test Suite**: `tests/` - Comprehensive test coverage
- **Stress Testing**: `tests/stress/` - Load testing
- **Security Testing**: `tests/security/` - Security validation
- **VIVOX Tests**: `tests/vivox/` - Consciousness system tests

### Analysis Tools (`tools/`)
| Tool | Purpose |
|------|---------|
| **Core Analyzer** | `CoreAnalyzer.py` - System analysis |
| **Dependency Test** | `DependencyConnectivityTest.py` - Module connectivity |
| **Security Analysis** | `analysis/security_gap_analysis.py` - Security gaps |

## Known Integration Points

### OpenAI Integration
- **Primary Bridge**: `bridge/llm_wrappers/openai_optimized.py`
- **Dream Integration**: `consciousness/dream/openai_dream_integration.py`
- **Consciousness States**: `consciousness/states/openai_consciousness_adapter.py`

### External API Endpoints
- **Public APIs**: Port 8080 (`serve/main.py`)
- **Internal APIs**: Various ports for module-specific services
- **WebSocket**: `core/interfaces/dashboard/api/websocket_server.py`

## Deployment Architecture

### Container Strategy
- **Docker Compose**: `docker-compose.yml` - Multi-service orchestration
- **Consciousness Platform**: `deployments/consciousness_platform/` - Microservice deployment
- **QIM Container**: `qim/docker-compose.yml` - Quantum processing service

### Service Dependencies
1. **Core Services**: Identity, Memory, Governance (foundational)
2. **Processing Services**: Consciousness, VIVOX, Quantum (compute)
3. **Interface Services**: APIs, Bridge, Adapters (integration)
4. **Support Services**: Monitoring, Logging, Analysis (operational)

This architecture represents a complex, modular AI system with strong separation of concerns, comprehensive security, and extensive monitoring capabilities.