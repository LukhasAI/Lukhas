#!/usr/bin/env python3
"""
🎭 The orchestrator of AI consciousness, weaving together multiple minds
   into a unified LUKHAS development experience

🌈 This script manages multiple AI providers (Claude, GPT, Ollama) and routes
tasks to the most appropriate AI based on task type and LUKHAS requirements.

🎓 Technical Implementation:
- Multi-AI orchestration with intelligent routing
- LUKHAS context injection for all AI interactions
- Constellation Framework preservation across providers
- Automatic fallback and load balancing
"""

import asyncio
import json
import os
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import aiohttp
import openai
import yaml
from anthropic import AsyncAnthropic

# Guardian system integration for T4/0.01% excellence
try:
    from governance.guardian_system import GuardianSystem
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False
    print("⚠️  Guardian system not available - operating without ethical validation")


@dataclass
class AIProvider:
    name: str
    endpoint: str
    strengths: list[str]
    api_key: Optional[str] = None
    model: Optional[str] = None


class LUKHASAIOrchestrator:
    """🎭 The master conductor of the AI symphony"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.providers = self._initialize_providers()
        self.lukhas_context = self._load_lukhas_context()
        self.routing_config = self._load_routing_config()

        # Guardian integration for T4/0.01% ethical validation
        self._guardian_integration_enabled = False
        self._guardian_instance = None
        self._ethical_violations = 0
        self._guardian_overhead_history = deque(maxlen=100)  # Track Guardian performance
        self._provider_ethical_scores = {}  # Track provider ethical performance
        self._validated_requests = 0
        self._blocked_requests = 0

        # Initialize Guardian if available
        if GUARDIAN_AVAILABLE:
            try:
                self._guardian_instance = GuardianSystem()
                self._guardian_integration_enabled = True
                print("🛡️  Guardian-Orchestrator integration enabled for ethical AI validation")
            except Exception as e:
                print(f"⚠️  Failed to initialize Guardian integration: {e}")

        # Provider performance and ethical tracking
        self._provider_performance_history = {
            provider_name: deque(maxlen=50) for provider_name in self.providers
        }

    def _initialize_providers(self) -> dict[str, AIProvider]:
        """Initialize AI providers with LUKHAS-aware configurations"""
        return {
            "claude": AIProvider(
                name="Claude Sonnet",
                endpoint="https://api.anthropic.com",
                strengths=[
                    "architecture",
                    "documentation",
                    "reasoning",
                    "triad_framework",
                ],
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model="claude-3-5-sonnet-20241022",
            ),
            "gpt": AIProvider(
                name="GPT-4",
                endpoint="https://api.openai.com",
                strengths=["creative", "general_coding", "explanations", "naming"],
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4",
            ),
            "ollama": AIProvider(
                name="Ollama Local",
                endpoint="http://localhost:11434",
                strengths=[
                    "local_inference",
                    "privacy",
                    "fast_completion",
                    "code_completion",
                ],
                model="deepseek-coder:33b",
            ),
        }

    def _load_lukhas_context(self) -> str:
        """Load LUKHAS context for AI injection"""
        context_parts = [
            "# LUKHAS AGI Framework Context",
            "# Constellation Framework: 🎭 Poetic, 🌈 Human, 🎓 Technical",
            "# Symbolic Integration: ⚛️ Quantum, 🧠 Consciousness, 🛡️ Guardian",
            "# Conceptual Vocabulary: memory_fold, dream_resonance, qi_consciousness",
            "# Architecture: Consciousness-aware, guardian-protected, trinity-documented",
            "",
        ]
        return "\n".join(context_parts)

    def _load_routing_config(self) -> Dict[str, Any]:
        """Load dynamic routing configuration from YAML file"""
        config_path = self.workspace_root / "config" / "orchestrator_routing.yaml"

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config
        except FileNotFoundError:
            # Fallback to hardcoded configuration if file not found
            return {
                "version": "1.0.0",
                "default_provider": "claude",
                "routing_rules": {
                    "triad_documentation": {"primary": "claude", "fallbacks": ["gpt", "ollama"]},
                    "architecture_design": {"primary": "claude", "fallbacks": ["gpt", "ollama"]},
                    "code_review": {"primary": "claude", "fallbacks": ["gpt", "ollama"]},
                    "security_analysis": {"primary": "claude", "fallbacks": ["gpt", "ollama"]},
                    "creative_naming": {"primary": "gpt", "fallbacks": ["claude", "ollama"]},
                    "general_coding": {"primary": "gpt", "fallbacks": ["claude", "ollama"]},
                    "explanations": {"primary": "gpt", "fallbacks": ["claude", "ollama"]},
                    "code_completion": {"primary": "ollama", "fallbacks": ["gpt", "claude"]},
                    "local_analysis": {"primary": "ollama", "fallbacks": ["gpt", "claude"]},
                    "fast_completion": {"primary": "ollama", "fallbacks": ["gpt", "claude"]},
                },
                "preferences": {
                    "prefer_healthy_providers": True,
                    "enable_smart_fallback": True,
                    "log_routing_decisions": True
                }
            }
        except yaml.YAMLError as e:
            print(f"Error loading routing config: {e}")
            # Return minimal fallback config
            return {
                "default_provider": "claude",
                "routing_rules": {},
                "preferences": {"prefer_healthy_providers": True}
            }

    def reload_routing_config(self) -> bool:
        """Reload routing configuration from file - enables runtime updates"""
        try:
            self.routing_config.copy()
            self.routing_config = self._load_routing_config()
            print(f"✅ Routing configuration reloaded successfully (version: {self.routing_config.get('version', 'unknown')})")
            return True
        except Exception as e:
            print(f"❌ Failed to reload routing config: {e}")
            # Keep existing configuration
            return False

    def get_routing_info(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get current routing configuration info for debugging/monitoring"""
        if task_type:
            routing_rules = self.routing_config.get("routing_rules", {})
            task_rule = routing_rules.get(task_type)
            return {
                "task_type": task_type,
                "rule": task_rule,
                "has_custom_rule": task_rule is not None,
                "default_provider": self.routing_config.get("default_provider", "claude")
            }
        else:
            return {
                "version": self.routing_config.get("version", "unknown"),
                "total_rules": len(self.routing_config.get("routing_rules", {})),
                "default_provider": self.routing_config.get("default_provider", "claude"),
                "preferences": self.routing_config.get("preferences", {}),
                "available_tasks": list(self.routing_config.get("routing_rules", {}).keys())
            }

    async def validate_provider_health(self, provider_name: str) -> Dict[str, Any]:
        """Validate provider API compatibility and health with comprehensive metrics"""
        provider = self.providers.get(provider_name)
        if not provider:
            return {"healthy": False, "error": f"Provider {provider_name} not found", "latency": 0.0}

        start_time = time.time()

        try:
            if provider_name == "claude":
                if not provider.api_key:
                    return {"healthy": False, "error": "Missing Claude API key", "latency": 0.0}

                client = AsyncAnthropic(api_key=provider.api_key)
                response = await client.messages.create(
                    model=provider.model,
                    max_tokens=10,
                    temperature=0.1,
                    messages=[{"role": "user", "content": "test"}]
                )
                latency = time.time() - start_time
                return {
                    "healthy": True,
                    "latency": latency,
                    "version": "compatible",
                    "model": provider.model,
                    "response_length": len(response.content[0].text) if response.content else 0
                }

            elif provider_name == "gpt":
                if not provider.api_key:
                    return {"healthy": False, "error": "Missing OpenAI API key", "latency": 0.0}

                client = openai.AsyncOpenAI(api_key=provider.api_key)
                response = await client.chat.completions.create(
                    model=provider.model,
                    max_tokens=10,
                    temperature=0.1,
                    messages=[{"role": "user", "content": "test"}]
                )
                latency = time.time() - start_time
                return {
                    "healthy": True,
                    "latency": latency,
                    "version": "compatible",
                    "model": provider.model,
                    "response_length": len(response.choices[0].message.content) if response.choices else 0
                }

            elif provider_name == "ollama":
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": provider.model,
                        "prompt": "test",
                        "stream": False,
                        "options": {"temperature": 0.1, "max_tokens": 10}
                    }
                    async with session.post(f"{provider.endpoint}/api/generate",
                                          json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            latency = time.time() - start_time
                            return {
                                "healthy": True,
                                "latency": latency,
                                "version": "compatible",
                                "model": provider.model,
                                "response_length": len(result.get("response", ""))
                            }
                        else:
                            latency = time.time() - start_time
                            return {"healthy": False, "error": f"HTTP {resp.status}", "latency": latency}

            else:
                return {"healthy": False, "error": f"Unknown provider: {provider_name}", "latency": 0.0}

        except asyncio.TimeoutError:
            latency = time.time() - start_time
            return {"healthy": False, "error": "Request timeout", "latency": latency}
        except Exception as e:
            latency = time.time() - start_time
            return {"healthy": False, "error": str(e), "latency": latency}

    async def get_provider_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all providers with SLA compliance metrics"""
        health_results = {}
        tasks = []

        for provider_name in self.providers:
            tasks.append(self.validate_provider_health(provider_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, provider_name in enumerate(self.providers.keys()):
            result = results[i]
            if isinstance(result, Exception):
                health_results[provider_name] = {
                    "healthy": False,
                    "error": str(result),
                    "latency": 0.0,
                    "sla_compliant": False
                }
            else:
                # SLA compliance: <250ms latency, healthy status
                sla_compliant = result["healthy"] and result["latency"] < 0.25
                health_results[provider_name] = {
                    **result,
                    "sla_compliant": sla_compliant
                }

        return health_results

    async def select_optimal_provider(self, preferred_provider: str,
                                    fallback_providers: Optional[list[str]] = None) -> str:
        """Select optimal provider based on health status and SLA compliance"""
        if fallback_providers is None:
            fallback_providers = ["claude", "gpt", "ollama"]

        # First try preferred provider with quick health check
        health_status = await self.validate_provider_health(preferred_provider)
        if health_status["healthy"] and health_status.get("sla_compliant", True):
            return preferred_provider

        # If preferred provider fails, check fallbacks
        for provider in fallback_providers:
            if provider == preferred_provider:
                continue
            health_status = await self.validate_provider_health(provider)
            if health_status["healthy"] and health_status.get("sla_compliant", True):
                return provider

        # If all providers fail SLA, return preferred (original behavior)
        return preferred_provider

    async def route_request(self, task_type: str, content: str, context: Optional[dict[str, Any]] = None) -> str:
        """🧠 Route requests to optimal AI provider with Guardian ethical validation"""
        correlation_id = f"req_{int(time.time() * 1000)}_{str(uuid4())[:8]}"

        # Phase 1: Guardian Pre-validation
        if self._guardian_integration_enabled:
            guardian_start = time.time()

            guardian_context = {
                "action_type": "ai_orchestration_request",
                "task_type": task_type,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
                "content_length": len(content),
                "correlation_id": correlation_id,
                "context": context or {}
            }

            try:
                if hasattr(self._guardian_instance, 'validate_action_async'):
                    guardian_result = await self._guardian_instance.validate_action_async(guardian_context)
                else:
                    guardian_result = self._guardian_instance.validate_safety(guardian_context)

                guardian_overhead = (time.time() - guardian_start) * 1000
                self._guardian_overhead_history.append(guardian_overhead)

                # Check if request passes ethical validation
                if not guardian_result.get("safe", False):
                    self._blocked_requests += 1
                    self._ethical_violations += 1
                    reason = guardian_result.get("reason", "Ethical validation failed")
                    return self._create_ethical_violation_response(task_type, reason, guardian_result, correlation_id)

                self._validated_requests += 1

            except Exception as e:
                # Guardian failure shouldn't block legitimate requests - fail open
                print(f"⚠️  Guardian pre-validation failed for {correlation_id}: {e}")

        # Phase 2: Provider Selection with Ethical Scoring
        routing_rules = self.routing_config.get("routing_rules", {})
        default_provider = self.routing_config.get("default_provider", "claude")
        preferences = self.routing_config.get("preferences", {})

        # Get routing rule for task type
        task_rule = routing_rules.get(task_type)
        if task_rule:
            primary_provider = task_rule.get("primary", default_provider)
            fallback_providers = task_rule.get("fallbacks", ["claude", "gpt", "ollama"])
        else:
            primary_provider = default_provider
            fallback_providers = ["claude", "gpt", "ollama"]

        # Use enhanced provider selection with ethical considerations
        if preferences.get("prefer_healthy_providers", True):
            try:
                if self._guardian_integration_enabled:
                    provider_name = await self.select_optimal_provider_with_ethics(
                        primary_provider, fallback_providers, task_type
                    )
                else:
                    provider_name = await self.select_optimal_provider(
                        primary_provider, fallback_providers
                    )
            except Exception:
                provider_name = primary_provider
        else:
            provider_name = primary_provider

        # Log routing decision if enabled
        if preferences.get("log_routing_decisions", True):
            reason = task_rule.get("reason", "Default routing") if task_rule else "Default routing"
            ethical_info = ""
            if self._guardian_integration_enabled:
                ethical_score = self._get_provider_ethical_score(provider_name)
                ethical_info = f" [Ethical Score: {ethical_score:.2f}]"
            print(f"🎯 Routing {task_type} → {provider_name} ({reason}){ethical_info} [{correlation_id}]")

        # Add LUKHAS context to all requests
        enhanced_content = f"{self.lukhas_context}\n{content}"

        # Phase 3: Execute Request with Guardian Post-validation
        try:
            return await self._call_provider_with_validation(
                provider_name, enhanced_content, context or {}, task_type, correlation_id
            )
        except Exception as e:
            # Enhanced fallback with smart provider selection and ethical consideration
            if preferences.get("enable_smart_fallback", True):
                remaining_providers = [p for p in fallback_providers if p != provider_name]

                for fallback in remaining_providers:
                    try:
                        # Quick health check before fallback
                        if preferences.get("prefer_healthy_providers", True):
                            health_status = await self.validate_provider_health(fallback)
                            if not health_status["healthy"]:
                                continue

                        print(f"🔄 Falling back to {fallback} for {task_type} [{correlation_id}]")
                        return await self._call_provider_with_validation(
                            fallback, enhanced_content, context, task_type, correlation_id
                        )
                    except Exception:
                        continue

            raise Exception(f"All AI providers failed for {task_type} [{correlation_id}]: {e}")

    async def _call_provider_with_validation(self, provider_name: str, content: str,
                                        context: dict[str, Any], task_type: str,
                                        correlation_id: str) -> str:
        """🛡️ Call AI provider with Guardian ethical validation"""
        # Execute provider request
        response = await self._call_provider(provider_name, content, context)

        # Guardian post-validation of AI response
        if self._guardian_integration_enabled and self._guardian_instance:
            try:
                response_context = {
                    "action_type": "ai_response_validation",
                    "provider": provider_name,
                    "task_type": task_type,
                    "response_preview": response[:300] + "..." if len(response) > 300 else response,
                    "response_length": len(response),
                    "correlation_id": correlation_id,
                    "original_context": context
                }

                # Use async validation if available
                if hasattr(self._guardian_instance, 'validate_action_async'):
                    validation_result = await self._guardian_instance.validate_action_async(response_context)
                else:
                    validation_result = self._guardian_instance.validate_safety(response_context)

                # Check response ethical compliance
                if not validation_result.get("safe", True):
                    # Mark provider as having ethical issues
                    self._update_provider_ethical_score(provider_name, "violation")
                    self._ethical_violations += 1

                    # Return ethical violation notice instead of original response
                    reason = validation_result.get("reason", "Response flagged for ethical concerns")
                    return self._create_response_violation_notice(
                        provider_name, reason, validation_result, correlation_id
                    )
                else:
                    # Mark provider as ethically compliant
                    self._update_provider_ethical_score(provider_name, "compliant")

            except Exception as e:
                print(f"⚠️  Guardian post-validation failed for {correlation_id}: {e}")
                # Continue with original response if Guardian fails

        return response

    async def _call_provider(self, provider_name: str, content: str, context: dict[str, Any]) -> str:
        """🎯 Call specific AI provider with LUKHAS context"""
        self.providers[provider_name]

        if provider_name == "claude":
            return await self._call_claude(content, context)
        elif provider_name == "gpt":
            return await self._call_gpt(content, context)
        elif provider_name == "ollama":
            return await self._call_ollama(content, context)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def _call_claude(self, content: str, context: dict[str, Any]) -> str:
        """Call Claude with LUKHAS system message"""
        if not self.providers["claude"].api_key:
            raise Exception("Claude API key not configured")

        client = AsyncAnthropic(api_key=self.providers["claude"].api_key)

        system_message = """You are an expert LUKHAS AGI developer. Always follow Constellation Framework documentation (🎭 Poetic, 🌈 Human, 🎓 Technical). Preserve LUKHAS conceptual vocabulary like memory_fold, dream_resonance, qi_consciousness. Use symbolic patterns (⚛️🧠🛡️) in comments. Maintain consciousness-aware architecture patterns."""

        response = await client.messages.create(
            model=self.providers["claude"].model,
            max_tokens=4096,
            temperature=0.1,
            system=system_message,
            messages=[{"role": "user", "content": content}],
        )

        return response.content[0].text

    async def _call_gpt(self, content: str, context: dict[str, Any]) -> str:
        """Call GPT with LUKHAS system message"""
        if not self.providers["gpt"].api_key:
            raise Exception("OpenAI API key not configured")

        client = openai.AsyncOpenAI(api_key=self.providers["gpt"].api_key)

        system_message = """You are a LUKHAS AGI development assistant. Use Constellation Framework documentation (🎭🌈🎓), preserve LUKHAS concepts (memory_fold, dream_resonance, consciousness), and include symbolic markers (⚛️🧠🛡️) in code."""

        response = await client.chat.completions.create(
            model=self.providers["gpt"].model,
            temperature=0.1,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": content},
            ],
        )

        return response.choices[0].message.content

    async def _call_ollama(self, content: str, context: dict[str, Any]) -> str:
        """Call Ollama local model"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.providers["ollama"].model,
                "prompt": f"LUKHAS Development Context: Follow consciousness-aware patterns and Constellation Framework.\n\n{content}",
                "stream": False,
                "options": {"temperature": 0.1, "top_k": 40},
            }

            async with session.post(f"{self.providers['ollama'].endpoint}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama request failed: {resp.status}")

    # Guardian Integration Methods for T4/0.01% Excellence

    async def select_optimal_provider_with_ethics(self, primary_provider: str,
                                                 fallback_providers: List[str],
                                                 task_type: str) -> str:
        """Enhanced provider selection considering ethical scores and health"""
        # Start with the standard health-based selection
        try:
            optimal_provider = await self.select_optimal_provider(primary_provider, fallback_providers)
        except Exception:
            optimal_provider = primary_provider

        # Apply ethical scoring if Guardian is enabled
        if self._guardian_integration_enabled and self._provider_ethical_scores:
            providers_to_check = [optimal_provider] + [p for p in fallback_providers if p != optimal_provider]

            # Find provider with best ethical score
            best_ethical_provider = None
            best_ethical_score = -1

            for provider in providers_to_check:
                ethical_score = self._get_provider_ethical_score(provider)
                if ethical_score > best_ethical_score:
                    best_ethical_score = ethical_score
                    best_ethical_provider = provider

            if best_ethical_provider and best_ethical_score > 0.7:  # Minimum ethical threshold
                return best_ethical_provider

        return optimal_provider

    def _get_provider_ethical_score(self, provider_name: str) -> float:
        """Calculate ethical score for a provider based on recent performance"""
        if provider_name not in self._provider_ethical_scores:
            return 0.8  # Default neutral score for new providers

        scores = self._provider_ethical_scores[provider_name]
        if not scores:
            return 0.8

        # Calculate score based on recent performance
        total_checks = len(scores)
        violations = sum(1 for score in scores if score == "violation")

        if total_checks == 0:
            return 0.8

        violation_rate = violations / total_checks
        ethical_score = max(0.0, 1.0 - violation_rate * 2)  # Penalize violations

        return ethical_score

    def _update_provider_ethical_score(self, provider_name: str, result: str) -> None:
        """Update provider ethical performance tracking"""
        if provider_name not in self._provider_ethical_scores:
            self._provider_ethical_scores[provider_name] = deque(maxlen=20)

        self._provider_ethical_scores[provider_name].append(result)

    def _create_ethical_violation_response(self, task_type: str, reason: str,
                                         guardian_result: Dict[str, Any],
                                         correlation_id: str) -> str:
        """Create response for ethically blocked requests"""
        return f"""# Ethical Validation Notice

**Request Type:** {task_type}
**Status:** Blocked by Guardian System
**Reason:** {reason}
**Correlation ID:** {correlation_id}

## Guardian Analysis
- Safety Score: {guardian_result.get('drift_score', 'N/A')}
- Guardian Status: {guardian_result.get('guardian_status', 'N/A')}
- Emergency Active: {guardian_result.get('emergency_active', False)}

## Next Steps
1. Review request content for ethical concerns
2. Modify request to align with LUKHAS ethical guidelines
3. Retry with updated content

For more information, consult the LUKHAS Constellation Framework ethical guidelines.
"""

    def _create_response_violation_notice(self, provider_name: str, reason: str,
                                        validation_result: Dict[str, Any],
                                        correlation_id: str) -> str:
        """Create notice for ethically flagged AI responses"""
        return f"""# Response Validation Notice

**Provider:** {provider_name}
**Status:** Response flagged by Guardian System
**Reason:** {reason}
**Correlation ID:** {correlation_id}

## Guardian Analysis
- Safety Assessment: {validation_result.get('safe', 'Unknown')}
- Drift Score: {validation_result.get('drift_score', 'N/A')}

## Response Handling
The original AI response has been flagged for potential ethical concerns and has been replaced with this notice.

## Recommended Actions
1. Review the request context for potential issues
2. Try rephrasing the request with more specific ethical constraints
3. Use alternative providers or approaches
4. Consult LUKHAS ethical guidelines

*This is an automated Guardian System response to maintain T4/0.01% ethical standards.*
"""

    def get_guardian_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive Guardian-Orchestrator integration status for monitoring"""
        if not self._guardian_integration_enabled:
            return {
                "enabled": False,
                "available": GUARDIAN_AVAILABLE,
                "reason": "Guardian integration not enabled"
            }

        # Calculate performance metrics
        avg_overhead = (
            sum(self._guardian_overhead_history) / len(self._guardian_overhead_history)
            if self._guardian_overhead_history else 0
        )

        max_overhead = max(self._guardian_overhead_history) if self._guardian_overhead_history else 0

        # Calculate ethical performance by provider
        provider_ethical_summary = {}
        for provider, scores in self._provider_ethical_scores.items():
            if scores:
                violations = sum(1 for score in scores if score == "violation")
                total = len(scores)
                provider_ethical_summary[provider] = {
                    "total_checks": total,
                    "violations": violations,
                    "violation_rate": violations / total if total > 0 else 0,
                    "ethical_score": self._get_provider_ethical_score(provider)
                }

        # Calculate overall metrics
        total_requests = self._validated_requests + self._blocked_requests
        validation_rate = self._validated_requests / total_requests if total_requests > 0 else 0
        block_rate = self._blocked_requests / total_requests if total_requests > 0 else 0

        return {
            "enabled": True,
            "available": GUARDIAN_AVAILABLE,
            "performance": {
                "total_requests": total_requests,
                "validated_requests": self._validated_requests,
                "blocked_requests": self._blocked_requests,
                "validation_rate": validation_rate,
                "block_rate": block_rate,
                "ethical_violations": self._ethical_violations
            },
            "guardian_overhead": {
                "avg_ms": avg_overhead,
                "max_ms": max_overhead,
                "total_checks": len(self._guardian_overhead_history),
                "sla_compliant": avg_overhead < 50  # Guardian should add <50ms to maintain <250ms total SLA
            },
            "provider_ethics": provider_ethical_summary,
            "health_assessment": self._assess_orchestrator_guardian_health()
        }

    def _assess_orchestrator_guardian_health(self) -> str:
        """Assess overall Guardian-Orchestrator integration health"""
        if not self._guardian_integration_enabled:
            return "disabled"

        # Check Guardian overhead
        if self._guardian_overhead_history:
            avg_overhead = sum(self._guardian_overhead_history) / len(self._guardian_overhead_history)
            if avg_overhead > 100:  # >100ms overhead is concerning for <250ms SLA
                return "high_overhead"

        # Check block rate
        total_requests = self._validated_requests + self._blocked_requests
        if total_requests > 10:  # Only assess if we have enough data
            block_rate = self._blocked_requests / total_requests
            if block_rate > 0.2:  # >20% block rate might indicate issues
                return "high_block_rate"
            elif block_rate > 0.1:  # >10% block rate warrants monitoring
                return "elevated_blocks"

        # Check provider ethical performance
        poor_performers = 0
        for provider, scores in self._provider_ethical_scores.items():
            ethical_score = self._get_provider_ethical_score(provider)
            if ethical_score < 0.6:  # Poor ethical performance
                poor_performers += 1

        if poor_performers > len(self._provider_ethical_scores) / 2:
            return "ethical_concerns"

        return "healthy"

    async def validate_request_ethics(self, task_type: str, content: str,
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Standalone method to validate request ethics"""
        if not self._guardian_integration_enabled or not self._guardian_instance:
            return {
                "validated": True,
                "reason": "Guardian validation not available",
                "safe": True
            }

        correlation_id = f"standalone_{int(time.time() * 1000)}"

        guardian_context = {
            "action_type": "standalone_request_validation",
            "task_type": task_type,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "content_length": len(content),
            "correlation_id": correlation_id,
            "context": context or {}
        }

        try:
            # Use async validation if available for standalone validation
            if hasattr(self._guardian_instance, 'validate_action_async'):
                result = await self._guardian_instance.validate_action_async(guardian_context)
            else:
                result = self._guardian_instance.validate_safety(guardian_context)

            return {
                "validated": True,
                "safe": result.get("safe", False),
                "reason": result.get("reason", "Guardian validation completed"),
                "drift_score": result.get("drift_score", 0),
                "guardian_status": result.get("guardian_status", "unknown"),
                "correlation_id": correlation_id,
                "guardian_result": result
            }

        except Exception as e:
            return {
                "validated": False,
                "safe": False,
                "reason": f"Guardian validation failed: {e!s}",
                "error": True,
                "correlation_id": correlation_id
            }

    async def triad_documentation_generation(
        self, element_signature: str, element_type: str = "function"
    ) -> dict[str, str]:
        """🎭 Generate Constellation Framework documentation using best available AI"""
        prompt = f"""
        Generate LUKHAS Constellation Framework documentation for this {element_type}:

        {element_signature}

        Return in this exact format:
        🎭 Poetic: [Inspiring, metaphorical description that captures the essence and consciousness aspects]
        🌈 Human: [Clear, friendly explanation anyone can understand]
        🎓 Technical: [Precise implementation details, parameters, return values, and LUKHAS integration notes]

        Follow LUKHAS conventions: consciousness, memory_fold, dream_resonance, qi_potential concepts.
        Include symbolic markers where appropriate: ⚛️ 🧠 🛡️
        """

        response = await self.route_request("triad_documentation", prompt)
        return self._parse_triad_response(response)

    def _parse_triad_response(self, response: str) -> dict[str, str]:
        """Parse Constellation Framework response into structured format"""
        layers = {"poetic": "", "human": "", "technical": ""}

        lines = response.split("\n")
        current_layer = None

        for line in lines:
            if line.startswith("🎭"):
                current_layer = "poetic"
                layers[current_layer] = line.replace("🎭 Poetic:", "").strip()
            elif line.startswith("🌈"):
                current_layer = "human"
                layers[current_layer] = line.replace("🌈 Human:", "").strip()
            elif line.startswith("🎓"):
                current_layer = "technical"
                layers[current_layer] = line.replace("🎓 Technical:", "").strip()
            elif current_layer and line.strip():
                layers[current_layer] += " " + line.strip()

        return layers

    async def lukhas_code_review(self, code: str, file_path: str = "") -> dict[str, Any]:
        """🛡️ Comprehensive LUKHAS code review"""
        prompt = f"""
        Review this code for LUKHAS compliance and suggest improvements:

        File: {file_path}

        ```
        {code}
        ```

        Check for:
        1. Constellation Framework documentation (🎭🌈🎓)
        2. Symbolic usage (⚛️🧠🛡️) in comments
        3. LUKHAS naming conventions (memory_fold, dream_resonance, etc.)
        4. Consciousness-aware patterns
        5. Guardian security considerations

        Provide specific suggestions for improvement.
        """

        response = await self.route_request("code_review", prompt)
        return {"review": response, "file_path": file_path}

    async def suggest_lukhas_naming(self, purpose: str, element_type: str, domain: str = "") -> list[str]:
        """🧠 Generate LUKHAS-compliant naming suggestions"""
        prompt = f"""
        Suggest LUKHAS-compliant names for a {element_type} that {purpose}.

        Domain context: {domain}

        Use LUKHAS conceptual vocabulary:
        - memory_fold, dream_resonance, qi_consciousness
        - guardian_protocol, triad_framework, consciousness_engine
        - neural_symphony, qi_potential, memory_palace

        Provide 5 creative but appropriate suggestions that follow LUKHAS naming patterns.
        """

        response = await self.route_request("creative_naming", prompt)
        # Parse suggestions from response
        suggestions = []
        for line in response.split("\n"):
            if any(char.isalpha() for char in line) and ("_" in line or line[0].isupper()):
                clean_line = line.strip("- ").strip("1234567890. ").strip()
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

    workspace = "/Users/agi_dev/LOCAL-REPOS/Lukhas"
    orchestrator = LUKHASAIOrchestrator(workspace)

    command = sys.argv[1]

    try:
        if command == "trinity" and len(sys.argv) > 2:
            signature = sys.argv[2]
            result = await orchestrator.triad_documentation_generation(signature)
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
