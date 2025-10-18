---
title: Constellation Top - 8-Star System Overview
updated: 2025-10-18
version: 2.0
owner: LUKHAS Core Team
status: active
schema_version: 1.1.0
contract_refs:
  - constellation.star_system@v2
  - matriz.cognitive_pipeline@v1
tags: [architecture, constellation, star-system, cognitive-framework]
---

# Constellation Top Overview

The **Constellation Framework** is LUKHAS's 8-star classification system that maps modules to cognitive capabilities and consciousness-aware patterns. Each star represents a fundamental aspect of the cognitive architecture, enabling systematic organization of 780+ modules across the platform.

## 🌟 The Eight Stars

### Core Cognitive Stars

#### ⚛️ Anchor (Identity)
**Domain**: Authentication, Authorization, Identity Management
**Current Modules**: 55
**Key Capabilities**: Session management, persona modeling, ΛiD system, OIDC/OAuth flows
**MATRIZ Nodes**: `identity`, `action`
**Example Modules**: `lukhas.identity`, `candidate/identity/anchor_core`

#### ✦ Trail (Memory)
**Domain**: Persistent State, Context, Retrieval Systems
**Current Modules**: 97
**Key Capabilities**: Episodic memory, semantic storage, vector embeddings, cache management
**MATRIZ Nodes**: `memory`, `attention`
**Example Modules**: `candidate/memory/trail_engine`, `lukhas.memory.persistent`

#### 🌊 Flow (Consciousness)
**Domain**: Consciousness Integration, Metacognition, Awareness
**Current Modules**: 108 (largest constellation)
**Key Capabilities**: Attention routing, self-reflection, consciousness processing, salience detection
**MATRIZ Nodes**: `attention`, `thought`
**Example Modules**: `candidate/consciousness/flow_integrator`, `lukhas.consciousness.core`

#### 🛡️ Watch (Guardian)
**Domain**: Policy Enforcement, Safety, Constitutional AI
**Current Modules**: 53
**Key Capabilities**: Policy guards, red-team simulation, audit trails, ethical drift detection
**MATRIZ Nodes**: `risk`, `action`
**Example Modules**: `lukhas.governance.guardian`, `candidate/guardian/watch_enforcer`

### Specialized Cognitive Stars

#### 🔬 Horizon (Vision)
**Domain**: Perception, Visual Processing, Scene Understanding
**Current Modules**: 53
**Key Capabilities**: Vision pipelines, OCR, image analysis, dashboard rendering
**MATRIZ Nodes**: `thought`, `attention`
**Example Modules**: `candidate/vision/horizon_processor`

#### 🌱 Living (Bio)
**Domain**: Bio-Inspired Adaptation, Organic Growth Patterns
**Current Modules**: TBD (under development)
**Key Capabilities**: Homeostatic regulation, cellular adaptation, metabolic modeling
**MATRIZ Nodes**: `thought`, `action`
**Example Modules**: `candidate/bio/living_systems`

#### 🌙 Drift (Dream)
**Domain**: Creative Synthesis, Imagination, Unconscious Processing
**Current Modules**: TBD (under development)
**Key Capabilities**: Dream generation, creative outputs, hypnagogic synthesis
**MATRIZ Nodes**: `thought`, `memory`
**Example Modules**: `candidate/dream/drift_engine`

#### 🔮 Oracle (Quantum)
**Domain**: Quantum-Inspired Algorithms, Superposition, Entanglement
**Current Modules**: 11
**Key Capabilities**: Quantum attention, annealing algorithms, qi-layer processing
**MATRIZ Nodes**: `thought`, `attention`
**Example Modules**: `candidate/quantum/oracle_processor`

### ⚖️ North (Ethics)
**Domain**: Ethical Reasoning, Value Alignment, Moral Decision-Making
**Current Modules**: TBD (under development)
**Key Capabilities**: Ethical auditing, consent management, provenance tracking, fairness analysis
**MATRIZ Nodes**: `risk`, `thought`
**Example Modules**: `candidate/ethics/north_reasoner`

### Supporting (Default)
**Domain**: Infrastructure, Utilities, General Services
**Current Modules**: 394 (50.5% of total)
**Purpose**: Foundational modules without specialized cognitive assignments
**Promotion Path**: Can be auto-promoted to specific stars via `--star-from-rules` based on capability detection

## 📊 Current Distribution (780 Total Modules)

| Star | Count | Percentage | Status |
|------|-------|------------|--------|
| 🌊 Flow (Consciousness) | 108 | 13.8% | Active |
| ✦ Trail (Memory) | 97 | 12.4% | Active |
| ⚛️ Anchor (Identity) | 55 | 7.1% | Active |
| 🛡️ Watch (Guardian) | 53 | 6.8% | Active |
| 🔬 Horizon (Vision) | 53 | 6.8% | Active |
| 🔮 Oracle (Quantum) | 11 | 1.4% | Active |
| Supporting | 394 | 50.5% | Default |
| **Total** | **780** | **100%** | - |

**Note**: 🌱 Living, 🌙 Drift, and ⚖️ North are in development and will be populated during Phase 3-4 manifest regeneration.

## 🔄 Star Assignment Workflow

### 1. Initial Assignment (Heuristic)
Stars are initially assigned using path-based heuristics in `scripts/generate_module_manifests.py`:
- Pattern matching on module paths (e.g., `/consciousness/` → Flow)
- Capability detection from dependencies
- MATRIZ node mapping

