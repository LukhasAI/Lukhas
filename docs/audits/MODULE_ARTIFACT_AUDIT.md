# Module Artifact Audit & Template Standards

**Purpose**: Document existing module artifacts, templates, and standards for MATRIZ rollout
**Date**: 2025-10-11
**Status**: Discovery Phase

---

## Executive Summary

**Current State**:
- **780 Python modules** total (636 candidate + 144 lukhas)
- **Only 3 modules** have `module.manifest.json` files
- **777 modules (99.6%)** need comprehensive documentation

**Artifact Types Discovered**:
1. `module.manifest.json` - Structured metadata (3 exist, schema v3.0.0)
2. `MODULE_MANIFEST.json` - Legacy format (found in consciousness/)
3. `lukhas_context.md` - AI development context (10 files)
4. `claude.me` - Claude Desktop format (10 files)
5. `README.md` - Human documentation (443 files)
6. `directory_index.json` - Directory metadata (found in consciousness/)
7. `__init__.py` - Required for all packages (780 exist)

---

## Artifact Type Analysis

### 1. `module.manifest.json` (Schema v3.0.0)

**Count**: 3 files
- `/candidate/module.manifest.json`
- `/lukhas/module.manifest.json`
- `/lukhas/core/module.manifest.json`

**Template Structure**:
```json
{
  "schema_version": "3.0.0",
  "module": "module_name",
  "description": "Brief description",
  
  // Core metadata
  "layout": {
    "code_layout": "package-root",
    "paths": {
      "assets": "assets",
      "code": ".",
      "config": "config",
      "docs": "docs",
      "tests": "tests"
    }
  },
  
  // MATRIZ integration
  "matrix": {
    "contract": "",
    "gates_profile": "standard",
    "lane": "L2"
  },
  
  // Identity & Auth
  "identity": {
    "requires_auth": false,
    "scopes": [],
    "tiers": []
  },
  
  // Observability
  "observability": {
    "otel_semconv_version": "1.37.0",
    "required_spans": ["lukhas.module.operation"]
  },
  
  // Testing
  "testing": {
    "coverage_observed": 0.0,
    "observed_at": "ISO-8601 timestamp"
  },
  
  // Ownership
  "ownership": {
    "codeowners": ["@lukhas-core"],
    "team": "Core"
  },
  
  // APIs & Features (extracted by automation)
  "apis": {},
  "features": [],
  "contracts": [],
  "dependencies": [],
  
  // Links
  "links": {
    "docs": "./docs/README.md",
    "issues": "https://github.com/LukhasAI/Lukhas/issues",
    "repo": "https://github.com/LukhasAI/Lukhas"
  },
  
  // Runtime
  "runtime": {
    "entrypoints": [],
    "language": "python"
  },
  
  // Tags
  "tags": ["tag1", "tag2"],
  
  // Tokenization (blockchain integration)
  "tokenization": {
    "chain": "none",
    "enabled": false
  },
  
  // Provenance (auto-generated metadata)
  "_provenance": {
    "apis": {
      "confidence": "low",
      "extracted_at": "ISO-8601 timestamp",
      "reasons": ["no_apis"],
      "sources": ["ast:__init__.py"]
    },
    "features": {
      "confidence": "low",
      "extracted_at": "ISO-8601 timestamp",
      "reasons": ["weak_evidence"],
      "sources": ["claude.me:bullets", "claude.me:headers"]
    }
  },
  
  // Extended metadata (advanced modules)
  "x_legacy": {
    "agent_guidance": {},
    "component_inventory": {},
    "directory_metadata": {},
    "performance_metadata": {},
    "relationships": {},
    "schema_references": []
  }
}
```

**Key Observations**:
- **Schema evolution**: v1.0.0 (lukhas/core, lukhas/) vs v3.0.0 (candidate/)
- **Auto-generation**: `_provenance` section shows automated extraction from AST
- **MATRIZ field**: Called `matrix` (not `matriz`) - lowercase, British spelling
- **Advanced metadata**: `x_legacy` section in candidate/ manifest is extensive
- **Component inventory**: candidate/ manifest includes detailed component analysis

---

### 2. `MODULE_MANIFEST.json` (Legacy Format)

**Count**: Found in well-documented modules (e.g., consciousness/)

