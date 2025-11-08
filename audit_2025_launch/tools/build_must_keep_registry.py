#!/usr/bin/env python3
"""
Build comprehensive must-keep file registry for LUKHAS public launch.
"""
import json
from pathlib import Path
from typing import List, Set


def find_entry_points(base_dir: Path) -> List[str]:
    """Find all entry point files."""
    entry_points = []

    # Main entry points
    candidates = [
        'main.py',
        'serve/main.py',
        'lukhas/api/app.py',
        'pyproject.toml',
        'setup.py',
        'Makefile',
        'README.md',
        'LICENSE',
        'CLAUDE.md'
    ]

    for candidate in candidates:
        path = base_dir / candidate
        if path.exists():
            entry_points.append(str(path.relative_to(base_dir)))

    return entry_points

def find_production_lane_files(base_dir: Path) -> List[str]:
    """Find all production lane (lukhas/) files."""
    files = []
    lukhas_dir = base_dir / 'lukhas'

    if lukhas_dir.exists():
        for file_path in lukhas_dir.rglob('*.py'):
            if not any(x in str(file_path) for x in ['__pycache__', '.venv', 'test_']):
                files.append(str(file_path.relative_to(base_dir)))

    return files

def find_matriz_engine_files(base_dir: Path) -> List[str]:
    """Find MATRIZ cognitive engine files."""
    files = []
    matriz_dir = base_dir / 'matriz'

    if matriz_dir.exists():
        for file_path in matriz_dir.rglob('*.py'):
            if not any(x in str(file_path) for x in ['__pycache__', '.venv']):
                files.append(str(file_path.relative_to(base_dir)))

    return files

def find_core_integration_files(base_dir: Path) -> List[str]:
    """Find core integration layer files."""
    files = []
    core_dir = base_dir / 'core'

    if core_dir.exists():
        for file_path in core_dir.rglob('*.py'):
            if not any(x in str(file_path) for x in ['__pycache__', '.venv', '/archive/', '/quarantine/']):
                files.append(str(file_path.relative_to(base_dir)))

    return files

def find_critical_tests(base_dir: Path) -> List[str]:
    """Find smoke tests and tier1 tests (critical for launch)."""
    files = []
    tests_dir = base_dir / 'tests'

    if tests_dir.exists():
        # Find smoke tests
        for file_path in tests_dir.rglob('*.py'):
            if 'smoke' in str(file_path) and not '__pycache__' in str(file_path):
                files.append(str(file_path.relative_to(base_dir)))

    return files

def find_branding_assets(base_dir: Path) -> List[str]:
    """Find branding assets critical for public launch."""
    files = []
    branding_dir = base_dir / 'branding'

    if branding_dir.exists():
        # Include website content, logos, official messaging
        patterns = ['*.md', '*.json', '*.yaml', '*.yml']
        for pattern in patterns:
            for file_path in branding_dir.rglob(pattern):
                if not any(x in str(file_path) for x in ['__pycache__', '.venv', '/archive/', '_old']):
                    files.append(str(file_path.relative_to(base_dir)))

    return files

def find_mcp_servers(base_dir: Path) -> List[str]:
    """Find MCP server implementations."""
    files = []
    mcp_dir = base_dir / 'mcp-servers'

    if mcp_dir.exists():
        for file_path in mcp_dir.rglob('*.py'):
            if '__pycache__' not in str(file_path):
                files.append(str(file_path.relative_to(base_dir)))

    return files

def find_critical_configs(base_dir: Path) -> List[str]:
    """Find critical configuration files (non-secret)."""
    files = []

    # GitHub Actions workflows (critical for CI/CD)
    workflows_dir = base_dir / '.github' / 'workflows'
    if workflows_dir.exists():
        for file_path in workflows_dir.glob('*.yml'):
            files.append(str(file_path.relative_to(base_dir)))

    # Root configs
    config_files = [
        'pyproject.toml',
        'requirements.txt',
        '.gitignore',
        '.python-version',
        'Makefile'
    ]

    for config_file in config_files:
        path = base_dir / config_file
        if path.exists():
            files.append(config_file)

    return files

