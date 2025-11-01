#!/usr/bin/env python3
"""
Codemod: Replace top-level `from labs.xxx import name1, name2` with
lazy, importlib-based assignments that eliminate static `ImportFrom` edges
to `labs` while preserving runtime behavior where possible.

Usage:
  - Dry-run (write .patch files only):
      python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
  - Apply in place (creates .bak backups):
      python3 scripts/codemods/replace_labs_with_provider.py --apply

Notes:
  - Only transforms top-level imports (module scope). Imports inside functions/classes are left as-is.
  - Star imports (from labs.x import *) are skipped and reported.
  - Adds `import importlib as _importlib` at module top if needed.
  - Skips files under tests/docs/venv/artifacts/archive folders.
"""
from __future__ import annotations

import argparse
import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import libcst as cst
from libcst import MaybeSentinel


LABS_PREFIX = "labs"


@dataclass
class ImportSpec:
    module_str: str
    names: List[Tuple[str, Optional[str]]]  # (name, alias)


def _is_top_level_stmt(stmt: cst.BaseStatement) -> bool:
    # In libcst's Module.body, statements are top-level.
    # We additionally ensure the ImportFrom sits directly in a SimpleStatementLine.
    return isinstance(stmt, cst.SimpleStatementLine)


def _extract_importfrom(stmt: cst.BaseStatement) -> Optional[cst.ImportFrom]:
    if not isinstance(stmt, cst.SimpleStatementLine):
        return None
    if len(stmt.body) != 1:
        return None
    small = stmt.body[0]
    if isinstance(small, cst.ImportFrom):
        return small
    return None


def _get_module_str(mod: Optional[cst.BaseExpression]) -> Optional[str]:
    if mod is None:
        return None
    try:
        # Best-effort full name
        return cst.helpers.get_full_name_for_node(mod)
    except Exception:
        try:
            return mod.code
        except Exception:
            return None


def _importfrom_to_spec(node: cst.ImportFrom) -> Optional[ImportSpec]:
    mod_text = _get_module_str(node.module)
    if not mod_text:
        return None
    if not (mod_text == LABS_PREFIX or mod_text.startswith(LABS_PREFIX + ".")):
        return None

    # Only handle explicit names; skip star imports
    if isinstance(node.names, MaybeSentinel):
        return None
    names: List[Tuple[str, Optional[str]]] = []
    for alias in node.names:
        if isinstance(alias, cst.ImportStar):
            # Skip star imports – too risky to rewrite automatically
            return None
        if isinstance(alias, cst.ImportAlias):
            name_node = alias.name
            nm = name_node.value if isinstance(name_node, cst.Name) else name_node.code
            asname = alias.asname
            alias_str = asname.name.value if (asname and isinstance(asname.name, cst.Name)) else None
            names.append((nm, alias_str))
    if not names:
        return None
    return ImportSpec(module_str=mod_text, names=names)


def _try_collect_labs_specs(try_node: cst.Try) -> Optional[List[ImportSpec]]:
    """If the try-block body consists of one or more labs ImportFrom lines, collect them.
    Returns list of specs or None if pattern not matched (to avoid risky rewrites).
    """
    # Only consider trivial try blocks (no else/finally), any except allowed.
    if try_node.orelse is not None or try_node.finalbody is not None:
        return None
    specs: List[ImportSpec] = []
    for st in try_node.body.body:
        if not isinstance(st, cst.SimpleStatementLine) or len(st.body) != 1:
            return None
        small = st.body[0]
        if not isinstance(small, cst.ImportFrom):
            return None
        spec = _importfrom_to_spec(small)
        if spec is None:
            return None
        specs.append(spec)
    if not specs:
        return None
    return specs


def _has_importlib_alias(module: cst.Module) -> Optional[str]:
    # Return the symbol to use for importlib (alias or bare name), if present
    for stmt in module.body:
        if isinstance(stmt, cst.SimpleStatementLine):
            for small in stmt.body:
                if isinstance(small, cst.Import):
                    for name in small.names:
                        if not isinstance(name, cst.ImportAlias):
                            continue
                        target = name.name
                        if isinstance(target, cst.Name) and target.value == "importlib":
                            if name.asname and isinstance(name.asname.name, cst.Name):
                                return name.asname.name.value
                            return "importlib"
    return None


def _build_lazy_block(spec: ImportSpec, importlib_symbol: str) -> cst.Try:
    # try:
    #   _mod = importlib_symbol.import_module("spec.module_str")
    #   Name = getattr(_mod, "Name"); ...
    # except Exception:
    #   Name = None; ...
    body_stmts: List[cst.BaseStatement] = []

    assign_mod = cst.parse_statement(
        f"_mod = {importlib_symbol}.import_module(\"{spec.module_str}\")"
    )
    body_stmts.append(assign_mod)

    for nm, alias in spec.names:
        varname = alias or nm
        body_stmts.append(cst.parse_statement(f"{varname} = getattr(_mod, \"{nm}\")"))

    except_body: List[cst.BaseStatement] = []
    for nm, alias in spec.names:
        varname = alias or nm
        except_body.append(cst.parse_statement(f"{varname} = None"))

    try_node = cst.Try(
        body=cst.IndentedBlock(body=body_stmts),
        handlers=[
            cst.ExceptHandler(
                type=cst.Name("Exception"),
                name=None,
                body=cst.IndentedBlock(body=except_body),
            )
        ],
        orelse=None,
        finalbody=None,
    )
    return try_node