**Template Structure**:
```json
{
  "module": "MODULE_NAME",
  "version": "2.0.0",
  "description": "Brief description",
  "path": "module/path/",
  
  "submodules": {
    "submodule_name": {
      "description": "submodule description",
      "is_hybrid": false,
      "path": "module/path/submodule/",
      "files": [],
      "colony_config": {
        "can_propagate": true,
        "base_colony": "base_colony.py"
      }
    }
  },
  
  "hybrid_components": [],
  "dependencies": [],
  "exports": [],
  
  "neuroplastic_config": {
    "can_reorganize": true,
    "stress_priority": 1,
    "hormone_receptors": ["cortisol", "dopamine"]
  },
  
  "tags": ["#TAG:tag1", "#TAG:tag2"],
  "enhanced": true,
  "enhancement_date": "ISO-8601",
  "integrated_directories": [],
  "last_reorganization": "ISO-8601",
  
  "research_validation": {
    "research_area": {
      "status": "validated",
      "research_source": "Source reference"
    }
  }
}
```

**Key Observations**:
- **Bio-inspired**: Includes `neuroplastic_config`, `hormone_receptors`
- **Colony system**: Integration with LUKHAS colony architecture
- **Research validation**: Links to consciousness research
- **Hybrid tracking**: Identifies hybrid components

---

### 3. `lukhas_context.md` (AI Development Context)

**Count**: 10 files
**Purpose**: Vendor-neutral AI development guidance

**Template Structure**:
```markdown
---
status: wip
type: documentation
---
# LUKHAS AI Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

---

# [Module Name] Development
*[N]+ Components - Constellation Framework [Star] Pillar*

## [Module] Development Overview

[Module description with Constellation Framework alignment]

### **Development Scope**
- **Components**: N+ modules and systems
- **Constellation Role**: Integration with 8-star system
- **Architecture**: MATRIZ pipeline integration
- **Integration**: Star coordination patterns

### **[Module] Architecture**
```
[Module] Development Ecosystem
├── subdirectory/
│   └── file.py
```

## 🧠 [Module] Architecture Components

[Detailed component breakdown]

## 🔗 Integration Points

[How module integrates with Constellation Framework]

## 📋 Development Guidelines

[Development best practices]

## 🎯 MATRIZ Pipeline Integration

[MATRIZ node assignments]

## 🧪 Testing Strategy

[Test coverage and quality standards]
```

**Key Observations**:
- **Dual format**: Identical content in `claude.me` for Claude Desktop
- **Constellation alignment**: Always references 8-star framework
- **MATRIZ integration**: Pipeline node assignments
- **Component inventory**: Visual tree structures
- **42 total files**: Distributed throughout repository (not just 10 in candidate/lukhas)

---

### 4. `README.md` (Human Documentation)

**Count**: 443 files
**Purpose**: Human-readable module documentation

**Variations**:
- Simple README (basic description)
- Enhanced README (comprehensive guide)
- README_ENHANCED.md (advanced modules)
- DEV_GUIDE.md, USER_GUIDE.md (consciousness/)

**Standard Sections**:
1. Overview
2. Features
3. Installation
4. Usage
5. API Reference
6. Contributing
7. License

---

### 5. `directory_index.json` (Directory Metadata)

**Count**: Found in major modules

**Template Structure**:
```json
{
  "module": "module_name",
  "path": "module/path/",
  "python_files": [
    {"filename": "file.py", "exports": [], "component_type": "TYPE"}
  ],
  "subdirectories": [
    {"name": "subdir", "component_count": N, "has_index": true}
  ],
  "documentation": [
    {"filename": "lukhas_context.md", "type": "context"}
  ],
  "metadata": {
    "last_updated": "ISO-8601",
    "lane": "development",
    "matriz_pipeline_integration": {},
    "t4_compliance_level": "experimental"
  }
}
```

---

## Documentation Coverage Analysis

### Current Coverage by Artifact Type

**Module-Level Artifacts** (per-module files):

| Artifact Type | Count | Coverage | Purpose |
|--------------|-------|----------|---------|
| `__init__.py` | 780 | 100% | Python package marker |
| `module.manifest.json` | 3 | 0.4% | **MATRIZ compliance metadata** |
| `MODULE_MANIFEST.json` | ~10 | 1.3% | Legacy colony/bio metadata |
| `lukhas_context.md` | 42 | 5.4% | AI development context |
| `claude.me` | 42 | 5.4% | Claude Desktop format |
| `README.md` | 443 | 56.8% | Human documentation |
| `directory_index.json` | ~10 | 1.3% | Directory metadata |

**Repository-Level Artifacts** (system-wide registries):

