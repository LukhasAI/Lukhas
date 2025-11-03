#!/usr/bin/env python3
"""
Module Manifest Upgrade Tool - T4/0.01% Module Standardization

Implements safe, idempotent upgrade from legacy directory_index.json to
standardized module.manifest.json with schema validation and layout enforcement.

Commands:
  --discover: Scan modules and generate discovery artifacts (no changes)
  --upgrade:  Create/update manifests and enforce layout (safe merge)
  --validate: Validate all manifests against schema (CI-friendly)

Safety Features:
- Never overwrites valid manifests without --force
- Preserves legacy data under "x_legacy" for rollback
- All operations logged to artifacts for audit trail
- Schema validation with detailed error reporting
"""
from __future__ import annotations


import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

def run_cmd(cmd: str, check: bool = False) -> subprocess.CompletedProcess:
    """Run shell command quietly"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
    return result

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file safely"""
    try:
        if not path.exists():
            return None
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load {path}: {e}")
        return None

def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file with proper formatting"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write('\n')

def get_git_sha() -> str:
    """Get current git SHA"""
    result = run_cmd("git rev-parse HEAD")
    return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"

def stable_module_id(module_name: str) -> str:
    """Generate stable module ID"""
    h = hashlib.sha256()
    h.update(module_name.encode('utf-8'))
    h.update(str(Path.cwd()).encode('utf-8'))
    return f"mod-{h.hexdigest()[:16]}"

def detect_matrix_contract(module_dir: Path) -> Optional[str]:
    """Detect MATRIZ contract file"""
    candidates = [
        f"matrix_{module_dir.name}.json",
        "matrix.json"
    ]

    for candidate in candidates:
        if (module_dir / candidate).exists():
            return candidate

    # Fallback: any matrix_*.json
    for matrix_file in module_dir.glob("matrix_*.json"):
        return matrix_file.name

    return None

def detect_code_layout(module_dir: Path) -> str:
    """Detect code layout pattern"""
    if (module_dir / "src").exists():
        return "src-root"
    return "package-root"

def create_manifest_defaults(module_name: str, module_dir: Path) -> Dict[str, Any]:
    """Create default manifest structure"""
    matrix_contract = detect_matrix_contract(module_dir)
    code_layout = detect_code_layout(module_dir)

    paths = {
        "code": "src" if code_layout == "src-root" else ".",
        "config": "config",
        "tests": "tests",
        "docs": "docs",
        "assets": "assets"
    }

    return {
        "schema_version": "1.0.0",
        "module": module_name,
        "description": f"LUKHAS {module_name} module",
        "ownership": {
            "team": "Core",
            "codeowners": ["@lukhas-core"]
        },
        "layout": {
            "code_layout": code_layout,
            "paths": paths
        },
        "runtime": {
            "language": "python",
            "entrypoints": []
        },
        "matrix": {
            "contract": matrix_contract or "",
            "lane": "L2",
            "gates_profile": "standard"
        },
        "identity": {
            "requires_auth": False,
            "tiers": [],
            "scopes": []
        },
        "links": {
            "repo": "https://github.com/LukhasAI/Lukhas",
            "docs": "./docs/README.md",
            "issues": "https://github.com/LukhasAI/Lukhas/issues"
        },
        "tags": [],
        "observability": {
            "required_spans": [],
            "otel_semconv_version": "1.37.0"
        },
        "tokenization": {
            "enabled": False,
            "chain": "none"
        },
        "dependencies": [],
        "contracts": [matrix_contract] if matrix_contract else []
    }

