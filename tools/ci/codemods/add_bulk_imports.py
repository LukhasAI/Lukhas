#!/usr/bin/env python3
"""
LibCST codemod to add bulk imports from resolved import map.

Usage:
    python3 add_bulk_imports.py --file <target> --map <json> --dry-run
    python3 add_bulk_imports.py --file <target> --map <json> --apply

Features:
- Inserts import statements after existing imports
- Groups imports by module
- Sorts class names alphabetically
- Creates backup before applying changes
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List

import libcst as cst


class BulkImportInserter(cst.CSTTransformer):
    """Add bulk imports from resolved map."""

    def __init__(self, import_map: Dict[str, str]):
        """
        Args:
            import_map: {classname: module_path}
        """
        self.import_map = import_map
        self.imports_added = False

        # Group imports by module
        self.grouped_imports: Dict[str, List[str]] = {}
        for cls, module in import_map.items():
            self.grouped_imports.setdefault(module, []).append(cls)

        # Sort class names for each module
        for module in self.grouped_imports:
            self.grouped_imports[module].sort()

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """Add imports at the end of the import section."""
        if not self.grouped_imports or self.imports_added:
            return updated_node

        # Find last import statement
        last_import_idx = -1
        for i, stmt in enumerate(updated_node.body):
            if isinstance(stmt, (cst.SimpleStatementLine,)):
                if isinstance(stmt.body[0], (cst.Import, cst.ImportFrom)):
                    last_import_idx = i

        if last_import_idx == -1:
            # No imports found - insert after module docstring
            insert_idx = 0
            if updated_node.body and isinstance(
                updated_node.body[0], cst.SimpleStatementLine
            ):
                first_stmt = updated_node.body[0].body[0]
                if isinstance(first_stmt, cst.Expr) and isinstance(
                    first_stmt.value, cst.SimpleString
                ):
                    insert_idx = 1
        else:
            insert_idx = last_import_idx + 1

        # Build import statements
        new_imports = []

        # Add blank line before new imports
        new_imports.append(cst.EmptyLine(whitespace=cst.SimpleWhitespace("")))

        # Add comment header
        comment_line = cst.EmptyLine(
            whitespace=cst.SimpleWhitespace(""),
            comment=cst.Comment("# F821: Bulk import fix - resolved undefined names"),
        )
        new_imports.append(comment_line)

        for module, classes in sorted(self.grouped_imports.items()):
            if len(classes) == 1:
                # Single import
                import_stmt = cst.SimpleStatementLine(
                    body=[
                        cst.ImportFrom(
                            module=cst.Attribute(
                                value=self._build_module_path(module.split(".")[:-1]),
                                attr=cst.Name(module.split(".")[-1]),
                            )
                            if "." in module
                            else cst.Name(module),
                            names=[cst.ImportAlias(name=cst.Name(classes[0]))],
                        )
                    ]
                )
            else:
                # Multi-line import with parentheses (one class per line)
                import_names = []
                for i, cls in enumerate(classes):
                    import_names.append(
                        cst.ImportAlias(
                            name=cst.Name(cls),
                            comma=cst.Comma(
                                whitespace_after=cst.ParenthesizedWhitespace(
                                    first_line=cst.TrailingWhitespace(
                                        whitespace=cst.SimpleWhitespace(""),
                                        newline=cst.Newline(),
                                    ),
                                    indent=True,
                                )
                            )
                            if i < len(classes) - 1
                            else cst.MaybeSentinel.DEFAULT,
                        )
                    )

                import_stmt = cst.SimpleStatementLine(
                    body=[
                        cst.ImportFrom(
                            module=cst.Attribute(
                                value=self._build_module_path(module.split(".")[:-1]),
                                attr=cst.Name(module.split(".")[-1]),
                            )
                            if "." in module
                            else cst.Name(module),
                            names=import_names,
                            lpar=cst.LeftParen(
                                whitespace_after=cst.ParenthesizedWhitespace(
                                    first_line=cst.TrailingWhitespace(
                                        whitespace=cst.SimpleWhitespace(""),
                                        newline=cst.Newline(),
                                    ),
                                    indent=True,
                                )
                            ),
                            rpar=cst.RightParen(),
                        )
                    ]
                )

            new_imports.append(import_stmt)

        # Insert imports at the determined position
        new_body = (
            list(updated_node.body[:insert_idx])
            + new_imports
            + list(updated_node.body[insert_idx:])
        )

        self.imports_added = True
        return updated_node.with_changes(body=new_body)

    def _build_module_path(self, parts: List[str]) -> cst.BaseExpression:
        """Build nested Attribute nodes for module path."""
        if len(parts) == 1:
            return cst.Name(parts[0])
        elif len(parts) == 2:
            return cst.Attribute(value=cst.Name(parts[0]), attr=cst.Name(parts[1]))
        else:
            # Recursively build nested attributes
            return cst.Attribute(
                value=self._build_module_path(parts[:-1]), attr=cst.Name(parts[-1])
            )


def main():
    parser = argparse.ArgumentParser(description="Add bulk imports from resolved map")
    parser.add_argument("--file", required=True, help="Target Python file")
    parser.add_argument(
        "--map", required=True, help="JSON import map {classname: module}"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show diff without applying"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes")

    args = parser.parse_args()

    if not (args.dry_run or args.apply):
        parser.error("Must specify --dry-run or --apply")

    # Load import map
    import_map = json.load(open(args.map))
    print(f"✅ Loaded import map: {len(import_map)} classes from {args.map}")

    # Read target file
    target = Path(args.file)
    if not target.exists():
        print(f"❌ File not found: {target}")
        return 1

    source_code = target.read_text()

    # Parse and transform
    tree = cst.parse_module(source_code)
    transformer = BulkImportInserter(import_map)
    modified_tree = tree.visit(transformer)

    if not transformer.imports_added:
        print("⚠️  No imports added (already present or no location found)")
        return 0

    new_code = modified_tree.code

    # Generate unified diff
    import difflib

    diff = difflib.unified_diff(
        source_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{target.name}",
        tofile=f"b/{target.name}",
        lineterm="",
    )
    diff_text = "".join(diff)

    if args.dry_run:
        print(f"\n{'=' * 70}")
        print(f"DRY-RUN: Proposed changes to {target.name}")
        print(f"{'=' * 70}\n")
        print(diff_text)
        print("\n✅ Dry-run complete. Use --apply to make changes.")

    if args.apply:
        # Create backup
        backup_path = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, backup_path)
        print(f"✅ Created backup: {backup_path}")

        # Write changes
        target.write_text(new_code)
        print(f"✅ Applied bulk imports to {target}")
        print(f"\n{'=' * 70}")
        print("Changes made:")
        print(f"{'=' * 70}\n")
        print(diff_text)

    return 0


if __name__ == "__main__":
    exit(main())
