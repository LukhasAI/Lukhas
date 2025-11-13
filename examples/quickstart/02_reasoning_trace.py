#!/usr/bin/env python3
"""
LUKHAS Quickstart Example 2: Reasoning Trace Visualization
===========================================================

Demonstrates step-by-step reasoning with visual trace output.
Shows how LUKHAS breaks down complex problems into reasoning steps.

Expected output:
- Multi-step reasoning process
- Visual trace with indentation and colors
- Confidence scores for each step

Troubleshooting:
- Ensure you completed example 01 successfully
- Check that colorama is installed: `pip install colorama`
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    print("⚠️  Install colorama for colored output: pip install colorama")


def display_reasoning_trace(trace: list[dict[str, Any]]) -> None:
    """Display a reasoning trace with visual formatting."""
    print(f"\n{Fore.CYAN if HAS_COLOR else ''}🧠 Reasoning Trace:{Style.RESET_ALL if HAS_COLOR else ''}")
    print("─" * 60)

    for i, step in enumerate(trace, 1):
        # Color based on confidence
        if HAS_COLOR:
            if step.get("confidence", 0) >= 0.8:
                color = Fore.GREEN
            elif step.get("confidence", 0) >= 0.6:
                color = Fore.YELLOW
            else:
                color = Fore.RED
        else:
            color = ""

        print(f"\n{color}Step {i}:{Style.RESET_ALL if HAS_COLOR else ''}")
        print(f"  💭 {step['thought']}")

        if "reasoning" in step:
            print(f"  📊 Reasoning: {step['reasoning']}")

        if "confidence" in step:
            confidence_bar = "█" * int(step["confidence"] * 10)
            print(f"  📈 Confidence: {confidence_bar} {step['confidence']:.1%}")

    print("─" * 60)


def main() -> None:
    """Demonstrate reasoning trace visualization."""
    print("🤖 LUKHAS Quickstart Example 2: Reasoning Trace")
    print("=" * 60)
    print()

    # Complex problem requiring multi-step reasoning
    problem = """
    Problem: Design a consciousness-inspired memory system that can:
    1. Store context across sessions
    2. Retrieve relevant memories efficiently
    3. Forget outdated information gracefully
    """

    print(f"📝 Problem:\n{problem}")
    print()

    # Simulated reasoning trace
    reasoning_trace = [
        {
            "thought": "Identify core requirements: persistence, retrieval, pruning",
            "reasoning": "Breaking down the problem into three main components",
            "confidence": 0.95,
        },
        {
            "thought": "Consider biological memory analogy: hippocampus + neocortex",
            "reasoning": "Bio-inspired approach suggests dual-system memory",
            "confidence": 0.88,
        },
        {
            "thought": "Design short-term buffer (hippocampus analog)",
            "reasoning": "Recent context stored in fast-access buffer with temporal decay",
            "confidence": 0.92,
        },
        {
            "thought": "Design long-term storage (neocortex analog)",
            "reasoning": "Consolidated memories with semantic indexing for retrieval",
            "confidence": 0.87,
        },
        {
            "thought": "Implement forgetting curve for graceful pruning",
            "reasoning": "Ebbinghaus forgetting curve: strength decays exponentially",
            "confidence": 0.90,
        },
        {
            "thought": "Synthesize into unified architecture: Memory Folds",
            "reasoning": "Short-term → consolidation → long-term with natural forgetting",
            "confidence": 0.93,
        },
    ]

    print("🔄 Processing with LUKHAS reasoning engine...")
    print()

    # Display the trace
    display_reasoning_trace(reasoning_trace)

    # Final solution
    print(f"\n{Fore.GREEN if HAS_COLOR else ''}✅ Solution Generated:{Style.RESET_ALL if HAS_COLOR else ''}")
    print(
        """
    Memory Folds Architecture:
    - Short-term: Fast in-memory buffer with 5-minute TTL
    - Consolidation: Background process promotes important memories
    - Long-term: Vector database with semantic search
    - Forgetting: Exponential decay based on access frequency
    """
    )

    print(f"\n{Fore.CYAN if HAS_COLOR else ''}📊 Statistics:{Style.RESET_ALL if HAS_COLOR else ''}")
    avg_confidence = sum(s["confidence"] for s in reasoning_trace) / len(reasoning_trace)
    print(f"   Steps: {len(reasoning_trace)}")
    print(f"   Average Confidence: {avg_confidence:.1%}")
    print(f"   Reasoning Mode: Bio-Inspired")
    print()

    print("✅ Success! You've seen how LUKHAS breaks down complex problems.")
    print()
    print("📚 Next steps:")
    print("   - Try example 03: python3 examples/quickstart/03_memory_persistence.py")
    print("   - Learn about Memory Folds: docs/ARCHITECTURE.md#memory-folds")
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
