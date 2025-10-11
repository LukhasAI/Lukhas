---
status: active
type: action-plan
created: 2025-10-09
priority: critical
purpose: Complete module mapping and MATRIZ compliance documentation for GPT-5 audit
---

# 🎯 MATRIZ Module Mapping & Compliance Plan
**Complete Documentation for 780 Cognitive Modules**

**Created**: October 9, 2025  
**Priority**: CRITICAL - Required for MATRIZ rollout audit  
**Target**: 100% module documentation with MATRIZ compliance

---

## 🚨 **Current State Analysis**

### **The Gap**
- **Total Modules**: 780 Python modules (636 candidate + 144 lukhas)
- **Documented**: 149 modules with module.manifest.json (19%)
- **Undocumented**: 631 modules without manifests (81%)
- **Status**: ⚠️ **CRITICAL GAP** - Insufficient for audit

### **What's Missing**
For the **631 undocumented modules**, we need:
1. Module manifest files (module.manifest.json)
2. MATRIZ compliance schema
3. Capability definitions
4. Dependency mappings
5. MATRIZ node integration status
6. API surface documentation
7. Entry points and configuration

---

## 📋 **Required Deliverables**

### **1. Complete Module Inventory** 
**File**: `docs/audits/COMPLETE_MODULE_INVENTORY.json`  
**Purpose**: Master catalog of all 780 modules with metadata  
**Status**: 🔨 TO CREATE

**Contents**:
```json
{
  "total_modules": 780,
  "inventory": [
    {
      "module_name": "candidate.core.identity",
      "path": "candidate/core/identity",
      "type": "package",
      "has_manifest": false,
      "has_init": true,
      "python_files": 15,
      "subdirectories": 3,
      "matriz_node": "identity",
      "constellation_star": "⚛️ Anchor",
      "primary_capability": "TBD",
      "dependencies": [],
      "status": "needs_documentation"
    }
  ]
}
```

**Effort**: 2-3 hours (automated script)

---

### **2. MATRIZ Compliance Schema**
**File**: `schemas/matriz_module_compliance.schema.json`  
**Purpose**: Standard schema for MATRIZ-compliant module documentation  
**Status**: 🔨 TO CREATE

**Contents**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MATRIZ Module Compliance Schema",
  "type": "object",
  "required": [
    "module",
    "matriz_integration",
    "capabilities",
    "dependencies",
    "constellation_alignment"
  ],
  "properties": {
    "module": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "path": {"type": "string"},
        "lane": {"enum": ["candidate", "lukhas", "matriz", "products"]},
        "python_files": {"type": "integer"},
        "entry_points": {"type": "array"}
      }
    },
    "matriz_integration": {
      "type": "object",
      "properties": {
        "status": {"enum": ["integrated", "partial", "pending", "not_applicable"]},
        "pipeline_nodes": {"type": "array", "items": {"enum": ["memory", "attention", "thought", "risk", "intent", "action"]}},
        "cognitive_function": {"type": "string"}
      }
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "api_endpoint": {"type": "string"},
          "authentication_required": {"type": "boolean"}
        }
      }
    },
    "constellation_alignment": {
      "type": "object",
      "properties": {
        "primary_star": {"enum": ["⚛️ Anchor", "✦ Trail", "🔬 Horizon", "🌱 Living", "🌙 Drift", "⚖️ North", "🛡️ Watch", "⚛️ Ambiguity"]},
        "integration_level": {"type": "number", "minimum": 0, "maximum": 100}
      }
    }
  }
}
```

**Effort**: 1-2 hours

---

### **3. Module Manifest Generator Script**
**File**: `scripts/generate_module_manifests.py`  
**Purpose**: Automated generation of manifests for 631 undocumented modules  
**Status**: 🔨 TO CREATE

**Functionality**:
- Scan all Python packages (directories with __init__.py)
- Extract module metadata (files, imports, exports)
- Infer capabilities from code analysis
- Map to MATRIZ nodes based on directory structure
- Generate compliant module.manifest.json files

**Usage**:
```bash
python scripts/generate_module_manifests.py \
  --scan candidate/ lukhas/ \
  --output-dir . \
  --schema schemas/matriz_module_compliance.schema.json \
  --dry-run  # Preview before creating files
