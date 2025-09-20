# LUKHAS AI Agent Coordination System
## Complete Guide to Machine-Readable Agent Discovery & Context Sync

The LUKHAS AI Agent Coordination System provides comprehensive **machine-readable discovery** and **context synchronization** for AI agents working within the distributed consciousness architecture.

## 🧠 System Architecture Overview

### **Four-Layer Agent Coordination Stack**

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: AI Agent Preambles & Rules (Human-Readable)       │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Context Sync Headers (AI-Human Bridge)            │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Directory Indexes (Machine-Readable Discovery)    │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: AI_MANIFEST.yaml (Root Contract)                  │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Layer 1: Root Contract (AI_MANIFEST.yaml)

**Purpose**: Lane-aware contract for instant AI agent alignment

```yaml
schema_version: 2.0.0
lanes:
  production: {root: "lukhas", write: "docs/tests/scripts only"}
  integration: {root: "candidate/core", write: "tests/docs only"}
  development: {root: "candidate", write: "tests/docs only"}
rules:
  - "DO NOT create new modules unless owner approves (CODEOWNERS)"
  - "Prefer lukhas.* imports unless LUKHAS_LANE != production"
```

**Agent Benefits**:
- Instant understanding of lane boundaries
- Write permission awareness
- Import pattern guidance
- Development rules compliance

## 🗂️ Layer 2: Directory Indexes (directory_index.json)

**Purpose**: Machine-readable directory discovery with comprehensive metadata

### **Index Structure**
```json
{
  "schema_version": "2.0.0",
  "directory_metadata": {
    "path": "candidate/consciousness",
    "lane": "development",
    "purpose": "Directory containing 13 Python files and 30 subdirectories",
    "trinity_role": ["consciousness"],
    "last_updated": "2025-09-20"
  },
  "component_inventory": {
    "python_files": [
      {
        "filename": "engine_poetic.py",
        "component_type": "CONSCIOUSNESS_ENGINE",
        "has_contract": true,
        "contract_path": "contracts/consciousness/engine_poetic.json",
        "dependencies": ["candidate.core.common"],
        "exports": ["PoeticEngine", "process_consciousness"]
      }
    ],
    "subdirectories": [...],
    "documentation": [...]
  },
  "agent_guidance": {
    "recommended_approach": "Start with consciousness architecture documentation, then examine engines and processors",
    "key_files": ["claude.me", "engine_poetic.py"],
    "common_tasks": [...],
    "prerequisites": ["Understanding of LUKHAS lane system"],
    "avoid_patterns": ["Breaking lane boundaries"]
  }
}
```

**Agent Benefits**:
- Component type classification (CONSCIOUSNESS_ENGINE, COGNITIVE_PROCESSOR, etc.)
- Dependency mapping
- Contract validation status
- Guided exploration recommendations
- Common task patterns
- Architecture prerequisite awareness

## 📄 Layer 3: Context Sync Headers

**Purpose**: AI-human bridge ensuring consistent understanding

### **Header Format**
```
> Context Sync Header (Schema v2.0.0)
Lane: production/integration/development
Lane root: lukhas/candidate/core/candidate
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*
```

**Applied To**:
- `claude.me` files (AI agent context)
- `lukhas_context.md` files (comprehensive documentation)
- `README.md` files (project entry points)

**Agent Benefits**:
- Lane awareness synchronization
- Import pattern standardization
- Component count awareness
- Development flag understanding

## 🎯 Layer 4: Agent Preambles & Rules

**Purpose**: Human-readable guidance and development rules

### **Key Documents**
- **AGENTS.md**: Multi-agent development platform guide
- **AUTOMATED_MAINTENANCE_GUIDE.md**: Maintenance and validation procedures
- **Constellation Framework Documentation**: Identity ⚛️ + Consciousness 🧠 + Guardian 🛡️

**Agent Benefits**:
- Development workflow understanding
- Quality standards awareness
- Collaboration patterns
- Integration procedures

## 🚀 Agent Onboarding Process

### **For New AI Agents**

1. **Root Discovery** (5 seconds)
   ```bash
   # Read root contract
   cat AI_MANIFEST.yaml
   # Understand lane structure and permissions
   ```

