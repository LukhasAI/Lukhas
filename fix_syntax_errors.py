#!/usr/bin/env python3
"""Fix syntax errors from malformed imports in tests/."""
import re
from pathlib import Path

FILES_TO_FIX = [
    "tests/unit/identity/test_webauthn_verify.py",
    "tests/core/orchestration/test_dream_adapter.py",
    "tests/core/modules/test_voice_narration.py",
    "tests/memory/test_cascade_property.py",
    "tests/security/test_pqc_redteam.py",
    "tests/security/test_security_validation.py",
    "tests/bridge/test_api_qrs_manager.py",
    "tests/utils/test_config_utils.py",
    "tests/observability/test_matriz_cognitive_instrumentation.py",
    "tests/test_guardian_serializers.py",
    "tests/orchestration/test_async_orchestrator_integration.py",
    "tests/governance/test_consent_manager.py",
    "tests/registry/test_legacy_reexports.py",
    "tests/guardian/test_schema_contract.py",
    "tests/performance/test_memory_production_load.py",
    "tests/e2e/test_matriz_orchestration.py",
]

def fix_file(filepath: Path):
    """Fix malformed typing imports."""
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # Fix "from typing import from"
    content = re.sub(
        r'from typing import ([^()\n]*?), from ',
        r'from typing import \1\nfrom ',
        content
    )
    
    # Fix "from typing import import"
    content = re.sub(
        r'from typing import ([^()\n]*?), import ',
        r'from typing import \1\nimport ',
        content
    )
    content = re.sub(
        r'from typing import import ',
        r'import ',
        content
    )
    
    # Remove empty "from typing import" lines
    content = re.sub(r'from typing import\s*\n', '', content)
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Fixed {filepath}")
        return True
    return False

def main():
    base = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
    fixed_count = 0
    
    for file_path in FILES_TO_FIX:
        filepath = base / file_path
        if filepath.exists():
            if fix_file(filepath):
                fixed_count += 1
    
    print(f"\n🎯 Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
