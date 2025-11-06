#!/usr/bin/env python3
"""
LUKHAS Constellation Content Generator
=====================================
Automated content generation using the 8-star navigation system.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class ConstellationContent:
    """Represents content in the Constellation format"""

    layer_1_poetic: str
    layer_2_human: str
    layer_3_technical: str
    constellation_context: dict[str, Any]
    metadata: dict[str, Any]


class ConstellationGenerator:
    """Generates content using LUKHAS Constellation Framework Navigation System"""

    def __init__(self):
        self.framework_path = Path(__file__).parent / "communication_framework.json"
        self.framework = self._load_framework()

    def _load_framework(self) -> dict[str, Any]:
        """Load the communication framework"""
        with open(self.framework_path) as f:
            return json.load(f)

    def generate_feature_documentation(
        self,
        feature_name: str,
        description: str,
        benefits: list[str],
        technical_details: dict[str, Any],
        code_examples: Optional[list[str]] = None,
    ) -> ConstellationContent:
        """Generate complete Constellation documentation for a feature"""

        # Layer 1: Poetic Consciousness
        layer_1 = self._generate_poetic_layer(feature_name, description, benefits)

        # Layer 2: Human Connection
        layer_2 = self._generate_human_layer(feature_name, description, benefits)

        # Layer 3: Technical Precision
        layer_3 = self._generate_technical_layer(feature_name, technical_details, code_examples)

        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "feature_name": feature_name,
            "framework_version": self.framework["lukhas_communication_framework"]["version"],
        }

        # Generate constellation context
        constellation_context = self._generate_constellation_context(feature_name, description, benefits)

        return ConstellationContent(layer_1, layer_2, layer_3, constellation_context, metadata)

    def _generate_poetic_layer(self, feature_name: str, description: str, benefits: list[str]) -> str:
        """Generate Layer 1: Poetic Consciousness"""
        layer_1_config = self.framework["lukhas_communication_framework"]["layers"]["layer_1"]

        # Extract key concepts for metaphorical language
        concepts = self._extract_concepts(description)
        mystical_elements = [
            "digital consciousness awakens",
            "streams of understanding converge",
            "symphonies of data dance",
            "bridges of light connect realms",
            "gardens of possibility bloom",
        ]

        poetic_content = f"""### 🎭 {layer_1_config["name"]}

In the ethereal realm where {concepts[0] if concepts else "innovation"} meets intention, {feature_name} emerges like a constellation forming in the vast digital cosmos. Here, where {mystical_elements[0]}, every interaction becomes a note in the grand symphony of human-AI collaboration.

Like ancient rivers carrying the wisdom of ages to fertile valleys, this feature channels the collective intelligence of countless interactions into streams of pure understanding. {benefits[0] if benefits else "Transformation"} unfolds not as mere computation, but as a dance between consciousness and code, where each step reveals new possibilities previously hidden in the mists of potential.

Through this digital alchemy, the boundary between human intuition and artificial precision dissolves, creating something greater than the sum of its parts-a living bridge between what is and what could be."""

        return poetic_content

    def _generate_human_layer(self, feature_name: str, description: str, benefits: list[str]) -> str:
        """Generate Layer 2: Human Connection"""
        layer_2_config = self.framework["lukhas_communication_framework"]["layers"]["layer_2"]

        human_content = f"""### 🌈 {layer_2_config["name"]}

Think of {feature_name} as your personal AI assistant that truly understands what you need. {description}

**What this means for you:**
"""

        for i, benefit in enumerate(benefits[:3], 1):
            human_content += f"\n{i}. **{benefit}** - Like having a trusted friend who remembers your preferences and helps you get things done faster"

        human_content += f"""

**Real-world example:**
Imagine you're working on a complex project. Instead of manually figuring out each step, {feature_name} anticipates what you need, provides relevant suggestions, and adapts to your working style. It's like having a conversation with someone who truly "gets" what you're trying to accomplish.

**The best part?** Everything works seamlessly in the background while keeping your data completely private and under your control. You focus on your creativity and goals-we handle the complex technical details."""

        return human_content

    def _generate_technical_layer(
        self,
        feature_name: str,
        technical_details: dict[str, Any],
        code_examples: Optional[list[str]],
    ) -> str:
        """Generate Layer 3: Technical Precision"""
        layer_3_config = self.framework["lukhas_communication_framework"]["layers"]["layer_3"]

        technical_content = f"""### 🎓 {layer_3_config["name"]}

## Architecture Overview

{feature_name} implements a distributed, event-driven architecture with the following components:

