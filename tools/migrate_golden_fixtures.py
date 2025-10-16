#!/usr/bin/env python3
"""
Migrate smoke tests to use golden fixtures.

Automated migration script to replace hardcoded auth tokens with golden fixtures.
"""
import re
from pathlib import Path

def migrate_test_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Migrate a single test file to use golden fixtures.
    
    Returns:
        (changed, changes_made): Whether file was modified and list of changes
    """
    content = filepath.read_text()
    original = content
    changes = []
    
    # Pattern 1: Replace hardcoded AUTH_HEADERS constant
    if 'AUTH_HEADERS = {"Authorization": "Bearer sk-lukhas-' in content:
        content = re.sub(
            r'AUTH_HEADERS = \{"Authorization": "Bearer sk-lukhas-[^"]+"\}',
            'from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS\n\nAUTH_HEADERS = GOLDEN_AUTH_HEADERS',
            content
        )
        changes.append("Replaced AUTH_HEADERS constant with GOLDEN_AUTH_HEADERS")
    
    # Pattern 2: Replace auth_headers fixture
    auth_fixture_pattern = r'@pytest\.fixture\s+def auth_headers\(\):[^}]+return \{"Authorization": "Bearer sk-lukhas-[^"]+"\}'
    if re.search(auth_fixture_pattern, content, re.DOTALL):
        # Add import at top if not present
        if 'from tests.smoke.fixtures import' not in content:
            # Find the last import line
            import_lines = [i for i, line in enumerate(content.split('\n')) if line.startswith('from ') or line.startswith('import ')]
            if import_lines:
                lines = content.split('\n')
                last_import_idx = max(import_lines)
                lines.insert(last_import_idx + 1, '\nfrom tests.smoke.fixtures import GOLDEN_AUTH_HEADERS')
                content = '\n'.join(lines)
        
        content = re.sub(
            auth_fixture_pattern,
            '@pytest.fixture\ndef auth_headers():\n    """Provide valid Bearer token for authenticated requests."""\n    return GOLDEN_AUTH_HEADERS',
            content,
            flags=re.DOTALL
        )
        changes.append("Updated auth_headers fixture to use GOLDEN_AUTH_HEADERS")
    
    # Pattern 3: Replace inline auth headers in test functions
    inline_pattern = r'\{"Authorization": "Bearer sk-lukhas-test-[0-9a-f]+"\}'
    if re.search(inline_pattern, content):
        # Add import if not present
        if 'from tests.smoke.fixtures import' not in content and 'GOLDEN_AUTH_HEADERS' not in content:
            import_lines = [i for i, line in enumerate(content.split('\n')) if line.startswith('from ') or line.startswith('import ')]
            if import_lines:
                lines = content.split('\n')
                last_import_idx = max(import_lines)
                lines.insert(last_import_idx + 1, '\nfrom tests.smoke.fixtures import GOLDEN_AUTH_HEADERS')
                content = '\n'.join(lines)
        
        content = re.sub(inline_pattern, 'GOLDEN_AUTH_HEADERS', content)
        changes.append("Replaced inline auth headers with GOLDEN_AUTH_HEADERS")
    
    # Pattern 4: Replace _auth_headers helper function with golden_auth_headers
    helper_pattern = r'def _auth_headers\(extra:[^\)]+\)[^:]+:[^\n]+\n[^\n]+headers = \{"Authorization": "Bearer[^}]+\}[^\n]+\n[^\n]+if extra:[^\n]+\n[^\n]+headers\.update\(extra\)[^\n]+\n[^\n]+return headers'
    if re.search(helper_pattern, content, re.DOTALL):
        # Replace the helper function
        content = re.sub(helper_pattern, '', content, flags=re.DOTALL)
        # Add import
        if 'golden_auth_headers' not in content:
            if 'from tests.smoke.fixtures import' in content:
                content = content.replace(
                    'from tests.smoke.fixtures import',
                    'from tests.smoke.fixtures import golden_auth_headers,'
                )
            else:
                import_lines = [i for i, line in enumerate(content.split('\n')) if line.startswith('from ') or line.startswith('import ')]
                if import_lines:
                    lines = content.split('\n')
                    last_import_idx = max(import_lines)
                    lines.insert(last_import_idx + 1, '\nfrom tests.smoke.fixtures import golden_auth_headers')
                    content = '\n'.join(lines)
        # Replace calls
        content = content.replace('_auth_headers(', 'golden_auth_headers(')
        changes.append("Replaced _auth_headers() with golden_auth_headers()")
    
    changed = content != original
    if changed:
        filepath.write_text(content)
    
    return changed, changes


def main():
    """Migrate all smoke test files."""
    smoke_dir = Path("tests/smoke")
    test_files = list(smoke_dir.glob("test_*.py"))
    
    migrated = []
    skipped = []
    
    for filepath in sorted(test_files):
        changed, changes = migrate_test_file(filepath)
        if changed:
            migrated.append((filepath.name, changes))
            print(f"✅ {filepath.name}: {len(changes)} changes")
            for change in changes:
                print(f"   - {change}")
        else:
            skipped.append(filepath.name)
    
    print(f"\n📊 Summary:")
    print(f"   Migrated: {len(migrated)} files")
    print(f"   Skipped: {len(skipped)} files (already clean or no auth tokens)")
    
    if migrated:
        print(f"\n✅ Migration complete!")
        print(f"\nNext steps:")
        print(f"1. Run: pytest tests/smoke/ -v")
        print(f"2. Verify all tests still pass")
        print(f"3. Commit: git add tests/smoke/test_*.py && git commit")


if __name__ == "__main__":
    main()
