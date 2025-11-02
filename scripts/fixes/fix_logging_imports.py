#!/usr/bin/env python3
"""Fix logging imports in MΛTRIZ consciousness modules to avoid conflicts.

Ensures consciousness packages use an explicit alias to avoid collisions
with the candidate/core/logging directory.
"""

import logging
import re
from pathlib import Path


logger = logging.getLogger(__name__)


def fix_logging_in_file(file_path: Path):
    """Fix logging import in a single file"""
    content = file_path.read_text()

    # Replace simple logging import
    if "import logging\n" in content and "import logging as std_logging" not in content:
        content = content.replace(
            "import logging\n",
            "# Explicit logging import to avoid conflicts with candidate/core/logging\nimport logging as std_logging\n",
        )

        # Replace logger creation
        content = re.sub(
            r"logger = logging\.getLogger\(__name__\)", "logger = std_logging.getLogger(__name__)", content
        )

        # Replace other logging references if needed
        content = re.sub(r"logging\.error\(", "std_logging.error(", content)
        content = re.sub(r"logging\.warning\(", "std_logging.warning(", content)
        content = re.sub(r"logging\.info\(", "std_logging.info(", content)
        content = re.sub(r"logging\.debug\(", "std_logging.debug(", content)

        file_path.write_text(content)
        print(f"Fixed logging imports in: {file_path}")
        return True

    return False


def main():
    """Fix logging imports in all MΛTRIZ modules"""
    base_path = Path("candidate/core")
    matriz_files = [
        "consciousness/matriz_consciousness_state.py",
        "consciousness/matriz_consciousness_orchestrator.py",
        "orchestration/matriz_consciousness_coordinator.py",
        "identity/matriz_consciousness_identity.py",
        "governance/matriz_consciousness_governance.py",
        "symbolic_core/matriz_symbolic_consciousness.py",
        "matriz_integrated_demonstration.py",
    ]

    fixed_count = 0
    for file_path_str in matriz_files:
        file_path = base_path / file_path_str
        if file_path.exists():
            if fix_logging_in_file(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\n✅ Fixed logging imports in {fixed_count} files")


if __name__ == "__main__":
    main()
