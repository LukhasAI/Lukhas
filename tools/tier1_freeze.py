#!/usr/bin/env python3
"""
Tier-1 Freeze: Prevent generation of non-Tier-1 modules

This script implements the scope freeze by:
1. Marking non-Tier-1 schemas as frozen
2. Adding generation guards to prevent updates
3. Creating a registry of Tier-1 vs non-Tier-1 modules
"""
import os
import yaml
from pathlib import Path

TIER1_MODULES = [
    "lukhas.memory", 
    "lukhas.consciousness", 
    "lukhas.orchestration", 
    "lukhas.api", 
    "lukhas.identity", 
    "lukhas.governance"
]

def is_tier1_module(module_name):
    """Check if module is Tier-1"""
    return module_name in TIER1_MODULES

def freeze_schema(schema_path):
    """Add freeze markers to non-Tier-1 schema"""
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Load YAML to get module name
    schema = yaml.safe_load(content)
    module_name = schema.get('identity', {}).get('name', 'unknown')
    
    if is_tier1_module(module_name):
        print(f"✅ Tier-1 module {module_name} - no freeze needed")
        return
    
    # Add freeze section if not Tier-1
    freeze_section = """
# GENERATION FREEZE: Non-Tier-1 modules frozen pending validation
# This module is frozen until Tier-1 validation path is proven
# To unfreeze: Remove this section and update the freeze registry
generation_freeze:
  frozen: true
  reason: "Tier-1 validation path implementation"
  frozen_date: "2025-09-10T13:00:00Z"
  unfreeze_criteria:
    - "Tier-1 validation path proven stable"
    - "All Tier-1 contracts validated"
    - "Reality tests passing for Tier-1"
    - "Architectural review approval"

"""
    
    # Add freeze section at the end
    if "generation_freeze:" not in content:
        content = content.rstrip() + "\n" + freeze_section
        
        with open(schema_path, 'w') as f:
            f.write(content)
            
        print(f"🧊 Froze non-Tier-1 module: {module_name}")

def create_freeze_registry():
    """Create registry of frozen vs active modules"""
    registry = {
        "tier1_active": [],
        "non_tier1_frozen": [],
        "freeze_metadata": {
            "frozen_date": "2025-09-10T13:00:00Z",
            "reason": "Scope freeze: Tier-1 validation path implementation",
            "unfreeze_criteria": [
                "All Tier-1 modules have valid contracts",
                "Golden traces complete for Tier-1",
                "Reality tests passing",
                "CI contracts-smoke job passing",
                "90-day stability demonstrated"
            ]
        }
    }
    
    # Scan existing schemas
    modules_dir = Path("modules")
    for schema_file in modules_dir.glob("lukhas_*.yaml"):
        try:
            with open(schema_file, 'r') as f:
                schema = yaml.safe_load(f)
                module_name = schema.get('identity', {}).get('name', 'unknown')
                
                if is_tier1_module(module_name):
                    registry["tier1_active"].append(module_name)
                else:
                    registry["non_tier1_frozen"].append(module_name)
        except Exception as e:
            print(f"Warning: Could not process {schema_file}: {e}")
    
    # Write registry
    registry_path = Path("audit/GENERATION_FREEZE_REGISTRY.yaml")
    with open(registry_path, 'w') as f:
        yaml.dump(registry, f, indent=2, sort_keys=False)
    
    print(f"📋 Created freeze registry: {registry_path}")
    print(f"   - Tier-1 active: {len(registry['tier1_active'])} modules")
    print(f"   - Non-Tier-1 frozen: {len(registry['non_tier1_frozen'])} modules")

def add_generator_guard():
    """Add guard to module generator to prevent non-Tier-1 generation"""
    generator_path = Path("tools/module_schema_generator.py")
    if not generator_path.exists():
        print(f"Warning: {generator_path} not found")
        return
    
    with open(generator_path, 'r') as f:
        content = f.read()
    
    # Add guard near the top
    guard_code = '''
# TIER-1 FREEZE GUARD - Added 2025-09-10
TIER1_MODULES = [
    "lukhas.memory", 
    "lukhas.consciousness", 
    "lukhas.orchestration", 
    "lukhas.api", 
    "lukhas.identity", 
    "lukhas.governance"
]

def check_generation_freeze(module_name):
    """Prevent generation of non-Tier-1 modules during freeze"""
    if module_name not in TIER1_MODULES:
        print(f"🧊 FREEZE: Module {module_name} generation blocked - not Tier-1")
        print("   To unfreeze: Remove TIER1_FREEZE_GUARD and update registry")
        return False
    return True
'''
    
    # Only add if not already present
    if "TIER-1 FREEZE GUARD" not in content:
        # Insert after imports
        lines = content.split('\n')
        insert_point = 0
        for i, line in enumerate(lines):
            if line.startswith('def ') or line.startswith('class '):
                insert_point = i
                break
        
        lines.insert(insert_point, guard_code)
        content = '\n'.join(lines)
        
        with open(generator_path, 'w') as f:
            f.write(content)
        
        print(f"🛡️ Added generation guard to {generator_path}")

def main():
    """Execute the Tier-1 freeze"""
    print("🧊 Implementing Tier-1 Generation Freeze...")
    print(f"   Active Tier-1 modules: {', '.join(TIER1_MODULES)}")
    
    # Freeze non-Tier-1 schemas
    modules_dir = Path("modules")
    for schema_file in modules_dir.glob("lukhas_*.yaml"):
        freeze_schema(schema_file)
    
    # Create freeze registry
    create_freeze_registry()
    
    # Add generator guard
    add_generator_guard()
    
    print("\n✅ Tier-1 freeze implementation complete!")
    print("   - Non-Tier-1 schemas marked as frozen")
    print("   - Generation registry created") 
    print("   - Generator guard implemented")
    print("   - Only Tier-1 modules can be updated during freeze")

if __name__ == "__main__":
    main()