def rewrite_module(module: cst.Module) -> Tuple[cst.Module, bool]:
    """Return (new_module, changed?)."""
    changed = False
    new_body: List[cst.BaseStatement] = []

    # Determine existing importlib symbol (alias) if present
    importlib_symbol = _has_importlib_alias(module)
    need_importlib = False

    for stmt in module.body:
        repl_done = False
        impfrom = _extract_importfrom(stmt)
        if _is_top_level_stmt(stmt) and impfrom is not None:
            spec = _importfrom_to_spec(impfrom)
            if spec is not None:
                changed = True
                # Ensure we have a usable importlib symbol
                sym = importlib_symbol or "_importlib"
                if importlib_symbol is None:
                    need_importlib = True
                # Replace the single-line import with a try/except block
                new_body.append(_build_lazy_block(spec, sym))
                repl_done = True
        elif isinstance(stmt, cst.Try):
            specs = _try_collect_labs_specs(stmt)
            if specs:
                changed = True
                sym = importlib_symbol or "_importlib"
                if importlib_symbol is None:
                    need_importlib = True
                # For each spec, emit a separate lazy block to keep names clear
                for sp in specs:
                    new_body.append(_build_lazy_block(sp, sym))
                repl_done = True

        if not repl_done:
            new_body.append(stmt)

    out_module = module.with_changes(body=new_body)

    # Insert `import importlib as _importlib` if needed and not already present.
    # Keep order: [docstring] -> [from __future__ ...] -> import importlib ... -> rest
    if need_importlib:
        import_stmt = cst.parse_statement("import importlib as _importlib\n")
        idx = 0
        body = list(out_module.body)

        # 1) Optional module docstring at index 0
        if body and isinstance(body[0], cst.SimpleStatementLine):
            first_small = body[0].body[0]
            if isinstance(first_small, cst.Expr) and isinstance(first_small.value, cst.SimpleString):
                idx = 1

        # 2) Consecutive __future__ imports after docstring block
        while idx < len(body):
            stmt = body[idx]
            if not isinstance(stmt, cst.SimpleStatementLine):
                break
            if len(stmt.body) != 1:
                break
            small = stmt.body[0]
            if isinstance(small, cst.ImportFrom):
                mod_text = _get_module_str(small.module)
                if mod_text == "__future__":
                    idx += 1
                    continue
            break

        new_body2: List[cst.BaseStatement] = [*body[:idx], import_stmt, *body[idx:]]
        out_module = out_module.with_changes(body=new_body2)

    return out_module, changed


def process_file(path: Path) -> Optional[Tuple[str, str]]:
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as e:
        print(f"[warn] parse failed for {path}: {e}")
        return None

    new_mod, changed = rewrite_module(module)
    if not changed:
        return None
    new_src = new_mod.code
    diff = "\n".join(
        difflib.unified_diff(
            src.splitlines(), new_src.splitlines(), fromfile=str(path), tofile=str(path), lineterm=""
        )
    )
    return new_src, diff


def collect_py_files(root: Path, includes: Optional[List[str]] = None) -> Iterable[Path]:
    root = root.resolve()
    if includes:
        include_paths = [ (root / inc).resolve() for inc in includes ]
    else:
        # Default to core/ lukhas/ serve/
        include_paths = [ (root / x).resolve() for x in ("core", "lukhas", "serve") ]

    for inc in include_paths:
        if not inc.exists():
            continue
        for p in inc.rglob("*.py"):
            # Skip common non-target paths
            if any(part in p.parts for part in (".venv", "venv", "tests", "docs", "artifacts", "archive", "labs")):
                continue
            # Skip typical test file name patterns
            name = p.name
            if name.startswith("test_") or name.endswith("_test.py"):
                continue
            yield p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--outdir", default="/tmp/codmod_patches")
    ap.add_argument("--apply", action="store_true", default=False)
    ap.add_argument("--include", action="append", default=None, help="Include subpaths (repeatable). Defaults: core, lukhas, serve")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    updated = 0
    for f in collect_py_files(root, args.include):
        try:
            res = process_file(f)
        except Exception as e:
            print(f"[warn] failed processing {f}: {e}")
            continue
        if not res:
            continue
        new_src, diff = res
        # Always emit a patch for review
        # Name patch by repo-relative path for clarity
        try:
            rel = f.relative_to(root)
        except Exception:
            rel = f
        safe_name = str(rel).replace("/", "__")
        patch_path = outdir / (safe_name + ".patch")
        patch_path.write_text(diff, encoding="utf-8")
        print(f"[info] patch written: {patch_path}")
        updated += 1
        if args.apply:
            bak = f.with_suffix(f.suffix + ".bak")
            if not bak.exists():
                # backup original and write new
                f.rename(bak)
                f.write_text(new_src, encoding="utf-8")
            else:
                print(f"[warn] backup exists; skip apply for {f}")

    print(f"[info] Completed. {updated} file(s) would be/were updated.")


if __name__ == "__main__":
    main()
