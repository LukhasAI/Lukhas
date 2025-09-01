#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


ΛBot PR Security Review Validator
===============================
Validates that the PR security review system is working correctly
and that all PRs with security issues are being reviewed.

Created: 2025-07-02
Status: VALIDATION TOOL ✅
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


def validate_pr_security_review():
    """Validate that the PR security review system is working"""
    print("=" * 60)
    print("ΛBot PR Security Review Validation")
    print("=" * 60)

    # Check if the PR security review log exists
    log_file = Path("/Users/A_G_I/Lukhas/pr_security_review.log")
    if not log_file.exists():
        print("❌ PR security review log not found!")
        print("   The system may not be running yet.")
        return

    # Check for recent log entries
    log_content = log_file.read_text()
    log_entries = log_content.strip().split("\n")

    if not log_entries:
        print("❌ PR security review log is empty!")
        return

    # Check the most recent log entry
    last_entry = log_entries[-1]
    try:
        # Extract the timestamp
        timestamp_str = last_entry.split(" - ")[0]
        timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Z %Y")

        # Check if the last entry is recent (within the last 24 hours)
        if datetime.now() - timestamp < timedelta(hours=24):
            print("✅ PR security review ran recently:")
            print(f"   Last run: {timestamp_str}")
        else:
            print("⚠️ PR security review hasn't run recently:")
            print(f"   Last run: {timestamp_str}")
    except Exception as e:
        print(f"❌ Error parsing log entry: {e}")

    # Check for detailed report files
    report_files = list(Path("/Users/A_G_I/Lukhas").glob("pr_security_review_*.json"))
    if report_files:
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        print(f"✅ Found {len(report_files)} report files")
        print(f"   Latest report: {latest_report.name}")

        # Parse the latest report
        try:
            with open(latest_report) as f:
                report_data = json.load(f)

            summary = report_data.get("summary", {})

            print("\nSummary from latest report:")
            print(f"- Repositories processed: {summary.get('repositories_processed', 0)}")
            print(f"- PRs scanned: {summary.get('stats', {}).get('prs_scanned', 0)}")
            print(f"- Security issues found: {summary.get('stats', {}).get('security_issues_found', 0)}")
            print(f"- Security PRs identified: {summary.get('total_security_prs', 0)}")
            print(f"- Critical security PRs: {summary.get('critical_security_prs', 0)}")
            print(f"- PRs reviewed: {summary.get('stats', {}).get('prs_reviewed', 0)}")

            unresolved = summary.get("total_security_prs", 0) - summary.get("stats", {}).get("prs_reviewed", 0)

            if unresolved == 0:
                print("✅ All security PRs have been reviewed!")
            else:
                print(f"⚠️ {unresolved} security PRs still need review")

            # Check if we've addressed the 264 security issues
            if summary.get("stats", {}).get("security_issues_found", 0) >= 264:
                issues_fixed = summary.get("stats", {}).get("security_issues_fixed", 0)
                issues_remaining = 264 - issues_fixed

                if issues_remaining <= 0:
                    print("✅ All 264 security issues have been addressed!")
                else:
                    print(f"⚠️ {issues_remaining} of 264 security issues still need to be addressed")

        except Exception as e:
            print(f"❌ Error parsing report: {e}")
    else:
        print("❌ No report files found!")

    # Check if the LaunchAgent is running
    try:
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)

        if "com.agi.lambda_bot_pr_security_review" in result.stdout:
            print("\n✅ PR security review LaunchAgent is active")
        else:
            print("\n❌ PR security review LaunchAgent is not running!")
    except Exception as e:
        print(f"\n❌ Error checking LaunchAgent status: {e}")

    print("\nRecommended actions:")
    print("1. If the system isn't running, run the setup script:")
    print("   /Users/A_G_I/Lukhas/setup_pr_security_review.sh")
    print("2. If needed, manually run the PR security review:")
    print("   /Users/A_G_I/Lukhas/run_pr_security_review.sh")
    print("3. Check the logs for errors:")
    print("   cat /Users/A_G_I/Lukhas/pr_security_review.log")
    print("=" * 60)


if __name__ == "__main__":
    validate_pr_security_review()
