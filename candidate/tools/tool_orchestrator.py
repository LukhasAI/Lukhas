"""
Tool Execution Orchestrator for Multi-AI Integration
==================================================
Coordinates tool execution across multiple AI services with consensus mechanisms.
"""
import streamlit as st
from datetime import timezone

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Optional

from .tool_executor import ToolExecutor
from .tool_executor_guardian import get_tool_executor_guardian

# Multi-AI Bridge Integration
try:
    from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient
except ImportError:
    UnifiedOpenAIClient = None

try:
    from candidate.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
except ImportError:
    AnthropicWrapper = None

try:
    from candidate.bridge.llm_wrappers.gemini_wrapper import GeminiWrapper
except ImportError:
    GeminiWrapper = None

try:
    from candidate.bridge.llm_wrappers.perplexity_wrapper import PerplexityWrapper
except ImportError:
    PerplexityWrapper = None

logger = logging.getLogger("ΛTRACE.tools.orchestrator", timezone)


class MultiAIConsensus:
    """Multi-AI consensus mechanism for tool execution validation"""

    def __init__(self, ai_clients: dict[str, Any], consensus_threshold: float = 0.7):
        self.ai_clients = ai_clients
        self.consensus_threshold = consensus_threshold
        self.consensus_cache = {}

    async def get_consensus(self, tool_name: str, arguments: dict[str, Any], execution_result: str) -> dict[str, Any]:
        """Get consensus from multiple AI services on tool execution"""
        cache_key = f"{tool_name}_{hash(str(arguments))}_{hash(execution_result[:100])}"

        if cache_key in self.consensus_cache:
            return self.consensus_cache[cache_key]

        consensus_prompt = f"""
        Evaluate this tool execution for safety, accuracy, and ethical concerns:

        Tool: {tool_name}
        Arguments: {json.dumps(arguments, indent=2)}
        Result: {execution_result[:1000]}...

        Provide evaluation as JSON:
        {{
            "safety_score": 0.0-1.0,
            "accuracy_score": 0.0-1.0,
            "ethical_score": 0.0-1.0,
            "overall_score": 0.0-1.0,
            "concerns": ["list", "of", "concerns"],
            "recommendations": ["list", "of", "recommendations"]
        }
        """

        evaluations = {}

        # Collect evaluations from available AI services
        for service_name, client in self.ai_clients.items():
            try:
                response = await self._get_ai_evaluation(client, service_name, consensus_prompt)
                if response:
                    evaluations[service_name] = response
            except Exception as e:
                logger.warning(f"Failed to get evaluation from {service_name}: {e}")

        # Calculate consensus
        consensus = self._calculate_consensus(evaluations)
        self.consensus_cache[cache_key] = consensus

        return consensus

    async def _get_ai_evaluation(self, client: Any, service_name: str, prompt: str) -> Optional[dict[str, Any]]:
        """Get evaluation from a specific AI service"""
        try:
            if service_name == "openai" and hasattr(client, "chat_completion"):
                response = await client.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    model="gpt-4",
                    temperature=0.1,
                )
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            elif service_name == "anthropic" and hasattr(client, "complete"):
                response = await client.complete(prompt, max_tokens=500, temperature=0.1)
                content = response.get("completion", "")

            elif service_name == "gemini" and hasattr(client, "generate"):
                response = await client.generate(prompt, temperature=0.1)
                content = response.get("text", "")

            else:
                return None

            # Try to parse JSON response
            try:
                # Extract JSON from response
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from {service_name} evaluation")

        except Exception as e:
            logger.error(f"AI evaluation error for {service_name}: {e}")

        return None

    def _calculate_consensus(self, evaluations: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Calculate consensus from multiple evaluations"""
        if not evaluations:
            return {
                "consensus_reached": False,
                "overall_score": 0.5,
                "confidence": 0.0,
                "concerns": ["No AI evaluations available"],
                "recommendations": ["Manual review recommended"],
                "evaluations": {},
            }

        # Aggregate scores
        scores = {
            "safety_score": [],
            "accuracy_score": [],
            "ethical_score": [],
            "overall_score": [],
        }

        all_concerns = []
        all_recommendations = []

        for evaluation in evaluations.values():
            for score_type in scores:
                if score_type in evaluation:
                    scores[score_type].append(evaluation[score_type])

            if "concerns" in evaluation:
                all_concerns.extend(evaluation["concerns"])
            if "recommendations" in evaluation:
                all_recommendations.extend(evaluation["recommendations"])

        # Calculate average scores
        avg_scores = {}
        for score_type, score_list in scores.items():
            if score_list:
                avg_scores[score_type] = sum(score_list) / len(score_list)
            else:
                avg_scores[score_type] = 0.5

        # Calculate consensus confidence
        overall_scores = scores["overall_score"]
        if len(overall_scores) >= 2:
            score_variance = sum((s - avg_scores["overall_score"]) ** 2 for s in overall_scores) / len(overall_scores)
            confidence = max(0.0, 1.0 - score_variance)
        else:
            confidence = 0.5

        consensus_reached = (
            len(evaluations) >= 2 and confidence >= self.consensus_threshold and avg_scores["overall_score"] >= 0.6
        )

        return {
            "consensus_reached": consensus_reached,
            "overall_score": avg_scores["overall_score"],
            "safety_score": avg_scores["safety_score"],
            "accuracy_score": avg_scores["accuracy_score"],
            "ethical_score": avg_scores["ethical_score"],
            "confidence": confidence,
            "concerns": list(set(all_concerns)),
            "recommendations": list(set(all_recommendations)),
            "evaluations": evaluations,
            "participating_services": list(evaluations.keys()),
        }


class ToolOrchestrator:
    """
    🎼 Tool Execution Orchestrator

    Coordinates tool execution with multi-AI consensus, Guardian validation,
    and comprehensive monitoring across the LUKHAS AI ecosystem.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core components
        self.tool_executor = ToolExecutor(config)
        self.guardian = get_tool_executor_guardian(config)

        # Multi-AI clients
        self.ai_clients = self._initialize_ai_clients()
        self.consensus = MultiAIConsensus(self.ai_clients)

        # Performance monitoring
        self.execution_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "guardian_blocks": 0,
            "consensus_approvals": 0,
            "consensus_concerns": 0,
            "avg_execution_time": 0.0,
            "avg_consensus_time": 0.0,
        }

        # Orchestration settings
        self.enable_consensus = self.config.get("enable_consensus", True)
        self.consensus_threshold = self.config.get("consensus_threshold", 0.7)
        self.max_execution_time = self.config.get("max_execution_time", 300)  # 5 minutes
        self.enable_performance_monitoring = self.config.get("enable_performance_monitoring", True)

        # Results cache
        self.results_cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hour

        logger.info("Tool Orchestrator initialized with multi-AI consensus")

    def _initialize_ai_clients(self) -> dict[str, Any]:
        """Initialize available AI service clients"""
        clients = {}

        # OpenAI Client
        if UnifiedOpenAIClient:
            try:
                clients["openai"] = UnifiedOpenAIClient()
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

        # Anthropic Client
        if AnthropicWrapper:
            try:
                clients["anthropic"] = AnthropicWrapper()
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")

        # Gemini Client
        if GeminiWrapper:
            try:
                clients["gemini"] = GeminiWrapper()
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

        # Perplexity Client
        if PerplexityWrapper:
            try:
                clients["perplexity"] = PerplexityWrapper()
                logger.info("Perplexity client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Perplexity client: {e}")

        return clients

    async def execute_with_orchestration(
        self,
        tool_name: str,
        arguments: str,
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute tool with full orchestration including Guardian validation,
        multi-AI consensus, and performance monitoring.
        """
        execution_start = time.time()
        execution_id = f"{tool_name}_{int(execution_start * 1000000)}"

        self.execution_metrics["total_executions"] += 1

        # Parse arguments
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
        except json.JSONDecodeError as e:
            return self._create_error_result(execution_id, f"Invalid JSON arguments: {e}", execution_start)

        # Check cache first
        cache_key = f"{tool_name}_{hash(str(args)}"
        if cache_key in self.results_cache:
            cache_entry = self.results_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                logger.info(f"Returning cached result for {tool_name}")
                return cache_entry["result"]

        try:
            # Step 1: Guardian Pre-validation
            guardian_result = None
            if self.guardian:
                try:
                    guardian_result = await self.guardian.validate_tool_execution(tool_name, args, user_context or {})

                    if not guardian_result["approved"]:
                        self.execution_metrics["guardian_blocks"] += 1
                        return self._create_guardian_blocked_result(execution_id, guardian_result, execution_start)

                except Exception as e:
                    logger.error(f"Guardian validation failed: {e}")
                    # Continue execution but log the failure

            # Step 2: Tool Execution
            execution_result = await asyncio.wait_for(
                self.tool_executor.execute(tool_name, arguments),
                timeout=self.max_execution_time,
            )

            execution_time = time.time() - execution_start

            # Step 3: Multi-AI Consensus (if enabled and available)
            consensus_result = None
            consensus_time = 0.0

            if self.enable_consensus and len(self.ai_clients) >= 2:
                consensus_start = time.time()
                try:
                    consensus_result = await asyncio.wait_for(
                        self.consensus.get_consensus(tool_name, args, execution_result),
                        timeout=30,  # 30 second timeout for consensus
                    )
                    consensus_time = time.time() - consensus_start

                    if consensus_result["consensus_reached"]:
                        self.execution_metrics["consensus_approvals"] += 1
                        if consensus_result["concerns"]:
                            self.execution_metrics["consensus_concerns"] += 1

                except asyncio.TimeoutError:
                    logger.warning(f"Consensus timeout for {tool_name}")
                except Exception as e:
                    logger.error(f"Consensus failed: {e}")

            # Step 4: Guardian Post-execution Logging
            if self.guardian and guardian_result:
                try:
                    await self.guardian.log_execution_decision(tool_name, args, guardian_result, execution_result)
                except Exception as e:
                    logger.warning(f"Guardian logging failed: {e}")

            # Update metrics
            self._update_execution_metrics(execution_time, consensus_time, True)

            # Create comprehensive result
            orchestration_result = {
                "execution_id": execution_id,
                "tool_name": tool_name,
                "arguments": args,
                "result": execution_result,
                "success": True,
                "execution_time": execution_time,
                "guardian_validation": guardian_result,
                "consensus_evaluation": consensus_result,
                "consensus_time": consensus_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cache_key": cache_key,
            }

            # Cache successful results
            self.results_cache[cache_key] = {
                "result": orchestration_result,
                "timestamp": time.time(),
            }

            logger.info(
                f"Tool orchestration completed: {tool_name}",
                extra={
                    "execution_id": execution_id,
                    "execution_time": execution_time,
                    "consensus_time": consensus_time,
                    "guardian_approved": (guardian_result["approved"] if guardian_result else None),
                    "consensus_reached": (consensus_result["consensus_reached"] if consensus_result else None),
                },
            )

            return orchestration_result

        except asyncio.TimeoutError:
            self._update_execution_metrics(0, 0, False)
            return self._create_error_result(
                execution_id,
                f"Execution timeout after {self.max_execution_time} seconds",
                execution_start,
            )

        except Exception as e:
            self._update_execution_metrics(0, 0, False)
            logger.error(f"Tool orchestration failed: {e}", exc_info=True)
            return self._create_error_result(execution_id, str(e), execution_start)

    def _create_error_result(self, execution_id: str, error: str, start_time: float) -> dict[str, Any]:
        """Create standardized error result"""
        self.execution_metrics["failed_executions"] += 1

        return {
            "execution_id": execution_id,
            "success": False,
            "error": error,
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _create_guardian_blocked_result(
        self, execution_id: str, guardian_result: dict[str, Any], start_time: float
    ) -> dict[str, Any]:
        """Create result when Guardian blocks execution"""
        return {
            "execution_id": execution_id,
            "success": False,
            "blocked_by": "guardian_system",
            "guardian_validation": guardian_result,
            "recommendations": guardian_result.get("recommendations", []),
            "ethical_concerns": guardian_result.get("ethical_concerns", []),
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _update_execution_metrics(self, execution_time: float, consensus_time: float, success: bool):
        """Update performance metrics"""
        if success:
            self.execution_metrics["successful_executions"] += 1
        else:
            self.execution_metrics["failed_executions"] += 1

        # Update average execution time
        total_executions = self.execution_metrics["total_executions"]
        current_avg = self.execution_metrics["avg_execution_time"]
        self.execution_metrics["avg_execution_time"] = (
            current_avg * (total_executions - 1) + execution_time
        ) / total_executions

        # Update average consensus time
        if consensus_time > 0:
            current_consensus_avg = self.execution_metrics["avg_consensus_time"]
            self.execution_metrics["avg_consensus_time"] = (
                current_consensus_avg * (total_executions - 1) + consensus_time
            ) / total_executions

    def get_orchestration_metrics(self) -> dict[str, Any]:
        """Get comprehensive orchestration metrics"""
        return {
            **self.execution_metrics,
            "success_rate": (
                self.execution_metrics["successful_executions"] / max(1, self.execution_metrics["total_executions"])
            ),
            "guardian_block_rate": (
                self.execution_metrics["guardian_blocks"] / max(1, self.execution_metrics["total_executions"])
            ),
            "consensus_reach_rate": (
                self.execution_metrics["consensus_approvals"] / max(1, self.execution_metrics["total_executions"])
            ),
            "available_ai_services": list(self.ai_clients.keys()),
            "cache_size": len(self.results_cache),
            "guardian_available": self.guardian is not None,
            "consensus_enabled": self.enable_consensus,
        }

    def clear_cache(self):
        """Clear the results cache"""
        self.results_cache.clear()
        logger.info("Orchestration cache cleared")

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            "orchestrator": "healthy",
            "tool_executor": "healthy",
            "guardian_system": "healthy" if self.guardian else "unavailable",
            "ai_services": {},
            "performance": self.get_orchestration_metrics(),
        }

        # Test AI services
        for service_name, client in self.ai_clients.items():
            try:
                # Simple test call with timeout
                test_response = await asyncio.wait_for(
                    self._get_ai_evaluation(client, service_name, "Test: respond with 'OK'"),
                    timeout=10,
                )
                health["ai_services"][service_name] = "healthy" if test_response else "degraded"
            except Exception as e:
                health["ai_services"][service_name] = f"error: {e!s}"

        return health


# Global orchestrator instance
_orchestrator: Optional[ToolOrchestrator] = None


def get_tool_orchestrator(config: Optional[dict[str, Any]] = None) -> ToolOrchestrator:
    """Get or create the global tool orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ToolOrchestrator(config)
    return _orchestrator
