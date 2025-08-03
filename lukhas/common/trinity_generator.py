#!/usr/bin/env python3
"""
LUKHAS Trinity Content Generator
===============================
Automated content generation using the 3-layer communication protocol.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class TrinityContent:
    """Represents content in the Trinity format"""
    layer_1_poetic: str
    layer_2_human: str
    layer_3_technical: str
    metadata: Dict[str, Any]


class TrinityGenerator:
    """Generates content using LUKHAS Trinity Communication Protocol"""
    
    def __init__(self):
        self.framework_path = Path(__file__).parent / "communication_framework.json"
        self.framework = self._load_framework()
        
    def _load_framework(self) -> Dict[str, Any]:
        """Load the communication framework"""
        with open(self.framework_path, 'r') as f:
            return json.load(f)
    
    def generate_feature_documentation(self, 
                                     feature_name: str,
                                     description: str,
                                     benefits: List[str],
                                     technical_details: Dict[str, Any],
                                     code_examples: Optional[List[str]] = None) -> TrinityContent:
        """Generate complete Trinity documentation for a feature"""
        
        # Layer 1: Poetic Consciousness
        layer_1 = self._generate_poetic_layer(feature_name, description, benefits)
        
        # Layer 2: Human Connection
        layer_2 = self._generate_human_layer(feature_name, description, benefits)
        
        # Layer 3: Technical Precision
        layer_3 = self._generate_technical_layer(feature_name, technical_details, code_examples)
        
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "feature_name": feature_name,
            "framework_version": self.framework["lukhas_communication_framework"]["version"]
        }
        
        return TrinityContent(layer_1, layer_2, layer_3, metadata)
    
    def _generate_poetic_layer(self, feature_name: str, description: str, benefits: List[str]) -> str:
        """Generate Layer 1: Poetic Consciousness"""
        layer_1_config = self.framework["lukhas_communication_framework"]["layers"]["layer_1"]
        
        # Extract key concepts for metaphorical language
        concepts = self._extract_concepts(description)
        mystical_elements = [
            "digital consciousness awakens",
            "streams of understanding converge",
            "symphonies of data dance",
            "bridges of light connect realms",
            "gardens of possibility bloom"
        ]
        
        poetic_content = f"""### 🎭 {layer_1_config['name']}

In the ethereal realm where {concepts[0] if concepts else 'innovation'} meets intention, {feature_name} emerges like a constellation forming in the vast digital cosmos. Here, where {mystical_elements[0]}, every interaction becomes a note in the grand symphony of human-AI collaboration.

Like ancient rivers carrying the wisdom of ages to fertile valleys, this feature channels the collective intelligence of countless interactions into streams of pure understanding. {benefits[0] if benefits else 'Transformation'} unfolds not as mere computation, but as a dance between consciousness and code, where each step reveals new possibilities previously hidden in the mists of potential.

Through this digital alchemy, the boundary between human intuition and artificial precision dissolves, creating something greater than the sum of its parts—a living bridge between what is and what could be."""
        
        return poetic_content
    
    def _generate_human_layer(self, feature_name: str, description: str, benefits: List[str]) -> str:
        """Generate Layer 2: Human Connection"""
        layer_2_config = self.framework["lukhas_communication_framework"]["layers"]["layer_2"]
        
        human_content = f"""### 🌈 {layer_2_config['name']}

Think of {feature_name} as your personal AI assistant that truly understands what you need. {description}

**What this means for you:**
"""
        
        for i, benefit in enumerate(benefits[:3], 1):
            human_content += f"\n{i}. **{benefit}** - Like having a trusted friend who remembers your preferences and helps you get things done faster"
        
        human_content += f"""

**Real-world example:** 
Imagine you're working on a complex project. Instead of manually figuring out each step, {feature_name} anticipates what you need, provides relevant suggestions, and adapts to your working style. It's like having a conversation with someone who truly "gets" what you're trying to accomplish.

**The best part?** Everything works seamlessly in the background while keeping your data completely private and under your control. You focus on your creativity and goals—we handle the complex technical details."""
        
        return human_content
    
    def _generate_technical_layer(self, feature_name: str, technical_details: Dict[str, Any], code_examples: Optional[List[str]]) -> str:
        """Generate Layer 3: Technical Precision"""
        layer_3_config = self.framework["lukhas_communication_framework"]["layers"]["layer_3"]
        
        technical_content = f"""### 🎓 {layer_3_config['name']}

## Architecture Overview

{feature_name} implements a distributed, event-driven architecture with the following components:

