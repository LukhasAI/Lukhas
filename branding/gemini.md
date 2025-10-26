# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Branding Module - Claude AI Context

**Module**: branding
**Purpose**: LUKHAS brand identity, tone systems, and content orchestration
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-18

---

## Module Overview

The branding module provides comprehensive brand identity and content systems for LUKHAS AI, including tone enforcement, vocabulary management, brand orchestration, and multi-domain branding across 37 subdirectories covering all aspects of LUKHAS brand presence.

### Key Components
- **Tone System**: 3-layer tone enforcement (2 Python files)
- **Vocabularies**: Domain-specific lexicons (11 Python files)
- **Design**: Visual identity and design systems
- **Automation**: Brand automation tools (10 Python files)
- **Enforcement**: Brand policy enforcement (2 Python files)
- **Orchestration**: Content orchestration (5 Python files)
- **Intelligence**: Brand intelligence and analysis (3 Python files)
- **Poetry**: Creative content generation (11 Python files)

### Constellation Framework Integration
- **🎭 Persona Star**: Brand personality and voice
- **🔮 Oracle Star**: Brand vision and strategy
- **⚡ Spark Star**: Creative brand expression

---

## Architecture

### Core Brand Systems

#### 1. Tone System
**Location**: `branding/tone/` (2 Python files)
**Purpose**: Multi-layer tone enforcement and modulation

The LUKHAS tone system implements a sophisticated 3-layer approach:
- **Layer 1 (Academic)**: Technical, precise, research-oriented
- **Layer 2 (Professional)**: Business, accessible, solution-focused
- **Layer 3 (Conversational)**: Friendly, approachable, relatable

#### 2. Vocabularies
**Location**: `branding/vocabularies/` (11 Python files)
**Purpose**: Domain-specific lexicons and terminology

Manages vocabulary for:
- Consciousness technology
- MATRIZ framework
- Constellation Framework
- Technical documentation
- Product descriptions
- Marketing materials

#### 3. Brand Automation
**Location**: `branding/automation/` (10 Python files)
**Purpose**: Automated brand enforcement and content generation

Features:
- Automated tone checking
- Content generation pipelines
- Brand policy enforcement
- Consistency validation
- Multi-domain orchestration

#### 4. Poetry & Creative Content
**Location**: `branding/poetry/` (11 Python files)
**Purpose**: Creative content generation

Systems for:
- Keatsian-inspired prose
- Technical poetry
- Brand storytelling
- Metaphor generation
- Narrative synthesis

---

## Module Structure

```
branding/
├── module.manifest.json         # Branding manifest (schema v3.0.0)
├── README.md                    # Branding overview
├── tone/                        # Tone system (2 files)
├── vocabularies/                # Lexicons (11 files)
├── design/                      # Visual identity (1 file)
├── tools/                       # Brand tools (2 files)
├── apis/                        # Brand APIs (1 file)
├── constellation/               # Constellation branding (1 file)
├── analysis/                    # Brand analysis (2 files)
├── intelligence/                # Brand intelligence (3 files)
├── optimization/                # Content optimization (1 file)
├── content/                     # Content systems (1 file)
├── personal_brand/              # Personal branding (2 files)
├── integrations/                # Platform integrations (3 files)
├── adapters/                    # Brand adapters (5 files)
├── poetry/                      # Creative content (11 files)
├── engines/                     # Brand engines (4 files)
├── storytelling/                # Narrative systems (1 file)
├── orchestration/               # Content orchestration (5 files)
├── automation/                  # Brand automation (10 files)
├── enforcement/                 # Policy enforcement (2 files)
├── profiles/                    # Brand profiles (2 files)
├── ai_agents/                   # AI brand agents (2 files)
├── policy/                      # Brand policies (2 files)
├── communications/              # Communications (1 file)
└── docs/                        # 38+ brand documentation files
    ├── TONE_GUIDE.md
    ├── LUKHAS_BRANDING_GUIDE.md
    ├── MATRIZ_BRAND_GUIDE.md
    ├── LUKHAS_LEXICON.md
    ├── BRAND_POLICY.md
    └── (33+ additional guides)
```

