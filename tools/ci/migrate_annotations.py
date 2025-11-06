#!/usr/bin/env python3
"""
T4 Annotation Migration Script
Converts legacy TODO[T4-UNUSED-IMPORT] and TODO[T4-LINT-ISSUE] to unified TODO[T4-ISSUE] format.

Features:
- Deduplication (multiple annotations on same line)
- Git blame inference for owner assignment
- Ticket merging (if multiple tickets exist)
- Comprehensive dry-run reporting
- Backup creation (.bak files)

Usage:
  python3 tools/ci/migrate_annotations.py --dry-run
  python3 tools/ci/migrate_annotations.py --apply
  python3 tools/ci/migrate_annotations.py --paths lukhas MATRIZ --apply
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "reports" / "todos"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
MIGRATION_LOG = REPORTS_DIR / "migration_log.jsonl"

# Legacy patterns to detect
LEGACY_UNUSED_IMPORT = re.compile(r"#\s*TODO\[T4-UNUSED-IMPORT\]\s*:\s*(.*)$")
LEGACY_LINT_ISSUE = re.compile(r"#\s*TODO\[T4-LINT-ISSUE\]\s*:\s*(\{.*\})\s*$")
# Already unified (skip these)
UNIFIED_PATTERN = re.compile(r"#\s*TODO\[T4-ISSUE\]\s*:\s*(\{.*\})\s*$")

DEFAULT_PATHS = ["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"]
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_id() -> str:
    return f"t4-{uuid.uuid4().hex[:8]}"


def git_blame_owner(file_path: Path, line_num: int) -> Optional[str]:
    """Use git blame to infer who last touched this line."""
    try:
        result = subprocess.run(
            ["git", "blame", "-L", f"{line_num},{line_num}", "--porcelain", str(file_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # Parse porcelain format for author
            for line in result.stdout.splitlines():
                if line.startswith("author "):
                    author = line[7:].strip()
                    return f"@{author}" if author else None
        return None
    except Exception:
        return None


def infer_code_from_reason(reason: str) -> str:
    """Heuristic: extract lint code from reason text."""
    # Common patterns: "F401 unused import", "kept pending MATRIZ"
    if "F401" in reason or "unused import" in reason.lower():
        return "F401"
    if "F821" in reason or "undefined" in reason.lower():
        return "F821"
    if "B008" in reason:
        return "B008"
    if "B904" in reason:
        return "B904"
    if "SIM102" in reason:
        return "SIM102"
    if "SIM105" in reason:
        return "SIM105"
    # Default for unused imports (most common legacy case)
    return "F401"


def infer_reason_category(code: str, reason: str) -> str:
    """Infer reason_category from code and reason text."""
    reason_lower = reason.lower()

    if "matriz" in reason_lower:
        return "MATRIZ"
    if "constellation" in reason_lower or "trinity" in reason_lower:
        return "CONSTELLATION"
    if "api" in reason_lower:
        return "API"
    if "bio" in reason_lower or "quantum" in reason_lower:
        return "BIO_QUANTUM"
    if "core" in reason_lower or "infra" in reason_lower:
        return "CORE_INFRA"

    # Code-based inference
    if code == "F401":
        return "CORE_INFRA"

    return "OTHER"


def parse_legacy_annotation(line: str, file_path: Path, line_num: int) -> Optional[dict]:
    """Parse legacy annotation and convert to unified format."""

    # Check if already unified (skip)
    if UNIFIED_PATTERN.search(line):
        return None

    # Try legacy unused import pattern
    m_unused = LEGACY_UNUSED_IMPORT.search(line)
    if m_unused:
        reason = m_unused.group(1).strip()
        if not reason:
            reason = "kept for future use (migration from legacy annotation)"

        code = infer_code_from_reason(reason)
        reason_category = infer_reason_category(code, reason)
        owner = git_blame_owner(file_path, line_num)

        return {
            "id": make_id(),
            "code": code,
            "type": "import" if code == "F401" else "lint",
            "reason_category": reason_category,
            "reason": reason,
            "suggestion": None,
            "owner": owner,
            "ticket": None,
            "eta": None,
            "status": "reserved",
            "created_at": iso_now(),
            "legacy_format": "T4-UNUSED-IMPORT",
        }

    # Try legacy lint issue pattern (already JSON)
    m_lint = LEGACY_LINT_ISSUE.search(line)
    if m_lint:
        try:
            old_data = json.loads(m_lint.group(1))
            # Already has most fields, just ensure unified schema
            if not old_data.get("type"):
                old_data["type"] = "lint"
            if not old_data.get("suggestion"):
                old_data["suggestion"] = None
            old_data["legacy_format"] = "T4-LINT-ISSUE"
            return old_data
        except json.JSONDecodeError:
            # Malformed JSON, treat as generic
            return {
                "id": make_id(),
                "code": "UNKNOWN",
                "type": "lint",
                "reason_category": "OTHER",
                "reason": "malformed legacy annotation",
                "suggestion": None,
                "owner": git_blame_owner(file_path, line_num),
                "ticket": None,
                "eta": None,
                "status": "reserved",
                "created_at": iso_now(),
                "legacy_format": "T4-LINT-ISSUE-MALFORMED",
            }

    return None


def convert_line(line: str, file_path: Path, line_num: int) -> tuple[str, bool, Optional[dict]]:
    """
    Convert a line with legacy annotation to unified format.
    Returns: (new_line, was_converted, annotation_dict)
    """
    annotation = parse_legacy_annotation(line, file_path, line_num)

    if not annotation:
        return line, False, None

    # Remove legacy tag and append unified tag
    # Remove old tag first
    line_clean = LEGACY_UNUSED_IMPORT.sub("", line)
    line_clean = LEGACY_LINT_ISSUE.sub("", line_clean)
    line_clean = line_clean.rstrip()

    # Create unified JSON
    json_compact = json.dumps(annotation, separators=(",", ":"), ensure_ascii=False)
    new_line = f"{line_clean}  # TODO[T4-ISSUE]: {json_compact}\n"

    return new_line, True, annotation


def deduplicate_annotations(file_path: Path, dry_run: bool = True) -> tuple[int, list[dict]]:
    """
    Process a file: convert legacy annotations and deduplicate.
    Returns: (num_conversions, list_of_annotations)
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️  Cannot read {file_path}: {e}")
        return 0, []

    lines = content.splitlines(keepends=True)
    new_lines = []
    conversions = 0
    annotations = []

    # Track line numbers for deduplication
    seen_line_nums: dict[int, dict] = {}

    for i, line in enumerate(lines, start=1):
        new_line, converted, annotation = convert_line(line, file_path, i)

        if converted:
            conversions += 1
            annotations.append(annotation)

            # Check for duplicates on same logical line (within 2 lines)
            duplicate_found = False
            for seen_line_num, seen_annot in list(seen_line_nums.items()):
                if abs(seen_line_num - i) <= 2:
                    # Merge: keep newer annotation, merge tickets
                    if seen_annot.get("ticket") and annotation.get("ticket"):
                        annotation["ticket"] = f"{seen_annot['ticket']},{annotation['ticket']}"
                    elif seen_annot.get("ticket"):
                        annotation["ticket"] = seen_annot["ticket"]

                    # Update the annotation
                    json_compact = json.dumps(annotation, separators=(",", ":"), ensure_ascii=False)
                    new_line = line.split("#")[0].rstrip() + f"  # TODO[T4-ISSUE]: {json_compact}\n"

                    duplicate_found = True
                    print(f"  🔀 Deduplicated line {i} with line {seen_line_num}")
                    break

            if not duplicate_found:
                seen_line_nums[i] = annotation

        new_lines.append(new_line)

    if conversions > 0 and not dry_run:
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        file_path.rename(backup_path)

        # Write new content
        file_path.write_text("".join(new_lines), encoding="utf-8")
        print(f"  ✅ Migrated {conversions} annotations (backup: {backup_path.name})")
    elif conversions > 0:
        print(f"  🔍 [DRY-RUN] Would migrate {conversions} annotations")

    return conversions, annotations


