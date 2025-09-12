import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
Dev Tools Utils Module
Provides utilities for development and debugging of LUKHAS  system
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


def find_project_root() -> Path:
    """Find the project root directory by looking for key files."""
    current_path = Path.cwd()

    # Look for key project files
    key_files = ["CLAUDE.md", "lukhas_config.yaml", "requirements.txt"]

    # Search up the directory tree
    for path in [current_path, *list(current_path.parents)]:
        if any((path / key_file).exists() for key_file in key_files):
            return path

    # If not found, return current directory
    return current_path


def get_module_info(module_path: str) -> dict[str, Any]:
    """Get information about a Python module file."""
    path = Path(module_path)

    if not path.exists():
        return {"error": f"File not found: {module_path}"}

    info = {
        "path": str(path),
        "name": path.stem,
        "size": path.stat().st_size,
        "modified": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "lines": 0,
        "imports": [],
        "classes": [],
        "functions": [],
    }

    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
            info["lines"] = len(lines)

            for line_no, line in enumerate(lines, 1):
                line = line.strip()

                # Extract imports
                if line.startswith(("import ", "from ")):
                    info["imports"].append({"line": line_no, "statement": line})

                # Extract class definitions
                elif line.startswith("class "):
                    class_name = line.split()[1].split("(")[0].split(":")[0]
                    info["classes"].append({"line": line_no, "name": class_name})

                # Extract function definitions
                elif line.startswith("def ") or line.startswith("async def "):
                    func_name = line.split("(")[0].split()[-1]
                    info["functions"].append({"line": line_no, "name": func_name})

    except Exception as e:
        info["error"] = str(e)

    return info


def analyze_directory_structure(directory: str = ".") -> dict[str, Any]:
    """Analyze directory structure and provide statistics."""
    root_path = Path(directory)

    if not root_path.exists():
        return {"error": f"Directory not found: {directory}"}

    stats = {
        "root": str(root_path),
        "total_files": 0,
        "total_directories": 0,
        "python_files": 0,
        "config_files": 0,
        "test_files": 0,
        "doc_files": 0,
        "largest_files": [],
        "file_types": {},
    }

    try:
        for item in root_path.rglob("*"):
            if item.is_file():
                stats["total_files"] += 1

                # File type statistics
                suffix = item.suffix.lower()
                stats["file_types"][suffix] = stats["file_types"].get(suffix, 0) + 1

                # Categorize files
                if suffix == ".py":
                    stats["python_files"] += 1

                    # Check if it's a test file
                    if "test" in item.name.lower() or item.parent.name == "tests":
                        stats["test_files"] += 1

                elif suffix in [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"]:
                    stats["config_files"] += 1

                elif suffix in [".md", ".rst", ".txt"]:
                    stats["doc_files"] += 1

                # Track largest files
                size = item.stat().st_size
                stats["largest_files"].append(
                    {
                        "path": str(item),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                    }
                )
            elif item.is_dir():
                stats["total_directories"] += 1

        # Sort and limit largest files
        stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = stats["largest_files"][:10]

    except Exception as e:
        stats["error"] = str(e)

    return stats


def check_dependencies() -> dict[str, Any]:
    """Check status of project dependencies."""
    project_root = find_project_root()
    requirements_file = project_root / "requirements.txt"

    result = {
        "requirements_file": str(requirements_file),
        "exists": requirements_file.exists(),
        "dependencies": [],
        "installed": [],
        "missing": [],
    }

    if not requirements_file.exists():
        return result

    try:
        with open(requirements_file) as f:
            lines = f.readlines()

        # Parse requirements
        for line in lines:
            line = line.strip()
            if line and not line.startswith("# "):
                # Extract package name (handle versions and extras)
                package_name = line.split("==")[0].split(">=")[0].split("<=")[0]
                package_name = package_name.split("[")[0].strip()

                result["dependencies"].append({"name": package_name, "requirement": line})

                # Check if installed
                try:
                    __import__(package_name)
                    result["installed"].append(package_name)
                except ImportError:
                    result["missing"].append(package_name)

    except Exception as e:
        result["error"] = str(e)

    return result


def generate_dev_report() -> dict[str, Any]:
    """Generate a comprehensive development status report."""
    project_root = find_project_root()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
        },
        "project_structure": analyze_directory_structure(str(project_root)),
        "dependencies": check_dependencies(),
        "key_files": {},
    }

    # Check for key project files
    key_files = [
        "CLAUDE.md",
        "README.md",
        "requirements.txt",
        "lukhas_config.yaml",
        "main.py",
        "pytest.ini",
    ]

    for key_file in key_files:
        file_path = project_root / key_file
        report["key_files"][key_file] = {
            "exists": file_path.exists(),
            "path": str(file_path),
            "size": file_path.stat().st_size if file_path.exists() else 0,
        }

    return report


def save_report(report: dict[str, Any], filename: Optional[str] = None) -> str:
    """Save a development report to a JSON file."""
    if filename is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"dev_report_{timestamp}.json"

    project_root = find_project_root()
    report_path = project_root / "docs" / "reports" / filename

    # Create directories if needed
    report_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Development report saved to {report_path}")
        return str(report_path)

    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        raise


def quick_health_check() -> dict[str, Any]:
    """Perform a quick health check of the development environment."""
    try:
        project_root = find_project_root()

        health = {
            "status": "healthy",
            "checks": {
                "project_root_found": True,
                "requirements_file_exists": (project_root / "requirements.txt").exists(),
                "config_file_exists": (project_root / "lukhas_config.yaml").exists(),
                "main_entry_exists": (project_root / "main.py").exists(),
                "claude_md_exists": (project_root / "CLAUDE.md").exists(),
            },
            "recommendations": [],
        }

        # Add recommendations based on missing files
        if not health["checks"]["requirements_file_exists"]:
            health["recommendations"].append("Create requirements.txt file")

        if not health["checks"]["config_file_exists"]:
            health["recommendations"].append("Create lukhas_config.yaml file")

        if not health["checks"]["main_entry_exists"]:
            health["recommendations"].append("Create main.py entry point")

        # Overall health status
        failed_checks = sum(1 for check in health["checks"].values() if not check)
        if failed_checks > 2:
            health["status"] = "unhealthy"
        elif failed_checks > 0:
            health["status"] = "warning"

    except Exception as e:
        health = {
            "status": "error",
            "error": str(e),
            "checks": {},
            "recommendations": ["Fix critical error in development environment"],
        }

    return health


# CLI interface functions
def main():
    """Main CLI entry point for dev tools utilities."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS  Development Tools")
    parser.add_argument("--health", action="store_true", help="Run quick health check")
    parser.add_argument("--report", action="store_true", help="Generate full dev report")
    parser.add_argument("--analyze", type=str, help="Analyze directory structure")
    parser.add_argument("--deps", action="store_true", help="Check dependencies")
    parser.add_argument("--save", action="store_true", help="Save report to file")

    args = parser.parse_args()

    if args.health:
        health = quick_health_check()
        print(json.dumps(health, indent=2))

    elif args.report:
        report = generate_dev_report()
        if args.save:
            path = save_report(report)
            print(f"Report saved to: {path}")
        else:
            print(json.dumps(report, indent=2))

    elif args.analyze:
        analysis = analyze_directory_structure(args.analyze)
        print(json.dumps(analysis, indent=2))

    elif args.deps:
        deps = check_dependencies()
        print(json.dumps(deps, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()