#!/usr/bin/env python3
"""
Fix critical missing imports in LUKHAS codebase.
Addresses F821 undefined name errors by adding proper imports.
"""

import re
from pathlib import Path

# Map of missing items to their proper imports
IMPORT_FIXES = {
    # Standard library
    "asyncio": "import asyncio",
    "timezone": "from datetime import timezone",
    "sqlalchemy": "import sqlalchemy",
    # Internal modules
    "VisionSymbolicVocabulary": "from symbolic.vocabularies.vision_vocabulary import VisionSymbolicVocabulary",
    "VoiceSymbolicVocabulary": "from symbolic.vocabularies.voice_vocabulary import VoiceSymbolicVocabulary",
    "BrandValidator": "from scripts.brand_validator import BrandValidator",
}

# Files that need specific fixes
FILE_FIXES = {
    "candidate/bridge/adapters/api_framework.py": ["asyncio"],
    "candidate/bridge/adapters/create_memory_fold_api.py": ["timezone"],
    "candidate/bridge/api/colony_endpoints.py": ["timezone"],
    "candidate/branding_bridge.py": ["BrandValidator"],
    "branding/vocabularies/vision_vocabulary.py": ["VisionSymbolicVocabulary"],
    "branding/vocabularies/vocabulary_creativity_engine.py": ["VisionSymbolicVocabulary"],
    "branding/vocabularies/voice_vocabulary.py": ["VoiceSymbolicVocabulary"],
    "candidate/aka_qualia/tests/test_memory_integration.py": ["sqlalchemy"],
}


def add_import_to_file(filepath: Path, import_statement: str):
    """Add import statement to file if not already present."""
    try:
        content = filepath.read_text()

        # Check if import already exists
        if import_statement in content:
            print(f"  ✓ Import already exists in {filepath}")
            return False

        # Find the best place to insert import
        lines = content.split("\n")

        # Find last import line
        last_import_idx = -1
        for idx, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_import_idx = idx

        # Insert after last import or after docstring
        if last_import_idx >= 0:
            insert_idx = last_import_idx + 1
        else:
            # Find end of module docstring if exists
            insert_idx = 0
            in_docstring = False
            for idx, line in enumerate(lines):
                if line.strip().startswith('"""'):
                    if not in_docstring:
                        in_docstring = True
                    else:
                        insert_idx = idx + 1
                        break

        # Insert the import
        lines.insert(insert_idx, import_statement)

        # Write back
        filepath.write_text("\n".join(lines))
        print(f"  ✅ Added import to {filepath}")
        return True

    except Exception as e:
        print(f"  ❌ Error fixing {filepath}: {e}")
        return False


def main():
    """Fix critical imports across the codebase."""
    print("🔧 Fixing Critical Missing Imports")
    print("=" * 50)

    fixed_count = 0

    for filepath, missing_items in FILE_FIXES.items():
        file_path = Path(filepath)

        if not file_path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n📄 Processing: {filepath}")

        for item in missing_items:
            if item in IMPORT_FIXES:
                import_stmt = IMPORT_FIXES[item]
                if add_import_to_file(file_path, import_stmt):
                    fixed_count += 1
            else:
                print(f"  ⚠️  No fix available for: {item}")

    print(f"\n{'=' * 50}")
    print(f"✅ Fixed {fixed_count} missing imports")

    # Additional fixes for unreachable code
    print("\n🔧 Fixing unreachable code issues...")

    # Fix vision_vocabulary.py unreachable code
    vision_vocab = Path("branding/vocabularies/vision_vocabulary.py")
    if vision_vocab.exists():
        content = vision_vocab.read_text()
        # Remove unreachable code after return statement
        pattern = r'(return f"\{analysis_symbol\}.*?\{confidence_symbol\}")\s+for obj in detected_objects:.*?return list\(set\(symbolic_elements\)\)[^\n]*'
        fixed_content = re.sub(pattern, r"\1", content, flags=re.DOTALL)

        if fixed_content != content:
            vision_vocab.write_text(fixed_content)
            print(f"  ✅ Fixed unreachable code in {vision_vocab}")
            fixed_count += 1

    print(f"\n🎯 Total fixes applied: {fixed_count}")
    print("\nRun 'ruff check --select=F821' to verify remaining issues")


if __name__ == "__main__":
    main()