| Artifact Type | Location | Purpose |
|--------------|----------|---------|
| `MODULE_INDEX.md` | Root | Master module navigation index |
| `MODULE_REGISTRY.json` | `docs/_generated/` (1.4M) | Complete module registry with 149 documented modules |
| `META_REGISTRY.json` | `docs/_generated/` (56K) | Fused analytics and metadata |
| `RELEASE_MANIFEST.json` | Root (18K) | T4/0.01% release quality metrics |
| `CONSCIOUSNESS_CONTRACT_REGISTRY.json` | `docs/` | Consciousness system contracts |
| **Deep Search Indexes** (17 files) | `docs/reports_root/deep_search/` | Code analysis artifacts |
| - `API_ENDPOINTS.txt` | 23K | All API endpoints |
| - `CLASSES_INDEX.txt` | 445K | All class definitions |
| - `FUNCTIONS_INDEX.txt` | 1.3M | All function definitions |
| - `SYMBOLS_INDEX.tsv` | 1.9M | Complete symbol index |
| - `MODULE_MAP.json` | 2.9M | Complete module mapping |
| - `IMPORT_GRAPH.dot` | 53K | Import dependency graph |
| - `TODO_FIXME_INDEX.txt` | 56K | All TODO/FIXME markers |
| **Ledgers** (~25 files) | `manifests/.ledger/` | NDJSON operational ledgers |
| - `api.ndjson` | | API module ledger |
| - `consciousness.ndjson` | | Consciousness ledger |
| - `governance_extended.ndjson` | | Governance ledger |
| - `observability.ndjson` | | Observability metrics |
| **Matrix Contracts** (~50 files) | `contracts/` | MATRIZ pipeline contracts |
| - `matrix_consciousness.json` | 4.6K | Consciousness contract |
| - `matrix_api.json` | 4.0K | API contract |
| - `matrix_bio.json` | 4.0K | Bio systems contract |
| **Schemas** (~20 files) | `schemas/` | JSON Schema definitions |
| - `directory_index.schema.json` | 8.7K | Directory index schema |
| - `consciousness_component.schema.json` | 7.5K | Consciousness component schema |
| - `matriz_module_compliance.schema.json` | NEW | MATRIZ compliance schema v1.0.0 |

### Gap Analysis

**Critical Gaps**:
1. **MATRIZ compliance**: 777 modules (99.6%) lack `module.manifest.json`
2. **AI context**: 738 modules (94.6%) lack `lukhas_context.md`
3. **Directory metadata**: ~770 modules (98.7%) lack `directory_index.json`

**Human Documentation**:
- 443 README.md files exist (56.8% coverage)
- Quality varies widely
- Many are stubs or outdated

---

## Schema Analysis

### Schema Evolution

| Schema Version | Files | Status |
|----------------|-------|--------|
| v1.0.0 | 2 | Legacy (lukhas/, lukhas/core/) |
| v3.0.0 | 1 | Current (candidate/) |
| MODULE_MANIFEST | ~5-10 | Bio/colony format |

### Schema Gaps in v3.0.0

Comparing our new MATRIZ compliance schema vs existing v3.0.0:

**Missing in Current Schema**:
1. **MATRIZ integration** (only has `matrix` with minimal fields)
2. **Constellation alignment** (no star mapping)
3. **Capabilities array** (has `features` but low confidence)
4. **Trinity aspects** (⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian)
5. **Exports detail** (classes, functions, constants)
6. **Internal dependencies** (has `dependencies: []` but empty)

**Present in v3.0.0**:
1. Provenance tracking (`_provenance`)
2. Agent guidance (`x_legacy.agent_guidance`)
3. Component inventory (`x_legacy.component_inventory`)
4. Performance metadata (`x_legacy.performance_metadata`)
5. Testing coverage (`testing.coverage_observed`)
6. Observability spans (`observability.required_spans`)

---

## Rollout Strategy Recommendations

### Phase 1: Schema Unification (CRITICAL)

**Action**: Merge best of both schemas
- ✅ Keep v3.0.0 `_provenance` (auto-generation metadata)
- ✅ Keep v3.0.0 `x_legacy` (rich component inventory)
- ✅ Add new `matriz_integration` section (not just `matrix`)
- ✅ Add new `constellation_alignment` section
- ✅ Add new `capabilities` array (replace weak `features`)
- ✅ Enhance `dependencies` with internal/external split

**Result**: `schemas/matriz_module_compliance.schema.json` v1.0.0 (already created)

### Phase 2: Automated Generation (HIGH PRIORITY)

