"""
GPT-Colony Parallel Orchestrator
================================
Orchestrates parallel processing between GPT models and colony systems.
Enables hybrid AI decision-making with both centralized and distributed intelligence.

Based on GPT5 audit recommendations for parallel AI orchestration.
"""
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

# Use TYPE_CHECKING to avoid importing heavy/runtime-only modules at module
# import time. This lets the module be imported in isolation (for linting,
# test discovery, etc.) without pulling in `labs` or other runtime deps.
if TYPE_CHECKING:
    from labs.consciousness.reflection.openai_modulated_service import (
        OpenAICapability,
        OpenAIModulatedService,
    )

    from core.colonies.consensus_mechanisms import ColonyConsensus

    # Import our components for type checking only
    from core.colonies.enhanced_colony import (
        ConsensusResult,
        EnhancedReasoningColony,
    )
    from orchestration.signals.signal_bus import Signal, SignalBus, SignalType
else:
    # Runtime fallback placeholders; modules will be imported lazily when needed
    OpenAICapability = None
    OpenAIModulatedService = None
    ColonyConsensus = None
    ConsensusResult = None
    EnhancedReasoningColony = None
    Signal = None
    SignalBus = None
    SignalType = None

logger = logging.getLogger(__name__)


def _get_openai_provider():
    """
    Get OpenAI provider via registry (runtime injection).

    This function uses lazy loading to prevent import-time dependencies
    from production → labs. The provider is only imported when actually needed.

    Returns:
        OpenAIModulatedService instance from labs

    Raises:
        ImportError: If labs module is not available
    """
    from core.adapters.config_resolver import make_resolver
    from core.adapters.provider_registry import ProviderRegistry

    registry = ProviderRegistry(make_resolver())
    return registry.get_openai()


class OrchestrationMode(Enum):
    """Modes of GPT-Colony orchestration"""

    PARALLEL = "parallel"  # GPT and Colony work in parallel
    SEQUENTIAL = "sequential"  # GPT then Colony or vice versa
    COMPETITIVE = "competitive"  # Both compete, best wins
    COLLABORATIVE = "collaborative"  # Iterative refinement
    HIERARCHICAL = "hierarchical"  # GPT supervises colonies
    FEDERATED = "federated"  # Colonies federate, GPT aggregates


