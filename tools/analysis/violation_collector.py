#!/usr/bin/env python3
"""
LUKHAS Violation Collector
==========================

Collects and processes lint violations to supplement the Code Atlas.
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def collect_violations():
    """Collect violations in manageable chunks."""
    violations = defaultdict(list)
    
    # Get violations in text format and parse
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", ".", "--no-cache"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.stdout:
            # Parse text format violations
            lines = result.stdout.strip().split("\n")
            current_violation = {}
            
            for line in lines:
                # Match file:line:col: CODE message pattern
                match = re.match(r"^([^:]+):(\d+):(\d+):\s+(\w+)\s+(.+)", line)
                if match:
                    filename, line_no, col, code, message = match.groups()
                    
                    violation = {
                        "filename": filename,
                        "location": {"row": int(line_no), "column": int(col)},
                        "code": code,
                        "message": message,
                        "rule_description": get_rule_description(code)
                    }
                    
                    violations[code].append(violation)
        
        # Also try JSON format for some directories
        focus_dirs = ["lukhas", "candidate", "consciousness", "core"]
        for focus_dir in focus_dirs:
            if Path(focus_dir).exists():
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "ruff", "check", focus_dir, "--format=json"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.stdout:
                        json_violations = json.loads(result.stdout)
                        for violation in json_violations:
                            code = violation.get("code", "UNKNOWN")
                            violations[code].append(violation)
                            
                except Exception as e:
                    print(f"Error collecting JSON violations from {focus_dir}: {e}")
        
        return violations
        
    except subprocess.TimeoutExpired:
        print("⚠️ Violation collection timeout")
        return violations
    except Exception as e:
        print(f"⚠️ Error collecting violations: {e}")
        return violations


def get_rule_description(code):
    """Get description for ruff rule code."""
    descriptions = {
        "B007": "Loop control variable not used within loop body",
        "PERF102": "When using only dict values, use values() method",
        "ARG001": "Unused function argument",
        "ARG002": "Unused method argument",
        "F821": "Undefined name",
        "F401": "Unused import",
        "RUF006": "Dangling async task",
        "B006": "Mutable default argument",
        "DTZ005": "Naive datetime usage",
        "DTZ003": "datetime.utcnow() usage", 
        "E402": "Module level import not at top",
        "F841": "Unused local variable",
        "F811": "Redefinition of unused name",
        "UP032": "Use f-string instead of format call",
        "E501": "Line too long",
        "W291": "Trailing whitespace"
    }
    return descriptions.get(code, f"Rule {code}")


def generate_violation_indices(violations):
    """Generate per-rule indices."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    indices_created = 0
    for rule_code, rule_violations in violations.items():
        if rule_violations:
            index_file = reports_dir / f"idx_{rule_code}.json"
            
            # Remove duplicates
            unique_violations = []
            seen = set()
            for violation in rule_violations:
                key = f"{violation.get('filename', '')}:{violation.get('location', {}).get('row', 0)}"
                if key not in seen:
                    seen.add(key)
                    unique_violations.append(violation)
            
            rule_index = {
                "rule_code": rule_code,
                "description": get_rule_description(rule_code),
                "total_violations": len(unique_violations),
                "violations": unique_violations,
                "affected_files": list(set(v.get("filename", "") for v in unique_violations)),
                "lukhas_files": [f for f in set(v.get("filename", "") for v in unique_violations) 
                               if "lukhas/" in f or "candidate/" in f],
                "severity": get_severity(rule_code)
            }
            
            with open(index_file, "w") as f:
                json.dump(rule_index, f, indent=2)
            
            indices_created += 1
            print(f"📄 Created idx_{rule_code}.json: {len(unique_violations)} violations")
    
    return indices_created


def get_severity(rule_code):
    """Get severity level for rule code."""
    high_severity = {"F821", "F401", "RUF006", "B006", "DTZ005"}
    medium_severity = {"ARG001", "ARG002", "E402", "F841", "F811"}
    
    if rule_code in high_severity:
        return "high"
    elif rule_code in medium_severity:
        return "medium"
    else:
        return "low"


def update_atlas_with_violations(violations):
    """Update the code atlas with violation information."""
    atlas_file = Path("reports/code_atlas.json")
    
    if atlas_file.exists():
        with open(atlas_file) as f:
            atlas = json.load(f)
        
        # Update metadata
        total_violations = sum(len(v) for v in violations.values())
        atlas["metadata"]["total_violations"] = total_violations
        atlas["metadata"]["violation_types"] = list(violations.keys())
        
        # Add violations summary
        atlas["violations_by_rule"] = {k: len(v) for k, v in violations.items()}
        
        # Add severity breakdown
        severity_breakdown = defaultdict(int)
        for rule_code, rule_violations in violations.items():
            severity = get_severity(rule_code)
            severity_breakdown[severity] += len(rule_violations)
        atlas["violations_by_severity"] = dict(severity_breakdown)
        
        # Save updated atlas
        with open(atlas_file, "w") as f:
            json.dump(atlas, f, indent=2)
        
        print(f"✅ Updated code_atlas.json with {total_violations} violations")
        return True
    else:
        print("⚠️ Code atlas not found")
        return False


def main():
    print("🔍 LUKHAS Violation Collector")
    print("=" * 40)
    
    # Collect violations
    print("📊 Collecting lint violations...")
    violations = collect_violations()
    
    total_violations = sum(len(v) for v in violations.values())
    print(f"📋 Found {total_violations} violations across {len(violations)} rule types")
    
    if violations:
        # Generate indices
        print("📊 Generating per-rule indices...")
        indices_created = generate_violation_indices(violations)
        
        # Update atlas
        print("📋 Updating code atlas...")
        update_atlas_with_violations(violations)
        
        # Print summary
        print("\n🎉 Violation Collection Complete!")
        print(f"   • {total_violations} total violations")
        print(f"   • {len(violations)} different rule types")
        print(f"   • {indices_created} index files created")
        
        # Show top violation types
        sorted_violations = sorted(violations.items(), key=lambda x: len(x[1]), reverse=True)
        print(f"   • Top violations: {', '.join([f'{k}({len(v)})' for k, v in sorted_violations[:10]])}")
    else:
        print("⚠️ No violations found")


if __name__ == "__main__":
    main()
