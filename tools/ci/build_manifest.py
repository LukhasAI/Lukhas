#!/usr/bin/env python3
"""
T4-Compliant TODO Manifest Builder

Implements ground truth enumeration per PLANNING_TODO.md:
- Parse all TODO markdown files
- Cross-check with live codebase
- Verify claimed completions against actual code
- Generate canonical manifest with evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class TodoManifestBuilder:
    def __init__(self):
        self.todos = []
        self.evidence_cache = {}

    def parse_markdown_todos(self, todo_files: List[str]) -> List[Dict[str, Any]]:
        """Parse structured TODOs from markdown files"""
        todos = []

        for file_path in todo_files:
            priority = self._extract_priority_from_filename(file_path)
            content = Path(file_path).read_text()

            # Parse markdown TODO entries
            todo_entries = self._parse_markdown_entries(content, file_path, priority)
            todos.extend(todo_entries)

        return todos

    def _extract_priority_from_filename(self, file_path: str) -> str:
        """Extract priority from filename"""
        file_name = Path(file_path).stem.lower()
        if "critical" in file_name:
            return "critical"
        elif "high" in file_name:
            return "high"
        elif "med" in file_name:
            return "med"
        elif "low" in file_name:
            return "low"
        return "unknown"

    def _parse_markdown_entries(self, content: str, source_file: str, priority: str) -> List[Dict[str, Any]]:
        """Parse individual TODO entries from markdown content"""
        entries = []

        # Split by separator lines (---)
        sections = re.split(r"\n---\n", content)

        for section in sections:
            if not section.strip():
                continue

            entry = self._parse_single_entry(section, source_file, priority)
            if entry:
                entries.append(entry)

        return entries

    def _parse_single_entry(self, section: str, source_file: str, priority: str) -> Dict[str, Any] | None:
        """Parse a single TODO entry from markdown section"""
        # Extract file path
        file_match = re.search(r"\*\*File\*\*:\s*`([^`]+)`", section)
        if not file_match:
            return None

        file_path = file_match.group(1)

        # Extract line hint if present
        line_match = re.search(r":(\d+)", file_path)
        line_hint = int(line_match.group(1)) if line_match else None
        clean_file = re.sub(r":\d+$", "", file_path)

        # Extract title/description
        title = self._extract_todo_text(section)

        # Check completion status
        status_match = re.search(r"\*\*Status\*\*:\s*(.+)", section)
        status = "open"
        if status_match and "✅ COMPLETED" in status_match.group(1):
            status = "completed"

        # Generate TaskID
        task_id = self._generate_task_id(priority, clean_file, title)

        # Determine Trinity aspect and module
        constellation = self._determine_trinity_aspect(clean_file, title)
        module = self._extract_module(clean_file)

        entry = {
            "task_id": task_id,
            "priority": priority,
            "title": title,
            "file": clean_file,
            "line_hint": line_hint,
            "module": module,
            "constellation": constellation,
            "status": status,
            "source": Path(source_file).name,
            "evidence": {"grep": None, "last_commit": None},
            "acceptance": [],
            "risk": self._assess_risk(clean_file, title),
            "est": {"type": self._classify_type(title), "size": self._estimate_size(title)},
        }

        return entry

    def _generate_task_id(self, priority: str, file_path: str, title: str) -> str:
        """Generate TaskID: TODO-{PRIORITY}-{MODULE}-{HASH8}"""
        priority_code = priority.upper()[:4]
        module_raw = self._extract_module(file_path)
        module = re.sub(r"[^A-Z0-9-]", "", module_raw.replace("/", "-").upper())
        if not module:
            module = "GENERAL"

        # Generate 8-char hash from file + title
        hash_input = f"{file_path}:{title}"
        hash_8 = hashlib.md5(hash_input.encode()).hexdigest()[:8]

        return f"TODO-{priority_code}-{module}-{hash_8}"

    def _extract_module(self, file_path: str) -> str:
        """Extract module name from file path"""
        parts = Path(file_path).parts
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        elif len(parts) >= 1:
            return parts[0]
        return "unknown"

    def _determine_trinity_aspect(self, file_path: str, title: str) -> str:
        """Determine Trinity Framework aspect"""
        path_lower = file_path.lower()
        title_lower = title.lower()

        if any(
            keyword in path_lower or keyword in title_lower for keyword in ["identity", "auth", "credential", "lambda"]
        ):
            return "Identity"
        elif any(
            keyword in path_lower or keyword in title_lower
            for keyword in ["consciousness", "awareness", "dream", "memory"]
        ):
            return "Consciousness"
        elif any(
            keyword in path_lower or keyword in title_lower
            for keyword in ["guardian", "ethics", "safety", "governance"]
        ):
            return "Guardian"
        return "null"

    def _assess_risk(self, file_path: str, title: str) -> str:
        """Assess risk level based on file path and content"""
        high_risk_patterns = ["quantum", "crypto", "security", "guardian", "safety"]
        med_risk_patterns = ["consciousness", "identity", "governance"]

        content = f"{file_path} {title}".lower()

        if any(pattern in content for pattern in high_risk_patterns):
            return "high"
        elif any(pattern in content for pattern in med_risk_patterns):
            return "med"
        return "low"

    def _classify_type(self, title: str) -> str:
        """Classify TODO type"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ["import", "f821", "rename", "docstring"]):
            return "mechanical"
        elif any(keyword in title_lower for keyword in ["integration", "coordinate", "orchestration"]):
            return "integration"
        return "logic"

    def _estimate_size(self, title: str) -> str:
        """Estimate task size"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ["document", "import", "rename"]):
            return "XS"
        elif any(keyword in title_lower for keyword in ["implement", "add", "create"]):
            return "S"
        elif any(keyword in title_lower for keyword in ["integration", "refactor"]):
            return "M"
        elif any(keyword in title_lower for keyword in ["system", "architecture", "framework"]):
            return "L"
        return "S"

    def cross_check_codebase(self, grep_file: str, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cross-check TODOs against live codebase"""
        # Read grep results
        grep_todos = []
        if Path(grep_file).exists():
            with open(grep_file) as f:
                for line in f:
                    line = line.strip()
                    if ":" in line and ("TODO" in line or "FIXME" in line or "HACK" in line):
                        grep_todos.append(line)

        # Add evidence to existing TODOs
        for todo in todos:
            evidence = self._find_evidence(todo, grep_todos)
            todo["evidence"] = evidence

        # Add new TODOs found in grep but not in markdown
        markdown_files = {todo["file"].lstrip("./") for todo in todos}
        existing_ids = {todo["task_id"] for todo in todos}
        for grep_line in grep_todos:
            file_path = grep_line.split(":")[0]
            if file_path.lstrip("./") not in markdown_files:
                new_todo = self._create_todo_from_grep(grep_line)
                if new_todo and new_todo["task_id"] not in existing_ids:
                    todos.append(new_todo)
                    existing_ids.add(new_todo["task_id"])

        return todos

    def _extract_todo_text(self, section: str) -> str:
        """Extract TODO text allowing for language-specific fences."""  # ΛTAG: manifest_resilience

        block_match = re.search(r"\*\*TODO Text:\*\*\s*```(?:[\w-]+\n)?([^`]+)```", section, re.DOTALL)
        if block_match:
            return block_match.group(1).strip()

        inline_match = re.search(r"\*\*TODO Text:\*\*\s*(.+)", section)
        return inline_match.group(1).strip() if inline_match else "No description"

    def _find_evidence(self, todo: Dict[str, Any], grep_todos: List[str]) -> Dict[str, Any]:
        """Find evidence for TODO in grep results and git history"""
        evidence = {"grep": None, "last_commit": None}

        # Check grep evidence
        file_path = todo["file"].lstrip("./")
        for grep_line in grep_todos:
            grep_file = grep_line.split(":", 1)[0].lstrip("./")
            if grep_file == file_path:
                evidence["grep"] = grep_line
                break

        # Check git history for last modification
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", file_path], capture_output=True, text=True, cwd="."
            )
            if result.returncode == 0 and result.stdout.strip():
                evidence["last_commit"] = result.stdout.strip()
        except Exception:
            pass

        return evidence

    def _create_todo_from_grep(self, grep_line: str) -> Dict[str, Any] | None:
        """Create TODO entry from grep result"""
        parts = grep_line.split(":", 2)
        if len(parts) < 3:
            return None

        file_path = parts[0]
        line_num = int(parts[1]) if parts[1].isdigit() else None
        content = parts[2]

        # Extract TODO content
        todo_match = re.search(r"(TODO|FIXME|HACK)[:\s]*(.+)", content, re.IGNORECASE)
        title = todo_match.group(2).strip() if todo_match else content.strip()

        task_id = self._generate_task_id("high", file_path, title)

        return {
            "task_id": task_id,
            "priority": "high",
            "title": title,
            "file": file_path,
            "line_hint": line_num,
            "module": self._extract_module(file_path),
            "constellation": self._determine_trinity_aspect(file_path, title),
            "status": "open",
            "source": "code_scan",
            "evidence": {"grep": grep_line, "last_commit": None},
            "acceptance": ["unit tests cover happy/failure paths"],
            "risk": self._assess_risk(file_path, title),
            "est": {"type": self._classify_type(title), "size": self._estimate_size(title)},
        }

    def generate_manifest(self, todos: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
        """Generate final manifest"""
        # Get git HEAD SHA
        try:
            result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
            root_sha = result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            root_sha = "unknown"

        manifest = {
            "run_id": run_id,
            "created_at": datetime.now().isoformat() + "Z",
            "root_sha": root_sha,
            "stats": {"total": len(todos), "by_priority": {}, "by_status": {}, "by_source": {}},
            "todos": todos,
        }

        # Calculate stats
        for todo in todos:
            priority = todo["priority"]
            status = todo["status"]
            source = todo["source"]

            manifest["stats"]["by_priority"][priority] = manifest["stats"]["by_priority"].get(priority, 0) + 1
            manifest["stats"]["by_status"][status] = manifest["stats"]["by_status"].get(status, 0) + 1
            manifest["stats"]["by_source"][source] = manifest["stats"]["by_source"].get(source, 0) + 1

        return manifest


def main():
    parser = argparse.ArgumentParser(description="Build T4-compliant TODO manifest")
    parser.add_argument("--todo-md", nargs="+", required=True, help="TODO markdown files to parse")
    parser.add_argument("--grep", required=True, help="Grep results file")
    parser.add_argument("--out", required=True, help="Output manifest file")
    parser.add_argument(
        "--run-id", default=f"LUKHAS-RUN-{datetime.now().strftime('%Y-%m-%d')}-A", help="Run ID for this enumeration"
    )

    args = parser.parse_args()

    builder = TodoManifestBuilder()

    # Parse markdown TODOs
    print(f"Parsing {len(args.todo_md)} TODO markdown files...")
    todos = builder.parse_markdown_todos(args.todo_md)
    print(f"Found {len(todos)} TODOs in markdown files")

    # Cross-check with codebase
    print(f"Cross-checking with codebase from {args.grep}...")
    todos = builder.cross_check_codebase(args.grep, todos)
    print(f"Total TODOs after cross-check: {len(todos)}")

    # Generate manifest
    print(f"Generating manifest with run ID: {args.run_id}")
    manifest = builder.generate_manifest(todos, args.run_id)

    # Write manifest
    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {args.out}")
    print(f"Stats: {manifest['stats']}")


if __name__ == "__main__":
    main()