```

**Effort**: 6-8 hours (comprehensive AST analysis)

---

### **4. Gap Analysis Report**
**File**: `docs/audits/MODULE_DOCUMENTATION_GAP_ANALYSIS.md`  
**Purpose**: Detailed analysis of 631 undocumented modules  
**Status**: 🔨 TO CREATE

**Sections**:
1. **Executive Summary**
   - Total gaps by lane (candidate vs lukhas)
   - Priority classification (critical, high, medium, low)
   - MATRIZ node coverage analysis

2. **Critical Modules** (needs immediate documentation)
   - Core MATRIZ pipeline modules
   - Identity/authentication modules
   - Guardian/ethics modules
   - API gateway modules

3. **Module Classification**
   - By lane (candidate/lukhas)
   - By Constellation star
   - By MATRIZ node
   - By priority for rollout

4. **Remediation Plan**
   - Automated generation approach (80%)
   - Manual review requirements (20%)
   - Timeline and effort estimates

**Effort**: 3-4 hours

---

### **5. MATRIZ Node Mapping**
**File**: `docs/audits/MATRIZ_NODE_TO_MODULE_MAPPING.json`  
**Purpose**: Complete mapping of all 780 modules to MATRIZ pipeline nodes  
**Status**: 🔨 TO CREATE

**Structure**:
```json
{
  "matriz_nodes": {
    "memory": {
      "modules": 87,
      "module_list": [
        "candidate.memory.fold_manager",
        "candidate.memory.temporal",
        "lukhas.memory.integration"
      ],
      "integration_status": "85%",
      "capabilities": ["fold-based storage", "temporal organization", "cascade prevention"]
    },
    "attention": {
      "modules": 45,
      "module_list": ["candidate.core.attention", "..."],
      "integration_status": "70%",
      "capabilities": ["pattern recognition", "focus mechanisms"]
    },
    "thought": {
      "modules": 120,
      "module_list": ["candidate.consciousness.reasoning", "..."],
      "integration_status": "60%",
      "capabilities": ["symbolic reasoning", "inference", "decision making"]
    },
    "risk": {
      "modules": 55,
      "module_list": ["candidate.governance.guardian", "ethics.drift_detection", "..."],
      "integration_status": "90%",
      "capabilities": ["ethical validation", "drift detection", "constitutional AI"]
    },
    "intent": {
      "modules": 78,
      "module_list": ["candidate.core.orchestration", "..."],
      "integration_status": "65%",
      "capabilities": ["goal formation", "planning", "coordination"]
    },
    "action": {
      "modules": 95,
      "module_list": ["candidate.bridge.api", "lukhas.api", "..."],
      "integration_status": "75%",
      "capabilities": ["API execution", "external integration", "response generation"]
    },
    "supporting": {
      "modules": 320,
      "module_list": ["candidate.core.types", "utilities", "..."],
      "integration_status": "50%",
      "capabilities": ["utilities", "types", "infrastructure"]
    }
  }
}
```

**Effort**: 4-6 hours (automated inference + manual validation)

---

### **6. Capability Matrix**
**File**: `docs/audits/MODULE_CAPABILITY_MATRIX.xlsx` / `.csv`  
**Purpose**: Comprehensive capability listing for all 780 modules  
**Status**: 🔨 TO CREATE

**Columns**:
- Module Name
- Path
- Lane
- MATRIZ Node
- Constellation Star
- Primary Capabilities (list)
- API Endpoints (count)
- Authentication Required (Y/N)
- External Dependencies
- Internal Dependencies
- Test Coverage %
- Documentation Status
- Manifest Status
- Priority for Audit

**Effort**: 2-3 hours (generated from inventory)

---

### **7. Complete Dependency Graph**
**File**: `docs/audits/COMPLETE_MODULE_DEPENDENCY_GRAPH.dot` + `.svg`  
**Purpose**: Visual dependency graph for all 780 modules  
**Status**: 🔨 TO CREATE

**Features**:
- Node colors by lane (candidate=blue, lukhas=green)
- Edge thickness by dependency strength
- Clusters by MATRIZ node
- Highlight critical paths
- Identify circular dependencies
- Show lane boundary violations

**Generation**:
```bash
python scripts/generate_dependency_graph.py \
  --modules docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --output docs/audits/COMPLETE_MODULE_DEPENDENCY_GRAPH.dot \
  --format svg
