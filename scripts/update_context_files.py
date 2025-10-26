#!/usr/bin/env python3
"""
Update all claude.me and lukhas_context.md files with latest system metrics and information.

This script updates context files across the entire LUKHAS repository with:
- Current file counts and statistics
- Latest deployment status (GA readiness)
- Recent documentation additions
- Updated dates and version information
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Key metrics to update (based on latest analysis)
METRICS = {
    "total_python_files": "33,845",
    "products_files": "4,107",
    "lukhas_files": "235",
    "total_context_files": "2,250",
    "claude_me_files": "343",
    "lukhas_context_files": "1,907",
    "last_updated": "2025-10-18",
    "ga_readiness": "66.7%",
    "rc_soak_success": "99.985%",
    "dependency_count": "196",
    "cve_count": "0",
}

# Key documentation additions
NEW_DOCS = [
    "docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures",
    "docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance",
    "docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)",
]

# Recent major changes
RECENT_CHANGES = [
    "E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)",
    "OpenAI façade validation - Full SDK compatibility",
    "Guardian MCP server deployment - Production ready",
    "Shadow diff harness - Pre-audit validation framework",
    "MATRIZ evaluation harness - Comprehensive testing",
]


def find_all_context_files() -> Tuple[List[Path], List[Path]]:
    """Find all claude.me and lukhas_context.md files."""
    repo_root = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    claude_me_files = list(repo_root.rglob("claude.me"))
    lukhas_context_files = list(repo_root.rglob("lukhas_context.md"))

    # Exclude certain directories
    exclude_patterns = [
        ".venv", "venv", "__pycache__", "node_modules",
        ".git", "dist", "build", "*.egg-info",
        "temp/ backups", "htmlcov"
    ]

    def should_exclude(path: Path) -> bool:
        path_str = str(path)
        return any(pattern in path_str for pattern in exclude_patterns)

    claude_me_files = [f for f in claude_me_files if not should_exclude(f)]
    lukhas_context_files = [f for f in lukhas_context_files if not should_exclude(f)]

    return claude_me_files, lukhas_context_files


def update_date_references(content: str) -> str:
    """Update date references in content."""
    # Update "Last Updated" dates
    content = re.sub(
        r'\*\*Last Updated\*\*:\s*\d{4}-\d{2}-\d{2}',
        f'**Last Updated**: {METRICS["last_updated"]}',
        content,
        flags=re.IGNORECASE
    )

    # Update standalone date patterns
    content = re.sub(
        r'Last Updated:\s*\d{4}-\d{2}-\d{2}',
        f'Last Updated: {METRICS["last_updated"]}',
        content,
        flags=re.IGNORECASE
    )

    return content


def update_file_counts(content: str) -> str:
    """Update file count references."""
    # Update total files
    content = re.sub(
        r'\*\*Total Files\*\*:\s*[\d,]+\+?',
        f'**Total Files**: {METRICS["total_python_files"]}+',
        content,
        flags=re.IGNORECASE
    )

    # Update products files
    content = re.sub(
        r'PRODUCTS\s+Domain[:\s]+[\d,]+\s+files',
        f'PRODUCTS Domain: {METRICS["products_files"]} files',
        content,
        flags=re.IGNORECASE
    )

    # Update lukhas files
    content = re.sub(
        r'LUKHAS\s+Core[:\s]+[\d,]+\s+files',
        f'LUKHAS Core: {METRICS["lukhas_files"]} files',
        content,
        flags=re.IGNORECASE
    )

    # Update context files count
    content = re.sub(
        r'\*\*Context Files\*\*:\s*[\d,]+\+?',
        f'**Context Files**: {METRICS["total_context_files"]}+',
        content,
        flags=re.IGNORECASE
    )

    return content


def add_ga_status_section(content: str) -> str:
    """Add or update GA deployment status section."""
    ga_section = f"""
## 🚀 GA Deployment Status

**Current Status**: {METRICS["ga_readiness"]} Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation ({METRICS["rc_soak_success"]} success rate)
- ✅ **Dependency Audit**: {METRICS["dependency_count"]} packages, {METRICS["cve_count"]} CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
{chr(10).join(f"- {doc}" for doc in NEW_DOCS)}

### Recent Updates
{chr(10).join(f"- {change}" for change in RECENT_CHANGES)}

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
"""

    # Check if GA section already exists
    if "GA Deployment Status" in content or "GA DEPLOYMENT STATUS" in content:
        # Replace existing section (find between ## GA and next ##)
        pattern = r'##\s+🚀?\s*GA\s+Deployment\s+Status.*?(?=\n##|\Z)'
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            content = re.sub(pattern, ga_section.strip(), content, flags=re.DOTALL | re.IGNORECASE)
        else:
            # Append if not found
            content = content.rstrip() + "\n\n" + ga_section
    else:
        # Add before the last section or at the end
        if "## 📚 Context Navigation" in content:
            content = content.replace("## 📚 Context Navigation", ga_section + "## 📚 Context Navigation")
        else:
            content = content.rstrip() + "\n\n" + ga_section

    return content


def update_context_file(file_path: Path, dry_run: bool = False) -> bool:
    """Update a single context file with latest information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content

        # Apply updates
        content = update_date_references(content)
        content = update_file_counts(content)

        # Add GA status section only to main/root level claude.me files
        if file_path.name == "claude.me" and len(file_path.parts) <= 8:  # Heuristic for "root-level"
            content = add_ga_status_section(content)

        # Check if content changed
        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                print(f"Would update: {file_path}")
                return True

        return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main execution function."""
    print("=" * 80)
    print("LUKHAS Context Files Update Script")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated metrics: {METRICS['last_updated']}")
    print()

    # Find all files
    print("Scanning for context files...")
    claude_me_files, lukhas_context_files = find_all_context_files()

    print(f"Found {len(claude_me_files)} claude.me files")
    print(f"Found {len(lukhas_context_files)} lukhas_context.md files")
    print(f"Total: {len(claude_me_files) + len(lukhas_context_files)} files to update")
    print()

    # Dry run first
    print("Running dry-run to preview changes...")
    dry_run_changes = 0

    for file_path in claude_me_files:
        if update_context_file(file_path, dry_run=True):
            dry_run_changes += 1

    for file_path in lukhas_context_files:
        if update_context_file(file_path, dry_run=True):
            dry_run_changes += 1

    print(f"\nDry run complete: {dry_run_changes} files would be updated")
    print()

    # Confirm before proceeding
    response = input("Proceed with actual updates? (yes/no): ").strip().lower()

    if response != "yes":
        print("Update cancelled.")
        return

    # Actual update
    print("\nUpdating files...")
    updated_count = 0

    for file_path in claude_me_files:
        if update_context_file(file_path, dry_run=False):
            updated_count += 1
            if updated_count % 50 == 0:
                print(f"  Updated {updated_count} files...")

    for file_path in lukhas_context_files:
        if update_context_file(file_path, dry_run=False):
            updated_count += 1
            if updated_count % 50 == 0:
                print(f"  Updated {updated_count} files...")

    print()
    print("=" * 80)
    print(f"✅ Update complete: {updated_count} files updated")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review changes: git diff")
    print("2. Commit changes: git add . && git commit -m 'docs: update all context files with latest metrics and GA status'")
    print()


if __name__ == "__main__":
    main()
