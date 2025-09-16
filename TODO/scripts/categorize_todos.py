#!/usr/bin/env python3
"""Categorize repository TODO markers into priority buckets."""

from __future__ import annotations

import logging
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

# Repository configuration
REPO_ROOT = Path(__file__).resolve().parents[2]

# ΛTAG: todo_scan_exclusions
EXCLUDE_TOKENS = (".venv/", "venv/", "__pycache__/", ".git/", "node_modules/", "dist/", "build/")
PRIORITIES = ("CRITICAL", "HIGH", "MED", "LOW")

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
class TODORecord:
    """Structured representation of a TODO entry discovered in the repository."""

    file: str
    line: str
    text: str
    priority: str
    raw: str

    @property
    def module(self) -> str:
        """Return the top-level module for grouping."""
        # ΛTAG: todo_module_detection
        parts = [part for part in Path(self.file).parts if part not in {".", ""}]
        return parts[0] if parts else "root"


@dataclass(frozen=True)
class TodoEntry:
    """Lightweight representation of a TODO match for internal processing."""

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


def load_exclusions(repo_path: Optional[Path] = None) -> list[str]:
    """Load TODO entries using ripgrep with fallback to Python scanner."""
    repo = Path(repo_path or REPO_ROOT)

    # Try ripgrep first
    command = [
        "rg",
        "--no-heading",
        "--with-filename",
        "--line-number",
        "TODO|FIXME|HACK",
        "--type",
        "py",
    ]

    try:
        result = subprocess.run(command, cwd=repo, capture_output=True, text=True, check=False)
        if result.returncode in {0, 1}:  # 0=matches, 1=no matches
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return [line for line in lines if not _contains_excluded_token(line)]
    except FileNotFoundError:
        pass  # Fall through to Python scanner

    # Fallback to Python scanner using more comprehensive exclusion logic
    return _scan_python_files_comprehensive(repo)


def _scan_python_files_comprehensive(repo: Path) -> list[str]:
    """Comprehensive Python scanner using enhanced exclusion logic."""
    # ΛTAG: todo_scan_fallback
    root = find_project_root(repo)
    entries: List[TodoEntry] = []

    for py_file in _iter_python_files(root):
        entries.extend(_scan_file_for_todos(py_file))

    # Sort deterministically by file path then line number for reproducible output
    # ΛTAG: todo_scan_sort
    entries.sort(key=lambda entry: (str(entry.file_path.relative_to(root)), entry.line_number))
    return [entry.to_output_line(root) for entry in entries]


def _scan_python_files(repo: Path) -> list[str]:
    """Simple fallback scanner for backwards compatibility."""
    # ΛTAG: todo_scan_fallback_simple
    todo_lines: list[str] = []
    excluded = {token.strip("/") for token in EXCLUDE_TOKENS}

    for py_file in repo.rglob("*.py"):
        if any(part in excluded for part in py_file.parts):
            continue

        try:
            contents = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            contents = py_file.read_text(encoding="utf-8", errors="ignore")

        for idx, raw_line in enumerate(contents.splitlines(), 1):
            if re.search(r"\b(TODO|FIXME|HACK)\b", raw_line):
                relative_path = py_file.relative_to(repo)
                todo_lines.append(f"{relative_path}:{idx}:{raw_line.strip()}")

    return todo_lines


def _contains_excluded_token(line: str) -> bool:
    """Return True if the path contains an excluded token."""
    return any(token in line for token in EXCLUDE_TOKENS)


def classify_priority(todo_line: str, file_path: str, context: str = "") -> str:
    """Classify TODO priority based on content and location."""

    todo_lower = todo_line.lower()
    file_lower = file_path.lower()

    # ΛTAG: todo_priority_classification
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
        if "unused-import" in todo_lower or "document or remove" in todo_lower:
            return "MED"  # Import cleanup is medium priority
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
    if "tools/" in file_lower or "tests/" in file_lower:
        return "LOW"  # Tools and tests are generally lower priority
    if "products/" in file_lower:
        return "HIGH"  # Products are user-facing, higher priority
    return "MED"  # Default to medium


def extract_todo_context(line: str) -> tuple[str, str, str]:
    """Extract TODO text and context from grep line."""

    # ΛTAG: todo_context_parser
    parts = line.split(":", 2)
    if len(parts) < 3:
        return "", "", ""

    file_path = str(Path(parts[0]))
    line_num = parts[1]
    content = parts[2]

    todo_match = re.search(r"TODO[^:]*:?\s*(.+)", content, re.IGNORECASE)
    todo_text = todo_match.group(1).strip() if todo_match else content.strip()

    return file_path, line_num, todo_text


def categorize_todos(
    todo_lines: Optional[Iterable[str]] = None,
    repo_path: Optional[Path] = None,
) -> dict[str, list[TODORecord]]:
    """Categorize TODO entries and return priority buckets."""

    print("🔍 Loading TODOs with clean search...")
    lines = list(todo_lines) if todo_lines is not None else load_exclusions(repo_path)

    if not lines:
        print("❌ No TODOs found!")
        return {priority: [] for priority in PRIORITIES}

    print(f"📊 Processing {len(lines)} TODO entries...")

    categories: dict[str, list[TODORecord]] = {priority: [] for priority in PRIORITIES}

    for line in lines:
        if not line.strip():
            continue

        file_path, line_num, todo_text = extract_todo_context(line)
        if not todo_text:
            continue

        priority = classify_priority(todo_text, file_path)
        record = TODORecord(file=file_path, line=line_num, text=todo_text, priority=priority, raw=line)
        categories[priority].append(record)

    total = sum(len(todos) for todos in categories.values())
    print(f"\n📋 TODO Categorization Results:")
    print(f"  🚨 CRITICAL: {len(categories['CRITICAL'])}")
    print(f"  ⭐ HIGH: {len(categories['HIGH'])}")
    print(f"  📋 MED: {len(categories['MED'])}")
    print(f"  🔧 LOW: {len(categories['LOW'])}")
    print(f"  📊 TOTAL: {total}")

    return categories


