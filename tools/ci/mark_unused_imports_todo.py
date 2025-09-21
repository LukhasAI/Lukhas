#!/usr/bin/env python3
"""
🎯 T4 UNUSED IMPORTS ANNOTATOR - Production Lane Focus

Mark unused imports with TODOs instead of deleting them.

- Runs ruff F401 to find unused imports in selected roots (--paths)
- Adds inline marker: # TODO[T4-UNUSED-IMPORT]: <reason>
- Adds a file header the first time a file is annotated
- Skips already-annotated lines and waived files/lines
- Emits JSONL log to reports/todos/unused_imports.jsonl
- Default paths: lukhas core api consciousness memory identity MATRIZ (production lanes only)
- Always skips: .git, .venv, node_modules, archive, quarantine, candidate

⚛️ LUKHAS AI Constellation Framework Integration:
- 🧠 Consciousness: Preserves developer intent and future planning
- ⚛️ Identity: Maintains module identity while documenting purpose
- 🛡️ Guardian: Protects against accidental deletion of future-needed imports

Usage:
    python3 tools/ci/mark_unused_imports_todo.py                    # Default: all production dirs
    python3 tools/ci/mark_unused_imports_todo.py --paths lukhas     # Only lukhas/
    python3 tools/ci/mark_unused_imports_todo.py --paths ops tools  # Custom paths
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Repository structure
REPO = Path(__file__).resolve().parents[2]
REPORTS = REPO / "reports" / "todos"
REPORTS.mkdir(parents=True, exist_ok=True)
LOG = REPORTS / "unused_imports.jsonl"
WAIVERS = REPO / "AUDIT" / "waivers" / "unused_imports.yaml"

# Production vs Experimental separation
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "reports"}
# Note: candidate is excluded by default but can be explicitly included via --paths

# T4 TODO system configuration
HEADER_BLOCK = (
    "# ---\n"
    "# TODO[T4-UNUSED-IMPORT]: This file contains unused imports intentionally kept.\n"
    "# Each import below is preserved for documented future use or MATRIZ integration.\n"
    "# Update reasons or remove imports when implemented.\n"
    "# ---\n\n"
)

TODO_TAG = "TODO[T4-UNUSED-IMPORT]"
INLINE_PATTERN = re.compile(rf"#\s*{re.escape(TODO_TAG)}")
IMPORT_LINE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")


def load_waivers():
    """Load waiver configuration for intentional unused imports."""
    try:
        import yaml  # type: ignore

        if not WAIVERS.exists():
            return {}
        data = yaml.safe_load(WAIVERS.read_text()) or {}
        result = {}
        for waiver in data.get("waivers", []):
            file_path = (REPO / waiver["file"]).resolve()
            line_num = int(waiver.get("line", 0))  # 0 = entire file
            result.setdefault(str(file_path), set()).add(line_num)
        return result
    except Exception:
        return {}


def ruff_F401(paths):
    """Run ruff F401 on the selected paths; return list[(abs_path, line, message)]."""
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json"] + list(paths)

    try:
        result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)

        if result.returncode not in (0, 1):  # 0 = clean, 1 = findings
            print(f"❌ ruff error: {result.stderr or result.stdout}", file=sys.stderr)
            sys.exit(result.returncode)

        items = json.loads(result.stdout or "[]")

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"❌ Failed to run ruff or parse output: {e}", file=sys.stderr)
        return []

    findings = []
    for item in items:
        file_path = (REPO / item["filename"]).resolve()

        # Skip if any path segment is in SKIP_DIRS
        path_parts = set(Path(file_path).parts)
        if path_parts & SKIP_DIRS:
            continue

        findings.append((str(file_path), item["location"]["row"], item["message"]))

    return findings


def ensure_header(text: str) -> str:
    """Add T4 header if no prior TODO tag present."""
    return text if TODO_TAG in text else (HEADER_BLOCK + text)


def mark_line(text: str, line_no: int, reason: str):
    """Mark a specific line with T4 TODO annotation."""
    lines = text.splitlines()
    idx = line_no - 1

    # Validate line exists and is an import
    if idx < 0 or idx >= len(lines):
        return text, False

    line = lines[idx]

    # Skip if already annotated
    if INLINE_PATTERN.search(line):
        return text, False

    # Skip if not an import line
    if not IMPORT_LINE.match(line.strip()):
        return text, False

    # Add TODO annotation
    lines[idx] = f"{line}  # {TODO_TAG}: {reason}"

    # Preserve original line endings
    new_text = "\n".join(lines)
    if text.endswith("\n") and not new_text.endswith("\n"):
        new_text += "\n"

    return new_text, True


def determine_smart_reason(file_path: str, line_content: str, message: str) -> str:
    """Determine contextually appropriate reason for keeping unused import."""
    file_path_lower = file_path.lower()
    line_lower = line_content.lower()

    # MATRIZ-related imports
    if "matriz" in line_lower or "trace" in line_lower:
        return "kept for MATRIZ-R2 trace integration"

    # Agent/AI orchestration
    if "agent" in line_lower or "orchestrat" in line_lower:
        return "kept for multi-AI agent coordination"

    # Consciousness/Constellation Framework
    if any(word in line_lower for word in ["consciousness", "constellation", "guardian", "identity"]):
        return "kept for Constellation Framework consciousness evolution"

    # API/Interface definitions
    if "api" in file_path_lower or "interface" in line_lower:
        return "kept for API expansion (document or implement)"

    # Core infrastructure
    if "core" in file_path_lower:
        return "kept for core infrastructure (review and implement)"

    # Bio/Quantum systems
    if any(word in line_lower for word in ["bio", "quantum", "symbolic"]):
        return "kept for bio-inspired/quantum systems development"

    # Default for production lanes
    return "kept pending MATRIZ wiring (document or remove)"


def main():
    """Main T4 unused imports annotator with production lane focus."""
    parser = argparse.ArgumentParser(
        description="T4 Unused Imports Annotator - Production Lane Focus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/ci/mark_unused_imports_todo.py                    # Default: all production dirs
  python3 tools/ci/mark_unused_imports_todo.py --paths lukhas     # Only lukhas/
  python3 tools/ci/mark_unused_imports_todo.py --paths ops tools  # Custom paths
        """,
    )

    parser.add_argument(
        "--paths",
        nargs="+",
        default=["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"],
        help="Roots to scan (default: lukhas core api consciousness memory identity MATRIZ). Use --paths candidate for experimental code.",
    )
    parser.add_argument("--reason", default=None, help="Override reason text (default: smart contextual reasons)")

    args = parser.parse_args()

    print("🎯 T4 UNUSED IMPORTS ANNOTATOR - Production Lane Focus")
    print("=" * 60)
    print("⚛️ Transforming technical debt into documented intent")

    # Resolve and filter paths that actually exist; skip disallowed roots up-front
    valid_roots = []
    for path_arg in args.paths:
        if path_arg.strip() in SKIP_DIRS:
            print(f"⚪ Skipping excluded path: {path_arg}")
            continue

        abs_path = (REPO / path_arg).resolve()
        if abs_path.exists():
            rel_path = str(abs_path.relative_to(REPO))
            valid_roots.append(rel_path)
        else:
            print(f"⚠️  Path does not exist: {path_arg}")

    if not valid_roots:
        print("❌ No valid roots to scan. Exiting.")
        sys.exit(0)

    print(f"📁 Scanning paths: {', '.join(valid_roots)}")

    # Load configuration
    waivers = load_waivers()
    if waivers:
        print(f"📋 Loaded {len(waivers)} waiver files")

    # Get F401 findings
    findings = ruff_F401(valid_roots)
    print(f"📊 Found {len(findings)} unused imports in production lanes")

    if not findings:
        print("✅ No unused imports found in production lanes!")
        return

    # Process findings
    edits = 0
    skipped_waived = 0
    skipped_annotated = 0

    # Prepare log file for append operations
    LOG.touch(exist_ok=True)
    existing_log = LOG.read_text(encoding="utf-8", errors="ignore")

    for file_path, line_no, message in findings:
        # Check waivers
        if file_path in waivers:
            waiver_lines = waivers[file_path]
            if 0 in waiver_lines or line_no in waiver_lines:
                skipped_waived += 1
                continue

        # Read file and process
        try:
            file_obj = Path(file_path)
            original_text = file_obj.read_text(encoding="utf-8", errors="ignore")

            # Get the import line for context
            lines = original_text.splitlines()
            line_content = lines[line_no - 1] if line_no <= len(lines) else ""

            # Determine reason
            reason = args.reason or determine_smart_reason(file_path, line_content, message)

            # Apply annotation
            new_text, changed = mark_line(original_text, line_no, reason)

            if not changed:
                skipped_annotated += 1
                continue

            # Ensure header (first time)
            new_text = ensure_header(new_text)

            # Apply changes
            file_obj.write_text(new_text, encoding="utf-8")

            # Log the edit
            log_entry = {
                "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
                "file": str(file_obj.relative_to(REPO)),
                "line": line_no,
                "reason": reason,
                "message": message,
                "tool": "T4-unused-imports-annotator",
            }
            existing_log += json.dumps(log_entry) + "\n"

            rel_path = file_obj.relative_to(REPO)
            print(f"✅ Annotated: {rel_path}:{line_no} - {reason}")
            edits += 1

        except Exception as e:
            rel_path = Path(file_path).relative_to(REPO)
            print(f"❌ Error processing {rel_path}:{line_no}: {e}")

    # Update log file
    LOG.write_text(existing_log, encoding="utf-8")

    # Summary
    print(f"\n📈 PRODUCTION LANE SUMMARY:")
    print(f"✅ Annotated: {edits} unused imports")
    print(f"⚪ Skipped (waived): {skipped_waived}")
    print(f"⚪ Skipped (already annotated): {skipped_annotated}")

    if edits > 0:
        print(f"📝 Log: {LOG}")
        print(f"\n🎯 Next steps:")
        print(f"1. Review annotated imports and update reasons as needed")
        print(f"2. Implement or remove imports when their purpose is fulfilled")
        print(f"3. Run 'make todo-unused-check' to validate annotations")


if __name__ == "__main__":
    main()
