#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


ΛBot PR Security Review Starter
==============================
Simple script to run the PR security review task directly.
Use this script to start the security review process manually
or through cron/launchd.

Created: 2025-07-02
Status: ACTIVE ✅
"""

import os
import subprocess
import sys
from datetime import datetime


def run_security_review():
    """Run the security review task"""
    print(f"[{datetime.now().isoformat()}] Starting PR Security Review")

    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "pr_security_review_task.py"
    )

    try:
        # Run the script
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[{datetime.now().isoformat()}] PR Security Review completed successfully")
            print(result.stdout)
        else:
            print(
                f"[{datetime.now().isoformat()}] PR Security Review failed with code {result.returncode}"
            )
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error running PR Security Review: {e}")


if __name__ == "__main__":
    run_security_review()