### 2. Rule-Based Promotion (Phase 3)
The `--star-from-rules` flag enables automated promotion from Supporting using `configs/star_rules.json`:

```bash
python scripts/generate_module_manifests.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --star-from-rules \
  --star-confidence-min 0.70
```

**Promotion Rules Include**:
- Path regex patterns (weight: 0.40)
- Capability overrides (weight: 0.60)
- MATRIZ node overrides (weight: 0.50)
- Owner priors (weight: 0.35)
- Dependency hints (weight: 0.30)

**Confidence Thresholds**:
- `min_suggest`: 0.50 (suggest in logs)
- `min_autopromote`: 0.70 (automatic promotion)

### 3. Manual Review & Validation
High-value modules (T1/T2) should be manually reviewed for star accuracy:
- Check `manifests/**/module.manifest.json` → `constellation_alignment.primary_star`
- Validate against architectural intent
- Update `configs/star_rules.json` patterns as needed

## 🛠️ Technical Integration

### Manifest Schema
Star assignments are stored in module manifests:

```json
{
  "constellation_alignment": {
    "primary_star": "🌊 Flow (Consciousness)",
    "star_aliases": ["Consciousness", "Flow"],
    "trinity_aspects": ["awareness", "metacognition"]
  }
}
```

### MATRIZ Node Mapping
Stars correlate with MATRIZ cognitive nodes:

| MATRIZ Node | Primary Stars | Cognitive Function |
|-------------|--------------|-------------------|
| `memory` | ✦ Trail | State persistence, retrieval |
| `attention` | 🌊 Flow, ✦ Trail | Routing, salience, context |
| `thought` | 🌊 Flow, 🔬 Horizon | Reasoning, processing |
| `risk` | 🛡️ Watch, ⚖️ North | Safety, ethics evaluation |
| `action` | ⚛️ Anchor, 🛡️ Watch | Execution, policy enforcement |
| `supporting` | Supporting | Infrastructure utilities |

### Quality Tier Correlation
Star assignments influence quality tier expectations:

- **T1 (Critical)**: Require precise star alignment with architecture
- **T2 (Important)**: Should have appropriate star, manual review recommended
- **T3 (Standard)**: Heuristic assignment acceptable
- **T4 (Experimental)**: Often Supporting, promoted as capabilities mature

## 📚 Related Documentation

### Core References
- **Star Rules**: [configs/star_rules.json](../configs/star_rules.json) - Promotion rules and weights
- **Manifest Schema**: [docs/schemas/matriz_module_compliance.schema.json](../docs/schemas/matriz_module_compliance.schema.json)
- **Inventory**: [docs/audits/COMPLETE_MODULE_INVENTORY.json](../docs/audits/COMPLETE_MODULE_INVENTORY.json)

### Tools & Scripts
- **Manifest Generator**: `scripts/generate_module_manifests.py`
- **Star Canon Sync**: `scripts/check_star_canon_sync.py`
- **Contract Validator**: `scripts/validate_contract_refs.py`
- **Context Bot**: `scripts/context_coverage_bot.py`

### Makefile Targets
```bash
make top              # Generate constellation dashboard
make manifest-regen   # Regenerate all 780 manifests with star rules
make star-audit       # Audit star assignments for consistency
```

## 🚀 Roadmap

### Phase 3: Star Promotion Finalization (Current)
- ✅ Star rules configuration validated
- ✅ `--star-from-rules` flag implemented
- ⏳ Stakeholder review of promotion thresholds
- ⏳ Strategic alignment with OpenAI ecosystem

### Phase 4: Manifest Regeneration (Next)
- Regenerate 780 manifests with updated stars
- Update constellation dashboards
- Validate 99% artifact coverage
- Refresh MATRIZ node mappings

### Phase 5: Directory Restructuring
- Elevate flagship star modules to root
- Update all manifest paths
- CI integration for star enforcement

## 🔍 Star Selection Guidelines

### When to Assign a Specific Star
1. **Clear Domain Match**: Module directly implements star's cognitive function
2. **High Confidence**: Pattern/capability scoring ≥ 0.70
3. **Architectural Alignment**: Matches LUKHAS consciousness framework intent
4. **MATRIZ Integration**: Aligns with appropriate cognitive pipeline nodes

### When to Keep Supporting
1. **Infrastructure Only**: No cognitive capability (utilities, helpers, configs)
2. **Low Confidence**: Pattern scoring < 0.50
3. **Unclear Intent**: Module purpose ambiguous or mixed
4. **Temporary/Experimental**: T4 prototypes without defined role

### Star Promotion Red Flags
- ❌ Module has conflicting star patterns (e.g., both Memory and Identity)
- ❌ Star assignment driven by naming convention alone
- ❌ T1/T2 module with Supporting (likely needs manual assignment)
- ❌ Quantum/Bio stars used for non-specialized modules

## 📞 Contact & Governance

**Owner**: LUKHAS Core Team
**Review Cycle**: Quarterly star distribution analysis
**Change Process**: RFC required for new stars or major rule changes
**Issues**: Use GitHub Issues with `constellation` and `star-system` tags

---

**Last Updated**: 2025-10-18
**Schema Version**: 2.0
**Manifest Count**: 780 modules
**Active Stars**: 6 of 9 deployed

