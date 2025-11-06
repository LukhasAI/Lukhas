"""
T4 Codemod Library - AST-Based Violation Fixes

LibCST transformers for violations that ruff cannot autofix.

Transformers:
- RemoveUnusedImport (F401): Remove specific unused imports
- ConvertImportStar (F403): Convert `from x import *` to explicit imports
- FixRUF012 (RUF012): Add ClassVar annotation to mutable class attributes
- FixB904 (B904): Add `from e` clause to exception re-raises

Usage:
  python3 tools/ci/codemods/run_codemod.py --transformer RemoveUnusedImport --file lukhas/api.py
  python3 tools/ci/codemods/run_codemod.py --transformer FixB904 --paths lukhas core --dry-run
"""

from __future__ import annotations

import libcst as cst
from libcst import matchers as m


class RemoveUnusedImport(cst.CSTTransformer):
    """
    Remove specific unused imports identified by name.

    Example:
      from foo import bar, baz  # baz unused
      -> from foo import bar
    """

    def __init__(self, unused_names: set[str]):
        super().__init__()
        self.unused_names = unused_names

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom | cst.RemovalSentinel:
        """Remove unused names from import statement."""
        if isinstance(updated_node.names, cst.ImportStar):
            return updated_node

        if not isinstance(updated_node.names, cst.ImportStar):
            # Filter out unused imports
            new_names = [
                name
                for name in updated_node.names
                if isinstance(name.name, cst.Name) and name.name.value not in self.unused_names
            ]

            if not new_names:
                # Remove entire import if all names unused
                return cst.RemovalSentinel.REMOVE

            if len(new_names) < len(updated_node.names):
                return updated_node.with_changes(names=new_names)

        return updated_node


class ConvertImportStar(cst.CSTTransformer):
    """
    Convert `from x import *` to explicit imports based on usage analysis.

    Example:
      from foo import *
      x = Bar()
      -> from foo import Bar
    """

    def __init__(self, module_name: str, used_names: set[str]):
        super().__init__()
        self.module_name = module_name
        self.used_names = used_names

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        """Replace star import with explicit names."""
        if not isinstance(updated_node.names, cst.ImportStar):
            return updated_node

        # Check if this is the target module
        if m.matches(
            updated_node,
            m.ImportFrom(module=m.Attribute(value=m.Name(self.module_name)))
            | m.ImportFrom(module=m.Name(self.module_name)),
        ):
            # Convert to explicit imports
            import_names = [
                cst.ImportAlias(name=cst.Name(name)) for name in sorted(self.used_names)
            ]

            return updated_node.with_changes(names=import_names)

        return updated_node


class FixRUF012(cst.CSTTransformer):
    """
    Add ClassVar annotation to mutable class attributes.

    Example:
      class Foo:
          items = []  # RUF012
      ->
      class Foo:
          items: ClassVar[list] = []
    """

    def __init__(self):
        super().__init__()
        self.class_stack: list[str] = []
        self.needs_classvar_import = False

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """Track class scope."""
        self.class_stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Exit class scope."""
        self.class_stack.pop()
        return updated_node

    def leave_AnnAssign(
        self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign
    ) -> cst.AnnAssign:
        """Skip if already annotated."""
        return updated_node

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> cst.AnnAssign | cst.Assign:
        """Add ClassVar annotation to mutable defaults."""
        # Only process class-level assignments
        if not self.class_stack:
            return updated_node

        # Check if value is mutable (list, dict, set)
        if isinstance(updated_node.value, (cst.List, cst.Dict, cst.Set)):
            # Single target only
            if len(updated_node.targets) != 1:
                return updated_node

            target = updated_node.targets[0].target

            if not isinstance(target, cst.Name):
                return updated_node

            # Infer type annotation
            if isinstance(updated_node.value, cst.List):
                type_name = "list"
            elif isinstance(updated_node.value, cst.Dict):
                type_name = "dict"
            elif isinstance(updated_node.value, cst.Set):
                type_name = "set"
            else:
                return updated_node

            self.needs_classvar_import = True

            # Convert to annotated assignment
            annotation = cst.Annotation(
                annotation=cst.Subscript(
                    value=cst.Name("ClassVar"),
                    slice=[cst.SubscriptElement(slice=cst.Index(value=cst.Name(type_name)))],
                )
            )

            return cst.AnnAssign(target=target, annotation=annotation, value=updated_node.value)

        return updated_node

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Add ClassVar import if needed."""
        if not self.needs_classvar_import:
            return updated_node

        # Check if ClassVar already imported
        for stmt in updated_node.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.ImportFrom):  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_ci_codemods_library_py_L185"}
                        if m.matches(item.module, m.Name("typing")):
                            # Already has typing import - would need to extend this
                            return updated_node

        # Add import at top
        new_import = cst.SimpleStatementLine(
            body=[
                cst.ImportFrom(
                    module=cst.Name("typing"), names=[cst.ImportAlias(name=cst.Name("ClassVar"))]
                )
            ]
        )

        return updated_node.with_changes(body=[new_import, *updated_node.body])


class FixB904(cst.CSTTransformer):
    """
    Add `from e` clause to exception re-raises in except blocks.

    Example:
      try:
          ...
      except Exception as e:
          raise ValueError("error")  # B904
      ->
      except Exception as e:
          raise ValueError("error") from e
    """

    def __init__(self):
        super().__init__()
        self.except_stack: list[str | None] = []

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> None:
        """Track exception variable name."""
        if node.name:
            self.except_stack.append(node.name.name.value)
        else:
            self.except_stack.append(None)

    def leave_ExceptHandler(
        self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        """Exit except block."""
        self.except_stack.pop()
        return updated_node

    def leave_Raise(self, original_node: cst.Raise, updated_node: cst.Raise) -> cst.Raise:
        """Add `from e` if missing."""
        # Only process raises inside except blocks
        if not self.except_stack:
            return updated_node

        # Already has `from` clause
        if updated_node.cause is not None:
            return updated_node

        # Get exception variable
        exc_var = self.except_stack[-1]
        if exc_var is None:
            return updated_node

        # Add `from e`
        return updated_node.with_changes(cause=cst.From(item=cst.Name(exc_var)))


# Registry
TRANSFORMERS = {
    "RemoveUnusedImport": RemoveUnusedImport,
    "ConvertImportStar": ConvertImportStar,
    "FixRUF012": FixRUF012,
    "FixB904": FixB904,
}
