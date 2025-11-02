#!/usr/bin/env python3
"""
Update GitHub workflow files to remove lukhas/ path references.

This script updates workflow files to match the Phase 5B flat structure
where lukhas/ no longer exists at the root level.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

# Mapping of old paths to new paths (pattern, replacement function or string)
PATH_REPLACEMENTS = [
    # Directory references in commands
    (r"\blukhas/governance/guardian\.py\b", "labs/governance/guardian/guardian.py"),
    (r"\blukhas/identity/rate_limiting\.py\b", "labs/identity/rate_limiting.py"),
    (r"\blukhas/observability/alerts\b", "observability/alerts"),
    (r"\blukhas/governance/", "labs/governance/"),
    # Black, isort, flake8, mypy commands - scan core production directories
    (r"black --check lukhas/ tests/", "black --check consciousness/ identity/ governance/ memory/ core/ bio/ tests/"),
    (
        r"isort --check-only lukhas/ tests/",
        "isort --check-only consciousness/ identity/ governance/ memory/ core/ bio/ tests/",
    ),
    (r"flake8 lukhas/ tests/", "flake8 consciousness/ identity/ governance/ memory/ core/ bio/ tests/"),
    (r"mypy lukhas/", "mypy consciousness/ identity/ governance/ memory/ core/ bio/"),
    (r"bandit -r lukhas/", "bandit -r consciousness/ identity/ governance/ memory/ core/ bio/"),
    (r"ruff check lukhas/", "ruff check consciousness/ identity/ governance/ memory/ core/ bio/"),
    # Semgrep commands
    (r"semgrep --config=auto lukhas/governance/", "semgrep --config=auto labs/governance/"),
    # Grep commands checking for imports
    (
        r'grep -r "from lukhas\.quarantine" lukhas/ candidate/',
        'grep -r "from lukhas.quarantine" consciousness/ identity/ governance/ memory/ core/ bio/ labs/',
    ),
    # Directory checks
    (r'if \[ -d "lukhas/observability/alerts" \]', 'if [ -d "observability/alerts" ]'),
    (r'if \[ -f "lukhas/identity/rate_limiting\.py" \]', 'if [ -f "labs/identity/rate_limiting.py" ]'),
    (
        r'if grep -q "ProductionGuardian" lukhas/governance/guardian\.py',
        'if grep -q "ProductionGuardian" labs/governance/guardian/guardian.py',
    ),
    # Path patterns in YAML
    (r"- 'lukhas/identity/\*\*'", "- 'identity/**'\n      - 'labs/identity/**'"),
    (r"- 'lukhas/adapters/openai/\*\*'", "- 'bridge/adapters/**'"),
    (r"- 'lukhas/\*\*/\*\.py'", "- '**/*.py'\n      - 'labs/**/*.py'"),
    (
        r"- 'lukhas/\*\*'",
        "- 'consciousness/**'\n      - 'identity/**'\n      - 'governance/**'\n      - 'memory/**'\n      - 'core/**'\n      - 'bio/**'",
    ),
    (
        r'- "lukhas/\*\*"',
        '- "consciousness/**"\n      - "identity/**"\n      - "governance/**"\n      - "memory/**"\n      - "core/**"\n      - "bio/**"',
    ),
    (r"- 'lukhas/core/matriz/\*\*'", "- 'core/matriz/**'"),
    # String literals (module paths in arrays)
    (r'"lukhas/adapters/openai"', '"bridge/adapters"'),
    (r'"lukhas/core/reliability"', '"core/reliability"'),
    (r'"lukhas/observability"', '"observability"'),
    (r'"lukhas/observability/"', '"observability/"'),
    (r'"lukhas/core/registry\.py"', '"core/registry.py"'),
    (r'"lukhas/core/guardian/"', '"governance/guardian/"'),
    (r'"lukhas/core/import_router\.py"', '"core/import_router.py"'),
    (r'"lukhas/identity/"', '"identity/"'),
    (r'"lukhas/consciousness/"', '"consciousness/"'),
    # Python path checks and walks
    (
        r'startswith\(\("lukhas/","MATRIZ/"\)\)',
        'startswith(("consciousness/","identity/","governance/","memory/","core/","bio/","MATRIZ/"))',
    ),
    (
        r"path\.startswith\(\(\"lukhas/\", \"MATRIZ/\"\)\)",
        'path.startswith(("consciousness/", "identity/", "governance/", "memory/", "core/", "bio/", "MATRIZ/"))',
    ),
    (r"os\.walk\('lukhas/memory'\)", "os.walk('labs/memory')"),
    (r"os\.path\.exists\('lukhas/core/registry'\)", "os.path.exists('core/registry')"),
    # Coverage commands
    (r"--cov=\.\./lukhas/governance", "--cov=../labs/governance"),
    (
        r"'lukhas/': 'Core LUKHAS',",
        "'consciousness/': 'Consciousness',\n              'identity/': 'Identity',\n              'governance/': 'Governance',\n              'memory/': 'Memory',\n              'core/': 'Core',",
    ),
    (r"'lukhas/core/',", "'core/',"),
    # Bandit with multiple directories
    (r"-r lukhas/ scripts/", "-r consciousness/ identity/ governance/ memory/ core/ bio/ scripts/"),
    # Comments
    (
        r"# Phase B: Hot paths \(lukhas/adapters, lukhas/core/reliability\)",
        "# Phase B: Hot paths (bridge/adapters, core/reliability)",
    ),
    (r"\(lukhas/adapters, lukhas/core/reliability\)", "(bridge/adapters, core/reliability)"),
    # Mutation testing
    (r"--paths-to-mutate=lukhas/consciousness", "--paths-to-mutate=consciousness"),
    # Python main
    (r"python lukhas/main\.py", "python main.py"),
    # Specific file paths in commands
    (r"lukhas/identity/webauthn_api\.py", "identity/webauthn_api.py"),
    (r"lukhas/orchestration/api\.py", "orchestration/api.py"),
    (r"'lukhas/adapters/openai/api\.py'", "'bridge/adapters/openai_adapter.py'"),
    # Markdown table entries
    (r"\| Core \(lukhas/, MATRIZ/\)", "| Core (consciousness/, identity/, governance/, memory/, core/, bio/, MATRIZ/)"),
    # Documentation strings with lists
    (r"- `lukhas/`, `core/", "- `consciousness/`, `identity/`, `governance/`, `memory/`, `core/`,"),
]


def update_workflow_file(filepath: pathlib.Path) -> tuple[int, list[str]]:
    """
    Update a single workflow file.
    Returns (number of changes, list of changed lines)
    """
    content = filepath.read_text(encoding="utf-8")
    original = content
    changes = []

    for pattern, replacement in PATH_REPLACEMENTS:
        matches = list(re.finditer(pattern, content))
        if matches:
            for match in matches:
                old_text = match.group(0)
                changes.append(f"  {old_text} → {replacement}")

        content = re.sub(pattern, replacement, content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return (len(changes), changes)

    return (0, [])


def main():
    if not WORKFLOWS_DIR.exists():
        print(f"❌ Workflows directory not found: {WORKFLOWS_DIR}")
        return 1

    workflow_files = list(WORKFLOWS_DIR.glob("*.yml"))
    if not workflow_files:
        print(f"❌ No workflow files found in {WORKFLOWS_DIR}")
        return 1

    print(f"Found {len(workflow_files)} workflow files to check")

    total_updated = 0
    total_changes = 0

    for workflow in sorted(workflow_files):
        num_changes, changes = update_workflow_file(workflow)
        if num_changes > 0:
            total_updated += 1
            total_changes += num_changes
            print(f"\n✓ Updated {workflow.name}:")
            for change in changes:
                print(change)

    print("\n📊 Summary:")
    print(f"  Files updated: {total_updated}")
    print(f"  Total changes: {total_changes}")

    if total_updated == 0:
        print("\n✓ No updates needed - all workflows already use flat structure!")
    else:
        print(f"\n✓ Updated {total_updated} workflow files to use Phase 5B flat structure")

    return 0


if __name__ == "__main__":
    sys.exit(main())
