#!/usr/bin/env python3
"""
Enhanced LibCST codemod: Convert multi-import try/except ImportError patterns.

Handles both:
    try:
        from fastapi import HTTPException, Request
    except ImportError:
        HTTPException = None
        Request = None

    try:
        import module_a, module_b
    except ImportError:
        module_a = None
        module_b = None

Converts to importlib.util.find_spec guards while preserving optional import behavior.
Conservative: only processes simple patterns in top-of-file import region.
"""
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

import libcst as cst
from libcst import FlattenSentinel

TOP_LINES_CUTOFF = 140  # only touch try-except in top area


def has_importlib_util(module: cst.Module) -> bool:
    """Check if importlib.util is already imported."""
    for node in module.body:
        if isinstance(node, cst.SimpleStatementLine):
            stmt = node.body[0]
            if isinstance(stmt, cst.Import):
                for alias in stmt.names:
                    if alias.name.value == "importlib.util":
                        return True
    return False


class MultiTryImportTransformer(cst.CSTTransformer):
    """
    Convert patterns like:

    try:
        from fastapi import HTTPException, Request
    except ImportError:
        HTTPException = None
        Request = None

    into:

    import importlib.util
    if importlib.util.find_spec("fastapi"):
        from fastapi import HTTPException, Request
    else:
        HTTPException = None
        Request = None
    """

    def __init__(self, top_line_cutoff: int = TOP_LINES_CUTOFF) -> None:
        self.top_line_cutoff = top_line_cutoff
        self.changed = False
        self.need_importlib_util = False
        super().__init__()

    def _is_simple_assign_none(self, node: cst.Assign) -> Optional[str]:
        """Return assigned name if pattern is 'NAME = None'."""
        if len(node.targets) != 1:
            return None
        tgt = node.targets[0].target
        if not isinstance(tgt, cst.Name):
            return None
        val = node.value
        if isinstance(val, cst.Name) and val.value == "None":
            return tgt.value
        return None

    def leave_Try(
        self, original_node: cst.Try, updated_node: cst.Try
    ) -> Union[cst.Try, FlattenSentinel[cst.If]]:
        """Transform try-except ImportError patterns to importlib.util.find_spec."""
        # Only process try blocks near top-of-file (heuristic)
        try_lineno = getattr(original_node, "lineno", 0)
        if try_lineno > self.top_line_cutoff and try_lineno != 0:
            return updated_node

        # body must be single stmt and that must be ImportFrom or Import
        if len(original_node.body.body) != 1:
            return updated_node
        body_stmt = original_node.body.body[0]
        from_stmt = None
        import_stmt = None
        if isinstance(body_stmt, cst.SimpleStatementLine) and isinstance(
            body_stmt.body[0], cst.ImportFrom
        ):
            from_stmt = body_stmt.body[0]
        elif isinstance(body_stmt, cst.SimpleStatementLine) and isinstance(
            body_stmt.body[0], cst.Import
        ):
            import_stmt = body_stmt.body[0]
        else:
            return updated_node

        # exactly one except handler
        if len(original_node.handlers) != 1:
            return updated_node
        handler = original_node.handlers[0]
        # handler must catch ImportError specifically
        if handler.type is None or not (
            isinstance(handler.type, cst.Name) and handler.type.value == "ImportError"
        ):
            return updated_node
        # handler body must be sequence of assignments NAME = None, for each imported name
        assigns = []
        for hstmt in handler.body.body:
            if not isinstance(hstmt, cst.SimpleStatementLine):
                return updated_node
            inner = hstmt.body[0]
            if not isinstance(inner, cst.Assign):
                return updated_node
            name = self._is_simple_assign_none(inner)
            if not name:
                return updated_node
            assigns.append(name)

        # If ImportFrom: module & names
        if from_stmt is not None:
            module = (
                from_stmt.module.value if from_stmt.module is not None else None
            )
            if not module:
                return updated_node
            imported_names = []
            for alias in from_stmt.names:
                if isinstance(alias, cst.ImportStar):
                    return updated_node  # skip star imports
                imported_names.append(alias.name.value)
            # sanity: assigns must match imported_names (subset or same)
            # require all imported names to be in assigns or at least many; conservative: require all
            if not set(imported_names).issubset(set(assigns)):
                return updated_node

            # Build replacement
            self.need_importlib_util = True
            # if importlib.util.find_spec("module"): from module import a,b else: a=None; b=None
            find_call = cst.Call(
                func=cst.Attribute(
                    value=cst.Attribute(
                        value=cst.Name("importlib"), attr=cst.Name("util")
                    ),
                    attr=cst.Name("find_spec"),
                ),
                args=[cst.Arg(cst.SimpleString(f"'{module}'"))],
            )
            if_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[from_stmt])])
            else_body_stmts = []
            for nm in imported_names:
                else_body_stmts.append(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[cst.AssignTarget(cst.Name(nm))],
                                value=cst.Name("None"),
                            )
                        ]
                    )
                )
            else_body = cst.IndentedBlock(body=else_body_stmts)
            if_node = cst.If(test=find_call, body=if_body, orelse=else_body)
            self.changed = True
            return FlattenSentinel([if_node])

        # If Import: import a, b
        if import_stmt is not None:
            imported_modules = []
            for alias in import_stmt.names:
                # alias.name may have dotted name 'a.b'; use first entry
                name = alias.name.value
                imported_modules.append(name)
            # check assigns correspond to imported module base names
            base_names = [nm.split(".")[-1] for nm in imported_modules]
            if not set(base_names).issubset(set(assigns)):
                return updated_node

            # Build if-chain: for each imported module we create an if find_spec('module'): import module else: base=None
            new_nodes = []
            for mod, base in zip(imported_modules, base_names):
                self.need_importlib_util = True
                find_call = cst.Call(
                    func=cst.Attribute(
                        value=cst.Attribute(
                            value=cst.Name("importlib"), attr=cst.Name("util")
                        ),
                        attr=cst.Name("find_spec"),
                    ),
                    args=[cst.Arg(cst.SimpleString(f"'{mod}'"))],
                )
                if_stmt = cst.If(
                    test=find_call,
                    body=cst.IndentedBlock(
                        body=[
                            cst.SimpleStatementLine(
                                body=[
                                    cst.Import(
                                        names=[cst.ImportAlias(name=cst.Name(mod))]
                                    )
                                ]
                            )
                        ]
                    ),
                    orelse=cst.IndentedBlock(
                        body=[
                            cst.SimpleStatementLine(
                                body=[
                                    cst.Assign(
                                        targets=[cst.AssignTarget(cst.Name(base))],
                                        value=cst.Name("None"),
                                    )
                                ]
                            )
                        ]
                    ),
                )
                new_nodes.append(if_stmt)
            self.changed = True
            return FlattenSentinel(new_nodes)

        return updated_node


