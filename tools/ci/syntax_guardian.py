#!/usr/bin/env python3
"""
Syntax Guardian - Mass Breakage Prevention System
================================================

Prevents automation experiments from causing mass syntax damage by:
1. Pre-commit validation with error thresholds
2. Syntax error trend monitoring 
3. Automated recovery suggestions
4. CI pipeline integration

This system was created after the candidate/ directory automation experiment
that increased syntax errors from 7,390 → 9,968, requiring git recovery.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Error thresholds for mass breakage detection
SYNTAX_ERROR_THRESHOLDS = {
    "warning": 100,      # Warn if adding >100 new syntax errors
    "critical": 500,     # Block commit if adding >500 new syntax errors  
    "emergency": 1000,   # Trigger emergency procedures if >1000 new errors
}

# Baseline error counts (updated after successful recoveries)
BASELINE_ERRORS = {
    "candidate/": 0,     # Post-Phase 3 recovery baseline (2025-09-08)
    "lukhas/": 0,        # Production lane baseline (clean)
    ".": 0,              # Repository-wide baseline (clean)
}


def run_ruff_syntax_check(directory: str = ".") -> Tuple[int, List[str]]:
    """
    Run ruff syntax check and return error count and file list.
    
    Returns:
        Tuple of (error_count, error_files)
    """
    try:
        result = subprocess.run([
            ".venv/bin/ruff", "check", directory,
            "--select=E999,F999",  # Syntax errors only
            "--output-format=json",
            "--quiet"
        ], capture_output=True, text=True, timeout=60)
        
        if result.stdout:
            errors = json.loads(result.stdout)
            error_files = list({error["filename"] for error in errors})
            return len(errors), error_files
        else:
            return 0, []
            
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️ Syntax check failed: {e}")
        return -1, []


def check_syntax_trends() -> Dict[str, int]:
    """
    Check current syntax error counts across key directories.
    
    Returns:
        Dictionary of directory -> error_count
    """
    trends = {}
    
    for directory in ["candidate/", "lukhas/", "."]:
        error_count, _ = run_ruff_syntax_check(directory)
        if error_count >= 0:
            trends[directory] = error_count
        else:
            trends[directory] = -1  # Check failed
            
    return trends


def analyze_syntax_delta(current_trends: Dict[str, int]) -> Dict[str, Dict]:
    """
    Analyze syntax error delta against baselines.
    
    Returns:
        Analysis results with severity levels and recommendations
    """
    analysis = {}
    
    for directory, current_count in current_trends.items():
        if current_count < 0:  # Check failed
            continue
            
        baseline = BASELINE_ERRORS.get(directory, 0)
        delta = current_count - baseline
        
        # Determine severity
        severity = "ok"
        if delta > SYNTAX_ERROR_THRESHOLDS["emergency"]:
            severity = "emergency"
        elif delta > SYNTAX_ERROR_THRESHOLDS["critical"]: 
            severity = "critical"
        elif delta > SYNTAX_ERROR_THRESHOLDS["warning"]:
            severity = "warning"
            
        analysis[directory] = {
            "current": current_count,
            "baseline": baseline,
            "delta": delta,
            "severity": severity,
            "percentage_change": (delta / baseline * 100) if baseline > 0 else 0
        }
        
    return analysis


def generate_recovery_plan(analysis: Dict[str, Dict]) -> List[str]:
    """
    Generate automated recovery recommendations based on analysis.
    
    Returns:
        List of recovery steps
    """
    recovery_steps = []
    
    # Check for emergency situations
    emergency_dirs = [d for d, a in analysis.items() if a["severity"] == "emergency"]
    if emergency_dirs:
        recovery_steps.extend([
            "🚨 EMERGENCY: Mass syntax breakage detected!",
            "1. STOP all automation experiments immediately",
            "2. Identify last known good commit with git log --oneline -20",
            "3. Consider git restore strategy: git checkout <clean_commit> -- candidate/",
            "4. Run comprehensive tests to verify recovery",
            "5. Cherry-pick essential recent changes if needed"
        ])
        
    # Check for critical situations  
    critical_dirs = [d for d, a in analysis.items() if a["severity"] == "critical"]
    if critical_dirs:
        recovery_steps.extend([
            "⚠️ CRITICAL: Significant syntax error increase detected",
            "1. Review recent commits for automation or mass changes",
            "2. Run .venv/bin/ruff check --fix on affected directories",
            "3. Run custom syntax fixer: python tools/fix_syntax_errors.py", 
            "4. Consider selective git restore if mass damage occurred"
        ])
        
    # Check for warning situations
    warning_dirs = [d for d, a in analysis.items() if a["severity"] == "warning"]
    if warning_dirs:
        recovery_steps.extend([
            "💡 WARNING: Elevated syntax errors detected",
            "1. Run ruff autofix: .venv/bin/ruff check --fix",
            "2. Review recent changes for systematic issues",
            "3. Update T4 autofix policies if needed"
        ])
        
    return recovery_steps


def create_syntax_report() -> Dict:
    """
    Create comprehensive syntax guardian report.
    
    Returns:
        Complete report dictionary
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    trends = check_syntax_trends()
    analysis = analyze_syntax_delta(trends)
    recovery_plan = generate_recovery_plan(analysis)
    
    # Determine overall status
    max_severity = "ok"
    for dir_analysis in analysis.values():
        if dir_analysis["severity"] == "emergency":
            max_severity = "emergency"
            break
        elif dir_analysis["severity"] == "critical" and max_severity != "emergency":
            max_severity = "critical"
        elif dir_analysis["severity"] == "warning" and max_severity not in ["critical", "emergency"]:
            max_severity = "warning"
    
    report = {
        "timestamp": timestamp,
        "status": max_severity,
        "trends": trends,
        "analysis": analysis,
        "recovery_plan": recovery_plan,
        "baselines": BASELINE_ERRORS,
        "thresholds": SYNTAX_ERROR_THRESHOLDS
    }
    
    return report


