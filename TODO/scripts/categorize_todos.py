#!/usr/bin/env python3
"""
categorize_todos.py - Categorize LUKHAS TODOs by priority
Processes the extracted TODO list and sorts into CRITICAL/HIGH/MED/LOW
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# ΛTAG: todo_scan_constants
_EXCLUDED_DIR_NAMES = {
    ".venv",
    "venv",
    "env",
    ".virtualenv",
    "virtualenv",
    ".conda",
    "conda-env",
    "python-env",
    "site-packages",
    "lib",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".git",
    "build",
    "dist",
    "archive",
    "quarantine",
    "backup",
}

_EXCLUDED_DIR_SUBSTRINGS = {"_venv", "venv-", "-venv", "lib/python"}


logger = logging.getLogger("ΛTRACE.todo.categorize")


@dataclass(frozen=True)
class TodoEntry:
    """Lightweight representation of a TODO match."""

    file_path: Path
    line_number: int
    raw_text: str

    # ΛTAG: todo_entry_format
    def to_output_line(self, project_root: Path) -> str:
        relative_path = self.file_path.relative_to(project_root)
        return f"./{relative_path}:{self.line_number}:{self.raw_text}"


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Locate the project root by walking upward until pyproject.toml or .git is found."""

    # ΛTAG: project_root_discovery
    start = start_path or Path(__file__).resolve()
    if start.is_file():
        current = start.parent
    else:
        current = start

    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").is_dir():
            return parent

    return current


def _is_path_excluded(path: Path) -> bool:
    """Check whether a file lives inside a directory that should be excluded."""

    # ΛTAG: todo_scan_filter
    parts = path.parts[:-1]  # Only inspect directory segments
    for part in parts:
        if part in _EXCLUDED_DIR_NAMES:
            return True
        if any(token in part for token in _EXCLUDED_DIR_SUBSTRINGS):
            return True

    joined = "/".join(parts)
    return any(token in joined for token in _EXCLUDED_DIR_SUBSTRINGS)


def _iter_python_files(project_root: Path) -> Iterable[Path]:
    """Yield Python files within the repository excluding virtual environments and build artifacts."""

    for path in project_root.rglob("*.py"):
        if _is_path_excluded(path):
            continue
        yield path


def _scan_file_for_todos(py_file: Path) -> Iterable[TodoEntry]:
    """Scan a Python file for TODO markers and yield entries."""

    try:
        with py_file.open("r", encoding="utf-8", errors="ignore") as handle:
            for index, raw_line in enumerate(handle, start=1):
                if "TODO" not in raw_line:
                    continue
                if "# noqa" in raw_line and "TODO" in raw_line:
                    # ΛTAG: todo_scan_skip_noqa
                    continue
                yield TodoEntry(py_file, index, raw_line.rstrip())
    except OSError as exc:  # pragma: no cover - guarded but we log for observability
        logger.debug("Skipping file due to read error", extra={"file": str(py_file), "error": str(exc)})


def load_exclusions(project_root: Optional[Path] = None) -> List[str]:
    """Load standardized exclusions and get clean TODO list."""

    root = find_project_root(project_root)

    entries: List[TodoEntry] = []
    for py_file in _iter_python_files(root):
        entries.extend(_scan_file_for_todos(py_file))

    # Sort deterministically by file path then line number for reproducible output
    # ΛTAG: todo_scan_sort
    entries.sort(key=lambda entry: (str(entry.file_path.relative_to(root)), entry.line_number))

    return [entry.to_output_line(root) for entry in entries]


