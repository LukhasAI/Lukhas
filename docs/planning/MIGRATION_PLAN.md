# LUKHAS Module Migration Plan - MATRIZ v1.1 Process

## Migration Strategy
Following the MATRIZ v1.1 validation framework with proper lane-based evaluation.

## Lane Definitions

### 1. **candidate/** - Evaluation Stage
Modules under review for migration to production. Must pass:
- MATRIZ v1.1 schema compliance
- Import purity (no cross-lane contamination)
- Test coverage requirements
- Documentation standards

### 2. **lukhas/** (accepted) - Production Ready
Modules that have passed ALL validation criteria:
- ✅ MATRIZ compliance verified
- ✅ No illegal imports
- ✅ Has unit/integration tests
- ✅ Meets SLOs
- ✅ Has docstrings
- ✅ Observability configured

### 3. **quarantine/** - Issues to Fix
Modules with problems that need resolution:
- Import violations
- Missing tests
- Security/consent issues
- Performance problems

### 4. **archive/** - Deprecated
Obsolete or replaced modules kept for reference

## Migration Process

### Phase 1: Initial Assessment
1. Identify all root-level modules
2. Categorize by complexity and dependencies
3. Create dependency graph
4. Identify migration order

### Phase 2: Candidate Evaluation
For each module:
1. Move to `candidate/`
2. Run MATRIZ validation
3. Check import dependencies
4. Verify test coverage
5. Review documentation

### Phase 3: Validation Gates
- **Gate 1**: MATRIZ Compliance
  - Validates against `MATRIZ/matriz_node_v1.json`
  - Accepts both schema_ref formats during transition

- **Gate 2**: Import Purity
  - No imports from candidate/quarantine/archive
  - Uses import-linter contracts

- **Gate 3**: Quality Standards
  - Has tests (pytest coverage > 70%)
  - Has docstrings
  - Follows naming conventions

- **Gate 4**: Security & Consent
  - PII linters pass
  - GTΨ-gated for privileged actions
  - Consent tracking implemented

### Phase 4: Production Migration
- Move validated modules from `candidate/` to `lukhas/`
- Update all import statements
- Run integration tests
- Document in audit trail

## Priority Migration Order

### Tier 1 - Core Infrastructure (No external dependencies)
- [ ] core/ - Core GLYPH engine, symbolic logic
- [ ] governance/ - Guardian System, ethics engine
- [ ] config/ - Configuration management

### Tier 2 - Foundation Modules (Depend on Tier 1)
- [ ] memory/ - Fold-based memory systems
- [ ] identity/ - ΛiD authentication system
- [ ] compliance/ - Compliance and audit

### Tier 3 - Processing Modules (Depend on Tier 1-2)
- [ ] consciousness/ - Awareness and decision systems
- [ ] orchestration/ - Brain integration, coordination
- [ ] reasoning/ - Logic and inference

### Tier 4 - Integration Modules (Depend on Tier 1-3)
- [ ] bridge/ - External API connections
- [ ] api/ - FastAPI endpoints
- [ ] adapters/ - Service adapters

### Tier 5 - Advanced Features (Depend on Tier 1-4)
- [ ] quantum/ - Quantum-inspired algorithms
- [ ] bio/ - Bio-inspired systems
- [ ] emotion/ - VAD affect system
- [ ] creativity/ - Dream engine

## Validation Commands

```bash
# Check current state
python tools/doctor.py
python tools/inventory.py

# Validate MATRIZ compliance
PYTHONPATH="$(pwd)" python -m MATRIZ.utils.matriz_validate candidate/

# Check imports
lint-imports

# Run tests
pytest candidate/module_name/

# Check for illegal imports
python tools/inventory.py | jq '.accepted_illegal_imports'
```

## Success Metrics
- Zero illegal cross-lane imports
- All migrated modules pass MATRIZ validation
- Test coverage > 70% for migrated modules
- Clean doctor.py health check
- Documented audit trail for all decisions

## Audit Trail Location
`docs/AUDIT/migration_decisions.json`
