#!/usr/bin/env python3
"""
Guardian Exemption Ledger Audit Script
======================================

This script audits a Guardian exemption ledger (in JSON format) for compliance
with security policies. It checks for unauthorized exemptions, stale entries,
and missing justifications, then generates a structured JSON report.

This is a standalone tool designed for independent security audits and does
not use lukhas.* imports.

Task: SG010-R

Usage:
    python3 scripts/security/audit_guardian_exemptions.py <input_json_file> <output_json_file>

Example:
    python3 scripts/security/audit_guardian_exemptions.py test_data/guardian_exemptions_sample.json docs/security/exemption_audit_report.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

# Set up the path to allow for consistent script execution and potential reuse
# of other script utilities, following the pattern in other repository scripts.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.parent))

def load_exemptions(filepath: str) -> list[dict]:
    """Loads exemptions from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'", file=sys.stderr)
        sys.exit(1)

def is_unauthorized(exemption: dict) -> str | None:
    """Checks for unauthorized exemptions."""
    if not exemption.get("override_granted"):
        return None

    band = exemption.get("band")
    approver1 = exemption.get("approver1_id")
    approver2 = exemption.get("approver2_id")

    if band == "critical":
        if not approver1 or not approver2:
            return "Critical override missing one or both approvers."
        if approver1 == approver2:
            return "Critical override has the same approver for both slots."
    elif band in ["minor", "major", "high"]:
        if not approver1:
            return f"{band.capitalize()} override missing primary approver."
    return None

def is_stale(exemption: dict, audit_date: datetime.datetime) -> str | None:
    """Checks for stale exemptions."""
    stale_threshold = audit_date - datetime.timedelta(days=365)
    created_at_str = exemption.get("created_at")
    if created_at_str:
        created_at = datetime.datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        if created_at < stale_threshold:
            return f"Exemption is older than one year (created at {created_at_str})."
    return None

def has_missing_justification(exemption: dict) -> str | None:
    """Checks for missing justifications."""
    if exemption.get("override_granted") and not exemption.get("justification"):
        return "Override granted without a justification."
    return None

def run_audit(exemptions: list[dict], audit_date: datetime.datetime) -> dict:
    """Runs the audit and returns the findings in a structured dictionary."""
    findings = {
        "unauthorized": [],
        "stale": [],
        "missing_justification": [],
    }

    for ex in exemptions:
        finding_details = {"id": ex.get("id"), "plan_id": ex.get("plan_id")}

        if reason := is_unauthorized(ex):
            findings["unauthorized"].append({**finding_details, "reason": reason})

        if reason := is_stale(ex, audit_date):
            findings["stale"].append({**finding_details, "reason": reason})

        if reason := has_missing_justification(ex):
            findings["missing_justification"].append({**finding_details, "reason": reason})

    return findings

def generate_json_report(findings: dict, audit_date: datetime.datetime, total_audited: int) -> str:
    """Generates a structured JSON report of the audit findings."""
    report = {
        "audit_date": audit_date.isoformat(),
        "summary": {
            "total_exemptions_audited": total_audited,
            "unauthorized_exemptions": len(findings["unauthorized"]),
            "stale_entries": len(findings["stale"]),
            "missing_justification": len(findings["missing_justification"]),
        },
        "findings": findings,
    }
    return json.dumps(report, indent=2)

def write_report(report: str, filepath: str):
    """Writes the report to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(report)
        print(f"Audit report successfully written to '{filepath}'")
    except IOError as e:
        print(f"Error: Could not write report to '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to run the audit script."""
    parser = argparse.ArgumentParser(description="Guardian Exemption Ledger Audit Script.")
    parser.add_argument("input_file", help="Path to the input JSON file with exemption data.")
    parser.add_argument("output_file", help="Path to the output JSON file for the report.")
    args = parser.parse_args()

    exemptions_data = load_exemptions(args.input_file)
    audit_date = datetime.datetime.now(datetime.timezone.utc)
    audit_findings = run_audit(exemptions_data, audit_date)
    report_content = generate_json_report(audit_findings, audit_date, len(exemptions_data))
    write_report(report_content, args.output_file)

if __name__ == "__main__":
    main()
