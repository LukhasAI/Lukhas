#!/usr/bin/env python3
"""
Safe Cleanup Analysis for LUKHAS AI
Combines usage analysis with AI/AGI value scoring to prevent accidental deletion
Trinity Framework: ⚛️🧠🛡️
"""

import json
from pathlib import Path


def load_reports():
    """Load both usage and audit reports"""
    with open("module_usage_report.json") as f:
        usage_report = json.load(f)

    with open("orphaned_modules_audit.json") as f:
        audit_report = json.load(f)

    return usage_report, audit_report


def categorize_safe_cleanup(usage_report: dict, audit_report: dict) -> dict[str, list[str]]:
    """Categorize files for safe cleanup based on both usage and AI value"""

    # Build a value score index from audit report
    value_scores = {}

    for category in [
        "high_value",
        "medium_value",
        "needs_review",
        "low_value",
        "safe_to_archive",
    ]:
        for file_info in audit_report.get(category, []):
            file_path = file_info.get("file_path", "")
            score = file_info.get("value_score", 0)
            value_scores[file_path] = score

    # Get all orphaned files
    never_imported = usage_report.get("never_imported", [])

    # Categorize with safety checks
    categories = {
        "high_value_keep": [],  # Score > 100 - NEVER DELETE
        "needs_manual_review": [],  # Score 50-100 or contains AI/AGI keywords
        "test_workspace_files": [],  # Agent workspace test files (safe to archive)
        "duplicate_implementations": [],  # Old/duplicate implementations
        "documentation_examples": [],  # Examples and demos
        "truly_safe_to_archive": [],  # Low value, no AI content
    }

    # Critical patterns that should NEVER be auto-deleted
    critical_patterns = [
        "orchestrat",
        "consciousness",
        "memory",
        "identity",
        "governance",
        "quantum",
        "bio",
        "emotion",
        "reasoning",
        "symbolic",
        "constellation",
        "guardian",
        "lukhas",
        "ai_",
        "agi",
        "neural",
        "cognitive",
    ]

    for file in never_imported:
        Path(file)
        score = value_scores.get(file, 0)

        # Check if it contains critical patterns
        has_critical = any(pattern in file.lower() for pattern in critical_patterns)

        # Categorize based on score and patterns
        if score > 100:
            categories["high_value_keep"].append(file)
        elif score >= 50 or has_critical:
            categories["needs_manual_review"].append(file)
        elif "CLAUDE_ARMY/workspaces" in file and "/test" in file:
            categories["test_workspace_files"].append(file)
        elif any(x in file for x in ["_old", "_backup", "_copy", "deprecated", "legacy"]):
            categories["duplicate_implementations"].append(file)
        elif any(x in file for x in ["example", "demo", "sample", "tutorial"]):
            categories["documentation_examples"].append(file)
        elif score < 20 and not has_critical:
            categories["truly_safe_to_archive"].append(file)
        else:
            categories["needs_manual_review"].append(file)

    return categories


