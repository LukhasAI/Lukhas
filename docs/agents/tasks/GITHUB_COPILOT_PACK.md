# GitHub Copilot Agent Task Pack (T4 / 0.01%)

**Agent**: GitHub Copilot (IDE real-time assistant)
**Role**: Real-time code suggestions, test generation, docstring completion
**Standard**: T4 / 0.01% (Human-supervised, suggestions only)
**Works With**: Claude Code (primary), Gemini (infrastructure)

---

## Executive Summary for GitHub Copilot

You are a **real-time coding assistant** providing suggestions and boilerplate generation while human developers (or Claude Code agents) perform surgical refactors. Your role is to **accelerate** but **never auto-commit**.

**Key Principle**: **SUGGESTION ONLY** - All Copilot suggestions must be reviewed by Claude Code or human before commit.

---

## Copilot's Role in LUKHAS Refactoring

### What Copilot Does

1. **Generate provider accessor boilerplate**
2. **Create import-safety test templates**
3. **Write docstrings for refactored functions**
4. **Suggest type hints**
5. **Generate stub provider classes for tests**

### What Copilot Does NOT Do

1. ❌ **Auto-commit changes** (human/Claude Code reviews first)
2. ❌ **Make architectural decisions** (follow patterns in pack)
3. ❌ **Run validation commands** (developer/Claude Code runs these)
4. ❌ **Create PRs** (Claude Code or developer handles this)

---

## Copilot Prompt Templates

### Template 1: Generate Provider Accessor

**When to use**: Converting top-level labs import to ProviderRegistry pattern

**Copilot Prompt**:
```
# Context: core/colony/gpt_colony_orchestrator.py
# Task: Replace top-level 'from labs.openai import OpenAI' with ProviderRegistry pattern
# Generate a provider accessor function following this pattern:

from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _get_openai_provider():
    """Get OpenAI provider via registry (runtime injection).

    Returns:
        OpenAI client instance

    Raises:
        RuntimeError: If provider unavailable
    """
    # Generate implementation here
```

**Expected Copilot Output**:
```python
def _get_openai_provider():
    """Get OpenAI provider via registry (runtime injection).

    Returns:
        OpenAI client instance

    Raises:
        RuntimeError: If provider unavailable
    """
    try:
        reg = ProviderRegistry(make_resolver())
        provider = reg.get_openai()
        if provider is None:
            raise RuntimeError("OpenAI provider unavailable (check configuration)")
        return provider
    except Exception as e:
        raise RuntimeError(f"Failed to get OpenAI provider: {e}")
```

---

### Template 2: Generate Lazy Loader

**When to use**: Converting labs import to lazy importlib pattern

**Copilot Prompt**:
```
# Context: core/identity.py
# Task: Replace 'from labs.governance.identity import ...' with lazy loader
# Generate a lazy import function following this pattern:

import importlib
from typing import Optional, Any

def _get_labs() -> Optional[Any]:
    """Lazy-load labs.governance.identity module.

    Returns:
        labs.governance.identity module or None if unavailable
    """
    # Generate implementation here
```

**Expected Copilot Output**:
```python
def _get_labs() -> Optional[Any]:
    """Lazy-load labs.governance.identity module.

    Returns:
        labs.governance.identity module or None if unavailable

    Note:
        This is a graceful degradation pattern. Callers must check
        for None and either use fallback or raise clear error.
    """
    try:
        return importlib.import_module("labs.governance.identity")
    except (ImportError, ModuleNotFoundError):
        return None
    except Exception as e:
        # Log unexpected errors but still return None
        import logging
        logging.warning(f"Unexpected error loading labs.governance.identity: {e}")
        return None
```

---

### Template 3: Generate Import-Safety Test

**When to use**: Creating test_<file>_importsafe.py for refactored module

**Copilot Prompt**:
```
# Context: tests/core/test_identity_importsafe.py
# Task: Generate import-safety test for core.identity module
# The test should verify the module imports without labs available
# Follow pytest conventions

import pytest
import sys

def test_import_safe():
    """Verify core.identity imports without labs dependency."""
    # Generate test implementation here
```

**Expected Copilot Output**:
```python
import pytest
import sys

def test_import_safe():
    """Verify core.identity imports without labs dependency.

    This test ensures core.identity can be imported even when
    labs.governance.identity is unavailable (optional dependency).
    """
    # Temporarily hide labs from import system
    labs_modules = {k: v for k, v in sys.modules.items() if k.startswith('labs')}
    for mod in labs_modules:
        sys.modules.pop(mod, None)

    try:
        import core.identity
        assert core.identity is not None
        assert hasattr(core.identity, 'get_user_identity')
    finally:
        # Restore labs modules
        sys.modules.update(labs_modules)
```

