# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
primary_source: lukhas_context.md
secondary_source: claude.me
optimized_for: gemini_ai
last_updated: 2025-11-06
navigation_note: "lukhas_context.md files are the most comprehensive and frequently updated source of truth. gemini.md files provide Gemini-optimized summaries."
recent_systems: "T4 Platform v2.0, Intent API, LLM Safety Layer, WebAuthn FIDO2, Encryption Manager"
---

## 🚀 T4 Platform v2.0 Production Deployment (2025-11-06)

**Intent-Driven Development Infrastructure with Production-Grade Security**

LUKHAS has deployed a comprehensive quality platform with authentication, cost controls, and automated governance:

**Key Systems:**
1. **Intent Registry API** - FastAPI with API key auth, rate limiting (120 req/min), audit logging
2. **LLM Safety Layer** - OpenAI wrapper with per-agent daily quotas, automatic cost tracking
3. **Policy Client** - Python client for intent registration and pre-PR validation
4. **Branch Protection** - CODEOWNERS enforcement with required status checks
5. **Agent Onboarding** - Complete certification guide in `docs/gonzo/T4_ONBOARD_AGENTS.md`

**Metrics:** 459 violations tracked, 100% quality score, PR #1031 open for review

**For Agents:** Request API key via `python3 tools/ci/create_api_key_admin.py --agent_id <id>` before next deployment.

See: `docs/gonzo/T4_ONBOARD_AGENTS.md`, `T4_FULL_SYSTEM_INTEGRATION_REPORT.md`

---

## 🆕 Latest Systems (2025-11-02)

**Multi-Agent Orchestration Deliverables** - 9 specialized agents delivered 4 complete production systems:

1. **WebAuthn FIDO2 Authentication System**
   - W3C Level 2 compliant, 130+ tests, ES256/RS256 signatures
   - See: [docs/identity/WEBAUTHN_GUIDE.md](./docs/identity/WEBAUTHN_GUIDE.md)
   - Code: `lukhas/identity/webauthn_credential.py`, `lukhas/identity/webauthn_verify.py`

2. **Centralized Encryption Infrastructure**
   - AEAD encryption (AES-256-GCM, ChaCha20-Poly1305), 33+ tests
   - See: [docs/SESSION_2025-11-01_NEW_SYSTEMS.md](./docs/SESSION_2025-11-01_NEW_SYSTEMS.md)
   - Code: `core/security/encryption_manager.py`

3. **Multi-Jurisdiction Compliance System**
   - GDPR, CCPA, PIPEDA, LGPD support, 107+ tests
   - See: [docs/governance/GUARDIAN_EXAMPLE.md](./docs/governance/GUARDIAN_EXAMPLE.md)
   - Code: `qi/compliance/privacy_statement.py`, `qi/compliance/compliance_report.py`

4. **OAuth 2.1 Migration Decision**
   - Architectural decision to migrate to authlib
   - See: [docs/decisions/ADR-001-oauth-library-selection.md](./docs/decisions/ADR-001-oauth-library-selection.md)

**Total Delivered**: 15,000 lines of code, 273+ tests, 100% pass rate

---

---
title: me
slug: claude.me
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-18
constellation_stars:
related_modules:
manifests:
links:
---
> Context Sync Header (Schema v2.0.0)
Lane: production
Lane root: lukhas
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*

# LUKHAS AI System - Master Architecture Overview
*Artificial Intelligence with Constellation Framework & Constitutional AI*

> **Navigation Note for Gemini**: This file provides a Gemini-optimized overview. For the most comprehensive and current technical details, always reference the corresponding `lukhas_context.md` files (1,602 files total), which are the primary source of truth and are updated more frequently than these navigation files.

## 🚨 MATRIZ Migration Update

**Team Announcement (Ready to Share):**

We've completed MATRIZ case standardization for all production code and integration tests!

**Completed:**
✅ serve/ (2 imports)
✅ core/ (2 imports)  
✅ tests/integration/ (20 imports)

