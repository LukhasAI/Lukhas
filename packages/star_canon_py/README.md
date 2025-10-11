# Star Canon Python Package

Canonical source of truth for LUKHAS Constellation stars and their aliases.

## Usage

```python
from star_canon import canon, normalize

# Get the full canon
c = canon()
print(c["stars"])  # List of canonical star names

# Normalize an alias
normalized = normalize("Consciousness")  # → "🌊 Flow (Consciousness)"
normalized = normalize("Identity")        # → "⚛️ Anchor (Identity)"
```

## Installation

```bash
pip install -e packages/star_canon_py
```

## Integration

This package is used by:
- `scripts/generate_module_manifests.py` - Module manifest generator
- `scripts/patch_schema_to_v1_1_0.py` - Schema patcher
- `scripts/validate_context_front_matter.py` - Context validator
- `schemas/matriz_module_compliance.schema.json` - Schema definitions
