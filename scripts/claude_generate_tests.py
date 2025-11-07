#!/usr/bin/env python3
"""
Claude Code Test Generator

Uses Claude API to generate test code for LUKHAS components.

Usage:
    python3 scripts/claude_generate_tests.py
    python3 scripts/claude_generate_tests.py --module matriz
    python3 scripts/claude_generate_tests.py --file path/to/file.py
    python3 scripts/claude_generate_tests.py --model claude-3-5-sonnet-20241022
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.env_loader import get_api_key


async def generate_tests_with_claude(
    target: str,
    context: str,
    model: str = "claude-3-5-sonnet-20241022"
):
    """
    Use Claude to generate test code

    Args:
        target: What to generate tests for
        context: Additional context (file content, etc.)
        model: Claude model to use

    Returns:
        Generated test code
    """
    print(f"🤖 Using Claude {model} to generate tests...\n")

    # Get API key
    api_key = get_api_key("anthropic")
    if not api_key:
        print("❌ No API key found. Configure with:")
        print("   python3 scripts/configure_claude_api.py")
        return None

    try:
        import anthropic
    except ImportError:
        print("❌ Anthropic package not installed")
        print("   pip install anthropic")
        return None

    # Build prompt
    prompt = f"""You are a Python test expert helping to write comprehensive tests for the LUKHAS AI system.

TARGET: {target}

CONTEXT:
{context}

REQUIREMENTS:
1. Use pytest framework
2. Include docstrings explaining what each test does
3. Test both success and failure cases
4. Include edge cases
5. Use descriptive test names (test_<what>_<condition>_<expected>)
6. Add type hints
7. Include async tests if the code is async
8. Mock external dependencies appropriately

LUKHAS SPECIFIC:
- The project uses: pytest, asyncio, pydantic
- Follow existing test patterns in tests/ directory
- Use LUKHAS terminology: "quantum-inspired", "bio-inspired", not "quantum computing"

Generate complete, runnable pytest test code. Include:
- Import statements
- Fixture definitions if needed
- Multiple test functions
- Clear assertions
- Helpful comments

Output ONLY the Python test code, no markdown formatting or explanations outside comments."""

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        print("📤 Sending request to Claude...")
        print(f"   Model: {model}")
        print(f"   Max tokens: 4000")
        print()

        response = await client.messages.create(
            model=model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        if response.content:
            test_code = response.content[0].text

            print("✅ Test code generated!")
            print(f"   Input tokens: {response.usage.input_tokens}")
            print(f"   Output tokens: {response.usage.output_tokens}")
            print(f"   Total tokens: {response.usage.input_tokens + response.usage.output_tokens}")

            # Estimate cost (Sonnet pricing)
            input_cost = (response.usage.input_tokens / 1_000_000) * 3.0
            output_cost = (response.usage.output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost
            print(f"   Estimated cost: ${total_cost:.4f}")
            print()

            return test_code
        else:
            print("❌ Empty response from Claude")
            return None

    except anthropic.APIError as e:
        print(f"❌ API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_for_module(module_name: str, model: str):
    """Generate tests for a LUKHAS module"""
    print(f"🎯 Generating tests for module: {module_name}\n")

    # Module descriptions
    modules = {
        "matriz": {
            "description": "MATRIZ is the Memory-Attention-Thought-Action-Decision-Awareness cognitive engine",
            "context": """MATRIZ Components:
- CognitiveEngine: Main orchestrator
- MemorySystem: Persistent state management
- AttentionMechanism: Focus and prioritization
- ReasoningEngine: Logical inference
- DecisionMaker: Action selection
- AwarenessMonitor: Self-monitoring

Key features:
- Async architecture
- <250ms p95 latency requirement
- Symbolic DNA processing
- Bio-inspired adaptation"""
        },
        "guardian": {
            "description": "Guardian is the Constitutional AI safety and governance system",
            "context": """Guardian Components:
- ConstitutionalValidator: Rule enforcement
- ContentModerator: Safety filtering
- PolicyEngine: Constitutional rules
- AuditLogger: Compliance tracking

Key features:
- Transparent rule system
- User appeal process
- Multi-level intervention (warning, soft block, hard block)
- Integration with 8-star Constellation Framework"""
        },
        "identity": {
            "description": "ΛiD (Lambda Identity) is the authentication and identity management system",
            "context": """Identity Components:
- AuthenticationService: User verification
- SessionManager: Session lifecycle
- NamespaceManager: Multi-tenant isolation
- PermissionEngine: Access control

