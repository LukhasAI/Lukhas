#!/usr/bin/env python3
"""
🎭 The orchestrator of AI consciousness, weaving together multiple minds
   into a unified LUKHAS development experience

🌈 This script manages multiple AI providers (Claude, GPT, Ollama) and routes
tasks to the most appropriate AI based on task type and LUKHAS requirements.

🎓 Technical Implementation:
- Multi-AI orchestration with intelligent routing
- LUKHAS context injection for all AI interactions
- Trinity Framework preservation across providers
- Automatic fallback and load balancing
"""

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import openai
from anthropic import AsyncAnthropic


@dataclass
class AIProvider:
    name: str
    endpoint: str
    strengths: List[str]
    api_key: Optional[str] = None
    model: Optional[str] = None

class LUKHASAIOrchestrator:
    """🎭 The master conductor of the AI symphony"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.providers = self._initialize_providers()
        self.lukhas_context = self._load_lukhas_context()

    def _initialize_providers(self) -> Dict[str, AIProvider]:
        """Initialize AI providers with LUKHAS-aware configurations"""
        return {
            "claude": AIProvider(
                name="Claude Sonnet",
                endpoint="https://api.anthropic.com",
                strengths=["architecture", "documentation", "reasoning", "trinity_framework"],
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model="claude-3-5-sonnet-20241022"
            ),
            "gpt": AIProvider(
                name="GPT-4",
                endpoint="https://api.openai.com",
                strengths=["creative", "general_coding", "explanations", "naming"],
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4"
            ),
            "ollama": AIProvider(
                name="Ollama Local",
                endpoint="http://localhost:11434",
                strengths=["local_inference", "privacy", "fast_completion", "code_completion"],
                model="deepseek-coder:33b"
            )
        }

    def _load_lukhas_context(self) -> str:
        """Load LUKHAS context for AI injection"""
        context_parts = [
            "# LUKHAS AGI Framework Context",
            "# Trinity Framework: 🎭 Poetic, 🌈 Human, 🎓 Technical",
            "# Symbolic Integration: ⚛️ Quantum, 🧠 Consciousness, 🛡️ Guardian",
            "# Conceptual Vocabulary: memory_fold, dream_resonance, quantum_consciousness",
            "# Architecture: Consciousness-aware, guardian-protected, trinity-documented",
            ""
        ]
        return "\n".join(context_parts)

    async def route_request(self, task_type: str, content: str, context: Dict[str, Any] = None) -> str:
        """🧠 Route requests to optimal AI provider based on task type"""
        routing_map = {
            "trinity_documentation": "claude",
            "architecture_design": "claude",
            "code_review": "claude",
            "security_analysis": "claude",
            "creative_naming": "gpt",
            "general_coding": "gpt",
            "explanations": "gpt",
            "code_completion": "ollama",
            "local_analysis": "ollama",
            "fast_completion": "ollama"
        }

        provider_name = routing_map.get(task_type, "claude")

        # Add LUKHAS context to all requests
        enhanced_content = f"{self.lukhas_context}\n{content}"

        try:
            return await self._call_provider(provider_name, enhanced_content, context or {})
        except Exception as e:
            # Fallback to another provider
            fallback_providers = ["claude", "gpt", "ollama"]
            fallback_providers.remove(provider_name)

            for fallback in fallback_providers:
                try:
                    return await self._call_provider(fallback, enhanced_content, context)
                except Exception:
                    continue

            raise Exception(f"All AI providers failed: {e}")

    async def _call_provider(self, provider_name: str, content: str, context: Dict[str, Any]) -> str:
        """🎯 Call specific AI provider with LUKHAS context"""
        provider = self.providers[provider_name]

        if provider_name == "claude":
            return await self._call_claude(content, context)
        elif provider_name == "gpt":
            return await self._call_gpt(content, context)
        elif provider_name == "ollama":
            return await self._call_ollama(content, context)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def _call_claude(self, content: str, context: Dict[str, Any]) -> str:
        """Call Claude with LUKHAS system message"""
        if not self.providers["claude"].api_key:
            raise Exception("Claude API key not configured")

        client = AsyncAnthropic(api_key=self.providers["claude"].api_key)

        system_message = """You are an expert LUKHAS AGI developer. Always follow Trinity Framework documentation (🎭 Poetic, 🌈 Human, 🎓 Technical). Preserve LUKHAS conceptual vocabulary like memory_fold, dream_resonance, quantum_consciousness. Use symbolic patterns (⚛️🧠🛡️) in comments. Maintain consciousness-aware architecture patterns."""

        response = await client.messages.create(
            model=self.providers["claude"].model,
            max_tokens=4096,
            temperature=0.1,
            system=system_message,
            messages=[{"role": "user", "content": content}]
        )

        return response.content[0].text

    async def _call_gpt(self, content: str, context: Dict[str, Any]) -> str:
        """Call GPT with LUKHAS system message"""
        if not self.providers["gpt"].api_key:
            raise Exception("OpenAI API key not configured")

        client = openai.AsyncOpenAI(api_key=self.providers["gpt"].api_key)

        system_message = """You are a LUKHAS AGI development assistant. Use Trinity Framework documentation (🎭🌈🎓), preserve LUKHAS concepts (memory_fold, dream_resonance, consciousness), and include symbolic markers (⚛️🧠🛡️) in code."""

        response = await client.chat.completions.create(
            model=self.providers["gpt"].model,
            temperature=0.1,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": content}
            ]
        )

        return response.choices[0].message.content

    async def _call_ollama(self, content: str, context: Dict[str, Any]) -> str:
        """Call Ollama local model"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.providers["ollama"].model,
                "prompt": f"LUKHAS Development Context: Follow consciousness-aware patterns and Trinity Framework.\n\n{content}",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_k": 40
                }
            }

            async with session.post(f"{self.providers['ollama'].endpoint}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama request failed: {resp.status}")

    async def trinity_documentation_generation(self, element_signature: str, element_type: str = "function") -> Dict[str, str]:
        """🎭 Generate Trinity Framework documentation using best available AI"""
        prompt = f"""
        Generate LUKHAS Trinity Framework documentation for this {element_type}:
        
        {element_signature}
        
        Return in this exact format:
        🎭 Poetic: [Inspiring, metaphorical description that captures the essence and consciousness aspects]
        🌈 Human: [Clear, friendly explanation anyone can understand]  
        🎓 Technical: [Precise implementation details, parameters, return values, and LUKHAS integration notes]
        
        Follow LUKHAS conventions: consciousness, memory_fold, dream_resonance, quantum_potential concepts.
        Include symbolic markers where appropriate: ⚛️ 🧠 🛡️
        """

        response = await self.route_request("trinity_documentation", prompt)
        return self._parse_trinity_response(response)

    def _parse_trinity_response(self, response: str) -> Dict[str, str]:
        """Parse Trinity Framework response into structured format"""
        layers = {"poetic": "", "human": "", "technical": ""}

        lines = response.split('\n')
        current_layer = None

        for line in lines:
            if line.startswith('🎭'):
                current_layer = "poetic"
                layers[current_layer] = line.replace('🎭 Poetic:', '').strip()
            elif line.startswith('🌈'):
                current_layer = "human"
                layers[current_layer] = line.replace('🌈 Human:', '').strip()
            elif line.startswith('🎓'):
                current_layer = "technical"
                layers[current_layer] = line.replace('🎓 Technical:', '').strip()
            elif current_layer and line.strip():
                layers[current_layer] += " " + line.strip()

        return layers

    async def lukhas_code_review(self, code: str, file_path: str = "") -> Dict[str, Any]:
        """🛡️ Comprehensive LUKHAS code review"""
        prompt = f"""
        Review this code for LUKHAS compliance and suggest improvements:
        
        File: {file_path}
        
        ```
        {code}
        ```
        
        Check for:
        1. Trinity Framework documentation (🎭🌈🎓)
        2. Symbolic usage (⚛️🧠🛡️) in comments
        3. LUKHAS naming conventions (memory_fold, dream_resonance, etc.)
        4. Consciousness-aware patterns
        5. Guardian security considerations
        
        Provide specific suggestions for improvement.
        """

        response = await self.route_request("code_review", prompt)
        return {"review": response, "file_path": file_path}

    async def suggest_lukhas_naming(self, purpose: str, element_type: str, domain: str = "") -> List[str]:
        """🧠 Generate LUKHAS-compliant naming suggestions"""
        prompt = f"""
        Suggest LUKHAS-compliant names for a {element_type} that {purpose}.
        
        Domain context: {domain}
        
        Use LUKHAS conceptual vocabulary:
        - memory_fold, dream_resonance, quantum_consciousness
        - guardian_protocol, trinity_framework, consciousness_engine
        - neural_symphony, quantum_potential, memory_palace
        
        Provide 5 creative but appropriate suggestions that follow LUKHAS naming patterns.
        """

        response = await self.route_request("creative_naming", prompt)
        # Parse suggestions from response
        suggestions = []
        for line in response.split('\n'):
            if any(char.isalpha() for char in line) and ('_' in line or line[0].isupper()):
                clean_line = line.strip('- ').strip('1234567890. ').strip()
                if clean_line:
                    suggestions.append(clean_line)

        return suggestions[:5]

