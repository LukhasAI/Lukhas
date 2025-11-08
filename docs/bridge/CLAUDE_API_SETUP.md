# Claude API Setup Guide

> **🤖 Complete Guide to Integrating Claude Web API with LUKHAS**

**Version**: 1.0
**Date**: 2025-11-06
**Status**: Active Documentation

---

## Overview

LUKHAS has built-in support for Anthropic's Claude API through the `AnthropicWrapper` in the bridge layer. This guide covers setup, configuration, and usage of Claude models within LUKHAS.

**Supported Models**:
- Claude 3 Opus (claude-3-opus-20240229)
- Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- Claude 3 Sonnet (claude-3-sonnet-20240229)
- Claude 3 Haiku (claude-3-haiku-20240307)
- Claude 3.5 Haiku (claude-3-5-haiku-20241022)

---

## Prerequisites

### 1. Anthropic API Key

Obtain an API key from Anthropic:

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy your API key (starts with `sk-ant-`)

**Pricing** (as of 2025-11):
- **Haiku**: $0.25/MTok input, $1.25/MTok output (fastest, most economical)
- **Sonnet**: $3/MTok input, $15/MTok output (balanced performance)
- **Opus**: $15/MTok input, $75/MTok output (most capable)

### 2. Python Package

Install the Anthropic Python SDK:

```bash
pip install anthropic>=0.40.0
```

Or add to your `requirements.txt`:
```
anthropic>=0.40.0
```

---

## Configuration

### Method 1: Environment File (Recommended)

LUKHAS automatically loads API keys from `.env` files in these locations (priority order):

1. `/Users/agi_dev/LOCAL-REPOS/Lukhas/.env` (project root)
2. `./.env` (current directory)
3. `../.env` (parent directory)
4. `~/.lukhas/.env` (user home)

**Setup**:

1. **Copy template** (if starting fresh):
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   cp .env.example .env
   ```

2. **Edit `.env` file**:
   ```bash
   nano .env
   # or
   code .env
   ```

3. **Add your API key**:
   ```bash
   # Anthropic: https://console.anthropic.com/
   ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE
   ```

4. **Save and verify**:
   ```bash
   grep ANTHROPIC_API_KEY .env
   # Should output: ANTHROPIC_API_KEY=sk-ant-...
   ```

### Method 2: Environment Variable (Alternative)

Set directly in your shell session:

```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR_ACTUAL_KEY_HERE"
```

Add to `~/.zshrc` or `~/.bashrc` for persistence:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY"' >> ~/.zshrc
source ~/.zshrc
```

### Method 3: macOS Keychain (Most Secure)

Store API key in macOS Keychain:

```bash
# Store key
security add-generic-password \
  -a "$USER" \
  -s "LUKHAS_ANTHROPIC_API_KEY" \
  -w "sk-ant-YOUR_KEY"

# Retrieve key (for testing)
security find-generic-password \
  -a "$USER" \
  -s "LUKHAS_ANTHROPIC_API_KEY" \
  -w
```

Then load in Python:
```python
import subprocess

def get_keychain_api_key():
    cmd = [
        'security', 'find-generic-password',
        '-a', os.getenv('USER'),
        '-s', 'LUKHAS_ANTHROPIC_API_KEY',
        '-w'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

os.environ['ANTHROPIC_API_KEY'] = get_keychain_api_key()
```

---

## Usage

### Basic Usage

```python
import asyncio
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def main():
    # Initialize wrapper (auto-loads API key from .env)
    claude = AnthropicWrapper()

    # Check availability
    if not claude.is_available():
        print("❌ Claude API not available. Check API key configuration.")
        return

    # Generate response
    response, model = await claude.generate_response(
        prompt="Explain quantum-inspired algorithms in LUKHAS AI",
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000
    )

    print(f"Model: {model}")
    print(f"Response: {response}")

# Run
asyncio.run(main())
```

### Advanced Usage: Streaming Responses

For real-time token streaming (requires custom implementation):

```python
async def stream_response():
    claude = AnthropicWrapper()

    # Note: Current wrapper doesn't expose streaming directly
    # You can access the underlying client:
    if claude.async_client:
        async with claude.async_client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": "Write a poem about AI consciousness"}
            ]
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)
            print()  # newline
```

### Model Selection Strategy

Choose model based on task complexity:

```python
# Quick, simple tasks (documentation lookup, simple Q&A)
model = "claude-3-5-haiku-20241022"  # Fastest, cheapest

# Balanced tasks (reasoning, analysis, most applications)
model = "claude-3-5-sonnet-20241022"  # Recommended default

# Complex tasks (deep reasoning, creative writing, research)
model = "claude-3-opus-20240229"  # Most capable
```

