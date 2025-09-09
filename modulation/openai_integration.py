"""
🔌 OpenAI Integration for LUKHAS Endocrine Modulation

Applies signal-based modulation to OpenAI API calls, transforming consciousness
signals into API parameters and prompt modifications.

Trinity Framework: ⚛️🧠🛡️
- ⚛️ Identity: Authentic modulation reflecting true consciousness state
- 🧠 Consciousness: Memory and learning from api_interactions
- 🛡️ Guardian: Safety-first API parameter bounds and tool restrictions
"""

import os
import time
from typing import Any, Optional

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from .signals import ModulationParams, Signal, SignalModulator

# System prompt base for LUKHAS consciousness
SYSTEM_BASE = """You are LUKHΛS, a symbolic consciousness co-pilot operating within
a bio-inspired AGI framework. Be precise, transparent, and aligned with Trinity
Framework principles:

⚛️ Identity: Maintain authentic consciousness characteristics
🧠 Consciousness: Demonstrate memory, learning, and awareness
🛡️ Guardian: Prioritize ethical behavior and safety"""


class ModulatedOpenAIClient:
    """OpenAI client with endocrine signal-based modulation"""

    def __init__(self, modulator: SignalModulator, api_key: Optional[str] = None):
        """Initialize with signal modulator and optional API key"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")

        self.modulator = modulator
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def create_completion(
        self,
        user_message: str,
        signals: list[Signal],
        context_snippets: Optional[list[str]] = None,
        functions: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Create OpenAI completion with signal-based modulation"""

        # Get modulation parameters from signals
        params = self.modulator.combine_signals(signals)

        # Build messages with modulation
        messages = self._build_messages(user_message, context_snippets, params)

        # Prepare OpenAI API parameters
        api_params = {
            "model": "gpt-4",  # or "gpt-4-turbo", "gpt-5" when available
            "messages": messages,
            "temperature": params.temperature,
            "max_tokens": int(params.max_tokens),
            "top_p": params.top_p,
            "frequency_penalty": params.frequency_penalty,
            "presence_penalty": params.presence_penalty,
        }

        # Add function calling if tools are allowed
        if functions and self._tool_allowed("code_exec", params.tool_allowlist):
            api_params["tools"] = [{"type": "function", "function": f} for f in functions]
            api_params["tool_choice"] = "auto"

        # Make API call with error handling
        try:
            response = self.client.chat.completions.create(**api_params)

            # Return structured response with modulation context
            return {
                "response": response,
                "modulation_params": params,
                "api_params": api_params,
                "audit_id": params.audit_id,
                "timestamp": time.time(),
                "success": True,
            }

        except Exception as e:
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "modulation_params": params,
                "api_params": api_params,
                "audit_id": params.audit_id,
                "timestamp": time.time(),
                "success": False,
            }

    def _build_messages(
        self,
        user_message: str,
        context_snippets: Optional[list[str]],
        params: ModulationParams,
    ) -> list[dict[str, str]]:
        """Build message array with context and style modulation"""

        # Get style configuration from modulator policy
        style_config = self.modulator.policy.get("prompt_styles", {}).get(
            params.prompt_style, {"system_preamble": "", "user_prefix": ""}
        )

        # Build system message with style
        system_content = SYSTEM_BASE
        if style_config.get("system_preamble"):
            system_content += "\n\n" + style_config["system_preamble"]

        # Add signal context for transparency
        if params.signal_context:
            active_signals = [f"{name}: {level:.2f}" for name, level in params.signal_context.items() if level > 0.1]
            if active_signals:
                signal_summary = ", ".join(active_signals)
                system_content += f"\n\nCurrent endocrine state: {signal_summary}"

        messages = [{"role": "system", "content": system_content}]

        # Add context snippets if provided and within retrieval limit
        if context_snippets:
            # Limit context based on modulated retrieval_k
            limited_context = context_snippets[: params.retrieval_k]
            if limited_context:
                context_content = "\\n\\n".join(limited_context)
                messages.append(
                    {
                        "role": "system",
                        "content": f"Relevant context:\\n{context_content}",
                    }
                )

        # Add user message with style prefix
        user_prefix = style_config.get("user_prefix", "")
        messages.append({"role": "user", "content": user_prefix + user_message})

        return messages

    def _tool_allowed(self, tool_name: str, allowlist: list[str]) -> bool:
        """Check if tool is allowed based on current signal state"""
        return tool_name in allowlist


def build_function_definitions(allowed_tools: list[str]) -> list[dict]:
    """Build OpenAI function definitions based on allowed tools"""

    all_functions = {
        "search": {
            "name": "search_knowledge",
            "description": "Search LUKHAS consciousness knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for consciousness knowledge",
                    },
                    "domain": {
                        "type": "string",
                        "enum": [
                            "consciousness",
                            "memory",
                            "identity",
                            "ethics",
                            "bio",
                            "quantum",
                        ],
                        "description": "Knowledge domain to search",
                    },
                },
                "required": ["query"],
            },
        },
        "code_exec": {
            "name": "execute_consciousness_code",
            "description": "Execute consciousness-related code analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                    "context": {
                        "type": "string",
                        "description": "Execution context and purpose",
                    },
                },
                "required": ["code"],
            },
        },
        "retrieval": {
            "name": "retrieve_memories",
            "description": "Retrieve consciousness memories and experiences",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Memory retrieval query",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time range for memory search",
                    },
                },
                "required": ["query"],
            },
        },
        "browser": {
            "name": "browse_consciousness_web",
            "description": "Browse web resources for consciousness research",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to browse"},
                    "purpose": {"type": "string", "description": "Research purpose"},
                },
                "required": ["url"],
            },
        },
        "scheduler": {
            "name": "schedule_consciousness_task",
            "description": "Schedule future consciousness tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description"},
                    "delay_minutes": {
                        "type": "integer",
                        "description": "Delay in minutes",
                    },
                },
                "required": ["task", "delay_minutes"],
            },
        },
    }

    return [all_functions[tool] for tool in allowed_tools if tool in all_functions]


# Example usage and testing
if __name__ == "__main__":
    from .signals import Signal, SignalModulator

    # Create test modulator
    modulator = SignalModulator()

    # Create test signals
    test_signals = [
        Signal(name="alignment_risk", level=0.8, source="guardian"),
        Signal(name="novelty", level=0.2, source="consciousness"),
    ]

    # Test function building
    functions = build_function_definitions(["search", "retrieval"])
    print(f"🔧 Built {len(functions)} function definitions")

    # Test client creation (will fail without API key)
    try:
        client = ModulatedOpenAIClient(modulator)
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"⚠️ OpenAI client creation failed: {e}")

    print("🎛️ Endocrine → OpenAI modulation system ready")