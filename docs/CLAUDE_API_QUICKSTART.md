# Claude API Quick Start for LUKHAS

> **⚡ Get up and running with Claude API in 5 minutes**

---

## Prerequisites

1. **Anthropic API Key** - Get one at [console.anthropic.com](https://console.anthropic.com/)
2. **Python 3.9+** - Already installed (`python3 --version`)
3. **Anthropic SDK** - Install with `pip install anthropic`

---

## Setup (Choose One Method)

### Method 1: Interactive Setup (Recommended)

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 scripts/configure_claude_api.py
```

Follow the prompts to:
1. Enter your API key
2. Test the connection
3. Choose storage method (.env file or macOS Keychain)

### Method 2: Manual .env Configuration

```bash
# Open .env file
nano .env

# Replace placeholder with your key
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE

# Save and exit (Ctrl+X, then Y, then Enter)
```

### Method 3: Command Line

```bash
python3 scripts/configure_claude_api.py --key sk-ant-YOUR_KEY
```

---

## Verify Setup

```bash
python3 scripts/test_claude_api.py
```

Expected output:
```
🧪 Testing Claude API Integration...
✅ Claude API key loaded
✅ Test 1 PASSED
✅ Test 2 PASSED
✅ Test 3 PASSED
✅ ALL TESTS PASSED
```

---

## Your First API Call

Create `test_claude.py`:

```python
import asyncio
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def main():
    claude = AnthropicWrapper()

    response, model = await claude.generate_response(
        prompt="What is LUKHAS AI?",
        model="claude-3-5-sonnet-20241022"
    )

    print(f"Response: {response}")

asyncio.run(main())
```

Run it:
```bash
python3 test_claude.py
```

---

## Next Steps

### 1. Explore Examples

```bash
python3 examples/claude_api_usage.py
```

See examples of:
- Basic usage
- Model comparison
- Cost optimization
- Error handling
- Usage tracking
- LUKHAS integration

### 2. Read Full Documentation

[docs/bridge/CLAUDE_API_SETUP.md](bridge/CLAUDE_API_SETUP.md) - Complete setup guide with:
- All configuration methods
- Advanced usage patterns
- Integration with Guardian and MATRIZ
- Troubleshooting
- Best practices

### 3. Check Model Pricing

Choose model based on task:

| Model | Input Cost | Output Cost | Best For |
|-------|-----------|-------------|----------|
| Haiku | $0.25/MTok | $1.25/MTok | Simple tasks, fast responses |
| Sonnet | $3/MTok | $15/MTok | Balanced reasoning (recommended) |
| Opus | $15/MTok | $75/MTok | Complex reasoning, creative work |

---

## Common Issues

### "Anthropic package not installed"
```bash
pip install anthropic
```

### "API key not found"
```bash
# Check .env file exists and has key
grep ANTHROPIC_API_KEY .env

# Run setup wizard
python3 scripts/configure_claude_api.py
```

### "Invalid API key"
- Verify key starts with `sk-ant-`
- Check key hasn't been revoked at console.anthropic.com
- Try generating a new key

---

## Quick Reference

**Configuration**: `python3 scripts/configure_claude_api.py`
**Testing**: `python3 scripts/test_claude_api.py`
**Examples**: `python3 examples/claude_api_usage.py`
**Full Docs**: [docs/bridge/CLAUDE_API_SETUP.md](bridge/CLAUDE_API_SETUP.md)

---

**Last Updated**: 2025-11-06
