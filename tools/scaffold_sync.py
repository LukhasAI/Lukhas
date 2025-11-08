#!/usr/bin/env python3
"""
Scaffold sync engine for LUKHAS modules.
Safely syncs templates to modules with provenance tracking.
"""

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Please pip install jinja2", file=sys.stderr)
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "module_scaffold"
IGNORE_FILE = TEMPLATES / ".scaffoldignore"
IGNORE = []

# Load ignore patterns
if IGNORE_FILE.exists():
    IGNORE = [line.strip() for line in IGNORE_FILE.read_text().splitlines()
              if line.strip() and not line.startswith('#')]

PROV_PREFIX = "# @generated LUKHAS scaffold v1"

def sha256_bytes(b: bytes) -> str:
    """Calculate SHA256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()

def load_module_manifest(module_path: pathlib.Path) -> dict[str, Any]:
    """Load module manifest for template context."""
    manifest_path = module_path / "module.manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_template_context(module_name: str, manifest: dict[str, Any]) -> dict[str, Any]:
    """Generate template context from module data."""
    context = {
        "module": module_name,
        "module_name": module_name,
        "module_title": module_name.replace("_", " ").title(),
        "module_entrypoints": [],
        "module_description": f"LUKHAS {module_name} module",
        "module_tags": ["lukhas", "consciousness"]
    }

    # Extract manifest data comprehensively
    if "description" in manifest:
        context["module_description"] = manifest["description"]

    if "tags" in manifest:
        context["module_tags"] = manifest["tags"]

    if "runtime" in manifest:
        if "entrypoints" in manifest["runtime"]:
            context["module_entrypoints"] = manifest["runtime"]["entrypoints"]
        if "language" in manifest["runtime"]:
            context["module_language"] = manifest["runtime"]["language"]

    # Extract ownership information
    if "ownership" in manifest:
        if "team" in manifest["ownership"]:
            context["module_team"] = manifest["ownership"]["team"]
        if "codeowners" in manifest["ownership"]:
            context["module_owners"] = ", ".join(manifest["ownership"]["codeowners"])
        if "slack_channel" in manifest["ownership"]:
            context["module_slack"] = manifest["ownership"]["slack_channel"]

    # Extract matrix information
    if "matrix" in manifest:
        if "lane" in manifest["matrix"]:
            context["module_lane"] = manifest["matrix"]["lane"]
        if "contract" in manifest["matrix"]:
            context["module_contract"] = manifest["matrix"]["contract"]

    # Extract identity requirements
    if 'identity' in manifest and 'tiers' in manifest['identity']:
        context["module_tier"] = manifest["identity"]["tiers"][0] if manifest["identity"]["tiers"] else "T3"

    # Extract observability requirements
    if "observability" in manifest and "required_spans" in manifest["observability"]:
        context["module_spans"] = manifest["observability"]["required_spans"]

    # Add default values for optional fields
    context.setdefault("module_tier", "T3")
    context.setdefault("module_lane", "development")
    context.setdefault("module_team", "consciousness")
    context.setdefault("module_owner", "team-consciousness@ai")
    context.setdefault("module_coverage", "pending")
    context.setdefault("module_rate_limit", "1000 req/s")
    context.setdefault("module_memory_budget", "512MB heap, 1GB total")
    context.setdefault("module_latency_budget", "p50 < 100ms, p99 < 500ms")

    return context

def render_template(env: Environment, template_rel: str, context: dict[str, Any]) -> str:
    """Render template with context and add provenance header."""
    template = env.get_template(template_rel)
    content = template.render(**context).rstrip() + "\n"

    # Calculate template hash from file content
    template_path = TEMPLATES / template_rel
    template_bytes = template_path.read_bytes()
    template_hash = sha256_bytes(template_bytes)

    # Create provenance header
    header = (
        f"{PROV_PREFIX}\n"
        f"# template: module_scaffold/{template_rel}\n"
        f"# template_sha256: {template_hash}\n"
        f"# module: {context['module']}\n"
        f"# do_not_edit: false\n"
        f"#\n"
    )

    return header + content

def list_template_files() -> list[str]:
    """List all template files to process."""
    if not TEMPLATES.exists():
        return []

    templates = []
    for p in TEMPLATES.rglob("*"):
        if p.is_dir():
            continue

        rel_path = p.relative_to(TEMPLATES).as_posix()

        # Skip ignored patterns
        if any(rel_path.startswith(ig.strip("/")) for ig in IGNORE if ig.strip()):
            continue

        if rel_path.endswith(".j2"):
            templates.append(rel_path)

    return sorted(templates)

def is_generated_file(file_path: pathlib.Path) -> bool:
    """Check if file has provenance header."""
    if not file_path.exists():
        return False

    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            return first_line == PROV_PREFIX.strip()
    except Exception:
        return False

def should_overwrite(target_path: pathlib.Path, new_content: str, force: bool = False) -> bool:
    """Determine if file should be overwritten."""
    if not target_path.exists():
        return True

    if force:
        return True

    # Only overwrite if it's a generated file
    if is_generated_file(target_path):
        # Check if content has changed
        try:
            current_content = target_path.read_text(encoding='utf-8', errors='ignore')
            return current_content != new_content
        except Exception:
            return True

    return False  # Don't overwrite human-edited files

def sync_module(module_path: pathlib.Path, templates: list[str],
                env: Environment, dry_run: bool = False,
                force: bool = False) -> dict[str, Any]:
    """Sync templates to a single module."""
    module_name = module_path.name
    manifest = load_module_manifest(module_path)
    context = get_template_context(module_name, manifest)

    results = {
        "module": module_name,
        "actions": [],
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0
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

            # Determine action
            action = "skip"
            if should_overwrite(target_path, new_content, force):
                action = "write" if not dry_run else "would_write"

                if not dry_run:
                    # Ensure parent directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write file
                    target_path.write_text(new_content, encoding='utf-8')

                    if target_path.exists():
                        results["updated" if target_path.stat().st_size > 0 else "created"] += 1
                    else:
                        results["created"] += 1
                else:
                    results["created"] += 1
            else:
                results["skipped"] += 1

            results["actions"].append({
                "template": template_rel,
                "target": str(target_path),
                "action": action
            })

        except Exception as e:
            results["errors"] += 1
            results["actions"].append({
                "template": template_rel,
                "target": str(target_path),
                "action": "error",
                "error": str(e)
            })

    return results

def main():
    """Main scaffold sync function."""
    parser = argparse.ArgumentParser(description="Sync module scaffolds with provenance tracking")
    parser.add_argument("--modules-root", default="lukhas",
                       help="Root directory containing modules")
    parser.add_argument("--only-module", action="append",
                       help="Sync specific module(s) only")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--force", action="store_true",
                       help="Overwrite human-edited files")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")

    args = parser.parse_args()

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

    # Get templates and modules
    templates = list_template_files()
    if not templates:
        print("No templates found", file=sys.stderr)
        sys.exit(1)

    # Find modules
    all_modules = [
        p.name for p in modules_root.iterdir()
        if p.is_dir() and not p.name.startswith('.')
    ]

    if args.only_module:
        modules = [m for m in all_modules if m in set(args.only_module)]
        if not modules:
            print(f"No matching modules found: {args.only_module}", file=sys.stderr)
            sys.exit(1)
    else:
        modules = all_modules

    # Sync modules
    all_results = []
    total_created = 0
    total_updated = 0
    total_skipped = 0
    total_errors = 0

    for module_name in sorted(modules):
        module_path = modules_root / module_name
        if not module_path.is_dir():
            continue

        result = sync_module(module_path, templates, env, args.dry_run, args.force)
        all_results.append(result)

        total_created += result["created"]
        total_updated += result["updated"]
        total_skipped += result["skipped"]
        total_errors += result["errors"]

    # Output results
    if args.json:
        output = {
            "summary": {
                "templates": len(templates),
                "modules": len(modules),
                "created": total_created,
                "updated": total_updated,
                "skipped": total_skipped,
                "errors": total_errors
            },
            "results": all_results
        }
        print(json.dumps(output, indent=2))
    else:
        print("📋 Scaffold Sync Results")
        print(f"   Templates: {len(templates)}")
        print(f"   Modules: {len(modules)}")
        print(f"   Created: {total_created}")
        print(f"   Updated: {total_updated}")
        print(f"   Skipped: {total_skipped}")
        print(f"   Errors: {total_errors}")

        if total_errors > 0:
            print("\n❌ Errors occurred:")
            for result in all_results:
                for action in result["actions"]:
                    if action["action"] == "error":
                        print(f"   {result['module']}: {action['error']}")

        if not args.dry_run and (total_created > 0 or total_updated > 0):
            print("\n✅ Scaffold sync completed successfully")

    return 0 if total_errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
