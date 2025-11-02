#!/usr/bin/env python3
"""
Mypy Error Enumeration Script
Creates a structured JSON file of all mypy errors for agent task assignment
"""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ErrorPriority(Enum):
    CRITICAL = "critical"  # Core functionality, imports, type safety
    HIGH = "high"  # Method signatures, class definitions
    MEDIUM = "medium"  # Variable annotations, return types
    LOW = "low"  # Minor type hints, documentation


class ErrorCategory(Enum):
    IMPORT = "import"
    TYPE_ANNOTATION = "type_annotation"
    ATTRIBUTE = "attribute"
    ASSIGNMENT = "assignment"
    ARGUMENT = "argument"
    UNREACHABLE = "unreachable"
    OVERLOAD = "overload"
    OTHER = "other"


@dataclass
class MypyError:
    id: int
    file_path: str
    line_number: int
    error_code: str
    error_message: str
    category: ErrorCategory
    priority: ErrorPriority
    context: str
    suggested_fix: str = ""
    assigned_agent: str = "unassigned"
    status: str = "pending"


@dataclass
class FileErrors:
    file_path: str
    total_errors: int
    errors: list[MypyError]
    priority_breakdown: dict[str, int]


def parse_mypy_output(output: str) -> list[MypyError]:
    """Parse mypy output into structured error objects"""
    errors = []
    lines = output.strip().split("\n")

    error_id = 1
    for line in lines:
        if ": error:" in line:
            try:
                # Parse line format: file.py:line: error: message [code]
                parts = line.split(": error: ", 1)
                if len(parts) != 2:
                    continue

                file_part = parts[0]
                error_part = parts[1]

                # Extract file path and line number
                file_path, line_str = file_part.rsplit(":", 1)
                line_number = int(line_str)

                # Extract error message and code
                if " [" in error_part and error_part.endswith("]"):
                    message, code = error_part.rsplit(" [", 1)
                    error_code = code.rstrip("]")
                else:
                    message = error_part
                    error_code = "unknown"

                # Categorize error
                category = categorize_error(error_code, message)
                priority = prioritize_error(error_code, message, file_path)

                error = MypyError(
                    id=error_id,
                    file_path=file_path,
                    line_number=line_number,
                    error_code=error_code,
                    error_message=message.strip(),
                    category=category,
                    priority=priority,
                    context=line,
                    suggested_fix=generate_suggested_fix(error_code, message),
                )

                errors.append(error)
                error_id += 1

            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse line: {line} ({e})")
                continue

    return errors


def categorize_error(error_code: str, message: str) -> ErrorCategory:
    """Categorize error by type"""
    if "import" in error_code.lower() or "attr-defined" in error_code:
        return ErrorCategory.IMPORT
    elif "no-untyped-def" in error_code or "var-annotated" in error_code:
        return ErrorCategory.TYPE_ANNOTATION
    elif "attr-defined" in error_code or "union-attr" in error_code:
        return ErrorCategory.ATTRIBUTE
    elif "assignment" in error_code:
        return ErrorCategory.ASSIGNMENT
    elif "arg-type" in error_code:
        return ErrorCategory.ARGUMENT
    elif "unreachable" in error_code:
        return ErrorCategory.UNREACHABLE
    elif "overload" in error_code:
        return ErrorCategory.OVERLOAD
    else:
        return ErrorCategory.OTHER


def prioritize_error(error_code: str, message: str, file_path: str) -> ErrorPriority:
    """Determine error priority based on impact"""
    # Critical errors
    if any(code in error_code for code in ["import", "attr-defined", "union-attr"]):
        return ErrorPriority.CRITICAL

    # High priority
    if any(code in error_code for code in ["assignment", "arg-type", "no-untyped-def"]):
        return ErrorPriority.HIGH

    # Medium priority
    if "var-annotated" in error_code:
        return ErrorPriority.MEDIUM

    # Low priority
    return ErrorPriority.LOW


def generate_suggested_fix(error_code: str, message: str) -> str:
    """Generate suggested fix based on error type"""
    if "no-untyped-def" in error_code:
        return "Add type annotations to function parameters and return type"
    elif "var-annotated" in error_code:
        return "Add type annotation to variable declaration"
    elif "attr-defined" in error_code:
        return "Add type: ignore[attr-defined] comment or ensure attribute exists"
    elif "assignment" in error_code:
        return "Fix type compatibility in assignment or add type: ignore[assignment]"
    elif "arg-type" in error_code:
        return "Fix argument type compatibility"
    elif "import" in error_code:
        return "Add type: ignore[import] or fix import path"
    else:
        return "Review and fix type issue"


def group_errors_by_file(errors: list[MypyError]) -> dict[str, FileErrors]:
    """Group errors by file"""
    file_groups = {}

    for error in errors:
        if error.file_path not in file_groups:
            file_groups[error.file_path] = FileErrors(
                file_path=error.file_path,
                total_errors=0,
                errors=[],
                priority_breakdown={"critical": 0, "high": 0, "medium": 0, "low": 0},
            )

        file_groups[error.file_path].errors.append(error)
        file_groups[error.file_path].total_errors += 1
        file_groups[error.file_path].priority_breakdown[error.priority.value] += 1

    return file_groups