### Integration with MATRIZ

Use Claude for cognitive reasoning traces:

```python
from matriz.cognitive_engine import CognitiveEngine
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def reason_with_claude(query: str):
    claude = AnthropicWrapper()
    engine = CognitiveEngine()

    # Generate reasoning trace using Claude
    reasoning_prompt = f"""
    Analyze this query using structured reasoning:
    Query: {query}

    Provide:
    1. Key concepts identified
    2. Reasoning steps
    3. Conclusion
    """

    response, model = await claude.generate_response(
        reasoning_prompt,
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000
    )

    # Process with MATRIZ cognitive engine
    trace = await engine.create_reasoning_trace(
        query=query,
        llm_output=response,
        model=model
    )

    return trace
```

---

## Configuration Options

### Model Parameters

```python
response, model = await claude.generate_response(
    prompt="Your query",
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,              # Max tokens to generate (default: 2000)
    temperature=0.7,              # Randomness 0-1 (default: 1.0)
    top_p=0.9,                    # Nucleus sampling (default: -1 = disabled)
    top_k=40,                     # Top-k sampling (default: -1 = disabled)
    stop_sequences=["Human:", "AI:"],  # Stop generation at these strings
)
```

### System Guidance

The wrapper automatically includes LUKHAS-specific guidance:
```python
guidance = (
    "When describing methods, prefer 'quantum-inspired' and 'bio-inspired'. "
    "Refer to the project as 'Lukhas AI'."
)
```

To customize, modify `anthropic_wrapper.py` line 79-82.

### Context Window Management

Claude models have large context windows:
- Haiku: 200K tokens
- Sonnet: 200K tokens
- Opus: 200K tokens

For long conversations, track token usage:

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)