**Action**: Build intelligent manifest generator
- Parse `__init__.py` for exports (AST analysis)
- Infer MATRIZ node from path/code patterns
- Infer Constellation star from module purpose
- Extract dependencies from imports
- Copy metadata from README.md if exists
- Generate with `manifest_generated: true` flag

**Script**: `scripts/generate_module_manifests.py` (to be created)

### Phase 3: Template Hierarchy (MEDIUM)

**Templates Needed**:
1. **Minimal template** (low-priority supporting modules)
   - Basic metadata, inferred MATRIZ node, simple capabilities
2. **Standard template** (most modules)
   - Full MATRIZ integration, Constellation alignment, dependencies
3. **Comprehensive template** (critical modules)
   - All fields, manual validation, research links, observability

### Phase 4: Validation Pipeline (MEDIUM)

**Validation Levels**:
1. **Schema validation**: JSON Schema compliance
2. **MATRIZ validation**: Node assignments valid
3. **Constellation validation**: Star mappings correct
4. **Dependency validation**: No circular deps, lane compliance
5. **Quality validation**: Coverage baselines, T4 tier assignments

### Phase 5: Integration (LOW - Post-Generation)

**Integration Points**:
- Update `MODULE_INDEX.md` with all 780 modules
- Regenerate `MODULE_REGISTRY.json` with new manifests
- Update `META_REGISTRY.json` with MATRIZ/Constellation analytics
- Create `MATRIZ_NODE_TO_MODULE_MAPPING.json`
- Generate dependency graphs

---

## Next Steps (Immediate)

### Step 1: Finalize Schema
- ✅ **DONE**: Created `schemas/matriz_module_compliance.schema.json`
- **Review**: Validate against existing v3.0.0 manifests
- **Adjust**: Add any missing critical fields

### Step 2: Create Generator Script
- **Input**: Module path, `__init__.py`, existing README.md
- **Process**: AST parsing, pattern inference, metadata extraction
- **Output**: `module.manifest.json` (schema v1.0.0 compliant)
- **Flags**: `--dry-run`, `--template [minimal|standard|comprehensive]`, `--validate`

### Step 3: Pilot Generation
- **Target**: 10 modules across priority tiers
  - 2 critical (identity, guardian)
  - 3 high (consciousness, memory, governance)
  - 3 medium (bridge, adapter modules)
  - 2 low (supporting utilities)
- **Review**: Manual validation of generated manifests
- **Adjust**: Refine inference algorithms

### Step 4: Batch Generation
- **Process**: Generate all 777 missing manifests
- **Review**: Statistical validation, spot-check samples
- **Commit**: Bulk commit with proper attribution

### Step 5: Validation & Integration
- **Validate**: Run schema validation across all 780 manifests
- **Integrate**: Update master registries and indexes
- **Verify**: MATRIZ rollout audit readiness

---

## Template Files to Create

1. `templates/module.manifest.minimal.json` - Minimal template
2. `templates/module.manifest.standard.json` - Standard template
3. `templates/module.manifest.comprehensive.json` - Comprehensive template
4. `scripts/generate_module_manifests.py` - Generator script
5. `scripts/validate_module_manifests.py` - Validation script
6. `docs/guides/MODULE_MANIFEST_GUIDE.md` - Author guide

---

## Summary

**What We Have**:
- 3 existing `module.manifest.json` files (v1.0.0 and v3.0.0)
- 1 comprehensive new schema (v1.0.0 MATRIZ compliance)
- 780 complete module inventory with inferred MATRIZ nodes
- Rich component inventory in existing manifests (`x_legacy` section)
- Established patterns for AI context files (lukhas_context.md, claude.me)

**What We Need**:
- 777 new module manifests (99.6% coverage gap)
- Intelligent generator script with AST parsing
- Template hierarchy (minimal/standard/comprehensive)
- Validation pipeline for schema/MATRIZ/Constellation compliance
- Integration with existing registries and indexes

**Strategic Approach**:
- **Automated generation** for 90% of modules (standard template)
- **Manual enhancement** for 10% critical modules (comprehensive template)
- **Continuous validation** to maintain T4/0.01% quality standards
- **Incremental rollout** with pilot before bulk generation

**Estimated Effort**:
- Generator script: 8-10 hours
- Pilot generation + review: 4-6 hours
- Bulk generation: 2-3 hours (automated)
- Validation + integration: 6-8 hours
- **Total**: 20-27 hours

---

**The MATRIZ rollout audit can proceed once we have 100% module manifest coverage with validated MATRIZ pipeline integration and Constellation Framework alignment.**

*⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian*
