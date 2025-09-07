#!/usr/bin/env python3
"""
LUKHAS System Status Report Generator
====================================
Comprehensive status analysis of all LUKHAS components
Trinity Framework: ⚛️🧠🛡️

Date: August 5, 2025
"""
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st


def run_command(cmd: str) -> dict[str, Any]:
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "returncode": -1,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def test_import(module_name: str) -> dict[str, Any]:
    """Test if a module can be imported"""
    cmd = f"python3 -c 'import {module_name}; print(\"SUCCESS\")'"
    result = run_command(cmd)
    return {
        "module": module_name,
        "importable": result["success"] and "SUCCESS" in result["stdout"],
        "error": result["stderr"] if not result["success"] else None,
    }


def test_api_endpoint(url: str, timeout: int = 5) -> dict[str, Any]:
    """Test if an API endpoint is responding"""
    cmd = f"curl -s --max-time {timeout} {url}"
    result = run_command(cmd)
    return {
        "url": url,
        "responding": result["success"],
        "response": result["stdout"][:200] if result["success"] else None,
        "error": result["stderr"] if not result["success"] else None,
    }


def count_files(pattern: str) -> int:
    """Count files matching a pattern"""
    try:
        from glob import glob

        return len(glob(pattern, recursive=True))
    except BaseException:
        return 0


def get_git_status() -> dict[str, Any]:
    """Get git repository status"""
    status = {}

    # Git branch
    result = run_command("git branch --show-current")
    status["current_branch"] = result["stdout"] if result["success"] else "unknown"

    # Git status
    result = run_command("git status --porcelain")
    status["dirty"] = bool(result["stdout"]) if result["success"] else None
    status["modified_files"] = len(result["stdout"].split("\n")) if result["stdout"] else 0

    # Last commit
    result = run_command("git log -1 --oneline")
    status["last_commit"] = result["stdout"] if result["success"] else "unknown"

    return status


def analyze_pytest_results() -> dict[str, Any]:
    """Analyze pytest test results"""
    result = run_command("python3 -m pytest tests/ --collect-only -q")

    if not result["success"]:
        return {
            "total_tests": 0,
            "collection_error": result["stderr"],
            "status": "error",
        }

    # Count tests
    lines = result["stdout"].split("\n")
    test_count = 0
    for line in lines:
        if "collected" in line and "items" in line:
            try:
                test_count = int(line.split()[0])
                break
            except BaseException:
                continue

    return {
        "total_tests": test_count,
        "collection_error": None,
        "status": "success" if test_count > 0 else "warning",
    }


def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()


def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return Path(filepath).stat().st_size
    except BaseException:
        return 0