---

## Key Documentation

The branding module includes 38+ comprehensive brand documentation files:

**Core Guides**:
- `TONE_GUIDE.md` - Complete tone system documentation
- `LUKHAS_BRANDING_GUIDE.md` - Primary branding guide
- `LUKHAS_LEXICON.md` - Complete terminology reference
- `BRAND_POLICY.md` - Brand usage policies
- `MATRIZ_BRAND_GUIDE.md` - MATRIZ-specific branding

**System Reports**:
- `SYSTEM_INTEGRATION_REPORT.md`
- `SYSTEM_CONSOLIDATION_REPORT.md`
- `ELITE_ORCHESTRATION_REPORT.md`
- `VOICE_COHERENCE_UPGRADE_REPORT.md`

**Framework Guides**:
- `LUKHAS_TRINITY_FRAMEWORK.md`
- `KEATSIAN_CONSTELLATION_GUIDE.md`
- `CONSTELLATION_FRAMEWORK.md`

---

## Development Guidelines

### 1. Using Tone System

```python
from branding.tone import ToneEnforcer, ToneLayer

# Create tone enforcer
enforcer = ToneEnforcer()

# Check content against tone layer
result = enforcer.check_tone(
    content="Your content here",
    target_layer=ToneLayer.PROFESSIONAL,
    strict=True
)

# Adjust content to target tone
adjusted = enforcer.adjust_tone(
    content="Your content",
    source_layer=ToneLayer.ACADEMIC,
    target_layer=ToneLayer.CONVERSATIONAL
)
```

### 2. Vocabulary Management

```python
from branding.vocabularies import get_vocabulary, validate_terminology

# Get domain-specific vocabulary
vocab = get_vocabulary(domain="consciousness")

# Validate terminology usage
validation = validate_terminology(
    text="Your text with technical terms",
    vocabulary=vocab,
    strict=True
)
```

### 3. Brand Automation

```python
from branding.automation import auto_brand_content

# Automatically brand content
branded = auto_brand_content(
    raw_content="Technical documentation",
    target_audience="developers",
    tone_layer="professional",
    enforce_policies=True
)
```

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Brand history and consistency
- **A (Attention)**: Focus on brand violations
- **T (Thought)**: Brand strategy decisions
- **R (Risk)**: Brand risk assessment
- **I (Intent)**: Brand intent understanding
- **A (Action)**: Brand enforcement actions

---

## Observability

### Required Spans

```python
REQUIRED_SPANS = [
    "lukhas.branding.operation",     # Branding operations
]
```

---

## Performance Targets

- **Tone Checking**: <100ms per document
- **Vocabulary Validation**: <50ms per check
- **Content Generation**: <2s for standard content
- **Brand Enforcement**: Real-time (<200ms)
- **Orchestration**: <500ms for multi-domain sync

---

## Dependencies

**Required Modules**: None (standalone module)

**Integration Points**:
- All LUKHAS modules use branding for consistency
- Content generation systems
- Documentation pipelines
- Marketing automation

---

## Related Modules

- **Tone** ([../tone/](../tone/)) - Tone system implementation
- **Serve** ([../serve/](../serve/)) - Brand-aware API serving
- **AI Orchestration** ([../ai_orchestration/](../ai_orchestration/)) - Brand content orchestration

---

## Documentation

- **README**: [branding/README.md](README.md)
- **Docs**: [branding/docs/](docs/) - 38+ brand guides
- **Tests**: [branding/tests/](tests/)
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#branding)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Components**: 70+ Python files across 37 subdirectories
**Documentation**: 38+ brand guides
**Test Coverage**: 85.0%
**Last Updated**: 2025-10-18


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