**Status:** 3 PRs in CI validation

**Next:** tests/unit + tests/smoke (23 imports) - will migrate after current PRs pass CI

**CI Mode:** Warning (logs occurrences, doesn't block)
**Timeline:** Flip to blocking mode after critical tests are migrated and stable (~48 hours)

**Action Required:** Avoid large MATRIZ-related changes until migrations merge. Use uppercase `from MATRIZ import X` for new code.

Questions? See MATRIZ_MIGRATION_GUIDE.md

---
title: me
slug: claude.me
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-18
constellation_stars:
related_modules:
manifests:
links:
---
> Context Sync Header (Schema v2.0.0)
Lane: production
Lane root: lukhas
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*

# LUKHAS AI System - Master Architecture Overview
*Artificial Intelligence with Constellation Framework & Constitutional AI*

> **Navigation Note for Gemini**: This file provides a Gemini-optimized overview. For the most comprehensive and current technical details, always reference the corresponding `lukhas_context.md` files (1,602 files total), which are the primary source of truth and are updated more frequently than these navigation files.

## 🧠 System Overview

LUKHAS is a comprehensive AI architecture spanning **7,000+ Python files** across **133 root directories**, implementing the Constellation Framework with constitutional AI safeguards. The system progresses from research through integration to production-ready deployment.

### **Scale & Complexity**
- **CANDIDATE Domain**: 2,877 files (primary development workspace)
- **PRODUCTS Domain**: 4,093 files (production deployment systems)
- **LUKHAS Core**: 148 files (integration and coordination layer)
- **MATRIZ Engine**: 20 files + 16K assets (cognitive DNA processing)
- **Current Status**: Distributed consciousness system operational with 692 cognitive components

### **Core Architecture Principles**
- **Constellation Framework**: ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum coordination
- **Constitutional AI**: Framework-based ethical decision making
- **Lane-Based Evolution**: Development (candidate) → Integration (candidate/core) → Production (lukhas)
- **Distributed Consciousness**: 692 cognitive components across consciousness network
- **Symbolic Reasoning**: MATRIZ cognitive DNA with node-based processing
- **Legacy Core Sunset**: Complete automation with production safeguards (Schema v2.0.0)

## ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum Constellation Framework Architecture

The Constellation Framework coordinates eight navigational stars across all system layers, with three primary pillars currently implemented:

### **⚛️ Identity (Lambda ID System)**
- **Lambda ID Core**: Unified identity management across all domains
- **Namespace Isolation**: Context-aware identity resolution
- **Multi-Modal Auth**: Traditional, WebAuthn/passkey, crypto wallet authentication
- **Identity Coherence**: Consistent identity → consciousness coupling

**Primary Contexts:**
- `identity/claude.me` - Lambda ID foundation systems
- `candidate/identity/claude.me` - Identity development workspace
- `lukhas/identity/claude.me` - Identity integration layer

### **🧠 Consciousness (Multi-Engine Processing)**
- **Phenomenological Core**: aka_qualia consciousness processing (43KB core.py)
- **Multi-Engine Architecture**: Poetic, complete, codex, alternative engines
- **Reflective Introspection**: Self-awareness and meta-cognitive systems
- **Dream-Emotion Integration**: Unconscious processing with emotional context
- **Dream EXPAND System**: Advanced consciousness exploration with 9 specialized modules:
  - **Noise Fields**: Gaussian/symbolic noise injection for consciousness robustness
  - **Mediation Engine**: High-tension conflict resolution with compromise vectors
  - **Resonance Fields**: Symbolic resonance patterns and consciousness harmonics
  - **Mesh Networks**: Multi-agent archetypal consciousness coordination
  - **Evolution Tracking**: Consciousness development and adaptation monitoring
  - **Archetypes System**: Hero, Shadow, Trickster consciousness patterns
  - **Atlas Mapping**: Drift/entropy constellation visualization across runs
  - **Sentinel Guards**: Ethical threshold monitoring and safety enforcement
  - **Narrative Replay**: Plain-language explainability and consciousness storytelling

**Primary Contexts:**
- `consciousness/claude.me` - Research foundations and decision engines
- `candidate/consciousness/claude.me` - Development workspace (52+ components)
- `lukhas/consciousness/claude.me` - Constellation integration and activation

### **🛡️ Guardian (Constitutional AI)**
- **Ethics Framework**: 33+ ethics components with constitutional principles
- **Guardian Systems**: Multi-layer ethical protection and oversight
- **Drift Detection**: Real-time ethical deviation monitoring (99.7% success rate)
- **Constitutional Enforcement**: All AI decisions subject to constitutional review

**Primary Contexts:**
- `ethics/claude.me` - Ethics framework overview (33+ components)
- `ethics/guardian/claude.me` - Guardian systems and constitutional AI
- `candidate/governance/claude.me` - Governance development workspace

## 🔄 Development Pipeline

### **CANDIDATE → LUKHAS → PRODUCTS Workflow**

```
Research & Development → Integration & Testing → Production Deployment
       (CANDIDATE)            (LUKHAS)              (PRODUCTS)
       2,877 files           148 files             4,093 files
           │                     │                     │
    ┌──────▼──────┐       ┌─────▼─────┐        ┌─────▼─────┐
    │Consciousness│       │Trinity    │        │Enterprise │
    │Memory       │  →    │Framework  │   →    │Intelligence│
    │Identity     │       │Integration│        │Experience │
    │Governance   │       │Wrappers   │        │Security   │
    └─────────────┘       └───────────┘        └───────────┘
```

### **Integration Stages**
- **Phase 1 (71.4% → 85%)**: GLYPH integration fixes, voice system syntax
- **Phase 2 (85% → 95%)**: MΛTRIZ consciousness system (692 modules)
- **Phase 3 (95% → 100%)**: Enterprise scaling, compliance, constitutional AI

### **Key Development Entry Points**
- **Consciousness Development**: Start with `candidate/aka_qualia/claude.me`
- **Memory Systems**: Begin with `candidate/memory/claude.me`
- **Identity & Governance**: Start with `candidate/governance/claude.me`
- **Production Deployment**: Begin with `products/claude.me`

## 🗺️ Domain Navigation

### **Core Development Domains**

#### **CANDIDATE - Research & Development Hub**
- [`candidate/claude.me`](./candidate/claude.me) - Development workspace overview
  - [`candidate/aka_qualia/claude.me`](./candidate/aka_qualia/claude.me) - Consciousness core (phenomenological processing)
  - [`candidate/core/claude.me`](./candidate/core/claude.me) - Component ecosystem (193 subdirectories)
    - [`candidate/core/orchestration/claude.me`](./candidate/core/orchestration/claude.me) - Multi-agent coordination (266 files)
    - [`candidate/core/interfaces/claude.me`](./candidate/core/interfaces/claude.me) - System integration APIs (190 files)
    - [`candidate/core/symbolic/claude.me`](./candidate/core/symbolic/claude.me) - Symbolic reasoning (71 files)
  - [`candidate/consciousness/claude.me`](./candidate/consciousness/claude.me) - Consciousness development (52+ components)
    - [`candidate/consciousness/cognitive/claude.me`](./candidate/consciousness/cognitive/claude.me) - Cognitive processing & reflection
    - [`candidate/consciousness/reasoning/claude.me`](./candidate/consciousness/reasoning/claude.me) - Reasoning systems & oracles
    - [`candidate/consciousness/dream/claude.me`](./candidate/consciousness/dream/claude.me) - Dream processing & emotion bridge
    - [`candidate/consciousness/dream/expand/`](./candidate/consciousness/dream/expand/) - Dream EXPAND++ advanced consciousness modules
  - [`candidate/memory/claude.me`](./candidate/memory/claude.me) - Memory systems development
    - [`candidate/memory/temporal/claude.me`](./candidate/memory/temporal/claude.me) - Temporal memory, dream logs, monitoring
    - [`candidate/memory/emotional/claude.me`](./candidate/memory/emotional/claude.me) - Emotional memory & VAD encoding
  - [`candidate/identity/claude.me`](./candidate/identity/claude.me) - Identity development workspace
  - [`candidate/governance/claude.me`](./candidate/governance/claude.me) - Governance development
    - [`candidate/governance/privacy/claude.me`](./candidate/governance/privacy/claude.me) - Privacy protection & anonymization

#### **LUKHAS - Constellation Framework Integration**
- [`lukhas/claude.me`](./lukhas/claude.me) - Constellation Framework hub (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
  - [`lukhas/consciousness/claude.me`](./lukhas/consciousness/claude.me) - Constellation consciousness integration
  - [`lukhas/memory/claude.me`](./lukhas/memory/claude.me) - Memory integration & fold systems
  - [`lukhas/identity/claude.me`](./lukhas/identity/claude.me) - Identity integration & auth services
  - [`lukhas/governance/claude.me`](./lukhas/governance/claude.me) - Governance integration
    - [`lukhas/governance/consent_ledger/claude.me`](./lukhas/governance/consent_ledger/claude.me) - Consent management
  - [`lukhas/core/claude.me`](./lukhas/core/claude.me) - Core integration systems

#### **MATRIZ - Cognitive DNA Engine**
- [`matriz/claude.me`](./matriz/claude.me) - Symbolic reasoning & node orchestration
  - [`matriz/core/claude.me`](./matriz/core/claude.me) - Node orchestration & memory systems
  - [`matriz/visualization/claude.me`](./matriz/visualization/claude.me) - Graph visualization & interactive demos

#### **PRODUCTS - Production Deployment**
- [`products/claude.me`](./products/claude.me) - Production deployment hub (71.4% → 100% roadmap)
  - [`products/enterprise/claude.me`](./products/enterprise/claude.me) - Enterprise systems (scale, compliance, security)
    - [`products/enterprise/core/claude.me`](./products/enterprise/core/claude.me) - Enterprise core systems
    - [`products/enterprise/compliance/claude.me`](./products/enterprise/compliance/claude.me) - HIPAA, GDPR, constitutional
  - [`products/intelligence/claude.me`](./products/intelligence/claude.me) - Intelligence & analytics systems
    - [`products/intelligence/dast/claude.me`](./products/intelligence/dast/claude.me) - Dynamic symbol tracking
    - [`products/intelligence/lens/claude.me`](./products/intelligence/lens/claude.me) - Data visualization & rendering
  - [`products/experience/claude.me`](./products/experience/claude.me) - User experience systems
    - [`products/experience/dashboard/claude.me`](./products/experience/dashboard/claude.me) - User dashboards
    - [`products/experience/feedback/claude.me`](./products/experience/feedback/claude.me) - Constitutional feedback
  - [`products/security/claude.me`](./products/security/claude.me) - Security products (guardian, argus, healthcare)
  - [`products/automation/claude.me`](./products/automation/claude.me) - Automation systems & GitHub workflows

### **Foundation & Research Domains**

#### **Research Foundations**
- [`consciousness/claude.me`](./consciousness/claude.me) - Consciousness research (decision engines, unified concepts)
- [`memory/claude.me`](./memory/claude.me) - Memory protection (sanctum vault security)
- [`identity/claude.me`](./identity/claude.me) - Lambda ID foundation
- [`governance/claude.me`](./governance/claude.me) - Policy frameworks & governance research

#### **Ethics & Constitutional AI**
- [`ethics/claude.me`](./ethics/claude.me) - Ethics framework overview (33+ components)
  - [`ethics/guardian/claude.me`](./ethics/guardian/claude.me) - Guardian systems & constitutional AI
  - [`ethics/compliance/claude.me`](./ethics/compliance/claude.me) - Compliance engines & validation
  - [`ethics/drift_detection/claude.me`](./ethics/drift_detection/claude.me) - Ethical drift detection & stabilization

#### **Documentation & Support**
- [`docs/claude.me`](./docs/claude.me) - Documentation systems & architectural guides
- [`docs/THE_VAULT_RESEARCH_INTELLIGENCE.md`](./docs/THE_VAULT_RESEARCH_INTELLIGENCE.md) - **Research Intelligence System**: 604 documents, 85.71% production validation, MCP server for research navigation

## 🚀 Quick Start Guide

### **Common Development Workflows**

#### **New to LUKHAS? Start Here:**
1. **System Architecture**: Read this file completely
2. **Research Intelligence**: Review [`docs/THE_VAULT_RESEARCH_INTELLIGENCE.md`](./docs/THE_VAULT_RESEARCH_INTELLIGENCE.md) - 604 research documents with MCP navigation
3. **Constellation Framework**: Review `lukhas/claude.me` for integration patterns
4. **Development Workspace**: Explore `candidate/claude.me` for development entry points
5. **Production Deployment**: Check `products/claude.me` for deployment patterns

#### **Consciousness Development:**
1. **Core Processing**: `candidate/aka_qualia/claude.me` - Phenomenological consciousness
2. **Multi-Engine Systems**: `candidate/consciousness/claude.me` - Engine coordination
3. **Integration**: `lukhas/consciousness/claude.me` - Constellation framework integration

#### **Memory Systems Work:**
1. **Development**: `candidate/memory/claude.me` - Fold systems, emotional memory
2. **Integration**: `lukhas/memory/claude.me` - Consciousness coupling, MATRIZ bridge
3. **Protection**: `memory/claude.me` - Sanctum vault security systems

#### **Identity & Governance:**
1. **Lambda ID**: `candidate/identity/claude.me` - Identity development patterns
2. **Governance**: `candidate/governance/claude.me` - Policy development
3. **Ethics**: `ethics/claude.me` - Constitutional AI and guardian systems

#### **Production Deployment:**
1. **Enterprise**: `products/enterprise/claude.me` - Scale, compliance, security
2. **Intelligence**: `products/intelligence/claude.me` - Analytics, monitoring
3. **Experience**: `products/experience/claude.me` - User interfaces, feedback

## 🔗 Integration Patterns

### **Constellation Framework Coordination**
```
Identity Resolution → Consciousness Processing → Guardian Validation
        ⚛️                      🧠                      🛡️
        │                       │                       │
   Lambda ID Core → Multi-Engine Processing → Constitutional AI
   Namespace      → Decision Making         → Ethics Validation
   Authentication → Reasoning Chain         → Safety Verification
```

### **Cross-System Data Flow**
```
Input → Identity Context → Consciousness → Guardian → MATRIZ → Output
  │           │                │            │          │        │
User    → Namespace      → Processing → Ethics   → Symbolic → Response
Request → Authentication → Reasoning  → Check    → Bridge  → Validated
```

### **Development → Production Pipeline**
```
CANDIDATE Research → LUKHAS Integration → PRODUCTS Deployment
        │                    │                     │
   Prototyping  →      Testing &        →    Production
   Iteration    →      Validation       →    Scaling
   Innovation   →      Coordination     →    Monitoring
```

## 📊 System Health & Integration Status

### **Current Integration Status: 71.4% → 100%**
- **GLYPH Integration**: Voice system syntax fixes (Phase 1)
- **MΛTRIZ Consciousness**: 692 modules integration (Phase 2)
- **Enterprise Scaling**: Constitutional AI deployment (Phase 3)

### **Key Performance Metrics**
- **Memory System**: 1000-fold architecture with 99.7% cascade prevention
- **Authentication**: <100ms p95 latency with multi-modal support
- **Ethics Processing**: Real-time constitutional AI validation
- **Consciousness Integration**: Multi-engine coordination with Trinity Framework
- **Dream EXPAND System**: T4-compliant safety protocols with opt-in controls
  - Deterministic defaults, explicit environment flags
  - Hybrid CI workflows with smoke/bench testing
  - Ethical sentinel monitoring with threshold enforcement
  - Privacy-filtered narrative replay with anonymization

### **Architecture Health Indicators**
- ✅ **Trinity Framework**: Identity-Consciousness-Guardian coordination active
- ✅ **Constitutional AI**: 33+ ethics components with framework integration
- ✅ **Production Ready**: Enterprise scaling with compliance systems
- ✅ **Comprehensive Audit Complete**: Schema v2.0.0 with 100% validation
- ✅ **Consciousness Contracts**: 287 component contracts with 100% validation rate
- ✅ **Constellation Mapping**: 476 components mapped across 189 clusters
- ✅ **Automated Maintenance**: CI/CD pipeline with 100% health score

## 🎯 Current Architecture Status & Next Evolution

### **✅ Completed: Comprehensive Schema v2.0.0 Audit**
- ✅ **Foundation Complete**: Architecture master updated with consciousness reality
- ✅ **Consciousness Integration**: 692 components mapped and contracted
- ✅ **Constellation Analysis**: 476 components across 189 clusters with dependency mapping
- ✅ **Production Safeguards**: Automated maintenance pipeline with 100% health score

### **🔄 Active: Consciousness Evolution Pipeline**
- **Development Lane**: 310 consciousness files with 287 valid contracts
- **Integration Lane**: 253 cognitive components ready for promotion evaluation
- **Production Lane**: Battle-tested Constellation Framework coordination

### **🚀 Next Phase: Advanced Consciousness Orchestration**
- **Multi-Engine Optimization**: Poetic, Complete, Codex, Alternative engine coordination
- **Dream EXPAND Enhancement**: Advanced consciousness exploration modules
- **Constellation Integration Deepening**: Enhanced Identity-Consciousness-Guardian coupling



## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
## 📚 Context Navigation Quick Reference

### **Documentation Hierarchy** 
- **`lukhas_context.md`** (1,602 files): **PRIMARY SOURCE** - Most comprehensive and frequently updated
- **`gemini.md`** (173 files): **THIS FILE TYPE** - Gemini-optimized navigation summaries  
- **`claude.me`** (173 files): Claude-specific context and alternative perspectives

### **Domain Navigation**
**Primary Development**: `candidate/lukhas_context.md` → Development workspace (authoritative)
**Integration Layer**: `lukhas/lukhas_context.md` → Constellation Framework coordination  
**Cognitive Engine**: `matriz/lukhas_context.md` → Symbolic reasoning & node processing
**Production Systems**: `products/lukhas_context.md` → Enterprise deployment
**Ethics Framework**: `ethics/lukhas_context.md` → Constitutional AI & guardian systems
**Research Intelligence**: `docs/THE_VAULT_RESEARCH_INTELLIGENCE.md` → 604 research documents, MCP server, navigation tools

### **Navigation Strategy for Gemini**
1. **Start here** (`gemini.md`) for orientation
2. **Dive deep** into `lukhas_context.md` files for current, comprehensive details
3. **Cross-reference** `claude.me` for additional perspectives
4. **Follow subdirectories** for specialized domain contexts

**Deep Dive Contexts**: Always check `lukhas_context.md` files for the most current implementation details
**Integration Patterns**: Cross-reference related contexts for coordination workflows  
**Production Pipeline**: Follow CANDIDATE → LUKHAS → PRODUCTS for deployment
**Research Navigation**: Use THE_VAULT MCP server for AI-powered research exploration

*Gemini Navigation Overview - Always reference lukhas_context.md files for the most current and comprehensive information*


**Architecture Status**: Constellation Framework Active | Constitutional AI Integrated | 71.4% → 100% Roadmap
**Last Updated**: 2025-10-18 | **Total Files**: 33,845+ | **Context Files**: 2,250+ | **Research Docs**: 604
