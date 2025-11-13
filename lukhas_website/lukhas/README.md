# lukhas_website/lukhas/ - Website Shim Layer

**Status**: Production
**Type**: Compatibility & Extension Layer
**Size**: 8.5MB (470 Python files)
**Purpose**: Website independence from production `/lukhas/` lane

---

## Why This Directory Exists

This directory provides a **shim layer** and **extension modules** for the LUKHAS website application, enabling:

1. **Lane Isolation**: Website development independent of production `/lukhas/` lane
2. **Backward Compatibility**: Fallback implementations when production modules unavailable
3. **Feature Independence**: Experimental features not yet ready for production
4. **Import Flexibility**: Graceful degradation when production API changes

**Key Principle**: This is NOT a duplicate of `/lukhas/` - it's a **separate, extended codebase** for website-specific functionality.

---

## Architecture Overview

### Directory Structure

```
lukhas_website/
├── lukhas/                    # THIS DIRECTORY (shim layer + extensions)
│   ├── shims/                 # Compatibility shims for missing production code
│   ├── api/                   # Website API extensions
│   ├── bio/                   # Bio-inspired systems (not in production)
│   ├── rl/                    # Reinforcement learning (not in production)
│   ├── quantum_bio_consciousness/  # Quantum-bio integration
│   ├── agents/                # Multi-agent systems
│   ├── colonies/              # Agent colony management
│   └── ... (50+ unique modules)
│
├── packages/                  # Website UI packages
├── tests/                     # Website-specific tests
└── docs/                      # Website documentation

/lukhas/                       # Production lane (420KB, ~50 files)
├── api/                       # Production API
├── orchestrator/              # Production orchestrator
├── identity/                  # Production identity
└── ... (core production modules)
```

### Size Comparison

| Metric | `/lukhas/` (Production) | `/lukhas_website/lukhas/` (Website) |
|--------|------------------------|-------------------------------------|
| **Size** | 420 KB | **8.5 MB** (20x larger) |
| **Files** | ~50 Python files | **470 Python files** |
| **Modules** | 12 core directories | **67 directories** (50+ unique) |

---

## Import Resolution Strategy

### How Imports Work

The website follows a **try-production-first, fallback-to-shim** pattern:

```python
# Pattern 1: Try importing from production /lukhas/ first
try:
    from lukhas.glyphs import bind_glyph, encode_concept
    GLYPHS_AVAILABLE = True
except ImportError:
    # Fallback to website shim or disable feature
    GLYPHS_AVAILABLE = False
    # OR: from lukhas_website.lukhas.shims.glyphs import bind_glyph

# Pattern 2: Use website-specific extensions directly
from lukhas_website.lukhas.bio import BioSymbolicOrchestrator
from lukhas_website.lukhas.rl import ConsciousnessEnvironment

# Pattern 3: Shims provide backward compatibility
from lukhas_website.lukhas.shims.core_swarm import SwarmHub
```

### Import Rules

**DO**:
- ✅ Import from production `/lukhas/` when available
- ✅ Use explicit `lukhas_website.lukhas.*` for website-specific code
- ✅ Use shims for backward compatibility when production API unavailable
- ✅ Add graceful fallbacks with feature flags

**DON'T**:
- ❌ Mix production and website imports without fallback handling
- ❌ Assume production `/lukhas/` is in PYTHONPATH
- ❌ Import `lukhas.*` when you mean `lukhas_website.lukhas.*`
- ❌ Duplicate code - use shims to bridge instead

---

## Module Categories

### 1. Shims (Compatibility Layer)

**Location**: `lukhas_website/lukhas/shims/`

Provides fallback implementations for production modules that may be unavailable:

```python
# shims/core_swarm.py
class SwarmHub:
    """Fallback SwarmHub implementation"""
    def __init__(self, *args, **kwargs):
        pass  # No-op when production unavailable
```

**Purpose**: Ensure website functions even if production `/lukhas/` not in path.

### 2. Website Extensions (Not in Production)

**50+ unique modules** providing features beyond production `/lukhas/`:

#### Consciousness & Cognitive
- `aka_qualia/` - Qualia processing and conscious experience modeling
- `cognitive_core/` - Core cognitive architecture
- `emotion/` - Emotional state processing
- `consciousness/` - Extended consciousness models (beyond production)

#### Multi-Agent Systems
- `agents/` - Agent definitions and management
- `colonies/` - Multi-agent colony orchestration
- `colony/` - Colony-level behavior patterns
- `constellation/` - Constellation framework implementation

#### Bio & Quantum
- `bio/` - Bio-inspired algorithms and patterns
- `quantum_bio_consciousness/` - Quantum-bio integration layer
- `rl/` - Reinforcement learning for consciousness training

#### Infrastructure
- `deployment/` - Deployment configurations
- `serve/` - Serving infrastructure
- `workflows/` - Workflow definitions
- `flags/` - Feature flag management
- `feedback/` - User feedback systems
- `compliance/` - Compliance and audit tooling

#### Core Extensions
- `adapters/` - Extended adapter patterns
- `audit/` - Audit logging (extended beyond production)
- `branding/` - Branding integration
- `bridge/` - External system bridges
- `interfaces/` - Interface definitions
- `ledger/` - Transaction ledger
- `tools/` - Development tooling

### 3. Production Overlaps (Extended Versions)

Some directories exist in both places but website version has extensions:

| Module | Production `/lukhas/` | Website `/lukhas_website/lukhas/` |
|--------|-----------------------|-----------------------------------|
| `api/` | Core API endpoints | Extended with website-specific routes |
| `consciousness/` | Basic consciousness loop | Full consciousness architecture |
| `core/` | Minimal core utilities | Extended utilities and helpers |
| `governance/` | Production governance | Extended with compliance tools |
| `identity/` | Core identity/auth | Extended with web auth flows |
| `memory/` | Core memory system | Extended with web caching |
| `orchestrator/` | Production orchestrator | Extended for website workflows |

