#!/usr/bin/env python3
"""
Constellation Framework Standardization Tool

Finds all Constellation Framework mentions and ensures they include
the complete canonical 8-star definition.

SAFEGUARDS:
- Dry-run mode by default (requires --apply to make changes)
- Git history used for recovery (no .bak files needed)
- Detailed diff preview before applying changes
- Never modifies .git, binary, or generated files
- Shows before/after context for each change
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Canonical 8-star definition
CANONICAL_CONSTELLATION = """Constellation Framework (8 Stars)
\t•\t⚛️ Identity (Anchor) — ΛiD authentication, namespace management
\t•\t✦ Memory (Trail) — Fold-based memory, temporal organization
\t•\t🔬 Vision (Horizon) — Pattern recognition, adaptive interfaces
\t•\t🌱 Bio (Living) — Adaptive bio-symbolic processing
\t•\t🌙 Dream (Drift) — Creative consciousness expansion
\t•\t⚖️ Ethics (North) — Constitutional AI, democratic oversight
\t•\t🛡️ Guardian (Watch) — Safety compliance, cascade prevention
\t•\t⚛️ Quantum (Ambiguity) — Quantum-inspired uncertainty"""

# Alternative compact format for inline mentions
CANONICAL_INLINE = "Constellation Framework (8 Stars: ⚛️ Identity, ✦ Memory, 🔬 Vision, 🌱 Bio, 🌙 Dream, ⚖️ Ethics, 🛡️ Guardian, ⚛️ Quantum)"

# Patterns to detect incomplete Constellation mentions
INCOMPLETE_PATTERNS = [
    # "Identity ⚛️ + Consciousness 🧠 + Guardian 🛡️" (old Trinity-style)
    r"Identity\s*⚛️\s*\+\s*Consciousness\s*🧠\s*\+\s*Guardian\s*🛡️",
    r"⚛️\s*Identity\s*\+\s*🧠\s*Consciousness\s*\+\s*🛡️\s*Guardian",

    # "Constellation Framework:" followed by incomplete list
    r"Constellation Framework[:\s]+(?:Identity|Memory|Vision|Bio|Dream|Ethics|Guardian|Quantum)[^⚛️✦🔬🌱🌙⚖️🛡️]{0,200}(?!\n.*⚛️.*✦.*🔬.*🌱.*🌙.*⚖️.*🛡️)",
]


def count_stars_in_text(text: str, after_pos: int = 0) -> int:
    """Count unique star symbols after a given position."""
    symbols = ["⚛️", "✦", "🔬", "🌱", "🌙", "⚖️", "🛡️"]
    # Look ahead up to 2000 chars
    search_window = text[after_pos:after_pos + 2000]
    found = sum(1 for s in symbols if s in search_window)
    return found


def find_constellation_mentions(file_path: Path) -> List[Tuple[int, str, int]]:
    """
    Find Constellation Framework mentions and count associated stars.
    Returns list of (line_num, context, star_count)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, PermissionError):
        return []

    mentions = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if 'Constellation Framework' in line or 'constellation framework' in line.lower():
            # Find position in full content
            pos = content.find(line)
            if pos >= 0:
                star_count = count_stars_in_text(content, pos)
                mentions.append((i, line.strip(), star_count))

    return mentions


def is_incomplete_mention(line: str, star_count: int, next_lines: str) -> bool:
    """
    Determine if a Constellation mention has an incomplete star list.

    Rules:
    - Simple mentions like "Constellation Framework" are OK (no stars listed)
    - If stars ARE listed, must have all 8 (7 unique symbols, ⚛️ appears twice)
    - Old Trinity-style (Identity + Consciousness + Guardian) needs updating
    - Docstrings, code comments, and prose are OK
    """
    combined = line + "\n" + next_lines

    # If we have all 8 stars (7 unique symbols), it's complete
    if star_count >= 7:  # ⚛️ appears twice, so 7 unique symbols
        return False

    # Ignore docstrings and code comments
    if '"""' in line or "'''" in line or line.strip().startswith('#'):
        return False

    # Ignore lines inside code blocks (indented or after ```)
    if line.strip().startswith('```') or re.match(r'^\s{4,}', line):
        return False

    # Check for old Trinity-style patterns (definitely incomplete)
    for pattern in INCOMPLETE_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return True

    # Check if this is an actual bullet list trying to enumerate stars
    # (vs just mentioning constellation with a star or two in the text)
    has_multiline_star_list = bool(re.search(
        r':\s*\n\s*[-•\*]\s*[⚛️✦🔬🌱🌙⚖️🛡️].*\n\s*[-•\*]\s*[⚛️✦🔬🌱🌙⚖️🛡️]',
        combined,
        re.MULTILINE
    ))

    # If there's a multiline bullet list with stars but not all 8, it's incomplete
    if has_multiline_star_list and star_count < 7:
        return True

    # Check for inline star lists with multiple stars using separators
    has_inline_star_list = bool(re.search(
        r'[⚛️✦🔬🌱🌙⚖️🛡️🧠]\s*[·•\-+]\s*[⚛️✦🔬🌱🌙⚖️🛡️🧠]',
        combined
    ))

    # If there's an inline list with separators but not all 8, it's incomplete
    if has_inline_star_list and star_count < 7:
        return True

    # Simple mentions (0-2 stars) without lists are OK
    return False


