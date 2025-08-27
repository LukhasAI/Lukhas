#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Multi-AI Router (Fixed Version)
Intelligent routing between multiple AI services with complete service definitions
"""

import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger("ABotAIRouter")

class TaskType(Enum):
    """Types of tasks that can be routed to different AI services"""
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    DOCUMENTATION = "documentation"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    REASONING = "reasoning"
    CHAT = "chat"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    MATH = "math"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    PLANNING = "planning"
    SECURITY_AUDIT = "security_audit"
    ENTERPRISE_ANALYSIS = "enterprise_analysis"

@dataclass
class AIServiceCapability:
    """Capabilities and characteristics of each AI service"""
    name: str
    model: str
    keychain_service: str
    strengths: list[TaskType]
    cost_per_1k_tokens: float
    max_tokens: int
    supports_streaming: bool
    response_time: str  # "fast", "medium", "slow"
    reasoning_quality: str  # "excellent", "good", "fair"
    code_quality: str  # "excellent", "good", "fair"
    creative_quality: str  # "excellent", "good", "fair"
    factual_accuracy: str  # "excellent", "good", "fair"
    max_context_length: int
    best_for: list[str]
    quality_score: int  # 1-10

class ABotIntelligentAIRouter:
    """
    LUKHAS AI ΛBot's Intelligent Multi-AI Router'
    Automatically routes tasks to the best AI service based on task type, cost, and quality requirements
    """

    def __init__(self):
        self.routing_analytics = {"total_requests": 0, "service_usage": {}}
        self.services = {
            "gpt-4o": AIServiceCapability(
                name="OpenAI GPT-4o",
                model="gpt-4o",
                keychain_service="LUKHAS AI ΛBot-OpenAI-API",
                strengths=[TaskType.CODE_REVIEW, TaskType.REASONING, TaskType.ANALYSIS, TaskType.PLANNING],
                cost_per_1k_tokens=0.005,
                max_tokens=4096,
                supports_streaming=True,
                response_time="fast",
                reasoning_quality="excellent",
                code_quality="excellent",
                creative_quality="good",
                factual_accuracy="excellent",
                max_context_length=128000,
                best_for=["code_review", "reasoning", "analysis"],
                quality_score=9
            ),
            "gpt-3.5-turbo": AIServiceCapability(
                name="OpenAI GPT-3.5 Turbo",
                model="gpt-3.5-turbo",
                keychain_service="LUKHAS AI ΛBot-OpenAI-API",
                strengths=[TaskType.CHAT, TaskType.SUMMARIZATION, TaskType.DOCUMENTATION],
                cost_per_1k_tokens=0.0015,
                max_tokens=4096,
                supports_streaming=True,
                response_time="fast",
                reasoning_quality="good",
                code_quality="good",
                creative_quality="good",
                factual_accuracy="good",
                max_context_length=16385,
                best_for=["chat", "summarization", "quick_tasks"],
                quality_score=7
            ),
            "claude-3-opus": AIServiceCapability(
                name="Anthropic Claude 3 Opus",
                model="claude-3-opus-20240229",
                keychain_service="LUKHAS AI ΛBot-Anthropic-API",
                strengths=[TaskType.CREATIVE_WRITING, TaskType.ANALYSIS, TaskType.REASONING, TaskType.CODE_GENERATION],
                cost_per_1k_tokens=0.015,
                max_tokens=4096,
                supports_streaming=True,
                response_time="medium",
                reasoning_quality="excellent",
                code_quality="excellent",
                creative_quality="excellent",
                factual_accuracy="excellent",
                max_context_length=200000,
                best_for=["creative_writing", "complex_analysis", "reasoning"],
                quality_score=10
            ),
            "claude-3-sonnet": AIServiceCapability(
                name="Anthropic Claude 3 Sonnet",
                model="claude-3-sonnet-20240229",
                keychain_service="LUKHAS AI ΛBot-Anthropic-API",
                strengths=[TaskType.CODE_REVIEW, TaskType.DOCUMENTATION, TaskType.ANALYSIS],
                cost_per_1k_tokens=0.003,
                max_tokens=4096,
                supports_streaming=True,
                response_time="fast",
                reasoning_quality="excellent",
                code_quality="excellent",
                creative_quality="good",
                factual_accuracy="excellent",
                max_context_length=200000,
                best_for=["code_review", "documentation", "balanced_tasks"],
                quality_score=9
            ),
            "gemini-pro": AIServiceCapability(
                name="Google Gemini Pro",
                model="gemini-pro",
                keychain_service="lukhas-ai-gemini",
                strengths=[TaskType.RESEARCH, TaskType.MATH, TaskType.TRANSLATION, TaskType.ANALYSIS],
                cost_per_1k_tokens=0.0003,  # Ultra cost-effective
                max_tokens=8192,
                supports_streaming=True,
                response_time="fast",
                reasoning_quality="good",
                code_quality="good",
                creative_quality="fair",
                factual_accuracy="excellent",
                max_context_length=32768,
                best_for=["research", "math", "cost_effective_tasks"],
                quality_score=8
            ),
            "azure-gpt-4": AIServiceCapability(
                name="Azure OpenAI GPT-4",
                model="gpt-4",
                keychain_service="lukhas-ai-azure-api-key",
                strengths=[TaskType.ENTERPRISE_ANALYSIS, TaskType.SECURITY_AUDIT, TaskType.REASONING],
                cost_per_1k_tokens=0.03,  # Premium enterprise pricing
                max_tokens=4096,
                supports_streaming=True,
                response_time="medium",
                reasoning_quality="excellent",
                code_quality="excellent",
                creative_quality="good",
                factual_accuracy="excellent",
                max_context_length=8192,
                best_for=["enterprise_analysis", "security_audit", "compliance"],
                quality_score=9
            ),
            "perplexity-ai": AIServiceCapability(
                name="Perplexity AI",
                model="llama-3.1-sonar-large-128k-online",
                keychain_service="LUKHAS AI ΛBot-Perplexity-API",
                strengths=[TaskType.RESEARCH, TaskType.ANALYSIS, TaskType.SUMMARIZATION],
                cost_per_1k_tokens=0.001,
                max_tokens=4096,
                supports_streaming=True,
                response_time="fast",
                reasoning_quality="good",
                code_quality="fair",
                creative_quality="fair",
                factual_accuracy="excellent",
                max_context_length=128000,
                best_for=["research", "fact_checking", "current_events"],
                quality_score=8
            )
        }

        logger.info(f"🤖 LUKHAS AI ΛBot Intelligent AI Router initialized with {len(self.services)} services")

    def _get_keychain_value(self, service: str) -> Optional[str]:
        """Get API key from Mac KeyChain"""
        try:
            result = subprocess.run([
                "security", "find-generic-password",
                "-s", service,
                "-w"
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            logger.warning(f"KeyChain access failed for {service}: {e}")
            return None

    def route_task(self, task_type: TaskType, prompt: str, priority: str = "balanced") -> dict:
        """
        Intelligently route a task to the best AI service

        Args:
            task_type: Type of task to perfrom prompt: The actual prompt/task content
            priority: "cost", "quality", "speed", or "balanced"

        Returns:
            Dict with service selection, reasoning, and estimated cost
        """

        # Filter services that are good at this task type
        suitable_services = []
        for service_id, service in self.services.items():
            if task_type in service.strengths:
                api_key = self._get_keychain_value(service.keychain_service)
                if api_key and len(api_key.strip()) > 10:
                    suitable_services.append((service_id, service))

        if not suitable_services:
            # Fallback to any available service
            for service_id, service in self.services.items():
                api_key = self._get_keychain_value(service.keychain_service)
                if api_key and len(api_key.strip()) > 10:
                    suitable_services.append((service_id, service))

        if not suitable_services:
            return {
                "service": "none",
                "reason": "No AI services available",
                "estimated_cost": 0.0,
                "error": "No API keys found in KeyChain"
            }

        # Apply priority-based selection
        if priority == "cost":
            # Choose cheapest
            best_service_id, best_service = min(suitable_services, key=lambda x: x[1].cost_per_1k_tokens)
            reason = f"Cost-effective choice: ${best_service.cost_per_1k_tokens:.4f}/1K tokens"
        elif priority == "quality":
            # Choose highest quality
            best_service_id, best_service = max(suitable_services, key=lambda x: x[1].quality_score)
            reason = f"Highest quality choice: Score {best_service.quality_score}/10"
        elif priority == "speed":
            # Choose fastest
            speed_ranking = {"fast": 3, "medium": 2, "slow": 1}
            best_service_id, best_service = max(suitable_services,
                                               key=lambda x: speed_ranking.get(x[1].response_time, 1))
            reason = f"Fastest response: {best_service.response_time}"
        else:  # balanced
            # Balanced scoring algorithm
            def calculate_balance_score(service):
                cost_score = 1.0 / (service.cost_per_1k_tokens * 1000 + 0.1)  # Lower cost = higher score
                quality_score = service.quality_score / 10.0
                speed_score = {"fast": 1.0, "medium": 0.7, "slow": 0.4}.get(service.response_time, 0.5)
                return (cost_score * 0.4) + (quality_score * 0.4) + (speed_score * 0.2)

            best_service_id, best_service = max(suitable_services,
                                               key=lambda x: calculate_balance_score(x[1]))
            reason = "Balanced cost/quality/speed optimization"

        # Estimate cost (rough calculation based on prompt length)
        estimated_tokens = len(prompt) // 4 + 150  # Rough estimate: 4 chars per token + response
        estimated_cost = (estimated_tokens / 1000) * best_service.cost_per_1k_tokens

        # Record analytics
        self.routing_analytics["total_requests"] += 1
        if best_service_id not in self.routing_analytics["service_usage"]:
            self.routing_analytics["service_usage"][best_service_id] = 0
        self.routing_analytics["service_usage"][best_service_id] += 1

        return {
            "service": best_service.name,
            "service_id": best_service_id,
            "model": best_service.model,
            "keychain_service": best_service.keychain_service,
            "estimated_cost": estimated_cost,
            "reason": f"Selected {best_service.name}: Strong at {task_type.value}, {reason}",
            "task_type": task_type.value,
            "priority": priority,
            "quality_score": best_service.quality_score,
            "cost_per_1k": best_service.cost_per_1k_tokens
        }

    def get_routing_analytics(self) -> dict:
        """Get routing analytics and usage statistics"""
        return self.routing_analytics.copy()

    def get_available_services(self) -> list[str]:
        """Get list of currently available AI services"""
        available = []
        for _service_id, service in self.services.items():
            api_key = self._get_keychain_value(service.keychain_service)
            if api_key and len(api_key.strip()) > 10:
                available.append(service.name)
        return available

def get_ai_router_status() -> dict:
    """Get comprehensive AI router status for reporting"""
    router = ABotIntelligentAIRouter()

    # Test all services
    services_status = {}
    for service_name, service_info in router.services.items():
        try:
            # Quick availability test (without making actual API calls)
            api_key = router._get_keychain_value(service_info.keychain_service)
            services_status[service_name] = {
                "available": api_key is not None and api_key != "your-api-key-here" and len(api_key.strip()) > 10,
                "cost_per_1k": service_info.cost_per_1k_tokens,
                "primary_use_cases": service_info.best_for,
                "keychain_service": service_info.keychain_service,
                "model": service_info.model,
                "quality_rating": service_info.quality_score
            }
        except Exception as e:
            services_status[service_name] = {
                "available": False,
                "error": str(e),
                "cost_per_1k": service_info.cost_per_1k_tokens,
                "primary_use_cases": service_info.best_for,
                "model": service_info.model
            }

    # Calculate statistics
    total_services = len(services_status)
    available_services = sum(1 for s in services_status.values() if s.get("available", False))

    # Get routing analytics from the global router
    try:
        analytics = router.get_routing_analytics()
    except:
        analytics = {"total_requests": 0, "service_usage": {}}

    # Find cheapest and most expensive available services
    available_service_costs = {k: v["cost_per_1k"] for k, v in services_status.items() if v.get("available", False)}

    cheapest_service = min(available_service_costs.keys(), key=lambda k: available_service_costs[k]) if available_service_costs else "none"
    most_expensive_service = max(available_service_costs.keys(), key=lambda k: available_service_costs[k]) if available_service_costs else "none"

    return {
        "timestamp": datetime.now().isoformat(),
        "services_overview": {
            "total_services": total_services,
            "available_services": available_services,
            "availability_percentage": (available_services / total_services) * 100 if total_services > 0 else 0,
            "cheapest_service": cheapest_service,
            "most_expensive_service": most_expensive_service
        },
        "services_detail": services_status,
        "routing_analytics": analytics,
        "cost_analysis": {
            "cheapest_cost": min(available_service_costs.values()) if available_service_costs else 0,
            "most_expensive_cost": max(available_service_costs.values()) if available_service_costs else 0,
            "average_cost": sum(available_service_costs.values()) / len(available_service_costs) if available_service_costs else 0
        },
        "recommendations": [
            f"✅ {available_services}/{total_services} AI services available",
            f"💰 Cost range: ${min(available_service_costs.values()):.4f} - ${max(available_service_costs.values()):.4f} per 1K tokens" if available_service_costs else "❌ No services available",
            "🚀 Use the AI router to automatically optimize costs and quality"
        ]
    }

# Global AI router instance for easy access
abot_ai_router = ABotIntelligentAIRouter()

if __name__ == "__main__":
    # Test the AI router
    router = ABotIntelligentAIRouter()

    print("🤖 LUKHAS AI ΛBot Intelligent AI Router")
    print("=" * 50)
    print(f"Available AI services: {len(router.services)}")

    # Show all services and their availability
    for _service_id, service in router.services.items():
        api_key = router._get_keychain_value(service.keychain_service)
        status = "✅" if (api_key and len(api_key.strip()) > 10) else "❌"
        print(f"{status} {service.name} (${service.cost_per_1k_tokens:.4f}/1K tokens)")

    print("\n🎯 Test Routing Decisions:")
    print()

    # Test routing for different tasks
    test_tasks = [
        (TaskType.CODE_REVIEW, "Review this Python function", "quality"),
        (TaskType.CREATIVE_WRITING, "Write a creative story", "quality"),
        (TaskType.CHAT, "Hello, how are you?", "cost"),
        (TaskType.RESEARCH, "What is quantum computing?", "balanced")
    ]

    for task_type, prompt, priority in test_tasks:
        best_service = router.route_task(task_type, prompt, priority)
        print(f"Task: {task_type.value} (Priority: {priority})")
        print(f"→ Routed to: {best_service['service']}")
        print(f"→ Reasoning: {best_service['reason']}")
        print(f"→ Est. Cost: ${best_service['estimated_cost']:.4f}")
        print()

    # Show analytics
    analytics = router.get_routing_analytics()
    print("📊 Routing Analytics:")
    print(f"Total requests: {analytics['total_requests']}")

    # Show status
    status = get_ai_router_status()
    print(f"🔍 Available Services: {status['services_overview']['available_services']}/{status['services_overview']['total_services']}")
    if status["services_overview"]["available_services"] > 0:
        print(f"💰 Cheapest: {status['services_overview']['cheapest_service']}")
        print(f"💎 Most Expensive: {status['services_overview']['most_expensive_service']}")
        print(f"📊 Cost range: ${status['cost_analysis']['cheapest_cost']:.4f} - ${status['cost_analysis']['most_expensive_cost']:.4f}")