---

## Development Guidelines

### When to Add Code Here

**Add to `/lukhas_website/lukhas/`** when:
- ✅ Feature is website-specific (UI integration, web workflows)
- ✅ Feature is experimental and not ready for production
- ✅ Need to extend production module without modifying it
- ✅ Providing backward compatibility shim

**Add to production `/lukhas/`** when:
- ✅ Feature is stable and tested
- ✅ Feature is useful across all LUKHAS deployments
- ✅ Code follows lane promotion criteria (75%+ coverage)
- ✅ Approved for production lane

### Promoting Code to Production

When website code matures, promote it to production:

1. **Identify Candidate**: Code in `lukhas_website/lukhas/` ready for production
2. **Meet Criteria**: 75%+ test coverage, documented, stable API
3. **Move to Lane**: Start in `/candidate/`, promote to `/lukhas/` when battle-tested
4. **Update Imports**: Change website to import from production
5. **Keep Shim**: Maintain backward compatibility shim temporarily

**Example Promotion Candidates**:
- `bio/` - Bio-inspired patterns (mature, well-tested)
- `rl/` - Reinforcement learning systems (stable API)
- `quantum_bio_consciousness/` - Quantum-bio integration (ready for wider use)

---

## Maintenance

### Regular Tasks

**Weekly**:
- Review import errors in website logs (failed production imports)
- Update shims when production API changes
- Document new website-specific modules

**Monthly**:
- Compare overlapping modules for divergence (see `scripts/audit/compare_lukhas_directories.py`)
- Identify promotion candidates
- Review and prune deprecated shims

**Quarterly**:
- Architectural review of shim layer necessity
- Evaluate moving to explicit API boundaries
- Update this README with new modules

### Import Linting

Enforce import boundaries with `import-linter`:

```bash
# Check import rules
lint-imports

# Rules enforced:
# 1. lukhas_website code doesn't import from /lukhas/ without try/except
# 2. Shims are only used when production unavailable
# 3. No circular dependencies between website and production
```

See `pyproject.toml` for import-linter configuration.

---

## Troubleshooting

### ImportError: No module named 'lukhas.X'

**Cause**: Website trying to import from production `/lukhas/` but it's not in PYTHONPATH.

**Solution**:
1. Add fallback import using shim
2. OR: Add feature flag to disable when production unavailable
3. OR: Ensure `/lukhas/` is installed in website environment

**Example Fix**:
```python
try:
    from lukhas.glyphs import bind_glyph
    GLYPHS_ENABLED = True
except ImportError:
    from lukhas_website.lukhas.shims.glyphs import bind_glyph
    GLYPHS_ENABLED = False
```

### Module exists in both places - which one is used?

**Answer**: Depends on import statement:
- `from lukhas.X import Y` → Production `/lukhas/X`
- `from lukhas_website.lukhas.X import Y` → Website `/lukhas_website/lukhas/X`

**Resolution Order**: Python resolves imports based on PYTHONPATH order.

**Best Practice**: Use explicit `lukhas_website.lukhas.*` imports for website-specific code.

### How do I know if code should go here or production?

**Use this decision tree**:
1. Is it website-specific UI/workflow? → `/lukhas_website/lukhas/`
2. Is it experimental/unstable? → `/lukhas_website/lukhas/`
3. Is it a production feature extension? → `/lukhas_website/lukhas/` (then promote later)
4. Is it stable and broadly useful? → `/candidate/` or `/lukhas/`

---

## Related Documentation

- **Audit Report**: [docs/audit/LUKHAS_WEBSITE_DIRECTORY_AUDIT_2025-11-12.md](../../docs/audit/LUKHAS_WEBSITE_DIRECTORY_AUDIT_2025-11-12.md)
- **Production Lane**: [/lukhas/README.md](../../lukhas/README.md)
- **Lane System**: [CLAUDE.md](../../CLAUDE.md) - Lane architecture overview
- **Website Docs**: [lukhas_website/README.md](../README.md)
- **Import Linter**: [pyproject.toml](../../pyproject.toml) - Import boundary rules

---

## Architecture Decision Record (ADR)

**Decision**: Maintain separate `lukhas_website/lukhas/` directory for website independence

**Context**:
- Website needs to develop independently from production lane releases
- Some features are website-specific and don't belong in production
- Backward compatibility required when production API changes
- Lane isolation prevents cross-contamination during development

**Consequences**:
- ✅ **Pro**: Website can develop at its own pace
- ✅ **Pro**: Production lane remains stable and focused
- ✅ **Pro**: Clear separation between production and experimental code
- ⚠️ **Con**: Potential code duplication (mitigated by shims)
- ⚠️ **Con**: Higher maintenance burden (470 files vs 50)
- ⚠️ **Con**: Import confusion (mitigated by linting and documentation)

**Alternatives Considered**:
1. ❌ **Website imports directly from production**: Breaks lane isolation
2. ❌ **Merge website and production**: Slows production development
3. ✅ **Current approach**: Balance between independence and code reuse

**Review Date**: Q1 2026 (evaluate if shim layer still needed)

---

**Last Updated**: 2025-11-12
**Maintained By**: LUKHAS Core Team
**Questions**: See [docs/audit/LUKHAS_WEBSITE_DIRECTORY_AUDIT_2025-11-12.md](../../docs/audit/LUKHAS_WEBSITE_DIRECTORY_AUDIT_2025-11-12.md)
