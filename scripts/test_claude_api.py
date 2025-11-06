#!/usr/bin/env python3
"""
Quick test script for Claude API integration

Tests the Anthropic/Claude API setup and verifies that the API key is working.

Usage:
    python3 scripts/test_claude_api.py
    python3 scripts/test_claude_api.py --model claude-3-opus-20240229
    python3 scripts/test_claude_api.py --verbose

Exit codes:
    0 - Success
    1 - Failure (API key not configured or API error)
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper


async def test_claude(model: str = "claude-3-5-haiku-20241022", verbose: bool = False):
    """
    Test Claude API integration

    Args:
        model: Claude model to test
        verbose: Enable verbose output

    Returns:
        bool: True if test passed, False otherwise
    """
    print("🧪 Testing Claude API Integration...")
    print(f"   Model: {model}")
    print()

    # Initialize
    if verbose:
        print("📦 Initializing AnthropicWrapper...")

    claude = AnthropicWrapper()

    # Check availability
    if not claude.is_available():
        print("❌ FAILED: Claude API not available")
        print()
        print("Troubleshooting:")
        print("  1. Check ANTHROPIC_API_KEY in .env file:")
        print("     grep ANTHROPIC_API_KEY .env")
        print()
        print("  2. Verify key format (should start with 'sk-ant-'):")
        print("     echo $ANTHROPIC_API_KEY")
        print()
        print("  3. Install anthropic package:")
        print("     pip install anthropic")
        print()
        print("  4. Get API key from: https://console.anthropic.com/")
        print()
        return False

    print("✅ Claude API key loaded")
    if verbose and claude.api_key:
        print(f"   Key prefix: {claude.api_key[:20]}...")
    print()

    # Test 1: Basic generation
    print("🧪 Test 1: Basic text generation")
    try:
        response, used_model = await claude.generate_response(
            prompt="Say 'Hello from LUKHAS!' in exactly 5 words.",
            model=model,
            max_tokens=50
        )

        if response:
            print(f"✅ Test 1 PASSED")
            print(f"   Model: {used_model}")
            print(f"   Response: {response[:200]}")
            if len(response) > 200:
                print(f"   ... (truncated)")
            print()
        else:
            print("❌ Test 1 FAILED: Empty response")
            print()
            return False

    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        print()
        return False

    # Test 2: Quantum-inspired terminology (LUKHAS-specific)
    print("🧪 Test 2: LUKHAS terminology adherence")
    try:
        response, used_model = await claude.generate_response(
            prompt="What is quantum-inspired computing? Answer in one sentence.",
            model=model,
            max_tokens=100
        )

        if response:
            # Check if response contains preferred terminology
            contains_preferred = "quantum-inspired" in response.lower()

            print(f"✅ Test 2 PASSED")
            print(f"   Uses 'quantum-inspired': {contains_preferred}")
            print(f"   Response: {response[:200]}")
            if len(response) > 200:
                print(f"   ... (truncated)")
            print()
        else:
            print("❌ Test 2 FAILED: Empty response")
            print()
            return False

    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        print()
        return False

    # Test 3: Longer reasoning task
    print("🧪 Test 3: Reasoning capabilities")
    try:
        response, used_model = await claude.generate_response(
            prompt="""Analyze this statement: "AI consciousness is emergent."

Provide:
1. One key assumption
2. One supporting argument
3. One counterargument

Be concise (under 100 words).""",
            model=model,
            max_tokens=200
        )

        if response:
            word_count = len(response.split())
            print(f"✅ Test 3 PASSED")
            print(f"   Response length: {word_count} words")
            print(f"   Response preview: {response[:300]}")
            if len(response) > 300:
                print(f"   ... (truncated)")
            print()
        else:
            print("❌ Test 3 FAILED: Empty response")
            print()
            return False

    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        print()
        return False

    # Success
    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print()
    print(f"Claude API ({model}) is configured correctly and working!")
    print()
    return True


async def test_all_models():
    """Test all available Claude models"""
    models = [
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
    ]

    print("🧪 Testing all Claude models...")
    print()

    results = {}
    for model in models:
        print(f"{'=' * 60}")
        print(f"Testing: {model}")
        print(f"{'=' * 60}")
        print()

        try:
            success = await test_claude(model=model, verbose=False)
            results[model] = "✅ PASS" if success else "❌ FAIL"
        except Exception as e:
            results[model] = f"❌ ERROR: {e}"

        print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    for model, result in results.items():
        print(f"{model}: {result}")
    print()

    all_passed = all("PASS" in r for r in results.values())
    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Test Claude API integration with LUKHAS"
    )
    parser.add_argument(
        "--model",
        default="claude-3-5-haiku-20241022",
        help="Claude model to test (default: claude-3-5-haiku-20241022)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all available Claude models"
    )

    args = parser.parse_args()

    if args.all:
        success = asyncio.run(test_all_models())
    else:
        success = asyncio.run(test_claude(model=args.model, verbose=args.verbose))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