Key features:
- OAuth 2.0 / OpenID Connect
- WebAuthn support
- Cross-domain SSO
- Namespace-based isolation"""
        },
        "memory": {
            "description": "Memory system for persistent state and context preservation",
            "context": """Memory Components:
- MemoryStore: Persistent storage
- ContextManager: Context window management
- RecallEngine: Memory retrieval
- ConsolidationService: Memory compression

Key features:
- Vector embeddings for semantic search
- Time-based decay
- Importance scoring
- Context reconstruction"""
        },
    }

    if module_name.lower() not in modules:
        print(f"❌ Unknown module: {module_name}")
        print(f"   Available: {', '.join(modules.keys())}")
        return None

    module_info = modules[module_name.lower()]
    target = f"{module_name} module - {module_info['description']}"
    context = module_info['context']

    test_code = await generate_tests_with_claude(target, context, model)

    if test_code:
        # Save to file
        output_dir = Path("tests") / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"test_{module_name.lower()}_generated.py"

        with open(output_file, 'w') as f:
            f.write(test_code)

        print(f"💾 Saved to: {output_file}")
        print()
        print("=" * 60)
        print("Generated Test Code:")
        print("=" * 60)
        print(test_code)
        print("=" * 60)

        return output_file
    else:
        return None


async def generate_for_file(file_path: str, model: str):
    """Generate tests for a specific Python file"""
    print(f"🎯 Generating tests for file: {file_path}\n")

    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    if path.suffix != ".py":
        print(f"❌ Not a Python file: {file_path}")
        return None

    # Read file content
    try:
        with open(path) as f:
            code = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

    # Limit context size
    if len(code) > 10000:
        print("⚠️  File is large, using first 10000 characters")
        code = code[:10000] + "\n... (truncated)"

    target = f"File: {path.name}"
    context = f"""File path: {file_path}

Code to test:
```python
{code}
```"""

    test_code = await generate_tests_with_claude(target, context, model)

    if test_code:
        # Suggest output path
        output_file = path.parent / f"test_{path.stem}.py"

        print(f"💡 Suggested output: {output_file}")
        save = input("\nSave to file? (y/N): ").strip().lower()

        if save == 'y':
            with open(output_file, 'w') as f:
                f.write(test_code)
            print(f"💾 Saved to: {output_file}")
        else:
            print("Not saved.")

        print()
        print("=" * 60)
        print("Generated Test Code:")
        print("=" * 60)
        print(test_code)
        print("=" * 60)

        return test_code
    else:
        return None


async def interactive_mode(model: str):
    """Interactive test generation"""
    print("🤖 Claude Test Generator - Interactive Mode\n")
    print("=" * 60)

    print("\nWhat would you like to generate tests for?")
    print()
    print("Options:")
    print("  1. MATRIZ cognitive engine")
    print("  2. Guardian constitutional AI")
    print("  3. ΛiD identity system")
    print("  4. Memory system")
    print("  5. Custom module (enter name)")
    print("  6. Specific file (enter path)")
    print()

    choice = input("Choice (1-6): ").strip()

    module_map = {
        "1": "matriz",
        "2": "guardian",
        "3": "identity",
        "4": "memory",
    }

    if choice in module_map:
        await generate_for_module(module_map[choice], model)

    elif choice == "5":
        module_name = input("\nModule name: ").strip()
        if module_name:
            # Generic module
            context = input("Brief description (optional): ").strip()
            if not context:
                context = f"Python module: {module_name}"

            test_code = await generate_tests_with_claude(
                f"{module_name} module",
                context,
                model
            )

            if test_code:
                print()
                print("=" * 60)
                print("Generated Test Code:")
                print("=" * 60)
                print(test_code)
                print("=" * 60)

    elif choice == "6":
        file_path = input("\nFile path: ").strip()
        if file_path:
            await generate_for_file(file_path, model)

    else:
        print("Invalid choice")


async def main():
    parser = argparse.ArgumentParser(
        description="Generate test code using Claude API"
    )
    parser.add_argument(
        "--module",
        help="Module to generate tests for (matriz, guardian, identity, memory)"
    )
    parser.add_argument(
        "--file",
        help="Python file to generate tests for"
    )
    parser.add_argument(
        "--model",
        default="claude-3-5-sonnet-20241022",
        help="Claude model to use (default: claude-3-5-sonnet-20241022)"
    )

    args = parser.parse_args()

    print("\n🧪 Claude Code Test Generator for LUKHAS")
    print("=" * 60)

    if args.module:
        await generate_for_module(args.module, args.model)
    elif args.file:
        await generate_for_file(args.file, args.model)
    else:
        await interactive_mode(args.model)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
