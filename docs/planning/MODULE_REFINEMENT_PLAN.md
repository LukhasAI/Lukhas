---
status: wip
type: documentation
owner: unknown
module: planning
redirect: false
moved_to: null
---

# LUKHAS  Module Refinement Plan

**Date**: 2025-08-01
**Phase**: Pre-Claude Code Automation

## Current State Analysis

### Connectivity Overview
- **Total Python files**: 3,732 (excluding archives)
- **Connected files**: 3,471 (93%)
- **Isolated files**: 261 (7%)
- **Critical hubs**: 50 high-connectivity modules
- **Average connectivity**: 5.88 connections per file

### Key Findings

#### 1. Isolated Files Assessment
- **Valuable prototypes**: 21 files
  - Memory evolution components
  - Symbolic diagnostics
  - Identity pattern analyzers
  - Quantum generators

- **Archive candidates**: 13 files
  - Small utility files (<50 lines)
  - Duplicate safety filters
  - Empty brain templates

- **Syntax errors**: 140 files
  - Many in tools/ directory
  - Archive directories
  - Need investigation for valuable code

- **Needs review**: 17 files
  - Ambiguous purpose
  - May contain valuable logic

#### 2. Critical Hubs (Top Connectivity)
1. `orchestration/core_modules/orchestration_service.py` (107 connections)
2. `core/colonies/base_colony.py` (77 connections)
3. `memory/core.py` (57 connections)
4. `memory/memory_hub.py` (52 connections)
5. `core/actor_system.py` (49 connections)

## Refinement Actions

### Phase 1: Archive Non-Essential Files (Today)

#### A. Create Archive Structure
```bash
/Users/agi_dev/lukhas-archive/
├── 2025-08-01-module-refinement/
│   ├── tools-prototypes/      # Valuable tool prototypes
│   ├── syntax-errors/         # Files with syntax issues
│   ├── small-utilities/       # Small disconnected files
│   └── duplicates/            # Duplicate implementations
```

#### B. Files to Archive

**Immediate Archives** (13 files):
- `core/interfaces/logic/safety_filter.py` → duplicates/
- `core/interfaces/as_agent/agent_logic/safety_filter.py` → duplicates/
- `identity/core/verifold_connector.py` → small-utilities/
- `creativity/personality/brain.py` → small-utilities/
- `meta/HEADER_TEMPLATE.py` → small-utilities/
- `reasoning/reasoning_errors.py` → small-utilities/
- `voice/speech_framework.py` → small-utilities/
- `orchestration/specialized/freeze_protection_check.py` → small-utilities/
- `orchestration/brain/prime_oscillator.py` → small-utilities/
- `orchestration/brain/brain.py` → duplicates/

**Syntax Error Files** (140 files):
- Archive after extracting any valuable logic
- Many are in tools/ directory
- Check for LUKHAS-specific algorithms

### Phase 2: Fix Critical Paths

#### A. High-Priority Fixes
1. **Memory System Consolidation**
   - Merge `memory/core.py` and `memory/memory_hub.py`
   - Resolve duplicate memory handlers
   - Fix voice-memory bridge connections

2. **Orchestration Cleanup**
   - Review `orchestration_service.py` (107 imports!)
   - Break into smaller, focused modules
   - Create clear orchestration interfaces

3. **Colony → Agent Network Rename**
   - Update `core/colonies/` → `core/agent_networks/`
   - Update all imports and references
   - Professional terminology alignment

#### B. Import Fixes
- Fix circular dependencies in consciousness module
- Resolve governance module import chains
- Update features/ references (already moved)

### Phase 3: Module Consolidation

#### A. Similar Module Groups
1. **Hub Consolidations**
   - `memory/memory_hub.py` + `memory/core.py` → `memory/hub.py`
   - `consciousness/consciousness_hub.py` + related → unified hub
   - `quantum/quantum_hub.py` + integrations → quantum core

2. **Engine Consolidations**
   - Multiple reasoning engines → `reasoning/engine.py`
   - Dream engines → `dream/engine.py`
   - Creative engines → `creativity/engine.py`

3. **Service Consolidations**
   - Identity services → `identity/service.py`
   - Consciousness services → `consciousness/service.py`
   - Memory services → `memory/service.py`

#### B. Remove Redundancies
- Merge duplicate implementations
- Consolidate similar functionality
- Maintain module independence

### Phase 4: Naming Conventions & Registry Creation

#### A. Naming Standards
1. **Class Names**
   - Use PascalCase for all classes
   - Keep LUKHAS personality in descriptive names
   ```python
   # Good Examples:
   class MemoryFoldProcessor:      # Industry standard + LUKHAS concept
   class DreamResonanceEngine:     # Clear purpose + personality
   class QuantumConsciousnessHub:  # Professional + innovative

   # Fix These:
   lukhas_memory_manager → LukhasMemoryManager
   dream_engine_base → DreamEngineBase
   ΛBOT_orchestrator → LambdaBotOrchestrator
   ```