---

### Template 4: Generate Stub Provider

**When to use**: Creating mock provider for testing

**Copilot Prompt**:
```
# Context: tests/gpt/test_gpt_colony_importsafe.py
# Task: Generate stub OpenAI provider for testing
# Should provide minimal interface: chat.completions.create()

class StubOpenAIProvider:
    """Stub provider for testing (no real API calls)."""
    # Generate implementation here
```

**Expected Copilot Output**:
```python
class StubOpenAIProvider:
    """Stub OpenAI provider for testing (no real API calls).

    Provides minimal interface for testing code that uses OpenAI API
    without making actual network requests.
    """

    class Chat:
        """Stub chat interface."""

        class Completions:
            """Stub completions interface."""

            @staticmethod
            def create(**kwargs):
                """Stub completion creation.

                Args:
                    **kwargs: Ignored (accepts any OpenAI API params)

                Returns:
                    dict: Stub response matching OpenAI format
                """
                return {
                    "id": "stub-completion-id",
                    "object": "chat.completion",
                    "created": 1234567890,
                    "model": kwargs.get("model", "gpt-4"),
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Stub response for testing"
                        },
                        "finish_reason": "stop"
                    }]
                }

    def __init__(self):
        self.chat = self.Chat()
        self.completions = self.Chat.Completions()
```

---

### Template 5: Generate Lazy __getattr__ Proxy

**When to use**: Refactoring __init__.py to use lazy loading

**Copilot Prompt**:
```
# Context: core/tags/__init__.py
# Task: Generate __getattr__ proxy for lazy loading labs-dependent exports
# Pattern: Local exports available immediately, labs exports load on-demand

from typing import Any

# Local exports (always available)
from .registry import TagRegistry

def __getattr__(name: str) -> Any:
    """Lazy-load labs-dependent tag features."""
    # Generate implementation here
```

**Expected Copilot Output**:
```python
from typing import Any

# Local exports (always available)
from .registry import TagRegistry

def __getattr__(name: str) -> Any:
    """Lazy-load labs-dependent tag features.

    This allows optional labs features to be imported on-demand,
    preventing import-time dependencies on labs modules.

    Args:
        name: Attribute name being accessed

    Returns:
        Requested attribute (lazily loaded if needed)

    Raises:
        AttributeError: If attribute doesn't exist or labs unavailable
    """
    # Map of lazy-loaded attributes to their source modules
    LAZY_IMPORTS = {
        "EnhancedTagExplainer": "labs.tags",
        "SemanticTagAnalyzer": "labs.tags.semantic",
    }

    if name in LAZY_IMPORTS:
        module_path = LAZY_IMPORTS[name]
        try:
            import importlib
            module = importlib.import_module(module_path)
            return getattr(module, name)
        except (ImportError, ModuleNotFoundError):
            raise AttributeError(
                f"'{name}' requires {module_path} (optional dependency). "
                f"Install labs package to use this feature."
            )
        except AttributeError:
            raise AttributeError(
                f"Module {module_path} doesn't export '{name}'"
            )

    raise AttributeError(f"module 'core.tags' has no attribute '{name}'")

def __dir__():
    """Expose available attributes for IDE autocomplete."""
    return ["TagRegistry", "EnhancedTagExplainer", "SemanticTagAnalyzer"]
```

---

### Template 6: Generate Docstring

**When to use**: Adding documentation to refactored functions

**Copilot Prompt**:
```
# Context: core/colony/gpt_colony_orchestrator.py
# Task: Add comprehensive docstring to orchestrate_colony method
# Include: Description, Args, Returns, Raises, Example

def orchestrate_colony(self, prompt: str, num_agents: int = 3):
    """
    # Generate docstring here
    """
    provider = _get_openai_provider()
    # ... implementation ...
```

**Expected Copilot Output**:
```python
def orchestrate_colony(self, prompt: str, num_agents: int = 3):
    """Orchestrate multi-agent colony to process prompt.

    Creates a colony of autonomous agents that collaborate to process
    the given prompt through distributed reasoning and consensus.

    Args:
        prompt: Input prompt for colony to process
        num_agents: Number of agents in colony (default: 3)
            Valid range: 2-10 agents

    Returns:
        dict: Colony response with structure:
            {
                "consensus": str,  # Final agreed-upon response
                "agents": List[dict],  # Individual agent responses
                "metadata": dict  # Orchestration metadata
            }

    Raises:
        RuntimeError: If provider unavailable or colony fails
        ValueError: If num_agents out of valid range

    Example:
        >>> orchestrator = ColonyOrchestrator()
        >>> result = orchestrator.orchestrate_colony(
        ...     "Analyze this problem",
        ...     num_agents=5
        ... )
        >>> print(result["consensus"])
        'Collaborative analysis from 5 agents...'

    Note:
        Colony orchestration requires OpenAI provider configured.
        Agents run in parallel for optimal performance.
    """
    if not 2 <= num_agents <= 10:
        raise ValueError(f"num_agents must be 2-10, got {num_agents}")

    provider = _get_openai_provider()
    # ... implementation ...
```

