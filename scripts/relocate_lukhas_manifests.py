#!/usr/bin/env python3
"""
Relocate manifests from manifests/lukhas/ to manifests/ (flat structure).

This script moves manifests created in manifests/lukhas/<module_path>/ 
to manifests/<module_path>/ to match the Phase 5B flat structure.
"""
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LUKHAS_MANIFESTS = ROOT / "manifests" / "lukhas"
MANIFESTS = ROOT / "manifests"

def main():
    if not LUKHAS_MANIFESTS.exists():
        print("No manifests/lukhas directory found. Nothing to relocate.")
        return 0
    
    # Find all manifest files in manifests/lukhas/
    manifest_files = list(LUKHAS_MANIFESTS.rglob("module.manifest.json"))
    print(f"Found {len(manifest_files)} manifest files to relocate")
    
    relocated = 0
    skipped = 0
    errors = 0
    
    for old_manifest in manifest_files:
        try:
            # Read the manifest to get the actual module path
            with open(old_manifest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            module_path = data.get("module", {}).get("path", "")
            if not module_path:
                print(f"⚠️  Warning: No path in {old_manifest}, skipping")
                skipped += 1
                continue
            
            # Calculate new location based on module path
            new_manifest_dir = MANIFESTS / module_path
            new_manifest = new_manifest_dir / "module.manifest.json"
            
            # Check if destination already exists
            if new_manifest.exists():
                print(f"⚠️  Skipping {module_path}: manifest already exists at correct location")
                skipped += 1
                continue
            
            # Create destination directory
            new_manifest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move the manifest file
            shutil.copy2(old_manifest, new_manifest)
            print(f"✓ Relocated {module_path}")
            
            # Also copy lukhas_context.md if it exists
            old_context = old_manifest.parent / "lukhas_context.md"
            if old_context.exists():
                new_context = new_manifest_dir / "lukhas_context.md"
                if not new_context.exists():
                    shutil.copy2(old_context, new_context)
                    print(f"  + Copied context file")
            
            relocated += 1
            
        except Exception as e:
            print(f"✗ Error processing {old_manifest}: {e}")
            errors += 1
    
    print(f"\n📊 Summary:")
    print(f"  Relocated: {relocated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Errors:    {errors}")
    print(f"\n✓ Relocation complete!")
    
    if errors > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
