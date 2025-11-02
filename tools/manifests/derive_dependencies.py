#!/usr/bin/env python3
import argparse
import ast
import json
import pathlib
import subprocess
import sys
from typing import Set, List

INTERNAL_TOPS = {'core', 'lukhas', 'matriz'}


def gather_py_files(pkg_dir: pathlib.Path) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for p in pkg_dir.rglob('*.py'):
        if any(seg.startswith('.') for seg in p.parts):
            continue
        if '__pycache__' in p.parts:
            continue
        if p.name.startswith('test_'):
            continue
        if p.name.endswith('_test.py'):
            continue
        files.append(p)
    return files


def extract_imports(py_path: pathlib.Path) -> Set[str]:
    try:
        src = py_path.read_text(encoding='utf-8',
                               errors='ignore')
        tree = ast.parse(src)
    except Exception:
        return set()
    mods: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name or ''
                if name:
                    top = name.split('.')[0]
                    if top:
                        mods.add(top)
        elif isinstance(node, ast.ImportFrom):
            module = getattr(node, 'module', None)
            if module:
                top = module.split('.')[0]
                if top:
                    mods.add(top)
    return mods


def to_internal_module_names(mods: Set[str]) -> List[str]:
    keep = [m for m in mods if m in INTERNAL_TOPS]
    return sorted(set(keep))


def derive_for_manifest(manifest_path: pathlib.Path) -> List[str]:
    obj = json.loads(manifest_path.read_text())
    pkg_path = obj.get('path')
    if not isinstance(pkg_path, str):
        return []
    pkg_dir = pathlib.Path(pkg_path)
    if not pkg_dir.exists():
        return []
    deps: Set[str] = set()
    for pyf in gather_py_files(pkg_dir):
        deps |= extract_imports(pyf)
    internals = to_internal_module_names(deps)
    return internals


def update_manifest_deps(manifest_path: pathlib.Path,
                         new_deps: List[str]) -> bool:
    obj = json.loads(manifest_path.read_text())
    cur = obj.get('dependencies')
    if not isinstance(cur, list):
        cur = []
    merged = sorted(set(cur) | set(new_deps))
    obj['dependencies'] = merged
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    text += '\n'
    manifest_path.write_text(text)
    return True


def collect_created_manifests_by_shas(shas: List[str]) -> List[pathlib.Path]:
    created: List[pathlib.Path] = []
    for sha in shas:
        out = subprocess.check_output([
            'git','diff-tree','--no-commit-id',
            '--name-only','-r', sha
        ]).decode().splitlines()
        for p in out:
            if p.startswith('manifests/'):
                if p.endswith('/module.manifest.json'):
                    created.append(pathlib.Path(p))
    return created


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--targets', nargs='*',
                    help='Specific manifest paths')
    ap.add_argument('--batches', action='store_true',
                    help='Use known batch SHAs')
    args = ap.parse_args()

    manifests: List[pathlib.Path] = []
    if args.targets:
        manifests = [pathlib.Path(p) for p in args.targets]
    elif args.batches:
        shas = [
            '1826fb30c43b165eda14c9ea0d1657d94a2f3880',
            'd9b5e47fe2fef4a56a1d39e4931e53ee299f5878',
            '1a2d64245a9df60604a518b02e541461532d26a7',
        ]
        manifests = collect_created_manifests_by_shas(shas)
    else:
        print('Provide --targets or --batches')
        sys.exit(2)

    changed = 0
    for m in manifests:
        new_deps = derive_for_manifest(m)
        if update_manifest_deps(m, new_deps):
            changed += 1
            print(f'Updated {m} deps -> {new_deps}')
    print(f'Updated {changed} manifest(s)')

if __name__ == '__main__':
    main()