#!/usr/bin/env python3
"""
Simple module enhancer - creates proper structure for all modules
"""

import json
import os
from datetime import datetime, timezone


def enhance_module(module_name, description):
    """Enhance a single module with proper structure"""
    print(f"\n🔧 Enhancing {module_name.upper()} module...")

    # Create directories
    dirs = [
        f"{module_name}/docs",
        f"{module_name}/docs/api",
        f"{module_name}/docs/guides",
        f"{module_name}/tests",
        f"{module_name}/tests/unit",
        f"{module_name}/tests/integration",
        f"{module_name}/examples",
        f"{module_name}/examples/basic",
        f"{module_name}/examples/advanced",
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Create README
    readme = f"""# {module_name.upper()} Module

## Overview
{description}

## Structure
- `docs/` - Documentation
- `tests/` - Test suite
- `examples/` - Usage examples
- `MODULE_MANIFEST.json` - Module configuration

## Quick Start
```python
from {module_name} import *
```

## Testing
```bash
cd {module_name}
make test
```

## Documentation
- [API Reference](docs/api/)
- [User Guide](docs/guides/)

## License
Part of LUKHAS AI
"""

    with open(f"{module_name}/README.md", "w") as f:
        f.write(readme)

    # Create Makefile
    makefile = """test:
\tpytest tests/ -v

clean:
\tfind . -name "*.pyc" -delete
\tfind . -name "__pycache__" -delete

.PHONY: test clean
"""

    with open(f"{module_name}/Makefile", "w") as f:
        f.write(makefile)

    # Create basic test
    test_code = f"""import pytest

def test_{module_name}_import():
    \"\"\"Test module can be imported\"\"\"
    import {module_name}
    assert True
"""

    with open(f"{module_name}/tests/unit/test_basic.py", "w") as f:
        f.write(test_code)

    # Create example
    example = f"""#!/usr/bin/env python3
\"\"\"Basic {module_name} example\"\"\"

from {module_name} import *  # noqa: F401,F403 - demo import for quick experimentation


def main():
    print("Using {module_name} module")
    public_members = [name for name in globals() if not name.startswith("_")]
    if public_members:
        print("Available helpers:", ", ".join(sorted(public_members)))
    else:
        print("Module does not expose public helpers yet. Inspect implementation for details.")

if __name__ == "__main__":
    main()
"""

    example_path = f"{module_name}/examples/basic/example.py"
    with open(example_path, "w") as f:
        f.write(example)
    os.chmod(example_path, 0o755)

    # Update manifest
    manifest_path = f"{module_name}/MODULE_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        manifest = {"module": module_name.upper()}

    manifest["enhanced"] = True
    manifest["enhancement_date"] = datetime.now(timezone.utc).isoformat()

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ {module_name} enhanced!")


def main():
    modules = {
        "core": "Central nervous system - GLYPH engine, symbolic processing",
        "consciousness": "Awareness, reflection, decision-making cortex",
        "lukhas.memory": "Fold-based memory with causal chains",
        "qim": "Quantum-Inspired Metaphors for advanced processing",
        "emotion": "VAD affect and mood regulation",
        "lukhas.governance": "Guardian system and ethical oversight",
        "bridge": "External API connections and interfaces",
    }

    print("🚀 ENHANCING LUKHAS MODULES")
    print("=" * 50)

    for module, desc in modules.items():
        enhance_module(module, desc)

    print("\n✅ All modules enhanced!")
    print("\nNext steps:")
    print("1. Move directories into appropriate modules")
    print("2. Update imports")
    print("3. Run tests")


if __name__ == "__main__":
    main()
