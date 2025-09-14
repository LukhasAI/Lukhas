"""
Audit Router - Comprehensive code quality and system health monitoring
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

router = APIRouter()

REPORTS_DIR = Path("reports")


@router.get("/status")
async def get_audit_status() -> dict[str, Any]:
    """Get current audit status and last run information"""
    try:
        # Check for existing audit reports
        audit_files = list(REPORTS_DIR.glob("*.txt")) + list(REPORTS_DIR.glob("*.json"))

        if not audit_files:
            return {
                "status": "no_audits_found",
                "message": "No audit reports found. Run an audit first.",
                "last_run": None,
            }

        # Get the most recent audit
        latest_file = max(audit_files, key=lambda f: f.stat().st_mtime)
        last_run = datetime.fromtimestamp(latest_file.stat().st_mtime, tz=timezone.utc)

        return {
            "status": "ready",
            "last_run": last_run.isoformat(),
            "reports_available": len(audit_files),
            "reports_directory": str(REPORTS_DIR),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
async def trigger_audit(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Trigger a new comprehensive audit"""
    try:
        # Add audit to background tasks
        background_tasks.add_task(run_audit_task)

        return {
            "status": "triggered",
            "message": "Audit has been triggered and will run in the background",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/summary")
async def get_audit_summary() -> dict[str, Any]:
    """Get summarized audit metrics"""
    try:
        metrics = {
            "code_quality": {},
            "security": {},
            "dependencies": {},
            "tests": {},
            "architecture": {},
        }

        # Read ruff results
        ruff_file = REPORTS_DIR / "ruff.txt"
        if ruff_file.exists():
            with open(ruff_file) as f:
                lines = f.readlines()
                metrics["code_quality"]["ruff_issues"] = len(lines)

        # Read git status
        git_status_file = REPORTS_DIR / "git_status.txt"
        if git_status_file.exists():
            with open(git_status_file) as f:
                lines = f.readlines()
                metrics["code_quality"]["uncommitted_files"] = len(lines)

        # Read gitleaks results
        gitleaks_file = REPORTS_DIR / "gitleaks.json"
        if gitleaks_file.exists():
            with open(gitleaks_file) as f:
                data = json.load(f)
                metrics["security"]["secrets_found"] = len(data) if isinstance(data, list) else 0

        # Calculate overall health score (0-100)
        health_score = calculate_health_score(metrics)

        return {
            "health_score": health_score,
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_name}")
async def get_specific_report(report_name: str) -> dict[str, Any]:
    """Get a specific audit report by name"""
    try:
        report_path = REPORTS_DIR / report_name

        if not report_path.exists():
            raise HTTPException(status_code=404, detail=f"Report {report_name} not found")

        # Handle different file types
        if report_name.endswith(".json"):
            with open(report_path) as f:
                content = json.load(f)
        else:
            with open(report_path) as f:
                content = f.read()

        return {
            "report_name": report_name,
            "content": content,
            "size_bytes": report_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(report_path.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Report {report_name} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_audit_trends() -> dict[str, Any]:
    """Get historical audit trends"""
    # This would typically query a database with historical data
    # For now, return mock data
    return {
        "trends": {
            "code_quality": {
                "7_days": [85, 86, 84, 87, 88, 89, 87],
                "30_days_avg": 86.5,
                "trend": "improving",
            },
            "security_score": {
                "7_days": [92, 93, 93, 94, 94, 94, 94],
                "30_days_avg": 93.2,
                "trend": "stable",
            },
            "test_coverage": {
                "7_days": [72, 73, 73, 74, 75, 75, 76],
                "30_days_avg": 74.1,
                "trend": "improving",
            },
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/dead-code")
async def get_dead_code_analysis() -> dict[str, Any]:
    """Get dead code analysis results"""
    try:
        dead_code = {
            "total_files": 0,
            "unused_files": [],
            "unused_functions": [],
            "unused_imports": [],
            "potential_savings_kb": 0,
        }

        # Read vulture results if available
        vulture_file = REPORTS_DIR / "vulture.txt"
        if vulture_file.exists():
            with open(vulture_file) as f:
                lines = f.readlines()
                dead_code["unused_functions"] = [line.strip() for line in lines[:10]]  # First 10

        # Read zero coverage files
        zero_cov_file = REPORTS_DIR / "zero_coverage_files.txt"
        if zero_cov_file.exists():
            with open(zero_cov_file) as f:
                lines = f.readlines()
                dead_code["unused_files"] = [line.strip() for line in lines[:10]]  # First 10

        return dead_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def calculate_health_score(metrics: dict) -> int:
    """Calculate overall health score from metrics"""
    score = 100

    # Deduct points for issues
    if "code_quality" in metrics:
        issues = metrics["code_quality"].get("ruff_issues", 0)
        score -= min(issues // 10, 30)  # Max 30 point deduction

    if "security" in metrics:
        secrets = metrics["security"].get("secrets_found", 0)
        score -= secrets * 5  # 5 points per secret

    return max(score, 0)


async def run_audit_task():
    """Background task to run the audit"""
    import subprocess

    try:
        # Run the audit script
        result = subprocess.run(
            ["./scripts/audit.sh"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Audit task failed: {e}")
        return False
