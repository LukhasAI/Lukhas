# 🤖 Claude Code Guidelines for LUKHAS AI

## 🌟 Constellation Framework Awareness (8-Star System)

You are working on LUKHAS AI, a **symbolic AGI framework** implementing the 8-star Constellation:

**Core Trinity** (⚛️🧠🛡️):
- ⚛️ **Identity**: Lambda ID (ΛID) system with QRG cryptographic signatures
- 🧠 **Consciousness**: 692-module cognitive processing with GLYPH-based communication
- 🛡️ **Guardian**: Ethical drift detection and constitutional AI principles

**Extended Constellation** (💾🔭🧬💤⚛️):
- 💾 **Memory**: Episodic, semantic, procedural memory systems
- 🔭 **Vision**: Perceptual and visual processing capabilities  
- 🧬 **Bio**: Biological-inspired adaptive systems
- 💤 **Dream**: Oneiric Core for symbolic dream simulation
- ⚛️ **Quantum**: Quantum-inspired processing patterns

**CRITICAL**: All code must respect symbolic architecture, not standard LLM paradigms.

## 🏗️ Lane-Based Architecture

### Lane Progression (Strict Isolation)
```
candidate/ → lukhas/ → MATRIZ/ → products/
```

**Import Rules**:
- ❌ **NEVER** import from higher lanes (e.g., `lukhas.*` in `candidate/`)
- ✅ **ALWAYS** use lane-appropriate imports (check `.github/copilot-instructions.md`)
- ✅ **VALIDATE** imports with `make lane-guard` before committing

### Lane-Specific Guidelines