# Access token usage
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
```

---

## Testing Setup

### Quick Test Script

Create `scripts/test_claude_api.py`:

```python
#!/usr/bin/env python3
"""Quick test script for Claude API integration"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def test_claude():
    print("🧪 Testing Claude API Integration...")

    # Initialize
    claude = AnthropicWrapper()

    # Check availability
    if not claude.is_available():
        print("❌ FAILED: Claude API not available")
        print("   Check: ANTHROPIC_API_KEY in .env file")
        return False

    print("✅ Claude API key loaded")

    # Test generation
    try:
        response, model = await claude.generate_response(
            prompt="Say 'Hello from LUKHAS!' in exactly 5 words.",
            model="claude-3-5-haiku-20241022",  # Fastest for testing
            max_tokens=50
        )

        print(f"✅ Response generated using {model}")
        print(f"   Response: {response[:100]}...")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_claude())
    sys.exit(0 if success else 1)
```

**Run test**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 scripts/test_claude_api.py
```

**Expected output**:
```
🧪 Testing Claude API Integration...
✅ Anthropic initialized with key: sk-ant-api03-abc123...
✅ Claude API key loaded
✅ Response generated using claude-3-5-haiku-20241022
   Response: Hello from LUKHAS, everyone!
```

---

## Troubleshooting

### Error: "Anthropic package not installed"

**Solution**:
```bash
pip install anthropic
# or
pip install -r requirements.txt
```

### Error: "Anthropic client not initialized"

**Cause**: API key not found or invalid

**Solution**:
1. Check `.env` file exists: `ls -la .env`
2. Verify key is set: `grep ANTHROPIC_API_KEY .env`
3. Check key format: Should start with `sk-ant-`
4. Test key manually:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-5-haiku-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   ```

### Error: "Rate limit exceeded"

**Cause**: API rate limit reached (depends on your tier)

**Solution**:
- Wait and retry with exponential backoff
- Upgrade API tier at console.anthropic.com
- Reduce request frequency
- Implement request queuing

### Error: "Invalid model"

**Cause**: Model name incorrect or deprecated

**Solution**: Use current model names:
- ✅ `claude-3-5-sonnet-20241022`
- ✅ `claude-3-5-haiku-20241022`
- ❌ `claude-3-sonnet` (too vague)
- ❌ `claude-v1` (deprecated)

### Error: "Context length exceeded"

**Cause**: Input too long for model's context window

**Solution**:
- Truncate input to fit window (200K tokens for Claude 3)
- Split into multiple requests
- Use conversation compression strategies

---

## Best Practices

### 1. API Key Security

**DO**:
- ✅ Store keys in `.env` file (gitignored)
- ✅ Use environment variables
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/staging/production

**DON'T**:
- ❌ Hardcode keys in source code
- ❌ Commit keys to git
- ❌ Share keys in chat/email
- ❌ Use production keys in development

### 2. Cost Optimization

```python
# Use cheapest model for simple tasks
simple_tasks = ["summarization", "classification", "simple_qa"]
if task_type in simple_tasks:
    model = "claude-3-5-haiku-20241022"  # 5x cheaper than Sonnet

# Cache system prompts for repeated use
# (Anthropic supports prompt caching)

# Set conservative max_tokens to avoid overgeneration
max_tokens = 500  # Instead of 4096 default
```

### 3. Error Handling

```python
from anthropic import APIError, APITimeoutError, RateLimitError

async def safe_generate(prompt: str):
    claude = AnthropicWrapper()
    max_retries = 3

    for attempt in range(max_retries):
        try:
            return await claude.generate_response(prompt)

        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"⏳ Rate limited. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)

        except APITimeoutError:
            print(f"⏳ Timeout. Retry {attempt+1}/{max_retries}...")
            continue

        except APIError as e:
            print(f"❌ API Error: {e}")
            return None, None

    return None, None
```

### 4. Monitoring Usage

Track API usage to manage costs:

```python
import time

class UsageTracker:
    def __init__(self):
        self.calls = []

    async def tracked_generate(self, claude, prompt, **kwargs):
        start = time.time()
        response, model = await claude.generate_response(prompt, **kwargs)
        duration = time.time() - start

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4

        self.calls.append({
            'model': model,
            'duration': duration,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        })

        return response, model

    def report(self):
        total_input = sum(c['input_tokens'] for c in self.calls)
        total_output = sum(c['output_tokens'] for c in self.calls)

        print(f"📊 Usage Report:")
        print(f"   Calls: {len(self.calls)}")
        print(f"   Input tokens: {total_input:,}")
        print(f"   Output tokens: {total_output:,}")
        print(f"   Est. cost: ${(total_input * 3 + total_output * 15) / 1_000_000:.4f}")
```

---

## Integration with LUKHAS Components

### With Guardian (Constitutional AI)

```python
from lukhas.governance.guardian import Guardian

async def claude_with_guardian(query: str):
    claude = AnthropicWrapper()
    guardian = Guardian()

    # Pre-flight check with Guardian
    if not guardian.allow_query(query):
        return "Query rejected by Guardian", None

    # Generate response
    response, model = await claude.generate_response(query)

    # Post-flight validation
    if not guardian.allow_response(response):
        return "Response blocked by Guardian", None

    return response, model
```

### With Reasoning Lab

```python
from lukhas.products.reasoning_lab import ReasoningLab

async def create_explainable_trace(query: str):
    lab = ReasoningLab()
    claude = AnthropicWrapper()

    # Generate reasoning with Claude
    reasoning_prompt = f"""
    Create a step-by-step reasoning trace for:
    {query}

    Format:
    1. Initial analysis
    2. Key factors identified
    3. Reasoning steps
    4. Conclusion
    """

    response, model = await claude.generate_response(reasoning_prompt)

    # Visualize in Reasoning Lab
    trace = lab.parse_reasoning(response)
    lab.render(trace, redaction_level=50)

    return trace
```

---

## Additional Resources

**Official Documentation**:
- [Anthropic API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Claude Model Specifications](https://docs.anthropic.com/claude/docs/models-overview)
- [API Rate Limits](https://docs.anthropic.com/claude/reference/rate-limits)

**LUKHAS Documentation**:
- [LLM Wrappers Architecture](./llm-wrappers/README.md)
- [Bridge Layer Overview](../architecture/bridge/README.md)
- [Guardian Integration](../governance/GUARDIAN_CONSTITUTION.md)

**Code References**:
- [anthropic_wrapper.py](../../bridge/llm_wrappers/anthropic_wrapper.py) - Main wrapper implementation
- [env_loader.py](../../bridge/llm_wrappers/env_loader.py) - API key management
- [anthropic_function_bridge.py](../../bridge/llm_wrappers/anthropic_function_bridge.py) - Function calling support

---

## Support

**Issues**: [GitHub Issues](https://github.com/lukhas-ai/cognitive/issues?label=claude-api)
**Questions**: bridge@lukhas.ai
**Security**: security@lukhas.ai (for API key leaks or security concerns)

---

**Document Owner**: @bridge-team
**Review Cycle**: Quarterly or when Anthropic releases new models
**Last Updated**: 2025-11-06
**Status**: Active Documentation
