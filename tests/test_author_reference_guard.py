#!/usr/bin/env python3
"""
Test for Author Reference Guard

Ensures the guard properly validates content and blocks author references.
"""

import subprocess
import sys
from pathlib import Path


def test_author_reference_guard_detects_existing_violations():
    """Run the guard on current repo; expect violations to be detected"""
    result = subprocess.run(
        [sys.executable, "enforcement/tone/author_reference_guard.py"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
        check=False,
    )
    out = (result.stdout + "\n" + result.stderr).strip()
    # Expect violations in current repo state - should exit with code 1
    assert result.returncode == 1, f"Guard should detect existing violations:\n{out}"
    assert "violations:" in out, "Should report violations"


def test_author_reference_guard_detects_violations():
    """Test that guard properly detects violations in problematic content"""
    # Create a temporary test file with violations in the current directory (not tests/)
    test_file = Path(__file__).parent.parent / "temp_test_violations.md"
    try:
        with test_file.open("w", encoding="utf-8") as f:
            f.write("This text mentions Keats and Einstein in public context.")

        result = subprocess.run(
            [sys.executable, "enforcement/tone/author_reference_guard.py", str(test_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        # Debug output
        # print(f"Return code: {result.returncode}")
        # print(f"Stdout: {result.stdout}")
        # print(f"Stderr: {result.stderr}")

        # Should find violations and exit with code 1
        assert result.returncode == 1, (
            f"Guard should detect violations. Got code {result.returncode}, output: {result.stdout}"
        )
        assert "violations:" in result.stdout.lower(), "Should detect violations"

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def test_author_reference_guard_allows_academic():
    """Test that guard allows academic context content"""
    # Create a temporary academic test file
    test_file = Path("temp_test_academic.md")
    try:
        with test_file.open("w", encoding="utf-8") as f:
            f.write("""---
context: academic
---

This academic paper references Keats and Einstein with proper citations.
""")

        result = subprocess.run(
            [sys.executable, "enforcement/tone/author_reference_guard.py", str(test_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        # Should allow academic content and exit with code 0
        assert result.returncode == 0, (
            f"Guard should allow academic content:\n{result.stdout}\n{result.stderr}"
        )

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    test_author_reference_guard_detects_existing_violations()
    test_author_reference_guard_detects_violations()
    test_author_reference_guard_allows_academic()
    print("✅ All author reference guard tests passed!")