```

**Effort**: 4-6 hours (analysis + visualization)

---

### **8. MATRIZ Integration Checklist**
**File**: `docs/audits/MATRIZ_INTEGRATION_CHECKLIST.md`  
**Purpose**: Per-module checklist for MATRIZ compliance validation  
**Status**: 🔨 TO CREATE

**Checklist Items** (per module):
- [ ] Module manifest exists (module.manifest.json)
- [ ] MATRIZ node assignment documented
- [ ] Constellation star alignment defined
- [ ] Capabilities documented with descriptions
- [ ] API surface documented (if applicable)
- [ ] Dependencies mapped (internal + external)
- [ ] Entry points defined
- [ ] Authentication requirements specified
- [ ] Performance SLOs defined
- [ ] Test coverage ≥30%
- [ ] Integration tests exist
- [ ] Documentation complete
- [ ] Lane boundaries respected
- [ ] Import hygiene validated

**Effort**: 1-2 hours (template creation)

---

### **9. Module Health Dashboard**
**File**: `docs/audits/MODULE_HEALTH_DASHBOARD.html` (interactive)  
**Purpose**: Live dashboard showing module health and MATRIZ readiness  
**Status**: 🔨 TO CREATE

**Metrics per Module**:
- Documentation completeness (0-100%)
- MATRIZ integration status
- Test coverage percentage
- Dependency health
- API compliance
- Performance SLOs met
- Security validation status
- Audit readiness score

**Effort**: 6-8 hours (dashboard + data pipeline)

---

### **10. Missing Manifests Report**
**File**: `docs/audits/MISSING_MANIFESTS_PRIORITY_LIST.md`  
**Purpose**: Prioritized list of 631 modules needing manifests  
**Status**: 🔨 TO CREATE

**Priority Levels**:
1. **CRITICAL (50-80 modules)**: Core MATRIZ pipeline, Identity, Guardian
2. **HIGH (150-200 modules)**: API gateways, consciousness core, memory systems
3. **MEDIUM (200-250 modules)**: Supporting infrastructure, utilities
4. **LOW (150-200 modules)**: Legacy, experimental, archived

**Effort**: 2-3 hours

---

## 🔧 **Implementation Plan**

### **Phase 1: Discovery & Inventory (4-6 hours)**
1. ✅ **Complete Module Inventory** - Scan and catalog all 780 modules
2. ✅ **Gap Analysis Report** - Identify critical missing documentation
3. ✅ **Missing Manifests Priority List** - Prioritize remediation

**Deliverables**:
- `COMPLETE_MODULE_INVENTORY.json`
- `MODULE_DOCUMENTATION_GAP_ANALYSIS.md`
- `MISSING_MANIFESTS_PRIORITY_LIST.md`

---

### **Phase 2: Schema & Standards (3-4 hours)**
1. ✅ **MATRIZ Compliance Schema** - Define standard structure
2. ✅ **Integration Checklist** - Create validation template
3. ✅ **Capability Matrix Template** - Define capability documentation format

**Deliverables**:
- `schemas/matriz_module_compliance.schema.json`
- `MATRIZ_INTEGRATION_CHECKLIST.md`
- `MODULE_CAPABILITY_MATRIX.csv`

---

### **Phase 3: Automated Generation (8-10 hours)**
1. ✅ **Module Manifest Generator** - Build automated tool
2. ✅ **Dry-run validation** - Test on sample modules
3. ✅ **Batch generation** - Create manifests for all 631 modules
4. ✅ **Validation** - Check schema compliance

**Deliverables**:
- `scripts/generate_module_manifests.py`
- 631 new `module.manifest.json` files
- Validation report

---

### **Phase 4: Analysis & Mapping (6-8 hours)**
1. ✅ **MATRIZ Node Mapping** - Map modules to pipeline nodes
2. ✅ **Dependency Graph** - Generate complete visualization
3. ✅ **Capability Matrix** - Populate from inventory

**Deliverables**:
- `MATRIZ_NODE_TO_MODULE_MAPPING.json`
- `COMPLETE_MODULE_DEPENDENCY_GRAPH.svg`
- `MODULE_CAPABILITY_MATRIX.xlsx`

---

### **Phase 5: Dashboard & Reporting (6-8 hours)**
1. ✅ **Module Health Dashboard** - Interactive HTML/Streamlit
2. ✅ **Audit Readiness Report** - Summary of compliance
3. ✅ **Integration Status Report** - Per-node rollout status

**Deliverables**:
- `MODULE_HEALTH_DASHBOARD.html`
- `MATRIZ_AUDIT_READINESS_REPORT.md`
- `MATRIZ_INTEGRATION_STATUS_REPORT.md`

---

## ⏱️ **Timeline & Effort**

| Phase | Deliverables | Effort | Priority |
|-------|--------------|--------|----------|
| **Phase 1** | Inventory & Gap Analysis | 4-6 hours | 🔴 CRITICAL |
| **Phase 2** | Schema & Standards | 3-4 hours | 🔴 CRITICAL |
| **Phase 3** | Automated Generation | 8-10 hours | 🟠 HIGH |
| **Phase 4** | Analysis & Mapping | 6-8 hours | 🟠 HIGH |
| **Phase 5** | Dashboard & Reporting | 6-8 hours | 🟡 MEDIUM |
| **TOTAL** | **All Deliverables** | **27-36 hours** | - |

**Recommended Approach**: Phases 1-2 before audit, Phase 3-5 during/after initial review

---

## 🎯 **Success Criteria**

### **Audit Readiness (Minimum)**
- ✅ All 780 modules cataloged in inventory
- ✅ Critical modules (100-150) have complete manifests
- ✅ MATRIZ node mapping complete (100%)
- ✅ Dependency graph generated and validated
- ✅ Capability matrix populated (≥80%)
- ✅ Gap analysis report with remediation plan

### **Full Compliance (Ideal)**
- ✅ All 780 modules have schema-compliant manifests
- ✅ Module health dashboard operational
- ✅ Integration checklist completed for all modules
- ✅ Automated validation pipeline in place
- ✅ Documentation synchronized with codebase

---

## 🚀 **Quick Start Commands**

### **Generate Complete Inventory**
```bash
# Create master inventory
python scripts/generate_complete_inventory.py \
  --scan candidate/ lukhas/ \
  --output docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --verbose

