#!/usr/bin/env python3
"""
Map 'missing' import paths to actual module locations in the codebase.

Discovers where code actually exists vs where imports think it should be.
"""
import subprocess
from pathlib import Path
from collections import defaultdict
import json

def find_actual_modules(search_term):
    """Find directories/files matching a search term."""
    matches = []

    # Search for directories
    for item in Path('.').rglob(f'*{search_term}*'):
        if '__pycache__' in str(item) or '.git' in str(item):
            continue

        if item.is_dir():
            py_files = list(item.glob('*.py'))
            py_files = [f for f in py_files if f.name != '__init__.py']
            if py_files:  # Has actual code
                matches.append({
                    'type': 'directory',
                    'path': str(item),
                    'files': len(py_files),
                    'file_names': [f.name for f in py_files[:5]]
                })
        elif item.suffix == '.py' and item.name != '__init__.py':
            matches.append({
                'type': 'file',
                'path': str(item)
            })

    return matches

def get_missing_modules():
    """Get list of missing modules from pytest."""
    result = subprocess.run(
        ['python3', '-m', 'pytest', '--collect-only', '-q'],
        capture_output=True,
        text=True
    )

    missing = set()
    for line in result.stderr.split('\n'):
        if 'No module named' in line:
            import re
            match = re.search(r"No module named '([^']+)'", line)
            if match:
                missing.add(match.group(1))

    return sorted(missing)

def main():
    print("🔍 Mapping 'missing' imports to actual module locations...\n")
    print("=" * 80)

    missing = get_missing_modules()
    print(f"Found {len(missing)} missing imports\n")

    mapping = {}
    truly_missing = []

    for module_path in missing:
        if not module_path or module_path == 'TODO':
            continue

        print(f"Searching: {module_path}")
        parts = module_path.split('.')
        last_part = parts[-1]

        # Search for the leaf module name
        matches = find_actual_modules(last_part)

        if matches:
            mapping[module_path] = matches
            print(f"  ✅ Found {len(matches)} potential matches")
            for match in matches[:2]:
                if match['type'] == 'directory':
                    print(f"     📁 {match['path']} ({match['files']} files)")
                else:
                    print(f"     📄 {match['path']}")
        else:
            truly_missing.append(module_path)
            print(f"  ❌ No matches found")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total 'missing' imports: {len(missing)}")
    print(f"Found existing code: {len(mapping)} ({len(mapping)/len(missing)*100:.1f}%)")
    print(f"Truly missing: {len(truly_missing)} ({len(truly_missing)/len(missing)*100:.1f}%)")

    # Save detailed mapping
    output = {
        'summary': {
            'total_missing': len(missing),
            'found_existing': len(mapping),
            'truly_missing': len(truly_missing)
        },
        'mapping': mapping,
        'truly_missing': truly_missing
    }

    output_file = Path('artifacts/import_mapping.json')
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2))

    print(f"\n📝 Detailed mapping saved to: {output_file}")

    if truly_missing:
        print(f"\n❌ Truly missing modules ({len(truly_missing)}):")
        for mod in truly_missing:
            print(f"   - {mod}")

    return 0 if len(truly_missing) < 10 else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
