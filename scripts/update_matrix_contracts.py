#!/usr/bin/env python3
"""
Update Matrix Contracts with Supply Chain and Telemetry Configuration
Adds missing supply_chain and telemetry sections to matrix contracts.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def update_contract_supply_chain(contract: Dict, module_name: str) -> bool:
    """Add supply_chain section if missing or null."""
    if contract.get('supply_chain') is None:
        contract['supply_chain'] = {
            "sbom_ref": f"../sbom/{module_name.split('.')[-1]}.cdx.json",
            "licenses": ["Apache-2.0"],
            "sarif_report": f"../artifacts/{module_name.split('.')[-1]}.sarif.json",
            "osv_snapshot": f"../artifacts/{module_name.split('.')[-1]}.osv.json",
            "attestations": [
                {
                    "type": "slsa.provenance",
                    "uri": f"oci://registry/lukhas/{module_name.split('.')[-1]}@sha256:pending"
                }
            ]
        }
        return True
    return False


def update_contract_telemetry(contract: Dict, module_name: str) -> bool:
    """Add telemetry section if missing or null."""
    if contract.get('telemetry') is None:
        module_short = module_name.split('.')[-1]
        contract['telemetry'] = {
            "opentelemetry_semconv_version": "1.37.0",
            "spans": [
                {
                    "name": f"{module_short}.operation",
                    "attrs": [
                        "code.function",
                        "lukhas.module",
                        f"lukhas.{module_short}.operation"
                    ]
                }
            ],
            "metrics": [
                {
                    "name": f"lukhas.{module_short}.latency",
                    "unit": "s",
                    "type": "histogram"
                },
                {
                    "name": f"lukhas.{module_short}.operations",
                    "unit": "1",
                    "type": "counter"
                }
            ]
        }
        return True
    return False


def update_contracts(pattern: str = "lukhas_website/**/matrix_*.json") -> tuple:
    """Update all contracts that need supply_chain or telemetry sections."""
    import glob
    
    contracts = glob.glob(pattern, recursive=True)
    updated_supply_chain = []
    updated_telemetry = []
    
    print(f"📊 Scanning {len(contracts)} matrix contracts...")
    
    for contract_path in contracts:
        try:
            with open(contract_path) as f:
                contract = json.load(f)
            
            module_name = contract.get('module', Path(contract_path).stem.replace('matrix_', ''))
            
            modified = False
            
            # Update supply_chain if needed
            if update_contract_supply_chain(contract, module_name):
                updated_supply_chain.append(module_name)
                modified = True
            
            # Update telemetry if needed
            if update_contract_telemetry(contract, module_name):
                updated_telemetry.append(module_name)
                modified = True
            
            # Write back if modified
            if modified:
                with open(contract_path, 'w') as f:
                    json.dump(contract, f, indent=2)
                print(f"✅ Updated contract for {module_name}")
                
        except Exception as e:
            print(f"❌ Error processing {contract_path}: {e}")
            continue
    
    return updated_supply_chain, updated_telemetry


def main():
    """Main entry point."""
    print("🔧 Matrix Contract Updater")
    print("=" * 60)
    
    updated_supply_chain, updated_telemetry = update_contracts()
    
    print(f"\n📊 Summary:")
    print(f"   Supply chain sections added: {len(updated_supply_chain)}")
    print(f"   Telemetry sections added: {len(updated_telemetry)}")
    
    if updated_supply_chain:
        print(f"\n✅ Updated supply_chain for:")
        for module in sorted(updated_supply_chain):
            print(f"   - {module}")
    
    if updated_telemetry:
        print(f"\n✅ Updated telemetry for:")
        for module in sorted(updated_telemetry):
            print(f"   - {module}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
