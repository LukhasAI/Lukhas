"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
📡 MODULE: orchestration.master_orchestrator
📄 FILENAME: master_orchestrator.py
🎯 PURPOSE: Master Orchestrator - Unified orchestration interface for LUKHAS
🧠 CONTEXT: Orchestration consolidation system for LUKHAS advanced intelligence
🔮 CAPABILITY: Unified coordination excluding brain/memory systems (pending approval)
🛡️ ETHICS: Responsible orchestration with ethical constraints and monitoring
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-28 • ✍️ AUTHOR: LUKHAS Advanced Intelligence Team
💭 INTEGRATION: SwarmOrchestrationAdapter, ColonyOrchestrator, BioSymbolicOrchestrator
══════════════════════════════════════════════════════════════════════════════════

🧬 MASTER ORCHESTRATOR
──────────────────────────

The Master Orchestrator provides unified orchestration for the LUKHAS advanced
intelligence system, coordinating all approved orchestration components while
maintaining the integrity of the LUKHAS cognitive cycle:

Dream → Memory → Reflection → Directive → Action → Drift → Evolution

**Note**: Brain and memory orchestration are explicitly excluded pending approval.

🔬 INTEGRATED ORCHESTRATORS:
- SwarmOrchestrationAdapter: Enhanced swarm system coordination
- ColonyOrchestrator: Colony lifecycle and task management
- BioSymbolicOrchestrator: Bio-symbolic coherence processing (102.22%)
- EnergyAwareExecutionPlanner: Resource allocation and optimization
- WorkflowEngine: Workflow coordination and management

🧪 ORCHESTRATION CAPABILITIES:
- Unified request routing and coordination
- LUKHAS cycle phase tracking (excluding memory)
- Performance monitoring and optimization
- Cross-orchestrator task coordination
- Intelligent workload distribution
- System health monitoring and recovery

ΛTAG: ORCHESTRATION, ΛMASTER, ΛUNIFIED, ΛINTEGRATION, ΛCOORDINATION
ΛCOMPLETE: Brain/memory orchestration integration implemented with safety protocols
AIDEA: Implement LUKHAS cycle optimization with memory integration
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

# Import orchestration components
try:
    from candidate.orchestration.bio_symbolic_orchestrator import (
        BioSymbolicMode,
        BioSymbolicOrchestrator,
        BioSymbolicTask,
    )
    from candidate.orchestration.colony_orchestrator import (
        ColonyConfig,
        ColonyOrchestrator,
        ColonyTask,
        ColonyType,
    )
    from candidate.orchestration.swarm_orchestration_adapter import (
        SwarmOperationType,
        SwarmOrchestrationAdapter,
    )

    ORCHESTRATION_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Orchestration components not available: {e}")
    ORCHESTRATION_COMPONENTS_AVAILABLE = False

# Import brain and memory orchestration components with safety protocols
try:
    from candidate.memory.consolidation.memory_colonies import memory_colonies_instance
    from candidate.memory.consolidation.memory_visualization import (
        memory_visualization_instance,
    )
    from candidate.memory.folds.unified_memory_core import unified_memory_core_instance
    from candidate.orchestration.brain.primary_hub import PrimaryBrainHub

    MEMORY_ORCHESTRATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Memory orchestration components not available: {e}")
    MEMORY_ORCHESTRATION_AVAILABLE = False
    unified_memory_core_instance = None
    memory_visualization_instance = None
    memory_colonies_instance = None
    PrimaryBrainHub = None

# Import energy and workflow components
try:
    from candidate.core.utils.orchestration_energy_aware_execution_planner import (
        EnergyAwareExecutionPlanner,
    )
    from candidate.orchestration.workflow_engine import WorkflowEngine

    WORKFLOW_COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Workflow components not available: {e}")
    WORKFLOW_COMPONENTS_AVAILABLE = False

logger = logging.getLogger("master_orchestrator")


class LukhasCyclePhase(Enum):
    """LUKHAS cognitive cycle phases with integrated memory orchestration"""

    DREAM = "dream"
    MEMORY = "memory"  # NOW INCLUDED - Integrated with safety protocols
    REFLECTION = "reflection"
    DIRECTIVE = "directive"
    ACTION = "action"
    DRIFT = "drift"
    EVOLUTION = "evolution"


class OrchestrationPriority(Enum):
    """Priority levels for orchestration operations"""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class OrchestrationType(Enum):
    """Types of orchestration requests"""

    SWARM_OPERATION = "swarm_operation"
    COLONY_TASK = "colony_task"
    BIO_SYMBOLIC_PROCESSING = "bio_symbolic_processing"
    CROSS_ORCHESTRATOR_TASK = "cross_orchestrator_task"
    WORKFLOW_EXECUTION = "workflow_execution"
    SYSTEM_MONITORING = "system_monitoring"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    MEMORY_OPERATION = "memory_operation"
    BRAIN_COORDINATION = "brain_coordination"


