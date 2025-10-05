#!/usr/bin/env python3
"""
Demo script showing the enhanced plugin registry capabilities.
Demonstrates T4/0.01% constructor-aware instantiation and entry point discovery.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lukhas.core.registry import _instantiate_plugin, register, resolve


class DemoNode:
    """Demo node with name parameter constructor."""

    def __init__(self, name=None):
        self.name = name or "demo"

    def process(self, context):
        return f"{self.name} processed: {context}"


class DemoFactoryNode:
    """Demo node with factory classmethod."""

    def __init__(self, name=None):
        self.name = name or "factory_default"

    @classmethod
    def from_entry_point(cls, name=None):
        instance = cls(name=f"factory_{name}")
        print(f"Created via factory: {instance.name}")
        return instance

    def process(self, context):
        return f"{self.name} factory processed: {context}"


class DemoZeroArgNode:
    """Demo node with zero-arg constructor."""

    def __init__(self):
        self.name = "zero_arg_demo"

    def process(self, context):
        return f"{self.name} processed: {context}"


def demo_manual_registration():
    """Demonstrate manual plugin registration."""
    print("🔧 Manual Plugin Registration Demo")
    print("=" * 40)

    # Register plugins manually
    register("node:demo", DemoNode("manual_demo"))
    register("node:factory", DemoFactoryNode("manual_factory"))
    register("node:zero", DemoZeroArgNode())

    # Resolve and use plugins
    demo_node = resolve("node:demo")
    factory_node = resolve("node:factory")
    zero_node = resolve("node:zero")

    print(f"✅ Demo node: {demo_node.process('test input')}")
    print(f"✅ Factory node: {factory_node.process('test input')}")
    print(f"✅ Zero-arg node: {zero_node.process('test input')}")


def demo_smart_instantiation():
    """Demonstrate smart plugin instantiation."""
    print("\n🧠 Smart Instantiation Demo")
    print("=" * 40)

    # Test different instantiation strategies
    test_cases = [
        ("name_param_node", DemoNode),
        ("factory_node", DemoFactoryNode),
        ("zero_arg_node", DemoZeroArgNode),
    ]

    for name, plugin_class in test_cases:
        obj = _instantiate_plugin(name, plugin_class)
        result = obj.process("smart test") if hasattr(obj, "process") else "Class factory"

        print(f"✅ {name}: {result}")
        print(f"   Type: {type(obj).__name__}")
        print(f"   Name: {getattr(obj, 'name', 'N/A')}")


def demo_compatibility_features():
    """Demonstrate compatibility and migration features."""
    print("\n🔄 Compatibility Features Demo")
    print("=" * 40)

    # Show alias support
    from lukhas.core.registry import ALIASES
    print("Legacy group aliases:")
    for legacy, modern in ALIASES.items():
        print(f"  {legacy} → {modern}")

    # Show environment variable control
    import os
    compat_mode = os.getenv("MATRIZ_COMPAT_IMPORTS", "1")
    print(f"\nCompatibility mode: {'enabled' if compat_mode == '1' else 'disabled'}")

    # Show discovery flag
    discovery_mode = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off")
    print(f"Plugin discovery: {discovery_mode}")


def demo_error_handling():
    """Demonstrate robust error handling."""
    print("\n🛡️ Error Handling Demo")
    print("=" * 40)

    class ProblematicNode:
        def __init__(self, required_arg, another_required):
            self.required_arg = required_arg
            self.another_required = another_required

    # Smart instantiation falls back to class-as-factory
    obj = _instantiate_plugin("problematic", ProblematicNode)
    print(f"✅ Problematic class handled gracefully: {obj}")
    print(f"   Type: {type(obj)}")
    print(f"   Is callable: {callable(obj)}")

    # Can still be used as a factory
    try:
        instance = obj("arg1", "arg2")
        print(f"   Factory usage: {instance.required_arg}, {instance.another_required}")
    except Exception as e:
        print(f"   Factory usage failed: {e}")


if __name__ == "__main__":
    print("🚀 LUKHAS AI Enhanced Plugin Registry Demo")
    print("==========================================")

    demo_manual_registration()
    demo_smart_instantiation()
    demo_compatibility_features()
    demo_error_handling()

    print("\n" + "=" * 40)
    print("🎉 Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Constructor-aware instantiation (T4/0.01%)")
    print("• Factory classmethod support")
    print("• Graceful error handling with fallbacks")
    print("• Legacy compatibility with aliases")
    print("• Production-ready plugin discovery")
    print("=" * 40)
