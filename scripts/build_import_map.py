#!/usr/bin/env python3
"""
Module: build_import_map.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path


def safe_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def from_manifest_exports(manifest: dict) -> list[str]:
    # Best-effort: look in common keys
    for key in ("public_api","exports","interfaces","exposes"):
        v = manifest.get(key)
        if isinstance(v, list):
            return [str(x) for x in v if isinstance(x, (str,))]
    return []

def top_level_symbols(py: Path):
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return [], [], [], []
    classes, funcs, consts, all_decl = [], [], [], []
    has_all = False
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # __all__ = [...]
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    has_all = True
                    try:
                        vals = []
                        if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    vals.append(elt.s)
                        all_decl = vals
                    except Exception:
                        pass
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    consts.append(t.id)
    if has_all and all_decl:
        # __all__ governs export surface
        classes = [c for c in classes if c in all_decl]
        funcs   = [f for f in funcs if f in all_decl]
        consts  = [k for k in consts if k in all_decl]
    return classes, funcs, consts, all_decl

def import_path_for(py: Path, repo_root: Path, root_pkg: str) -> str|None:
    try:
        rel = py.resolve().relative_to(repo_root.resolve())
    except Exception:
        return None
    parts = list(rel.parts)
    if not parts or parts[0] != root_pkg: return None
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].replace(".py","")
    return ".".join(parts)

def main():
    repo_root = Path(".").resolve()
    root_pkg = "lukhas"
    symbol_to_modules = {}  # symbol -> set(modules)
    module_to_symbols = {}  # module -> set(symbols)

    # 1) manifests
    for mf in repo_root.rglob("module.manifest.json"):
        man = safe_json(mf)
        if not man:
            continue
        exports = from_manifest_exports(man)
        # Try to infer code module path next to the manifest
        code_dir = mf.parent
        for py in list(code_dir.glob("*.py")) + list(code_dir.rglob("__init__.py")):
            mod = import_path_for(py, repo_root, root_pkg)
            if not mod:
                continue
            if exports:
                module_to_symbols.setdefault(mod, set()).update(exports)
                for s in exports:
                    symbol_to_modules.setdefault(s, set()).add(mod)

    # 2) code scan under lukhas/**
    pkg_dir = repo_root / root_pkg
    if pkg_dir.exists():
        for py in pkg_dir.rglob("*.py"):
            if "/generated/" in str(py):
                continue
            mod = import_path_for(py, repo_root, root_pkg)
            if not mod:
                continue
            cls, fn, cs, all_decl = top_level_symbols(py)
            syms = set(cls + fn + cs)
            if all_decl:  # prefer explicit exports
                syms = syms.union(all_decl)
            if syms:
                module_to_symbols.setdefault(mod, set()).update(syms)
                for s in syms:
                    symbol_to_modules.setdefault(s, set()).add(mod)

    # to JSON
    out = {
        "generated_from": "build_import_map.py",
        "symbol_to_modules": {k: sorted(list(v)) for k,v in symbol_to_modules.items()},
        "module_to_symbols": {k: sorted(list(v)) for k,v in module_to_symbols.items()},
    }
    outp = Path("docs/audits/import_map.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[OK] wrote {outp} (symbols: {len(symbol_to_modules)}, modules: {len(module_to_symbols)})")

if __name__ == "__main__":
    main()
