"""Utilities for categorising TODO lines collected from the repository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, MutableMapping, Sequence

__all__ = [
    "PRIORITY_KEYWORDS",
    "TODORecord",
    "categorize_todos",
    "extract_todo_context",
    "generate_priority_files",
    "load_exclusions",
]


@dataclass(frozen=True, slots=True)
class TODORecord:
    """Represents a single TODO entry along with its computed priority."""

    file: str
    line: str
    text: str
    priority: str


# Priority keywords are ordered from highest to lowest severity.
PRIORITY_KEYWORDS: MutableMapping[str, Sequence[str]] = {
    "CRITICAL": (
        "security",
        "vulnerability",
        "breach",
        "exploit",
        "credential",
    ),
    "HIGH": (
        "guardian",
        "identity",
        "compliance",
        "auth",
        "encryption",
    ),
    "MED": (
        "performance",
        "optimize",
        "scaling",
        "refactor",
    ),
}

# Directories that should be ignored when scanning for TODOs.
SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}

# File extensions we care about when gathering TODO lines.
SCAN_EXTENSIONS = {".py", ".md", ".txt", ".rst"}

_COMMENT_PREFIX_RE = re.compile(r"^(#|//|/\*|<!--)\s*")
_TODO_PREFIX_RE = re.compile(r"^(?:TODO|FIXME|BUG)[:\s]+", re.IGNORECASE)

_DOMAIN_BADGES: Sequence[tuple[str, str]] = (
    ("identity", "⚛️ Identity"),
    ("guardian", "🛡️ Guardian"),
    ("security", "🛡️ Guardian"),
    ("memory", "🧠 Memory"),
    ("matriz", "🧩 Matriz"),
)


def extract_todo_context(raw_line: str) -> tuple[str, str, str]:
    """Normalise a raw ripgrep style match into (file, line, text)."""

    try:
        path_part, line_part, text_part = raw_line.split(":", 2)
    except ValueError:  # pragma: no cover - defensive branch
        raise ValueError(f"Unable to parse TODO line: {raw_line!r}") from None

    path = path_part.lstrip("./")
    line = line_part.strip()

    text = text_part.strip()
    text = _COMMENT_PREFIX_RE.sub("", text)
    text = _TODO_PREFIX_RE.sub("", text).strip()

    return path, line, text


def _iter_records(todo_lines: Iterable[str]) -> Iterator[TODORecord]:
    for raw_line in todo_lines:
        file_path, line, text = extract_todo_context(raw_line)
        priority = _determine_priority(file_path, text)
        yield TODORecord(file=file_path, line=line, text=text, priority=priority)


def _determine_priority(file_path: str, text: str) -> str:
    haystack = f"{file_path} {text}".lower()
    for priority in ("CRITICAL", "HIGH", "MED"):
        if any(keyword in haystack for keyword in PRIORITY_KEYWORDS[priority]):
            return priority
    return "LOW"


def categorize_todos(todo_lines: Iterable[str]) -> Dict[str, List[TODORecord]]:
    """Group TODO lines by inferred priority."""

    buckets: Dict[str, List[TODORecord]] = {key: [] for key in ("CRITICAL", "HIGH", "MED", "LOW")}
    for record in _iter_records(todo_lines):
        buckets[record.priority].append(record)
    return buckets


def _resolve_output_base(repo_path: Path | None, output_base: Path | None) -> Path:
    if output_base is not None:
        return output_base
    if repo_path is None:
        raise ValueError("Either repo_path or output_base must be provided.")
    return Path(repo_path)


def generate_priority_files(
    categories: Mapping[str, Iterable[TODORecord | Mapping[str, str]]],
    *,
    repo_path: Path | None = None,
    output_base: Path | None = None,
    updated_at: datetime | None = None,
) -> Dict[str, Path]:
    """Create per-priority markdown files for reviewer triage."""

    base = _resolve_output_base(repo_path, output_base)
    base.mkdir(parents=True, exist_ok=True)

    generated: Dict[str, Path] = {}
    timestamp = (updated_at or datetime.utcnow()).strftime("%B %d, %Y")

    for priority in ("CRITICAL", "HIGH", "MED", "LOW"):
        records = [_ensure_record(item) for item in categories.get(priority, [])]
        structured_dir = base / priority
        structured_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{priority.lower()}_todos.md"
        structured_path = structured_dir / filename
        legacy_path = base / filename

        content_lines = _build_markdown(priority, timestamp, records)
        structured_path.write_text("\n".join(content_lines) + "\n", encoding="utf-8")
        legacy_path.write_text("\n".join(content_lines) + "\n", encoding="utf-8")

        generated[priority] = structured_path
        generated.setdefault(f"legacy_{priority}", legacy_path)
        generated.setdefault(structured_path, structured_path)
        generated.setdefault(legacy_path, legacy_path)

    return generated


def _ensure_record(item: TODORecord | Mapping[str, str]) -> TODORecord:
    if isinstance(item, TODORecord):
        return item
    return TODORecord(
        file=str(item["file"]).lstrip("./"),
        line=str(item["line"]),
        text=str(item["text"]),
        priority=str(item.get("priority", "LOW")),
    )


def _build_markdown(priority: str, timestamp: str, records: Sequence[TODORecord]) -> List[str]:
    header_icon = {
        "CRITICAL": "🚨",
        "HIGH": "⚠️",
        "MED": "ℹ️",
        "LOW": "📝",
    }[priority]

    lines = [f"{header_icon} {priority.title()} TODOs", "", f"_Updated: {timestamp}_", ""]

    if not records:
        lines.append("- None")
        return lines

    for record in records:
        badge = _domain_badge(record)
        badge_str = f" {badge}" if badge else ""
        lines.append(f"- {record.file}:{record.line} — {record.text}{badge_str}")

    return lines


def _domain_badge(record: TODORecord) -> str | None:
    haystack = f"{record.file} {record.text}".lower()
    for keyword, badge in _DOMAIN_BADGES:
        if keyword in haystack:
            return badge
    return None


def load_exclusions(*, project_root: Path) -> List[str]:
    """Return TODO matches for backwards compatible exclusion scanning."""

    todo_lines: List[str] = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]
        for filename in files:
            if Path(filename).suffix not in SCAN_EXTENSIONS:
                continue
            file_path = Path(root, filename)
            rel_rel = file_path.relative_to(project_root).as_posix()
            rel_path = f"./{rel_rel}" if not rel_rel.startswith("./") else rel_rel
            lines = file_path.read_text(encoding="utf-8").splitlines()
            for lineno, text in enumerate(lines, start=1):
                if "TODO" in text or "FIXME" in text or "BUG" in text:
                    todo_lines.append(f"{rel_path}:{lineno}:{text}")
    return sorted(todo_lines)
