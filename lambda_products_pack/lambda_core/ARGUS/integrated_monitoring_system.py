#!/usr/bin/env python3
"""
Integrated Monitoring System
============================
Central integration hub that connects all monitoring components with the existing
SignalBus and HomeostasisController to create a unified monitoring ecosystem.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from orchestration.signals.signal_bus import Signal, SignalBus, SignalType

try:
    from orchestration.signals.homeostasis_controller import (
        HomeostasisController,
        HomeostasisState,
    )
except Exception:
    # Provide minimal stubs if controller is unavailable
    class HomeostasisState(Enum):
        NORMAL = "normal"

    class HomeostasisController:
        def register_state_callback(self, cb):
            return None


# Import our monitoring components with flexible fallbacks
try:
    from monitoring.endocrine_observability_engine import (
        EndocrineObservabilityEngine,
        EndocrineSnapshot,
        PlasticityEvent,
        create_endocrine_observability_engine,
    )
except Exception:
    try:
        from .endocrine_observability_engine import (
            EndocrineObservabilityEngine,
            EndocrineSnapshot,
            PlasticityEvent,
            create_endocrine_observability_engine,
        )
    except Exception:
        EndocrineObservabilityEngine = object  # type: ignore
        EndocrineSnapshot = object  # type: ignore
        PlasticityEvent = object  # type: ignore

        def create_endocrine_observability_engine(*args, **kwargs):  # type: ignore
            class _Dummy:
                async def initialize(self):
                    return True

                def get_current_state(self):
                    return None

                async def start_monitoring(self):
                    return True

                async def stop_monitoring(self):
                    return True

            return _Dummy()


try:
    from monitoring.plasticity_trigger_manager import (
        AdaptationPlan,
        PlasticityTriggerManager,
    )
except Exception:
    try:
        from .plasticity_trigger_manager import AdaptationPlan, PlasticityTriggerManager
    except Exception:

        class PlasticityTriggerManager:  # type: ignore
            def __init__(self, *_, **__):
                pass

            def get_adaptation_statistics(self):
                return {"total_adaptations": 0, "success_rates": {}}

        @dataclass
        class AdaptationPlan:  # type: ignore
            rule: Any = None


try:
    from monitoring.bio_symbolic_coherence_monitor import (
        BioSymbolicCoherenceMonitor,
        CoherenceReport,
        create_bio_symbolic_coherence_monitor,
    )
except Exception:
    try:
        from .bio_symbolic_coherence_monitor import (
            BioSymbolicCoherenceMonitor,
            CoherenceReport,
            create_bio_symbolic_coherence_monitor,
        )
    except Exception:
        BioSymbolicCoherenceMonitor = object  # type: ignore
        CoherenceReport = object  # type: ignore

        def create_bio_symbolic_coherence_monitor(*args, **kwargs):  # type: ignore
            class _Dummy:
                async def update_bio_system_state(self, *_a, **_k):
                    return True

                async def update_symbolic_system_state(self, *_a, **_k):
                    return True

                def get_current_coherence(self):
                    class _R:
                        overall_coherence = 0.0
                        stability_index = 0.0

                    return _R()

                async def initialize(self):
                    return True

            return _Dummy()


try:
    from monitoring.adaptive_metrics_collector import (
        AdaptiveMetricsCollector,
        MetricContext,
        MetricType,
        create_adaptive_metrics_collector,
    )
except Exception:
    try:
        from .adaptive_metrics_collector import (
            AdaptiveMetricsCollector,
            MetricContext,
            MetricType,
            create_adaptive_metrics_collector,
        )
    except Exception:
        AdaptiveMetricsCollector = object  # type: ignore

        class MetricContext(Enum):  # type: ignore
            NORMAL_OPERATION = "normal_operation"

        class MetricType(Enum):  # type: ignore
            RESPONSE_TIME = "response_time"

        def create_adaptive_metrics_collector(*args, **kwargs):  # type: ignore
            class _Dummy:
                async def initialize(self):
                    return True

                async def start_collection(self):
                    return True

                async def stop_collection(self):
                    return True

                def get_collection_statistics(self):
                    return {"is_collecting": True}

                def get_current_metrics(self):
                    return {
                        "response_time": 0.0,
                        "cpu_utilization": 0.0,
                        "decision_confidence": 0.0,
                        "communication_clarity": 0.0,
                        "attention_focus": 0.0,
                    }

                def update_endocrine_state(self, *_a, **_k):
                    return None

            return _Dummy()


try:
    from monitoring.hormone_driven_dashboard import (
        DashboardMode,
        HormoneDrivenDashboard,
        create_hormone_driven_dashboard,
    )
except Exception:
    try:
        from .hormone_driven_dashboard import (
            DashboardMode,
            HormoneDrivenDashboard,
            create_hormone_driven_dashboard,
        )
    except Exception:
        HormoneDrivenDashboard = object  # type: ignore

        class DashboardMode(Enum):  # type: ignore
            BASIC = "basic"

        def create_hormone_driven_dashboard(*args, **kwargs):  # type: ignore
            class _Dummy:
                async def initialize(self, *_a, **_k):
                    return True

                async def start_dashboard(self):
                    return True

                async def stop_dashboard(self):
                    return True

            return _Dummy()


try:
    from monitoring.neuroplastic_learning_orchestrator import (
        LearningPhase,
        NeuroplasticLearningOrchestrator,
        create_neuroplastic_learning_orchestrator,
    )
except Exception:
    try:
        from .neuroplastic_learning_orchestrator import (
            LearningPhase,
            NeuroplasticLearningOrchestrator,
            create_neuroplastic_learning_orchestrator,
        )
    except Exception:

        class LearningPhase(Enum):  # type: ignore
            OBSERVATION = "observation"

        def create_neuroplastic_learning_orchestrator(*args, **kwargs):  # type: ignore
            from monitoring.neuroplastic_learning_orchestrator import (
                NeuroplasticLearningOrchestrator as _N,
            )

            return _N(*args, **kwargs)

        NeuroplasticLearningOrchestrator = None  # type: ignore

logger = structlog.get_logger(__name__)


class IntegrationState(Enum):
    """States of the integrated monitoring system"""

    INITIALIZING = "initializing"
    STARTING = "starting"
    ACTIVE = "active"
    LEARNING = "learning"
    ADAPTING = "adapting"
    STABILIZING = "stabilizing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class MonitoringLevel(Enum):
    """Levels of monitoring intensity"""

    MINIMAL = "minimal"  # Basic system metrics only
    STANDARD = "standard"  # Normal monitoring
    INTENSIVE = "intensive"  # High-frequency monitoring
    MAXIMUM = "maximum"  # All systems at full capacity


@dataclass
class SystemHealthMetrics:
    """Overall system health metrics"""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    overall_health: float = 0.0
    bio_symbolic_coherence: float = 0.0
    system_stability: float = 0.0
    adaptation_effectiveness: float = 0.0
    learning_progress: float = 0.0

    # Component health
    endocrine_health: float = 0.0
    metrics_health: float = 0.0
    plasticity_health: float = 0.0
    coherence_health: float = 0.0

    # Performance indicators
    response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    resource_utilization: float = 0.0

    # Predictive indicators
    predicted_stability_1h: float = 0.0
    predicted_performance_1h: float = 0.0
    risk_level: str = "low"


class IntegratedMonitoringSystem:
    """
    Central hub that integrates all monitoring components to create a unified
    biological-inspired monitoring and adaptation system.
    """

    def __init__(
        self,
        signal_bus: Optional[SignalBus] = None,
        config: Optional[Dict[str, Any]] = None,
        data_dir: str = "data/integrated_monitoring",
    ):
        self.signal_bus = signal_bus or SignalBus()
        self.config = config or {}
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # System state
        self.state = IntegrationState.INITIALIZING
        self.monitoring_level = MonitoringLevel.STANDARD
        self.is_running = False

        # Core components (will be initialized)
        self.endocrine_engine = None
        self.plasticity_manager = None
        self.coherence_monitor = None
        self.metrics_collector = None
        self.dashboard = None
        self.learning_orchestrator = None

        # Integration with existing systems
        self.homeostasis_controller = None
        self.existing_systems_connected = False

        # System health and performance tracking
        self.health_history = deque(maxlen=1000)
        self.performance_baselines = {}
        self.system_alerts = {}

        # Cross-component coordination
        self.component_states = {}
        self.cross_component_correlations = defaultdict(dict)
        self.unified_insights = []

        # Signal routing and processing
        self.signal_handlers = defaultdict(list)
        self.signal_history = deque(maxlen=5000)

        # Configuration
        self.auto_adaptation_enabled = self.config.get("auto_adaptation", True)
        self.learning_enabled = self.config.get("learning_enabled", True)
        self.dashboard_enabled = self.config.get("dashboard_enabled", True)
        self.health_check_interval = self.config.get("health_check_interval", 30.0)

        logger.info(
            "IntegratedMonitoringSystem initialized",
            data_dir=str(self.data_dir),
            auto_adaptation=self.auto_adaptation_enabled,
            learning_enabled=self.learning_enabled,
        )

    async def initialize(self):
        """Initialize all monitoring components and integrate with existing systems"""

        self.state = IntegrationState.INITIALIZING
        logger.info("Initializing integrated monitoring system")

        try:
            # Initialize individual components
            await self._initialize_monitoring_components()

            # Connect to existing systems
            await self._connect_existing_systems()

            # Set up cross-component integration
            await self._setup_cross_component_integration()

            # Register signal handlers
            self._register_signal_handlers()

            # Load historical data and baselines
            await self._load_system_baselines()

            logger.info("Integrated monitoring system initialized successfully")

        except Exception as e:
            self.state = IntegrationState.ERROR
            logger.error(
                "Failed to initialize integrated monitoring system", error=str(e)
            )
            raise

    async def _initialize_monitoring_components(self):
        """Initialize all monitoring components"""

        # Create endocrine observability engine
        self.endocrine_engine = create_endocrine_observability_engine(
            self.signal_bus, self.config.get("endocrine_config", {})
        )
        await self.endocrine_engine.initialize()

        # Create plasticity trigger manager
        self.plasticity_manager = PlasticityTriggerManager(
            self.config.get("plasticity_config", {})
        )

        # Create bio-symbolic coherence monitor
        self.coherence_monitor = create_bio_symbolic_coherence_monitor(
            self.signal_bus, self.config.get("coherence_config", {})
        )

        # Create adaptive metrics collector
        self.metrics_collector = create_adaptive_metrics_collector(
            self.signal_bus, self.config.get("metrics_config", {})
        )

        # Create hormone-driven dashboard
        if self.dashboard_enabled:
            self.dashboard = create_hormone_driven_dashboard(
                self.signal_bus, self.config.get("dashboard_config", {})
            )

        # Create neuroplastic learning orchestrator
        if self.learning_enabled:
            self.learning_orchestrator = create_neuroplastic_learning_orchestrator(
                self.signal_bus, self.config.get("learning_config", {})
            )

        # Initialize cross-connections between components
        if self.dashboard:
            await self.dashboard.initialize(
                self.endocrine_engine,
                self.metrics_collector,
                self.coherence_monitor,
                self.plasticity_manager,
            )

        if self.learning_orchestrator:
            await self.learning_orchestrator.initialize(
                self.endocrine_engine,
                self.plasticity_manager,
                self.metrics_collector,
                self.coherence_monitor,
                self.dashboard,
            )

        logger.info("All monitoring components initialized")

    async def _connect_existing_systems(self):
        """Connect to existing LUKHAS systems"""

        try:
            # Connect to HomeostasisController
            try:
                # Prefer passing the shared bus when supported
                self.homeostasis_controller = HomeostasisController(self.signal_bus)  # type: ignore[arg-type]
            except TypeError:
                # Fallback to no-arg constructor
                self.homeostasis_controller = HomeostasisController()

            # Register for homeostasis state changes
            self.homeostasis_controller.register_state_callback(
                self._on_homeostasis_change
            )

            self.existing_systems_connected = True
            logger.info("Connected to existing LUKHAS systems")

        except Exception as e:
            logger.warning("Could not connect to all existing systems", error=str(e))
            # Continue without existing systems

    async def _setup_cross_component_integration(self):
        """Set up integration between monitoring components"""

        # Set up data flow between components
        if self.endocrine_engine and self.metrics_collector:
            # Update metrics collector with endocrine state
            current_state = self.endocrine_engine.get_current_state()
            if current_state:
                self.metrics_collector.update_endocrine_state(current_state)

        if self.coherence_monitor and self.endocrine_engine:
            # Update coherence monitor with endocrine data
            current_state = self.endocrine_engine.get_current_state()
            if current_state:
                await self.coherence_monitor.update_bio_system_state(current_state)

        # Set up cross-component correlation tracking
        self._setup_correlation_tracking()

        logger.info("Cross-component integration configured")

    async def _load_system_baselines(self):
        """Load or initialize performance/coherence baselines.

        This is a lightweight, non-blocking stub to quiet initialization warnings
        when no baseline file exists. It seeds sensible defaults.
        """
        try:
            # Seed minimal baselines if none exist yet
            if not self.performance_baselines:
                self.performance_baselines = {
                    "response_time_target": 0.2,  # seconds
                    "cpu_utilization_target": 0.75,  # 75%
                    "coherence_target": 0.8,
                    "adaptation_success_target": 0.6,
                }
            return True
        except Exception as e:
            logger.warning("Baseline initialization skipped", error=str(e))
            return False

    def _setup_correlation_tracking(self):
        """Set up correlation tracking between components"""

        # Define which components should correlate with each other
        correlation_pairs = [
            ("endocrine_engine", "coherence_monitor"),
            ("endocrine_engine", "metrics_collector"),
            ("coherence_monitor", "plasticity_manager"),
            ("metrics_collector", "learning_orchestrator"),
        ]

        for comp1, comp2 in correlation_pairs:
            self.cross_component_correlations[comp1][comp2] = 0.0
            self.cross_component_correlations[comp2][comp1] = 0.0

    def _register_signal_handlers(self):
        """Register handlers for different signal types"""

        # Homeostasis signals
        self.signal_handlers[SignalType.HOMEOSTASIS].append(
            self._handle_homeostasis_signal
        )

        # Adaptation signals
        self.signal_handlers[SignalType.ADAPTATION].append(
            self._handle_adaptation_signal
        )

        # Alert signals
        self.signal_handlers[SignalType.ALERT].append(self._handle_alert_signal)

        # Coherence signals
        self.signal_handlers[SignalType.COHERENCE].append(self._handle_coherence_signal)

        # Metric update signals
        self.signal_handlers[SignalType.METRIC_UPDATE].append(
            self._handle_metric_update_signal
        )

        # Learning phase signals
        self.signal_handlers[SignalType.LEARNING_PHASE].append(
            self._handle_learning_phase_signal
        )

        # Subscribe to signal bus
        for signal_type, handlers in self.signal_handlers.items():
            for handler in handlers:
                self.signal_bus.subscribe(signal_type, handler)

    async def start_monitoring(self):
        """Start the integrated monitoring system"""

        if self.is_running:
            logger.warning("Monitoring system already running")
            return

        self.state = IntegrationState.STARTING
        self.is_running = True
        logger.info("Starting integrated monitoring system")

        try:
            # Start individual components
            await self._start_monitoring_components()

            # Start integration management tasks
            asyncio.create_task(self._system_health_monitoring_loop())
            asyncio.create_task(self._cross_component_coordination_loop())
            asyncio.create_task(self._unified_insights_generation_loop())
            asyncio.create_task(self._system_optimization_loop())

            self.state = IntegrationState.ACTIVE
            logger.info("Integrated monitoring system started successfully")

        except Exception as e:
            self.state = IntegrationState.ERROR
            logger.error("Failed to start integrated monitoring system", error=str(e))
            raise

    async def _start_monitoring_components(self):
        """Start all monitoring components"""

        # Start endocrine observability
        if self.endocrine_engine:
            await self.endocrine_engine.start_monitoring()

        # Start metrics collection
        if self.metrics_collector:
            await self.metrics_collector.start_collection()

        # Start dashboard
        if self.dashboard:
            await self.dashboard.start_dashboard()

        # Start learning orchestrator
        if self.learning_orchestrator and self.learning_enabled:
            await self.learning_orchestrator.start_learning()

        logger.info("All monitoring components started")

    async def stop_monitoring(self):
        """Stop the integrated monitoring system"""

        self.state = IntegrationState.STOPPING
        self.is_running = False
        logger.info("Stopping integrated monitoring system")

        try:
            # Stop individual components
            if self.endocrine_engine:
                await self.endocrine_engine.stop_monitoring()

            if self.metrics_collector:
                await self.metrics_collector.stop_collection()

            if self.dashboard:
                await self.dashboard.stop_dashboard()

            if self.learning_orchestrator:
                await self.learning_orchestrator.stop_learning()

            # Save final state
            await self._save_system_state()

            self.state = IntegrationState.STOPPED
            logger.info("Integrated monitoring system stopped")

        except Exception as e:
            self.state = IntegrationState.ERROR
            logger.error("Error stopping integrated monitoring system", error=str(e))

    async def _system_health_monitoring_loop(self):
        """Monitor overall system health"""

        while self.is_running:
            try:
                # Calculate system health metrics
                health_metrics = await self._calculate_system_health()
                self.health_history.append(health_metrics)

                # Check for system alerts
                await self._check_system_alerts(health_metrics)

                # Emit health signal
                await self._emit_health_signal(health_metrics)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error("Error in system health monitoring", error=str(e))
                await asyncio.sleep(60.0)

    async def _calculate_system_health(self) -> SystemHealthMetrics:
        """Calculate comprehensive system health metrics"""

        health = SystemHealthMetrics()

        # Get component health metrics
        if self.endocrine_engine:
            current_state = self.endocrine_engine.get_current_state()
            if current_state:
                health.endocrine_health = current_state.coherence_score

        if self.coherence_monitor:
            coherence_report = self.coherence_monitor.get_current_coherence()
            if coherence_report:
                health.bio_symbolic_coherence = coherence_report.overall_coherence
                health.coherence_health = coherence_report.stability_index

        if self.metrics_collector:
            collector_stats = self.metrics_collector.get_collection_statistics()
            health.metrics_health = 1.0 if collector_stats["is_collecting"] else 0.0

            current_metrics = self.metrics_collector.get_current_metrics()
            health.response_time = current_metrics.get("response_time", 0.0)
            health.resource_utilization = current_metrics.get("cpu_utilization", 0.0)

        if self.plasticity_manager:
            adaptation_stats = self.plasticity_manager.get_adaptation_statistics()
            total_adaptations = adaptation_stats["total_adaptations"]
            if total_adaptations > 0:
                success_rates = adaptation_stats["success_rates"]
                avg_success = (
                    sum(success_rates.values()) / len(success_rates)
                    if success_rates
                    else 0.0
                )
                health.adaptation_effectiveness = avg_success
                health.plasticity_health = avg_success

        if self.learning_orchestrator:
            learning_status = self.learning_orchestrator.get_learning_status()
            if asyncio.iscoroutine(learning_status["learning_progress"]):
                health.learning_progress = await learning_status["learning_progress"]
            else:
                health.learning_progress = learning_status.get("learning_progress", 0.0)

        # Calculate overall health
        component_healths = [
            health.endocrine_health,
            health.coherence_health,
            health.metrics_health,
            health.plasticity_health,
        ]

        health.overall_health = sum(h for h in component_healths if h > 0) / len(
            [h for h in component_healths if h > 0]
        )

        # Calculate system stability
        if len(self.health_history) >= 10:
            recent_health = [h.overall_health for h in list(self.health_history)[-10:]]
            variance = sum(
                (h - health.overall_health) ** 2 for h in recent_health
            ) / len(recent_health)
            health.system_stability = 1.0 - min(1.0, variance * 2.0)
        else:
            health.system_stability = 0.5

        # Predictive indicators (simplified)
        health.predicted_stability_1h = (
            health.system_stability * 0.9
        )  # Assume slight degradation
        health.predicted_performance_1h = health.overall_health * 0.95

        # Risk assessment
        if health.overall_health < 0.3:
            health.risk_level = "critical"
        elif health.overall_health < 0.5:
            health.risk_level = "high"
        elif health.overall_health < 0.7:
            health.risk_level = "medium"
        else:
            health.risk_level = "low"

        return health

    async def _cross_component_coordination_loop(self):
        """Coordinate data flow between components"""

        while self.is_running:
            try:
                # Update cross-component data flows
                await self._update_cross_component_data()

                # Calculate cross-component correlations
                await self._calculate_cross_component_correlations()

                # Optimize monitoring based on system state
                await self._optimize_monitoring_configuration()

                await asyncio.sleep(15.0)  # Coordinate every 15 seconds

            except Exception as e:
                logger.error("Error in cross-component coordination", error=str(e))
                await asyncio.sleep(30.0)

    async def _update_cross_component_data(self):
        """Update data flow between components"""

        # Endocrine to metrics collector
        if self.endocrine_engine and self.metrics_collector:
            current_state = self.endocrine_engine.get_current_state()
            if current_state:
                self.metrics_collector.update_endocrine_state(current_state)

        # Endocrine to coherence monitor
        if self.endocrine_engine and self.coherence_monitor:
            current_state = self.endocrine_engine.get_current_state()
            if current_state:
                await self.coherence_monitor.update_bio_system_state(current_state)

        # Metrics to coherence monitor
        if self.metrics_collector and self.coherence_monitor:
            current_metrics = self.metrics_collector.get_current_metrics()
            if current_metrics:
                symbolic_data = {
                    "glyph_processing_rate": current_metrics.get("response_time", 0.0),
                    "consciousness_level": current_metrics.get("attention_focus", 0.0),
                    "decision_making_active": current_metrics.get(
                        "decision_confidence", 0.0
                    )
                    > 0.7,
                    "memory_operations": 10,  # Mock value
                    "reasoning_depth": current_metrics.get("decision_confidence", 0.0),
                    "symbolic_complexity": current_metrics.get(
                        "communication_clarity", 0.0
                    ),
                    "processing_load": current_metrics.get("cpu_utilization", 0.0),
                }
                await self.coherence_monitor.update_symbolic_system_state(symbolic_data)

    async def _unified_insights_generation_loop(self):
        """Generate unified insights from all components"""

        while self.is_running:
            try:
                # Collect insights from all components
                insights = await self._collect_unified_insights()

                # Merge and deduplicate insights
                unified_insight = await self._merge_insights(insights)

                if unified_insight:
                    self.unified_insights.append(unified_insight)

                    # Emit unified insight signal
                    await self._emit_insight_signal(unified_insight)

                # Limit insights history
                if len(self.unified_insights) > 100:
                    self.unified_insights = self.unified_insights[-100:]

                await asyncio.sleep(120.0)  # Generate insights every 2 minutes

            except Exception as e:
                logger.error("Error in unified insights generation", error=str(e))
                await asyncio.sleep(300.0)

    async def _system_optimization_loop(self):
        """Optimize system configuration based on performance"""

        while self.is_running:
            try:
                # Analyze system performance
                performance_analysis = await self._analyze_system_performance()

                # Adjust monitoring level if needed
                await self._adjust_monitoring_level(performance_analysis)

                # Optimize component configurations
                await self._optimize_component_configurations(performance_analysis)

                await asyncio.sleep(300.0)  # Optimize every 5 minutes

            except Exception as e:
                logger.error("Error in system optimization", error=str(e))
                await asyncio.sleep(600.0)

    # Signal handlers
    async def _handle_homeostasis_signal(self, signal: Signal):
        """Handle homeostasis-related signals"""
        self.signal_history.append(signal)

        homeostasis_state = signal.metadata.get("state")
        if homeostasis_state:
            logger.info("Homeostasis state change detected", state=homeostasis_state)

            # Adjust monitoring based on homeostasis state
            if homeostasis_state in ["stressed", "critical"]:
                await self._set_monitoring_level(MonitoringLevel.INTENSIVE)
            elif homeostasis_state == "recovering":
                await self._set_monitoring_level(MonitoringLevel.STANDARD)

    async def _handle_adaptation_signal(self, signal: Signal):
        """Handle adaptation-related signals"""
        self.signal_history.append(signal)

        logger.info(
            "Adaptation signal received",
            trigger_type=signal.metadata.get("trigger_type"),
            success=signal.metadata.get("success"),
        )

    async def _handle_alert_signal(self, signal: Signal):
        """Handle alert signals"""
        self.signal_history.append(signal)

        alert_type = signal.metadata.get("alert_type")
        if alert_type == "critical_coherence":
            logger.critical("Critical coherence alert received")
            # Take emergency measures
            await self._handle_critical_coherence_alert(signal)

    async def _handle_coherence_signal(self, signal: Signal):
        """Handle coherence monitoring signals"""
        self.signal_history.append(signal)

        coherence_level = signal.level
        if coherence_level < 0.5:
            logger.warning("Low coherence detected", level=coherence_level)

    async def _handle_metric_update_signal(self, signal: Signal):
        """Handle metric update signals"""
        # Don't store all metric updates in history (too many)
        # Just process for real-time decisions

        metric_name = signal.metadata.get("metric_name")
        anomaly_score = signal.metadata.get("anomaly_score", 0.0)

        if anomaly_score > 0.8:
            logger.warning(
                "High anomaly detected in metric",
                metric=metric_name,
                anomaly_score=anomaly_score,
            )

    async def _handle_learning_phase_signal(self, signal: Signal):
        """Handle learning phase change signals"""
        self.signal_history.append(signal)

        new_phase = signal.metadata.get("new_phase")
        if new_phase == "exploration":
            # Increase monitoring during exploration
            await self._set_monitoring_level(MonitoringLevel.INTENSIVE)
        elif new_phase == "consolidation":
            # Normal monitoring during consolidation
            await self._set_monitoring_level(MonitoringLevel.STANDARD)

    # Callback for homeostasis controller
    async def _on_homeostasis_change(
        self, old_state: HomeostasisState, new_state: HomeostasisState
    ):
        """Called when homeostasis state changes"""

        logger.info(
            "Homeostasis state changed",
            old_state=old_state.value if old_state else None,
            new_state=new_state.value,
        )

        # Emit signal for other components
        signal = Signal(
            name=SignalType.HOMEOSTASIS,
            source="integrated_monitoring",
            level=0.8,
            metadata={
                "old_state": old_state.value if old_state else None,
                "new_state": new_state.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.signal_bus.publish(signal)

    # Public API methods
    async def set_monitoring_level(self, level: MonitoringLevel):
        """Set the monitoring intensity level"""
        await self._set_monitoring_level(level)

    async def _set_monitoring_level(self, level: MonitoringLevel):
        """Internal method to set monitoring level"""
        if self.monitoring_level != level:
            old_level = self.monitoring_level
            self.monitoring_level = level

            logger.info(
                "Monitoring level changed",
                old_level=old_level.value,
                new_level=level.value,
            )

            # Adjust component configurations based on level
            await self._apply_monitoring_level_configuration(level)

    async def _apply_monitoring_level_configuration(self, level: MonitoringLevel):
        """Apply monitoring level to all components"""

        level_configs = {
            MonitoringLevel.MINIMAL: {
                "endocrine_interval": 30.0,
                "metrics_interval": 10.0,
                "health_check_interval": 60.0,
            },
            MonitoringLevel.STANDARD: {
                "endocrine_interval": 10.0,
                "metrics_interval": 5.0,
                "health_check_interval": 30.0,
            },
            MonitoringLevel.INTENSIVE: {
                "endocrine_interval": 2.0,
                "metrics_interval": 1.0,
                "health_check_interval": 10.0,
            },
            MonitoringLevel.MAXIMUM: {
                "endocrine_interval": 1.0,
                "metrics_interval": 0.5,
                "health_check_interval": 5.0,
            },
        }

        config = level_configs.get(level, level_configs[MonitoringLevel.STANDARD])

        # Apply configuration to components
        if self.endocrine_engine:
            self.endocrine_engine.monitoring_interval = config["endocrine_interval"]

        self.health_check_interval = config["health_check_interval"]

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""

        latest_health = self.health_history[-1] if self.health_history else None

        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "monitoring_level": self.monitoring_level.value,
            "components": {
                "endocrine_engine": self.endocrine_engine is not None,
                "plasticity_manager": self.plasticity_manager is not None,
                "coherence_monitor": self.coherence_monitor is not None,
                "metrics_collector": self.metrics_collector is not None,
                "dashboard": self.dashboard is not None,
                "learning_orchestrator": self.learning_orchestrator is not None,
            },
            "health": {
                "overall": latest_health.overall_health if latest_health else 0.0,
                "stability": latest_health.system_stability if latest_health else 0.0,
                "risk_level": latest_health.risk_level if latest_health else "unknown",
            },
            "statistics": {
                "health_history_points": len(self.health_history),
                "signals_processed": len(self.signal_history),
                "unified_insights": len(self.unified_insights),
                "active_alerts": len(self.system_alerts),
            },
            "existing_systems_connected": self.existing_systems_connected,
        }

    def get_unified_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent unified insights"""
        return self.unified_insights[-limit:]

    def get_system_health_trend(self, hours: int = 24) -> List[SystemHealthMetrics]:
        """Get system health trend over specified hours"""

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        return [
            health for health in self.health_history if health.timestamp > cutoff_time
        ]


# Factory function
def create_integrated_monitoring_system(
    signal_bus: SignalBus, config: Optional[Dict[str, Any]] = None
) -> IntegratedMonitoringSystem:
    """Create and return an IntegratedMonitoringSystem instance"""
    return IntegratedMonitoringSystem(signal_bus, config)


# Helper function to start the complete system
async def start_complete_monitoring_system(
    signal_bus: SignalBus, config: Optional[Dict[str, Any]] = None
) -> IntegratedMonitoringSystem:
    """
    Start the complete integrated monitoring system with all components.
    This is the main entry point for the enhanced monitoring system.
    """

    logger.info(
        "Starting complete LUKHAS monitoring system with endocrine-triggered plasticity"
    )

    # Create the integrated system
    monitoring_system = create_integrated_monitoring_system(signal_bus, config)

    # Initialize all components
    await monitoring_system.initialize()

    # Start monitoring
    await monitoring_system.start_monitoring()

    logger.info("Complete LUKHAS monitoring system started successfully")

    return monitoring_system