2. **Function Names**
   - Use snake_case for all functions
   - Preserve LUKHAS-specific terms where meaningful
   ```python
   # Good Examples:
   def fold_memory(data):          # LUKHAS concept preserved
   def apply_mutation(genome):     # Scientific + LUKHAS
   def resonate_emotions(state):   # Descriptive + personality

   # Fix These:
   def ProcessMemory() → def process_memory()
   def GetQuantumState() → def get_quantum_state()
   ```

3. **Module & File Names**
   - Always use snake_case for files
   - Remove special characters (Λ → lambda)
   ```
   # Fix These:
   ΛBot_orchestrator.py → lambda_bot_orchestrator.py
   DreamEngine.py → dream_engine.py
   ```

#### B. Registry Creation

1. **Class Registry Structure**
   ```python
   # /tools/analysis/generate_class_registry.py
   {
     "consciousness": {
       "ConsciousnessEngine": {
         "file": "consciousness/systems/engine.py",
         "line": 45,
         "type": "class",
         "base_classes": ["BaseEngine"],
         "methods": ["process", "reflect", "integrate"]
       }
     }
   }
   ```

2. **Function Index Structure**
   ```python
   # /tools/analysis/generate_function_index.py
   {
     "memory": {
       "fold_memory": {
         "file": "memory/systems/memory_fold.py",
         "line": 123,
         "type": "function",
         "params": ["data", "context", "emotional_state"],
         "returns": "FoldedMemory"
       }
     }
   }
   ```

#### C. Automated Tools

1. **Naming Convention Scanner**
   ```bash
   # Create scanner to identify non-compliant names
   python tools/analysis/naming_convention_scanner.py
   ```

2. **Automatic Renaming Tool**
   ```bash
   # Safe renaming with import updates
   python tools/analysis/safe_rename.py --preview
   python tools/analysis/safe_rename.py --execute
   ```

3. **Registry Generators**
   ```bash
   # Generate comprehensive registries
   python tools/analysis/generate_class_registry.py
   python tools/analysis/generate_function_index.py
   ```

#### D. LUKHAS Personality Preservation

**Keep These Unique Terms:**
- `memory_fold` - Core LUKHAS concept
- `dream_resonance` - Emotional processing
- `quantum_consciousness` - Advanced awareness
- `bio_oscillation` - Biological rhythms
- `symbolic_mutation` - Evolution concept
- `emotional_drift` - State changes
- `trace_trail` - Audit mechanism
- `glyph_tokens` - Communication symbols

**Standardize These:**
- `lucas_*` → `lukhas_*` (consistency)
- Mixed case in same module → consistent case
- Special characters in names → ASCII equivalents

### Phase 5: Enhance Critical Paths

#### A. Core Workflows
1. **Consciousness Flow**
   ```
   awareness → processing → integration → reflection
   ```

2. **Memory Flow**
   ```
   capture → emotional_context → storage → retrieval
   ```

3. **Identity Flow**
   ```
   authentication → tier_check → access_control → audit
   ```

#### B. Integration Points
- Standardize inter-module communication
- Use GLYPH tokens consistently
- Implement proper event systems

### Phase 6: Testing & Validation

#### A. Critical Path Tests
```bash
# Test consciousness integration
python -m consciousness.tests.test_integration

# Test memory systems
python -m memory.tests.test_core

# Test identity flow
python -m identity.tests.test_access
```

#### B. Module Independence Tests
- Each module must run standalone
- Test with minimal dependencies
- Verify enhancement when combined

## Success Metrics

### Immediate Goals
- [ ] Reduce isolated files from 261 to <50
- [ ] Archive 140+ syntax error files
- [ ] Fix all critical path imports
- [ ] Consolidate duplicate modules

### Quality Metrics
- [ ] Average connectivity: >8 (from 5.88)
- [ ] No circular dependencies
- [ ] All tests passing
- [ ] <3 second startup time

### Architecture Goals
- [ ] Clear module boundaries
- [ ] Consistent naming conventions
- [ ] Professional terminology
- [ ] Ready for Claude Code automation

## Next Steps

1. **Today**: Archive non-essential files
2. **Tomorrow**: Fix critical imports and paths
3. **This Week**: Complete module consolidation
4. **Next Week**: Implement Claude Code automation

## Command Reference

```bash
# Create archive
mkdir -p /Users/agi_dev/lukhas-archive/2025-08-01-module-refinement/{tools-prototypes,syntax-errors,small-utilities,duplicates}

# Archive files
mv <file> /Users/agi_dev/lukhas-archive/2025-08-01-module-refinement/<category>/

# Test connectivity
python3 tools/analysis/_CURRENT_CONNECTIVITY_ANALYSIS.py

# Run assessments
python3 tools/analysis/ISOLATED_FILES_ASSESSMENT.py
```

---

*This plan sets the foundation for implementing comprehensive Claude Code automation while maintaining LUKHAS's innovative architecture.*
