#!/usr/bin/env python3
"""
Scaffold diff viewer for LUKHAS modules.
Shows human-friendly diffs between current files and templates.
"""

import argparse
import difflib
import json
import pathlib
import sys
from typing import Any, Dict, List

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Please pip install jinja2", file=sys.stderr)
    sys.exit(2)

# Import from scaffold_sync
try:
    from scaffold_sync import (
        ROOT,
        TEMPLATES,
        get_template_context,
        list_template_files,
        load_module_manifest,
        render_template,
    )
except ImportError:
    # Fallback definitions if import fails
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    TEMPLATES = ROOT / "templates" / "module_scaffold"

    def list_template_files():
        if not TEMPLATES.exists():
            return []
        templates = []
        for p in TEMPLATES.rglob("*.j2"):
            templates.append(p.relative_to(TEMPLATES).as_posix())
        return sorted(templates)

    def load_module_manifest(module_path):
        manifest_path = module_path / "module.manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_template_context(module_name, manifest):
        return {"module": module_name, "module_name": module_name}

    def render_template(env, template_rel, context):
        template = env.get_template(template_rel)
        return template.render(**context)


def diff_module_files(
    module_path: pathlib.Path, templates: List[str], env: Environment, context_lines: int = 3
) -> Dict[str, Any]:
    """Generate diffs for a module's files vs templates."""
    module_name = module_path.name
    manifest = load_module_manifest(module_path)
    context = get_template_context(module_name, manifest)

    results = {
        "module": module_name,
        "diffs": [],
        "missing_files": [],
        "extra_files": [],
        "stats": {"files_compared": 0, "files_different": 0, "files_missing": 0, "lines_added": 0, "lines_removed": 0},
    }

    for template_rel in templates:
        # Calculate target path - render filename to handle template variables
        target_rel = template_rel[:-3]  # Remove .j2 extension

        # Render the filename to substitute variables like {{ module }}
        from jinja2 import Template as JinjaTemplate

        filename_template = JinjaTemplate(target_rel)
        target_rel = filename_template.render(**context)

        target_path = module_path / target_rel

        try:
            # Render template
            new_content = render_template(env, template_rel, context)
            new_lines = new_content.splitlines(keepends=True)

            results["stats"]["files_compared"] += 1

            if target_path.exists():
                # Read current content
                try:
                    current_content = target_path.read_text(encoding="utf-8", errors="ignore")
                    current_lines = current_content.splitlines(keepends=True)
                except Exception as e:
                    current_lines = [f"# Error reading file: {e}\n"]

                # Generate diff
                diff_lines = list(
                    difflib.unified_diff(
                        current_lines,
                        new_lines,
                        fromfile=f"current/{target_rel}",
                        tofile=f"template/{target_rel}",
                        n=context_lines,
                    )
                )

                if diff_lines:
                    results["stats"]["files_different"] += 1

                    # Count added/removed lines
                    for line in diff_lines:
                        if line.startswith("+") and not line.startswith("+++"):
                            results["stats"]["lines_added"] += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            results["stats"]["lines_removed"] += 1

                    results["diffs"].append(
                        {"file": target_rel, "template": template_rel, "diff": "".join(diff_lines), "has_changes": True}
                    )
                else:
                    results["diffs"].append(
                        {"file": target_rel, "template": template_rel, "diff": "", "has_changes": False}
                    )
            else:
                # File is missing
                results["stats"]["files_missing"] += 1
                results["missing_files"].append(
                    {
                        "file": target_rel,
                        "template": template_rel,
                        "content_preview": new_content[:200] + "..." if len(new_content) > 200 else new_content,
                    }
                )

        except Exception as e:
            results["diffs"].append(
                {
                    "file": target_rel,
                    "template": template_rel,
                    "diff": f"Error generating diff: {e}",
                    "has_changes": True,
                    "error": str(e),
                }
            )

    return results


