#!/usr/bin/env python3
"""
Module README Generator
=======================

Generate comprehensive README.md files for modules using enriched manifest data
and actual module content for T4/0.01% documentation standards.
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Optional


def extract_module_docstring(module_path: Path) -> Optional[str]:
    """Extract comprehensive docstring from module __init__.py."""
    init_file = module_path / "__init__.py"
    if not init_file.exists():
        return None

    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
            return tree.body[0].value.s
        elif tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            return tree.body[0].value.value

    except Exception as e:
        print(f"Warning: Could not extract docstring from {init_file}: {e}")

    return None


def generate_module_readme(module_path: Path) -> str:
    """Generate comprehensive README.md for a module."""

    # Load manifest
    manifest_file = module_path / "module.manifest.json"
    if not manifest_file.exists():
        return ""

    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error loading {manifest_file}: {e}")
        return ""

    module_name = manifest.get("module", module_path.name)
    description = manifest.get("description", f"LUKHAS {module_name} module")
    entrypoints = manifest.get("runtime", {}).get("entrypoints", [])
    tags = manifest.get("tags", [])
    dependencies = manifest.get("dependencies", [])
    team = manifest.get("ownership", {}).get("team", "Core")

    # Extract rich docstring if available
    docstring = extract_module_docstring(module_path)

    # Generate README content
    readme_lines = []

    # Header
    readme_lines.append(f"# {module_name.title()} Module")
    readme_lines.append("")
    readme_lines.append(f"> {description}")
    readme_lines.append("")

    # Badges
    badges = []
    if "t4-experimental" in tags:
        badges.append("![T4-Experimental](https://img.shields.io/badge/T4-Experimental-orange)")
    if "consciousness" in tags:
        badges.append("![Consciousness](https://img.shields.io/badge/Consciousness-Enabled-blue)")
    if "webauthn" in tags:
        badges.append("![WebAuthn](https://img.shields.io/badge/WebAuthn-Supported-green)")
    if "fold-architecture" in tags:
        badges.append("![Fold-Architecture](https://img.shields.io/badge/Fold-Architecture-Enabled-purple)")

    if badges:
        readme_lines.append(" ".join(badges))
        readme_lines.append("")

    # Quick overview
    readme_lines.append("## Overview")
    readme_lines.append("")

    if docstring:
        # Use rich docstring content
        docstring_lines = docstring.strip().split('\n')
        in_overview = False
        for line in docstring_lines:
            line = line.strip()
            if line.startswith('=') or not line:
                continue
            if "Key Features:" in line:
                break
            if in_overview or (len(line) > 20 and not line.endswith(':')):
                readme_lines.append(line)
                in_overview = True
        readme_lines.append("")
    else:
        readme_lines.append(description)
        readme_lines.append("")

    # Key Features (if available in docstring)
    if docstring and "Key Features:" in docstring:
        readme_lines.append("## Key Features")
        readme_lines.append("")
        in_features = False
        for line in docstring.split('\n'):
            line = line.strip()
            if "Key Features:" in line:
                in_features = True
                continue
            if in_features and line.startswith('-'):
                readme_lines.append(line)
            elif in_features and line and not line.startswith('-'):
                break
        readme_lines.append("")

    # API Reference
    if entrypoints:
        readme_lines.append("## API Reference")
        readme_lines.append("")
        readme_lines.append(f"The {module_name} module provides {len(entrypoints)} entrypoints:")
        readme_lines.append("")

        # Group entrypoints by category
        classes = [ep for ep in entrypoints if any(word in ep for word in ['Class', 'System', 'Hub', 'Monitor', 'Manager', 'Tracker', 'Engine'])]
        functions = [ep for ep in entrypoints if any(word in ep for word in ['create_', 'get_', 'process_', 'validate_', 'activate_', 'monitor_'])]
        others = [ep for ep in entrypoints if ep not in classes and ep not in functions]

        if classes:
            readme_lines.append("### Core Classes")
            readme_lines.append("")
            for cls in sorted(classes)[:10]:  # Top 10
                class_name = cls.split('.')[-1]
                readme_lines.append(f"- `{class_name}` - {cls}")
            readme_lines.append("")

        if functions:
            readme_lines.append("### Functions")
            readme_lines.append("")
            for func in sorted(functions)[:10]:  # Top 10
                func_name = func.split('.')[-1]
                readme_lines.append(f"- `{func_name}()` - {func}")
            readme_lines.append("")

    # Installation/Usage
    readme_lines.append("## Usage")
    readme_lines.append("")
    readme_lines.append(f"Import the {module_name} module:")
    readme_lines.append("")
    readme_lines.append("```python")
    readme_lines.append(f"import {module_name}")
    readme_lines.append("")
    if entrypoints:
        # Show a few key imports
        key_imports = [ep for ep in entrypoints[:3] if '.' in ep]
        if key_imports:
            readme_lines.append("# Key components")
            for imp in key_imports:
                parts = imp.split('.')
                if len(parts) >= 2:
                    class_name = parts[-1]
                    module_part = '.'.join(parts[:-1])
                    readme_lines.append(f"from {module_part} import {class_name}")
    readme_lines.append("```")
    readme_lines.append("")

    # Dependencies
    if dependencies:
        readme_lines.append("## Dependencies")
        readme_lines.append("")
        readme_lines.append("This module depends on:")
        readme_lines.append("")
        for dep in dependencies:
            readme_lines.append(f"- `{dep}` module")
        readme_lines.append("")

    # Tags/Categories
    if tags:
        readme_lines.append("## Categories")
        readme_lines.append("")
        tag_descriptions = {
            'consciousness': 'Consciousness processing and awareness systems',
            'memory': 'Memory management and storage systems',
            'identity': 'Identity and authentication systems',
            'governance': 'Governance and policy enforcement',
            'orchestration': 'System orchestration and coordination',
            'webauthn': 'WebAuthn and passwordless authentication',
            'fold-architecture': 'Fold-based memory architecture',
            't4-experimental': 'T4/0.01% experimental systems',
            'bio-symbolic': 'Bio-symbolic processing systems',
            'quantum-inspired': 'Quantum-inspired algorithms'
        }

        for tag in sorted(tags):
            if tag in tag_descriptions:
                readme_lines.append(f"- **{tag}**: {tag_descriptions[tag]}")
            else:
                readme_lines.append(f"- **{tag}**")
        readme_lines.append("")

    # Team information
    readme_lines.append("## Team")
    readme_lines.append("")
    readme_lines.append(f"**Owner**: {team} Team")
    readme_lines.append("")
    codeowners = manifest.get("ownership", {}).get("codeowners", [])
    if codeowners:
        readme_lines.append("**Code Owners**:")
        for owner in codeowners:
            readme_lines.append(f"- {owner}")
        readme_lines.append("")

    # Footer
    readme_lines.append("---")
    readme_lines.append("")
    readme_lines.append("*This documentation is generated from the module manifest and source code.*")

    return '\n'.join(readme_lines)


def main():
    """Generate README files for key modules."""
    repo_root = Path.cwd()

    # Priority modules for README generation
    priority_modules = [
        'brain', 'consciousness', 'memory', 'identity', 'governance',
        'matriz', 'core', 'api', 'bridge', 'orchestration'
    ]

    print("📝 Generating comprehensive README.md files...")

    generated_count = 0

    for module_name in priority_modules:
        module_path = repo_root / module_name
        if module_path.exists() and (module_path / "module.manifest.json").exists():
            readme_content = generate_module_readme(module_path)
            if readme_content:
                readme_file = module_path / "README.md"
                try:
                    with open(readme_file, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    print(f"✅ Generated README for {module_name}")
                    generated_count += 1
                except Exception as e:
                    print(f"❌ Error writing README for {module_name}: {e}")

    print(f"\n🎯 Generated {generated_count} comprehensive README files")


if __name__ == "__main__":
    main()