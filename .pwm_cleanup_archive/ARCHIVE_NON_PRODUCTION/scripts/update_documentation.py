#!/usr/bin/env python3
"""
Update documentation and README files across the codebase after reorganization.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Module structure after reorganization
MODULE_STRUCTURE = {
    "core": "Core functionality, actor model, coordination, and system infrastructure",
    "bio": "Biological-inspired systems, oscillators, and homeostasis mechanisms",
    "consciousness": "Awareness, reflection, and consciousness systems",
    "creativity": "Creative expression, dream systems, and personality engines",
    "memory": "Memory management, storage, and retrieval systems",
    "reasoning": "Reasoning engines, logic processing, and decision making",
    "bridge": "Integration bridges, LLM wrappers, and communication engines",
    "api": "API endpoints and interfaces",
    "ethics": "Ethical frameworks and compliance systems",
    "identity": "Identity management, authentication, and persona systems",
    "orchestration": "Multi-agent orchestration and brain systems",
    "quantum": "Advanced probabilistic and parallel processing algorithms inspired by quantum computing principles",
    "symbolic": "Symbolic reasoning and vocabulary systems",
    "emotion": "Emotional modeling and affect systems",
    "voice": "Voice synthesis and audio processing",
    "perception": "Sensory processing and perception systems",
    "learning": "Learning algorithms and meta-learning systems",
    "narrative": "Narrative generation and storytelling",
    "embodiment": "Physical embodiment and robotics interfaces",
    "features": "Feature modules and components",
    "interfaces": "User interfaces and interaction systems",
    "meta": "Meta-learning and self-improvement systems",
    "security": "Security frameworks and access control",
    "simulation": "Simulation environments and testing",
    "tagging": "Tagging and categorization systems",
    "tools": "Development tools and utilities",
    "trace": "Tracing, logging, and debugging systems",
}


def analyze_module_imports(module_path: Path) -> Dict[str, List[str]]:
    """Analyze imports in a module to understand dependencies."""
    imports = {"internal": [], "external": [], "issues": []}

    python_files = list(module_path.rglob("*.py"))

    for py_file in python_files:
        if any(
            skip in str(py_file) for skip in [".venv", "__pycache__", "node_modules"]
        ):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
        except:
            continue

        # Find all imports
        import_pattern = r"(?:from\s+(\S+)\s+import|import\s+(\S+))"
        matches = re.findall(import_pattern, content)

        for match in matches:
            import_name = match[0] or match[1]
            if not import_name:
                continue

            # Check if it's an old lukhas import
            if "lukhas." in import_name:
                imports["issues"].append(f"{py_file.name}: Old import '{import_name}'")
            # Check if it's an internal module import
            elif import_name.split(".")[0] in MODULE_STRUCTURE:
                imports["internal"].append(import_name)
            # Otherwise it's external
            elif not import_name.startswith("."):
                imports["external"].append(import_name)

    # Deduplicate
    imports["internal"] = sorted(list(set(imports["internal"])))
    imports["external"] = sorted(list(set(imports["external"])))

    return imports


def generate_module_readme(module_name: str, module_path: Path) -> str:
    """Generate an updated README for a module."""
    description = MODULE_STRUCTURE.get(module_name, "Module description")

    # Analyze the module
    imports = analyze_module_imports(module_path)

    # Count Python files
    py_files = list(module_path.rglob("*.py"))
    py_files = [
        f
        for f in py_files
        if not any(skip in str(f) for skip in [".venv", "__pycache__"])
    ]

    # Find submodules
    subdirs = [
        d
        for d in module_path.iterdir()
        if d.is_dir() and not d.name.startswith((".", "__"))
    ]

    readme_content = f"""# {module_name.upper()} Module

## Overview
{description}