def save_syntax_report(report: Dict, filepath: str = "syntax_guardian_report.json"):
    """Save syntax report to file."""
    Path(filepath).write_text(json.dumps(report, indent=2))


def print_syntax_report(report: Dict):
    """Print human-readable syntax report."""
    print("=" * 60)
    print("🛡️ SYNTAX GUARDIAN REPORT")
    print("=" * 60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Status: {report['status'].upper()}")
    print()
    
    print("📊 SYNTAX ERROR TRENDS:")
    for directory, analysis in report["analysis"].items():
        severity_emoji = {
            "ok": "✅",
            "warning": "⚠️", 
            "critical": "🔥",
            "emergency": "🚨"
        }[analysis["severity"]]
        
        print(f"{severity_emoji} {directory}:")
        print(f"   Current: {analysis['current']} errors")
        print(f"   Baseline: {analysis['baseline']} errors") 
        print(f"   Delta: {analysis['delta']:+d} ({analysis['percentage_change']:+.1f}%)")
        print()
    
    if report["recovery_plan"]:
        print("🔧 RECOVERY RECOMMENDATIONS:")
        for step in report["recovery_plan"]:
            print(f"   {step}")
        print()
    
    print("=" * 60)


def main():
    """Main syntax guardian execution."""
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-commit":
        # Pre-commit hook mode - stricter validation
        report = create_syntax_report()
        
        if report["status"] in ["critical", "emergency"]:
            print_syntax_report(report)
            print("❌ COMMIT BLOCKED: Mass syntax breakage detected!")
            print("Fix syntax errors before committing.")
            sys.exit(1)
        elif report["status"] == "warning":
            print("⚠️ Warning: Elevated syntax errors detected.")
            print("Consider running: .venv/bin/ruff check --fix")
            # Allow commit but warn
            sys.exit(0)
        else:
            # All good
            sys.exit(0)
    else:
        # Regular monitoring mode
        report = create_syntax_report()
        print_syntax_report(report)
        save_syntax_report(report)
        
        # Exit with status code for CI integration
        if report["status"] == "emergency":
            sys.exit(2)
        elif report["status"] == "critical":
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()