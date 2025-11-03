#!/usr/bin/env python3
"""
Rewrite import modules according to a mapping using LibCST.

Usage:
  python3 rewrite_imports_libcst.py --mapping '{"old.module":"new.module"}' --root .
  python3 rewrite_imports_libcst.py --mapping-file mapping.json --root .
  python3 rewrite_imports_libcst.py --mapping '{"a.b":"c_d"}' path/to/file.py > out.py

Note: This tool edits Import and ImportFrom nodes by replacing the left-hand
module string if it matches any mapping key.
"""
import argparse
import json
import sys
from pathlib import Path
import libcst as cst

class ImportRewriter(cst.CSTTransformer):
    def __init__(self, mapping):
        self.mapping = mapping

    def leave_Import(self, original_node, updated_node):
        # import a.b as ab  -> import new.module as ab (if mapping matches a.b or prefix)
        new_names = []
        changed = False
        for name in updated_node.names:
            n = name.name.value
            for old, new in self.mapping.items():
                if n == old or n.startswith(old + "."):
                    suffix = n[len(old):]
                    new_name = new + suffix
                    new_names.append(name.with_changes(name=cst.Name(new_name)))
                    changed = True
                    break
            else:
                new_names.append(name)
        if changed:
            return updated_node.with_changes(names=new_names)
        return updated_node

    def leave_ImportFrom(self, original_node, updated_node):
        if original_node.module is None:
            return updated_node
        mod_name = original_node.module.value
        for old, new in self.mapping.items():
            if mod_name == old or mod_name.startswith(old + "."):
                suffix = mod_name[len(old):]
                new_mod = new + suffix
                return updated_node.with_changes(module=cst.Name(new_mod))
        return updated_node

def rewrite_file(path: Path, mapping: dict):
    src = path.read_text(encoding="utf-8")
    wrapper = cst.parse_module(src)
    modified = wrapper.visit(ImportRewriter(mapping))
    return modified.code

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mapping", help='JSON mapping e.g. \'{"old.mod":"new.mod"}\'')
    p.add_argument("--mapping-file", help="path to JSON mapping file")
    p.add_argument("--root", default=".", help="root to walk if no path provided")
    p.add_argument("paths", nargs="*", help="files to rewrite (optional)")
    args = p.parse_args()

    if args.mapping_file:
        mapping = json.loads(Path(args.mapping_file).read_text())
    elif args.mapping:
        mapping = json.loads(args.mapping)
    else:
        print("Mapping required", file=sys.stderr)
        sys.exit(2)

    if args.paths:
        for pth in args.paths:
            out = rewrite_file(Path(pth), mapping)
            print(out)
    else:
        # Walk root
        for pth in Path(args.root).rglob("*.py"):
            if any(ex in str(pth) for ex in (".venv", "venv", "build", "dist", "generated", "migrations")):
                continue
            code = rewrite_file(pth, mapping)
            pth.write_text(code, encoding="utf-8")
            print(f"rewrote {pth}")

if __name__ == "__main__":
    main()
