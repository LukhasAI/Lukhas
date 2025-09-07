"""
Tools Utilities Module
======================
Essential utility functions for LUKHAS AI tools and development workflows.
Built on the established system/common/utils pattern for consistency.
"""
import json
import logging
import platform
import subprocess
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Optional, Union

import streamlit as st


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance for tools"""
    logger = logging.getLogger(f"tools.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def run_command(
    cmd: Union[str, list[str]],
    cwd: Optional[Path] = None,
    capture_output: bool = True,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """Run a shell command with proper error handling and timeout"""
    logger = get_logger("command")

    if isinstance(cmd, str):
        cmd = cmd.split()

    try:
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, text=True, timeout=timeout)

        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")

        return result

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        raise
    except FileNotFoundError:
        logger.error(f"Command not found: {cmd[0]}")
        raise


def safe_json_load(file_path: Path) -> Optional[dict[str, Any]]:
    """Safely load JSON file with error handling"""
    logger = get_logger("json")

    if not file_path.exists():
        logger.warning(f"JSON file not found: {file_path}")
        return None

    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


def safe_json_save(data: dict[str, Any], file_path: Path) -> bool:
    """Safely save data to JSON file"""
    logger = get_logger("json")

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return False


def find_files(directory: Path, pattern: str = "*.py", exclude_patterns: Optional[list[str]] = None) -> list[Path]:
    """Find files matching pattern, excluding specified patterns"""
    exclude_patterns = exclude_patterns or []
    exclude_patterns.extend(["__pycache__", ".git", ".venv", "node_modules", ".pytest_cache"])

    files = []
    for file_path in directory.rglob(pattern):
        if any(exclude in str(file_path) for exclude in exclude_patterns):
            continue
        files.append(file_path)

    return sorted(files)


def validate_python_syntax(file_path: Path) -> bool:
    """Validate Python file syntax"""
    logger = get_logger("syntax")

    try:
        with open(file_path) as f:
            source = f.read()

        compile(source, str(file_path), "exec")
        return True

    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error validating {file_path}: {e}")
        return False


def get_git_status() -> Optional[dict[str, Any]]:
    """Get current git repository status"""
    logger = get_logger("git")

    try:
        # Get current branch
        branch_result = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if branch_result.returncode != 0:
            return None

        current_branch = branch_result.stdout.strip()

        # Get status
        status_result = run_command(["git", "status", "--porcelain"])
        if status_result.returncode != 0:
            return None

        # Parse status
        modified = []
        untracked = []
        staged = []

        for line in status_result.stdout.splitlines():
            if line.startswith("M "):
                modified.append(line[3:])
            elif line.startswith("??"):
                untracked.append(line[3:])
            elif line.startswith("A "):
                staged.append(line[3:])

        return {
            "branch": current_branch,
            "modified": modified,
            "untracked": untracked,
            "staged": staged,
            "clean": len(modified) + len(untracked) + len(staged) == 0,
        }

    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_info(file_path: Path) -> dict[str, Any]:
    """Get comprehensive file information"""
    if not file_path.exists():
        return {"exists": False}

    stat = file_path.stat()

    info = {
        "exists": True,
        "size": stat.st_size,
        "size_human": format_file_size(stat.st_size),
        "modified": stat.st_mtime,
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "extension": file_path.suffix,
        "name": file_path.name,
        "parent": str(file_path.parent),
    }

    # Line count for text files
    if file_path.is_file() and file_path.suffix in [
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
    ]:
        try:
            with open(file_path, encoding="utf-8") as f:
                info["lines"] = len(f.readlines())
        except (UnicodeDecodeError, PermissionError):
            info["lines"] = None

    return info


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function calls on failure"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("retry")

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        import time

                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed. Last error: {e}")
                        raise

        return wrapper

    return decorator


@retry_on_failure(max_attempts=3)
def check_dependency(package_name: str) -> bool:
    """Check if a Python package is installed"""
    try:
        result = run_command([sys.executable, "-c", f"import {package_name}"], timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def get_system_info() -> dict[str, Any]:
    """Get basic system information for debugging"""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd()),
    }
