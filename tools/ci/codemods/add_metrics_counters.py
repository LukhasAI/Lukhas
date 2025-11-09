#!/usr/bin/env python3
"""
LibCST codemod to add Prometheus Counter imports and missing metric definitions.

Scans for undefined metric names (ending in _total or matching patterns) and:
1. Adds 'from prometheus_client import Counter' if missing
2. Creates Counter definitions for undefined metrics

Usage:
  python3 tools/ci/codemods/add_metrics_counters.py --files oidc.py --dry-run
  python3 tools/ci/codemods/add_metrics_counters.py --files oidc.py --apply
"""

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import libcst as cst


class MetricsCounterTransformer(cst.CSTTransformer):
    """Add Prometheus imports and Counter definitions"""

    def __init__(self, undefined_metrics):
        self.undefined_metrics = undefined_metrics
        self.has_prometheus_import = False
        self.added_import = False
        self.added_counters = False
        super().__init__()

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Check if prometheus_client already imported"""
        if node.module and hasattr(node.module, "value"):
            if node.module.value == "prometheus_client":
                self.has_prometheus_import = True

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """Add imports and metric definitions at module level"""
        if not self.undefined_metrics:
            return updated_node

        body = list(updated_node.body)
        insert_idx = 0

        # Skip module docstring if present
        if body and isinstance(body[0], cst.SimpleStatementLine):
            first_stmt = body[0].body[0]
            if isinstance(first_stmt, cst.Expr) and isinstance(
                first_stmt.value, (cst.SimpleString, cst.ConcatenatedString)
            ):
                insert_idx = 1

        # Find position after imports
        for i in range(insert_idx, len(body)):
            stmt = body[i]
            if not isinstance(stmt, (cst.SimpleStatementLine, cst.EmptyLine)):
                break
            if isinstance(stmt, cst.SimpleStatementLine):
                if not any(
                    isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
                ):
                    break
            insert_idx = i + 1

        new_statements = []

        # Add prometheus import if needed
        if not self.has_prometheus_import:
            import_stmt = cst.parse_statement("from prometheus_client import Counter\n")
            new_statements.append(import_stmt)
            new_statements.append(cst.EmptyLine())
            self.added_import = True

        # Add Counter definitions
        if self.undefined_metrics:
            # Add comment as EmptyLine with comment
            comment_line = cst.EmptyLine(
                indent=False,
                comment=cst.Comment("# Auto-generated Prometheus counters (F821 fix)"),
            )
            new_statements.append(comment_line)

            for metric in sorted(self.undefined_metrics):
                # Create snake_case help text from metric name
                help_text = metric.replace("_", " ").title()
                counter_def = f'{metric} = Counter("{metric}", "{help_text}")'
                new_statements.append(cst.parse_statement(counter_def))
            new_statements.append(cst.EmptyLine())
            self.added_counters = True

        # Insert new statements
        new_body = body[:insert_idx] + new_statements + body[insert_idx:]
        return updated_node.with_changes(body=new_body)


def find_undefined_metrics(filepath: Path, ruff_json_path: Path):
    """Extract undefined metric names from ruff F821 JSON for this file"""
    if not ruff_json_path.exists():
        return set()

    data = json.loads(ruff_json_path.read_text())
    metrics = set()

    file_str = str(filepath.absolute())
    for entry in data:
        if entry.get("filename") == file_str or entry.get("filename", "").endswith(
            filepath.name
        ):
            msg = entry.get("message", "")
            if "Undefined name" in msg:
                # Extract name from message like "Undefined name `foo`"
                match = re.search(r"Undefined name [`']([^'`]+)[`']", msg)
                if match:
                    name = match.group(1)
                    # Check if it looks like a metric (ends with _total, _count, etc.)
                    if any(
                        name.endswith(suffix)
                        for suffix in [
                            "_total",
                            "_count",
                            "_duration",
                            "_bytes",
                            "_requests",
                        ]
                    ):
                        metrics.add(name)

    return metrics


def run_codemod(
    filepath: Path,
    dry_run: bool = True,
    ruff_json: Path = Path("/tmp/ruff_f821_updated.json"),
):
    """Run the metrics counter codemod on a file"""
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return False, ""

    # Find undefined metrics
    undefined = find_undefined_metrics(filepath, ruff_json)
    if not undefined:
        print(f"No undefined metrics found in {filepath}")
        return False, ""

    print(f"Found {len(undefined)} undefined metrics: {', '.join(sorted(undefined))}")

    # Parse and transform
    source = filepath.read_text()
    try:
        module = cst.parse_module(source)
    except Exception as e:
        print(f"Failed to parse {filepath}: {e}")
        return False, ""

    transformer = MetricsCounterTransformer(undefined)
    new_module = module.visit(transformer)

    if not (transformer.added_import or transformer.added_counters):
        print("No changes needed")
        return False, ""

    if dry_run:
        # Generate diff
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp:
            tmp.write(new_module.code)
            tmp_path = tmp.name

        result = subprocess.run(
            ["git", "diff", "--no-index", "--", str(filepath), tmp_path],
            capture_output=True,
            text=True,
        )
        os.unlink(tmp_path)
        return True, result.stdout
    else:
        # Apply changes with backup
        backup_dir = Path("codemod_backups")
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f"{filepath.name}.bak"
        backup_path.write_text(source)

        filepath.write_text(new_module.code)
        print(f"✅ Applied changes to {filepath}")
        print(f"   Backup saved to {backup_path}")
        return True, f"Applied to {filepath}"


def main():
    parser = argparse.ArgumentParser(
        description="Add Prometheus Counter imports and definitions"
    )
    parser.add_argument("--files", nargs="+", required=True, help="Files to process")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show diffs without applying"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument(
        "--ruff-json", default="/tmp/ruff_f821_updated.json", help="Ruff F821 JSON file"
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Must specify --dry-run or --apply")
        return 1

    ruff_json = Path(args.ruff_json)
    if not ruff_json.exists():
        print(f"Ruff JSON not found: {ruff_json}")
        print(
            "Run: python3 -m ruff check --select F821 --output-format json . > /tmp/ruff_f821_updated.json"
        )
        return 1

    for filepath in args.files:
        path = Path(filepath)
        print(f"\n{'=' * 60}")
        print(f"Processing: {path}")
        print("=" * 60)

        changed, output = run_codemod(path, dry_run=args.dry_run, ruff_json=ruff_json)

        if changed:
            print(output)
        else:
            print("No changes needed")

    return 0


if __name__ == "__main__":
    exit(main())