def classify_priority(todo_line, file_path, context=""):
    """Classify TODO priority based on content and location"""
    todo_lower = todo_line.lower()
    file_lower = file_path.lower()

    # CRITICAL: Security, safety, blocking issues
    critical_keywords = [
        "security",
        "vulnerability",
        "critical",
        "urgent",
        "blocking",
        "corrupted",
        "failed",
        "broken",
        "error",
        "exception",
        "crash",
        "deadlock",
        "race condition",
        "data loss",
        "memory leak",
        "infinite loop",
        "guardian",
        "safety",
    ]

    critical_modules = [
        "security",
        "identity",
        "auth",
        "guardian",
        "consciousness/core",
        "api/auth",
        "crypto",
        "validation",
    ]

    # HIGH: Core functionality, Trinity Framework, agent coordination
    high_keywords = [
        "core",
        "important",
        "trinity",
        "consciousness",
        "identity",
        "memory",
        "integration",
        "api",
        "performance",
        "optimize",
        "agent",
        "coordinator",
        "essential",
        "required",
        "needed",
        "framework",
        "architecture",
    ]

    high_modules = [
        "core/",
        "api/",
        "consciousness/",
        "identity/",
        "memory/",
        "lukhas/",
        "orchestration/",
        "coordination",
    ]

    # MED: Features, enhancements, documentation
    med_keywords = [
        "enhance",
        "improve",
        "feature",
        "document",
        "refactor",
        "cleanup",
        "optimize",
        "better",
        "upgrade",
        "modernize",
        "extend",
    ]

    # LOW: Minor cleanup, style, nice-to-have
    low_keywords = [
        "style",
        "cosmetic",
        "minor",
        "cleanup",
        "format",
        "comment",
        "nice to have",
        "optional",
        "later",
        "future",
        "consider",
    ]

    # Check for T4 annotations (these are often important)
    if "t4-" in todo_lower or "[t4" in todo_lower:
        if any(kw in todo_lower for kw in critical_keywords):
            return "CRITICAL"
        elif "unused-import" in todo_lower or "document or remove" in todo_lower:
            return "MED"  # Import cleanup is medium priority
        else:
            return "HIGH"  # T4 framework items are generally high priority

    # Check for specialist assignments (agent coordination)
    if "specialist]" in todo_lower or "agent]" in todo_lower:
        return "HIGH"

    # Critical checks
    if any(kw in todo_lower for kw in critical_keywords):
        return "CRITICAL"

    if any(module in file_lower for module in critical_modules):
        return "CRITICAL"

    # High priority checks
    if any(kw in todo_lower for kw in high_keywords):
        return "HIGH"

    if any(module in file_lower for module in high_modules):
        return "HIGH"

    # Medium priority checks
    if any(kw in todo_lower for kw in med_keywords):
        return "MED"

    # Low priority checks
    if any(kw in todo_lower for kw in low_keywords):
        return "LOW"

    # Default based on module location
    if "candidate/" in file_lower:
        return "MED"  # Candidate modules are generally medium priority
    elif "tools/" in file_lower or "tests/" in file_lower:
        return "LOW"  # Tools and tests are generally lower priority
    elif "products/" in file_lower:
        return "HIGH"  # Products are user-facing, higher priority
    else:
        return "MED"  # Default to medium


def extract_todo_context(line):
    """Extract TODO text and context from grep line"""
    # Format: ./path/file.py:line_number:content
    parts = line.split(":", 2)
    if len(parts) < 3:
        return "", "", ""

    file_path = parts[0]
    line_num = parts[1]
    content = parts[2]

    # Extract just the TODO part
    todo_match = re.search(r"TODO[^:]*:?\s*(.+)", content, re.IGNORECASE)
    todo_text = todo_match.group(1).strip() if todo_match else content.strip()

    return file_path, line_num, todo_text


def categorize_todos():
    """Main function to categorize all TODOs"""
    print("🔍 Loading TODOs with clean search...")
    todo_lines = load_exclusions()

    if not todo_lines or (len(todo_lines) == 1 and not todo_lines[0]):
        print("❌ No TODOs found!")
        return

    print(f"📊 Processing {len(todo_lines)} TODO entries...")

    categories = {"CRITICAL": [], "HIGH": [], "MED": [], "LOW": []}

    for line in todo_lines:
        if not line.strip():
            continue

        file_path, line_num, todo_text = extract_todo_context(line)
        if not todo_text:
            continue

        priority = classify_priority(todo_text, file_path)

        categories[priority].append({"file": file_path, "line": line_num, "text": todo_text, "full_line": line})

    # Summary
    total = sum(len(todos) for todos in categories.values())
    print(f"\n📋 TODO Categorization Results:")
    print(f"  🚨 CRITICAL: {len(categories['CRITICAL'])}")
    print(f"  ⭐ HIGH: {len(categories['HIGH'])}")
    print(f"  📋 MED: {len(categories['MED'])}")
    print(f"  🔧 LOW: {len(categories['LOW'])}")
    print(f"  📊 TOTAL: {total}")

    return categories


