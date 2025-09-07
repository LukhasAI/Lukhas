#!/usr/bin/env python3
"""
Lambda Products Installation Verification Script
Checks that all components are properly installed and functional
"""
import streamlit as st

import sys
from pathlib import Path


def check_component(name, import_path, critical=True):
    """Check if a component can be imported"""
    try:
        exec(f"from {import_path} import *")
        print(f"✅ {name}")
        return True
    except ImportError as e:
        if critical:
            print(f"❌ {name}: {e}")
        else:
            print(f"⚠️  {name}: {e}")
        return False


def main():
    print("=" * 60)
    print("🔍 LAMBDA PRODUCTS - INSTALLATION VERIFICATION")
    print("=" * 60)

    # Add to path
    package_dir = Path(__file__).parent
    sys.path.insert(0, str(package_dir))

    print("\n📋 Checking Components...")
    print("-" * 40)

    results = []

    # Check plugins
    print("\n🔌 Plugin System:")
    results.append(check_component("Plugin Base", "plugins.plugin_base"))
    results.append(check_component("Lambda Adapter", "plugins.lambda_products_adapter"))

    # Check agents
    print("\n🤖 Agent Framework:")
    results.append(check_component("Autonomous Framework", "agents.autonomous_agent_framework"))
    results.append(check_component("Workforce Agents", "agents.lambda_workforce_agents"))

    # Check integrations
    print("\n🔗 Integrations:")
    results.append(check_component(" Adapter", "integrations.lukhas_adapter"))
    results.append(check_component("OpenAI Bridge", "integrations.openai_agi_bridge"))

    # Check config
    print("\n⚙️ Configuration:")
    results.append(check_component("Unified Dreams", "config.unified_dream_system"))

    # Check files
    print("\n📁 Files:")
    files_to_check = [
        "INSTALLATION_GUIDE.md",
        "MANIFEST.json",
        "README_PACKAGE.md",
        "quick_setup.py",
        "requirements.txt",
        "setup.py",
    ]

    for file in files_to_check:
        file_path = package_dir / file
        if file_path.exists():
            print(f"✅ {file}")
            results.append(True)
        else:
            print(f"❌ {file} not found")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"\nTotal Checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed / total} * 100:.1f}%")

    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("Lambda Products package is correctly installed.")
        print("\nNext steps:")
        print("  1. Run: python quick_setup.py")
        print("  2. Deploy agents as needed")
        print("  3. Monitor performance")
    else:
        print("\n⚠️  Some components are missing.")
        print("Please check the failed items above.")
        print("\nTry running:")
        print("  pip install -r requirements.txt")
        print("  python setup.py develop")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