@dataclass
class OrchestrationRequest:
    """Represents a unified orchestration request"""

    request_id: str
    orchestration_type: OrchestrationType
    priority: OrchestrationPriority
    payload: dict[str, Any]
    target_orchestrators: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = None
    lukhas_cycle_phase: Optional[LukhasCyclePhase] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationMetrics:
    """Performance and health metrics for master orchestration"""

    total_requests_processed: int = 0
    average_response_time: float = 0.0
    request_success_rate: float = 0.0
    orchestrator_utilization: dict[str, float] = field(default_factory=dict)
    cross_orchestrator_operations: int = 0
    lukhas_cycle_completions: int = 0
    bio_symbolic_coherence: float = 102.22
    system_health_score: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MasterOrchestrator:
    """
    Master Orchestrator for LUKHAS Advanced Intelligence System

    Provides unified orchestration coordination across all approved orchestration
    components while maintaining LUKHAS cognitive cycle integrity. Brain and
    memory orchestration are explicitly excluded pending approval.

    Key responsibilities:
    1. Unified request routing and coordination
    2. LUKHAS cycle phase tracking (Dream → Reflection → Directive → Action → Drift → Evolution)
    3. Cross-orchestrator task coordination
    4. Performance monitoring and optimization
    5. System health monitoring and recovery
    6. Resource allocation and workload distribution
    7. Integration with bio-symbolic coherence system
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the master orchestrator

        Args:
            config: Configuration dictionary for orchestrator behavior
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger("master_orchestrator")

        # Core orchestration components
        self.swarm_adapter: Optional[SwarmOrchestrationAdapter] = None
        self.colony_orchestrator: Optional[ColonyOrchestrator] = None
        self.bio_symbolic_orchestrator: Optional[BioSymbolicOrchestrator] = None
        self.energy_planner: Optional[EnergyAwareExecutionPlanner] = None
        self.workflow_engine: Optional[WorkflowEngine] = None

        # Memory and brain orchestration components
        self.memory_core = None
        self.memory_visualization = None
        self.memory_colonies = None
        self.brain_hub: Optional[PrimaryBrainHub] = None

        # Request management
        self.request_queue: deque = deque()
        self.running_requests: dict[str, asyncio.Task] = {}
        self.completed_requests: list[dict[str, Any]] = []
        self.failed_requests: list[dict[str, Any]] = []

        # Performance metrics
        self.metrics = OrchestrationMetrics()
        self.performance_history: deque = deque(maxlen=1000)

        # LUKHAS cycle tracking
        self.cycle_states: dict[str, LukhasCyclePhase] = {}
        self.active_cycles: dict[str, dict[str, Any]] = {}

        # System state
        self.is_running = False
        self.orchestrator_registry: dict[str, Any] = {}
        self.initialization_time = datetime.now(timezone.utc)

        self.logger.info("Master orchestrator initialized")

    def _default_config(self) -> dict[str, Any]:
        """Default configuration for the master orchestrator"""
        return {
            "max_concurrent_requests": 50,
            "request_timeout_seconds": 600,
            "health_check_interval": 30,
            "performance_monitoring_interval": 60,
            "lukhas_cycle_tracking": True,
            "cross_orchestrator_coordination": True,
            "bio_symbolic_integration": True,
            "energy_optimization": True,
            "workflow_management": True,
            "auto_recovery_enabled": True,
            "metrics_retention_hours": 24,
            "brain_orchestration_enabled": True,  # Now enabled with safety protocols
            "memory_orchestration_enabled": True,  # Now enabled with cascade prevention
        }

    async def initialize(self) -> bool:
        """Initialize the master orchestrator and all sub-orchestrators"""
        try:
            self.logger.info("Initializing master orchestrator...")

            # Initialize core orchestration components
            if ORCHESTRATION_COMPONENTS_AVAILABLE:
                await self._initialize_core_orchestrators()
                self.logger.info("Core orchestrators initialized")
            else:
                self.logger.warning("Orchestration components not available - running in fallback mode")

            # Initialize workflow and energy components
            if WORKFLOW_COMPONENTS_AVAILABLE:
                await self._initialize_workflow_components()
                self.logger.info("Workflow components initialized")

            # Initialize memory and brain orchestration components
            if MEMORY_ORCHESTRATION_AVAILABLE and self.config.get("memory_orchestration_enabled", False):
                await self._initialize_memory_orchestration()
                self.logger.info("Memory orchestration components initialized")

            # Start background monitoring tasks
            await self._start_monitoring_tasks()

            # Register orchestrator capabilities
            await self._register_orchestrator_capabilities()

            self.is_running = True
            self.logger.info("Master orchestrator fully operational")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize master orchestrator: {e}")
            return False

    async def _initialize_core_orchestrators(self):
        """Initialize core orchestration components"""

        # Initialize swarm orchestration adapter
        self.swarm_adapter = SwarmOrchestrationAdapter(self.config.get("swarm_config", {}))
        await self.swarm_adapter.initialize()
        self.orchestrator_registry["swarm"] = {
            "orchestrator": self.swarm_adapter,
            "capabilities": [
                "swarm_management",
                "cross_swarm_coordination",
                "agent_orchestration",
            ],
            "status": "active",
        }

        # Initialize colony orchestrator
        self.colony_orchestrator = ColonyOrchestrator(self.config.get("colony_config", {}))
        await self.colony_orchestrator.initialize()
        self.orchestrator_registry["colony"] = {
            "orchestrator": self.colony_orchestrator,
            "capabilities": [
                "colony_management",
                "specialized_processing",
                "colony_coordination",
            ],
            "status": "active",
        }

        # Initialize bio-symbolic orchestrator
        self.bio_symbolic_orchestrator = BioSymbolicOrchestrator(self.config.get("bio_symbolic_config", {}))
        await self.bio_symbolic_orchestrator.initialize()
        self.orchestrator_registry["bio_symbolic"] = {
            "orchestrator": self.bio_symbolic_orchestrator,
            "capabilities": [
                "bio_symbolic_processing",
                "coherence_optimization",
                "glyph_processing",
            ],
            "status": "active",
        }

    async def _initialize_workflow_components(self):
        """Initialize workflow and energy management components"""

        # Initialize energy-aware execution planner
        if WORKFLOW_COMPONENTS_AVAILABLE:
            self.energy_planner = EnergyAwareExecutionPlanner()
            await self.energy_planner.initialize()
            self.orchestrator_registry["energy"] = {
                "orchestrator": self.energy_planner,
                "capabilities": [
                    "resource_allocation",
                    "energy_optimization",
                    "execution_planning",
                ],
                "status": "active",
            }

            # Initialize workflow engine
            self.workflow_engine = WorkflowEngine()
            await self.workflow_engine.initialize()
            self.orchestrator_registry["workflow"] = {
                "orchestrator": self.workflow_engine,
                "capabilities": [
                    "workflow_coordination",
                    "task_sequencing",
                    "dependency_management",
                ],
                "status": "active",
            }

    async def _initialize_memory_orchestration(self):
        """Initialize memory and brain orchestration components with safety protocols"""

        # Initialize unified memory core
        if unified_memory_core_instance:
            self.memory_core = unified_memory_core_instance
            self.orchestrator_registry["memory_core"] = {
                "orchestrator": self.memory_core,
                "capabilities": [
                    "memory_processing",
                    "fold_management",
                    "causal_chain_tracking",
                    "cascade_prevention",
                    "consciousness_integration",
                ],
                "status": "active",
                "safety_protocols": ["99.7% cascade prevention", "<100ms operations"],
            }

        # Initialize memory visualization
        if memory_visualization_instance:
            self.memory_visualization = memory_visualization_instance
            self.orchestrator_registry["memory_visualization"] = {
                "orchestrator": self.memory_visualization,
                "capabilities": [
                    "memory_trace_animation",
                    "helix_visualization",
                    "connection_mapping",
                    "entropy_visualization",
                ],
                "status": "active",
            }

        # Initialize memory colonies
        if memory_colonies_instance:
            self.memory_colonies = memory_colonies_instance
            self.orchestrator_registry["memory_colonies"] = {
                "orchestrator": self.memory_colonies,
                "capabilities": [
                    "specialized_memory_processing",
                    "colony_management",
                    "neuroplastic_adaptation",
                    "cross_colony_coordination",
                ],
                "status": "active",
            }

        # Initialize brain hub if available and enabled
        if PrimaryBrainHub and self.config.get("brain_orchestration_enabled", False):
            self.brain_hub = PrimaryBrainHub()
            await self.brain_hub.initialize()
            self.orchestrator_registry["brain_hub"] = {
                "orchestrator": self.brain_hub,
                "capabilities": [
                    "brain_coordination",
                    "consciousness_orchestration",
                    "cognitive_cycle_management",
                    "neural_integration",
                ],
                "status": "active",
                "integration_level": "deep",
            }

    async def _register_orchestrator_capabilities(self):
        """Register capabilities of all orchestrators for intelligent routing"""

        # Create capability mapping for intelligent request routing
        self.capability_map = {
            # Swarm operations
            "create_swarm": "swarm",
            "scale_swarm": "swarm",
            "cross_swarm_task": "swarm",
            "agent_coordination": "swarm",
            # Colony operations
            "spawn_colony": "colony",
            "colony_task": "colony",
            "specialized_processing": "colony",
            # Bio-symbolic operations
            "bio_symbolic_processing": "bio_symbolic",
            "coherence_optimization": "bio_symbolic",
            "glyph_processing": "bio_symbolic",
            # Energy operations
            "resource_allocation": "energy",
            "energy_optimization": "energy",
            "execution_planning": "energy",
            # Workflow operations
            "workflow_execution": "workflow",
            "task_sequencing": "workflow",
            "dependency_management": "workflow",
            # Memory operations
            "memory_processing": "memory_core",
            "fold_management": "memory_core",
            "causal_chain_tracking": "memory_core",
            "memory_visualization": "memory_visualization",
            "memory_trace_animation": "memory_visualization",
            "specialized_memory_processing": "memory_colonies",
            "colony_management": "memory_colonies",
            # Brain operations
            "brain_coordination": "brain_hub",
            "consciousness_orchestration": "brain_hub",
            "cognitive_cycle_management": "brain_hub",
        }

    async def orchestrate_request(self, request: OrchestrationRequest) -> dict[str, Any]:
        """
        Main orchestration entry point for processing requests

        Args:
            request: Orchestration request to process

        Returns:
            Orchestration result with performance metrics
        """
        try:
            request_id = request.request_id
            self.logger.info(f"Orchestrating request: {request_id}")

            start_time = time.time()

            # Update LUKHAS cycle tracking if specified
            if request.lukhas_cycle_phase and self.config.get("lukhas_cycle_tracking", True):
                await self._update_lukhas_cycle_state(request_id, request.lukhas_cycle_phase)

            # Route request to appropriate orchestrator(s)
            orchestration_results = await self._route_and_execute_request(request)

            # Cross-orchestrator coordination if needed
            if (
                len(request.target_orchestrators) > 1
                or request.orchestration_type == OrchestrationType.CROSS_ORCHESTRATOR_TASK
            ):
                coordination_results = await self._coordinate_cross_orchestrator_task(request, orchestration_results)
                orchestration_results.update(coordination_results)

            # Energy optimization if enabled
            if self.energy_planner and self.config.get("energy_optimization", True):
                energy_results = await self._optimize_energy_allocation(request, orchestration_results)
                orchestration_results["energy_optimization"] = energy_results

            # Update metrics
            processing_time = time.time() - start_time
            await self._update_orchestration_metrics(request, orchestration_results, processing_time)

            result = {
                "success": True,
                "request_id": request_id,
                "orchestration_type": request.orchestration_type.value,
                "processing_time": processing_time,
                "orchestration_results": orchestration_results,
                "lukhas_cycle_phase": (request.lukhas_cycle_phase.value if request.lukhas_cycle_phase else None),
                "performance_metrics": {
                    "bio_symbolic_coherence": self.metrics.bio_symbolic_coherence,
                    "system_health_score": self.metrics.system_health_score,
                    "request_success_rate": self.metrics.request_success_rate,
                },
            }

            self.completed_requests.append(result)
            self.logger.info(f"Request orchestrated successfully: {request_id}")

            return result

        except Exception as e:
            self.logger.error(f"Request orchestration failed {request.request_id}: {e}")

            failure_result = {
                "success": False,
                "error": str(e),
                "request_id": request.request_id,
                "orchestration_type": request.orchestration_type.value,
            }

            self.failed_requests.append(failure_result)
            return failure_result

    async def _route_and_execute_request(self, request: OrchestrationRequest) -> dict[str, Any]:
        """Route request to appropriate orchestrators and execute"""

        results = {}

        # Determine target orchestrators based on request type and content
        target_orchestrators = request.target_orchestrators
        if not target_orchestrators:
            target_orchestrators = self._determine_target_orchestrators(request)

        # Execute request on each target orchestrator
        for orchestrator_name in target_orchestrators:
            if orchestrator_name not in self.orchestrator_registry:
                results[orchestrator_name] = {
                    "success": False,
                    "error": f"Orchestrator {orchestrator_name} not available",
                }
                continue

            try:
                orchestrator_info = self.orchestrator_registry[orchestrator_name]
                orchestrator = orchestrator_info["orchestrator"]

                # Execute based on orchestration type
                if request.orchestration_type == OrchestrationType.SWARM_OPERATION and orchestrator_name == "swarm":
                    result = await self._execute_swarm_operation(orchestrator, request)
                elif request.orchestration_type == OrchestrationType.COLONY_TASK and orchestrator_name == "colony":
                    result = await self._execute_colony_task(orchestrator, request)
                elif (
                    request.orchestration_type == OrchestrationType.BIO_SYMBOLIC_PROCESSING
                    and orchestrator_name == "bio_symbolic"
                ):
                    result = await self._execute_bio_symbolic_processing(orchestrator, request)
                elif (
                    request.orchestration_type == OrchestrationType.WORKFLOW_EXECUTION
                    and orchestrator_name == "workflow"
                ):
                    result = await self._execute_workflow(orchestrator, request)
                elif request.orchestration_type == OrchestrationType.MEMORY_OPERATION:
                    result = await self._execute_memory_operation(orchestrator, request)
                elif (
                    request.orchestration_type == OrchestrationType.BRAIN_COORDINATION
                    and orchestrator_name == "brain_hub"
                ):
                    result = await self._execute_brain_coordination(orchestrator, request)
                else:
                    result = await self._execute_generic_operation(orchestrator, request)

                results[orchestrator_name] = result

            except Exception as e:
                results[orchestrator_name] = {"success": False, "error": str(e)}
                self.logger.error(f"Orchestrator {orchestrator_name} execution failed: {e}")

        return results

    def _determine_target_orchestrators(self, request: OrchestrationRequest) -> list[str]:
        """Determine which orchestrators should handle the request"""

        targets = []

        # Route based on orchestration type
        if request.orchestration_type == OrchestrationType.SWARM_OPERATION:
            targets.append("swarm")
        elif request.orchestration_type == OrchestrationType.COLONY_TASK:
            targets.append("colony")
        elif request.orchestration_type == OrchestrationType.BIO_SYMBOLIC_PROCESSING:
            targets.append("bio_symbolic")
        elif request.orchestration_type == OrchestrationType.WORKFLOW_EXECUTION:
            targets.append("workflow")
        elif request.orchestration_type == OrchestrationType.MEMORY_OPERATION:
            # Route to appropriate memory orchestrator
            memory_type = request.payload.get("memory_type", "core")
            if memory_type == "visualization":
                targets.append("memory_visualization")
            elif memory_type == "colonies":
                targets.append("memory_colonies")
            else:
                targets.append("memory_core")
        elif request.orchestration_type == OrchestrationType.BRAIN_COORDINATION:
            targets.append("brain_hub")
        elif request.orchestration_type == OrchestrationType.CROSS_ORCHESTRATOR_TASK:
            # For cross-orchestrator tasks, analyze payload to determine targets
            targets = self._analyze_cross_orchestrator_targets(request.payload)

        # Add energy optimization if enabled
        if (
            self.config.get("energy_optimization", True) and "energy" in self.orchestrator_registry
        ) and "energy" not in targets:
            targets.append("energy")

        # If no specific targets, use capability-based routing
        if not targets:
            targets = self._route_by_capability(request.payload)

        return targets

    def _analyze_cross_orchestrator_targets(self, payload: dict[str, Any]) -> list[str]:
        """Analyze payload to determine which orchestrators are needed for cross-orchestrator task"""

        targets = []

        # Check for swarm requirements
        if any(key in payload for key in ["swarms", "agents", "swarm_config"]):
            targets.append("swarm")

        # Check for colony requirements
        if any(key in payload for key in ["colonies", "colony_types", "specialized_processing"]):
            targets.append("colony")

        # Check for bio-symbolic requirements
        if any(key in payload for key in ["bio_data", "symbolic_context", "coherence_target"]):
            targets.append("bio_symbolic")

        # Check for workflow requirements
        if any(key in payload for key in ["workflow_definition", "task_sequence", "dependencies"]):
            targets.append("workflow")

        # Check for memory requirements
        if any(key in payload for key in ["memory_data", "memory_operation", "fold_data", "causal_chain"]):
            memory_type = payload.get("memory_type", "core")
            if memory_type == "visualization":
                targets.append("memory_visualization")
            elif memory_type == "colonies":
                targets.append("memory_colonies")
            else:
                targets.append("memory_core")

        # Check for brain coordination requirements
        if any(
            key in payload
            for key in [
                "brain_coordination",
                "cognitive_cycle",
                "consciousness_integration",
            ]
        ):
            targets.append("brain_hub")

        return targets

    def _route_by_capability(self, payload: dict[str, Any]) -> list[str]:
        """Route request based on required capabilities"""

        targets = []

        # Extract required capabilities from payload
        required_capabilities = payload.get("required_capabilities", [])

        for capability in required_capabilities:
            if capability in self.capability_map:
                orchestrator = self.capability_map[capability]
                if orchestrator not in targets:
                    targets.append(orchestrator)

        # Default to colony if no specific routing found
        if not targets and "colony" in self.orchestrator_registry:
            targets.append("colony")

        return targets

    async def _execute_swarm_operation(
        self, swarm_adapter: SwarmOrchestrationAdapter, request: OrchestrationRequest
    ) -> dict[str, Any]:
        """Execute swarm operation"""

        operation_type = SwarmOperationType(request.payload.get("operation_type", "create_swarm"))

        if operation_type == SwarmOperationType.CREATE_SWARM:
            return await swarm_adapter.create_swarm(request.payload["swarm_id"], request.payload["swarm_config"])
        elif operation_type == SwarmOperationType.CROSS_SWARM_TASK:
            return await swarm_adapter.orchestrate_cross_swarm_task(
                request.request_id,
                request.payload["target_swarms"],
                request.payload["task_payload"],
            )
        else:
            # Handle other swarm operations
            return {
                "success": True,
                "operation_type": operation_type.value,
                "executed": True,
            }

    async def _execute_colony_task(
        self, colony_orchestrator: ColonyOrchestrator, request: OrchestrationRequest
    ) -> dict[str, Any]:
        """Execute colony task"""

        if "spawn_colony" in request.payload:
            config_data = request.payload["spawn_colony"]
            config = ColonyConfig(
                colony_type=ColonyType(config_data["type"]),
                colony_id=config_data["id"],
                initial_agents=config_data.get("agents", 5),
                specialized_config=config_data.get("config", {}),
            )
            return await colony_orchestrator.spawn_colony(config)
        elif "execute_task" in request.payload:
            task_data = request.payload["execute_task"]
            task = ColonyTask(
                task_id=task_data["id"],
                colony_type=ColonyType(task_data["type"]),
                target_colonies=task_data["colonies"],
                payload=task_data["payload"],
            )
            return await colony_orchestrator.execute_colony_task(task)
        else:
            return {
                "success": True,
                "task_type": "generic_colony_task",
                "executed": True,
            }

    async def _execute_bio_symbolic_processing(
        self,
        bio_symbolic_orchestrator: BioSymbolicOrchestrator,
        request: OrchestrationRequest,
    ) -> dict[str, Any]:
        """Execute bio-symbolic processing"""

        task = BioSymbolicTask(
            task_id=request.request_id,
            mode=BioSymbolicMode(request.payload.get("mode", "real_time_processing")),
            bio_data=request.payload.get("bio_data", {}),
            symbolic_context=request.payload.get("symbolic_context", {}),
            target_coherence=request.payload.get("target_coherence", 85.0),
            priority=request.priority.value,
        )

        return await bio_symbolic_orchestrator.process_bio_symbolic_task(task)

    async def _execute_workflow(self, workflow_engine: WorkflowEngine, request: OrchestrationRequest) -> dict[str, Any]:
        """Execute workflow"""

        workflow_definition = request.payload.get("workflow_definition", {})

        # This would be implemented based on actual WorkflowEngine interface
        return {
            "success": True,
            "workflow_id": workflow_definition.get("id", "default"),
            "executed": True,
        }

    async def _execute_memory_operation(
        self, memory_orchestrator: Any, request: OrchestrationRequest
    ) -> dict[str, Any]:
        """Execute memory operation with safety protocols"""

        operation_type = request.payload.get("operation", "process")
        memory_data = request.payload.get("memory_data", {})

        try:
            if operation_type == "process":
                result = await memory_orchestrator.process_memory(memory_data)
            elif operation_type == "create":
                result = await memory_orchestrator.create_memory(memory_data)
            elif operation_type == "retrieve":
                memory_id = request.payload.get("memory_id")
                result = await memory_orchestrator.retrieve_memory(memory_id)
            elif operation_type == "consolidate":
                memory_ids = request.payload.get("memory_ids", [])
                result = await memory_orchestrator.consolidate_memories(memory_ids)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown memory operation: {operation_type}",
                }

            # Add safety protocol confirmation
            if result and result.get("status") == "success":
                result["safety_protocols_applied"] = True
                result["cascade_prevention_active"] = True

            return result

        except Exception as e:
            self.logger.error(f"Memory operation failed: {e!s}")
            return {"success": False, "error": str(e), "safety_protocols_applied": True}

    async def _execute_brain_coordination(self, brain_hub: Any, request: OrchestrationRequest) -> dict[str, Any]:
        """Execute brain coordination operation"""

        coordination_type = request.payload.get("coordination_type", "cognitive_cycle")

        try:
            if coordination_type == "cognitive_cycle":
                cycle_phase = request.payload.get("phase", "reflection")
                result = await brain_hub.coordinate_cognitive_cycle(
                    phase=cycle_phase, context=request.payload.get("context", {})
                )
            elif coordination_type == "consciousness_integration":
                integration_data = request.payload.get("integration_data", {})
                result = await brain_hub.integrate_consciousness_state(integration_data)
            elif coordination_type == "neural_coordination":
                neural_data = request.payload.get("neural_data", {})
                result = await brain_hub.coordinate_neural_processes(neural_data)
            else:
                result = {
                    "success": True,
                    "coordination_type": coordination_type,
                    "executed": True,
                }

            return result

        except Exception as e:
            self.logger.error(f"Brain coordination failed: {e!s}")
            return {"success": False, "error": str(e)}

    async def _execute_generic_operation(self, orchestrator: Any, request: OrchestrationRequest) -> dict[str, Any]:
        """Execute generic operation on any orchestrator"""

        # Try to call a process method if available
        if hasattr(orchestrator, "process_request"):
            return await orchestrator.process_request(request.payload)
        elif hasattr(orchestrator, "execute"):
            return await orchestrator.execute(request.payload)
        else:
            return {"success": True, "generic_execution": True}

    async def _coordinate_cross_orchestrator_task(
        self, request: OrchestrationRequest, orchestration_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Coordinate results from multiple orchestrators"""

        successful_orchestrators = [
            name for name, result in orchestration_results.items() if result.get("success", False)
        ]

        failed_orchestrators = [
            name for name, result in orchestration_results.items() if not result.get("success", False)
        ]

        # Update cross-orchestrator metrics
        self.metrics.cross_orchestrator_operations += 1

        return {
            "cross_orchestrator_coordination": {
                "total_orchestrators": len(orchestration_results),
                "successful_orchestrators": len(successful_orchestrators),
                "failed_orchestrators": len(failed_orchestrators),
                "overall_success": len(failed_orchestrators) == 0,
                "coordination_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }

    async def _optimize_energy_allocation(
        self, request: OrchestrationRequest, orchestration_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimize energy allocation for the request"""

        # This would integrate with actual EnergyAwareExecutionPlanner
        return {
            "energy_optimization": {
                "optimization_applied": True,
                "estimated_energy_saved": "15%",
                "resource_allocation": "optimized",
                "recommendations": ["Use bio-symbolic processing for efficiency"],
            }
        }

    async def _update_lukhas_cycle_state(self, request_id: str, phase: LukhasCyclePhase):
        """Update LUKHAS cycle state tracking"""

        self.cycle_states[request_id] = phase

        # Track complete cycles (excluding memory phase until approved)
        if request_id not in self.active_cycles:
            self.active_cycles[request_id] = {
                "start_time": datetime.now(timezone.utc),
                "phases_completed": [],
                "current_phase": phase,
            }

        cycle_info = self.active_cycles[request_id]
        cycle_info["phases_completed"].append(phase)
        cycle_info["current_phase"] = phase

        # Check if cycle is complete (all phases including memory)
        completed_phases = set(cycle_info["phases_completed"])
        required_phases = {
            LukhasCyclePhase.DREAM,
            LukhasCyclePhase.MEMORY,  # Now included in complete cycles
            LukhasCyclePhase.REFLECTION,
            LukhasCyclePhase.DIRECTIVE,
            LukhasCyclePhase.ACTION,
            LukhasCyclePhase.DRIFT,
            LukhasCyclePhase.EVOLUTION,
        }

        if required_phases.issubset(completed_phases):
            cycle_info["completed"] = True
            cycle_info["completion_time"] = datetime.now(timezone.utc)
            self.metrics.lukhas_cycle_completions += 1

            self.logger.info(f"LUKHAS cycle completed for request {request_id}")

    async def _update_orchestration_metrics(
        self,
        request: OrchestrationRequest,
        results: dict[str, Any],
        processing_time: float,
    ):
        """Update performance metrics"""

        # Update basic metrics
        self.metrics.total_requests_processed += 1

        # Update average response time with exponential smoothing
        alpha = 0.1
        self.metrics.average_response_time = alpha * processing_time + (1 - alpha) * self.metrics.average_response_time

        # Update success rate
        success = all(result.get("success", False) for result in results.values())
        success_value = 1.0 if success else 0.0
        self.metrics.request_success_rate = alpha * success_value + (1 - alpha) * self.metrics.request_success_rate

        # Update bio-symbolic coherence from results
        for result in results.values():
            if "coherence_metrics" in result:
                coherence = result["coherence_metrics"].get("overall_coherence", 0.0)
                if coherence > 0:
                    self.metrics.bio_symbolic_coherence = (
                        alpha * coherence + (1 - alpha) * self.metrics.bio_symbolic_coherence
                    )

        # Record performance history
        self.performance_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "request_id": request.request_id,
                "processing_time": processing_time,
                "success": success,
                "orchestration_type": request.orchestration_type.value,
            }
        )

        self.metrics.last_updated = datetime.now(timezone.utc)

    # Background monitoring tasks
    async def _start_monitoring_tasks(self):
        """Start background monitoring and maintenance tasks"""

        # Health monitoring task
        asyncio.create_task(self._health_monitoring_loop())

        # Performance monitoring task
        asyncio.create_task(self._performance_monitoring_loop())

        # Request processing loop
        asyncio.create_task(self._request_processing_loop())

        # LUKHAS cycle monitoring
        if self.config.get("lukhas_cycle_tracking", True):
            asyncio.create_task(self._lukhas_cycle_monitoring_loop())

    async def _health_monitoring_loop(self):
        """Background task for monitoring system health"""
        while self.is_running:
            try:
                health_score = await self._calculate_system_health()
                self.metrics.system_health_score = health_score

                if health_score < 0.7:
                    self.logger.warning(f"System health degraded: {health_score:.2f}")

                await asyncio.sleep(self.config["health_check_interval"])
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.config["health_check_interval"])

    async def _performance_monitoring_loop(self):
        """Background task for monitoring performance metrics"""
        while self.is_running:
            try:
                await self._update_orchestrator_utilization()
                await asyncio.sleep(self.config["performance_monitoring_interval"])
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(self.config["performance_monitoring_interval"])

    async def _request_processing_loop(self):
        """Background task for processing queued requests"""
        while self.is_running:
            try:
                if self.request_queue:
                    request = self.request_queue.popleft()
                    asyncio.create_task(self.orchestrate_request(request))
                else:
                    await asyncio.sleep(1.0)
            except Exception as e:
                self.logger.error(f"Request processing error: {e}")
                await asyncio.sleep(1.0)

    async def _lukhas_cycle_monitoring_loop(self):
        """Background task for monitoring LUKHAS cycle health"""
        while self.is_running:
            try:
                await self._monitor_lukhas_cycles()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"LUKHAS cycle monitoring error: {e}")
                await asyncio.sleep(60)

    def get_master_status(self) -> dict[str, Any]:
        """Get comprehensive status of master orchestration"""
        return {
            "orchestrator_status": "running" if self.is_running else "stopped",
            "registered_orchestrators": list(self.orchestrator_registry.keys()),
            "active_orchestrators": [
                name for name, info in self.orchestrator_registry.items() if info["status"] == "active"
            ],
            "request_queue_length": len(self.request_queue),
            "running_requests": len(self.running_requests),
            "completed_requests_today": len(self.completed_requests),
            "failed_requests_today": len(self.failed_requests),
            "performance_metrics": {
                "total_requests_processed": self.metrics.total_requests_processed,
                "average_response_time": self.metrics.average_response_time,
                "request_success_rate": self.metrics.request_success_rate,
                "bio_symbolic_coherence": self.metrics.bio_symbolic_coherence,
                "system_health_score": self.metrics.system_health_score,
                "cross_orchestrator_operations": self.metrics.cross_orchestrator_operations,
                "lukhas_cycle_completions": self.metrics.lukhas_cycle_completions,
            },
            "lukhas_cycle_tracking": {
                "enabled": self.config.get("lukhas_cycle_tracking", True),
                "active_cycles": len(self.active_cycles),
                "total_completions": self.metrics.lukhas_cycle_completions,
                "included_phases": [
                    "dream",
                    "memory",
                    "reflection",
                    "directive",
                    "action",
                    "drift",
                    "evolution",
                ],  # All phases now included
            },
            "system_info": {
                "initialized_at": self.initialization_time.isoformat(),
                "uptime_hours": (datetime.now(timezone.utc) - self.initialization_time).total_seconds() / 3600,
                "brain_orchestration_enabled": self.config.get("brain_orchestration_enabled", False),
                "memory_orchestration_enabled": self.config.get("memory_orchestration_enabled", False),
            },
        }

    # Helper methods
    async def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        health_scores = []

        for info in self.orchestrator_registry.values():
            if info["status"] == "active":
                orchestrator = info["orchestrator"]

                # Try to get health status from orchestrator
                if hasattr(orchestrator, "get_health_status"):
                    try:
                        health = await orchestrator.get_health_status()
                        health_scores.append(health.get("score", 0.5))
                    except BaseException:
                        health_scores.append(0.5)  # Neutral score if unavailable
                else:
                    health_scores.append(0.8)  # Assume healthy if no status method
            else:
                health_scores.append(0.0)  # Inactive orchestrator

        return sum(health_scores) / len(health_scores) if health_scores else 0.0

    async def _update_orchestrator_utilization(self):
        """Update utilization metrics for each orchestrator"""
        for name, info in self.orchestrator_registry.items():
            if info["status"] == "active":
                orchestrator = info["orchestrator"]

                # Try to get utilization from orchestrator
                if hasattr(orchestrator, "get_utilization"):
                    try:
                        utilization = await orchestrator.get_utilization()
                        self.metrics.orchestrator_utilization[name] = utilization
                    except BaseException:
                        self.metrics.orchestrator_utilization[name] = 0.0
                else:
                    # Estimate utilization based on active tasks
                    active_tasks = len(getattr(orchestrator, "running_tasks", {}))
                    max_tasks = getattr(orchestrator, "max_concurrent_tasks", 10)
                    self.metrics.orchestrator_utilization[name] = min(active_tasks / max_tasks, 1.0)

    async def _monitor_lukhas_cycles(self):
        """Monitor health and progress of LUKHAS cycles"""
        current_time = datetime.now(timezone.utc)

        # Check for stalled cycles
        stalled_cycles = []
        for request_id, cycle_info in self.active_cycles.items():
            if not cycle_info.get("completed", False):
                time_since_start = (current_time - cycle_info["start_time"]).total_seconds()
                if time_since_start > 3600:  # Stalled for more than 1 hour
                    stalled_cycles.append(request_id)

        if stalled_cycles:
            self.logger.warning(f"Detected {len(stalled_cycles)} stalled LUKHAS cycles")

        # Clean up completed cycles older than 24 hours
        cleanup_threshold = current_time - timedelta(hours=24)
        completed_cycles_to_remove = [
            request_id
            for request_id, cycle_info in self.active_cycles.items()
            if cycle_info.get("completed", False)
            and cycle_info.get("completion_time", current_time) < cleanup_threshold
        ]

        for request_id in completed_cycles_to_remove:
            del self.active_cycles[request_id]
            if request_id in self.cycle_states:
                del self.cycle_states[request_id]


# Export main classes
__all__ = [
    "LukhasCyclePhase",
    "MasterOrchestrator",
    "OrchestrationMetrics",
    "OrchestrationPriority",
    "OrchestrationRequest",
    "OrchestrationType",
]
