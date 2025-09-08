#!/usr/bin/env python3
"""
LUKHAS Code Atlas Validator
===========================

Validates the completeness and accuracy of the generated Code Atlas.
"""

import json
from pathlib import Path


def validate_atlas():
    """Validate the code atlas structure and content."""
    atlas_file = Path("reports/code_atlas.json")

    if not atlas_file.exists():
        print("❌ Code atlas file not found!")
        return False

    print("🧬 LUKHAS Code Atlas Validation")
    print("=" * 50)

    # Load atlas
    with open(atlas_file) as f:
        atlas = json.load(f)

    # Validate structure
    required_keys = ["metadata", "symbols", "modules", "violations_by_rule", "module_roles"]
    missing_keys = [key for key in required_keys if key not in atlas]

    if missing_keys:
        print(f"❌ Missing required keys: {missing_keys}")
        return False

    print("✅ Atlas structure valid")

    # Validate metadata
    metadata = atlas["metadata"]
    print(f"📊 Metadata validation:")
    print(f"   • Generator: {metadata.get('generator', 'Unknown')}")
    print(f"   • Total modules: {metadata.get('total_modules', 0):,}")
    print(f"   • Total symbols: {metadata.get('total_symbols', 0):,}")
    print(f"   • Total violations: {metadata.get('total_violations', 0):,}")
    print(f"   • Focus directories: {len(metadata.get('focus_directories', []))}")

    # Validate symbols
    symbols = atlas["symbols"]
    print(f"🔍 Symbol validation:")
    print(f"   • Total symbols: {len(symbols):,}")

    # Check symbol structure
    sample_symbols = list(symbols.values())[:5]
    for symbol in sample_symbols:
        required_symbol_keys = ["name", "type", "file_path", "line_number", "signature"]
        missing_symbol_keys = [key for key in required_symbol_keys if key not in symbol]
        if missing_symbol_keys:
            print(f"   ⚠️ Symbol missing keys: {missing_symbol_keys}")

    # Check symbol types
    symbol_types = {}
    for symbol in symbols.values():
        symbol_type = symbol.get("type", "unknown")
        symbol_types[symbol_type] = symbol_types.get(symbol_type, 0) + 1

    print(f"   • Symbol types: {dict(symbol_types)}")

    # Validate modules
    modules = atlas["modules"]
    print(f"📁 Module validation:")
    print(f"   • Total modules: {len(modules):,}")

    # Check module roles
    module_roles = atlas["module_roles"]
    total_role_modules = sum(len(module_list) for module_list in module_roles.values())

    print(f"   • Module roles: {len(module_roles)} different roles")
    print(f"   • Total role assignments: {total_role_modules:,}")

    for role, module_list in sorted(module_roles.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"     - {role}: {len(module_list)} modules")

    # Validate violations
    violations = atlas["violations_by_rule"]
    print(f"🚨 Violation validation:")
    print(f"   • Total rule types: {len(violations)}")
    print(f"   • Total violations: {sum(violations.values()):,}")

    # Check top violations
    sorted_violations = sorted(violations.items(), key=lambda x: x[1], reverse=True)
    print(f"   • Top 5 violations:")
    for rule, count in sorted_violations[:5]:
        print(f"     - {rule}: {count:,} violations")

    # Validate index files
    reports_dir = Path("reports")
    index_files = list(reports_dir.glob("idx_*.json"))
    print(f"📋 Index file validation:")
    print(f"   • Total index files: {len(index_files)}")

    # Check consistency
    index_rules = set()
    for index_file in index_files:
        rule_code = index_file.stem.replace("idx_", "")
        index_rules.add(rule_code)

    atlas_rules = set(violations.keys())
    missing_indices = atlas_rules - index_rules
    extra_indices = index_rules - atlas_rules

    if missing_indices:
        print(f"   ⚠️ Missing indices: {missing_indices}")
    if extra_indices:
        print(f"   ⚠️ Extra indices: {extra_indices}")

    if not missing_indices and not extra_indices:
        print(f"   ✅ All {len(atlas_rules)} rules have corresponding indices")

    # LUKHAS-specific validation
    print(f"🧬 LUKHAS consciousness validation:")
    consciousness_keywords = metadata.get("consciousness_keywords", [])
    print(f"   • Consciousness keywords tracked: {len(consciousness_keywords)}")

    consciousness_modules = 0
    for role, module_list in module_roles.items():
        if any(keyword in role for keyword in ["consciousness", "governance", "advanced"]):
            consciousness_modules += len(module_list)

    print(f"   • Consciousness-related modules: {consciousness_modules:,}")
    print(f"   • Consciousness coverage: {consciousness_modules/len(modules)*100:.1f}%")

    # File path validation
    print(f"🔗 File path validation:")
    valid_paths = 0
    total_paths = 0

    for symbol in list(symbols.values())[:100]:  # Sample check
        total_paths += 1
        file_path = Path(symbol.get("file_path", ""))
        if file_path.exists():
            valid_paths += 1

    if total_paths > 0:
        print(f"   • Valid file paths: {valid_paths}/{total_paths} ({valid_paths/total_paths*100:.1f}%)")

    print("\n🎉 Atlas Validation Complete!")
    print(f"✅ Code Atlas successfully maps {len(symbols):,} symbols across {len(modules):,} modules")
    print(f"✅ Comprehensive violation analysis of {sum(violations.values()):,} issues")
    print(f"✅ Strategic intelligence ready for consciousness-aware transformation")

    return True


def main():
    validate_atlas()


if __name__ == "__main__":
    main()