def find_critical_documentation(base_dir: Path) -> List[str]:
    """Find critical documentation for launch."""
    files = []

    # Root level docs
    root_docs = [
        'README.md',
        'CLAUDE.md',
        'LICENSE',
        'CONTRIBUTING.md',
        'SECURITY.md',
        'CODE_OF_CONDUCT.md'
    ]

    for doc in root_docs:
        path = base_dir / doc
        if path.exists():
            files.append(doc)

    # Critical docs/ content
    docs_dir = base_dir / 'docs'
    if docs_dir.exists():
        critical_docs = [
            'docs/README.md',
            'docs/architecture/README.md',
            'docs/api/README.md',
            'docs/development/README.md'
        ]
        for doc in critical_docs:
            path = base_dir / doc
            if path.exists():
                files.append(doc)

    return files

def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract Python imports from a file."""
    imports = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple regex-based import extraction
        import re
        # Match "import foo" and "from foo import bar"
        import_pattern = r'(?:from\s+([a-zA-Z0-9_.]+)|import\s+([a-zA-Z0-9_.]+))'
        matches = re.findall(import_pattern, content)

        for match in matches:
            # match is a tuple (from_import, direct_import)
            module = match[0] if match[0] else match[1]
            if module:
                # Get top-level module
                top_module = module.split('.')[0]
                # Only include local imports (lukhas, matriz, core, candidate)
                if top_module in ['lukhas', 'matriz', 'core', 'candidate']:
                    imports.add(top_module)

    except Exception as e:
        pass  # Skip files with encoding issues

    return imports

def build_dependency_map(base_dir: Path, root_files: List[str]) -> Set[str]:
    """Build transitive dependency map from root files."""
    dependencies = set(root_files)
    to_process = list(root_files)
    processed = set()

    max_iterations = 1000  # Prevent infinite loops
    iteration = 0

    while to_process and iteration < max_iterations:
        current = to_process.pop(0)
        if current in processed:
            continue

        processed.add(current)
        file_path = base_dir / current

        if file_path.exists() and file_path.suffix == '.py':
            imports = extract_imports_from_file(file_path)

            for imp in imports:
                # Convert module to file path
                # lukhas.api.app -> lukhas/api/app.py
                possible_file = f"{imp.replace('.', '/')}/__init__.py"
                possible_file2 = f"{imp.replace('.', '/')}.py"

                for candidate in [possible_file, possible_file2]:
                    if candidate not in dependencies and (base_dir / candidate).exists():
                        dependencies.add(candidate)
                        to_process.append(candidate)

        iteration += 1

    return dependencies

def main():
    """Main registry builder."""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = Path(__file__).parent.parent / 'reports'

    print("Building must-keep file registry...")
    print(f"Base directory: {base_dir}")

    # Collect critical files by category
    registry = {
        'summary': {
            'total_must_keep_files': 0,
            'by_category': {}
        },
        'files': {}
    }

    categories = {
        'entry_points': find_entry_points(base_dir),
        'production_lane': find_production_lane_files(base_dir),
        'matriz_engine': find_matriz_engine_files(base_dir),
        'core_integration': find_core_integration_files(base_dir),
        'critical_tests': find_critical_tests(base_dir),
        'branding_assets': find_branding_assets(base_dir),
        'mcp_servers': find_mcp_servers(base_dir),
        'critical_configs': find_critical_configs(base_dir),
        'critical_docs': find_critical_documentation(base_dir)
    }

    # Build file registry
    all_files = {}
    for category, files in categories.items():
        print(f"  {category}: {len(files)} files")
        registry['summary']['by_category'][category] = len(files)

        for file_path in files:
            if file_path not in all_files:
                all_files[file_path] = []
            all_files[file_path].append(category)

    # Add to registry with metadata
    for file_path, cats in all_files.items():
        full_path = base_dir / file_path
        size = full_path.stat().st_size if full_path.exists() else 0

        registry['files'][file_path] = {
            'categories': cats,
            'priority': 'critical' if 'entry_points' in cats else 'high',
            'size_bytes': size,
            'reason': f"Required for {', '.join(cats)}"
        }

    registry['summary']['total_must_keep_files'] = len(all_files)

    # Save registry
    output_file = output_dir / 'must_keep_registry.json'
    with open(output_file, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"\nMust-keep registry saved to: {output_file}")
    print(f"Total must-keep files: {registry['summary']['total_must_keep_files']}")
    print("\nBy category:")
    for category, count in registry['summary']['by_category'].items():
        print(f"  {category}: {count}")

    # Calculate total size
    total_size_mb = sum(f['size_bytes'] for f in registry['files'].values()) / 1024 / 1024
    print(f"\nTotal size: {total_size_mb:.2f} MB")

    return 0

if __name__ == '__main__':
    exit(main())
