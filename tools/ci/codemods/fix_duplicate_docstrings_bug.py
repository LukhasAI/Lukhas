#!/usr/bin/env python3
"""
Fix the F821 bug in fix_duplicate_docstrings.py where 'lines' is undefined.

The fix_file function uses 'lines' without reading the file or defining it.
This codemod adds the missing file read and line split.
"""

import libcst as cst
from pathlib import Path


class FixDuplicateDocstringsBugTransformer(cst.CSTTransformer):
    """Add missing file read operation to fix_file function."""

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        # Only modify the fix_file function
        if updated_node.name.value != "fix_file":
            return updated_node

        # Check if the function already reads content
        body_code = updated_node.body.body[0] if updated_node.body.body else None
        if body_code and isinstance(body_code, cst.SimpleStatementLine):
            first_stmt = body_code.body[0] if body_code.body else None
            if isinstance(first_stmt, cst.Assign):
                targets = first_stmt.targets
                if targets and hasattr(targets[0].target, 'value'):
                    if targets[0].target.value == 'content':
                        # Already has content read
                        return updated_node

        # Add the missing file read at the beginning
        new_statements = [
            # content = path.read_text()
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("content"))],
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Name("path"),
                                attr=cst.Name("read_text")
                            )
                        )
                    )
                ]
            ),
            # lines = content.splitlines()
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("lines"))],
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Name("content"),
                                attr=cst.Name("splitlines")
                            )
                        )
                    )
                ]
            ),
            cst.EmptyLine(whitespace=cst.SimpleWhitespace("")),
        ]

        # Prepend to existing body
        new_body = cst.IndentedBlock(
            body=new_statements + list(updated_node.body.body)
        )

        return updated_node.with_changes(body=new_body)


def main():
    target_file = Path("scripts/fix_duplicate_docstrings.py")
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return 1

    # Read source
    source_code = target_file.read_text()
    
    # Parse
    source_tree = cst.parse_module(source_code)
    
    # Transform
    transformer = FixDuplicateDocstringsBugTransformer()
    modified_tree = source_tree.visit(transformer)
    
    # Write back
    target_file.write_text(modified_tree.code)
    
    print(f"✅ Fixed fix_duplicate_docstrings.py - added missing file read")
    print(f"   Added: content = path.read_text()")
    print(f"   Added: lines = content.splitlines()")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