## Module Structure
- **Python Files**: {len(py_files)}
- **Submodules**: {len(subdirs)}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Directory Structure
```
{module_name}/
"""

    # Add directory tree (simplified)
    for subdir in sorted(subdirs)[:10]:  # Limit to first 10
        readme_content += f"├── {subdir.name}/\n"

    if len(subdirs) > 10:
        readme_content += f"└── ... ({len(subdirs) - 10} more directories)\n"

    readme_content += "```\n\n"

    # Add dependencies section
    if imports["internal"]:
        readme_content += "## Internal Dependencies\n"
        for dep in sorted(set(d.split(".")[0] for d in imports["internal"]))[:10]:
            readme_content += f"- `{dep}`\n"
        readme_content += "\n"

    # Add import issues if any
    if imports["issues"]:
        readme_content += "## ⚠️ Import Issues to Fix\n"
        for issue in imports["issues"][:5]:
            readme_content += f"- {issue}\n"
        if len(imports["issues"]) > 5:
            readme_content += f"- ... ({len(imports['issues']) - 5} more issues)\n"
        readme_content += "\n"

    # Add usage section
    readme_content += f"""## Usage

```python
# Import example
from {module_name} import ...

# Module initialization
# Add specific examples based on module content
```

## Key Components

"""

    # Find main classes/functions
    main_files = list(module_path.glob("*.py"))[:5]
    for py_file in main_files:
        if py_file.name == "__init__.py":
            continue
        readme_content += f"### `{py_file.stem}`\n"
        readme_content += (
            f"Module containing {py_file.stem.replace('_', ' ')} functionality.\n\n"
        )

    # Add development section
    readme_content += """## Development

### Running Tests
```bash
pytest tests/test_{module_name}*.py
```

### Adding New Features
1. Create new module file in appropriate subdirectory
2. Update `__init__.py` exports
3. Add tests in `tests/` directory
4. Update this README

## Related Documentation
- [Main README](../README.md)
- [Architecture Overview](../docs/architecture.md)
- [API Reference](../docs/api_reference.md)
"""

    return readme_content


def update_main_readme(base_path: Path):
    """Update the main README with current module structure."""
    readme_path = base_path / "README.md"

    content = """# LUKHAS AI System - Consolidated Repository

## 🧠 Overview
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) is an advanced AGI system with biological-inspired architecture, quantum-inspired processing capabilities, and multi-agent orchestration.

## 📋 Recent Updates
- **Repository Consolidation**: All lukhas modules have been reorganized for better structure
- **Import Path Updates**: Module imports have been updated to reflect new structure
- **Documentation**: All module documentation has been updated

## 🏗️ Module Structure

| Module | Description | Status |
|--------|-------------|--------|
"""

    for module, desc in sorted(MODULE_STRUCTURE.items()):
        module_path = base_path / module
        if module_path.exists():
            status = "✅ Active"
            py_files = len(list(module_path.rglob("*.py")))
            content += f"| [`{module}/`](./{module}) | {desc} | {status} ({py_files} files) |\n"

    content += """
## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Consolidation-Repo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```python
# Example: Using the core module
from core import lukhas_core
from consciousness import awareness
from memory import adaptive_memory

# Initialize system
system = lukhas_core.LukhasSystem()
system.initialize()
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_core*.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Syntax check
python scripts/check_syntax.py

# Fix imports
python scripts/fix_imports.py

# Update documentation
python scripts/update_documentation.py
```

## 📚 Documentation
- [Architecture Overview](./docs/architecture.md)
- [API Reference](./docs/api_reference.md)
- [Development Guide](./docs/development_guide.md)
- [Module Index](./INDEX.md)

## 🤝 Contributing
Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📄 License
See [LICENSE.md](./LICENSE.md) for details.

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return content


def main():
    """Main function to update documentation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update documentation across the codebase"
    )
    parser.add_argument("--path", type=str, default=".", help="Base path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be updated"
    )
    parser.add_argument("--modules", nargs="+", help="Specific modules to update")
    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    print(f"Updating documentation in: {base_path}")
    print("-" * 80)

    # Update main README
    if not args.modules or "README" in args.modules:
        print("Updating main README.md...")
        new_content = update_main_readme(base_path)
        if args.dry_run:
            print("Would update README.md")
        else:
            readme_path = base_path / "README.md"
            readme_path.write_text(new_content)
            print("✅ Updated README.md")

    # Update module READMEs
    modules_to_update = args.modules if args.modules else MODULE_STRUCTURE.keys()

    for module_name in modules_to_update:
        if module_name == "README":
            continue

        module_path = base_path / module_name
        if not module_path.exists():
            continue

        readme_path = module_path / "README.md"
        print(f"\nUpdating {module_name}/README.md...")

        new_content = generate_module_readme(module_name, module_path)

        if args.dry_run:
            print(f"Would update {module_name}/README.md")
            # Show import issues if any
            imports = analyze_module_imports(module_path)
            if imports["issues"]:
                print(f"  Found {len(imports['issues'])} import issues")
        else:
            readme_path.write_text(new_content)
            print(f"✅ Updated {module_name}/README.md")

    print("\n" + "=" * 80)
    print("Documentation update complete!")


if __name__ == "__main__":
    main()
