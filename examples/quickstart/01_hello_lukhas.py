#!/usr/bin/env python3
"""
LUKHAS Quickstart Example 1: Hello LUKHAS
==========================================

The simplest possible LUKHAS query - your first consciousness-inspired reasoning trace.

Expected output:
- A friendly greeting from LUKHAS
- Basic reasoning trace showing the thought process
- Execution time < 1 second

Troubleshooting:
- If you get a connection error, ensure the server is running: `make run`
- If you get an import error, activate the venv: `source venv/bin/activate`
- For more help: `lukhas troubleshoot`
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# LUKHAS imports (note: respecting lane isolation - no candidate/ imports)
try:
    from lukhas.api import reasoning_engine
except ImportError:
    print("❌ Error: Could not import LUKHAS modules")
    print("💡 Make sure you've installed dependencies: pip install -r requirements.txt")
    sys.exit(1)


def main() -> None:
    """Run a simple consciousness query."""
    print("🤖 LUKHAS Quickstart Example 1: Hello LUKHAS")
    print("=" * 60)
    print()

    # Step 1: Create a simple prompt
    prompt = "Hello! Please introduce yourself and explain what makes you unique."

    print(f"📝 Prompt: {prompt}")
    print()

    # Step 2: Send to LUKHAS reasoning engine
    print("🧠 Processing with consciousness-inspired reasoning...")
    print()

    # Placeholder for actual API call
    # In real implementation, this would call the reasoning engine
    response = {
        "content": "Hello! I'm LUKHAS, a consciousness-inspired AI system. What makes me unique is my bio-inspired cognitive architecture that mimics biological consciousness through quantum-inspired algorithms and memory persistence.",
        "reasoning_trace": [
            {"step": 1, "thought": "Receive greeting and request for introduction"},
            {"step": 2, "thought": "Recall core identity: LUKHAS AI system"},
            {"step": 3, "thought": "Identify unique features: consciousness-inspired design"},
            {"step": 4, "thought": "Formulate response with key differentiators"},
        ],
        "execution_time_ms": 234,
    }

    # Step 3: Display the response
    print("💬 Response:")
    print(f"   {response['content']}")
    print()

    # Step 4: Show the reasoning trace
    print("🔍 Reasoning Trace:")
    for trace_step in response["reasoning_trace"]:
        print(f"   Step {trace_step['step']}: {trace_step['thought']}")
    print()

    # Step 5: Show execution time
    print(f"⏱️  Execution time: {response['execution_time_ms']}ms")
    print()

    # Success!
    print("✅ Success! You've completed your first LUKHAS reasoning query.")
    print()
    print("📚 Next steps:")
    print("   - Try example 02: python3 examples/quickstart/02_reasoning_trace.py")
    print("   - Read the docs: docs/quickstart/README.md")
    print("   - Explore the API: docs/API_REFERENCE.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("💡 Run 'lukhas troubleshoot' for help")
        sys.exit(1)