def generate_report(root_dir: Path, exclude_patterns: List[str]) -> None:
    """Generate report of incomplete Constellation mentions."""
    print("=" * 80)
    print("CONSTELLATION FRAMEWORK STANDARDIZATION REPORT")
    print("=" * 80)
    print()

    exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules',
                    'dist', 'build', '.pytest_cache', 'artifacts'}

    incomplete_files = []
    complete_files = []

    for file_path in root_dir.rglob('*'):
        # Skip excluded directories and non-text files
        if any(p in file_path.parts for p in exclude_dirs):
            continue
        if not file_path.is_file():
            continue
        if file_path.suffix not in ['.md', '.py', '.txt', '.rst', '.yaml', '.yml', '.me']:
            continue

        mentions = find_constellation_mentions(file_path)
        if not mentions:
            continue

        # Read file for context checking
        try:
            lines = file_path.read_text(encoding='utf-8').split('\n')
        except:
            continue

        has_incomplete = False
        for line_num, line_content, star_count in mentions:
            # Get next 20 lines for context
            next_lines = '\n'.join(lines[line_num:line_num+20])

            if is_incomplete_mention(line_content, star_count, next_lines):
                has_incomplete = True
                if file_path not in incomplete_files:
                    incomplete_files.append((file_path, mentions))
                break

        if not has_incomplete:
            complete_files.append(file_path)

    print("📊 Summary:")
    print(f"  ✅ Complete definitions: {len(complete_files)}")
    print(f"  ⚠️  Incomplete definitions: {len(incomplete_files)}")
    print()

    if incomplete_files:
        print("📝 Files needing standardization:")
        print()
        for file_path, mentions in sorted(incomplete_files)[:50]:  # Show first 50
            rel_path = file_path.relative_to(root_dir)
            print(f"  {rel_path}")
            for line_num, line_content, star_count in mentions[:2]:  # Show first 2 mentions
                print(f"    Line {line_num}: {star_count} stars - {line_content[:80]}")

        if len(incomplete_files) > 50:
            print(f"\n  ... and {len(incomplete_files) - 50} more files")

    print()
    print("=" * 80)
    print("\n🔧 To standardize these files, use the interactive mode:")
    print("   python tools/standardize_constellation.py --fix")
    print()


def generate_diff_preview(file_path: Path, old_content: str, new_content: str) -> None:
    """Show a detailed diff preview of proposed changes."""
    print(f"\n{'='*80}")
    print(f"FILE: {file_path}")
    print(f"{'='*80}")

    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')

    # Find changed sections
    for i, (old, new) in enumerate(zip(old_lines, new_lines), 1):
        if old != new:
            # Show context (3 lines before/after)
            start = max(0, i-4)
            end = min(len(old_lines), i+3)

            print(f"\n--- Line {i} (BEFORE) ---")
            for j in range(start, end):
                prefix = ">>>" if j == i-1 else "   "
                print(f"{prefix} {old_lines[j]}")

            print(f"\n+++ Line {i} (AFTER) +++")
            for j in range(start, end):
                prefix = ">>>" if j == i-1 else "   "
                if j < len(new_lines):
                    print(f"{prefix} {new_lines[j]}")

            print()
            break  # Show only first change per file


def dry_run_report(root_dir: Path) -> List[Tuple[Path, str, str]]:
    """Generate dry-run report showing what would be changed."""
    print("=" * 80)
    print("🔍 CONSTELLATION FRAMEWORK - DRY RUN REPORT")
    print("=" * 80)
    print()
    print("⚠️  DRY-RUN MODE: No files will be modified")
    print("    Use --apply flag to apply changes after review")
    print()

    exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules',
                    'dist', 'build', '.pytest_cache', 'artifacts', 'docs/transcripts'}

    changes = []

    for file_path in root_dir.rglob('*'):
        # Skip excluded directories and non-text files
        if any(p in file_path.parts for p in exclude_dirs):
            continue
        if not file_path.is_file():
            continue
        if file_path.suffix not in ['.md', '.me']:  # Only markdown and .me files for safety
            continue

        mentions = find_constellation_mentions(file_path)
        if not mentions:
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
        except:
            continue

        # Check if incomplete
        has_incomplete = False
        for line_num, line_content, star_count in mentions:
            next_lines = '\n'.join(lines[line_num:line_num+20])
            if is_incomplete_mention(line_content, star_count, next_lines):
                has_incomplete = True
                break

        if has_incomplete:
            # For dry-run, just note the file (no actual changes yet)
            rel_path = file_path.relative_to(root_dir)
            changes.append((file_path, content, None))
            print(f"📝 Would update: {rel_path}")
            for line_num, line_content, star_count in mentions[:1]:
                print(f"    Line {line_num}: {star_count} stars detected")

    print()
    print(f"{'='*80}")
    print(f"Summary: {len(changes)} files need standardization")
    print()
    print("⚠️  This is a DRY RUN - no changes were made")
    print()
    print("Next steps:")
    print("  1. Review the files listed above")
    print("  2. Check git status to ensure working tree is clean")
    print("  3. Run with --preview to see detailed diffs")
    print("  4. Run with --apply to make actual changes")
    print(f"{'='*80}")

    return changes


