# LUKHAS Module Artifact Ecosystem - Quick Reference

**Last Updated**: 2025-10-11  
**Purpose**: Quick reference for module documentation artifacts and standards

---

## 📚 Artifact Types at a Glance

**Module-Level Artifacts** (per-module documentation):

| Artifact | Purpose | Format | Priority | Coverage |
|----------|---------|--------|----------|----------|
| `module.manifest.json` | MATRIZ compliance metadata | JSON (schema v1.0.0) | **CRITICAL** | 0.4% (3/780) |
| `lukhas_context.md` | AI development context | Markdown | **HIGH** | 5.4% (42/780) |
| `claude.me` | Claude Desktop context | Markdown | **HIGH** | 5.4% (42/780) |
| `README.md` | Human documentation | Markdown | **MEDIUM** | 56.8% (443/780) |
| `MODULE_MANIFEST.json` | Legacy bio/colony metadata | JSON (legacy) | **LOW** | ~1.3% (10/780) |
| `directory_index.json` | Directory metadata | JSON | **LOW** | ~1.3% (10/780) |
| `__init__.py` | Python package marker | Python | **REQUIRED** | 100% (780/780) |

**Repository-Level Artifacts** (system-wide registries & indexes):

| Artifact | Location | Size | Purpose |
|----------|----------|------|---------|
| **Master Registries** | | | |
| `MODULE_INDEX.md` | Root | 20K | Master module navigation (149 documented) |
| `MODULE_REGISTRY.json` | `docs/_generated/` | 1.4M | Complete module registry (149 modules) |
| `META_REGISTRY.json` | `docs/_generated/` | 56K | Fused analytics and metadata |
| `RELEASE_MANIFEST.json` | Root | 18K | T4/0.01% release quality metrics |
| **Consciousness & Contracts** | | | |
| `CONSCIOUSNESS_CONTRACT_REGISTRY.json` | `docs/` | - | Consciousness system contracts |
| Matrix Contracts (~50 files) | `contracts/` | 4-5K each | MATRIZ pipeline contracts |
| - `matrix_consciousness.json` | `contracts/` | 4.6K | Consciousness contract |
| - `matrix_api.json` | `contracts/` | 4.0K | API contract |
| - `matrix_bio.json` | `contracts/` | 4.0K | Bio systems contract |
| **Deep Search Indexes** (17 files) | `docs/reports_root/deep_search/` | 6.8M total | |
| `API_ENDPOINTS.txt` | | 23K | All API endpoints catalog |
| `CLASSES_INDEX.txt` | | 445K | All class definitions |
| `FUNCTIONS_INDEX.txt` | | 1.3M | All function definitions |
| `SYMBOLS_INDEX.tsv` | | 1.9M | Complete symbol index (TSV) |
| `MODULE_MAP.json` | | 2.9M | Complete module dependency mapping |
| `IMPORT_GRAPH.dot` | | 53K | GraphViz import dependency graph |
| `TODO_FIXME_INDEX.txt` | | 56K | All TODO/FIXME markers |
| `PACKAGE_MAP.txt` | | 26K | Package structure map |
| **Operational Ledgers** (~25 files) | `manifests/.ledger/` | NDJSON | Event-sourced ledgers |
| `api.ndjson` | | - | API module operational ledger |
| `consciousness.ndjson` | | - | Consciousness events ledger |
| `governance_extended.ndjson` | | - | Governance events ledger |
| `observability.ndjson` | | - | Observability metrics ledger |
| `freeze.ndjson` | | - | Production freeze events |
| **JSON Schemas** (~20 files) | `schemas/` | 1-9K each | Type definitions |
| `directory_index.schema.json` | | 8.7K | Directory index validation |
| `consciousness_component.schema.json` | | 7.5K | Consciousness component schema |
| `matriz_module_compliance.schema.json` | | NEW | **MATRIZ compliance schema v1.0.0** |
| **Generated Reports** (~20 files) | `docs/_generated/` | Various | CI/CD artifacts |
| `COVERAGE_BENCHMARK_COMPLETE.md` | | 12K | Coverage benchmarks |
| `DOCUMENTATION_MAP.md` | | 7.9K | Documentation structure |
| `SITE_MAP.md` | | 137K | Complete site map |

---

## 🎯 Primary Artifact: `module.manifest.json`

### Location
```
<module_path>/module.manifest.json
```

### Schema
```
schemas/matriz_module_compliance.schema.json v1.0.0
```

