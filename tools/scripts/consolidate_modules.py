#!/usr/bin/env python3
"""
🔧 Module Consolidation Script
=============================
Updates modules to use common utilities from core.common
"""

import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ModuleConsolidator:
    """Consolidates duplicate code by updating imports"""

    def __init__(self):
        self.files_updated = 0
        self.imports_replaced = 0
        self.logger_inits_replaced = 0
        self.decorators_replaced = 0

    def update_file(self, file_path: Path) -> bool:
        """Update a single file to use common utilities"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Update imports
            content = self._update_imports(content)

            # Update logger initialization
            content = self._update_logger_init(content)

            # Update decorator usage
            content = self._update_decorators(content)

            # Update exception usage
            content = self._update_exceptions(content)

            # Update GLYPH handling
            content = self._update_glyph_handling(content)

            # Only write if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.files_updated += 1
                return True

            return False

        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False

    def _update_imports(self, content: str) -> str:
        """Update imports to use common utilities"""
        lines = content.split("\n")
        new_lines = []
        imports_added = set()

        for line in lines:
            # Skip if already importing from core.common
            if "from core.common" in line:
                new_lines.append(line)
                continue

            # Replace logging imports
            if re.match(r"^import logging", line):
                if "logger" not in imports_added:
                    new_lines.append("from core.common import get_logger")
                    imports_added.add("logger")
                    self.imports_replaced += 1
                continue

            # Replace custom logger factories
            if "get_logger" in line and "core.common" not in line:
                if "logger" not in imports_added:
                    new_lines.append("from core.common import get_logger")
                    imports_added.add("logger")
                    self.imports_replaced += 1
                continue

            # Replace retry decorators
            if re.search(r"def retry\(|from .+ import retry", line):
                if "decorators" not in imports_added:
                    new_lines.append("from core.common import retry, with_timeout")
                    imports_added.add("decorators")
                    self.imports_replaced += 1
                continue

            # Replace custom exceptions
            if re.search(
                r"class .+Error\(Exception\):|GuardianRejection|MemoryDrift", line
            ):
                if "exceptions" not in imports_added:
                    new_lines.append("from core.common import LukhasError, GuardianRejectionError,
                                     MemoryDriftError"
                                     )
                    imports_added.add("exceptions")
                    self.imports_replaced += 1

            new_lines.append(line)

        return "\n".join(new_lines)

    def _update_logger_init(self, content: str) -> str:
        """Update logger initialization patterns"""
        # Pattern 1: logging.getLogger(__name__)
        content = re.sub(
            r"logger\s*=\s*logging\.getLogger\(__name__\)",
            "logger = get_logger(__name__)",
            content,
        )

        # Pattern 2: Custom logger factory
        content = re.sub(
            r"logger\s*=\s*\w+\.get_logger\(([^)]+)\)",
            r"logger = get_logger(\1)",
            content,
        )

        # Count replacements
        if "logger = get_logger" in content:
            self.logger_inits_replaced += content.count("logger = get_logger")

        return content

    def _update_decorators(self, content: str) -> str:
        """Update decorator usage"""
        # Update lukhas_tier_required
        content = re.sub(
            r"@\w+\.lukhas_tier_required", "@lukhas_tier_required", content
        )

        # Update retry decorator
        content = re.sub(r"@\w+\.retry", "@retry", content)

        # Update with_timeout decorator
        content = re.sub(r"@\w+\.with_timeout", "@with_timeout", content)

        # Count replacements
        for decorator in ["@retry", "@with_timeout", "@lukhas_tier_required"]:
            if decorator in content:
                self.decorators_replaced += content.count(decorator)

        return content

    def _update_exceptions(self, content: str) -> str:
        """Update exception usage"""
        # Replace custom Guardian exceptions
        content = re.sub(
            r"raise \w+GuardianRejection\(", "raise GuardianRejectionError(", content
        )

        # Replace custom Memory exceptions
        content = re.sub(r"raise \w+MemoryDrift\(", "raise MemoryDriftError(", content)

        # Replace base exception classes
        content = re.sub(
            r"class (\w+Error)\(Exception\):", r"class \1(LukhasError):", content
        )

        return content

    def _update_glyph_handling(self, content: str) -> str:
        """Update GLYPH token handling"""
        # Add import if GLYPH is used
        if (
            "GLYPH" in content
            and "from core.common import" in content
            and "GLYPHToken" not in content
        ):
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "from core.common import" in line:
                    lines[i] = line.rstrip() + ", GLYPHToken, create_glyph"
                    break
            content = "\n".join(lines)

        # Replace custom GLYPH classes
        content = re.sub(
            r"class GLYPH\w*Token[:\(]", "class CustomGLYPHToken(GLYPHToken):", content
        )

        return content


def update_module_base_classes(root_path: Path) -> None:
    """Update modules to inherit from BaseModule"""
    base_class_updates = []

    for py_file in root_path.rglob("*.py"):
        if "__pycache__" in str(py_file) or "archive" in str(py_file):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Look for module-like classes
            if re.search(r"class \w+Module\(.*\):", content):
                # Check if not already inheriting from BaseModule
                if "BaseModule" not in content:
                    base_class_updates.append(py_file)

        except Exception:
            pass

    # Report findings
    if base_class_updates:
        print("\n📋 Modules that could inherit from BaseModule:")
        for file in base_class_updates[:10]:
            print(f"   • {file.relative_to(root_path)}")
        if len(base_class_updates) > 10:
            print(f"   ... and {len(base_class_updates) - 10} more")


def main():
    """Main consolidation function"""
    print("🔧 Module Consolidation Script")
    print("=" * 60)

    consolidator = ModuleConsolidator()

    # Target modules for consolidation
    modules = [
        "consciousness",
        "memory",
        "reasoning",
        "governance",
        "orchestration",
        "identity",
        "quantum",
        "bio",
        "emotion",
        "creativity",
        "bridge",
        "security",
        "api",
        "vivox",
    ]

    print("\n📝 Updating modules to use common utilities...")

    for module in modules:
        module_path = PROJECT_ROOT / module
        if not module_path.exists():
            continue

        print(f"\n   Processing {module}...")
        module_files = list(module_path.rglob("*.py"))

        for py_file in module_files:
            if "__pycache__" in str(py_file):
                continue

            consolidator.update_file(py_file)

    # Report results
    print("\n📊 Consolidation Results:")
    print(f"   Files updated: {consolidator.files_updated}")
    print(f"   Imports replaced: {consolidator.imports_replaced}")
    print(f"   Logger inits updated: {consolidator.logger_inits_replaced}")
    print(f"   Decorators updated: {consolidator.decorators_replaced}")

    # Check for base class updates
    update_module_base_classes(PROJECT_ROOT)

    # Create example migration
    print("\n💡 Example Module Migration:")
    print(
        """
Before:
```python
import logging
logger = logging.getLogger(__name__)

def retry(max_attempts=3):
    # Custom retry implementation
    ...

@retry()

def process_data():
    ...
```

After:
```python
from core.common import get_logger, retry

logger = get_logger(__name__)

@retry(max_attempts=3)

def process_data():
    ...
```
    """
    )

    print("\n✅ Consolidation complete!")
    print("\nNext steps:")
    print("1. Run tests to ensure functionality is preserved")
    print("2. Update modules to inherit from BaseModule where appropriate")
    print("3. Remove old duplicate implementations")


if __name__ == "__main__":
    main()