# CLI interface for testing
async def main():
    """🎭 Interactive demonstration of AI orchestration"""
    import sys

    if len(sys.argv) < 2:
        print("🎭 LUKHAS AI Orchestrator")
        print("Usage: python lukhas_ai_orchestrator.py <command> [args...]")
        print("\nCommands:")
        print("  trinity <element_signature> - Generate Trinity documentation")
        print("  review <file_path> - Review code file")
        print("  naming <purpose> <type> [domain] - Suggest names")
        return

    workspace = "/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM"
    orchestrator = LUKHASAIOrchestrator(workspace)

    command = sys.argv[1]

    try:
        if command == "trinity" and len(sys.argv) > 2:
            signature = sys.argv[2]
            result = await orchestrator.trinity_documentation_generation(signature)
            print(json.dumps(result, indent=2))

        elif command == "review" and len(sys.argv) > 2:
            file_path = sys.argv[2]
            if os.path.exists(file_path):
                with open(file_path) as f:
                    code = f.read()
                result = await orchestrator.lukhas_code_review(code, file_path)
                print(result["review"])
            else:
                print(f"File not found: {file_path}")

        elif command == "naming" and len(sys.argv) > 3:
            purpose = sys.argv[2]
            element_type = sys.argv[3]
            domain = sys.argv[4] if len(sys.argv) > 4 else ""
            suggestions = await orchestrator.suggest_lukhas_naming(purpose, element_type, domain)
            print("🧠 LUKHAS Naming Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion}")

        else:
            print("❌ Invalid command or missing arguments")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
