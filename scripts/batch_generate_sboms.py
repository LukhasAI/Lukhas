#!/usr/bin/env python3
"""
Batch SBOM Generator for Matrix Tracks
Generates placeholder SBOM files for all modules referenced in matrix contracts.
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import List


def generate_sbom_for_module(module_name: str, output_path: Path) -> dict:
    """Generate a minimal CycloneDX SBOM for a module."""
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{hashlib.sha256((module_name + timestamp).encode()).hexdigest()[:32]}",
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "tools": [
                {
                    "vendor": "LUKHAS AI",
                    "name": "batch-sbom-generator",
                    "version": "1.0.0"
                }
            ],
            "authors": [
                {
                    "name": "LUKHAS Core Team",
                    "email": "core@lukhas.ai"
                }
            ],
            "component": {
                "type": "application",
                "bom-ref": f"lukhas-{module_name.replace('.', '-')}",
                "name": f"lukhas-{module_name.replace('.', '-')}",
                "version": "1.0.0",
                "description": f"LUKHAS {module_name} Module",
                "licenses": [
                    {
                        "license": {
                            "id": "Apache-2.0",
                            "url": "https://www.apache.org/licenses/LICENSE-2.0"
                        }
                    }
                ]
            },
            "manufacture": {
                "name": "LUKHAS AI",
                "url": ["https://lukhas.ai"]
            },
            "properties": [
                {
                    "name": "cdx:reproducible",
                    "value": "true"
                },
                {
                    "name": "lukhas:module",
                    "value": module_name
                },
                {
                    "name": "lukhas:generated",
                    "value": "batch"
                }
            ]
        },
        "components": [
            # Placeholder - in production, would scan actual dependencies
            {
                "type": "library",
                "bom-ref": "python-stdlib",
                "name": "python",
                "version": "3.11+",
                "purl": "pkg:generic/python@3.11",
                "licenses": [
                    {
                        "license": {
                            "id": "PSF-2.0"
                        }
                    }
                ],
                "description": "Python Standard Library"
            }
        ],
        "dependencies": [
            {
                "ref": f"lukhas-{module_name.replace('.', '-')}",
                "dependsOn": ["python-stdlib"]
            }
        ]
    }
    
    return sbom


def find_modules_needing_sboms(pattern: str = "lukhas_website/**/matrix_*.json") -> List[tuple]:
    """Find all modules that need SBOM files."""
    import glob
    
    modules_needing_sboms = []
    contracts = glob.glob(pattern, recursive=True)
    
    print(f"📊 Scanning {len(contracts)} matrix contracts...")
    
    for contract_path in contracts:
        try:
            with open(contract_path) as f:
                contract = json.load(f)
            
            module_name = contract.get('module', Path(contract_path).stem.replace('matrix_', ''))
            supply_chain = contract.get('supply_chain', {})
            sbom_ref = supply_chain.get('sbom_ref', '')
            
            if sbom_ref:
                # Resolve SBOM path
                contract_dir = Path(contract_path).parent
                sbom_path = (contract_dir / sbom_ref).resolve()
                
                if not sbom_path.exists():
                    modules_needing_sboms.append((module_name, sbom_path, contract_path))
                    
        except Exception as e:
            print(f"⚠️  Error processing {contract_path}: {e}")
            continue
    
    return modules_needing_sboms


def main():
    """Main entry point."""
    print("🔧 LUKHAS Batch SBOM Generator")
    print("=" * 60)
    
    # Find modules needing SBOMs
    modules = find_modules_needing_sboms()
    
    if not modules:
        print("✅ All modules already have SBOM files!")
        return 0
    
    print(f"\n📝 Found {len(modules)} modules needing SBOM files\n")
    
    # Generate SBOMs
    generated_count = 0
    for module_name, sbom_path, contract_path in modules:
        try:
            # Ensure output directory exists
            sbom_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate SBOM
            sbom = generate_sbom_for_module(module_name, sbom_path)
            
            # Write SBOM file
            with open(sbom_path, 'w') as f:
                json.dump(sbom, f, indent=2)
            
            print(f"✅ Generated SBOM for {module_name:30s} -> {sbom_path.name}")
            generated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to generate SBOM for {module_name}: {e}")
            continue
    
    print(f"\n🎉 Successfully generated {generated_count}/{len(modules)} SBOM files!")
    
    return 0 if generated_count == len(modules) else 1


if __name__ == "__main__":
    sys.exit(main())
