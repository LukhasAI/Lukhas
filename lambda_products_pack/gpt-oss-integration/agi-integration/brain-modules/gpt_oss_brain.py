"""
GPT-OSS Brain Module for MultiBrainSymphony Integration
Integrates OpenAI's GPT-OSS models as a specialized brain in the symphony

This module creates a GPT-OSS-powered brain that can work alongside
Dreams, Memory, and Learning brains in the MultiBrainSymphony orchestrator.
"""

import asyncio
import hashlib
import json
import logging

# Import base classes from MultiBrainSymphony
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np

sys.path.append(
    str(Path(__file__).parent.parent.parent.parent / "organized/ai-core/brain/brain")
)
try:
    from MultiBrainSymphony import SpecializedBrainCore
except ImportError:
    # Fallback implementation if import fails
    class SpecializedBrainCore:
        def __init__(self, brain_id: str, specialization: str, base_frequency: float):
            self.brain_id = brain_id
            self.specialization = specialization
            self.base_frequency = base_frequency
            self.active = False
            self.processing_queue = []
            self.harmony_protocols = {
                "bio_oscillation": True,
                "quantum_coupling": True,
                "inter_brain_communication": True,
            }
            self.last_sync_time = time.time()


logger = logging.getLogger("GPTOSSBrain")