def transform_file(path: str, dry_run: bool = True) -> dict:
    """Transform a single file, either in dry-run or apply mode."""
    p = Path(path)
    if not p.exists():
        return {"changed": False, "error": "file_not_found"}

    src = p.read_text()
    module = cst.parse_module(src)
    transformer = MultiTryImportTransformer()
    new_module = module.visit(transformer)
    if not transformer.changed:
        return {"changed": False, "reason": "no_match"}
    new_src = new_module.code
    # add importlib.util at top if needed and not present
    if transformer.need_importlib_util and "importlib.util" not in src:
        # insert at very top after module docstring and existing imports
        lines = new_src.splitlines()
        insert_at = 0
        # skip shebang and docstring if present
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        # find first non-import line
        for i, line in enumerate(lines[insert_at:], start=insert_at):
            if not line.strip().startswith("import") and not line.strip().startswith(
                "from"
            ):
                insert_at = i
                break
        lines.insert(insert_at, "import importlib.util")
        new_src = "\n".join(lines)
    if dry_run:
        with tempfile.NamedTemporaryFile("w", delete=False) as fh:
            fh.write(new_src)
            tmp = fh.name
        diff = subprocess.run(
            ["git", "diff", "--no-index", "--", path, tmp],
            capture_output=True,
            text=True,
        )
        os.unlink(tmp)
        return {"changed": True, "diff": diff.stdout}
    else:
        # backup original done by caller
        p.write_text(new_src)
        return {"changed": True, "applied": True}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = {}
    for f in args.files:
        try:
            out[f] = transform_file(f, dry_run=args.dry_run)
        except Exception as e:
            out[f] = {"changed": False, "error": f"ERROR: {e!s}"}
    print(json.dumps(out, indent=2))