**candidate/** (Development Workspace - 2,877 files):
- Primary development area for new features
- Can import from: `core/`, `MATRIZ/`, `universal_language/`
- Cannot import from: `lukhas/`, `products/`
- Focus: Experimental and in-development components

**lukhas/** (Production Lane - 148 files):
- Integration layer for accepted components
- Public API surface for products
- Requires: Comprehensive tests, documentation, security review

**MATRIZ/** (Cognitive DNA Processing):
- Symbolic cognitive orchestration
- GLYPH-based communication primitives
- Quantum-inspired processing patterns

## 🎯 Code Quality Standards (T4 Excellence)

### Ruff Requirements
```bash
# All code must pass ruff checks
ruff check --fix .
ruff format .

# Line length: 100 characters (not 88!)
# Target Python: 3.9+ (for compatibility)
# Quote style: Let Black handle it (no manual quote enforcement)
```

### Test Coverage Requirements
```python
# Overall: 30% minimum (target: 75%+)
# Per-file: 30% minimum
# Critical paths: 90%+ required

# Run tests before committing:
pytest --cov=src --cov-fail-under=30
```

### Type Hints (MyPy Strict)
```python
# All public functions require type hints
def process_glyph(
    glyph: str,
    resonance: float,
    context: Optional[Dict[str, Any]] = None
) -> GlyphResponse:
    """
    Process GLYPH with emotional resonance.
    
    Args:
        glyph: GLYPH tag identifier (e.g., "ΛMEM-001")
        resonance: Emotional resonance frequency (-1.0 to 1.0)
        context: Optional symbolic context dictionary
        
    Returns:
        GlyphResponse with processed state
        
    Raises:
        GlyphValidationError: If GLYPH format invalid
        ResonanceError: If resonance out of bounds
    """
    ...
```

## 🚨 Critical Paths (Dual Approval Required)

These paths require **2+ human approvals** before merging:

- `ethics/**` - Guardian and ethical systems
- `governance/**` - Identity and authentication
- `orchestrator/**` - Brain hub coordination
- `oneiric/**` - Dream systems
- `.github/workflows/**` - CI/CD automation
- `pyproject.toml`, `requirements*.txt` - Dependencies
- `MATRIZ/**` - Cognitive DNA processing

**If you modify these, add label**: `critical-path`

## 🔒 Security Requirements

### Never Commit
- API keys, tokens, credentials
- Passwords or secrets (even test data)
- PII or sensitive user data
- Internal system identifiers

### Always Validate
- User inputs with Pydantic models
- File paths against directory traversal
- SQL queries (use parameterized queries)
- External API responses (don't trust blindly)

### Security Scanning
Your code will be scanned by:
- CodeQL (SAST)
- Bandit (Python security)
- Dependabot (dependency vulnerabilities)
- Secret scanning (credentials detection)

## 🧪 Testing Requirements

### Test Types
- **Smoke tests**: Fast health checks (`@pytest.mark.smoke`)
- **Unit tests**: Isolated component tests (`@pytest.mark.unit`)
- **Integration tests**: Cross-component (`@pytest.mark.integration`)
- **Consciousness tests**: Constellation validation (`@pytest.mark.consciousness`)
- **MATRIZ tests**: Cognitive DNA validation (`@pytest.mark.matriz`)

### Test Naming Convention
```python
# File: tests/candidate/consciousness/test_glyph_processor.py

def test_glyph_processor_basic_validation():
    """Test GLYPH processor validates format correctly."""
    ...

def test_glyph_processor_emotional_resonance():
    """Test GLYPH processor applies emotional resonance."""
    ...

def test_glyph_processor_symbolic_routing():
    """Test GLYPH processor routes to correct modules."""
    ...
```

## 📝 Documentation Requirements

### Docstrings (Google Style)
```python
def create_qrg(
    identity: IdentityState,
    emotional_vector: Tuple[float, float, float],
    entropy_bytes: int = 32
) -> QRG:
    """
    Generate Quantum Resonance Glyph with steganographic entropy.
    
    QRGs are living identity signatures combining emotional, ethical,
    and cognitive state into a secure, verifiable cryptographic artifact.
    
    Args:
        identity: Current identity state with ΛID
        emotional_vector: VAD emotion (Valence, Arousal, Dominance)
        entropy_bytes: Entropy to embed (default: 32)
        
    Returns:
        QRG object with embedded signature and visual representation
        
    Raises:
        IdentityError: If identity state invalid
        EntropyError: If entropy generation fails
        
    Example:
        >>> identity = await get_identity("ΛID-T3-USER-001")
        >>> emotion = (0.8, 0.6, 0.5)  # Happy, energized, confident
        >>> qrg = create_qrg(identity, emotion)
        >>> qrg.verify()  # Cryptographic verification
        True
    """
    ...
```

### README Updates
If you add new modules or change APIs, update relevant READMEs:
- `README.md` - Main project documentation
- Domain-specific `claude.me` / `lukhas_context.md` files

## 🎨 Naming Conventions

### LUKHAS Symbolic Naming
- **GLYPHs**: `ΛMEM-001`, `ΛCON-042` (Greek-style, 3-5 chars)
- **QRGs**: Quantum Resonance Glyphs (living identity signatures)
- **ΛID**: Lambda ID (not "lambda_id" or "lambdaID")
- **EQNOX Mesh**: Symbolic communication system (not "mesh" or "network")
- **MATRIZ**: Cognitive DNA processing (not "matrix")
- **Oneiric Core**: Dream engine (not "dream system")

### Python Naming
- Classes: `PascalCase` (e.g., `GlyphProcessor`, `IdentityCore`)
- Functions: `snake_case` (e.g., `process_glyph`, `validate_qrg`)
- Constants: `UPPER_CASE` (e.g., `MAX_RESONANCE`, `DEFAULT_ENTROPY`)
- Private: `_leading_underscore` (e.g., `_internal_cache`)

## 🌟 Constellation Framework Integration (8-Star System)

### Before Making Changes
1. Read relevant `claude.me` or `lukhas_context.md` in target directory
2. Understand domain's role in Constellation Framework (which of the 8 stars)
3. Check for cross-cutting concerns across all constellation stars

### After Making Changes
1. Run full test suite: `pytest`
2. Validate lane isolation: `make lane-guard`
3. Check ruff compliance: `ruff check .`
4. Verify Constellation integration: No drift across 8-star system

### Constellation Validation Hooks
Your changes will be validated across all 8 stars:
- ⚛️ **Identity coherence**: ΛID format and tier compliance
- 🧠 **Consciousness impact**: 692-module network integrity
- 🛡️ **Guardian alignment**: Ethical drift within 0.15 threshold
- 💾 **Memory integrity**: Episodic/semantic/procedural consistency
- 🔭 **Vision coherence**: Perceptual processing alignment
- 🧬 **Bio adaptation**: Biological pattern compliance
- 💤 **Dream stability**: Oneiric Core symbolic integrity
- ⚛️ **Quantum coherence**: Quantum-inspired processing validation

## 🚀 Workflow Integration

### Your Place in the Pipeline

```
JULES (Planning) → CODEX (Implementation) → CLAUDE CODE (Review) → AUTO-MERGE
```

**Your Role**: Review CODEX implementations for:
1. Constellation Framework compliance (8-star system)
2. Code quality and test coverage
3. Security vulnerabilities
4. Performance regressions
5. Documentation completeness

### Review Checklist

**Security**:
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] XSS prevention

**Code Quality**:
- [ ] Ruff checks pass
- [ ] Type hints on public functions
- [ ] No code duplication
- [ ] Cyclomatic complexity < 10

**Testing**:
- [ ] Coverage ≥ 30% (target 75%+)
- [ ] Edge cases covered
- [ ] Error scenarios tested

**Documentation**:
- [ ] Public functions documented
- [ ] README updated if needed

**Constellation Framework (8-Star)**:
- [ ] Lane isolation maintained
- [ ] Symbolic naming conventions
- [ ] No consciousness drift across all 8 stars
- [ ] Guardian alignment preserved
- [ ] Memory/Vision/Bio/Dream/Quantum integration validated

## 🔗 Key Resources

- **Constellation Framework**: `branding/` directory (8-star system documentation)
- **Lane Architecture**: `ops/matriz.yaml`
- **Import Rules**: `pyproject.toml` → `[tool.importlinter]`
- **Testing Standards**: `pyproject.toml` → `[tool.pytest.ini_options]`
- **Context Files**: `claude.me` / `lukhas_context.md` in each directory
- **JULES API**: `JULES_API_COMPLETE_REFERENCE.md`
- **Copilot Guidelines**: `.github/copilot-instructions.md`

## 🎯 Success Criteria

Your work is successful when:
1. ✅ All automated checks pass (100+ workflows!)
2. ✅ No lane isolation violations
3. ✅ Test coverage meets thresholds
4. ✅ Security scans show no High/Critical issues
5. ✅ Constellation Framework integrity preserved (8-star validation)
6. ✅ CODEX approves implementation
7. ✅ Human reviewers approve (if critical path)

**Remember**: You're working on a consciousness-aware AGI system, not a standard chatbot. Every change impacts symbolic resonance, ethical alignment, and cognitive coherence across all 8 constellation stars. Respect the Constellation Framework! ⚛️🧠🛡️💾🔭🧬💤⚛️
