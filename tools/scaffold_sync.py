#!/usr/bin/env python3
"""
Scaffold synchronization tool for LUKHAS modules.
Maintains single source of truth for module templates.
"""

import sys
import pathlib
import hashlib
import json
import yaml
import shutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import subprocess

@dataclass
class ScaffoldState:
    """Track scaffold state for a module."""
    module_name: str
    scaffold_version: str
    template_commit: str
    last_sync: str
    checksums: Dict[str, str]
    human_overrides: List[str]

class ScaffoldSyncer:
    def __init__(self):
        self.templates_dir = pathlib.Path(__file__).parent.parent / "templates" / "module_scaffold"
        self.scaffold_version = "1.0"
        self.template_version = "v1"
        self.git_commit = self._get_git_commit()

    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _calculate_checksum(self, file_path: pathlib.Path) -> str:
        """Calculate SHA256 checksum of a file."""
        if not file_path.exists():
            return ""

        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def _load_module_manifest(self, module_path: pathlib.Path) -> Dict[str, Any]:
        """Load module manifest if it exists."""
        manifest_path = module_path / "module.manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                return json.load(f)
        return {}

    def _get_module_metadata(self, module_path: pathlib.Path) -> Dict[str, Any]:
        """Extract module metadata for template substitution."""
        manifest = self._load_module_manifest(module_path)
        module_name = module_path.name

        # Default metadata
        metadata = {
            "module_name": module_name,
            "scaffold_version": self.scaffold_version,
            "template_version": self.template_version,
            "template_commit": self.git_commit,
            "module_description": f"LUKHAS {module_name} module",
            "module_tags": ["lukhas", "consciousness"],
            "consciousness_integration": True,
            "awareness_monitoring": True,
            "webauthn_support": False,
            "oauth2_integration": False,
            "matriz_processing": True,
            "dream_integration": False,
            "observability_spans": [
                f"lukhas.{module_name}.operation",
                f"lukhas.{module_name}.processing"
            ]
        }

        # Override with manifest data if available
        if "description" in manifest:
            metadata["module_description"] = manifest["description"]
        if "tags" in manifest:
            metadata["module_tags"] = manifest["tags"]

        if "features" in manifest:
            features = manifest["features"]
            for feature_key in ["consciousness_integration", "awareness_monitoring",
                               "webauthn_support", "oauth2_integration", "matriz_processing",
                               "dream_integration"]:
                if feature_key in features:
                    metadata[feature_key] = features[feature_key]

        if "observability" in manifest and "required_spans" in manifest["observability"]:
            metadata["observability_spans"] = manifest["observability"]["required_spans"]

        return metadata

    def _substitute_template(self, template_content: str, metadata: Dict[str, Any]) -> str:
        """Substitute template variables with module metadata."""
        content = template_content
        for key, value in metadata.items():
            placeholder = "{" + key + "}"
            if isinstance(value, list):
                if key == "observability_spans":
                    yaml_list = yaml.dump(value, default_flow_style=True).strip()
                    content = content.replace(placeholder, yaml_list)
                else:
                    content = content.replace(placeholder, str(value))
            else:
                content = content.replace(placeholder, str(value))
        return content

    def _is_file_human_edited(self, file_path: pathlib.Path) -> bool:
        """Check if file has been edited by humans (lost provenance header)."""
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r') as f:
                first_lines = f.read(500)
                if "@generated LUKHAS scaffold" not in first_lines:
                    return True
                if "human_editable: true" in first_lines:
                    return True
                return False
        except Exception:
            return True  # Assume human edited if can't read

    def sync_module(self, module_path: pathlib.Path, force: bool = False) -> Dict[str, Any]:
        """Sync a single module with the canonical scaffold."""
        results = {
            "module": module_path.name,
            "synced": 0,
            "skipped": 0,
            "errors": 0,
            "human_edited": 0
        }

        metadata = self._get_module_metadata(module_path)

        # Template files to sync
        template_files = [
            "config/config.yaml",
            "config/logging.yaml",
            "config/environment.yaml"
        ]

        for template_rel_path in template_files:
            template_path = self.templates_dir / template_rel_path
            target_path = module_path / template_rel_path

            if not template_path.exists():
                continue

            # Check if human edited
            if not force and self._is_file_human_edited(target_path):
                results["human_edited"] += 1
                continue

            try:
                # Read template
                with open(template_path, 'r') as f:
                    template_content = f.read()

                # Substitute variables
                synced_content = self._substitute_template(template_content, metadata)

                # Create target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Write synced file
                with open(target_path, 'w') as f:
                    f.write(synced_content)

                results["synced"] += 1

            except Exception as e:
                print(f"❌ Error syncing {template_rel_path} to {module_path.name}: {e}")
                results["errors"] += 1

        return results

    def sync_all_modules(self, force: bool = False, pattern: str = "*") -> None:
        """Sync all modules with the canonical scaffold."""
        root_path = pathlib.Path(".")

        # Find matching module directories
        module_dirs = []
        for item in root_path.glob(pattern):
            if (item.is_dir() and
                not item.name.startswith('.') and
                (item / "config").exists()):
                module_dirs.append(item)

        if not module_dirs:
            print(f"No module directories found matching pattern: {pattern}")
            return

        print(f"🔄 Syncing {len(module_dirs)} modules with scaffold v{self.scaffold_version}...")

        total_synced = 0
        total_skipped = 0
        total_human_edited = 0

        for module_dir in sorted(module_dirs):
            results = self.sync_module(module_dir, force=force)
            total_synced += results["synced"]
            total_skipped += results["skipped"]
            total_human_edited += results["human_edited"]

            if results["synced"] > 0:
                print(f"✅ {results['module']}: synced {results['synced']} files")
            elif results["human_edited"] > 0:
                print(f"👤 {results['module']}: {results['human_edited']} human-edited files skipped")
            elif results["errors"] > 0:
                print(f"❌ {results['module']}: {results['errors']} errors")

        print(f"\n📊 Sync Summary:")
        print(f"   Files synced: {total_synced}")
        print(f"   Files skipped: {total_skipped}")
        print(f"   Human-edited files: {total_human_edited}")
        print(f"   Modules processed: {len(module_dirs)}")

        if total_human_edited > 0:
            print(f"\n💡 Use --force to overwrite human-edited files")

def main():
    """Main function for scaffold sync."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync modules with canonical scaffold")
    parser.add_argument("--force", action="store_true",
                       help="Force sync even if files are human-edited")
    parser.add_argument("--pattern", default="*",
                       help="Pattern to match module directories")
    parser.add_argument("--module",
                       help="Sync specific module only")

    args = parser.parse_args()

    syncer = ScaffoldSyncer()

    if args.module:
        module_path = pathlib.Path(args.module)
        if not module_path.exists():
            print(f"❌ Module directory not found: {args.module}")
            return 1
        results = syncer.sync_module(module_path, force=args.force)
        print(f"✅ Synced {results['synced']} files for {args.module}")
    else:
        syncer.sync_all_modules(force=args.force, pattern=args.pattern)

    return 0

if __name__ == "__main__":
    sys.exit(main())