def create_agent_tasks(file_groups: dict[str, FileErrors], max_per_task: int = 10) -> dict[str, Any]:
    """Create agent task assignments"""
    tasks = {}
    task_id = 1

    # Sort files by error count (most critical first)
    sorted_files = sorted(
        file_groups.items(), key=lambda x: (x[1].priority_breakdown["critical"], x[1].total_errors), reverse=True
    )

    current_task = []
    current_task_errors = 0

    for file_path, file_errors in sorted_files:
        # If adding this file would exceed the limit, create a new task
        if current_task_errors + file_errors.total_errors > max_per_task and current_task:
            tasks[f"task_{task_id}"] = {
                "task_id": task_id,
                "agent": f"agent_{(task_id % 6) + 1}",  # Distribute across 6 agents
                "total_errors": current_task_errors,
                "files": current_task.copy(),
                "priority_breakdown": calculate_task_priority(current_task, file_groups),
                "estimated_complexity": estimate_complexity(current_task, file_groups),
            }
            task_id += 1
            current_task = []
            current_task_errors = 0

        current_task.append(file_path)
        current_task_errors += file_errors.total_errors

    # Add remaining files to final task
    if current_task:
        tasks[f"task_{task_id}"] = {
            "task_id": task_id,
            "agent": f"agent_{(task_id % 6) + 1}",
            "total_errors": current_task_errors,
            "files": current_task,
            "priority_breakdown": calculate_task_priority(current_task, file_groups),
            "estimated_complexity": estimate_complexity(current_task, file_groups),
        }

    return tasks


def calculate_task_priority(files: list[str], file_groups: dict[str, FileErrors]) -> dict[str, int]:
    """Calculate priority breakdown for a task"""
    breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for file_path in files:
        if file_path in file_groups:
            for priority, count in file_groups[file_path].priority_breakdown.items():
                breakdown[priority] += count
    return breakdown


def estimate_complexity(files: list[str], file_groups: dict[str, FileErrors]) -> str:
    """Estimate task complexity"""
    total_critical = sum(file_groups[f].priority_breakdown["critical"] for f in files if f in file_groups)
    total_errors = sum(file_groups[f].total_errors for f in files if f in file_groups)

    if total_critical > 5 or total_errors > 15:
        return "high"
    elif total_critical > 2 or total_errors > 8:
        return "medium"
    else:
        return "low"


def main():
    """Main function to generate mypy error enumeration"""
    print("🔍 Running mypy to collect current errors...")

    # Run mypy on the codebase
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", ".", "--show-error-codes", "--pretty", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        mypy_output = result.stdout + result.stderr

        if not mypy_output.strip():
            print("✅ No mypy errors found!")
            return

        print(f"📊 Parsing {len(mypy_output.splitlines())} lines of mypy output...")

        # Parse errors
        errors = parse_mypy_output(mypy_output)

        if not errors:
            print("⚠️ No parseable errors found in mypy output")
            return

        print(f"🎯 Found {len(errors)} parseable mypy errors")

        # Group by file
        file_groups = group_errors_by_file(errors)

        # Create agent tasks
        tasks = create_agent_tasks(file_groups)

        # Create final JSON structure
        error_enumeration = {
            "metadata": {
                "generated_at": "2025-09-01T00:00:00Z",
                "total_errors": len(errors),
                "total_files": len(file_groups),
                "total_tasks": len(tasks),
                "mypy_command": "python -m mypy . --show-error-codes --pretty --ignore-missing-imports",
            },
            "summary": {
                "errors_by_category": {},
                "errors_by_priority": {},
                "files_by_error_count": sorted(
                    [
                        {"file": f, "errors": fg.total_errors, "critical": fg.priority_breakdown["critical"]}
                        for f, fg in file_groups.items()
                    ],
                    key=lambda x: (x["critical"], x["errors"]),
                    reverse=True,
                )[
                    :10
                ],  # Top 10
            },
            "files": {
                file_path: {
                    "total_errors": fg.total_errors,
                    "priority_breakdown": fg.priority_breakdown,
                    "errors": [asdict(error) for error in fg.errors],
                }
                for file_path, fg in file_groups.items()
            },
            "tasks": tasks,
        }

        # Calculate summary stats
        for error in errors:
            error_enumeration["summary"]["errors_by_category"][error.category.value] = (
                error_enumeration["summary"]["errors_by_category"].get(error.category.value, 0) + 1
            )
            error_enumeration["summary"]["errors_by_priority"][error.priority.value] = (
                error_enumeration["summary"]["errors_by_priority"].get(error.priority.value, 0) + 1
            )

        # Save to JSON file
        output_file = Path("mypy_errors_enumeration.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(error_enumeration, f, indent=2, ensure_ascii=False)

        print(f"✅ Created {output_file} with {len(errors)} errors across {len(file_groups)} files")
        print(f"📋 Generated {len(tasks)} agent tasks for parallel processing")

        # Print summary
        print("\n📊 SUMMARY:")
        print(f"   Total Errors: {len(errors)}")
        print(f"   Files Affected: {len(file_groups)}")
        print(f"   Agent Tasks: {len(tasks)}")

        print("\n🔥 TOP 5 FILES BY CRITICAL ERRORS:")
        for i, file_info in enumerate(error_enumeration["summary"]["files_by_error_count"][:5], 1):
            print(f"   {i}. {file_info['file']} - {file_info['errors']} errors ({file_info['critical']} critical)")

        print("\n🎯 ERRORS BY CATEGORY:")
        for category, count in error_enumeration["summary"]["errors_by_category"].items():
            print(f"   {category}: {count}")

        print("\n🚨 ERRORS BY PRIORITY:")
        for priority, count in error_enumeration["summary"]["errors_by_priority"].items():
            print(f"   {priority}: {count}")

    except Exception as e:
        print(f"❌ Error running mypy: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
