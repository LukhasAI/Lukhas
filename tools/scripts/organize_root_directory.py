#!/usr/bin/env python3
"""
Organize Root Directory
======================
Moves files from root to appropriate subdirectories.
"""

import shutil
from pathlib import Path


def organize_root():
    root = Path("/Users/agi_dev/Lukhas_PWM")

    # Create necessary directories
    (root / "tests" / "vivox").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "reports" / "vivox").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "analysis").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "planning").mkdir(parents=True, exist_ok=True)
    (root / "examples" / "vivox").mkdir(parents=True, exist_ok=True)

    # Define file movements
    movements = {
        # VIVOX test files -> tests/vivox/
        "test_vivox_*.py": "tests/vivox/",
        "vivox_*_test.py": "tests/vivox/",
        "test_state_variety.py": "tests/vivox/",
        # VIVOX reports -> docs/reports/vivox/
        "vivox_*.json": "docs/reports/vivox/",
        "vivox_*.md": "docs/reports/vivox/",
        "vivox_*.txt": "docs/reports/vivox/",
        "vivox_*.log": "docs/reports/vivox/",
        "vivox_*.png": "docs/reports/vivox/",
        "VIVOX_*.md": "docs/reports/vivox/",
        # VIVOX examples -> examples/vivox/
        "vivox_enhanced_example.py": "examples/vivox/",
        # Analysis reports -> docs/analysis/
        "*_ANALYSIS.md": "docs/analysis/",
        "*_REPORT.md": "docs/analysis/",
        "IMPLEMENTATION_STATUS_REPORT.md": "docs/analysis/",
        # Planning docs -> docs/planning/
        "RADICAL_SIMPLIFICATION_PLAN.md": "docs/planning/",
        "RECOVERY_PLAN.md": "docs/planning/",
        # Other test files -> tests/
        "test_math_formula.py": "tests/",
        "test_professional_architecture.py": "tests/",
        # Z_C files -> docs/
        "Z_C_*.md": "docs/",
    }

    # Execute movements
    for pattern, destination in movements.items():
        for file in root.glob(pattern):
            if file.is_file():
                dest_path = root / destination / file.name
                print(f"Moving {file.name} -> {destination}")
                shutil.move(str(file), str(dest_path))

    print("\n✅ Root directory organized!")


if __name__ == "__main__":
    organize_root()
