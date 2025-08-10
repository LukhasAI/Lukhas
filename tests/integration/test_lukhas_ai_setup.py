#!/usr/bin/env python3
"""
🎭 Quick test of your LUKHAS AI integration setup

🌈 This script tests all your available AI tools and shows how they work together
with LUKHAS patterns and Trinity Framework.

🎓 Tests:
- Ollama local model functionality
- LUKHAS knowledge server
- Trinity documentation generation
- VS Code extension readiness
"""

import asyncio
import json
import subprocess
from pathlib import Path


def test_ollama():
    """Test Ollama local model availability"""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            models = result.stdout.strip()
            print("✅ Ollama is working!")
            print(f"📋 Available models:\n{models}")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return False


def test_lukhas_knowledge_server():
    """Test LUKHAS knowledge server"""
    try:
        import sys

        sys.path.append("/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")

        # Test import
        from ai_orchestration.lukhas_knowledge_server import LUKHASKnowledgeServer

        # Create instance
        server = LUKHASKnowledgeServer("/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")

        # Test basic functionality (sync methods)
        vocabulary = server.symbolic_vocabulary
        templates = server.trinity_templates
        patterns_sync = [p for p in server.patterns if p.category == "naming"]

        print("✅ LUKHAS Knowledge Server working!")
        print(f"📋 Found {len(patterns_sync)} naming patterns")
        print(f"📖 Loaded {len(vocabulary)} symbolic concepts")
        print(f"🎭 Trinity templates: {list(templates.keys())}")
        return True

    except Exception as e:
        print(f"❌ LUKHAS Knowledge Server error: {e}")
        return False


def test_vs_code_extensions():
    """Test VS Code AI extensions"""
    try:
        result = subprocess.run(
            ["code", "--list-extensions"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            extensions = result.stdout
            ai_extensions = []

            if "anthropic.claude-code" in extensions:
                ai_extensions.append("Claude Code")
            if "openai.chatgpt" in extensions:
                ai_extensions.append("ChatGPT")
            if "continue.continue" in extensions:
                ai_extensions.append("Continue.dev")

            print("✅ VS Code AI Extensions:")
            for ext in ai_extensions:
                print(f"  📦 {ext}")
            return True
        else:
            print("❌ VS Code not accessible")
            return False
    except Exception as e:
        print(f"❌ VS Code extension check error: {e}")
        return False


def test_desktop_apps():
    """Test desktop AI applications"""
    apps_found = []

    desktop_apps = [
        ("/Applications/Claude.app", "Claude Desktop"),
        ("/Applications/ChatGPT.app", "ChatGPT Desktop"),
        ("/Applications/Ollama.app", "Ollama Desktop"),
        ("/Applications/Perplexity.app", "Perplexity"),
    ]

    for app_path, app_name in desktop_apps:
        if Path(app_path).exists():
            apps_found.append(app_name)

    print("✅ Desktop AI Applications:")
    for app in apps_found:
        print(f"  🖥️  {app}")

    return len(apps_found) > 0


def test_claude_config():
    """Test Claude Desktop configuration"""
    claude_config_path = (
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    )

    if claude_config_path.exists():
        try:
            with open(claude_config_path) as f:
                config = json.load(f)

            if (
                "customInstructions" in config
                and "LUKHAS" in config["customInstructions"]
            ):
                print("✅ Claude Desktop configured with LUKHAS context!")
                return True
            else:
                print("⚠️  Claude Desktop config exists but no LUKHAS context")
                return False
        except Exception as e:
            print(f"❌ Claude config error: {e}")
            return False
    else:
        print("⚠️  Claude Desktop config not found")
        return False


async def main():
    """Run comprehensive AI setup test"""
    print("🎭 LUKHAS AI Integration Test")
    print("=" * 50)
    print()

    tests = [
        ("🧠 Ollama Local Models", test_ollama),
        ("📚 LUKHAS Knowledge Server", test_lukhas_knowledge_server),
        ("🔌 VS Code Extensions", test_vs_code_extensions),
        ("🖥️  Desktop Applications", test_desktop_apps),
        ("⚙️  Claude Configuration", test_claude_config),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🏆 Score: {passed}/{total} tests passed")

    if passed >= 3:
        print("\n🎉 Your LUKHAS AI setup is ready!")
        print("\n🚀 Next steps:")
        print("1. Open Claude Desktop and test with LUKHAS prompts")
        print("2. Use VS Code AI extensions with Trinity Framework")
        print("3. Try the LUKHAS knowledge server commands")
        print("4. Install more Ollama models as needed")
    else:
        print("\n⚠️  Some issues detected. Check the failed tests above.")

    print("\n🎭 Trinity Framework Example:")
    print('Ask Claude: "Generate Trinity docs for memory_fold_activation function"')


if __name__ == "__main__":
    asyncio.run(main())