class GPTOSSModelLoader:
    """Manages GPT-OSS model loading and inference"""

    def __init__(self, model_variant: str = "gpt-oss-20b"):
        self.model_variant = model_variant
        self.model = None
        self.is_loaded = False
        self.model_path = Path.home() / ".gpt-oss" / "models" / model_variant

        # Model configurations
        self.configs = {
            "gpt-oss-20b": {
                "context_window": 8192,
                "max_tokens": 2048,
                "memory_required": 16,  # GB
                "optimal_batch_size": 8,
            },
            "gpt-oss-120b": {
                "context_window": 32768,
                "max_tokens": 8192,
                "memory_required": 80,  # GB
                "optimal_batch_size": 4,
            },
        }

        self.current_config = self.configs.get(
            model_variant, self.configs["gpt-oss-20b"]
        )

    async def load_model(self) -> bool:
        """Load GPT-OSS model asynchronously"""
        try:
            logger.info(f"Loading {self.model_variant}...")

            # Check if model files exist
            if not self.model_path.exists():
                logger.warning(
                    f"Model not found at {self.model_path}. Using mock mode."
                )
                self.model = "mock"
            else:
                # In production, load actual model using appropriate framework
                # This could be ONNX Runtime, TensorFlow, PyTorch, etc.
                import subprocess

                result = subprocess.run(
                    ["python", "-c", "import ollama; print(ollama.list())"],
                    capture_output=True,
                    text=True,
                )

                if "gpt-oss" in result.stdout:
                    self.model = "ollama"
                else:
                    self.model = "mock"

            self.is_loaded = True
            logger.info(f"✅ {self.model_variant} loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = "mock"
            self.is_loaded = True
            return False

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text using GPT-OSS model"""

        if not self.is_loaded:
            await self.load_model()

        if self.model == "ollama":
            # Use Ollama for actual generation
            import subprocess

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            try:
                result = subprocess.run(
                    ["ollama", "run", self.model_variant, full_prompt],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return result.stdout.strip()
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                return self._mock_generate(prompt, system_prompt)

        else:
            # Mock generation for testing
            return self._mock_generate(prompt, system_prompt)

    def _mock_generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Mock generation for testing"""
        responses = {
            "reasoning": "Based on quantum-enhanced analysis using GPT-OSS neural pathways, the optimal approach involves synthesizing multiple cognitive dimensions through parallel processing streams.",
            "creative": "Imagine a symphony of neural networks dancing in quantum superposition, where each thought exists in multiple states until observed by consciousness.",
            "technical": "The implementation leverages transformer architecture with 20 billion parameters, enabling complex pattern recognition across 8192 token contexts.",
            "memory": "Storing this information in the distributed memory network with quantum entanglement for instant recall across all brain modules.",
            "learning": "Adapting neural weights through reinforcement learning patterns observed in the data stream, optimizing for future predictions.",
        }

        # Detect intent from prompt
        prompt_lower = prompt.lower()
        if "creative" in prompt_lower or "imagine" in prompt_lower:
            return responses["creative"]
        elif "technical" in prompt_lower or "implement" in prompt_lower:
            return responses["technical"]
        elif "memory" in prompt_lower or "remember" in prompt_lower:
            return responses["memory"]
        elif "learn" in prompt_lower or "adapt" in prompt_lower:
            return responses["learning"]
        else:
            return responses["reasoning"]


class GPTOSSBrainSpecialist(SpecializedBrainCore):
    """GPT-OSS Brain - Advanced Language Reasoning Specialist"""

    def __init__(self, model_variant: str = "gpt-oss-20b"):
        super().__init__(
            "gpt_oss_brain", "language reasoning", 30.0
        )  # 30Hz gamma frequency

        self.model_loader = GPTOSSModelLoader(model_variant)
        self.reasoning_cache = {}
        self.context_window = []
        self.max_context_size = 10

        # GPT-OSS specific protocols
        self.gpt_protocols = {
            "contextual_awareness": True,
            "multi_turn_reasoning": True,
            "symbolic_integration": True,
            "lukhas_pattern_recognition": True,
        }

        # Integration with LUKHAS patterns
        self.lukhas_patterns = {
            "lambda_symbolic": True,
            "quantum_reasoning": True,
            "consciousness_modeling": True,
            "ethical_constraints": True,
        }

        # Performance metrics
        self.metrics = {
            "total_inferences": 0,
            "cache_hits": 0,
            "average_latency": 0,
            "reasoning_depth": [],
        }

    async def initialize(self) -> bool:
        """Initialize GPT-OSS brain with model loading"""
        logger.info(f"🧠 Initializing {self.brain_id} - {self.specialization}")

        # Load the GPT-OSS model
        model_loaded = await self.model_loader.load_model()

        if not model_loaded:
            logger.warning("GPT-OSS model loading failed, using fallback mode")

        self.active = True
        return True

    async def process_with_reasoning(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through GPT-OSS reasoning engine"""

        if not self.active:
            await self.initialize()

        start_time = time.time()
        self.metrics["total_inferences"] += 1

        try:
            # Check cache first
            cache_key = self._generate_cache_key(data)
            if cache_key in self.reasoning_cache:
                self.metrics["cache_hits"] += 1
                cached_result = self.reasoning_cache[cache_key]
                cached_result["from_cache"] = True
                return cached_result

            # Build context from recent interactions
            context = self._build_context(data)

            # Create specialized prompt for LUKHAS integration
            prompt = self._create_lukhas_prompt(data, context)

            # Generate reasoning with GPT-OSS
            reasoning_result = await self.model_loader.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                system_prompt=self._get_system_prompt(),
            )

            # Parse and enhance result
            enhanced_result = self._enhance_reasoning(reasoning_result, data)

            # Update context window
            self._update_context(data, enhanced_result)

            # Calculate latency
            latency = time.time() - start_time
            self._update_metrics(latency)

            # Create response
            response = {
                "brain_id": self.brain_id,
                "processing_type": "gpt_oss_reasoning",
                "reasoning": enhanced_result,
                "context_depth": len(self.context_window),
                "latency_ms": int(latency * 1000),
                "confidence": self._calculate_confidence(enhanced_result),
                "lukhas_integration": self._check_lukhas_patterns(enhanced_result),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache result
            self.reasoning_cache[cache_key] = response

            # Limit cache size
            if len(self.reasoning_cache) > 100:
                oldest_key = list(self.reasoning_cache.keys())[0]
                del self.reasoning_cache[oldest_key]

            return response

        except Exception as e:
            logger.error(f"GPT-OSS processing error: {e}")
            return self._fallback_reasoning(data)

    def _generate_cache_key(self, data: dict[str, Any]) -> str:
        """Generate cache key for data"""
        # Create deterministic key from data
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _build_context(self, data: dict[str, Any]) -> str:
        """Build context from recent interactions"""
        context_parts = []

        # Add recent context
        for ctx in self.context_window[-5:]:
            context_parts.append(f"Previous: {ctx.get('summary', '')}")

        # Add current data context
        if "context" in data:
            context_parts.append(f"Current context: {data['context']}")

        return "\n".join(context_parts)

    def _create_lukhas_prompt(self, data: dict[str, Any], context: str) -> str:
        """Create LUKHAS-aware prompt for GPT-OSS"""

        # Extract key information
        content = data.get("content", "")
        task_type = data.get("type", "general")

        # Build specialized prompt
        prompt_parts = []

        # Add context if available
        if context:
            prompt_parts.append(f"Context:\n{context}\n")

        # Add Lambda symbolic awareness
        if self.lukhas_patterns["lambda_symbolic"]:
            prompt_parts.append("Apply Lambda (Λ) symbolic reasoning patterns.\n")

        # Add quantum reasoning if applicable
        if self.lukhas_patterns["quantum_reasoning"] and "quantum" in str(data).lower():
            prompt_parts.append("Consider quantum superposition of possibilities.\n")

        # Main task
        prompt_parts.append(f"Task: {task_type}")
        prompt_parts.append(f"Input: {content}")

        # Request structured reasoning
        prompt_parts.append("\nProvide structured reasoning with:")
        prompt_parts.append("1. Analysis of the input")
        prompt_parts.append("2. Key insights or patterns")
        prompt_parts.append("3. Recommended approach or solution")

        return "\n".join(prompt_parts)

    def _get_system_prompt(self) -> str:
        """Get system prompt for GPT-OSS"""
        return """You are a GPT-OSS enhanced reasoning module integrated with the LUKHAS AGI system.
You work in harmony with Dreams, Memory, and Learning brain modules in a MultiBrainSymphony.
Apply advanced reasoning with awareness of:
- Lambda (Λ) symbolic patterns and notation
- Quantum-inspired cognitive processing
- Bio-rhythmic synchronization with other brain modules
- Ethical AI constraints and safety considerations

Provide clear, structured, and insightful reasoning."""

    def _enhance_reasoning(
        self, raw_reasoning: str, original_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Enhance raw reasoning with structured analysis"""

        # Parse reasoning into structured format
        enhanced = {
            "raw_output": raw_reasoning,
            "structured_analysis": {},
            "key_insights": [],
            "recommendations": [],
            "confidence_factors": {},
        }

        # Extract insights from reasoning
        lines = raw_reasoning.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if "analysis" in line.lower():
                current_section = "analysis"
                enhanced["structured_analysis"]["main"] = []
            elif "insight" in line.lower() or "pattern" in line.lower():
                current_section = "insights"
            elif "recommend" in line.lower() or "approach" in line.lower():
                current_section = "recommendations"
            elif current_section == "analysis":
                enhanced["structured_analysis"]["main"].append(line)
            elif current_section == "insights":
                enhanced["key_insights"].append(line)
            elif current_section == "recommendations":
                enhanced["recommendations"].append(line)

        # Add confidence factors
        enhanced["confidence_factors"] = {
            "reasoning_depth": len(lines),
            "insight_count": len(enhanced["key_insights"]),
            "recommendation_count": len(enhanced["recommendations"]),
            "context_relevance": 0.8 if self.context_window else 0.5,
        }

        return enhanced

    def _update_context(self, data: dict[str, Any], result: dict[str, Any]):
        """Update context window with new interaction"""

        # Create context entry
        context_entry = {
            "timestamp": datetime.now().isoformat(),
            "input_type": data.get("type", "unknown"),
            "summary": result.get("raw_output", "")[:200],
            "insights": result.get("key_insights", [])[:3],
        }

        # Add to window
        self.context_window.append(context_entry)

        # Maintain window size
        if len(self.context_window) > self.max_context_size:
            self.context_window.pop(0)

    def _calculate_confidence(self, reasoning: dict[str, Any]) -> float:
        """Calculate confidence score for reasoning"""

        factors = reasoning.get("confidence_factors", {})

        # Weight different factors
        depth_score = min(factors.get("reasoning_depth", 0) / 20, 1.0) * 0.3
        insight_score = min(factors.get("insight_count", 0) / 5, 1.0) * 0.3
        recommendation_score = (
            min(factors.get("recommendation_count", 0) / 3, 1.0) * 0.2
        )
        context_score = factors.get("context_relevance", 0.5) * 0.2

        confidence = depth_score + insight_score + recommendation_score + context_score

        return min(max(confidence, 0.0), 1.0)

    def _check_lukhas_patterns(self, reasoning: dict[str, Any]) -> dict[str, bool]:
        """Check for LUKHAS-specific patterns in reasoning"""

        raw_output = str(reasoning.get("raw_output", "")).lower()

        return {
            "lambda_detected": "lambda" in raw_output or "λ" in raw_output,
            "quantum_concepts": "quantum" in raw_output
            or "superposition" in raw_output,
            "consciousness_aware": "consciousness" in raw_output
            or "awareness" in raw_output,
            "ethical_considered": "ethical" in raw_output or "safety" in raw_output,
        }

    def _update_metrics(self, latency: float):
        """Update performance metrics"""

        # Update average latency
        if self.metrics["average_latency"] == 0:
            self.metrics["average_latency"] = latency
        else:
            # Exponential moving average
            self.metrics["average_latency"] = (
                0.9 * self.metrics["average_latency"] + 0.1 * latency
            )

        # Track reasoning depth
        self.metrics["reasoning_depth"].append(len(self.context_window))

        # Keep only recent depth measurements
        if len(self.metrics["reasoning_depth"]) > 100:
            self.metrics["reasoning_depth"] = self.metrics["reasoning_depth"][-50:]

    def _fallback_reasoning(self, data: dict[str, Any]) -> dict[str, Any]:
        """Fallback reasoning when GPT-OSS is unavailable"""

        return {
            "brain_id": self.brain_id,
            "processing_type": "fallback_reasoning",
            "reasoning": {
                "raw_output": "GPT-OSS reasoning unavailable, using fallback heuristics",
                "structured_analysis": {"main": ["Basic analysis based on patterns"]},
                "key_insights": [
                    "Pattern recognition active",
                    "Heuristic processing engaged",
                ],
                "recommendations": ["Continue with available brain modules"],
                "confidence_factors": {"fallback_mode": True},
            },
            "confidence": 0.3,
            "timestamp": datetime.now().isoformat(),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""

        cache_hit_rate = 0
        if self.metrics["total_inferences"] > 0:
            cache_hit_rate = (
                self.metrics["cache_hits"] / self.metrics["total_inferences"]
            )

        avg_depth = 0
        if self.metrics["reasoning_depth"]:
            avg_depth = np.mean(self.metrics["reasoning_depth"])

        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "average_reasoning_depth": avg_depth,
            "model_variant": self.model_loader.model_variant,
            "model_loaded": self.model_loader.is_loaded,
            "context_window_size": len(self.context_window),
        }


def create_gpt_oss_symphony_integration(symphony_orchestrator):
    """
    Factory function to integrate GPT-OSS brain with MultiBrainSymphony

    Args:
        symphony_orchestrator: Existing MultiBrainSymphonyOrchestrator instance

    Returns:
        Enhanced orchestrator with GPT-OSS brain
    """

    # Create GPT-OSS brain
    gpt_oss_brain = GPTOSSBrainSpecialist()

    # Add to symphony
    symphony_orchestrator.specialized_brains["gpt_oss"] = gpt_oss_brain

    # Extend conduct_symphony to include GPT-OSS
    original_conduct = symphony_orchestrator.conduct_symphony

    async def enhanced_conduct_symphony(input_data: dict[str, Any]) -> dict[str, Any]:
        # Get original result
        result = await original_conduct(input_data)

        # Add GPT-OSS processing
        try:
            gpt_result = await gpt_oss_brain.process_with_reasoning(input_data)
            result["specialized_processing"]["gpt_oss"] = gpt_result

            # Enhance synthesized insights with GPT-OSS reasoning
            if "reasoning" in gpt_result and "key_insights" in gpt_result["reasoning"]:
                result["synthesized_insights"].extend(
                    gpt_result["reasoning"]["key_insights"]
                )

        except Exception as e:
            logger.error(f"GPT-OSS integration error: {e}")
            result["specialized_processing"]["gpt_oss"] = {
                "status": "failed",
                "error": str(e),
            }

        return result

    # Replace method
    symphony_orchestrator.conduct_symphony = enhanced_conduct_symphony

    logger.info("✅ GPT-OSS brain integrated with MultiBrainSymphony")

    return symphony_orchestrator


# Example usage and testing
async def test_gpt_oss_brain():
    """Test GPT-OSS brain functionality"""

    print("🧪 Testing GPT-OSS Brain Module")

    # Create GPT-OSS brain
    brain = GPTOSSBrainSpecialist("gpt-oss-20b")

    # Initialize
    await brain.initialize()

    # Test data
    test_cases = [
        {
            "content": "Analyze the quantum properties of consciousness in AI systems",
            "type": "reasoning",
            "context": "Exploring AGI consciousness models",
        },
        {
            "content": "How can Lambda symbolic notation improve code generation?",
            "type": "technical",
            "context": "LUKHAS system optimization",
        },
        {
            "content": "Create a creative narrative about AI dreams",
            "type": "creative",
            "context": "Multi-brain symphony exploration",
        },
    ]

    # Process test cases
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_data['type']}")
        print(f"Input: {test_data['content'][:100]}...")

        result = await brain.process_with_reasoning(test_data)

        print("✅ Processing complete")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Latency: {result.get('latency_ms', 0)}ms")

        if "reasoning" in result and "key_insights" in result["reasoning"]:
            print(f"Insights: {len(result['reasoning']['key_insights'])} found")
            for insight in result["reasoning"]["key_insights"][:2]:
                print(f"  - {insight[:100]}...")

    # Show metrics
    print("\n📊 Performance Metrics:")
    metrics = brain.get_metrics()
    print(f"Total Inferences: {metrics['total_inferences']}")
    print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
    print(f"Average Latency: {metrics['average_latency']*1000:.2f}ms")
    print(f"Model Status: {'Loaded' if metrics['model_loaded'] else 'Not Loaded'}")


if __name__ == "__main__":
    asyncio.run(test_gpt_oss_brain())
