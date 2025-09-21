#!/usr/bin/env python3
"""
🧪 LUKHAS MCP Server Integration Test
===================================

Test LUKHAS MCP servers to ensure they're ready for Claude Desktop integration.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_main_server():
    """Test main LUKHAS MCP server"""
    print("🧪 Testing Main LUKHAS MCP Server...")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "lukhas_mcp_server", project_root / "mcp_servers" / "lukhas_mcp_server.py"
        )
        server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server_module)

        # Test knowledge base initialization
        kb = server_module.LUKHASKnowledgeBase(str(project_root))
        print("   ✅ Knowledge base initialized")
        print(f"   📊 Patterns available: {len(kb.patterns)}")
        print(f"   📚 Vocabulary loaded: {len(kb.symbolic_vocabulary)}")

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_consciousness_server():
    """Test consciousness MCP server"""
    print("\n🧠 Testing Consciousness MCP Server...")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "consciousness_server",
            project_root / "mcp_servers" / "lukhas_consciousness" / "server.py",
        )
        server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server_module)

        # Test server initialization
        server = server_module.LukhosConsciousnessServer(str(project_root))
        print("   ✅ Consciousness server initialized")
        print(f"   🔧 Trinity status: {server.constellation_status}")

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_identity_server():
    """Test identity MCP server"""
    print("\n🛡️ Testing Identity MCP Server...")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "identity_server", project_root / "mcp_servers" / "identity" / "server.py"
        )
        server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server_module)

        print("   ✅ Identity server module loaded")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_mcp_imports():
    """Test MCP SDK imports"""
    print("\n📦 Testing MCP SDK...")
    try:
        import mcp.server.stdio  # noqa: F401  # TODO: mcp.server.stdio; consider usi...
        from mcp import types  # noqa: F401  # TODO: mcp.types; consider using impo...
        from mcp.server import Server  # noqa: F401  # TODO: mcp.server.Server; consider us...

        print("   ✅ All MCP imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ MCP import error: {e}")
        return False


def main():
    """Run all MCP integration tests"""
    print("🤖 LUKHAS MCP Server Integration Test Suite")
    print("=" * 50)

    # Set environment variables
    os.environ["LUKHAS_PROJECT_ROOT"] = str(project_root)
    os.environ["PYTHONPATH"] = str(project_root)

    tests = [
        ("MCP SDK", test_mcp_imports),
        ("Main Server", test_main_server),
        ("Consciousness Server", test_consciousness_server),
        ("Identity Server", test_identity_server),
    ]

    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()

    # Summary
    print("\n" + "=" * 50)
    print("🏆 Test Results Summary:")
    print("-" * 30)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! MCP servers are ready for Claude Desktop.")
        print("\n📋 Next Steps:")
        print("   1. Restart Claude Desktop")
        print("   2. Check for MCP server indicators in Claude interface")
        print("   3. Test LUKHAS knowledge integration:")
        print('      • Ask: "What are the Constellation Framework principles?"')
        print('      • Ask: "Generate LUKHAS-compliant variable names"')
        print('      • Ask: "Review this code using LUKHAS patterns"')
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
