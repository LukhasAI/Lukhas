#!/usr/bin/env python3
from __future__ import annotations

import glob
import json
import sys

REQUIRED = {
    'name': str,
    'path': str,
    'constellation_stars': list,
    'confidence': (int, float),
    'description': str,
    'status': str,
    'tier': str,
    'lane': str,
    'version': str,
    'created': str,
    'updated': str,
    'metadata': dict,
}

OPTIONAL_TYPES = {
    'dependencies': list,
}

def validate_obj(obj):
    errors = []
    for k, t in REQUIRED.items():
        if k not in obj:
            errors.append(f"missing required field: {k}")
        else:
            if not isinstance(obj[k], t):
                errors.append(
                    f"field {k} wrong type: expected {t}, got {type(obj[k])}"
                )
    for k, t in OPTIONAL_TYPES.items():
        if k in obj and not isinstance(obj[k], t):
            errors.append(
                f"field {k} wrong type: expected {t}, got {type(obj[k])}"
            )
    # Quick value checks
    if 'name' in obj and 'path' in obj and obj['name'].replace('.', '/') != obj['path']:
        errors.append(
            'name/path mismatch: name with dots should match path with slashes'
        )
    if 'lane' in obj and obj['lane'] not in {'core', 'lukhas', 'matriz', 'labs'}:
        errors.append('lane must be one of core|lukhas|matriz|labs')
    if 'constellation_stars' in obj and (not all((isinstance(s, str) for s in obj['constellation_stars']))):
        errors.append('constellation_stars must be an array of strings')
    return errors

def main():
    if len(sys.argv) < 2:
        print('Usage: validate_manifest.py <file-or-glob> [...]', file=sys.stderr)
        return 2
    files = []
    for arg in sys.argv[1:]:
        files.extend(glob.glob(arg))
    bad = 0
    for f in files:
        try:
            with open(f) as fh:
                obj = json.load(fh)
        except Exception as e:
            print(f'ERROR {f}: invalid JSON: {e}')
            bad += 1
            continue
        errs = validate_obj(obj)
        if errs:
            print(f'ERROR {f}:')
            for e in errs:
                print(f'  - {e}')
            bad += 1
    if bad:
        print('Validation failed for %d file(s)' % bad)
        return 1
    print('All checked manifests passed validation')
    return 0

if __name__ == '__main__':
    sys.exit(main())