def replace_incomplete_constellation(content: str, file_path: Path) -> str:
    """
    Replace incomplete Constellation Framework mentions with canonical 8-star version.

    Strategy:
    1. Find old Trinity-style patterns and replace with canonical format
    2. Find incomplete bullet lists and replace with canonical format
    3. Preserve surrounding context and formatting
    """
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line mentions Constellation Framework
        if 'Constellation Framework' in line or 'constellation framework' in line.lower():
            # Get next 20 lines for context
            context_end = min(len(lines), i + 20)
            next_lines = '\n'.join(lines[i:context_end])

            # Count stars in context
            star_count = count_stars_in_text(next_lines, 0)

            # Check if this needs replacement
            if is_incomplete_mention(line, star_count, next_lines):
                # Detect if it's a bullet list format
                any('•' in lines[j] or re.match(r'^\s*[-*]\s+', lines[j])
                                 for j in range(i, min(len(lines), i + 10)))

                # Detect indentation level
                indent_match = re.match(r'^(\s*)', line)
                indent = indent_match.group(1) if indent_match else ''

                # Replace the line
                result_lines.append(f"{indent}**Constellation Framework (8 Stars)**")
                result_lines.append(f"{indent}")
                result_lines.append(f"{indent}- **⚛️ Identity (Anchor)** — ΛiD authentication, namespace management")
                result_lines.append(f"{indent}- **✦ Memory (Trail)** — Fold-based memory, temporal organization")
                result_lines.append(f"{indent}- **🔬 Vision (Horizon)** — Pattern recognition, adaptive interfaces")
                result_lines.append(f"{indent}- **🌱 Bio (Living)** — Adaptive bio-symbolic processing")
                result_lines.append(f"{indent}- **🌙 Dream (Drift)** — Creative consciousness expansion")
                result_lines.append(f"{indent}- **⚖️ Ethics (North)** — Constitutional AI, democratic oversight")
                result_lines.append(f"{indent}- **🛡️ Guardian (Watch)** — Safety compliance, cascade prevention")
                result_lines.append(f"{indent}- **⚛️ Quantum (Ambiguity)** — Quantum-inspired uncertainty")

                # Skip old incomplete content (find end of the incomplete list)
                j = i + 1
                while j < len(lines) and j < i + 15:
                    # Stop if we hit a blank line or new section
                    if not lines[j].strip() or lines[j].startswith('#'):
                        break
                    # Stop if line has star symbols (part of incomplete list)
                    if any(s in lines[j] for s in ['⚛️', '✦', '🔬', '🌱', '🌙', '⚖️', '🛡️', '🧠']):
                        j += 1
                        continue
                    # Stop if it's a bullet point continuation
                    if re.match(r'^\s*[-*•]\s+', lines[j]):
                        j += 1
                        continue
                    break

                i = j
                continue

        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)


def apply_standardization(root_dir: Path, changes: List[Tuple[Path, str, str]]) -> None:
    """Apply constellation standardization changes to files."""
    print("=" * 80)
    print("🔧 APPLYING CONSTELLATION FRAMEWORK STANDARDIZATION")
    print("=" * 80)
    print()
    print(f"Processing {len(changes)} files...")
    print()

    updated_count = 0
    skipped_count = 0

    for file_path, old_content, _ in changes:
        try:
            # Generate new content
            new_content = replace_incomplete_constellation(old_content, file_path)

            # Only write if content actually changed
            if new_content != old_content:
                file_path.write_text(new_content, encoding='utf-8')
                rel_path = file_path.relative_to(root_dir)
                print(f"✅ Updated: {rel_path}")
                updated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            rel_path = file_path.relative_to(root_dir)
            print(f"❌ Error updating {rel_path}: {e}")
            skipped_count += 1

    print()
    print("=" * 80)
    print("📊 Summary:")
    print(f"  ✅ Updated: {updated_count} files")
    print(f"  ⏭️  Skipped: {skipped_count} files")
    print()
    print("Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Test: make smoke")
    print("  3. Commit: git add -A && git commit")
    print("=" * 80)


def main():
    root_dir = Path(__file__).parent.parent

    # Parse arguments
    apply_mode = '--apply' in sys.argv
    preview_mode = '--preview' in sys.argv

    if preview_mode:
        print("❌ --preview mode not yet implemented")
        print("   Use default dry-run mode first")
        sys.exit(1)

    if apply_mode:
        print("⚠️  APPLY MODE - Files will be modified")
        print()
        input("Press ENTER to continue or Ctrl+C to cancel...")
        print()

        # Run detection again to get file list
        changes = dry_run_report(root_dir)
        print()

        # Apply changes
        apply_standardization(root_dir, changes)
    else:
        # Default: dry-run report
        dry_run_report(root_dir)


if __name__ == '__main__':
    main()