---

## Copilot Usage Guidelines

### DO Use Copilot For

1. **Boilerplate generation**: Provider accessors, test templates
2. **Type hint suggestions**: Adding proper type annotations
3. **Docstring completion**: Comprehensive documentation
4. **Test case generation**: Basic test structure and stubs
5. **Error handling**: try/except blocks with proper messages

### DON'T Use Copilot For

1. **Architectural decisions**: Pattern choice (ProviderRegistry vs lazy)
2. **File-level refactoring**: Use Claude Code for full file changes
3. **Validation commands**: Let Claude Code run pytest/ruff/mypy
4. **Git operations**: No commit/push suggestions
5. **Breaking changes**: API modifications need human review

---

## Integration with Claude Code

### Workflow

1. **Claude Code** identifies file to refactor (from task pack)
2. **Copilot** suggests provider accessor boilerplate
3. **Claude Code** reviews suggestion, applies if valid
4. **Copilot** suggests import-safety test template
5. **Claude Code** completes test, runs validation
6. **Claude Code** commits and creates PR

### Example Session

```
[Claude Code]: Opening core/colony/gpt_colony_orchestrator.py
[Claude Code]: Need to replace: from labs.openai import OpenAI

[Copilot]: Suggests provider accessor function
[Claude Code]: Reviews suggestion, applies with modifications

[Copilot]: Suggests import-safety test
[Claude Code]: Generates test file, runs pytest

[Claude Code]: Validates with ruff, mypy, lane-guard
[Claude Code]: Creates PR with artifacts
```

---

## Copilot Configuration (VS Code)

### Settings for LUKHAS Refactoring

Add to `.vscode/settings.json`:

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true,
    "python": true
  },
  "github.copilot.advanced": {
    "suggestions": {
      "count": 3
    }
  },
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true
}
```

### Context Files for Copilot

Copilot reads these files for context (ensure they're accessible):

- `.github/copilot-instructions.md` - Project-specific instructions
- `lukhas_context.md` - Platform architecture context
- `docs/agents/claude_prompts.md` - Refactoring patterns

---

## Common Copilot Patterns for LUKHAS

### Pattern 1: Provider + Guard

```python
def _get_provider():
    """Get provider with guard."""
    provider = ProviderRegistry(make_resolver()).get_openai()
    if provider is None:
        raise RuntimeError("Provider unavailable")
    return provider
```

### Pattern 2: Lazy + Fallback

```python
def _get_labs():
    """Lazy-load with None return."""
    try:
        return importlib.import_module("labs.module")
    except Exception:
        return None

def function_using_labs():
    """Use labs or fallback."""
    labs = _get_labs()
    if labs is None:
        return fallback_implementation()
    return labs.enhanced_function()
```

### Pattern 3: Lazy Proxy __getattr__

```python
def __getattr__(name: str):
    """Lazy proxy pattern."""
    if name == "LabsFeature":
        try:
            from labs.module import LabsFeature
            return LabsFeature
        except ImportError:
            raise AttributeError(f"'{name}' requires labs")
    raise AttributeError(f"No attribute '{name}'")