def generate_priority_files(categories: Dict[str, List[Dict[str, str]]], output_base: Optional[Path] = None) -> List[Path]:
    """Generate markdown files for each priority level."""

    project_root = find_project_root(output_base)
    base_path = (output_base or (project_root / "TODO")).resolve()
    base_path.mkdir(parents=True, exist_ok=True)

    priority_info = {
        "CRITICAL": {"emoji": "🚨", "description": "Security, consciousness safety, blocking issues"},
        "HIGH": {"emoji": "⭐", "description": "Core functionality, Trinity Framework, agent coordination"},
        "MED": {"emoji": "📋", "description": "Feature enhancements, optimization, documentation"},
        "LOW": {"emoji": "🔧", "description": "Cleanup, refactoring, nice-to-have features"},
    }

    generated_files: List[Path] = []

    for priority, todos in categories.items():
        if not todos:
            continue

        info = priority_info[priority]
        filename = f"{priority.lower()}_todos.md"
        priority_dir = base_path / priority
        priority_dir.mkdir(parents=True, exist_ok=True)
        filepath = priority_dir / filename

        # Group by module for better organization
        by_module = defaultdict(list)
        for todo in todos:
            module = todo["file"].split("/")[1] if "/" in todo["file"] else "root"
            by_module[module].append(todo)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {info['emoji']} {priority} Priority TODOs\n\n")
            f.write(f"**{info['description']}**\n\n")
            f.write(f"**Count**: {len(todos)} TODOs\n")
            f.write(f"**Last Updated**: September 12, 2025\n\n")

            f.write("## 📊 Summary by Module\n\n")
            for module in sorted(by_module.keys()):
                f.write(f"- **{module}**: {len(by_module[module])} TODOs\n")

            f.write("\n---\n\n")

            for module in sorted(by_module.keys()):
                module_todos = by_module[module]
                f.write(f"## 📁 {module.title()} Module ({len(module_todos)} TODOs)\n\n")

                for i, todo in enumerate(module_todos, 1):
                    f.write(f"### {i}. {todo['text'][:80]}{'...' if len(todo['text']) > 80 else ''}\n\n")
                    f.write(f"- **File**: `{todo['file']}:{todo['line']}`\n")
                    f.write(f"- **Priority**: {priority}\n")
                    f.write(f"- **Status**: Open\n")

                    # Determine Trinity aspect
                    text_lower = todo["text"].lower()
                    if any(word in text_lower for word in ["identity", "auth", "id"]):
                        f.write(f"- **Trinity Aspect**: ⚛️ Identity\n")
                    elif any(word in text_lower for word in ["consciousness", "memory", "cognitive"]):
                        f.write(f"- **Trinity Aspect**: 🧠 Consciousness\n")
                    elif any(word in text_lower for word in ["security", "guardian", "safety"]):
                        f.write(f"- **Trinity Aspect**: 🛡️ Guardian\n")

                    f.write(f"\n**TODO Text:**\n```\n{todo['text']}\n```\n\n")
                    f.write("---\n\n")

        print(f"✅ Generated {filepath}")

        # ΛTAG: todo_legacy_mirror
        legacy_path = base_path / f"{priority.lower()}_todos.md"
        legacy_path.write_text(filepath.read_text(encoding="utf-8"), encoding="utf-8")
        generated_files.extend([filepath, legacy_path])

    return generated_files


if __name__ == "__main__":
    print("🎯 LUKHAS TODO Categorization System")
    print("=" * 50)

    categories = categorize_todos()
    if categories:
        print("\n📝 Generating priority files...")
        generated = generate_priority_files(categories)
        print("\n✅ TODO categorization complete!")
        print("📂 Generated files:")
        for path in generated:
            print(f"   • {path}")
    else:
        print("❌ No TODOs to categorize")