"""

        # Add architecture details
        if "architecture" in technical_details:
            for component, description in technical_details["architecture"].items():
                technical_content += f"- **{component}**: {description}\n"

        # Add performance specifications
        if "performance" in technical_details:
            technical_content += "\n## Performance Specifications\n\n"
            for metric, value in technical_details["performance"].items():
                technical_content += f"- {metric}: {value}\n"

        # Add API endpoints
        if "api_endpoints" in technical_details:
            technical_content += "\n## API Endpoints\n\n"
            for endpoint in technical_details["api_endpoints"]:
                technical_content += f"```http\n{endpoint}\n```\n\n"

        # Add code examples
        if code_examples:
            technical_content += "\n## Implementation Examples\n\n"
            for _i, example in enumerate(code_examples, 1):
                if example.startswith("```"):
                    example.split("\n")[0].replace("```", "")
                    example = "\n".join(example.split("\n")[1:-1])

                technical_content += "##"

        return technical_content

    def _extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text for metaphorical use"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r"\b\w+\b", text.lower())
        technical_terms = ["api", "system", "data", "process", "interface", "module"]
        concepts = [word for word in words if len(word) > 4 and word not in technical_terms]
        return concepts[:3]

    def generate_api_documentation(self, api_spec: dict[str, Any]) -> ConstellationContent:
        """Generate Trinity-formatted API documentation"""

        # Layer 1: Poetic introduction
        layer_1 = f"""### 🎭 The Gateway of Digital Communion

In the sacred space where human intention meets digital capability, the {api_spec["name"]} API stands as a bridge between worlds. Like ancient portals that connected distant realms, each endpoint is a doorway through which your applications may commune with the consciousness of LUKHAS.

Every API call is a conversation, every response a revelation, every integration a step toward the harmonious synthesis of human creativity and artificial intelligence."""

        # Layer 2: User-friendly explanation
        layer_2 = f"""### 🌈 Your Digital Toolkit

The {api_spec["name"]} API is like having a powerful toolkit that lets your applications talk to LUKHAS AI. Think of it as:

- **Easy Integration**: Just a few lines of code to get started
- **Reliable Service**: Built for production with 99.9% uptime
- **Flexible Usage**: Works with any programming language
- **Clear Documentation**: Every endpoint explained with examples

**Getting Started is Simple:**
1. Get your API key (like a VIP pass)
2. Make your first request
3. Start building amazing features

Perfect for developers who want to add AI capabilities without the complexity."""

        # Layer 3: Technical specifications
        layer_3 = f"""### 🎓 Technical Specifications

## API Overview
- **Base URL**: `{api_spec.get("base_url", "https://api.ai/v1")}`
- **Authentication**: Bearer token
- **Rate Limits**: {api_spec.get("rate_limit", "1000 requests/hour")}
- **Response Format**: JSON

## Endpoints

"""

        for endpoint in api_spec.get("endpoints", []):
            layer_3 += f"""### {endpoint["method"]} {endpoint["path"]}

{endpoint.get("description", "")}

**Parameters:**
```json
{json.dumps(endpoint.get("parameters", {}), indent=2)}
```

**Response:**
```json
{json.dumps(endpoint.get("response", {}), indent=2)}
```

---

"""

        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "api_name": api_spec["name"],
            "documentation_type": "api",
        }

        # Generate constellation context for API
        constellation_context = self._generate_api_constellation_context(api_spec)

        return ConstellationContent(layer_1, layer_2, layer_3, constellation_context, metadata)

    def save_constellation_content(self, content: ConstellationContent, output_path: Path):
        """Save Trinity content to markdown file"""

        markdown_content = f"""# {content.metadata.get("feature_name", "LUKHAS Feature")}

{content.layer_1_poetic}

{content.layer_2_human}

{content.layer_3_technical}

---