def generate_safe_cleanup_script(categories: dict[str, list[str]]) -> str:
    """Generate a SAFE cleanup script that preserves AI/AGI value"""

    script = """#!/bin/bash
# LUKHAS AI Safe Cleanup Script
# Trinity Framework: ⚛️🧠🛡️
#
# This script ONLY archives files with LOW AI/AGI value
# All high-value AI logic is preserved

set -e  # Exit on error

ARCHIVE_DIR="/Users/agi_dev/lukhas-archive/2025-08-13-safe-cleanup"
mkdir -p "$ARCHIVE_DIR"

echo "🛡️ Starting SAFE LUKHAS AI cleanup..."
echo "⚠️  Preserving all high-value AI/AGI modules"
echo ""

"""

    # Only archive truly safe files
    if categories["test_workspace_files"]:
        script += """
# Archive isolated test workspace files
echo "📦 Archiving workspace test files..."
mkdir -p "$ARCHIVE_DIR/workspace_tests"
"""
        for file in categories["test_workspace_files"][:10]:
            script += f'mv "{file}" "$ARCHIVE_DIR/workspace_tests/" 2>/dev/null || true\n'

    if categories["documentation_examples"]:
        script += """
# Archive example/demo files
echo "📚 Archiving documentation examples..."
mkdir -p "$ARCHIVE_DIR/examples"
"""
        for file in categories["documentation_examples"][:10]:
            script += f'mv "{file}" "$ARCHIVE_DIR/examples/" 2>/dev/null || true\n'

    if categories["truly_safe_to_archive"]:
        script += """
# Archive low-value files with no AI content
echo "🗂️ Archiving low-value files..."
mkdir -p "$ARCHIVE_DIR/low_value"
"""
        for file in categories["truly_safe_to_archive"][:20]:
            script += f'mv "{file}" "$ARCHIVE_DIR/low_value/" 2>/dev/null || true\n'

    script += """
echo ""
echo "✅ Safe cleanup complete!"
echo "📊 Files archived to: $ARCHIVE_DIR"
echo ""
echo "⚠️  PRESERVED FILES:"
"""

    # List preserved high-value files
    if categories["high_value_keep"]:
        script += f'echo "  - {len(categories["high_value_keep"])} high-value AI/AGI modules preserved"\n'

    if categories["needs_manual_review"]:
        script += f'echo "  - {len(categories["needs_manual_review"])} files need manual review"\n'

    script += """
echo ""
echo "💾 Run 'git status' to see changes"
echo "📋 Check 'safe_cleanup_review.txt' for files needing manual review"
"""

    return script


def main():
    print("🔍 Performing SAFE cleanup analysis...")
    print("⚠️  This tool preserves all AI/AGI value")

    # Load reports
    usage_report, audit_report = load_reports()

    # Categorize with safety checks
    categories = categorize_safe_cleanup(usage_report, audit_report)

    # Print analysis
    print("\n📊 SAFE CLEANUP ANALYSIS")
    print("=" * 60)

    print(f"\n🛡️ HIGH VALUE - MUST KEEP: {len(categories['high_value_keep'])} files")
    for file in categories["high_value_keep"][:5]:
        print(f"  ✓ {file}")

    print(f"\n⚠️ NEEDS MANUAL REVIEW: {len(categories['needs_manual_review'])} files")
    for file in categories["needs_manual_review"][:5]:
        print(f"  ? {file}")

    print("\n✅ SAFE TO ARCHIVE:")
    print(f"  - Test workspace files: {len(categories['test_workspace_files'])}")
    print(f"  - Documentation examples: {len(categories['documentation_examples'])}")
    print(f"  - Duplicate implementations: {len(categories['duplicate_implementations'])}")
    print(f"  - Low value files: {len(categories['truly_safe_to_archive'])}")

    # Generate safe cleanup script
    script = generate_safe_cleanup_script(categories)
    script_path = Path("scripts/safe_cleanup.sh")
    with open(script_path, "w") as f:
        f.write(script)
    script_path.chmod(0o755)

    print(f"\n✅ Safe cleanup script generated: {script_path}")

    # Create review file for manual inspection
    review_path = Path("test_metadata/safe_cleanup_review.txt")
    with open(review_path, "w") as f:
        f.write("LUKHAS AI Safe Cleanup Review\n")
        f.write("=" * 60 + "\n\n")

        f.write("HIGH VALUE FILES - DO NOT DELETE\n")
        f.write("-" * 40 + "\n")
        for file in categories["high_value_keep"]:
            score = next(
                (item["value_score"] for item in audit_report.get("high_value", []) if item.get("file_path") == file),
                "N/A",
            )
            f.write(f"{file} (Score: {score})\n")

        f.write("\n\nFILES NEEDING MANUAL REVIEW\n")
        f.write("-" * 40 + "\n")
        for file in categories["needs_manual_review"][:50]:
            f.write(f"{file}\n")

    print(f"📋 Review file created: {review_path}")

    # Calculate actual safe savings
    safe_count = (
        len(categories["test_workspace_files"])
        + len(categories["documentation_examples"])
        + len(categories["truly_safe_to_archive"])
    )

    print(f"\n💾 Files safe to archive: {safe_count}")
    print(f"🛡️ Files preserved: {len(categories['high_value_keep']) + len(categories['needs_manual_review'])}")


if __name__ == "__main__":
    main()