def find_python_files(paths: list[str]) -> list[Path]:
    """Find all Python files in given paths, excluding skip directories."""
    result = []

    for path_str in paths:
        path = REPO_ROOT / path_str
        if not path.exists():
            continue

        if path.is_file() and path.suffix == ".py":
            result.append(path)
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                # Check if any parent is in SKIP_DIRS
                if any(skip_dir in py_file.parts for skip_dir in SKIP_DIRS):
                    continue
                result.append(py_file)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Migrate legacy T4 annotations to unified TODO[T4-ISSUE] format"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=DEFAULT_PATHS,
        help="Paths to scan (default: production lanes)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes and create backups")
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORTS_DIR / "migration_report.json",
        help="Path to save migration report",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("⚠️  Must specify --dry-run or --apply")
        sys.exit(1)

    print(f"{'🔍 DRY-RUN MODE' if args.dry_run else '✨ APPLYING CHANGES'}")
    print(f"Scanning paths: {', '.join(args.paths)}")
    print()

    # Find all Python files
    python_files = find_python_files(args.paths)
    print(f"Found {len(python_files)} Python files to scan\n")

    # Process each file
    total_conversions = 0
    all_annotations = []
    files_modified = []

    for py_file in python_files:
        conversions, annotations = deduplicate_annotations(py_file, dry_run=args.dry_run)

        if conversions > 0:
            total_conversions += conversions
            all_annotations.extend(annotations)
            files_modified.append(
                {
                    "file": str(py_file.relative_to(REPO_ROOT)),
                    "conversions": conversions,
                    "annotations": [a["id"] for a in annotations],
                }
            )

            print(f"📝 {py_file.relative_to(REPO_ROOT)}: {conversions} conversions")

    # Generate report
    report = {
        "timestamp": iso_now(),
        "mode": "dry-run" if args.dry_run else "applied",
        "total_files_scanned": len(python_files),
        "files_modified": len(files_modified),
        "total_conversions": total_conversions,
        "files": files_modified,
        "annotations": all_annotations,
    }

    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"{'🔍 MIGRATION DRY-RUN COMPLETE' if args.dry_run else '✅ MIGRATION COMPLETE'}")
    print(f"{'=' * 60}")
    print(f"Files scanned:    {len(python_files)}")
    print(f"Files modified:   {len(files_modified)}")
    print(f"Total conversions: {total_conversions}")
    print(f"Report saved:     {args.report}")
    print()

    if args.dry_run:
        print("💡 Run with --apply to execute migration (backups will be created)")
    else:
        print("✨ Migration complete! Backup files created with .bak extension")
        print("💡 Review changes and commit:")
        print(f"   git add {' '.join(args.paths)}")
        print("   git commit -m 'chore(t4): migrate to unified TODO[T4-ISSUE] format'")

    # Write to migration log
    if not args.dry_run:
        with MIGRATION_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(report, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