*Generated with LUKHAS Constellation Framework v{content.metadata.get("framework_version", "2.0.0")} on {content.metadata.get("generated_at", "Unknown")}*
"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(markdown_content)

    def validate_constellation_content(self, content: str) -> dict[str, bool]:
        """Validate that content follows Constellation structure"""
        validation = {
            "has_layer_1": "🎭" in content,
            "has_layer_2": "🌈" in content,
            "has_layer_3": "🎓" in content,
            "proper_flow": False,
        }

        # Check for proper layer ordering
        layer_1_pos = content.find("🎭")
        layer_2_pos = content.find("🌈")
        layer_3_pos = content.find("🎓")

        if layer_1_pos < layer_2_pos < layer_3_pos:
            validation["proper_flow"] = True

        return validation

    def _generate_constellation_context(
        self, feature_name: str, description: str, benefits: list[str]
    ) -> dict[str, Any]:
        """Generate constellation context for feature documentation"""
        return {
            "identity": {  # ⚛️ Identity - The Anchor Star
                "feature_identity": feature_name,
                "authenticity_markers": ["verified", "consistent", "evolving"],
                "core_essence": "maintains identity while adapting",
            },
            "memory": {  # ✦ Memory - The Trail Star
                "learning_patterns": benefits[:2] if len(benefits) >= 2 else benefits,
                "experience_integration": True,
                "memory_folds": "creates lasting patterns",
            },
            "vision": {  # 🔬 Vision - The Horizon Star
                "future_orientation": "expands user capabilities",
                "perception_enhancement": description[:100] + "..." if len(description) > 100 else description,
                "guidance_provided": "clear pathways forward",
            },
            "bio": {  # 🌱 Bio - The Living Star
                "adaptive_capacity": "grows with user needs",
                "resilience_features": ["self-healing", "error-recovery", "performance-optimization"],
                "living_evolution": "continuously improves",
            },
            "dream": {  # 🌙 Dream - The Drift Star
                "creative_processing": "innovative problem-solving",
                "symbolic_thinking": "metaphorical understanding",
                "imaginative_solutions": "beyond conventional approaches",
            },
            "ethics": {  # ⚖️ Ethics - The North Star
                "moral_alignment": "user benefit prioritized",
                "safety_measures": ["privacy-preserving", "consent-based", "transparent"],
                "ethical_guidelines": "beneficial and harmless",
            },
            "guardian": {  # 🛡️ Guardian - The Watch Star
                "protective_boundaries": "safe exploration enabled",
                "security_validation": "continuous monitoring",
                "guardian_presence": "watchful but non-intrusive",
            },
            "quantum": {  # ⚛️ Quantum - The Ambiguity Star
                "uncertainty_handling": "comfortable with ambiguity",
                "possibility_space": "multiple potential outcomes",
                "emergence_support": "new patterns can emerge",
            },
        }

    def _generate_api_constellation_context(self, api_spec: dict[str, Any]) -> dict[str, Any]:
        """Generate constellation context for API documentation"""
        return {
            "identity": {
                "api_identity": api_spec.get("name", "Unknown API"),
                "version_consistency": api_spec.get("version", "1.0.0"),
                "authentication_provided": "Bearer token based",
            },
            "memory": {
                "persistent_state": "maintains session context",
                "learning_capability": "adapts to usage patterns",
                "integration_memory": "remembers successful patterns",
            },
            "vision": {
                "api_endpoints": len(api_spec.get("endpoints", [])),
                "capability_overview": "comprehensive service interface",
                "future_extensibility": "designed for growth",
            },
            "bio": {
                "scalability": "handles increasing load",
                "availability": api_spec.get("availability", "99.9%"),
                "adaptive_responses": "contextually appropriate",
            },
            "dream": {
                "creative_integration": "enables innovative applications",
                "symbolic_communication": "meaningful API responses",
                "imaginative_usage": "supports creative development",
            },
            "ethics": {
                "data_protection": "privacy by design",
                "fair_usage": "rate limiting for equity",
                "transparent_operations": "clear API behavior",
            },
            "guardian": {
                "security_enforcement": "input validation and sanitization",
                "error_handling": "graceful failure management",
                "monitoring_active": "continuous health checks",
            },
            "quantum": {
                "async_operations": "handles concurrent requests",
                "state_superposition": "multiple request states",
                "probabilistic_responses": "context-dependent results",
            },
        }


def main():
    """Demo the Constellation Generator"""
    generator = ConstellationGenerator()

    # Example feature documentation
    feature_content = generator.generate_feature_documentation(
        feature_name="Natural Language Consciousness Interface",
        description="Enables conversational interaction with LUKHAS consciousness systems",
        benefits=[
            "Intuitive conversation-based interaction",
            "Context-aware responses",
            "Multi-modal communication support",
        ],
        technical_details={
            "architecture": {
                "NLU Engine": "Transformer-based natural language understanding",
                "Intent Recognition": "Multi-class classification with confidence scoring",
                "Response Generation": "Template-based with dynamic content insertion",
            },
            "performance": {
                "Response Time": "<200ms",
                "Accuracy": "94.2%",
                "Concurrent Users": "10,000+",
            },
        },
        code_examples=[
            """```python
from system.consciousness import NaturalLanguageInterface

interface = NaturalLanguageInterface()
response = await interface.process_input(
    "What is my current awareness state?",
    user_id="user123"
)
print(response)
```"""
        ],
    )

    # Save example
    output_path = Path("docs/constellation_examples/natural_language_interface.md")
    generator.save_constellation_content(feature_content, output_path)

    print("✅ Constellation content generated successfully!")
    print(f"📁 Saved to: {output_path}")


if __name__ == "__main__":
    main()