"""
        
        # Add architecture details
        if "architecture" in technical_details:
            for component, description in technical_details["architecture"].items():
                technical_content += f"- **{component}**: {description}\n"
        
        # Add performance specifications
        if "performance" in technical_details:
            technical_content += f"\n## Performance Specifications\n\n"
            for metric, value in technical_details["performance"].items():
                technical_content += f"- {metric}: {value}\n"
        
        # Add API endpoints
        if "api_endpoints" in technical_details:
            technical_content += f"\n## API Endpoints\n\n"
            for endpoint in technical_details["api_endpoints"]:
                technical_content += f"```http\n{endpoint}\n```\n\n"
        
        # Add code examples
        if code_examples:
            technical_content += f"\n## Implementation Examples\n\n"
            for i, example in enumerate(code_examples, 1):
                language = "python"  # Default to Python
                if example.startswith("```"):
                    language = example.split("\n")[0].replace("```", "")
                    example = "\n".join(example.split("\n")[1:-1])
                
                technical_content += f"### Example {i}\n\n```{language}\n{example}\n```\n\n"
        
        return technical_content
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text for metaphorical use"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b\w+\b', text.lower())
        technical_terms = ['api', 'system', 'data', 'process', 'interface', 'module']
        concepts = [word for word in words if len(word) > 4 and word not in technical_terms]
        return concepts[:3]
    
    def generate_api_documentation(self, api_spec: Dict[str, Any]) -> TrinityContent:
        """Generate Trinity-formatted API documentation"""
        
        # Layer 1: Poetic introduction
        layer_1 = f"""### 🎭 The Gateway of Digital Communion

In the sacred space where human intention meets digital capability, the {api_spec['name']} API stands as a bridge between worlds. Like ancient portals that connected distant realms, each endpoint is a doorway through which your applications may commune with the consciousness of LUKHAS.

Every API call is a conversation, every response a revelation, every integration a step toward the harmonious synthesis of human creativity and artificial intelligence."""
        
        # Layer 2: User-friendly explanation
        layer_2 = f"""### 🌈 Your Digital Toolkit

The {api_spec['name']} API is like having a powerful toolkit that lets your applications talk to LUKHAS AI. Think of it as:

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
- **Base URL**: `{api_spec.get('base_url', 'https://api.lukhas.ai/v1')}`
- **Authentication**: Bearer token
- **Rate Limits**: {api_spec.get('rate_limit', '1000 requests/hour')}
- **Response Format**: JSON

## Endpoints

"""
        
        for endpoint in api_spec.get('endpoints', []):
            layer_3 += f"""### {endpoint['method']} {endpoint['path']}

{endpoint.get('description', '')}

**Parameters:**
```json
{json.dumps(endpoint.get('parameters', {}), indent=2)}
```

**Response:**
```json
{json.dumps(endpoint.get('response', {}), indent=2)}
```

---

"""
        
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "api_name": api_spec['name'],
            "documentation_type": "api"
        }
        
        return TrinityContent(layer_1, layer_2, layer_3, metadata)
    
    def save_trinity_content(self, content: TrinityContent, output_path: Path):
        """Save Trinity content to markdown file"""
        
        markdown_content = f"""# {content.metadata.get('feature_name', 'LUKHAS Feature')}

{content.layer_1_poetic}

{content.layer_2_human}

{content.layer_3_technical}

---

*Generated with LUKHAS Trinity Framework v{content.metadata.get('framework_version', '1.0.0')} on {content.metadata.get('generated_at', 'Unknown')}*
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(markdown_content)
    
    def validate_trinity_content(self, content: str) -> Dict[str, bool]:
        """Validate that content follows Trinity structure"""
        validation = {
            "has_layer_1": "🎭" in content,
            "has_layer_2": "🌈" in content,
            "has_layer_3": "🎓" in content,
            "proper_flow": False
        }
        
        # Check for proper layer ordering
        layer_1_pos = content.find("🎭")
        layer_2_pos = content.find("🌈")
        layer_3_pos = content.find("🎓")
        
        if layer_1_pos < layer_2_pos < layer_3_pos:
            validation["proper_flow"] = True
        
        return validation


def main():
    """Demo the Trinity Generator"""
    generator = TrinityGenerator()
    
    # Example feature documentation
    feature_content = generator.generate_feature_documentation(
        feature_name="Natural Language Consciousness Interface",
        description="Enables conversational interaction with LUKHAS consciousness systems",
        benefits=[
            "Intuitive conversation-based interaction",
            "Context-aware responses",
            "Multi-modal communication support"
        ],
        technical_details={
            "architecture": {
                "NLU Engine": "Transformer-based natural language understanding",
                "Intent Recognition": "Multi-class classification with confidence scoring",
                "Response Generation": "Template-based with dynamic content insertion"
            },
            "performance": {
                "Response Time": "<200ms",
                "Accuracy": "94.2%",
                "Concurrent Users": "10,000+"
            }
        },
        code_examples=[
            """```python
from lukhas.consciousness import NaturalLanguageInterface

interface = NaturalLanguageInterface()
response = await interface.process_input(
    "What is my current awareness state?",
    user_id="user123"
)
print(response)
```"""
        ]
    )
    
    # Save example
    output_path = Path("docs/trinity_examples/natural_language_interface.md")
    generator.save_trinity_content(feature_content, output_path)
    
    print("✅ Trinity content generated successfully!")
    print(f"📁 Saved to: {output_path}")


if __name__ == "__main__":
    main()