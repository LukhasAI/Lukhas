#!/usr/bin/env python3
"""
🔧 PWM Import Fixer
==================
Automatically fixes common import issues in the LUKHAS PWM codebase.
"""

import ast
import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ImportFixer:
    """Fixes common import issues"""

    # Import mappings for moved/renamed modules
    IMPORT_MAPPINGS = {
        # lukhas. prefix removal
        "lukhas.core": "core",
        "lukhas.memory": "memory",
        "lukhas.consciousness": "consciousness",
        "lukhas.orchestration": "orchestration",
        "lukhas.governance": "governance",
        "lukhas.api": "api",
        "lukhas.bio": "bio",
        "lukhas.quantum": "quantum",
        "lukhas.reasoning": "reasoning",
        "lukhas.emotion": "emotion",
        "lukhas.creativity": "creativity",
        "lukhas.identity": "identity",
        "lukhas.bridge": "bridge",
        "lukhas.ethics": "ethics",
        "lukhas.security": "security",
        "lukhas.unified": "unified",
        "lukhas.vivox": "vivox",
        # Common typos and variations
        "lukhas_core": "core",
        "lukhas_memory": "memory",
        "LUKHAS.core": "core",
        "LUKHAS.memory": "memory",
        # Old structure to new
        "lukhas.common.logger": "core.logging",
        "lukhas.CORE.voice.voice_engine": "core.voice.voice_engine",
        "lukhas.CORE_INTEGRATION.orchestrator": "orchestration.orchestrator",
    }

    # Modules that should be commented out (not available)
    COMMENT_OUT_IMPORTS = {
        "edge_tts",
        "streamlit",
        "gradio",
        "discord",
        "telegram",
        "slack_sdk",
        "twilio",
        "sendgrid",
        "stripe",
        "paypal",
        "Bot_agi_core",
        "Bot_consciousness_monitor",
        "AGENT",
        "AID",
        "Agent_Logic_Architecture",
        "BIO_SYMBOLIC",
        "CORE",
        "DASHBOARD",
        "FILES_LIBRARY",
        "INTENT",
    }

    def __init__(self):
        self.files_fixed = 0
        self.imports_fixed = 0
        self.errors = []

    def fix_file(self, file_path: Path) -> bool:
        """Fix imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix imports using regex
            content = self._fix_imports_regex(content)

            # Fix imports using AST (more complex cases)
            try:
                content = self._fix_imports_ast(content, file_path)
            except SyntaxError:
                # If AST parsing fails, stick with regex fixes
                pass

            # Only write if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.files_fixed += 1
                return True

            return False

        except Exception as e:
            self.errors.append(f"{file_path}: {e}")
            return False

    def _fix_imports_regex(self, content: str) -> str:
        """Fix imports using regex patterns"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            fixed_line = line

            # Fix import statements
            if re.match(r"^\s*(from|import)\s+", line):
                # Apply mappings
                for old_module, new_module in self.IMPORT_MAPPINGS.items():
                    if old_module in line:
                        fixed_line = line.replace(old_module, new_module)
                        self.imports_fixed += 1
                        break

                # Comment out unavailable imports
                for module in self.COMMENT_OUT_IMPORTS:
                    if re.search(rf"\b{module}\b", line):
                        if not line.strip().startswith("#"):
                            fixed_line = (
                                f"# {line}  # TODO: Install or implement {module}"
                            )
                            self.imports_fixed += 1
                        break

            fixed_lines.append(fixed_line)

        return "\n".join(fixed_lines)

    def _fix_imports_ast(self, content: str, file_path: Path) -> str:
        """Fix imports using AST parsing for complex cases"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return content

        # Track changes
        changes = []

        # Analyze imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # Check for mappings
                for old_module, new_module in self.IMPORT_MAPPINGS.items():
                    if node.module.startswith(old_module):
                        new_name = node.module.replace(old_module, new_module, 1)
                        changes.append((node.lineno, node.module, new_name))

        # Apply changes in reverse order to maintain line numbers
        lines = content.split("\n")
        for lineno, old_name, new_name in sorted(changes, reverse=True):
            if 0 <= lineno - 1 < len(lines):
                lines[lineno - 1] = lines[lineno - 1].replace(old_name, new_name)
                self.imports_fixed += 1

        return "\n".join(lines)

    def create_missing_init_files(self) -> int:
        """Create missing __init__.py files"""
        created = 0

        # Common directories that should have __init__.py
        module_dirs = [
            "api",
            "architectures",
            "bio",
            "bridge",
            "consciousness",
            "core",
            "creativity",
            "emotion",
            "ethics",
            "governance",
            "identity",
            "memory",
            "orchestration",
            "quantum",
            "reasoning",
            "recovery",
            "security",
            "tests",
            "tools",
            "unified",
            "vivox",
        ]

        for module_dir in module_dirs:
            module_path = PROJECT_ROOT / module_dir
            if module_path.exists() and module_path.is_dir():
                # Check all subdirectories
                for subdir in module_path.rglob("*"):
                    if subdir.is_dir() and not subdir.name.startswith("."):
                        init_file = subdir / "__init__.py"
                        if not init_file.exists():
                            # Check if directory has Python files
                            py_files = list(subdir.glob("*.py"))
                            if py_files and not any(
                                f.name.startswith("test_") for f in py_files
                            ):
                                init_file.write_text(
                                    '"""Auto-generated __init__.py"""\n'
                                )
                                created += 1

        return created

    def fix_all_files(self) -> None:
        """Fix imports in all Python files"""
        # Get all Python files in active modules
        py_files = []
        for module_dir in [
            "api",
            "architectures",
            "bio",
            "bridge",
            "consciousness",
            "core",
            "creativity",
            "emotion",
            "ethics",
            "governance",
            "identity",
            "memory",
            "orchestration",
            "quantum",
            "reasoning",
            "recovery",
            "security",
            "tests",
            "tools",
            "unified",
            "vivox",
        ]:
            module_path = PROJECT_ROOT / module_dir
            if module_path.exists():
                py_files.extend(module_path.rglob("*.py"))

        # Fix each file
        for py_file in py_files:
            if "__pycache__" not in str(py_file):
                self.fix_file(py_file)

    def generate_requirements_additions(self) -> list[str]:
        """Generate list of packages that might need to be added to requirements.txt"""
        # Read current requirements
        req_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
        ]
        current_packages = set()

        for req_file in req_files:
            req_path = PROJECT_ROOT / req_file
            if req_path.exists():
                with open(req_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            package = line.split("==")[0].split(">=")[0].split("[")[0]
                            current_packages.add(package.lower())

        # Suggest additions
        suggested_packages = {
            "streamlit": "streamlit>=1.28.0",
            "gradio": "gradio>=4.0.0",
            "edge-tts": "edge-tts>=6.1.0",
            "discord.py": "discord.py>=2.3.0",
            "python-telegram-bot": "python-telegram-bot>=20.0",
            "slack-sdk": "slack-sdk>=3.23.0",
            "twilio": "twilio>=8.10.0",
            "sendgrid": "sendgrid>=6.10.0",
            "stripe": "stripe>=7.0.0",
            "transformers": "transformers>=4.36.0",
            "langchain": "langchain>=0.1.0",
            "pinecone-client": "pinecone-client>=2.2.0",
            "redis": "redis>=5.0.0",
            "aioredis": "aioredis>=2.0.0",
            "celery": "celery>=5.3.0",
            "dramatiq": "dramatiq>=1.15.0",
            "pydantic": "pydantic>=2.5.0",
            "sqlalchemy": "sqlalchemy>=2.0.0",
            "alembic": "alembic>=1.13.0",
        }

        additions = []
        for package, requirement in suggested_packages.items():
            if package not in current_packages:
                additions.append(requirement)

        return sorted(additions)


def main():
    """Main function"""
    print("🔧 PWM Import Fixer")
    print("=" * 60)

    fixer = ImportFixer()

    # Create missing __init__.py files
    print("\n📁 Creating missing __init__.py files...")
    created = fixer.create_missing_init_files()
    print(f"   Created {created} __init__.py files")

    # Fix import statements
    print("\n🔧 Fixing import statements...")
    fixer.fix_all_files()
    print(f"   Fixed {fixer.imports_fixed} imports in {fixer.files_fixed} files")

    # Show errors
    if fixer.errors:
        print(f"\n❌ Errors ({len(fixer.errors)}):")
        for error in fixer.errors[:10]:
            print(f"   • {error}")

    # Suggest package additions
    additions = fixer.generate_requirements_additions()
    if additions:
        print("\n📦 Suggested additions to requirements.txt:")
        for package in additions[:10]:
            print(f"   {package}")

        # Write suggestions to file
        suggestions_file = (
            PROJECT_ROOT / "docs" / "reports" / "SUGGESTED_REQUIREMENTS.txt"
        )
        suggestions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(suggestions_file, "w") as f:
            f.write("# Suggested package additions based on import analysis\n")
            f.write("# Add these to requirements.txt as needed\n\n")
            f.write("\n".join(additions))
        print(f"\n   Full list saved to: {suggestions_file.relative_to(PROJECT_ROOT)}")

    print("\n✅ Import fixing complete!")


if __name__ == "__main__":
    main()