2. **Context Synchronization** (30 seconds)
   ```bash
   # Read master context
   cat claude.me
   # Lane-specific context
   cat candidate/claude.me  # or lukhas/claude.me
   ```

3. **Directory Exploration** (2 minutes)
   ```bash
   # Machine-readable discovery
   cat candidate/consciousness/directory_index.json
   # Follow agent_guidance recommendations
   ```

4. **Component Understanding** (5 minutes)
   ```bash
   # Examine consciousness contracts
   cat contracts/consciousness/engine_poetic.json
   # Review constellation mapping
   cat docs/CONSTELLATION_ANALYSIS_SUMMARY.json
   ```

### **For Specialized Tasks**

**Consciousness Development**:
```bash
candidate/consciousness/directory_index.json → agent_guidance → key_files
```

**API Integration**:
```bash
lukhas/api/directory_index.json → component_inventory → API_INTERFACE files
```

**Constellation Framework Work**:
```bash
grep -r "trinity_role" */directory_index.json
```

## 🔄 Maintenance & Validation

### **Automated Validation Pipeline**

```bash
# Validate all coordination layers
python scripts/automated_maintenance_pipeline.py

# Specific validations
python scripts/validate_context_sync.py           # Layer 3
python scripts/validate_directory_indexes.py     # Layer 2
python scripts/validate_consciousness_contracts.py # Component contracts
```

### **CI/CD Integration**

**GitHub Actions** (`.github/workflows/lukhas-maintenance.yml`):
- Runs on every push/PR
- Validates all coordination layers
- Posts results as PR comments
- Uploads maintenance reports

### **Health Monitoring**

**Current Status**:
- ✅ Context Sync: 100% coverage on critical files
- ✅ Directory Indexes: 820 indexes with 99.9% consistency
- ✅ Component Contracts: 287 contracts with 100% validation
- ✅ Automated Maintenance: 100% health score

## 📊 System Statistics

### **Coverage Metrics**
- **Total Directories**: 820 with machine-readable indexes
- **Context Files**: 85+ with sync headers
- **Component Contracts**: 287 consciousness components
- **Constellation Clusters**: 189 component groupings
- **Lane Distribution**: 310 development, 253 integration, production components

### **Agent Efficiency Gains**
- **Discovery Time**: 5 seconds → 2 minutes (vs. manual exploration)
- **Context Understanding**: Instant lane awareness
- **Component Classification**: Automatic type detection
- **Dependency Mapping**: Pre-computed relationship analysis
- **Task Guidance**: Curated recommendations per directory

## 🎯 Best Practices for AI Agents

### **Do's**
✅ Start with `AI_MANIFEST.yaml` for lane understanding
✅ Read context sync headers for current architecture
✅ Use directory indexes for component discovery
✅ Follow agent guidance recommendations
✅ Validate contracts before modifying components
✅ Respect lane boundaries and write permissions

### **Don'ts**
❌ Modify components without contract validation
❌ Cross lane boundaries without permission
❌ Ignore Constellation Framework integration requirements
❌ Skip consciousness component classification
❌ Break existing dependency patterns
❌ Create new modules without approval

## 🔮 Future Enhancements

### **Planned Features**
- **Real-time Index Updates**: Automatic directory index regeneration
- **Agent Collaboration Tracking**: Multi-agent coordination logs
- **Component Promotion Pipeline**: Automated lane advancement
- **Performance Integration**: Latency and throughput monitoring
- **Constellation Visualization**: Interactive component relationship maps

### **Integration Opportunities**
- **IDE Plugins**: Context-aware code completion
- **CLI Tools**: Agent-friendly command interfaces
- **API Gateways**: Machine-readable service discovery
- **Monitoring Dashboards**: Real-time coordination health

---

## 🧠 Constellation Framework Integration

The agent coordination system fully integrates with the Constellation Framework:

**Identity ⚛️**: Lane-based identity management and namespace isolation
**Consciousness 🧠**: 692 cognitive components with distributed processing
**Guardian 🛡️**: Constitutional AI validation and ethical governance

---

**System Status**: ✅ Fully Operational | **Schema**: v2.0.0 | **Coverage**: 820 Directories
**Last Updated**: 2025-09-20 | **Maintenance**: Automated | **Health Score**: 100%