### Required Fields
```json
{
  "schema_version": "1.0.0",
  "module": {
    "name": "dot.separated.name",
    "path": "filesystem/path",
    "lane": "candidate|lukhas|core|matriz|products",
    "type": "package"
  },
  "matriz_integration": {
    "status": "not_integrated|partial|integrated|optimized",
    "pipeline_nodes": ["memory", "attention", "thought", "risk", "intent", "action"],
    "cognitive_function": "primary_function"
  },
  "constellation_alignment": {
    "primary_star": "⚛️ Anchor (Identity)",
    "trinity_aspects": ["⚛️ Identity", "🧠 Consciousness", "🛡️ Guardian"]
  },
  "capabilities": [
    {"name": "capability_name", "type": "api|processing|storage|..."}
  ],
  "metadata": {
    "created": "ISO-8601",
    "last_updated": "ISO-8601"
  }
}
```

### Auto-Generation Flags
```json
{
  "metadata": {
    "manifest_generated": true  // Indicates automated generation
  },
  "_provenance": {
    "apis": {
      "confidence": "low|medium|high",
      "sources": ["ast:__init__.py", "readme:capabilities"]
    }
  }
}
```

---

## 🧠 MATRIZ Pipeline Nodes

### Node Types & Module Classification

| MATRIZ Node | Purpose | Example Modules | Count |
|-------------|---------|-----------------|-------|
| **memory** | Storage, retrieval, consolidation | memory/, fold/ | 97 |
| **attention** | Focus, awareness, filtering | awareness/ | 12 |
| **thought** | Reasoning, decision-making | consciousness/, cognitive/ | 126 |
| **risk** | Ethics, governance, validation | guardian/, governance/, ethics/ | 111 |
| **intent** | Planning, orchestration | orchestration/, coordination/ | 143 |
| **action** | Execution, API, interfaces | api/, bridge/, adapter/ | 70 |
| **supporting** | Utilities, helpers | utils/, tools/ | 221 |

---

## 🌟 Constellation Framework Stars

### 8-Star Dynamic System

| Star | Symbol | Purpose | Example Modules |
|------|--------|---------|-----------------|
| **Anchor** | ⚛️ | Identity, authentication | identity/, auth/, lambda/ |
| **Trail** | ✦ | Memory, temporal tracking | memory/, fold/, temporal/ |
| **Horizon** | 🔬 | Vision, interfaces, patterns | interface/, ui/, pattern/ |
| **Living** | 🌱 | Bio-inspired systems | bio/, neuroplastic/, hormone/ |
| **Drift** | 🌙 | Dream, creativity, exploration | dream/, creative/, exploration/ |
| **North** | ⚖️ | Ethics, values | ethics/, values/ |
| **Watch** | 🛡️ | Guardian, security, drift detection | guardian/, security/, compliance/ |
| **Oracle** | 🔮 | Quantum, prediction, ambiguity | quantum/, oracle/, prediction/ |

### Trinity Aspects

| Aspect | Symbol | Purpose |
|--------|--------|---------|
| **Identity** | ⚛️ | Self-representation, ΛID |
| **Consciousness** | 🧠 | Awareness, cognition |
| **Guardian** | 🛡️ | Ethics, protection |

---

## 📝 AI Context Files

### `lukhas_context.md` Template

```markdown
---
status: wip|active|stable
type: documentation
---
# LUKHAS AI Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

---

# [Module Name] Development
*[N]+ Components - Constellation Framework [Star] Pillar*

## [Module] Development Overview
[Description with Constellation Framework alignment]

### **Development Scope**
- **Components**: N+ modules and systems
- **Constellation Role**: Integration with 8-star system
- **Architecture**: MATRIZ pipeline integration
- **Integration**: Star coordination patterns

### **[Module] Architecture**
```
[Module] Ecosystem
├── subdirectory/
│   └── file.py
```

## 🧠 [Module] Architecture Components
[Detailed component breakdown]

## 🔗 Integration Points
[Constellation Framework integration]

## 📋 Development Guidelines
[Best practices]

## 🎯 MATRIZ Pipeline Integration
[Pipeline node assignments]

## 🧪 Testing Strategy
[Test coverage and quality]
```

### Sync Requirements

- **Bidirectional sync**: `lukhas_context.md` ↔ `claude.me`
- **Identical content**: Only format differs
- **Update both**: When modifying either file
- **Sync script**: `scripts/sync_context_files.sh --bidirectional`

---

## 🔄 Lane System & Import Rules

### Lane Hierarchy

