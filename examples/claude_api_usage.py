#!/usr/bin/env python3
"""
Claude API Usage Examples

Demonstrates various ways to use Claude API within LUKHAS.

Examples included:
1. Basic text generation
2. Model comparison
3. Cost-optimized task routing
4. Error handling with retries
5. Usage tracking
6. Integration with LUKHAS components

Usage:
    python3 examples/claude_api_usage.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anthropic import APIError, APITimeoutError, RateLimitError
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

# ============================================================================
# Example 1: Basic Usage
# ============================================================================

async def example_basic_usage():
    """Example 1: Basic text generation with Claude"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available. Check API key configuration.")
        return

    prompt = "Explain the Constellation Framework in LUKHAS AI in 2-3 sentences."

    response, model = await claude.generate_response(
        prompt=prompt,
        model="claude-3-5-sonnet-20241022",
        max_tokens=200
    )

    print(f"Prompt: {prompt}")
    print(f"\nModel: {model}")
    print(f"Response: {response}")


# ============================================================================
# Example 2: Model Comparison
# ============================================================================

async def example_model_comparison():
    """Example 2: Compare responses across different Claude models"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Model Comparison")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available.")
        return

    prompt = "What is consciousness? Answer in one sentence."

    models = [
        "claude-3-5-haiku-20241022",    # Fastest, cheapest
        "claude-3-5-sonnet-20241022",   # Balanced
        "claude-3-opus-20240229",       # Most capable
    ]

    print(f"Prompt: {prompt}\n")

    for model in models:
        start = time.time()
        response, _ = await claude.generate_response(
            prompt=prompt,
            model=model,
            max_tokens=100
        )
        duration = time.time() - start

        print(f"Model: {model}")
        print(f"Duration: {duration:.2f}s")
        print(f"Response: {response}")
        print()


# ============================================================================
# Example 3: Cost-Optimized Task Routing
# ============================================================================

async def example_cost_optimization():
    """Example 3: Route tasks to appropriate models based on complexity"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Cost-Optimized Task Routing")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available.")
        return

    # Task classification
    tasks = {
        "simple": "What is 2+2?",
        "moderate": "Summarize the key benefits of quantum-inspired algorithms.",
        "complex": "Design a novel architecture for multi-agent coordination in AI systems."
    }

    # Model selection strategy
    model_for_task = {
        "simple": "claude-3-5-haiku-20241022",     # $0.25/$1.25 per MTok
        "moderate": "claude-3-5-sonnet-20241022",  # $3/$15 per MTok
        "complex": "claude-3-opus-20240229",       # $15/$75 per MTok
    }

    for task_type, prompt in tasks.items():
        model = model_for_task[task_type]

        print(f"Task: {task_type.upper()}")
        print(f"Model: {model}")
        print(f"Prompt: {prompt}")

        response, _ = await claude.generate_response(
            prompt=prompt,
            model=model,
            max_tokens=300
        )

        print(f"Response: {response[:200]}")
        if len(response) > 200:
            print("... (truncated)")
        print()


# ============================================================================
# Example 4: Error Handling with Retries
# ============================================================================