def generate_system_report() -> dict[str, Any]:
    """Generate comprehensive system status report"""

    print("🔍 Generating LUKHAS System Status Report...")
    print("=" * 50)

    report = {
        "metadata": {
            "report_title": "LUKHAS System Status Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "constellation_framework": "⚛️🧠🛡️",
            "version": "LUKHAS v7.0",
            "python_version": None,
            "working_directory": os.getcwd(),
        },
        "environment": {},
        "core_modules": {},
        "api_services": {},
        "file_system": {},
        "git_repository": {},
        "tests": {},
        "issues": [],
        "recommendations": [],
    }

    # Python environment
    print("🐍 Checking Python environment...")
    py_result = run_command("python3 --version")
    report["metadata"]["python_version"] = py_result["stdout"] if py_result["success"] else "unknown"

    # Environment variables
    print("🔧 Checking environment variables...")
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "PERPLEXITY_API_KEY",
        "GOOGLE_API_KEY",
    ]
    for var in env_vars:
        report["environment"][var] = {
            "present": bool(os.getenv(var)),
            "length": len(os.getenv(var, "")),
        }

    # Core module imports
    print("📦 Testing core module imports...")
    core_modules = [
        "lukhas_embedding",
        "symbolic_healer",
        "symbolic_api",
        "memory_chain",
        "memory_fold_tracker",
        "persona_similarity_engine",
        "gpt_integration_layer",
        "identity_emergence",
        "vivox",
    ]

    for module in core_modules:
        result = test_import(module)
        report["core_modules"][module] = result
        if not result["importable"]:
            report["issues"].append(f"❌ Module {module} failed to import: {result['error']}")

    # API services
    print("🌐 Testing API services...")
    api_endpoints = ["http://localhost:8000/health", "http://localhost:5888/health"]

    for endpoint in api_endpoints:
        result = test_api_endpoint(endpoint)
        port = endpoint.split(":")[-1].split("/")[0]
        report["api_services"][f"port_{port}"] = result
        if not result["responding"]:
            report["issues"].append(f"⚠️ API on port {port} not responding")

    # File system analysis
    print("📁 Analyzing file system...")
    important_files = {
        "README.md": "README.md",
        "requirements.txt": "requirements.txt",
        "integration_config.yaml": "integration_config.yaml",
        "symbolic_api.py": "symbolic_api.py",
        "lukhas_embedding.py": "lukhas_embedding.py",
        "symbolic_healer.py": "symbolic_healer.py",
        ".env": ".env",
        "z_collapse_engine.py": "z_collapse_engine.py",
    }

    for name, filepath in important_files.items():
        exists = check_file_exists(filepath)
        size = get_file_size(filepath) if exists else 0
        report["file_system"][name] = {
            "exists": exists,
            "size_bytes": size,
            "size_kb": round(size / 1024, 2) if size > 0 else 0,
        }
        if not exists:
            report["issues"].append(f"❌ Critical file missing: {filepath}")

    # Count files by type
    file_counts = {
        "python_files": count_files("**/*.py"),
        "test_files": count_files("**/test_*.py"),
        "yaml_files": count_files("**/*.yaml"),
        "json_files": count_files("**/*.json"),
        "markdown_files": count_files("**/*.md"),
    }
    report["file_system"]["file_counts"] = file_counts

    # Git repository status
    print("📋 Checking git repository...")
    report["git_repository"] = get_git_status()

    # Test suite analysis
    print("🧪 Analyzing test suite...")
    report["tests"] = analyze_pytest_results()

    if report["tests"]["status"] == "error":
        report["issues"].append(f"❌ Test collection failed: {report['tests']['collection_error']}")
    elif report["tests"]["total_tests"] == 0:
        report["issues"].append("⚠️ No tests found")

    # Generate recommendations
    print("💡 Generating recommendations...")

    # Check module import issues
    failed_imports = [name for name, data in report["core_modules"].items() if not data["importable"]]
    if failed_imports:
        report["recommendations"].append(f"Fix import issues: {', '.join(failed_imports)}")

    # Check API services
    non_responding_apis = [name for name, data in report["api_services"].items() if not data["responding"]]
    if non_responding_apis:
        report["recommendations"].append(f"Start API services: {', '.join(non_responding_apis)}")

    # Check missing files
    missing_files = [
        name for name, data in report["file_system"].items() if isinstance(data, dict) and not data.get("exists", True)
    ]
    if missing_files:
        report["recommendations"].append(f"Restore missing files: {', '.join(missing_files)}")

    # Environment variables
    missing_env = [var for var, data in report["environment"].items() if not data["present"]]
    if missing_env:
        report["recommendations"].append(f"Set environment variables: {', '.join(missing_env)}")

    # Calculate overall health score
    total_checks = (
        len(report["core_modules"])
        + len(report["api_services"])
        + len([f for f in report["file_system"] if isinstance(report["file_system"][f], dict)])
        + len(report["environment"])
    )

    successful_checks = (
        len([m for m in report["core_modules"].values() if m["importable"]])
        + len([a for a in report["api_services"].values() if a["responding"]])
        + len([f for f in report["file_system"].values() if isinstance(f, dict) and f.get("exists", False)])
        + len([e for e in report["environment"].values() if e["present"]])
    )

    health_score = (successful_checks / total_checks * 100) if total_checks > 0 else 0

    report["summary"] = {
        "overall_health_score": round(health_score, 1),
        "total_issues": len(report["issues"]),
        "total_recommendations": len(report["recommendations"]),
        "core_modules_working": len([m for m in report["core_modules"].values() if m["importable"]]),
        "total_core_modules": len(report["core_modules"]),
        "apis_responding": len([a for a in report["api_services"].values() if a["responding"]]),
        "total_apis_tested": len(report["api_services"]),
        "test_count": report["tests"]["total_tests"],
    }

    return report


def print_report_summary(report: dict[str, Any]):
    """Print a human-readable summary of the report"""

    print("\n" + "=" * 60)
    print("📊 LUKHAS SYSTEM STATUS SUMMARY")
    print("=" * 60)

    summary = report["summary"]

    print(f"🎯 Overall Health Score: {summary['overall_health_score']}%")
    print(f"📦 Core Modules: {summary['core_modules_working']}/{summary['total_core_modules']} working")
    print(f"🌐 API Services: {summary['apis_responding']}/{summary['total_apis_tested']} responding")
    print(f"🧪 Tests Available: {summary['test_count']}")
    print(f"⚠️ Issues Found: {summary['total_issues']}")
    print(f"💡 Recommendations: {summary['total_recommendations']}")

    if summary["overall_health_score"] >= 90:
        print("✅ System Status: EXCELLENT")
    elif summary["overall_health_score"] >= 75:
        print("🟡 System Status: GOOD")
    elif summary["overall_health_score"] >= 50:
        print("🟠 System Status: NEEDS ATTENTION")
    else:
        print("🔴 System Status: CRITICAL")

    print("\n📋 Core Module Status:")
    for module, status in report["core_modules"].items():
        icon = "✅" if status["importable"] else "❌"
        print(f"   {icon} {module}")

    print("\n🌐 API Service Status:")
    for service, status in report["api_services"].items():
        icon = "✅" if status["responding"] else "❌"
        port = service.replace("port_", "")
        print(f"   {icon} Port {port}")

    if report["issues"]:
        print("\n⚠️ Issues Found:")
        for issue in report["issues"]:
            print(f"   {issue}")

    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")

    print("\n" + "=" * 60)


def main():
    """Main function"""
    report = generate_system_report()

    # Save detailed report
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_file = f"data/system_status_report_{timestamp}.json"

    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print_report_summary(report)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return report_file


if __name__ == "__main__":
    main()