```
candidate/ → lukhas/ → MATRIZ → products/
   ↓           ↓         ↓         ↓
  L2          L3        L4        L5
```

### Import Isolation Rules

| Lane | Can Import From | Cannot Import From |
|------|----------------|-------------------|
| **candidate** | core/, matriz/ | lukhas/, products/ |
| **lukhas** | core/, matriz/, universal_language/ | products/ |
| **core** | matriz/ | candidate/, lukhas/ |
| **matriz** | - | All (foundation layer) |
| **products** | lukhas/, core/, matriz/ | candidate/ |

### Validation
```bash
make lane-guard  # Validate import boundaries
```

---

## 🧪 Quality Tiers (T4 System)

| Tier | Level | Coverage | Latency | Use Cases |
|------|-------|----------|---------|-----------|
| **T1** | Critical | >90% | <100ms | Identity, Guardian, Core API |
| **T2** | Important | >80% | <250ms | MATRIZ nodes, Memory, Orchestration |
| **T3** | Standard | >70% | <500ms | Standard modules, Integrations |
| **T4** | Experimental | >50% | <1s | Research, Prototypes, Candidates |

### T4/0.01% Standard
- **Reliability**: 99.99% uptime
- **Error rate**: <0.01% of operations
- **Test coverage**: Tier-appropriate baselines
- **Documentation**: 100% public API coverage

---

## 🛠️ Generation Commands

### Generate Module Inventory
```bash
python scripts/generate_complete_inventory.py \
  --scan candidate lukhas \
  --output docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --verbose
```

### Generate Module Manifests (Coming Soon)
```bash
python scripts/generate_module_manifests.py \
  --template standard \
  --validate \
  --dry-run \
  candidate/consciousness/
  
# Bulk generation
python scripts/generate_module_manifests.py \
  --template standard \
  --batch \
  --input docs/audits/COMPLETE_MODULE_INVENTORY.json
```

### Validate Manifests
```bash
python scripts/validate_module_manifests.py \
  --schema schemas/matriz_module_compliance.schema.json \
  --check-matriz \
  --check-constellation \
  --check-dependencies
```

---

## 📊 Current Status (2025-10-11)

### Coverage Statistics

| Metric | Value | Target | Gap |
|--------|-------|--------|-----|
| Total modules | 780 | 780 | 0 |
| module.manifest.json | 3 (0.4%) | 780 (100%) | 777 |
| lukhas_context.md | 42 (5.4%) | 780 (100%) | 738 |
| README.md | 443 (56.8%) | 780 (100%) | 337 |
| MATRIZ integration | Unknown | 780 (100%) | TBD |

### Priority Breakdown (From Inventory)

| Priority | Count | Percentage |
|----------|-------|------------|
| **Documented** | 3 | 0.4% |
| **Critical** | ~150 | 19.2% |
| **High** | ~250 | 32.1% |
| **Medium** | ~200 | 25.6% |
| **Low** | ~177 | 22.7% |

---

## 🚀 Rollout Phase Status

- [x] **Phase 1**: Schema Unification ✅ **COMPLETE**
- [ ] **Phase 2**: Automated Generation 🔨 **IN PROGRESS**
- [ ] **Phase 3**: Template Hierarchy ⏳ **PENDING**
- [ ] **Phase 4**: Validation Pipeline ⏳ **PENDING**
- [ ] **Phase 5**: Integration ⏳ **PENDING**

---

## 📚 Related Documentation

- **Comprehensive Audit**: `docs/audits/MODULE_ARTIFACT_AUDIT.md`
- **Module Inventory**: `docs/audits/COMPLETE_MODULE_INVENTORY.json`
- **MATRIZ Mapping Plan**: `docs/audits/MATRIZ_MODULE_MAPPING_PLAN.md`
- **Schema Definition**: `schemas/matriz_module_compliance.schema.json`
- **Master Index**: `MODULE_INDEX.md`
- **Agent Coordination**: `AGENTS.md`

---

## 🎯 Key Takeaways

1. **Only 3 modules (0.4%) have MATRIZ-compliant manifests** - this is the critical gap
2. **777 modules need documentation** - automated generation is essential
3. **Schema v1.0.0 is ready** - merges best of existing schemas
4. **MATRIZ nodes already inferred** - from module inventory analysis
5. **Rollout plan is 20-27 hours** - mostly automated generation

**Next Action**: Create `scripts/generate_module_manifests.py` to automate manifest creation for 777 undocumented modules.

---

*⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian*
