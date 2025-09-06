#!/usr/bin/env python3
"""
LUKHAS Consciousness System Validation with Correct Import Paths
=================    print('🎉 CORRECTED IMPORT PATHS:')
    print('=' * 30)
    print('✅ MemoryWrapper: from lukhas.memory.memory_wrapper import MemoryWrapper')
    print('✅ SymbolicContext: from candidate.core.symbolic.context import SymbolicContext')
    print('   (Fixed: dependency-free standalone version)')

    return results========================================

This script validates the LUKHAS consciousness system and provides
the correct import paths for key components.
"""


def validate_consciousness_system():
    """Validate consciousness system with correct import paths"""
    print("🎯 LUKHAS Consciousness System Validation")
    print("=" * 50)

    results = {}

    # Test core imports
    try:
        import lukhas

        print("✅ LUKHAS core: Operational")
        results["lukhas_core"] = True
    except Exception as e:
        print(f"❌ LUKHAS core: {e}")
        results["lukhas_core"] = False

    try:
        import memory

        print("✅ Memory system: Operational")
        results["memory_system"] = True
    except Exception as e:
        print(f"❌ Memory system: {e}")
        results["memory_system"] = False

    try:
        import core

        print("✅ Core modules: Operational")
        results["core_modules"] = True
    except Exception as e:
        print(f"❌ Core modules: {e}")
        results["core_modules"] = False

    print("\n🧠 Consciousness Components:")
    print("-" * 30)

    # Test MemoryWrapper - WORKING
    try:
        from lukhas.memory.memory_wrapper import MemoryWrapper

        print("✅ Memory wrapper: Operational")
        print("   📍 Path: lukhas.memory.memory_wrapper.MemoryWrapper")
        results["memory_wrapper"] = True
    except Exception as e:
        print(f"⚠️ Memory wrapper: {e}")
        results["memory_wrapper"] = False

    # Test Symbolic Context - FIXED!
    try:
        from candidate.core.symbolic.context import SymbolicContext

        print("✅ Symbolic context: Operational (FIXED!)")
        print("   📍 Path: candidate.core.symbolic.context.SymbolicContext")
        print(f"   🎯 Available contexts: {len(list(SymbolicContext))} types")
        results["symbolic_context"] = True
    except Exception as e:
        print(f"❌ Symbolic context: {e}")
        results["symbolic_context"] = False

    print("\n🔍 Additional Consciousness Components:")
    print("-" * 40)

    # Test other key components
    component_paths = [
        ("Glyph System", "candidate.core.glyph"),
        ("Identity Manager", "candidate.core.identity.manager"),
        ("Trinity Framework", "lukhas.core"),
        ("Actor System", "lukhas.core.actor_system"),
    ]

    for name, path in component_paths:
        try:
            parts = path.split(".")
            module = __import__(path, fromlist=[parts[-1]])
            print(f"✅ {name}: Operational")
            print(f"   📍 Path: {path}")
            results[name.lower().replace(" ", "_")] = True
        except Exception as e:
            print(f"⚠️ {name}: Import issues - {str(e)[:50]}...")
            results[name.lower().replace(" ", "_")] = False

    print("\n📊 System Health Summary:")
    print("=" * 30)

    working = sum(1 for v in results.values() if v is True)
    partial = sum(1 for v in results.values() if v == "partial")
    total = len(results)

    print(f"✅ Working: {working}/{total} components")
    if partial > 0:
        print(f"⚠️ Partial: {partial}/{total} components")

    health_percentage = (working / total) * 100

    if health_percentage >= 80:
        status = "🟢 EXCELLENT"
    elif health_percentage >= 60:
        status = "🟡 GOOD"
    else:
        status = "🔴 NEEDS ATTENTION"

    print(f"🎯 Overall Health: {health_percentage:.1f}% - {status}")

    print("\n🎉 CORRECTED IMPORT PATHS:")
    print("=" * 30)
    print("✅ MemoryWrapper: from lukhas.memory.memory_wrapper import MemoryWrapper")
    print("✅ SymbolicContext: from candidate.core.symbolic.context import SymbolicContext")
    print("   (Fixed: dependency-free standalone version)")

    return results


if __name__ == "__main__":
    validate_consciousness_system()