@dataclass
class OrchestrationTask:
    """A task to be processed by the orchestrator"""

    task_id: str
    content: str
    context: dict[str, Any] = field(default_factory=dict)
    mode: OrchestrationMode = OrchestrationMode.PARALLEL
    priority: int = 5
    deadline: Optional[float] = None
    required_confidence: float = 0.7
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Result from orchestrated processing"""

    task_id: str
    gpt_response: Optional[dict[str, Any]] = None
    colony_response: Optional[ConsensusResult] = None
    final_decision: Any = None
    confidence: float = 0.0
    processing_time: float = 0.0
    mode_used: OrchestrationMode = OrchestrationMode.PARALLEL
    signals_emitted: list[Signal] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class GPTColonyOrchestrator:
    """
    Orchestrates parallel processing between GPT models and colony systems.
    Implements multiple orchestration patterns for hybrid AI decision-making.
    """

    def __init__(
        self,
        openai_service: Optional[OpenAIModulatedService] = None,
        signal_bus: Optional[SignalBus] = None,
    ):
        # Use provided service or lazy-load via provider (eliminates import-time dependency)
        self._openai_service = openai_service
        self._signal_bus = signal_bus
        self._openai_loaded = False
        self._signal_bus_loaded = False

        # Colony management
        self.colonies: dict[str, EnhancedReasoningColony] = {}
        self.colony_consensus: dict[str, ColonyConsensus] = {}

        # Task management
        self.active_tasks: dict[str, OrchestrationTask] = {}
        self.results: dict[str, OrchestrationResult] = {}

        # Performance tracking
        self.performance_metrics = {
            "gpt_success_rate": 0.0,
            "colony_success_rate": 0.0,
            "collaboration_improvement": 0.0,
            "avg_processing_time": 0.0,
        }

        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=10)

    @property
    def openai_service(self):
        """Lazy-load OpenAI service on first access."""
        if self._openai_service is None and not self._openai_loaded:
            try:
                self._openai_service = _get_openai_provider()
                self._openai_loaded = True
            except ImportError as e:
                logger.warning(f"Failed to load OpenAI provider: {e}")
                self._openai_loaded = True  # Mark as attempted to avoid repeated failures
        return self._openai_service

    @property
    def signal_bus(self):
        """Lazy-load signal bus on first access."""
        if self._signal_bus is None and not self._signal_bus_loaded:
            try:
                # Import signal bus lazily
                from orchestration.signals.signal_bus import SignalBus
                self._signal_bus = SignalBus()
                self._signal_bus_loaded = True
            except ImportError as e:
                logger.warning(f"Failed to load SignalBus: {e}")
                self._signal_bus_loaded = True
        return self._signal_bus

    def register_colony(self, colony_id: str, colony: EnhancedReasoningColony):
        """Register a colony for orchestration"""
        self.colonies[colony_id] = colony
        self.colony_consensus[colony_id] = ColonyConsensus(colony_id, self.signal_bus)

        # Register some default agents
        for i in range(5):
            self.colony_consensus[colony_id].register_agent(f"{colony_id}_agent_{i}", weight=1.0)

        logger.info(f"Registered colony {colony_id} for orchestration")

    async def process_task(self, task: OrchestrationTask) -> OrchestrationResult:
        """Process a task using the specified orchestration mode"""
        start_time = time.time()

        self.active_tasks[task.task_id] = task

        # Choose orchestration strategy
        if task.mode == OrchestrationMode.PARALLEL:
            result = await self._parallel_orchestration(task)
        elif task.mode == OrchestrationMode.SEQUENTIAL:
            result = await self._sequential_orchestration(task)
        elif task.mode == OrchestrationMode.COMPETITIVE:
            result = await self._competitive_orchestration(task)
        elif task.mode == OrchestrationMode.COLLABORATIVE:
            result = await self._collaborative_orchestration(task)
        elif task.mode == OrchestrationMode.HIERARCHICAL:
            result = await self._hierarchical_orchestration(task)
        elif task.mode == OrchestrationMode.FEDERATED:
            result = await self._federated_orchestration(task)
        else:
            result = await self._parallel_orchestration(task)

        result.processing_time = time.time() - start_time

        # Store result
        self.results[task.task_id] = result
        del self.active_tasks[task.task_id]

        # Update metrics
        self._update_metrics(result)

        # Emit completion signal
        await self._emit_signal(
            SignalType.TRUST,
            result.confidence,
            {
                "task_id": task.task_id,
                "mode": task.mode.value,
                "success": result.confidence > task.required_confidence,
            },
        )

        return result

    async def _parallel_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """GPT and Colony process in parallel, results combined"""

        # Create parallel tasks
        gpt_task = asyncio.create_task(self._process_with_gpt(task))
        colony_task = asyncio.create_task(self._process_with_colony(task))

        # Wait for both
        gpt_response, colony_response = await asyncio.gather(
            gpt_task, colony_task, return_exceptions=True
        )

        # Handle exceptions
        if isinstance(gpt_response, Exception):
            logger.error(f"GPT processing failed: {gpt_response}")
            gpt_response = None

        if isinstance(colony_response, Exception):
            logger.error(f"Colony processing failed: {colony_response}")
            colony_response = None

        # Combine results
        result = OrchestrationResult(
            task_id=task.task_id,
            gpt_response=gpt_response,
            colony_response=colony_response,
            mode_used=OrchestrationMode.PARALLEL,
        )

        # Determine final decision
        if gpt_response and colony_response:
            # Both succeeded - combine with weighted average
            gpt_confidence = gpt_response.get("confidence", 0.5)
            colony_confidence = colony_response.confidence

            if gpt_confidence > colony_confidence:
                result.final_decision = gpt_response.get("response")
                result.confidence = gpt_confidence
            else:
                result.final_decision = colony_response.decision
                result.confidence = colony_confidence

            # Boost confidence if both agree
            if self._responses_agree(gpt_response, colony_response):
                result.confidence = min(1.0, result.confidence * 1.2)

        elif gpt_response:
            result.final_decision = gpt_response.get("response")
            result.confidence = gpt_response.get("confidence", 0.5)
        elif colony_response:
            result.final_decision = colony_response.decision
            result.confidence = colony_response.confidence
        else:
            result.confidence = 0.0

        return result

    async def _sequential_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """Process with GPT first, then refine with Colony"""

        # First, process with GPT
        gpt_response = await self._process_with_gpt(task)

        if gpt_response:
            # Add GPT response to context for colony
            enhanced_task = OrchestrationTask(
                task_id=f"{task.task_id}_enhanced",
                content=task.content,
                context={
                    **task.context,
                    "gpt_suggestion": gpt_response.get("response"),
                    "gpt_confidence": gpt_response.get("confidence", 0.5),
                },
            )

            # Process with colony
            colony_response = await self._process_with_colony(enhanced_task)
        else:
            colony_response = await self._process_with_colony(task)

        result = OrchestrationResult(
            task_id=task.task_id,
            gpt_response=gpt_response,
            colony_response=colony_response,
            mode_used=OrchestrationMode.SEQUENTIAL,
        )

        # Colony has final say in sequential mode
        if colony_response:
            result.final_decision = colony_response.decision
            result.confidence = colony_response.confidence
        elif gpt_response:
            result.final_decision = gpt_response.get("response")
            result.confidence = gpt_response.get("confidence", 0.5) * 0.8  # Reduce confidence

        return result

    async def _competitive_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """GPT and Colony compete, best solution wins"""

        # Process in parallel
        gpt_response, colony_response = await asyncio.gather(
            self._process_with_gpt(task),
            self._process_with_colony(task),
            return_exceptions=True,
        )

        # Handle exceptions
        if isinstance(gpt_response, Exception):
            gpt_response = None
        if isinstance(colony_response, Exception):
            colony_response = None

        result = OrchestrationResult(
            task_id=task.task_id,
            gpt_response=gpt_response,
            colony_response=colony_response,
            mode_used=OrchestrationMode.COMPETITIVE,
        )

        # Competition scoring
        gpt_score = 0.0
        colony_score = 0.0

        if gpt_response:
            gpt_score = gpt_response.get("confidence", 0.5)
            # Adjust for response quality
            if "reasoning" in gpt_response:
                gpt_score *= 1.1

        if colony_response:
            colony_score = colony_response.confidence
            # Adjust for consensus quality
            if colony_response.participation_rate > 0.8:
                colony_score *= 1.1

        # Winner takes all
        if gpt_score > colony_score:
            result.final_decision = gpt_response.get("response") if gpt_response else None
            result.confidence = gpt_score
            result.metadata["winner"] = "gpt"
        else:
            result.final_decision = colony_response.decision if colony_response else None
            result.confidence = colony_score
            result.metadata["winner"] = "colony"

        result.metadata["competition_scores"] = {
            "gpt": gpt_score,
            "colony": colony_score,
        }

        return result

    async def _collaborative_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """Iterative refinement between GPT and Colony"""

        max_iterations = 3
        convergence_threshold = 0.9

        result = OrchestrationResult(
            task_id=task.task_id, mode_used=OrchestrationMode.COLLABORATIVE
        )

        current_context = task.context.copy()

        for iteration in range(max_iterations):
            # GPT proposes
            gpt_task = OrchestrationTask(
                task_id=f"{task.task_id}_gpt_{iteration}",
                content=task.content,
                context=current_context,
            )
            gpt_response = await self._process_with_gpt(gpt_task)

            if not gpt_response:
                break

            # Colony reviews
            colony_task = OrchestrationTask(
                task_id=f"{task.task_id}_colony_{iteration}",
                content=f"Review: {gpt_response.get('response')}",
                context={
                    **current_context,
                    "gpt_proposal": gpt_response.get("response"),
                    "iteration": iteration,
                },
            )
            colony_response = await self._process_with_colony(colony_task)

            if not colony_response:
                break

            # Update context for next iteration
            current_context["previous_gpt"] = gpt_response.get("response")
            current_context["previous_colony"] = colony_response.decision
            current_context["iteration"] = iteration + 1

            # Check convergence
            new_confidence = (gpt_response.get("confidence", 0.5) + colony_response.confidence) / 2

            if new_confidence > convergence_threshold:
                # Converged
                result.final_decision = gpt_response.get("response")
                result.confidence = new_confidence
                result.gpt_response = gpt_response
                result.colony_response = colony_response
                break

        result.metadata["iterations"] = iteration + 1
        result.metadata["converged"] = result.confidence > convergence_threshold

        return result

    async def _hierarchical_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """GPT supervises and directs colony operations"""

        # GPT creates sub-tasks for colonies
        gpt_planning = await self._process_with_gpt(
            OrchestrationTask(
                task_id=f"{task.task_id}_planning",
                content=f"Create 3 sub-tasks for: {task.content}",
                context=task.context,
            )
        )

        if not gpt_planning:
            # Fallback to direct colony processing
            colony_response = await self._process_with_colony(task)
            return OrchestrationResult(
                task_id=task.task_id,
                colony_response=colony_response,
                final_decision=colony_response.decision if colony_response else None,
                confidence=colony_response.confidence if colony_response else 0.0,
                mode_used=OrchestrationMode.HIERARCHICAL,
            )

        # Parse sub-tasks (simplified - in production would parse properly)
        sub_tasks = []
        response_text = str(gpt_planning.get("response", ""))
        for i, line in enumerate(response_text.split("\n")[:3]):
            if line.strip():
                sub_tasks.append({"id": f"sub_{i}", "content": line.strip()})

        # Process sub-tasks with colonies
        colony_results = []
        for sub_task in sub_tasks:
            sub_response = await self._process_with_colony(
                OrchestrationTask(
                    task_id=f"{task.task_id}_{sub_task['id']}",
                    content=sub_task["content"],
                    context=task.context,
                )
            )
            if sub_response:
                colony_results.append(sub_response)

        # GPT aggregates colony results
        aggregation_context = {
            **task.context,
            "colony_results": [
                {"decision": str(r.decision), "confidence": r.confidence}
                for r in colony_results
            ],
        }

        gpt_final = await self._process_with_gpt(
            OrchestrationTask(
                task_id=f"{task.task_id}_aggregation",
                content=f"Synthesize results for: {task.content}",
                context=aggregation_context,
            )
        )

        result = OrchestrationResult(
            task_id=task.task_id,
            gpt_response=gpt_final,
            mode_used=OrchestrationMode.HIERARCHICAL,
        )

        if gpt_final:
            result.final_decision = gpt_final.get("response")
            result.confidence = gpt_final.get("confidence", 0.5)

        result.metadata["sub_tasks"] = len(sub_tasks)
        result.metadata["colony_results"] = len(colony_results)

        return result

    async def _federated_orchestration(self, task: OrchestrationTask) -> OrchestrationResult:
        """Multiple colonies federate, GPT aggregates consensus"""

        # Process with all available colonies
        colony_tasks = []
        for colony_id in self.colonies:
            colony_tasks.append(self._process_with_specific_colony(task, colony_id))

        colony_responses = await asyncio.gather(*colony_tasks, return_exceptions=True)

        # Filter successful responses
        valid_responses = [
            r
            for r in colony_responses
            if not isinstance(r, Exception) and r is not None
        ]

        if not valid_responses:
            return OrchestrationResult(
                task_id=task.task_id,
                confidence=0.0,
                mode_used=OrchestrationMode.FEDERATED,
            )

        # Calculate federated consensus
        decisions = {}
        total_confidence = 0.0

        for response in valid_responses:
            decision_key = str(response.decision)
            if decision_key not in decisions:
                decisions[decision_key] = {"count": 0, "total_confidence": 0.0}
            decisions[decision_key]["count"] += 1
            decisions[decision_key]["total_confidence"] += response.confidence
            total_confidence += response.confidence

        # Find majority decision
        best_decision = max(decisions.items(), key=lambda x: x[1]["total_confidence"])[0]

        # GPT synthesizes the federated results
        synthesis_context = {
            **task.context,
            "federated_consensus": best_decision,
            "colony_count": len(valid_responses),
            "decision_distribution": decisions,
        }

        gpt_synthesis = await self._process_with_gpt(
            OrchestrationTask(
                task_id=f"{task.task_id}_synthesis",
                content=f"Synthesize federated consensus for: {task.content}",
                context=synthesis_context,
            )
        )

        result = OrchestrationResult(
            task_id=task.task_id,
            gpt_response=gpt_synthesis,
            mode_used=OrchestrationMode.FEDERATED,
        )

        if gpt_synthesis:
            result.final_decision = gpt_synthesis.get("response")
            result.confidence = gpt_synthesis.get("confidence", 0.5)
        else:
            result.final_decision = best_decision
            result.confidence = (
                decisions[best_decision]["total_confidence"] / max(1, total_confidence)
            )

        result.metadata["colonies_participated"] = len(valid_responses)
        result.metadata["federated_consensus"] = best_decision

        return result

    async def _process_with_gpt(self, task: OrchestrationTask) -> Optional[dict[str, Any]]:
        """Process task with GPT model"""
        try:
            # Import OpenAICapability lazily to avoid import-time dependency
            if TYPE_CHECKING:
                from labs.consciousness.reflection.openai_modulated_service import OpenAICapability
            else:
                import importlib
                module = importlib.import_module("labs.consciousness.reflection.openai_modulated_service")
                OpenAICapability = getattr(module, "OpenAICapability")

            response = await self.openai_service.process_modulated_request(
                module="orchestrator",
                capability=OpenAICapability.REASONING,
                data={"prompt": task.content, "context": task.context},
            )

            if response and response.success:
                return {
                    "response": response.data.get("response"),
                    "confidence": response.data.get("confidence", 0.7),
                    "reasoning": response.data.get("reasoning"),
                    "model": response.model_used,
                }

        except Exception as e:
            logger.error(f"GPT processing error: {e}")

        return None

    async def _process_with_colony(self, task: OrchestrationTask) -> Optional[ConsensusResult]:
        """Process task with first available colony"""
        if not self.colonies:
            return None

        # Use first colony (in production, would select based on capabilities)
        colony_id = next(iter(self.colonies.keys()))
        return await self._process_with_specific_colony(task, colony_id)

    async def _process_with_specific_colony(
        self, task: OrchestrationTask, colony_id: str
    ) -> Optional[ConsensusResult]:
        """Process task with specific colony"""
        try:
            colony = self.colonies.get(colony_id)
            if not colony:
                return None

            result = await colony.process_query(query=task.content, context=task.context)

            return result

        except Exception as e:
            logger.error(f"Colony processing error: {e}")
            return None

    def _responses_agree(
        self, gpt_response: dict[str, Any], colony_response: ConsensusResult
    ) -> bool:
        """Check if GPT and Colony responses agree"""
        if not gpt_response or not colony_response:
            return False

        # Simplified agreement check
        gpt_text = str(gpt_response.get("response", "")).lower()
        colony_text = str(colony_response.decision).lower()

        # Check for common agreement patterns
        positive_terms = ["yes", "approve", "agree", "accept", "true"]
        negative_terms = ["no", "reject", "disagree", "deny", "false"]

        gpt_positive = any(term in gpt_text for term in positive_terms)
        gpt_negative = any(term in gpt_text for term in negative_terms)
        colony_positive = any(term in colony_text for term in positive_terms)
        colony_negative = any(term in colony_text for term in negative_terms)

        return (gpt_positive == colony_positive) and (gpt_negative == colony_negative)

    def _update_metrics(self, result: OrchestrationResult):
        """Update performance metrics"""
        # Simplified metric tracking
        if result.gpt_response:
            self.performance_metrics[
                "gpt_success_rate"
            ] = self.performance_metrics["gpt_success_rate"] * 0.9 + 0.1

        if result.colony_response:
            self.performance_metrics[
                "colony_success_rate"
            ] = self.performance_metrics["colony_success_rate"] * 0.9 + 0.1

        if result.confidence > 0.8:
            self.performance_metrics["collaboration_improvement"] = (
                self.performance_metrics["collaboration_improvement"] * 0.9 + 0.1
            )

        self.performance_metrics["avg_processing_time"] = (
            self.performance_metrics["avg_processing_time"] * 0.9
            + result.processing_time * 0.1
        )

    async def _emit_signal(self, signal_type: SignalType, level: float, metadata: dict):
        """Emit signal through signal bus"""
        signal = Signal(
            name=signal_type,
            source="gpt_colony_orchestrator",
            level=level,
            metadata=metadata,
        )
        self.signal_bus.publish(signal)

    def get_performance_report(self) -> dict[str, Any]:
        """Get orchestrator performance report"""
        return {
            "metrics": self.performance_metrics,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.results),
            "registered_colonies": len(self.colonies),
            "orchestration_modes_used": {
                mode.value: (
                    sum(1 for r in self.results.values() if r.mode_used == mode)
                )
                for mode in OrchestrationMode
            },
        }


# Demo usage
async def demo_orchestrator():
    """Demonstrate GPT-Colony orchestration"""

    # Create orchestrator
    orchestrator = GPTColonyOrchestrator()

    # Register a colony
    colony = EnhancedReasoningColony("demo-colony")
    orchestrator.register_colony("demo-colony", colony)

    print("🎭 GPT-Colony Orchestrator Demo")
    print("=" * 50)

    # Test different orchestration modes
    test_tasks = [
        OrchestrationTask(
            task_id="task_parallel",
            content="Should we scale up the system resources?",
            mode=OrchestrationMode.PARALLEL,
            context={"current_load": 0.75},
        ),
        OrchestrationTask(
            task_id="task_competitive",
            content="What's the best optimization strategy?",
            mode=OrchestrationMode.COMPETITIVE,
            context={"performance_goal": "latency"},
        ),
        OrchestrationTask(
            task_id="task_collaborative",
            content="Design a new feature for user engagement",
            mode=OrchestrationMode.COLLABORATIVE,
            context={"user_segment": "power_users"},
        ),
    ]

    for task in test_tasks:
        print(f"\n📋 Processing task: {task.task_id}")
        print(f"   Mode: {task.mode.value}")
        print(f"   Content: {task.content}")

        result = await orchestrator.process_task(task)

        print("   ✅ Result:")
        print(f"      Decision: {result.final_decision}")
        print(f"      Confidence: {result.confidence:.2%}")
        print(f"      Processing time: {result.processing_time:.2f}s")

        if result.metadata:
            print(f"      Metadata: {result.metadata}")

    # Show performance report
    print("\n📊 Performance Report:")
    report = orchestrator.get_performance_report()
    for key, value in report["metrics"].items():
        print(f"   {key}: {value:.2%}" if "rate" in key else f"   {key}: {value:.2f}")


if __name__ == "__main__":
    asyncio.run(demo_orchestrator())
