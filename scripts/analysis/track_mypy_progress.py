#!/usr/bin/env python3
"""
Mypy Error Progress Tracker
Quick script to check current mypy error status and compare with enumeration
"""

import json
import subprocess
import sys
from pathlib import Path


def load_enumeration():
    """Load the error enumeration file"""
    try:
        with open("mypy_errors_enumeration.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ mypy_errors_enumeration.json not found")
        return None


def run_mypy_check():
    """Run mypy and get current error count"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", ".", "--show-error-codes", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            cwd=Path("."),
        )

        # Count errors (rough estimate)
        error_lines = [line for line in result.stdout.split("\n") if ": error:" in line]
        return len(error_lines), result.stdout
    except Exception as e:
        print(f"❌ Error running mypy: {e}")
        return 0, ""


def main():
    """Main progress tracking function"""
    print("📊 Mypy Error Progress Tracker")
    print("=" * 50)

    # Load enumeration
    enumeration = load_enumeration()
    if not enumeration:
        return

    original_errors = enumeration["metadata"]["total_errors"]
    print(f"🎯 Original Error Count: {original_errors}")

    # Get current status
    current_errors, mypy_output = run_mypy_check()
    print(f"📈 Current Error Count: {current_errors}")

    # Calculate progress
    if original_errors > 0:
        reduction = original_errors - current_errors
        percent_reduction = (reduction / original_errors) * 100
        print(f"✅ Errors Fixed: {reduction}")
        print(f"📊 Progress: {percent_reduction:.1f}%")

        # Task status
        total_tasks = enumeration["metadata"]["total_tasks"]
        print(f"📋 Total Tasks: {total_tasks}")

        # Show top priority files
        print("\n🔥 TOP PRIORITY FILES:")
        for i, file_info in enumerate(enumeration["summary"]["files_by_error_count"][:5], 1):
            print(f"   {i}. {file_info['file']} - {file_info['errors']} errors ({file_info['critical']} critical)")

        # Agent assignments
        print("\n🤖 AGENT ASSIGNMENTS:")
        for agent, tasks in enumeration["agent_assignments"].items():
            task_count = len(tasks)
            print(f"   {agent}: {task_count} task(s)")

        print("\n📝 COMPLETION CRITERIA:")
        for criterion in enumeration["completion_criteria"]["per_task"]:
            print(f"   • {criterion}")

        print("\n💡 NEXT STEPS:")
        print("   1. Assign tasks to agents based on specialization")
        print("   2. Each agent works on their assigned files")
        print("   3. Run this tracker regularly to monitor progress")
        print("   4. Update enumeration.json as tasks complete")


if __name__ == "__main__":
    main()