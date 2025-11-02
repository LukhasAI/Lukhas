#!/usr/bin/env python3
"""
Comprehensive F821 Mass Elimination Script
Targets top violation patterns across entire LUKHAS codebase

Target patterns:
- 3213 timezone violations
- 427 st violations
- 368 log violations
- 236 VisualSymbol violations
- 66 VoiceSymbol violations
- 50 random violations
- Other high-frequency patterns

Surgical approach with syntax validation
"""

import ast
import re
import subprocess
from pathlib import Path


class ComprehensiveF821Eliminator:
    def __init__(self):
        self.fixes_applied = 0
        self.files_modified = 0
        self.errors = []

        # Target directories for processing
        self.target_dirs = ["branding/", "candidate/", "tools/", "products/", "matriz/", "next_gen/", "lukhas/"]

        # High-frequency import fixes
        self.import_fixes = {
            "timezone": "from datetime import timezone",
            "st": "import streamlit as st",
            "random": "import random",
            "time": "import time",
            "logging": "import logging",
            "VisualSymbol": "from core.symbolic import VisualSymbol",
            "VoiceSymbol": "from core.symbolic import VoiceSymbol",
            "Dict": "from typing import Dict",
            "List": "from typing import List",
            "Optional": "from typing import Optional",
            "lukhas_pb2": "import lukhas_pb2",
            "qi": "from consciousness.qi import qi",
            "QuantumCreativeComponent": "from quantum.creative import QuantumCreativeComponent",
        }

        # Logger pattern fixes
        self.logger_patterns = ["log", "logger"]

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip certain directories and files
        skip_patterns = ["__pycache__", ".git", "node_modules", "website_v1", ".venv", "venv", ".pytest_cache"]

        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False

        return file_path.suffix == ".py" and file_path.is_file()

    def analyze_file(self, file_path: Path) -> dict:
        """Analyze file for F821 violations that we can fix"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": str(e), "content": "", "violations": []}

        violations = []

        # Check for our target violations
        for violation_name in self.import_fixes:
            if violation_name in content and not self.has_import_for(content, violation_name):
                violations.append(violation_name)

        # Check for logger violations
        for logger_pattern in self.logger_patterns:
            if re.search(rf"\b{logger_pattern}\.(info|debug|warning|error|critical)\b", content):
                if not self.has_logger_definition(content):
                    violations.append("log_declaration")

        return {"content": content, "violations": violations, "error": None}

    def has_import_for(self, content: str, violation_name: str) -> bool:
        """Check if file already has appropriate import for violation"""
        import_patterns = {
            "timezone": [r"from datetime import.*timezone", r"import datetime.*timezone"],
            "st": [r"import streamlit", r"import streamlit as st"],
            "random": [r"import random"],
            "time": [r"import time"],
            "logging": [r"import logging"],
            "VisualSymbol": [r"from.*symbolic.*import.*VisualSymbol", r"from core.symbolic import.*VisualSymbol"],
            "VoiceSymbol": [r"from.*symbolic.*import.*VoiceSymbol", r"from core.symbolic import.*VoiceSymbol"],
            "Dict": [r"from typing import.*Dict"],
            "List": [r"from typing import.*List"],
            "Optional": [r"from typing import.*Optional"],
            "lukhas_pb2": [r"import lukhas_pb2"],
            "qi": [r"from.*qi.*import.*qi", r"from consciousness.qi import qi"],
            "QuantumCreativeComponent": [r"from.*quantum.*creative.*import.*QuantumCreativeComponent"],
        }

        patterns = import_patterns.get(violation_name, [])
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)

    def has_logger_definition(self, content: str) -> bool:
        """Check if file has logger definition"""
        logger_patterns = [
            r"log\s*=\s*logging\.getLogger",
            r"logger\s*=\s*logging\.getLogger",
            r"import logging.*log\s*=",
            r"log\s*=.*getLogger",
        ]

        return any(re.search(pattern, content) for pattern in logger_patterns)

    def fix_file(self, file_path: Path, analysis: dict) -> bool:
        """Apply fixes to a single file"""
        if analysis.get("error"):
            return False

        content = analysis["content"]
        violations = analysis["violations"]

        if not violations:
            return False

        original_content = content

        # Apply import fixes
        for violation in violations:
            if violation == "log_declaration":
                content = self.add_logger_declaration(content)
            elif violation in self.import_fixes:
                content = self.add_import_safely(content, self.import_fixes[violation])

        # Validate syntax
        if not self.validate_syntax(content):
            self.errors.append(f"Syntax validation failed for {file_path}")
            return False

        # Write back if changed
        if content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except Exception as e:
                self.errors.append(f"Error writing {file_path}: {e}")
                return False

        return False

    def add_import_safely(self, content: str, import_statement: str) -> str:
        """Add import statement safely"""
        lines = content.split("\n")

        # Check if import already exists
        for line in lines:
            if import_statement.strip() in line:
                return content

        # Find insertion point
        insert_idx = self.find_import_insertion_point(lines)
        lines.insert(insert_idx, import_statement)

        return "\n".join(lines)

    def add_logger_declaration(self, content: str) -> str:
        """Add logger declaration"""
        if self.has_logger_definition(content):
            return content

        lines = content.split("\n")

        # Add logging import if needed
        has_logging_import = any("import logging" in line for line in lines)
        if not has_logging_import:
            insert_idx = self.find_import_insertion_point(lines)
            lines.insert(insert_idx, "import logging")

        # Add logger declaration
        logger_line = "log = logging.getLogger(__name__)"

        # Find where to add logger (after imports, before main code)
        insert_idx = len(lines)
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith(("#", "import", "from")):
                insert_idx = i
                break

        lines.insert(insert_idx, logger_line)
        return "\n".join(lines)

    def find_import_insertion_point(self, lines: list[str]) -> int:
        """Find appropriate place to insert import"""
        # Skip shebang and encoding
        insert_idx = 0
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith("#") and ("coding" in line or "encoding" in line or line.startswith("#!")):
                insert_idx = i + 1

        # Skip docstring
        in_docstring = False
        for i in range(insert_idx, len(lines)):
            line = lines[i].strip()
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_idx = i + 1
                    break
            elif in_docstring:
                continue
            elif line.startswith(("import ", "from ")):
                insert_idx = max(insert_idx, i + 1)
            elif line and not line.startswith("#"):
                break

        return insert_idx

    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def process_directory(self, directory: Path):
        """Process all Python files in directory"""
        print(f"📂 Processing: {directory}")

        py_files = []
        for py_file in directory.rglob("*.py"):
            if self.should_process_file(py_file):
                py_files.append(py_file)

        for py_file in py_files:
            try:
                analysis = self.analyze_file(py_file)
                if analysis["violations"] and self.fix_file(py_file, analysis):
                    self.files_modified += 1
                    self.fixes_applied += len(analysis["violations"])
                    print(f"  ✅ {py_file.relative_to(directory.parent)}")

            except Exception as e:
                self.errors.append(f"Error processing {py_file}: {e}")

    def run_elimination(self):
        """Run comprehensive F821 elimination"""
        print("🎯 LUKHAS Comprehensive F821 Elimination")
        print("=" * 60)

        # Get baseline count
        print("📊 Getting baseline F821 count...")
        try:
            result = subprocess.run(
                [".venv/bin/ruff", "check", ".", "--select=F821", "--statistics"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            baseline_count = 0
            for line in result.stdout.split("\n"):
                if "F821" in line and "undefined-name" in line:
                    baseline_count = int(line.split()[0])
                    break

            print(f"📈 Baseline F821 violations: {baseline_count}")
        except Exception as e:
            baseline_count = 0
            print("⚠️ Could not get baseline count")

        print("\n🎯 Target patterns:")
        for pattern, import_fix in self.import_fixes.items():
            print(f"   {pattern}: {import_fix}")

        # Process each target directory
        for dir_name in self.target_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                self.process_directory(dir_path)

        print("\n✅ ELIMINATION COMPLETE!")
        print(f"📁 Files modified: {self.files_modified}")
        print(f"🔧 Fixes applied: {self.fixes_applied}")

        if self.errors:
            print(f"\n⚠️ Errors: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"   {error}")

        # Get final count
        print("\n📊 Getting final F821 count...")
        try:
            result = subprocess.run(
                [".venv/bin/ruff", "check", ".", "--select=F821", "--statistics"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            final_count = 0
            for line in result.stdout.split("\n"):
                if "F821" in line and "undefined-name" in line:
                    final_count = int(line.split()[0])
                    break

            reduction = baseline_count - final_count
            print(f"📊 Final F821 violations: {final_count}")
            print(f"📉 Total reduction: {reduction}")

            if reduction >= 1500:
                print("🎯 TARGET ACHIEVED! Reduced by 1,500+ violations")
            elif reduction >= 1000:
                print("✅ GOOD PROGRESS! Significant reduction achieved")

        except Exception as e:
            print("⚠️ Could not get final count")


def main():
    eliminator = ComprehensiveF821Eliminator()
    eliminator.run_elimination()


if __name__ == "__main__":
    main()