def generate_priority_files(
    categories: dict[str, list[TODORecord]],
    repo_path: Optional[Path] = None,
    updated_at: Optional[datetime] = None,
) -> dict[str, Path]:
    """Generate markdown files for each priority level."""

    repo = Path(repo_path or REPO_ROOT)
    base_path = repo / "TODO"
    base_path.mkdir(parents=True, exist_ok=True)
    last_updated = (updated_at or datetime.now()).strftime("%B %d, %Y")

    priority_info = {
        "CRITICAL": {"emoji": "🚨", "description": "Security, consciousness safety, blocking issues"},
        "HIGH": {"emoji": "⭐", "description": "Core functionality, Trinity Framework, agent coordination"},
        "MED": {"emoji": "📋", "description": "Feature enhancements, optimization, documentation"},
        "LOW": {"emoji": "🔧", "description": "Cleanup, refactoring, nice-to-have features"},
    }

    generated_paths: dict[str, Path] = {}

    for priority, todos in categories.items():
        if not todos:
            continue

        info = priority_info[priority]
        filename = f"{priority.lower()}_todos.md"
        priority_dir = base_path / priority
        priority_dir.mkdir(parents=True, exist_ok=True)
        filepath = priority_dir / filename

        by_module = defaultdict(list)
        for todo in todos:
            by_module[todo.module].append(todo)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {info['emoji']} {priority} Priority TODOs\n\n")
            f.write(f"**{info['description']}**\n\n")
            f.write(f"**Count**: {len(todos)} TODOs\n")
            f.write(f"**Last Updated**: {last_updated}\n\n")

            f.write("## 📊 Summary by Module\n\n")
            for module in sorted(by_module.keys()):
                f.write(f"- **{module}**: {len(by_module[module])} TODOs\n")

            f.write("\n---\n\n")

            for module in sorted(by_module.keys()):
                module_todos = by_module[module]
                f.write(f"## 📁 {module.title()} Module ({len(module_todos)} TODOs)\n\n")

                for i, todo in enumerate(sorted(module_todos, key=_record_sort_key), 1):
                    preview = todo.text[:80] + ("..." if len(todo.text) > 80 else "")
                    f.write(f"### {i}. {preview}\n\n")
                    f.write(f"- **File**: `{todo.file}:{todo.line}`\n")
                    f.write(f"- **Priority**: {priority}\n")
                    f.write("- **Status**: Open\n")

                    trinity_aspect = _determine_trinity_aspect(todo.text)
                    if trinity_aspect:
                        f.write(f"- **Trinity Aspect**: {trinity_aspect}\n")

                    f.write(f"\n**TODO Text:**\n```\n{todo.text}\n```\n\n")
                    f.write("---\n\n")

        print(f"✅ Generated {filepath}")
        generated_paths[priority] = filepath

        # ΛTAG: todo_legacy_mirror - Keep legacy compatibility
        legacy_path = base_path / f"{priority.lower()}_todos.md"
        legacy_path.write_text(filepath.read_text(encoding="utf-8"), encoding="utf-8")

    return generated_paths


def _determine_trinity_aspect(text: str) -> Optional[str]:
    """Identify which Trinity aspect the TODO belongs to."""

    # ΛTAG: trinity_aspect_detection
    lowered = text.lower()
    if any(keyword in lowered for keyword in ["identity", "auth", "id", "lambda"]):
        return "⚛️ Identity"
    if any(keyword in lowered for keyword in ["consciousness", "memory", "cognitive", "dream"]):
        return "🧠 Consciousness"
    if any(keyword in lowered for keyword in ["security", "guardian", "safety", "ethics"]):
        return "🛡️ Guardian"
    return None


def _record_sort_key(record: TODORecord) -> tuple[str, int, str]:
    """Return a deterministic sort key for TODO records."""

    # ΛTAG: todo_output_sort
    try:
        line_number = int(record.line)
    except (TypeError, ValueError):
        line_number = 0
    return (record.file, line_number, record.text)


def main() -> None:
    """Execute the categorization workflow."""

    print("🎯 LUKHAS TODO Categorization System")
    print("=" * 50)

    repo_root = REPO_ROOT
    categories = categorize_todos(repo_path=repo_root)
    total = sum(len(entries) for entries in categories.values())

    if total:
        print("\n📝 Generating priority files...")
        generated = generate_priority_files(categories, repo_path=repo_root)
        print("\n✅ TODO categorization complete!")
        print("📂 Generated files:")
        for priority, path in generated.items():
            print(f"   • {priority}: {path}")
    else:
        print("❌ No TODOs to categorize")


__all__ = [
    "TODORecord",
    "categorize_todos",
    "generate_priority_files",
    "load_exclusions",
    "extract_todo_context",
    "classify_priority",
]


if __name__ == "__main__":
    main()