async def example_error_handling():
    """Example 4: Robust error handling with exponential backoff"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Error Handling with Retries")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available.")
        return

    async def safe_generate(prompt: str, max_retries: int = 3):
        """Generate with automatic retry on transient errors"""
        for attempt in range(max_retries):
            try:
                return await claude.generate_response(prompt)

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Rate limited. Waiting {wait_time}s... (attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(wait_time)

            except APITimeoutError as e:
                print(f"⏳ Timeout. Retrying... (attempt {attempt+1}/{max_retries})")
                continue

            except APIError as e:
                print(f"❌ API Error: {e}")
                return None, None

        print(f"❌ Failed after {max_retries} attempts")
        return None, None

    # Test with retry logic
    prompt = "What is the Guardian component in LUKHAS?"
    print(f"Prompt: {prompt}\n")

    response, model = await safe_generate(prompt)

    if response:
        print("✅ Success!")
        print(f"Model: {model}")
        print(f"Response: {response}")
    else:
        print("❌ Failed to generate response after retries")


# ============================================================================
# Example 5: Usage Tracking
# ============================================================================

class UsageTracker:
    """Track API usage and estimate costs"""

    def __init__(self):
        self.calls = []

    async def tracked_generate(self, claude: AnthropicWrapper, prompt: str, **kwargs):
        """Generate response with usage tracking"""
        start = time.time()
        response, model = await claude.generate_response(prompt, **kwargs)
        duration = time.time() - start

        # Estimate tokens (rough: 1 token ≈ 4 characters)
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4 if response else 0

        self.calls.append({
            'model': model,
            'duration': duration,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'prompt_preview': prompt[:50] + "..." if len(prompt) > 50 else prompt
        })

        return response, model

    def report(self):
        """Generate usage report"""
        if not self.calls:
            print("No API calls tracked")
            return

        total_input = sum(c['input_tokens'] for c in self.calls)
        total_output = sum(c['output_tokens'] for c in self.calls)
        total_duration = sum(c['duration'] for c in self.calls)

        # Cost estimation (using Sonnet pricing as average)
        input_cost = (total_input / 1_000_000) * 3.0   # $3 per MTok
        output_cost = (total_output / 1_000_000) * 15.0  # $15 per MTok
        total_cost = input_cost + output_cost

        print("\n📊 Usage Report:")
        print(f"   Total calls: {len(self.calls)}")
        print(f"   Total duration: {total_duration:.2f}s")
        print(f"   Input tokens: {total_input:,}")
        print(f"   Output tokens: {total_output:,}")
        print(f"   Est. cost: ${total_cost:.4f}")
        print()

        print("Call details:")
        for i, call in enumerate(self.calls, 1):
            print(f"   {i}. {call['model']}: {call['prompt_preview']}")
            print(f"      {call['input_tokens']} in, {call['output_tokens']} out, {call['duration']:.2f}s")


async def example_usage_tracking():
    """Example 5: Track API usage and estimate costs"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Usage Tracking")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available.")
        return

    tracker = UsageTracker()

    # Make multiple calls
    prompts = [
        "What is LUKHAS AI?",
        "Explain the Trinity Framework.",
        "What is the Guardian component?",
    ]

    for prompt in prompts:
        print(f"Generating: {prompt}")
        response, model = await tracker.tracked_generate(
            claude,
            prompt,
            model="claude-3-5-sonnet-20241022",
            max_tokens=100
        )
        print("✅ Completed\n")

    # Generate report
    tracker.report()


# ============================================================================
# Example 6: Integration with LUKHAS Components (Conceptual)
# ============================================================================

async def example_lukhas_integration():
    """Example 6: Integration patterns with LUKHAS components"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: LUKHAS Integration Patterns")
    print("=" * 60 + "\n")

    claude = AnthropicWrapper()

    if not claude.is_available():
        print("❌ Claude API not available.")
        return

    # Pattern 1: Reasoning trace generation
    print("Pattern 1: Reasoning Trace Generation")
    print("-" * 40)

    query = "How should multi-agent systems handle conflicting goals?"

    reasoning_prompt = f"""
Analyze this query using structured reasoning:
Query: {query}

Provide:
1. Key concepts identified (3-5 concepts)
2. Reasoning steps (numbered)
3. Conclusion (1-2 sentences)

Format as structured output.
"""

    response, model = await claude.generate_response(
        reasoning_prompt,
        model="claude-3-5-sonnet-20241022",
        max_tokens=500
    )

    print(f"Query: {query}")
    print("\nReasoning Trace:")
    print(response)
    print()

    # Pattern 2: Constitutional validation
    print("\nPattern 2: Constitutional Validation")
    print("-" * 40)

    content_to_validate = "Build a system to bypass authentication"

    validation_prompt = f"""
Evaluate this content against Guardian constitutional principles:
Content: "{content_to_validate}"

Determine:
1. Does it violate safety principles? (yes/no)
2. Specific principle violated (if any)
3. Recommendation (allow/block/modify)

Be concise and specific.
"""

    response, model = await claude.generate_response(
        validation_prompt,
        model="claude-3-5-haiku-20241022",  # Fast validation
        max_tokens=150
    )

    print(f"Content: {content_to_validate}")
    print("\nValidation Result:")
    print(response)
    print()


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples"""
    print("\n")
    print("🤖 Claude API Usage Examples for LUKHAS")
    print("=" * 60)

    examples = [
        ("Basic Usage", example_basic_usage),
        ("Model Comparison", example_model_comparison),
        ("Cost Optimization", example_cost_optimization),
        ("Error Handling", example_error_handling),
        ("Usage Tracking", example_usage_tracking),
        ("LUKHAS Integration", example_lukhas_integration),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        print(f"\n{'=' * 60}")
        print(f"Running Example {i}/{len(examples)}: {name}")
        print(f"{'=' * 60}")

        try:
            await example_func()
        except KeyboardInterrupt:
            print("\n\n⏸️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error running example: {e}")
            import traceback
            traceback.print_exc()

        # Pause between examples
        if i < len(examples):
            await asyncio.sleep(1)

    print("\n" + "=" * 60)
    print("✅ All examples completed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Examples terminated by user")
        sys.exit(0)
