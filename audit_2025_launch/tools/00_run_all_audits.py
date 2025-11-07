#!/usr/bin/env python3
"""
LUKHAS Pre-Launch Audit - Master Orchestrator
Runs all audit tools and generates comprehensive executive summary.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_DIR = ROOT_DIR / "audit_2025_launch"
TOOLS_DIR = AUDIT_DIR / "tools"
REPORTS_DIR = AUDIT_DIR / "reports"
DATA_DIR = AUDIT_DIR / "data"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_TOOLS = [
    {
        "name": "Baseline Metrics",
        "script": "01_baseline_metrics.py",
        "description": "Gather codebase baseline statistics"
    },
    {
        "name": "Duplicate Detection",
        "script": "02_duplicate_detector.py",
        "description": "Find exact duplicates and suspicious file names"
    },
    {
        "name": "Archive Candidates",
        "script": "03_archive_candidates.py",
        "description": "Identify stale files and legacy code"
    },
    {
        "name": "Security Scan",
        "script": "04_security_scanner.py",
        "description": "Detect secrets, credentials, and sensitive data"
    },
    {
        "name": "Configuration Analysis",
        "script": "05_config_analyzer.py",
        "description": "Inventory and validate configurations"
    },
    {
        "name": "Documentation Quality",
        "script": "06_docs_quality_checker.py",
        "description": "Assess documentation completeness and quality"
    },
    {
        "name": "Test Coverage Mapping",
        "script": "07_test_coverage_mapper.py",
        "description": "Map tests to source code"
    },
    {
        "name": "Must-Keep Registry",
        "script": "08_must_keep_registry.py",
        "description": "Identify critical files to preserve"
    }
]

def run_audit_tool(tool_info):
    """Run a single audit tool and capture results."""
    script_path = TOOLS_DIR / tool_info["script"]

    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
            "duration": 0
        }

    print(f"\n{'=' * 80}")
    print(f"Running: {tool_info['name']}")
    print(f"Description: {tool_info['description']}")
    print(f"{'=' * 80}\n")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=ROOT_DIR
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(result.stdout)
            return {
                "success": True,
                "duration": round(duration, 2),
                "stdout": result.stdout,
                "stderr": result.stderr if result.stderr else None
            }
        else:
            print(f"ERROR: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr,
                "duration": round(duration, 2)
            }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "success": False,
            "error": "Timeout (>10 minutes)",
            "duration": round(duration, 2)
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "duration": round(duration, 2)
        }

def load_report(report_name):
    """Load a JSON report if it exists."""
    report_path = REPORTS_DIR / report_name

    if not report_path.exists():
        return None

    try:
        with open(report_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {report_name}: {e}")
        return None

def generate_executive_summary(execution_results):
    """Generate comprehensive executive summary."""
    print("\n" + "=" * 80)
    print("GENERATING EXECUTIVE SUMMARY")
    print("=" * 80 + "\n")

    # Load all reports
    baseline = load_report("baseline_metrics.json")
    duplicates = load_report("duplicate_files.json")
    archives = load_report("archive_candidates.json")
    security = load_report("security_findings.json")
    configs = load_report("config_inventory.json")
    docs = load_report("docs_quality_report.json")
    tests = load_report("test_coverage_map.json")
    must_keep = load_report("must_keep_registry.json")

    # Calculate launch readiness score
    readiness_score = 100
    blocking_issues = []

    # Security (critical)
    if security:
        critical_count = security.get("summary", {}).get("critical", 0)
        high_count = security.get("summary", {}).get("high", 0)

        if critical_count > 0:
            readiness_score -= 30
            blocking_issues.append(f"{critical_count} critical security findings")

        if high_count > 5:
            readiness_score -= 10

    # Duplicate waste
    if duplicates:
        wasted_mb = duplicates.get("summary", {}).get("total_wasted_space_mb", 0)
        if wasted_mb > 20:
            readiness_score -= 5

    # Documentation quality
    if docs:
        avg_quality = docs.get("summary", {}).get("average_quality_score", 0)
        if avg_quality < 60:
            readiness_score -= 10
        elif avg_quality < 75:
            readiness_score -= 5

    # Stale files
    if archives:
        high_confidence = archives.get("summary", {}).get("high_confidence", 0)
        if high_confidence > 100:
            readiness_score -= 5

    readiness_score = max(0, readiness_score)

    # Compile executive summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "audit_execution": {
            "total_tools": len(AUDIT_TOOLS),
            "successful": sum(1 for r in execution_results if r["success"]),
            "failed": sum(1 for r in execution_results if not r["success"]),
            "total_duration_seconds": sum(r["duration"] for r in execution_results)
        },
        "launch_readiness_score": readiness_score,
        "blocking_issues": blocking_issues,
        "key_metrics": {
            "total_files": baseline.get("file_type_counts", {}).get("python_total", 0) if baseline else 0,
            "total_tests": tests.get("summary", {}).get("total_test_functions", 0) if tests else 0,
            "documentation_files": docs.get("summary", {}).get("total_docs", 0) if docs else 0,
            "critical_security_findings": security.get("summary", {}).get("critical", 0) if security else 0,
            "duplicate_groups": duplicates.get("summary", {}).get("total_duplicate_groups", 0) if duplicates else 0,
            "archive_candidates": archives.get("summary", {}).get("total_candidates", 0) if archives else 0,
            "must_keep_files": must_keep.get("summary", {}).get("total_must_keep", 0) if must_keep else 0
        },
        "reports_generated": {
            "baseline_metrics": baseline is not None,
            "duplicate_files": duplicates is not None,
            "archive_candidates": archives is not None,
            "security_findings": security is not None,
            "config_inventory": configs is not None,
            "docs_quality": docs is not None,
            "test_coverage": tests is not None,
            "must_keep_registry": must_keep is not None
        }
    }

    # Save executive summary
    summary_path = REPORTS_DIR / "EXECUTIVE_SUMMARY.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, indent=2, fp=f)

    # Generate markdown summary
    md_path = REPORTS_DIR / "EXECUTIVE_SUMMARY.md"
    with open(md_path, 'w') as f:
        f.write("# LUKHAS Pre-Launch Comprehensive Audit\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

        f.write("## Launch Readiness Score\n\n")
        if readiness_score >= 90:
            status_emoji = "🟢"
            status_text = "READY FOR LAUNCH"
        elif readiness_score >= 75:
            status_emoji = "🟡"
            status_text = "MINOR ISSUES - LAUNCH READY AFTER FIXES"
        elif readiness_score >= 60:
            status_emoji = "🟠"
            status_text = "MODERATE ISSUES - CLEANUP RECOMMENDED"
        else:
            status_emoji = "🔴"
            status_text = "BLOCKING ISSUES - DO NOT LAUNCH"

        f.write(f"### {status_emoji} {readiness_score}/100 - {status_text}\n\n")

        if blocking_issues:
            f.write("### 🚨 Blocking Issues\n\n")
            for issue in blocking_issues:
                f.write(f"- {issue}\n")
            f.write("\n")

        f.write("## Audit Execution\n\n")
        f.write(f"- **Total Tools Run:** {summary['audit_execution']['total_tools']}\n")
        f.write(f"- **Successful:** {summary['audit_execution']['successful']}\n")
        f.write(f"- **Failed:** {summary['audit_execution']['failed']}\n")
        f.write(f"- **Total Duration:** {round(summary['audit_execution']['total_duration_seconds'] / 60, 1)} minutes\n\n")

        f.write("## Key Metrics\n\n")
        for metric, value in summary["key_metrics"].items():
            f.write(f"- **{metric.replace('_', ' ').title()}:** {value:,}\n")

        f.write("\n## Individual Reports\n\n")
        report_files = [
            ("baseline_metrics.json", "Baseline Metrics", "Codebase statistics and file counts"),
            ("duplicate_files.json", "Duplicate Detection", "Exact duplicates and suspicious file names"),
            ("archive_candidates.json", "Archive Candidates", "Stale files and legacy code"),
            ("security_findings.json", "Security Scan", "⚠️ SENSITIVE - Secrets and credentials"),
            ("config_inventory.json", "Configuration Analysis", "Config files and environment variables"),
            ("docs_quality_report.json", "Documentation Quality", "Docs completeness and quality scores"),
            ("docs_quality_report.md", "Documentation Summary", "Human-readable docs report"),
            ("test_coverage_map.json", "Test Coverage", "Test-to-code mapping"),
            ("must_keep_registry.json", "Must-Keep Registry", "Critical files to preserve")
        ]

        for filename, title, description in report_files:
            exists = "✓" if (REPORTS_DIR / filename).exists() else "✗"
            f.write(f"### {exists} {title}\n")
            f.write(f"**File:** `audit_2025_launch/reports/{filename}`\n")
            f.write(f"**Description:** {description}\n\n")

        f.write("## Recommendations\n\n")

        if security and security.get("summary", {}).get("critical", 0) > 0:
            f.write("### 🔴 CRITICAL: Security Findings\n")
            f.write(f"- {security['summary']['critical']} critical security issues found\n")
            f.write("- Review `security_findings.json` immediately\n")
            f.write("- **DO NOT launch until all critical findings are resolved**\n\n")

        if duplicates and duplicates.get("summary", {}).get("total_wasted_space_mb", 0) > 10:
            f.write("### 🟡 Duplicate Files\n")
            f.write(f"- {duplicates['summary']['total_wasted_space_mb']} MB wasted on duplicates\n")
            f.write("- Review `duplicate_files.json` for consolidation opportunities\n\n")

        if archives and archives.get("summary", {}).get("high_confidence", 0) > 50:
            f.write("### 🟡 Archive Candidates\n")
            f.write(f"- {archives['summary']['high_confidence']} high-confidence files can be archived\n")
            f.write("- Review `archive_candidates.json` before archiving\n\n")

        if docs and docs.get("summary", {}).get("average_quality_score", 0) < 75:
            f.write("### 🟡 Documentation Quality\n")
            f.write(f"- Average quality score: {docs['summary']['average_quality_score']}/100\n")
            f.write("- Target: 85/100 for public launch\n")
            f.write("- Review `docs_quality_report.md` for improvement areas\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. **Review EXECUTIVE_SUMMARY.md** (this file)\n")
        f.write("2. **Address blocking issues** (if any)\n")
        f.write("3. **Review individual reports** in `audit_2025_launch/reports/`\n")
        f.write("4. **Create GitHub issues** for remediation tasks\n")
        f.write("5. **Re-run audit** after fixes to validate improvements\n")

    print("\n✓ Executive summary saved to:")
    print(f"  JSON: {summary_path}")
    print(f"  Markdown: {md_path}")

    return summary

def main():
    """Main orchestrator function."""
    print("=" * 80)
    print("LUKHAS PRE-LAUNCH COMPREHENSIVE AUDIT")
    print("Master Orchestrator")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().isoformat()}")
    print(f"Repository: {ROOT_DIR}")
    print(f"Output Directory: {AUDIT_DIR}")
    print()

    execution_results = []

    # Run all audit tools
    for i, tool in enumerate(AUDIT_TOOLS, 1):
        print(f"\n[{i}/{len(AUDIT_TOOLS)}] {tool['name']}")
        result = run_audit_tool(tool)
        result["tool"] = tool["name"]
        execution_results.append(result)

        if not result["success"]:
            print(f"\n⚠️  Warning: {tool['name']} failed: {result.get('error', 'Unknown error')}")

    # Generate executive summary
    summary = generate_executive_summary(execution_results)

    # Final summary
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"\nLaunch Readiness Score: {summary['launch_readiness_score']}/100")

    if summary['blocking_issues']:
        print(f"\n🚨 BLOCKING ISSUES ({len(summary['blocking_issues'])}):")
        for issue in summary['blocking_issues']:
            print(f"  - {issue}")

    print(f"\nReports generated: {summary['audit_execution']['successful']}/{summary['audit_execution']['total_tools']}")
    print(f"Total duration: {round(summary['audit_execution']['total_duration_seconds'] / 60, 1)} minutes")

    print(f"\n📁 All reports saved to: {REPORTS_DIR}")
    print(f"📄 Executive summary: {REPORTS_DIR / 'EXECUTIVE_SUMMARY.md'}")

    print("\n" + "=" * 80)

    return 0 if summary['launch_readiness_score'] >= 75 else 1

if __name__ == "__main__":
    sys.exit(main())
