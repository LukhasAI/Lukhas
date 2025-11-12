import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Mock missing lukhas modules
try:
    from lukhas.reporting import report_error, report_info, report_warning
except ImportError:
    print("Faking lukhas.reporting for local run")
    def report_info(msg, *args):
        print(f"INFO: {msg}", *args)
    def report_warning(msg, *args):
        print(f"WARN: {msg}", *args)
    def report_error(msg, *args):
        print(f"ERROR: {msg}", *args)


# Regex for SHA pinning (commit hash)
SHA_PINNED_ACTION_REGEX = re.compile(r"^[a-zA-Z0-9_/-]+@[a-f0-9]{40}$")

# Regex for detecting potential secrets. This is a basic check.
SECRET_REGEX = re.compile(
    r"""(?i)\b(key|secret|token|password|auth|credential|pass)\b\s*[:=]\s*['\"]?[a-zA-Z0-9\-_]{20,}['\"]?"""
)


def find_workflow_files(workflows_dir: Path) -> List[Path]:
    """Finds all YAML workflow files in the given directory."""
    return list(workflows_dir.glob("*.yml"))


def check_unpinned_actions(workflow_content: Dict[str, Any], file_path: Path) -> int:
    """Checks for unpinned actions in a workflow."""
    error_count = 0
    if "jobs" not in workflow_content:
        return 0

    for job_name, job_def in workflow_content.get("jobs", {}).items():
        if "steps" not in job_def:
            continue
        for step in job_def.get("steps", []):
            if "uses" in step:
                action = step["uses"]
                if not SHA_PINNED_ACTION_REGEX.match(action):
                    report_warning(
                        f"Unpinned action found in {file_path} -> job:"
                        f" {job_name} -> uses: {action}. Use a full-length"
                        " commit SHA."
                    )
                    error_count += 1
    return error_count


def check_secret_leaks(workflow_content_str: str, file_path: Path) -> int:
    """Scans for potential secret leaks in a workflow file."""
    error_count = 0
    for match in SECRET_REGEX.finditer(workflow_content_str):
        report_error(
            f"Potential secret leak found in {file_path} at line"
            f" {workflow_content_str.count(os.linesep, 0, match.start()) + 1}:"
            f" '{match.group(0)}'"
        )
        error_count += 1
    return error_count


def check_permissions(workflow_content: Dict[str, Any], file_path: Path) -> int:
    """Checks for missing or overly permissive permissions."""
    error_count = 0
    has_top_level_permissions = "permissions" in workflow_content

    if not has_top_level_permissions:
         report_warning(f"Missing top-level 'permissions' block in {file_path}")
         error_count += 1


    for job_name, job_def in workflow_content.get("jobs", {}).items():
        if "permissions" not in job_def and not has_top_level_permissions:
            report_warning(
                f"Missing 'permissions' block for job '{job_name}' in"
                f" {file_path}"
            )
            error_count += 1

        job_permissions = job_def.get("permissions")
        if isinstance(job_permissions, str) and job_permissions == "write-all":
            report_error(
                f"Overly permissive 'permissions: write-all' for job"
                f" '{job_name}' in {file_path}"
            )
            error_count += 1

    top_level_permissions = workflow_content.get("permissions")
    if isinstance(top_level_permissions, str) and top_level_permissions == "write-all":
        report_error(f"Overly permissive top-level 'permissions: write-all' in {file_path}")
        error_count += 1


    return error_count


def main():
    """Main function to audit GitHub Actions workflows."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.is_dir():
        report_error(f"Directory not found: {workflows_dir}")
        sys.exit(1)

    workflow_files = find_workflow_files(workflows_dir)
    if not workflow_files:
        report_info("No workflow files found to audit.")
        sys.exit(0)

    total_errors = 0
    report_info(f"Scanning {len(workflow_files)} workflow files...")

    for file_path in workflow_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_content_str = f.read()
                # The FullLoader is safer than the default Loader
                workflow_content = yaml.load(workflow_content_str, Loader=yaml.FullLoader)

            if not workflow_content:
                report_warning(f"Skipping empty or invalid workflow file: {file_path}")
                continue

            total_errors += check_unpinned_actions(workflow_content, file_path)
            total_errors += check_secret_leaks(workflow_content_str, file_path)
            total_errors += check_permissions(workflow_content, file_path)

        except yaml.YAMLError as e:
            report_error(f"Error parsing YAML file {file_path}: {e}")
            total_errors += 1
        except Exception as e:
            report_error(f"An unexpected error occurred with file {file_path}: {e}")
            total_errors += 1


    if total_errors > 0:
        report_error(f"Found {total_errors} issues in workflow files.")
        sys.exit(1)
    else:
        report_info("No issues found in workflow files. ✨")
        sys.exit(0)


if __name__ == "__main__":
    main()
