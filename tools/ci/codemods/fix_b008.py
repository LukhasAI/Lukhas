#!/usr/bin/env python3
"""
LibCST transformer to fix B008: function-call-in-default-argument.

Usage as module (driver provided separately) to run in dry-run or apply mode.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import libcst as cst


def _is_call(node: cst.BaseExpression | None) -> bool:
    return isinstance(node, cst.Call)


def _has_existing_none_check(param_name: str, body: cst.IndentedBlock) -> bool:
    """
    Detect a pattern at the top of the function body like:
      if <param_name> is None:
          <param_name> = <something>
    Searches first few statements to avoid false positives deeper in body.
    """
    for stmt in body.body[:6]:
        if isinstance(stmt, cst.If):
            test = stmt.test
            # We expect a Comparison: Name(param) is None
            if isinstance(test, cst.Comparison):
                left = test.left
                if isinstance(left, cst.Name) and left.value == param_name:
                    for comp in test.comparisons:
                        if isinstance(comp.operator, cst.Is) and isinstance(comp.comparator, cst.Name) and comp.comparator.value == "None":
                            # check that body assigns param_name
                            for inner in stmt.body.body:
                                if isinstance(inner, cst.SimpleStatementLine):
                                    for expr in inner.body:
                                        if isinstance(expr, cst.Assign):
                                            for targ in expr.targets:
                                                if isinstance(targ.target, cst.Name) and targ.target.value == param_name:
                                                    return True
    return False


class FixB008Transformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        params = updated_node.params

        # helper to process a list of Param nodes and produce new ones plus fixes
        def process_param_list(param_list: List[cst.Param]) -> Tuple[List[cst.Param], List[Tuple[str, cst.BaseExpression]]]:
            new_params = []
            fixes: List[Tuple[str, cst.BaseExpression]] = []
            for p in param_list:
                if p.default and _is_call(p.default):
                    # Skip if default already 'None' or if it's a simple literal
                    param_name = p.name.value
                    # Create new param default = None
                    new_p = p.with_changes(default=cst.Name("None"))
                    new_params.append(new_p)
                    fixes.append((param_name, p.default))
                else:
                    new_params.append(p)
            return new_params, fixes

        # process positional, posonly, kwonly
        pos_params, pos_fixes = process_param_list(list(params.params))
        posonly_params, posonly_fixes = process_param_list(list(params.posonly_params))
        kwonly_params, kwonly_fixes = process_param_list(list(params.kwonly_params))

        all_fixes = pos_fixes + posonly_fixes + kwonly_fixes
        if not all_fixes:
            return updated_node  # nothing to do

        # Build new Params object
        new_params_obj = params.with_changes(
            params=pos_params,
            posonly_params=posonly_params,
            kwonly_params=kwonly_params
        )

        # If function has no body or not an IndentedBlock, skip
        body = updated_node.body
        if not isinstance(body, cst.IndentedBlock):
            return updated_node

        prepend_stmts: List[cst.BaseSmallStatement] = []
        for param_name, orig_default in all_fixes:
            # Avoid adding None-check if it already exists
            if _has_existing_none_check(param_name, body):
                continue
            # Create: if <param_name> is None: <param_name> = <orig_default>
            assign = cst.Assign(targets=[cst.AssignTarget(target=cst.Name(param_name))], value=orig_default)
            simple_assign = cst.SimpleStatementLine([assign])
            test = cst.Comparison(left=cst.Name(param_name), comparisons=[cst.ComparisonTarget(operator=cst.Is(), comparator=cst.Name("None"))])
            if_node = cst.If(test=test, body=cst.IndentedBlock(body=[simple_assign]))
            prepend_stmts.append(if_node)

        # If nothing to prepend (all had existing check), just return updated with new params
        if not prepend_stmts:
            return updated_node.with_changes(params=new_params_obj)

        # Create new body with prepended statements followed by existing body
        new_body = cst.IndentedBlock(body=[*prepend_stmts, *body.body])
        return updated_node.with_changes(params=new_params_obj, body=new_body)
