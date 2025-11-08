#!/usr/bin/env python3
"""
Root Documentation Hygiene Validator

STRICT validator that blocks new documentation files from being added to root.
Specifically targets .md, .txt, and similar documentation files.

Exit codes:
    0 - No unauthorized documentation at root
    1 - Unauthorized documentation files found
    2 - Configuration error
"""

import sys
from pathlib import Path
# Allowed documentation files at root (grandfathered in)
ALLOWED_DOCS = {
    'README.md',
    'SECURITY.md',
    'LICENSE',
    'LICENSE.md',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'gemini.md',
    'lukhas_context.md',
    'claude.me',
}

# Documentation file extensions to check
DOC_EXTENSIONS = {
    '.md', '.txt', '.rst', '.adoc', '.asciidoc',
    '.org', '.textile', '.rdoc', '.creole',
}

# Allowed patterns for non-documentation text files
ALLOWED_TXT_PATTERNS = {
    'requirements',  # requirements.txt, requirements-dev.txt, etc.
    'constraints',   # constraints.txt
}

# Allowed temporary/log patterns (should be in .gitignore)
TEMP_PATTERNS = {
    'coverage',      # coverage.txt, coverage_baseline.txt
    'smoke_',        # smoke_collection_log.txt, smoke_errors_sample.txt
    'branch_audit',  # branch_audit_2025-11-03.txt
    'collection_',   # collection_test.txt
    'error_',        # error_analysis.txt
    'context_',      # context_files.txt
    'lukhas_agent',  # lukhas_agent_todos.txt
}


def is_doc_file(path: Path) -> bool:
    """Check if file is a documentation file."""
    return path.suffix.lower() in DOC_EXTENSIONS


def is_allowed_doc(name: str) -> bool:
    """Check if documentation file is explicitly allowed."""
    # Hidden files are allowed (should be in .gitignore anyway)
    if name.startswith('.'):
        return True

    if name in ALLOWED_DOCS:
        return True

    # Allow requirements.txt and similar
    if name.endswith('.txt'):
        base = name.rsplit('.', 1)[0]
        for pattern in ALLOWED_TXT_PATTERNS:
            if base.startswith(pattern):
                return True
        # Allow temporary/log files
        for pattern in TEMP_PATTERNS:
            if base.startswith(pattern):
                return True

    return False


def get_root_doc_files(repo_root: Path) -> list[Path]:
    """Get all documentation files at repository root."""
    doc_files = []
    for item in repo_root.iterdir():
        if item.is_file() and is_doc_file(item):
            doc_files.append(item)
    return doc_files


def main() -> int:
    """Main validation logic."""
    repo_root = Path(__file__).parent.parent.resolve()

    # Get all documentation files at root
    doc_files = get_root_doc_files(repo_root)

    # Check each file
    violations = []
    for doc_file in sorted(doc_files):
        if not is_allowed_doc(doc_file.name):
            violations.append(doc_file.name)

    # Report results
    if violations:
        print("❌ Root documentation hygiene check FAILED", file=sys.stderr)
        print(f"\n🚫 Unauthorized documentation files at root ({len(violations)}):", file=sys.stderr)
        for name in violations:
            print(f"  - {name}", file=sys.stderr)

        print("\n📋 Required actions:", file=sys.stderr)
        print("  Documentation files must be organized in docs/ subdirectories:", file=sys.stderr)
        print("  - Agent guides → docs/agents/", file=sys.stderr)
        print("  - Session notes → docs/sessions/", file=sys.stderr)
        print("  - Status reports → docs/project_status/", file=sys.stderr)
        print("  - Test documentation → docs/testing/", file=sys.stderr)
        print("  - Security docs → docs/security/", file=sys.stderr)
        print("  - MATRIZ docs → docs/matriz/", file=sys.stderr)
        print("  - Bridge docs → docs/bridge/", file=sys.stderr)
        print("  - Codex docs → docs/codex/", file=sys.stderr)
        print("  - Audit reports → docs/audits/", file=sys.stderr)
        print("  - General docs → docs/", file=sys.stderr)

        print("\n✅ Only these documentation files allowed at root:", file=sys.stderr)
        for allowed in sorted(ALLOWED_DOCS):
            print(f"  - {allowed}", file=sys.stderr)

        print("\n🔧 To fix: git mv <file> docs/<appropriate-subdir>/", file=sys.stderr)

        return 1

    print("✅ Root documentation hygiene check PASSED")
    print(f"   All {len(doc_files)} documentation files at root are authorized")
    return 0


if __name__ == '__main__':
    sys.exit(main())
