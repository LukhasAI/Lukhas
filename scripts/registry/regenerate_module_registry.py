"""
Regenerates the LUKHAS Module Registry documentation.

This script scans the 'lukhas' namespace to discover all modules,
extracts metadata such as version and dependencies, and determines
the module's development "lane" based on its location.

It generates a Markdown report in 'docs/REPOSITORY_STATE_YYYYMMDD.md'.
"""

import ast
import importlib
import os
import pkgutil
import sys
from datetime import datetime
from unittest.mock import MagicMock

import tomllib

# A set to keep track of modules that failed to import even after mocking
_failed_imports = set()


def get_lane(module_path):
    """Determines the development lane based on the module path."""
    if 'candidate/' in module_path:
        return 'Candidate'
    if 'MATRIZ/' in module_path.upper(): # Case-insensitive check for MATRIZ
        return 'MATRIZ'
    if 'lukhas/' in module_path:
        return 'LUKHAS'
    if 'products/' in module_path:
        return 'Products'
    return 'Unknown'

def get_imports_from_file(file_path):
    """Parses a Python file to extract top-level imports."""
    imports = set()
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
    return sorted(list(imports))


def get_module_info(module_name):
    """
    Imports a module, mocking dependencies if necessary, and extracts its info.
    """
    if module_name in _failed_imports:
        return None, [], "Failed"

    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'N/A')
        return module, version, "Success"
    except ImportError as e:
        missing_module = e.name
        if missing_module and missing_module not in sys.modules:
            print(f"Info: Mocking missing module '{missing_module}' to import '{module_name}'")
            sys.modules[missing_module] = MagicMock()
            # Retry importing
            return get_module_info(module_name)
        else:
            print(f"Warning: Failed to import '{module_name}': {e}", file=sys.stderr)
            _failed_imports.add(module_name)
            return None, [], "Failed"
    except Exception as e:
        print(f"Warning: Could not get info for module '{module_name}': {e}", file=sys.stderr)
        _failed_imports.add(module_name)
        return None, [], "Failed"

def discover_modules(path, prefix):
    """Discovers all modules in a given path."""
    module_inventory = []
    for finder, name, ispkg in pkgutil.walk_packages(path, prefix):
        module, version, status = get_module_info(name)

        if module:
            filepath = getattr(module, '__file__', 'N/A')
            imports = get_imports_from_file(filepath) if filepath and filepath.endswith('.py') else []
            lane = get_lane(filepath)

            module_inventory.append({
                "name": name,
                "version": version,
                "lane": lane,
                "path": filepath,
                "dependencies": imports,
                "status": status,
            })
        else:
             module_inventory.append({
                "name": name,
                "version": "N/A",
                "lane": "Unknown",
                "path": "N/A",
                "dependencies": [],
                "status": status,
            })

    return sorted(module_inventory, key=lambda x: x['name'])


def generate_report(module_inventory, project_meta):
    """Generates the Markdown report."""
    today = datetime.now().strftime("%Y-%m-%d")
    report = [
        f"# Repository State as of {today}",
        "",
        "## Project Overview",
        f"- **Name**: {project_meta.get('name', 'N/A')}",
        f"- **Version**: {project_meta.get('version', 'N/A')}",
        f"- **Python Version**: {project_meta.get('requires-python', 'N/A')}",
        "",
        "## Module Inventory",
        "",
        "| Module | Version | Assigned Lane | Dependencies |",
        "|---|---|---|---|",
    ]

    for mod in module_inventory:
        deps = f"`{', '.join(mod['dependencies'])}`" if mod['dependencies'] else " "
        report.append(f"| `{mod['name']}` | {mod['version']} | {mod['lane']} | {deps} |")

    return "\n".join(report)


def main():
    """Main function to generate the module registry."""
    print("Starting module registry regeneration...")

    try:
        with open("pyproject.toml", "rb") as f:
            project_meta = tomllib.load(f).get("project", {})
    except FileNotFoundError:
        print("Error: pyproject.toml not found.", file=sys.stderr)
        sys.exit(1)

    # Add project root to path to ensure lukhas is importable
    sys.path.insert(0, os.getcwd())

    import lukhas

    module_path = lukhas.__path__
    module_prefix = lukhas.__name__ + "."

    print(f"Scanning for modules in '{module_prefix[:-1]}'...")
    inventory = discover_modules(module_path, module_prefix)

    report_content = generate_report(inventory, project_meta)

    report_filename = f"docs/REPOSITORY_STATE_{datetime.now().strftime('%Y%m%d')}.md"

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Successfully generated module registry at: {report_filename}")

    # Clean up mocked modules
    for mod in list(sys.modules.keys()):
        if isinstance(sys.modules[mod], MagicMock):
            del sys.modules[mod]

if __name__ == "__main__":
    main()
