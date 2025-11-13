#!/usr/bin/env python3
"""Quick fix for critical syntax errors and remaining RUF012 violations."""

import re
from pathlib import Path

def fix_syntax_errors():
    """Fix critical syntax errors in various files."""
    fixes = [
        # Fix broken dictionaries in tools
        {
            "file": "tools/ci/f821_scan.py",
            "pattern": r'    "Optional": "from typing import Optional"\n    "List": "from typing import",',
            "replacement": r'    "Optional": "from typing import Optional",\n    "List": "from typing import List",',
        },
        {
            "file": "tools/ci/f821_scan.py", 
            "pattern": r'    "Union": "from typing import Union"\n    "Tuple": "from typing import",',
            "replacement": r'    "Union": "from typing import Union",\n    "Tuple": "from typing import Tuple",',
        },
        # Fix comprehensive f821 eliminator
        {
            "file": "tools/analysis/comprehensive_f821_eliminator.py",
            "pattern": r'"Optional": "from typing import Optional"\n            "lukhas_pb2": "import lukhas_pb2",',
            "replacement": r'"Optional": "from typing import Optional",\n            "lukhas_pb2": "import lukhas_pb2",',
        },
        # Fix broken test file indentation
        {
            "file": "tests/e2e/test_core_components_comprehensive.py",
            "pattern": r"# Skip experimental aka_qualia tests\npytestmark = pytest.mark.skip\(reason=\"aka_qualia is experimental\"\)\n\n            # Check that project root is in path",
            "replacement": r"# Skip experimental aka_qualia tests\npytestmark = pytest.mark.skip(reason=\"aka_qualia is experimental\")\n\ndef check_project_root():\n    try:\n        # Check that project root is in path",
        },
        # Fix broken import in products test
        {
            "file": "tests/unit/products_infra/legado/test_lambda_governor_quantum.py",
            "pattern": r"from products.infrastructure.legado.legacy_systems.governor.lambda_governor import \(\nfrom typing import ClassVar, List, Tuple\n    EscalationPriority,",
            "replacement": r"from typing import ClassVar, List, Tuple\n\nfrom products.infrastructure.legado.legacy_systems.governor.lambda_governor import (\n    EscalationPriority,",
        },
        # Fix broken import in qi test
        {
            "file": "tests/unit/qi/test_privacy_statement.py",
            "pattern": r"from qi.compliance.privacy_statement import \(\nfrom typing import ClassVar, List\n    Jurisdiction,",
            "replacement": r"from typing import ClassVar, List\n\nfrom qi.compliance.privacy_statement import (\n    Jurisdiction,",
        },
    ]

    for fix in fixes:
        file_path = Path(fix["file"])
        if file_path.exists():
            try:
                content = file_path.read_text()
                if fix["pattern"] in content:
                    content = content.replace(fix["pattern"], fix["replacement"])
                    file_path.write_text(content)
                    print(f"✅ Fixed syntax in {fix['file']}")
            except Exception as e:
                print(f"❌ Error fixing {fix['file']}: {e}")

def fix_remaining_ruf012():
    """Fix the actual remaining RUF012 violations."""
    # Get current RUF012 violations
    import subprocess

    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", "--select", "RUF012", "--no-fix", "."],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print("🎉 No RUF012 violations found!")
            return

        violations = []
        lines = result.stdout.split('\n')
        current_file = None

        for line in lines:
            if 'RUF012' in line and '-->' in line:
                # Extract file and line number
                parts = line.split('-->')
                if len(parts) > 1:
                    location = parts[1].strip()
                    if ':' in location:
                        file_path, line_num = location.split(':')[:2]
                        violations.append((file_path.strip(), int(line_num)))

        print(f"Found {len(violations)} RUF012 violations to fix:")

        for file_path, line_num in violations:
            print(f"  {file_path}:{line_num}")
            fix_ruf012_in_file(file_path, line_num)

    except Exception as e:
        print(f"Error getting RUF012 violations: {e}")

def fix_ruf012_in_file(file_path: str, line_num: int):
    """Fix specific RUF012 violation in a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return

        lines = path.read_text().splitlines()

        # Check if ClassVar import exists
        has_classvar_import = any("from typing import" in line and "ClassVar" in line for line in lines)

        if line_num <= len(lines):
            target_line = lines[line_num - 1]

            # Common patterns to fix
            patterns = [
                # json_schema_extra pattern
                (r'(\s+)(json_schema_extra)\s*:\s*(.*?)\s*=\s*{', r'\1\2: ClassVar[dict] = {'),
                # List/dict/set without ClassVar
                (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(List\[.*?\]|list)\s*=', r'\1\2: ClassVar[\3] = '),
                (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(Dict\[.*?\]|dict)\s*=', r'\1\2: ClassVar[\3] = '),
                (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(Set\[.*?\]|set)\s*=', r'\1\2: ClassVar[\3] = '),
                # Plain mutable defaults
                (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([a-zA-Z_][a-zA-Z0-9_\[\],\s]*?)\s*=\s*(\[|\{)', r'\1\2: ClassVar[\3] = \4'),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, target_line):
                    new_line = re.sub(pattern, replacement, target_line)
                    if new_line != target_line:
                        lines[line_num - 1] = new_line

                        # Add ClassVar import if needed
                        if not has_classvar_import:
                            # Find first typing import to add ClassVar
                            for i, line in enumerate(lines):
                                if "from typing import" in line and not "ClassVar" in line:
                                    if line.strip().endswith(','):
                                        lines[i] = line.rstrip().rstrip(',') + ', ClassVar'
                                    else:
                                        lines[i] = line.rstrip() + ', ClassVar'
                                    has_classvar_import = True
                                    break

                            # If no typing import found, add one
                            if not has_classvar_import:
                                # Find good place to add import
                                insert_pos = 0
                                for i, line in enumerate(lines):
                                    if line.strip() and not line.startswith('#') and not line.startswith('"""'):
                                        insert_pos = i
                                        break
                                lines.insert(insert_pos, "from typing import ClassVar")

                        # Write fixed content
                        path.write_text('\n'.join(lines) + '\n')
                        print(f"  ✅ Fixed RUF012 in {file_path}:{line_num}")
                        return

        print(f"  ⚠️  Could not fix RUF012 in {file_path}:{line_num}")

    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")

if __name__ == "__main__":
    print("🔧 Fixing critical syntax errors and RUF012 violations...")

    # Step 1: Fix syntax errors
    print("\n1️⃣ Fixing syntax errors...")
    fix_syntax_errors()

    # Step 2: Fix remaining RUF012 violations
    print("\n2️⃣ Fixing remaining RUF012 violations...")
    fix_remaining_ruf012()

    print("\n✨ Done!")