# Validate inventory
python scripts/validate_inventory.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json
```

### **Generate Missing Manifests**
```bash
# Dry run (preview only)
python scripts/generate_module_manifests.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --schema schemas/matriz_module_compliance.schema.json \
  --dry-run

# Generate for critical modules only
python scripts/generate_module_manifests.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --priority critical \
  --output-dir .

# Generate all missing manifests
python scripts/generate_module_manifests.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --priority all \
  --output-dir . \
  --confirm
```

### **Generate Dependency Graph**
```bash
python scripts/generate_dependency_graph.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --output docs/audits/COMPLETE_MODULE_DEPENDENCY_GRAPH.dot \
  --format svg png \
  --cluster-by matriz_node
```

### **Launch Health Dashboard**
```bash
python scripts/launch_module_dashboard.py \
  --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
  --port 8050
```

---

## 📊 **Current Status**

| Deliverable | Status | Progress | ETA |
|-------------|--------|----------|-----|
| 1. Complete Module Inventory | 🔨 TO CREATE | 0% | +4 hours |
| 2. MATRIZ Compliance Schema | 🔨 TO CREATE | 0% | +2 hours |
| 3. Module Manifest Generator | 🔨 TO CREATE | 0% | +8 hours |
| 4. Gap Analysis Report | 🔨 TO CREATE | 0% | +3 hours |
| 5. MATRIZ Node Mapping | 🔨 TO CREATE | 0% | +5 hours |
| 6. Capability Matrix | 🔨 TO CREATE | 0% | +3 hours |
| 7. Dependency Graph | 🔨 TO CREATE | 0% | +6 hours |
| 8. Integration Checklist | 🔨 TO CREATE | 0% | +2 hours |
| 9. Module Health Dashboard | 🔨 TO CREATE | 0% | +8 hours |
| 10. Missing Manifests Report | 🔨 TO CREATE | 0% | +3 hours |

**Total Progress**: 0% (0/10 deliverables complete)

---

## 🎯 **Next Actions (Immediate)**

### **1. Create Inventory Script** (Priority: CRITICAL)
```bash
touch scripts/generate_complete_inventory.py
# Implement module scanning and cataloging
```

### **2. Create MATRIZ Schema** (Priority: CRITICAL)
```bash
mkdir -p schemas
touch schemas/matriz_module_compliance.schema.json
# Define compliance requirements
```

### **3. Generate Initial Inventory** (Priority: CRITICAL)
```bash
python scripts/generate_complete_inventory.py
# Creates COMPLETE_MODULE_INVENTORY.json
```

### **4. Create Gap Analysis** (Priority: HIGH)
```bash
python scripts/analyze_documentation_gaps.py
# Creates MODULE_DOCUMENTATION_GAP_ANALYSIS.md
```

### **5. Prioritize Missing Manifests** (Priority: HIGH)
```bash
python scripts/prioritize_missing_manifests.py
# Creates MISSING_MANIFESTS_PRIORITY_LIST.md
```

---

## 📝 **Notes for GPT-5 Auditor**

1. **This is a living document** - Status will be updated as deliverables complete
2. **Automated generation preferred** - 80% can be automated, 20% needs manual review
3. **Validation is critical** - All generated manifests must pass schema validation
4. **Incremental approach** - Can start with critical modules, expand coverage over time
5. **Integration testing required** - Generated manifests need validation against MATRIZ pipeline

---

**Plan Status**: 🔴 DRAFT - Awaiting approval and resource allocation  
**Last Updated**: 2025-10-09  
**Owner**: LUKHAS Core Team  
**Audit Standard**: T4/0.01% (99.99% reliability)

---

*This plan ensures complete MATRIZ compliance documentation for all 780 cognitive modules, enabling comprehensive audit and successful rollout.*
