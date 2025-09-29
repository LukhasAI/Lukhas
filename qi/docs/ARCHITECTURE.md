# QI (Quantum-Inspired) Module Architecture

## Directory Structure Philosophy

### Current Structure
```
qi/
├── __init__.py              # Main package initialization
├── core/                    # Core engines and fundamental components
├── bio/                     # Bio-inspired algorithms and simulators
├── processing/              # Data processing and coordination
├── systems/                 # System-level integrations
├── mind/                    # Consciousness and awareness systems
└── [other subsystems]/
```

### Import Strategy

#### Public API (Recommended)
Users of the QI module should import from the top level:
```python
from qi import Engine, BioSimulator, Processor
```

#### Internal Imports
Within QI module, use absolute imports from qi root:
```python
from qi.engines.consciousness.engine import QuantumEngine
from qi.bio.components import BioComponent
```

### Best Practices

1. **Keep It Flat**: Avoid nesting deeper than 3 levels
   - `qi/` (root)
   - `qi/core/` (subsystem)
   - `qi/core/engine.py` (implementation)

2. **Clear Naming**: Directory names should be:
   - Lowercase
   - No prefixes (no `quantum_` since we're already in `qi/`)
   - Descriptive but concise

3. **Public vs Private**:
   - Public API: Exported in `__init__.py`
   - Private/Internal: Prefix with underscore `_internal.py`

4. **Deprecation Path**:
   - Old code goes to `legacy/` subdirectory
   - Add deprecation warnings
   - Document migration path

### Migration Status

As of 2025-08-14:
- ✅ Renamed from `quantum/` and `qim/` to `qi/`
- ✅ Removed `quantum_` prefixes from subdirectories
- ✅ Consolidated overlapping directories
- ⚠️  Some internal imports may need updating

### Future Improvements

1. **Standardize Imports**: Update all files to use consistent import patterns
2. **API Documentation**: Generate docs from `__init__.py` exports
3. **Type Hints**: Add type annotations for better IDE support
4. **Testing**: Ensure each submodule has corresponding tests

### Module Principles

- **Quantum-Inspired, Not Quantum**: We use classical algorithms inspired by quantum concepts
- **Modular Design**: Each subdirectory should work independently
- **Clear Dependencies**: Avoid circular imports
- **Performance First**: Optimize hot paths

## Example: Adding a New Component

```python
# 1. Create implementation file
# qi/bio/new_simulator.py
class NewSimulator:
    """Bio-inspired simulator component"""
    pass

# 2. Export in subsystem __init__.py
# qi/bio/__init__.py
from .new_simulator import NewSimulator
__all__ = ['NewSimulator', ...]  # Add to exports

# 3. Optionally export at root level for public API
# qi/__init__.py
from .bio import NewSimulator
__all__ = ['NewSimulator', ...]  # Add to root exports
```

## Testing Import Structure

```bash
# Test that imports work correctly
python -c "from qi import Engine; print('✓ Public API works')"
python -c "from qi.engines.consciousness.engine import QuantumEngine; print('✓ Internal imports work')"
```

---
*This architecture ensures maintainability, clarity, and professional Python standards.*