def merge_manifests(existing: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Merge existing manifest with defaults, preserving existing values"""
    result = dict(defaults)

    # Preserve all existing values
    for key, value in existing.items():
        if key in result:
            if isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = {**result[key], **value}
            else:
                result[key] = value
        else:
            # Unknown fields go to x_legacy
            if "x_legacy" not in result:
                result["x_legacy"] = {}
            result["x_legacy"][key] = value

    return result

def ensure_required_directories(module_dir: Path, manifest: Dict[str, Any]) -> List[str]:
    """Ensure required directories exist and return list of created directories"""
    created = []
    required_dirs = ["docs", "tests", "config", "schema"]

    for dir_name in required_dirs:
        dir_path = module_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path))

            # Create README stubs for docs, tests, config
            if dir_name in ["docs", "tests", "config"]:
                readme_path = dir_path / "README.md"
                if not readme_path.exists():
                    readme_content = f"# {module_dir.name.title()} {dir_name.title()}\n\nThis directory contains {dir_name} for the {module_dir.name} module.\n"
                    readme_path.write_text(readme_content, encoding='utf-8')

    return created

def validate_manifest_with_schema(manifest: Dict[str, Any], schema_path: Path) -> List[str]:
    """Validate manifest against JSON schema"""
    if not JSONSCHEMA_AVAILABLE:
        return ["jsonschema library not available - install with: pip install jsonschema"]

    if not schema_path.exists():
        return [f"Schema file not found: {schema_path}"]

    try:
        schema = load_json(schema_path)
        if not schema:
            return ["Failed to load schema file"]

        jsonschema.validate(manifest, schema)
        return []
    except jsonschema.ValidationError as e:
        return [f"Validation error: {e.message} at {e.absolute_path}"]
    except Exception as e:
        return [f"Schema validation failed: {e}"]

def discover_modules(root_dir: Path) -> Dict[str, Any]:
    """Discover all modules and their current state"""
    print("🔍 Discovering modules...")

    discovery = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_directory": str(root_dir),
        "modules": []
    }

    for module_path in sorted(root_dir.iterdir()):
        if not module_path.is_dir() or module_path.name.startswith('.'):
            continue

        module_info = {
            "name": module_path.name,
            "path": str(module_path),
            "has_legacy_index": (module_path / "directory_index.json").exists(),
            "has_manifest": (module_path / "module.manifest.json").exists(),
            "has_matrix_contract": bool(detect_matrix_contract(module_path)),
            "matrix_contract": detect_matrix_contract(module_path),
            "code_layout": detect_code_layout(module_path),
            "missing_directories": []
        }

        # Check for missing required directories
        required_dirs = ["docs", "tests", "config", "schema"]
        for dir_name in required_dirs:
            if not (module_path / dir_name).exists():
                module_info["missing_directories"].append(dir_name)

        discovery["modules"].append(module_info)

    return discovery

def upgrade_modules(root_dir: Path, force: bool = False) -> Dict[str, Any]:
    """Upgrade all modules to new manifest format"""
    print("📦 Upgrading modules...")

    upgrade_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_directory": str(root_dir),
        "git_sha": get_git_sha(),
        "force_mode": force,
        "modules": []
    }

    for module_path in sorted(root_dir.iterdir()):
        if not module_path.is_dir() or module_path.name.startswith('.'):
            continue

        module_name = module_path.name
        print(f"  Processing {module_name}...")

        module_log = {
            "name": module_name,
            "path": str(module_path),
            "actions": [],
            "errors": []
        }

        try:
            # Check existing manifests
            manifest_path = module_path / "module.manifest.json"
            legacy_path = module_path / "directory_index.json"

            existing_manifest = load_json(manifest_path)
            legacy_manifest = load_json(legacy_path)

            # Skip if valid manifest exists and not forcing
            if existing_manifest and not force:
                schema_path = Path("schemas/module.manifest.schema.json")
                validation_errors = validate_manifest_with_schema(existing_manifest, schema_path)
                if not validation_errors:
                    module_log["actions"].append("skipped - valid manifest exists")
                    upgrade_log["modules"].append(module_log)
                    continue

            # Create defaults and merge
            defaults = create_manifest_defaults(module_name, module_path)

            # Start with legacy data if available
            base_manifest = legacy_manifest or {}
            merged_manifest = merge_manifests(base_manifest, defaults)

            # If we have an existing manifest, merge that too
            if existing_manifest:
                merged_manifest = merge_manifests(existing_manifest, merged_manifest)

            # Save new manifest
            save_json(manifest_path, merged_manifest)
            module_log["actions"].append(f"created/updated {manifest_path}")

            # Ensure required directories
            created_dirs = ensure_required_directories(module_path, merged_manifest)
            if created_dirs:
                module_log["actions"].extend([f"created directory {d}" for d in created_dirs])

            # Rename legacy file if it exists
            if legacy_path.exists():
                backup_path = module_path / f"directory_index.json.backup.{int(time.time())}"
                legacy_path.rename(backup_path)
                module_log["actions"].append(f"backed up legacy index to {backup_path}")

        except Exception as e:
            module_log["errors"].append(str(e))
            print(f"❌ Error processing {module_name}: {e}")

        upgrade_log["modules"].append(module_log)

    return upgrade_log

def validate_modules(root_dir: Path) -> Dict[str, Any]:
    """Validate all module manifests"""
    print("🔍 Validating modules...")

    validation_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_directory": str(root_dir),
        "schema_available": JSONSCHEMA_AVAILABLE,
        "modules": []
    }

    schema_path = Path("schemas/module.manifest.schema.json")
    total_errors = 0

    for module_path in sorted(root_dir.iterdir()):
        if not module_path.is_dir() or module_path.name.startswith('.'):
            continue

        module_name = module_path.name
        manifest_path = module_path / "module.manifest.json"

        module_validation = {
            "name": module_name,
            "path": str(module_path),
            "manifest_exists": manifest_path.exists(),
            "errors": [],
            "warnings": []
        }

        if not manifest_path.exists():
            module_validation["errors"].append("module.manifest.json not found")
            total_errors += 1
        else:
            manifest = load_json(manifest_path)
            if not manifest:
                module_validation["errors"].append("Failed to parse manifest JSON")
                total_errors += 1
            else:
                # Schema validation
                validation_errors = validate_manifest_with_schema(manifest, schema_path)
                if validation_errors:
                    module_validation["errors"].extend(validation_errors)
                    total_errors += len(validation_errors)

                # Check required directories
                required_dirs = ["docs", "tests", "config", "schema"]
                for dir_name in required_dirs:
                    if not (module_path / dir_name).exists():
                        module_validation["warnings"].append(f"Missing directory: {dir_name}")

        validation_log["modules"].append(module_validation)

    validation_log["total_errors"] = total_errors
    validation_log["passed"] = total_errors == 0

    return validation_log

def main():
    parser = argparse.ArgumentParser(description="Module Manifest Upgrade Tool")
    parser.add_argument("--root", default="Lukhas", help="Root directory to scan")
    parser.add_argument("--discover", action="store_true", help="Discover modules and generate artifacts")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade modules to new manifest format")
    parser.add_argument("--validate", action="store_true", help="Validate all manifests")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing valid manifests")
    args = parser.parse_args()

    root_dir = Path(args.root)
    if not root_dir.exists():
        print(f"❌ Root directory not found: {root_dir}")
        sys.exit(1)

    # Ensure artifacts directory exists
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    if args.discover:
        discovery = discover_modules(root_dir)
        save_json(artifacts_dir / "module_manifest.discovery.json", discovery)

        # Generate dry-run markdown
        dry_run_md = "# Module Manifest Discovery\n\n"
        dry_run_md += f"**Root**: `{root_dir}`\n"
        dry_run_md += f"**Generated**: {discovery['timestamp']}\n\n"
        dry_run_md += "| Module | Legacy Index | Manifest | Matrix Contract | Missing Dirs |\n"
        dry_run_md += "|--------|--------------|----------|-----------------|-------------|\n"

        for module in discovery["modules"]:
            legacy = "✅" if module["has_legacy_index"] else "❌"
            manifest = "✅" if module["has_manifest"] else "❌"
            matrix = "✅" if module["has_matrix_contract"] else "❌"
            missing = ", ".join(module["missing_directories"]) or "none"
            dry_run_md += f"| {module['name']} | {legacy} | {manifest} | {matrix} | {missing} |\n"

        (artifacts_dir / "module_manifest.dry_run.md").write_text(dry_run_md, encoding='utf-8')

        print("✅ Discovery complete")
        print(f"📋 Artifacts: {artifacts_dir / 'module_manifest.discovery.json'}")
        print(f"📋 Dry run: {artifacts_dir / 'module_manifest.dry_run.md'}")

    elif args.upgrade:
        upgrade_log = upgrade_modules(root_dir, force=args.force)
        save_json(artifacts_dir / "module_manifest.upgrade.log.jsonl", upgrade_log)

        print("✅ Upgrade complete")
        print(f"📋 Log: {artifacts_dir / 'module_manifest.upgrade.log.jsonl'}")

        # Run validation after upgrade
        validation_log = validate_modules(root_dir)
        if validation_log["passed"]:
            print("✅ All modules validated successfully")
        else:
            print(f"⚠️  {validation_log['total_errors']} validation errors found")

    elif args.validate:
        validation_log = validate_modules(root_dir)
        save_json(artifacts_dir / "module_manifest.validation.log", validation_log)

        if validation_log["passed"]:
            print("✅ All modules validated successfully")
            sys.exit(0)
        else:
            print(f"❌ {validation_log['total_errors']} validation errors found")
            for module in validation_log["modules"]:
                if module["errors"]:
                    print(f"  {module['name']}: {', '.join(module['errors'])}")
            sys.exit(1)

    else:
        print("❌ Please specify --discover, --upgrade, or --validate")
        sys.exit(1)

if __name__ == "__main__":
    main()