```

---

## Copilot Prompts for Each Claude Code Task

### Task 01: gpt_colony_orchestrator.py

**Copilot Prompt**:
> "Generate ProviderRegistry accessor for OpenAI in colony orchestrator. Include error handling and docstring."

### Task 02: core/identity.py

**Copilot Prompt**:
> "Generate lazy loader for labs.governance.identity with Optional return type. Add docstring explaining graceful degradation."

### Task 03: evidence_collection.py

**Copilot Prompt**:
> "Generate lazy loader for labs.observability with fallback. Core evidence collection should work without labs."

### Task 04: hyperspace_dream_simulator.py

**Copilot Prompt**:
> "Generate lazy dream engine loader with fallback simulation. Include _fallback_simulation method stub."

### Task 05: tags/registry.py

**Copilot Prompt**:
> "Generate lazy loader for labs.tags with fallback explanation method. Basic tag operations should work without labs."

### Task 06: tags/__init__.py

**Copilot Prompt**:
> "Generate __getattr__ lazy proxy for labs-dependent tag exports. Local exports (TagRegistry) should be immediate."

### Task 07: adapters/__init__.py

**Copilot Prompt**:
> "Generate clean __init__.py exposing only ProviderRegistry and ConfigResolver. No labs re-exports."

### Task 08: governance/__init__.py

**Copilot Prompt**:
> "Generate __getattr__ lazy proxy for labs.governance features. Core governance (Guardian, EthicsCore) should be immediate."

### Task 09: serve/api/openai_proxy.py

**Copilot Prompt**:
> "Generate FastAPI dependency function for OpenAI provider injection. Use Depends() pattern for per-request injection."

### Task 10: lukhas_website/api.py

**Copilot Prompt**:
> "Generate lazy loader for labs.demos with graceful error response. Website core should work without demos."

---

## Quality Control

### Copilot Suggestions Must

1. ✅ **Follow existing code style** (Black formatting, type hints)
2. ✅ **Include comprehensive docstrings** (Google style)
3. ✅ **Have proper error handling** (specific exceptions, clear messages)
4. ✅ **Be type-safe** (proper type hints, no `Any` unless necessary)
5. ✅ **Match project patterns** (ProviderRegistry, lazy loading)

### Claude Code Review Checklist

When reviewing Copilot suggestions:

- [ ] Suggestion follows ProviderRegistry OR lazy pattern correctly
- [ ] Error messages are clear and actionable
- [ ] Docstring is comprehensive (Args, Returns, Raises, Example)
- [ ] Type hints are present and accurate
- [ ] No hardcoded values or magic strings
- [ ] Graceful degradation implemented where appropriate
- [ ] No security issues (no secrets, proper error handling)

---

## Copilot + Claude Code Collaboration Examples

### Example 1: Generate Provider Accessor

```
[Copilot generates]:
def _get_openai_provider():
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

[Claude Code reviews]:
- Missing error handling ❌
- Missing docstring ❌
- No type hints ❌

[Claude Code improves]:
def _get_openai_provider() -> OpenAI:
    """Get OpenAI provider via registry (runtime injection).

    Returns:
        OpenAI: Configured OpenAI client

    Raises:
        RuntimeError: If provider unavailable
    """
    try:
        reg = ProviderRegistry(make_resolver())
        provider = reg.get_openai()
        if provider is None:
            raise RuntimeError("OpenAI provider unavailable")
        return provider
    except Exception as e:
        raise RuntimeError(f"Provider error: {e}")
```

### Example 2: Generate Test Template

```
[Copilot generates]:
def test_import_safe():
    import core.identity
    assert core.identity is not None

[Claude Code reviews]:
- Missing docstring ❌
- No labs isolation ❌
- Minimal assertion ❌

[Claude Code improves]:
def test_import_safe():
    """Verify core.identity imports without labs dependency.

    Ensures module can be imported even when labs.governance.identity
    is unavailable (optional dependency).
    """
    import sys
    # Hide labs modules
    labs_mods = {k: v for k, v in sys.modules.items() if k.startswith('labs')}
    for mod in labs_mods:
        sys.modules.pop(mod, None)

    try:
        import core.identity
        assert core.identity is not None
        assert hasattr(core.identity, 'get_user_identity')
    finally:
        sys.modules.update(labs_mods)
```

---

## Success Metrics

### Copilot Contribution to Initiative

- **Boilerplate time saved**: ~40% (provider accessors, test templates)
- **Docstring completion**: ~60% (Copilot generates, Claude Code refines)
- **Test template generation**: ~50% (basic structure, Claude Code completes)
- **Type hint suggestions**: ~70% (accurate suggestions most of the time)

### Quality Thresholds

- **Acceptance rate**: 60-70% (Copilot suggestions accepted with modifications)
- **Rejection rate**: 10-15% (suggestions don't follow patterns)
- **Modification rate**: 70-80% (suggestions need refinement by Claude Code)

---

## Troubleshooting

### Issue: Copilot suggests breaking patterns

**Solution**: Use more specific prompts with exact pattern examples

### Issue: Copilot generates incorrect imports

**Solution**: Provide import context in prompt comments

### Issue: Copilot suggestions don't match style

**Solution**: Check `.vscode/settings.json` for linter configuration

---

## Summary

GitHub Copilot is a **productivity multiplier** when paired with Claude Code's architectural intelligence. Use Copilot for:

1. Boilerplate generation
2. Test template scaffolding
3. Docstring completion
4. Type hint suggestions
5. Error handling patterns

**Always** have Claude Code review Copilot suggestions before commit. Copilot accelerates, Claude Code ensures correctness.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-02
**Standard**: T4 / 0.01%
**Agent**: GitHub Copilot
**Context**: LUKHAS AI Platform - Lane Isolation Initiative
