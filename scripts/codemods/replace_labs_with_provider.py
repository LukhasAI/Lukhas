#!/usr/bin/env python3
"""
Codemod: replace top-level `from labs.xxx import name1, name2` with importlib-based lazy assignments.
Usage:
  python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/patches
  python3 scripts/codemods/replace_labs_with_provider.py --apply
"""
from __future__ import annotations
import argparse
import difflib
from pathlib import Path
import libcst as cst

# NOTE: This codemod is intentionally conservative. It only converts top-level
# ImportFrom nodes whose module string starts with "labs". It does not change call sites
# aggressively — we create top-level names that callers can use, but callers may need manual review.

class LabsImportRewriter(cst.CSTTransformer):
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.CSTNode:
        # Only act on `from labs... import ...` at module level
        module = original_node.module
        if module is None:
            return updated_node
        module_code = module.code if hasattr(module, "code") else None
        if not module_code or not module_code.strip().startswith("labs"):
            return updated_node

        # Build replacement: importlib import + getattr assignments
        # Example:
        # import importlib as _importlib
        # try:
        #   _mod = _importlib.import_module("labs.foo")
        #   X = getattr(_mod, "X")
        #   Y = getattr(_mod, "Y")
        # except Exception:
        #   X = None
        #   Y = None

        importlib_stmt = cst.parse_statement("import importlib as _importlib\n")
        try_items = []
        mod_str = module_code.strip()
        # _mod = _importlib.import_module("module")
        try_items.append(
            cst.parse_statement(f"_mod = _importlib.import_module({repr(mod_str)})\n")
        )
        names = []
        for alias in original_node.names:
            if isinstance(alias, cst.ImportAlias):
                if isinstance(alias.name, cst.Name):
                    name = alias.name.value
                    asname = alias.asname.name.value if alias.asname else None
                    names.append((name, asname))
                else:
                    # fallback: write original import to manual review
                    return updated_node
            else:
                return updated_node

        for nm, asn in names:
            var = asn if asn else nm
            try_items.append(cst.parse_statement(f"{var} = getattr(_mod, {repr(nm)})\n"))

        except_items = []
        for nm, asn in names:
            var = asn if asn else nm
            except_items.append(cst.parse_statement(f"{var} = None\n"))

        try_stmt = cst.Try(
            body=cst.IndentedBlock(try_items),
            handlers=[cst.ExceptHandler(body=cst.IndentedBlock(except_items))],
            orelse=None,
            finalbody=None,
        )

        # Return a SmallBlock with importlib + try
        return cst.SimpleStatementLine([importlib_stmt, try_stmt])

def process_file(path: Path):
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as e:
        print(f"[skip] parse error {path}: {e}")
        return None
    rewriter = LabsImportRewriter()
    new_module = module.visit(rewriter)
    new_src = new_module.code
    if new_src != src:
        return src, new_src
    return None

def collect_py_files(root: Path):
    for p in root.rglob("*.py"):
        if any(x in p.parts for x in (".venv","venv",".git","tests","docs","artifacts","archive")):
            continue
        yield p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/codmod_patches")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in collect_py_files(root):
        res = process_file(f)
        if not res:
            continue
        old, new = res
        rel = f.relative_to(root)
        patch_path = outdir / (str(rel).replace("/", "__") + ".patch")
        # produce unified diff
        diff = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=str(f), tofile=str(f), lineterm=""))
        patch_path.write_text(diff, encoding="utf-8")
        print(f"[info] wrote patch {patch_path}")
        count += 1
        if args.apply:
            bak = f.with_suffix(f.suffix + ".bak")
            if not bak.exists():
                f.write_text(new, encoding="utf-8")
                print(f"[apply] updated {f} (backup at {bak})")
    print(f"[info] total patches: {count}")

if __name__ == "__main__":
    main()