def format_diff_output(results: Dict[str, Any], show_unchanged: bool = False) -> str:
    """Format diff results for human-readable output."""
    lines = []
    module = results["module"]
    stats = results["stats"]

    # Header
    lines.append(f"📋 Scaffold Diff for {module}")
    lines.append("=" * (20 + len(module)))

    # Stats summary
    lines.append(f"Files compared: {stats['files_compared']}")
    lines.append(f"Files different: {stats['files_different']}")
    lines.append(f"Files missing: {stats['files_missing']}")
    lines.append(f"Lines added: {stats['lines_added']}")
    lines.append(f"Lines removed: {stats['lines_removed']}")
    lines.append("")

    # Missing files
    if results["missing_files"]:
        lines.append("🆕 Missing Files:")
        for missing in results["missing_files"]:
            lines.append(f"   📄 {missing['file']} (from {missing['template']})")
            lines.append(f"      Preview: {missing['content_preview'][:100]}...")
        lines.append("")

    # Diffs
    for diff_result in results["diffs"]:
        if diff_result["has_changes"] or show_unchanged:
            if diff_result["has_changes"]:
                icon = "🔄" if "error" not in diff_result else "❌"
                lines.append(f"{icon} {diff_result['file']}")
            else:
                lines.append(f"✅ {diff_result['file']} (no changes)")

            if diff_result["diff"]:
                lines.append(diff_result["diff"])
            lines.append("")

    return "\n".join(lines)


def main():
    """Main diff function."""
    parser = argparse.ArgumentParser(description="Show diffs between current files and scaffold templates")
    parser.add_argument("--modules-root", default="lukhas", help="Root directory containing modules")
    parser.add_argument("--module", help="Show diff for specific module")
    parser.add_argument("--all-modules", action="store_true", help="Show diffs for all modules")
    parser.add_argument("--context", type=int, default=3, help="Number of context lines in diff")
    parser.add_argument("--show-unchanged", action="store_true", help="Show files with no changes")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--summary-only", action="store_true", help="Show only summary statistics")

    args = parser.parse_args()

    if not args.module and not args.all_modules:
        parser.error("Must specify either --module or --all-modules")

    # Setup paths
    modules_root = ROOT / args.modules_root
    if not modules_root.exists():
        print(f"Modules root not found: {modules_root}", file=sys.stderr)
        sys.exit(1)

    if not TEMPLATES.exists():
        print(f"Templates directory not found: {TEMPLATES}", file=sys.stderr)
        sys.exit(1)

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))

    # Get templates
    templates = list_template_files()
    if not templates:
        print("No templates found", file=sys.stderr)
        sys.exit(1)

    # Determine modules to diff
    if args.module:
        modules = [args.module]
        module_path = modules_root / args.module
        if not module_path.exists():
            print(f"Module not found: {args.module}", file=sys.stderr)
            sys.exit(1)
    else:
        modules = [p.name for p in modules_root.iterdir() if p.is_dir() and not p.name.startswith(".")]

    # Generate diffs
    all_results = []
    for module_name in sorted(modules):
        module_path = modules_root / module_name
        if not module_path.is_dir():
            continue

        results = diff_module_files(module_path, templates, env, args.context)
        all_results.append(results)

    # Output results
    if args.json:
        print(json.dumps(all_results, indent=2))
    elif args.summary_only:
        total_compared = sum(r["stats"]["files_compared"] for r in all_results)
        total_different = sum(r["stats"]["files_different"] for r in all_results)
        total_missing = sum(r["stats"]["files_missing"] for r in all_results)
        total_added = sum(r["stats"]["lines_added"] for r in all_results)
        total_removed = sum(r["stats"]["lines_removed"] for r in all_results)

        print("📊 Scaffold Diff Summary")
        print(f"   Modules: {len(all_results)}")
        print(f"   Files compared: {total_compared}")
        print(f"   Files different: {total_different}")
        print(f"   Files missing: {total_missing}")
        print(f"   Lines added: {total_added}")
        print(f"   Lines removed: {total_removed}")
    else:
        for results in all_results:
            # Only show modules with changes unless show_unchanged is True
            has_changes = results["stats"]["files_different"] > 0 or results["stats"]["files_missing"] > 0

            if has_changes or args.show_unchanged:
                print(format_diff_output(results, args.show_unchanged))
                if len(all_results) > 1:
                    print("\n" + "=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
