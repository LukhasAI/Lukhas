# LUKHAS Bridge Layer Documentation

> **🌉 LLM Integration & External Service Bridge**

**Version**: 1.0
**Last Updated**: 2025-11-06
**Status**: Active Documentation

---

## Overview

The Bridge Layer provides unified interfaces for integrating external Large Language Models (LLMs) and services into LUKHAS. It abstracts API complexities, provides consistent error handling, and enables seamless switching between different AI providers.

**Supported Services**:
- **Anthropic Claude** (Opus, Sonnet, Haiku)
- **OpenAI GPT** (GPT-4, GPT-3.5)
- **Google Gemini**
- **Azure OpenAI**
- **Perplexity AI**
- **Jules AI** (Google's coding agent)

---

## Quick Start

### 1. Configure Claude API (Recommended)

```bash
# Interactive setup
python3 scripts/configure_claude_api.py

# Non-interactive
python3 scripts/configure_claude_api.py --key sk-ant-YOUR_KEY

# Test configuration
python3 scripts/test_claude_api.py
```

### 2. Basic Usage

```python
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def main():
    claude = AnthropicWrapper()
    response, model = await claude.generate_response(
        prompt="Explain the LUKHAS Constellation Framework",
        model="claude-3-5-sonnet-20241022"
    )
    print(response)
```

### 3. See Examples

```bash
python3 examples/claude_api_usage.py
```

---

## Documentation

### API Setup Guides

#### [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md) - **Claude/Anthropic Integration**
Complete guide for setting up and using Claude API:
- Prerequisites and API key setup
- Configuration methods (.env, keychain, environment)
- Usage examples (basic, advanced, streaming)
- Model selection strategy
- Integration with LUKHAS components
- Troubleshooting and best practices
- Cost optimization

**Quick Links**:
- Configuration: `python3 scripts/configure_claude_api.py`
- Testing: `python3 scripts/test_claude_api.py`
- Examples: `python3 examples/claude_api_usage.py`

#### OpenAI Integration (Coming Soon)
- GPT-4 and GPT-3.5 setup
- Function calling
- Vision API integration

#### Gemini Integration (Coming Soon)
- Google Gemini Pro setup
- Multimodal capabilities

---

## Architecture

### Bridge Layer Structure

```
bridge/
├── llm_wrappers/              # LLM service integrations
│   ├── base.py               # Abstract base class
│   ├── anthropic_wrapper.py  # Claude integration ⭐
│   ├── openai_wrapper.py     # OpenAI GPT integration
│   ├── gemini_wrapper.py     # Google Gemini
│   ├── jules_wrapper.py      # Jules AI agent
│   ├── env_loader.py         # API key management
│   └── ...
├── function_bridges/          # Function calling adapters
│   ├── anthropic_function_bridge.py
│   └── openai_function_bridge.py
└── services/                  # External service clients
```

### Key Components

#### 1. LLM Wrappers

Abstract LLM APIs into unified interfaces:

```python
class LLMWrapper:
    async def generate_response(self, prompt: str, **kwargs) -> tuple[str, str]:
        """Generate response using LLM"""
        pass

    def is_available(self) -> bool:
        """Check if LLM service is available"""
        pass
```

#### 2. Environment Loader

Secure API key management:
- Loads from `.env` files (gitignored)
- Supports multiple .env locations
- No hardcoded credentials
- Service name mapping

#### 3. Function Bridges

Enable function calling for Claude and GPT:
- Schema validation
- Parameter extraction
- Result formatting
- Error handling

---

## Configuration

### API Key Management

#### Method 1: .env File (Recommended)

Create `.env` in project root:

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY

# OpenAI
OPENAI_API_KEY=sk-YOUR_KEY
OPENAI_ORG_ID=org-YOUR_ORG
OPENAI_PROJECT_ID=proj_YOUR_PROJECT

# Google
GOOGLE_API_KEY=YOUR_KEY

# Perplexity
PERPLEXITY_API_KEY=pplx-YOUR_KEY
```

#### Method 2: macOS Keychain

```bash
# Store
security add-generic-password \
  -a "$USER" \
  -s "LUKHAS_ANTHROPIC_API_KEY" \
  -w "sk-ant-YOUR_KEY"

# Retrieve
security find-generic-password \
  -a "$USER" \
  -s "LUKHAS_ANTHROPIC_API_KEY" \
  -w
```

#### Method 3: Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY"
export OPENAI_API_KEY="sk-YOUR_KEY"
```

---

## Usage Examples

### Example 1: Multi-Model Comparison

```python
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
from bridge.llm_wrappers.openai_wrapper import OpenAIWrapper

async def compare_models():
    claude = AnthropicWrapper()
    gpt = OpenAIWrapper()

    prompt = "Explain quantum-inspired algorithms"

    claude_response, _ = await claude.generate_response(prompt)
    gpt_response, _ = await gpt.generate_response(prompt)

    print(f"Claude: {claude_response}")
    print(f"GPT:    {gpt_response}")
```

### Example 2: Cost-Optimized Routing

```python
async def smart_routing(task_complexity: str, prompt: str):
    if task_complexity == "simple":
        model = "claude-3-5-haiku-20241022"  # Cheapest
    elif task_complexity == "moderate":
        model = "claude-3-5-sonnet-20241022"  # Balanced
    else:
        model = "claude-3-opus-20240229"  # Most capable

    claude = AnthropicWrapper()
    return await claude.generate_response(prompt, model=model)
```

### Example 3: Integration with MATRIZ

```python
from matriz.cognitive_engine import CognitiveEngine
from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

async def reason_with_matriz(query: str):
    claude = AnthropicWrapper()
    engine = CognitiveEngine()

    # Generate reasoning with Claude
    response, model = await claude.generate_response(
        prompt=f"Analyze with structured reasoning: {query}",
        model="claude-3-5-sonnet-20241022"
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

## Testing

### Test Individual Service

```bash
# Claude
python3 scripts/test_claude_api.py

# Test all models
python3 scripts/test_claude_api.py --all

# Verbose output
python3 scripts/test_claude_api.py --verbose
```

### Run Comprehensive Examples

```bash
python3 examples/claude_api_usage.py
```

### Unit Tests

```bash
# Test bridge wrappers
pytest tests/bridge/llm_wrappers/test_anthropic_wrapper.py
pytest tests/bridge/llm_wrappers/test_env_loader.py

# Test function bridges
pytest tests/bridge/function_bridges/
```

---

## Best Practices

### 1. Model Selection

```python
# Task-appropriate model selection
tasks = {
    "classification": "claude-3-5-haiku-20241022",  # Fast, cheap
    "summarization": "claude-3-5-haiku-20241022",
    "reasoning": "claude-3-5-sonnet-20241022",      # Balanced
    "creative": "claude-3-opus-20240229",            # Most capable
    "analysis": "claude-3-opus-20240229"
}
```

### 2. Error Handling

```python
from anthropic import APIError, RateLimitError

async def robust_generate(prompt: str):
    for attempt in range(3):
        try:
            return await claude.generate_response(prompt)
        except RateLimitError:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except APIError as e:
            logger.error(f"API error: {e}")
            return None
```

### 3. Cost Monitoring

```python
class CostTracker:
    def __init__(self):
        self.total_cost = 0.0

    async def tracked_call(self, prompt: str, model: str):
        input_tokens = len(prompt) // 4
        response, _ = await claude.generate_response(prompt, model=model)
        output_tokens = len(response) // 4

        # Calculate cost based on model pricing
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost

        return response
```

### 4. Security

- ✅ Never hardcode API keys
- ✅ Use `.env` files (gitignored)
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/prod
- ❌ Don't commit keys to git
- ❌ Don't log full API responses (may contain sensitive data)

---

## Troubleshooting

### Common Issues

#### "Package not installed"
```bash
pip install anthropic openai google-generativeai
```

#### "API key not found"
```bash
# Verify .env file
grep ANTHROPIC_API_KEY .env

# Run configuration wizard
python3 scripts/configure_claude_api.py
```

#### "Rate limit exceeded"
- Wait and retry with exponential backoff
- Reduce request frequency
- Upgrade API tier

#### "Invalid model"
- Use current model names (see [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md))
- Check Anthropic docs for latest models

---

## Resources

### Internal Documentation
- [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md) - Complete Claude setup guide
- [../architecture/bridge/](../architecture/bridge/) - Bridge architecture
- [../governance/GUARDIAN_CONSTITUTION.md](../governance/GUARDIAN_CONSTITUTION.md) - Guardian integration

### External Documentation
- [Anthropic API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Google AI Docs](https://ai.google.dev/docs)

### Code References
- [bridge/llm_wrappers/](../../bridge/llm_wrappers/) - Wrapper implementations
- [examples/](../../examples/) - Usage examples
- [scripts/](../../scripts/) - Configuration and testing scripts

---

## Contributing

### Adding New LLM Integration

1. Create wrapper class inheriting from `LLMWrapper`
2. Implement `generate_response()` and `is_available()`
3. Add API key to `env_loader.py`
4. Create tests in `tests/bridge/llm_wrappers/`
5. Document in this README and create setup guide

### Example Template

```python
from .base import LLMWrapper
from .env_loader import get_api_key

class NewLLMWrapper(LLMWrapper):
    def __init__(self):
        self.api_key = get_api_key("newllm")
        # Initialize client

    async def generate_response(self, prompt: str, **kwargs):
        # Implementation
        pass

    def is_available(self) -> bool:
        return self.api_key is not None
```

---

## Support

**Questions**: bridge@lukhas.ai
**Issues**: [GitHub Issues](https://github.com/lukhas-ai/cognitive/issues?label=bridge)
**Security**: security@lukhas.ai

---

**Document Owner**: @bridge-team
**Review Cycle**: Monthly or when new LLM services added
**Last Updated**: 2025-11-06
**Status**: Active Documentation
