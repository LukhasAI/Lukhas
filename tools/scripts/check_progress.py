#!/usr/bin/env python3
"""
Check linting progress and provide summary
"""
import time
import streamlit as st

import subprocess
import sys
from pathlib import Path


def check_directory(directory: str) -> int:
    """Check issues in a directory"""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "flake8",
                directory,
                "--max-line-length=88",
                "--extend-ignore=E203,E501,W503,W291,W293,F401,F403",
                "--exclude=.venv,venv,__pycache__,test_metadata",
                "--count",
                "--exit-zero",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse the count from output
        lines = result.stdout.strip().split("\n")
        if lines and lines[-1].isdigit():
            return int(lines[-1])
        return 0
    except BaseException:
        return -1


def main():
    """Check progress across key directories"""
    print("🔍 Checking Linting Progress")
    print("=" * 60)

    directories = {
        "bridge/llm_wrappers": "LLM Wrappers",
        "lukhas": "LUKHAS  Core",
        "bridge/api": "Bridge API",
        "serve": "Serve Module",
        "tests": "Tests",
        "tools": "Tools",
    }

    total_issues = 0
    results = []

    for dir_path, name in directories.items():
        if Path(dir_path).exists():
            count = check_directory(dir_path)
            if count >= 0:
                total_issues += count
                status = "✅" if count < 10 else "⚠️" if count < 50 else "❌"
                results.append((name, count, status))
                print(f"{status} {name:25} {count:5} issues")
            else:
                print(f"⏭️  {name:25} skipped (timeout)")

    print("=" * 60)
    print(f"📊 Total Issues: {total_issues}")

    if total_issues < 100:
        print("🎉 Excellent! Very few issues remaining.")
    elif total_issues < 500:
        print("✅ Good progress! Most critical issues fixed.")
    else:
        print("⚠️ More work needed, but significant improvement made.")

    print("\n📝 Recommendations:")
    if total_issues > 0:
        print("1. Run 'make fix' to handle remaining auto-fixable issues")
        print("2. Use 'git diff' to review all changes")
        print("3. Run 'make test' to ensure nothing broke")
        print("4. Commit when satisfied: git add -A && git commit -m 'Fix linting'")
    else:
        print("✨ All clear! Ready to commit.")


if __name__ == "__main__":
    main()
