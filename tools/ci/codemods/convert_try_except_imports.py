#!/usr/bin/env python3
"""
Conservative codemod: Convert try/except ImportError patterns to importlib.util.find_spec.

Pattern conversion:
    try:
        import foo
    except ImportError:
        foo = None

    →

    import importlib.util
    if importlib.util.find_spec("foo"):
        import foo
    else:
        foo = None

Only converts simple patterns in top ~120 lines (import region).
Conservative by design - skips complex cases.
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import libcst as cst


class ConvertTryExceptImports(cst.CSTTransformer):
    """
    Convert patterns:
    try:
        import foo
    except ImportError:
        foo = None

    into:

    import importlib.util
    if importlib.util.find_spec("foo"):
        import foo
    else:
        foo = None
    """

    def __init__(self, top_lines_cutoff: int = 120):
        self.top_lines_cutoff = top_lines_cutoff
        self.changed = False
        super().__init__()

    def leave_Try(
        self, original_node: cst.Try, updated_node: cst.Try
    ) -> Optional[cst.BaseStatement]:
        # Only consider simple try-except blocks that are in the top-of-file import region
        lineno = getattr(original_node, "lineno", 0)
        if lineno and lineno > self.top_lines_cutoff:
            return updated_node

        # require single body statement that is Import or ImportFrom
        if len(original_node.body.body) != 1:
            return updated_node
        first = original_node.body.body[0]
        if not isinstance(first, (cst.SimpleStatementLine,)):
            return updated_node
        stmt = first.body[0]  # the underlying statement
        if not isinstance(stmt, (cst.Import, cst.ImportFrom)):
            return updated_node

        # require exactly one except handler, catching ImportError or ExceptionName 'ImportError'
        if len(original_node.handlers) != 1:
            return updated_node
        handler = original_node.handlers[0]
        if handler.type is None:
            return updated_node
        if not (isinstance(handler.type, cst.Name) and handler.type.value == "ImportError"):
            return updated_node

        # except body must exist and set same name(s) to None
        if len(handler.body.body) != 1:
            return updated_node
        handler_stmt = handler.body.body[0]
        if not isinstance(handler_stmt, cst.SimpleStatementLine):
            return updated_node
        inner = handler_stmt.body[0]
        # allow assignment(s) like foo = None or multiple assigns - handle simple single target
        if not isinstance(inner, cst.Assign):
            return updated_node

        # collect target names from import and assignment
        import_names = []
        if isinstance(stmt, cst.Import):
            for alias in stmt.names:
                name = alias.name.value.split(".")[-1]
                import_names.append(name)
        else:
            # from X import a,b
            for alias in stmt.names:
                name = alias.name.value
                import_names.append(name)

        # assignment target
        targets = inner.targets
        if len(targets) != 1:
            return updated_node
        target = targets[0].target
        if isinstance(target, cst.Name):
            assigned_name = target.value
        else:
            return updated_node
        # value must be Name 'None'
        if not isinstance(inner.value, cst.Name) or inner.value.value != "None":
            return updated_node

        # require assigned_name to be one of imported names (simple heuristic)
        if assigned_name not in import_names:
            return updated_node

        # Build new nodes: ensure importlib.util included at top - we'll return an If statement
        # Create: import importlib.util
        importlib_import = cst.SimpleStatementLine(
            body=[
                cst.Import(
                    names=[
                        cst.ImportAlias(
                            name=cst.Attribute(value=cst.Name("importlib"), attr=cst.Name("util"))
                        )
                    ]
                )
            ]
        )
        # create "if importlib.util.find_spec('X'):\n    import X\nelse:\n    X = None"
        find_call = cst.Call(
            func=cst.Attribute(
                value=cst.Attribute(value=cst.Name("importlib"), attr=cst.Name("util")),
                attr=cst.Name("find_spec"),
            ),
            args=[cst.Arg(cst.SimpleString(f"'{import_names[0]}'"))],
        )
        if_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[stmt])])
        else_assign = cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(cst.Name(assigned_name))],
                    value=cst.Name("None"),
                )
            ]
        )
        else_body = cst.IndentedBlock(body=[else_assign])
        if_stmt = cst.If(test=find_call, body=if_body, orelse=else_body)

        self.changed = True
        # Return a sequence: importlib import (if not already present - leave to driver to dedupe), then the if
        return cst.FlattenSentinel([importlib_import, if_stmt])


def run_transform_on_file(path: str, dry_run: bool = True) -> tuple[bool, str]:
    src = Path(path).read_text()
    module = cst.parse_module(src)
    transformer = ConvertTryExceptImports()
    modified = module.visit(transformer)
    if not transformer.changed:
        return False, ""
    new_src = modified.code
    if dry_run:
        # produce a unified diff
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as fh:
            fh.write(new_src)
            tmpfile = fh.name
        diff = subprocess.run(
            ["git", "diff", "--no-index", "--", path, tmpfile],
            capture_output=True,
            text=True,
        )
        os.unlink(tmpfile)
        return True, diff.stdout
    else:
        # write back and return change
        Path(path).write_text(new_src)
        return True, "APPLIED"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    results = {}
    for f in args.files:
        try:
            ok, out = run_transform_on_file(f, dry_run=args.dry_run)
            results[f] = {"changed": ok, "output": out}
        except Exception as e:
            results[f] = {"changed": False, "output": f"ERROR: {e!s}"}
    print(json.dumps(results, indent=2))
