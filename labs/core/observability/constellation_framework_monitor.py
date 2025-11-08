"""
Constellation Framework Monitoring System for LUKHAS AI

This module provides comprehensive monitoring for the Constellation Framework
(⚛️🧠🛡️) with integrated authentication monitoring, API performance tracking,
and cross-component health analysis. Monitors the interconnections between
Identity, Consciousness, and Guardian systems.

Features:
- Constellation Framework component monitoring (⚛️🧠🛡️)
- Authentication system monitoring and security tracking
- API performance and latency monitoring
- Cross-component interaction analysis
- Identity coherence and integrity monitoring
- Consciousness state and performance tracking
- Guardian system effectiveness monitoring
- Integrated performance metrics and alerting
- Security event correlation and analysis
- Compliance monitoring across all Constellation components

#TAG:constellation
#TAG:monitoring
#TAG:authentication
#TAG:api
#TAG:framework
"""
import asyncio
import logging
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConstellationComponent(Enum):
    """Constellation Framework components (dynamic stars)"""

    IDENTITY = "identity"  # ⚛️
    CONSCIOUSNESS = "consciousness"  # 🧠
    GUARDIAN = "guardian"  # 🛡️


class InteractionType(Enum):
    """Types of component interactions"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DECISION_REQUEST = "decision_request"
    MEMORY_ACCESS = "memory_access"
    DRIFT_DETECTION = "drift_detection"
    COMPLIANCE_CHECK = "compliance_check"
    HEALTH_CHECK = "health_check"
    DATA_VALIDATION = "data_validation"
    THREAT_ASSESSMENT = "threat_assessment"


class PerformanceMetric(Enum):
    """Performance metric types"""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    AVAILABILITY = "availability"
    LATENCY = "latency"
    QUEUE_DEPTH = "queue_depth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"


@dataclass
class ConstellationInteraction:
    """Constellation Framework component interaction"""

    interaction_id: str
    timestamp: datetime

    # Components involved
    source_component: ConstellationComponent
    target_component: ConstellationComponent
    interaction_type: InteractionType

    # Performance data
    response_time: float  # milliseconds
    success: bool
    error_message: Optional[str] = None

    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_size: int = 0
    response_size: int = 0

    # Security context
    authentication_method: Optional[str] = None
    authorization_level: Optional[str] = None
    security_context: dict[str, Any] = field(default_factory=dict)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class AuthenticationEvent:
    """Authentication system event"""

    event_id: str
    timestamp: datetime
    event_type: str  # login, logout, token_refresh, mfa, etc.

    # User information
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Authentication details
    authentication_method: str = "unknown"
    success: bool = True
    failure_reason: Optional[str] = None

    # Security indicators
    risk_score: float = 0.0
    anomaly_detected: bool = False
    geolocation: Optional[dict[str, str]] = None

    # Performance
    processing_time: float = 0.0

    # Compliance
    compliance_logged: bool = False
    data_retention_category: str = "authentication"


@dataclass
class APIPerformanceMetric:
    """API performance measurement"""

    metric_id: str
    timestamp: datetime

    # API identification
    endpoint: str
    method: str

    # Performance metrics
    response_time: float  # milliseconds
    throughput: float  # requests per second
    error_rate: float  # percentage

    # Fields with defaults
    version: Optional[str] = None
    status_code: int = 200

    # Resource usage
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    database_query_time: float = 0.0

    # Constellation Framework context
    constellation_component: Optional[ConstellationComponent] = None
    requires_authentication: bool = False
    requires_authorization: bool = False

    # Request/response details
    request_size: int = 0
    response_size: int = 0
    cache_hit: bool = False

    # Error details
    error_message: Optional[str] = None
    error_category: Optional[str] = None


@dataclass
class ConstellationHealthStatus:
    """Overall Constellation Framework health status"""

    status_id: str
    timestamp: datetime

    # Component health scores (0.0 to 1.0)
    identity_health: float = 1.0  # ⚛️
    consciousness_health: float = 1.0  # 🧠
    guardian_health: float = 1.0  # 🛡️

    # Overall Constellation health
    overall_health: float = 1.0
    framework_coherence: float = 1.0

    # Inter-component metrics
    identity_consciousness_sync: float = 1.0  # ⚛️🧠
    consciousness_guardian_sync: float = 1.0  # 🧠🛡️
    guardian_identity_sync: float = 1.0  # 🛡️⚛️

    # Performance indicators
    average_response_time: float = 0.0
    total_throughput: float = 0.0
    system_error_rate: float = 0.0

    # Authentication health
    authentication_success_rate: float = 100.0
    authentication_response_time: float = 0.0
    security_incidents: int = 0

    # API health
    api_availability: float = 100.0
    api_performance_score: float = 1.0
    api_error_rate: float = 0.0

    # Compliance status
    compliance_score: float = 1.0
    active_violations: int = 0

    # Alerts and issues
    active_alerts: int = 0
    critical_issues: int = 0
    warnings: int = 0


@dataclass
class ConstellationReport:
    """Comprehensive Constellation Framework report"""

    report_id: str
    generated_at: datetime
    time_period: tuple[datetime, datetime]

    # Executive summary
    overall_framework_health: float
    health_trend: str

    # Component analysis
    component_performance: dict[ConstellationComponent, dict[str, float]] = field(default_factory=dict)
    component_interactions: dict[str, int] = field(default_factory=dict)

    # Authentication analysis
    authentication_metrics: dict[str, Any] = field(default_factory=dict)
    security_incidents: list[dict[str, Any]] = field(default_factory=list)

    # API performance analysis
    api_performance_summary: dict[str, Any] = field(default_factory=dict)
    slowest_endpoints: list[dict[str, Any]] = field(default_factory=list)
    highest_error_endpoints: list[dict[str, Any]] = field(default_factory=list)

    # Cross-component insights
    interaction_patterns: list[dict[str, Any]] = field(default_factory=list)
    performance_correlations: dict[str, float] = field(default_factory=dict)

    # Recommendations
    performance_recommendations: list[str] = field(default_factory=list)
    security_recommendations: list[str] = field(default_factory=list)
    optimization_opportunities: list[str] = field(default_factory=list)


class ConstellationFrameworkMonitor:
    """
    Comprehensive Constellation Framework monitoring system

    Monitors the interconnected Constellation Framework components (⚛️🧠🛡️)
    with authentication tracking, API performance monitoring, and
    cross-component health analysis for the LUKHAS AI system.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core configuration
        self.monitoring_interval = 2.0  # seconds
        self.interaction_retention_hours = 48
        self.performance_retention_hours = 72

        # Performance thresholds
        self.performance_thresholds = {
            "response_time_warning": 1000.0,  # ms
            "response_time_critical": 5000.0,  # ms
            "error_rate_warning": 2.0,  # %
            "error_rate_critical": 5.0,  # %
            "throughput_min": 10.0,  # requests/second
            "health_score_warning": 0.8,
            "health_score_critical": 0.6,
        }

        # Data storage
        self.constellation_interactions: deque = deque(maxlen=25000)
        self.authentication_events: deque = deque(maxlen=10000)
        self.api_metrics: deque = deque(maxlen=50000)
        self.health_snapshots: deque = deque(maxlen=5000)

        # Current state
        self.current_health: Optional[ConstellationHealthStatus] = None
        self.component_states: dict[ConstellationComponent, dict[str, Any]] = {}
        self.monitoring_active = True

        # Performance tracking
        self.framework_metrics = {
            "interactions_processed": 0,
            "auth_events_processed": 0,
            "api_metrics_collected": 0,
            "health_checks_performed": 0,
            "security_incidents_detected": 0,
            "performance_alerts_generated": 0,
            "average_framework_health": 1.0,
            "total_api_requests": 0,
            "monitoring_uptime": 0.0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Initialize monitoring
        asyncio.create_task(self._initialize_constellation_monitoring())

        logger.info("🔺 Constellation Framework Monitor initialized")

    async def _initialize_constellation_monitoring(self):
        """Initialize Constellation Framework monitoring"""

        try:
            # Initialize component states
            await self._initialize_component_states()

            # Start monitoring loops
            asyncio.create_task(self._constellation_health_loop())
            asyncio.create_task(self._interaction_monitoring_loop())
            asyncio.create_task(self._authentication_monitoring_loop())
            asyncio.create_task(self._api_performance_loop())
            asyncio.create_task(self._cross_component_analysis_loop())
            asyncio.create_task(self._cleanup_loop())

            logger.info("✅ Constellation monitoring loops started")

        except Exception as e:
            logger.error(f"❌ Constellation monitoring initialization failed: {e}")

    async def _initialize_component_states(self):
        """Initialize Constellation component states"""

        for component in ConstellationComponent:
            self.component_states[component] = {
                "health": 1.0,
                "last_update": datetime.now(timezone.utc),
                "response_time": 0.0,
                "error_rate": 0.0,
                "throughput": 0.0,
                "active_connections": 0,
                "recent_interactions": 0,
            }

    async def _constellation_health_loop(self):
        """Main Constellation health monitoring loop"""

        while self.monitoring_active:
            try:
                await self._capture_constellation_health_snapshot()
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"❌ Constellation health monitoring error: {e}")
                await asyncio.sleep(5)

    async def _interaction_monitoring_loop(self):
        """Monitor Constellation component interactions"""

        while self.monitoring_active:
            try:
                await self._analyze_component_interactions()
                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"❌ Interaction monitoring error: {e}")
                await asyncio.sleep(10)

    async def _authentication_monitoring_loop(self):
        """Monitor authentication system"""

        while self.monitoring_active:
            try:
                await self._monitor_authentication_activity()
                await asyncio.sleep(1.0)  # High frequency for security

            except Exception as e:
                logger.error(f"❌ Authentication monitoring error: {e}")
                await asyncio.sleep(5)

    async def _api_performance_loop(self):
        """Monitor API performance"""

        while self.monitoring_active:
            try:
                await self._collect_api_performance_metrics()
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"❌ API performance monitoring error: {e}")
                await asyncio.sleep(5)

    async def _cross_component_analysis_loop(self):
        """Analyze cross-component performance"""

        while self.monitoring_active:
            try:
                await self._analyze_cross_component_performance()
                await asyncio.sleep(30)  # Less frequent, more intensive analysis

            except Exception as e:
                logger.error(f"❌ Cross-component analysis error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_loop(self):
        """Data cleanup loop"""

        while self.monitoring_active:
            try:
                await self._cleanup_old_monitoring_data()
                await asyncio.sleep(3600)  # Every hour

            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
                await asyncio.sleep(1800)

    async def record_constellation_interaction(
        self,
        source_component: ConstellationComponent,
        target_component: ConstellationComponent,
        interaction_type: InteractionType,
        response_time: float,
        success: bool,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ConstellationInteraction:
        """Record a Constellation Framework component interaction"""

        interaction_id = f"interaction_{uuid.uuid4().hex[:12]}"
        metadata = metadata or {}

        interaction = ConstellationInteraction(
            interaction_id=interaction_id,
            timestamp=datetime.now(timezone.utc),
            source_component=source_component,
            target_component=target_component,
            interaction_type=interaction_type,
            response_time=response_time,
            success=success,
            user_id=user_id,
            session_id=session_id,
            error_message=error_message,
            metadata=metadata,
        )

        # Store interaction
        self.constellation_interactions.append(interaction)

        # Update component states
        await self._update_component_state(source_component, interaction)
        await self._update_component_state(target_component, interaction)

        # Update metrics
        self.framework_metrics["interactions_processed"] += 1

        logger.debug(
            f"⭐ Constellation interaction: {source_component.value} -> {target_component.value} ({response_time:.1f}ms)"
        )

        return interaction

    async def record_authentication_event(
        self,
        event_type: str,
        success: bool,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        authentication_method: str = "unknown",
        processing_time: float = 0.0,
        failure_reason: Optional[str] = None,
        risk_score: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AuthenticationEvent:
        """Record an authentication event"""

        event_id = f"auth_{uuid.uuid4().hex[:12]}"
        metadata = metadata or {}

        # Detect anomalies based on risk score
        anomaly_detected = risk_score > 0.7

        auth_event = AuthenticationEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            authentication_method=authentication_method,
            success=success,
            failure_reason=failure_reason,
            risk_score=risk_score,
            anomaly_detected=anomaly_detected,
            processing_time=processing_time,
        )

        # Store event
        self.authentication_events.append(auth_event)

        # Update metrics
        self.framework_metrics["auth_events_processed"] += 1

        if anomaly_detected or not success:
            self.framework_metrics["security_incidents_detected"] += 1

        logger.debug(f"🔐 Auth event: {event_type} ({'success' if success else 'failure'}) - {processing_time:.1f}ms")

        return auth_event

    async def record_api_performance(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int = 200,
        throughput: float = 0.0,
        constellation_component: Optional[ConstellationComponent] = None,
        request_size: int = 0,
        response_size: int = 0,
        requires_authentication: bool = False,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> APIPerformanceMetric:
        """Record API performance metrics"""

        metric_id = f"api_{uuid.uuid4().hex[:12]}"
        metadata = metadata or {}

        # Calculate error rate
        error_rate = 0.0 if 200 <= status_code < 400 else 100.0

        api_metric = APIPerformanceMetric(
            metric_id=metric_id,
            timestamp=datetime.now(timezone.utc),
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            status_code=status_code,
            constellation_component=constellation_component,
            requires_authentication=requires_authentication,
            request_size=request_size,
            response_size=response_size,
            error_message=error_message,
        )

        # Store metric
        self.api_metrics.append(api_metric)

        # Update metrics
        self.framework_metrics["api_metrics_collected"] += 1
        self.framework_metrics["total_api_requests"] += 1

        logger.debug(f"📊 API metric: {method} {endpoint} ({response_time:.1f}ms, {status_code})")

        return api_metric

    async def _capture_constellation_health_snapshot(self):
        """Capture comprehensive Constellation health snapshot"""

        try:
            snapshot_id = f"health_{uuid.uuid4().hex[:12]}"
            timestamp = datetime.now(timezone.utc)

            # Calculate component health scores
            identity_health = await self._calculate_component_health(ConstellationComponent.IDENTITY)
            consciousness_health = await self._calculate_component_health(ConstellationComponent.CONSCIOUSNESS)
            guardian_health = await self._calculate_component_health(ConstellationComponent.GUARDIAN)

            # Calculate overall health
            overall_health = (identity_health + consciousness_health + guardian_health) / 3.0

            # Calculate framework coherence (how well components work together)
            framework_coherence = await self._calculate_framework_coherence()

            # Calculate inter-component sync scores
            identity_consciousness_sync = await self._calculate_sync_score(
                ConstellationComponent.IDENTITY, ConstellationComponent.CONSCIOUSNESS
            )
            consciousness_guardian_sync = await self._calculate_sync_score(
                ConstellationComponent.CONSCIOUSNESS, ConstellationComponent.GUARDIAN
            )
            guardian_identity_sync = await self._calculate_sync_score(
                ConstellationComponent.GUARDIAN, ConstellationComponent.IDENTITY
            )

            # Calculate authentication metrics
            auth_metrics = await self._calculate_authentication_metrics()

            # Calculate API metrics
            api_metrics = await self._calculate_api_metrics()

            # Create health snapshot
            health_snapshot = ConstellationHealthStatus(
                status_id=snapshot_id,
                timestamp=timestamp,
                identity_health=identity_health,
                consciousness_health=consciousness_health,
                guardian_health=guardian_health,
                overall_health=overall_health,
                framework_coherence=framework_coherence,
                identity_consciousness_sync=identity_consciousness_sync,
                consciousness_guardian_sync=consciousness_guardian_sync,
                guardian_identity_sync=guardian_identity_sync,
                average_response_time=api_metrics.get("average_response_time", 0.0),
                total_throughput=api_metrics.get("total_throughput", 0.0),
                system_error_rate=api_metrics.get("error_rate", 0.0),
                authentication_success_rate=auth_metrics.get("success_rate", 100.0),
                authentication_response_time=auth_metrics.get("response_time", 0.0),
                security_incidents=auth_metrics.get("incidents", 0),
                api_availability=api_metrics.get("availability", 100.0),
                api_performance_score=api_metrics.get("performance_score", 1.0),
                api_error_rate=api_metrics.get("error_rate", 0.0),
                compliance_score=await self._calculate_compliance_score(),
                active_alerts=0,  # Would integrate with alerting system
                critical_issues=0,
                warnings=0,
            )

            # Store snapshot
            self.health_snapshots.append(health_snapshot)
            self.current_health = health_snapshot

            # Update framework metrics
            self.framework_metrics["health_checks_performed"] += 1
            self.framework_metrics["average_framework_health"] = overall_health

            logger.debug(
                f"🔺 Constellation health: {overall_health:.3f} (I:{identity_health:.2f} C:{consciousness_health:.2f} G:{guardian_health:.2f})"
            )

        except Exception as e:
            logger.error(f"❌ Constellation health snapshot failed: {e}")

    async def _calculate_component_health(self, component: ConstellationComponent) -> float:
        """Calculate health score for a Constellation component"""

        if component not in self.component_states:
            return 1.0

        state = self.component_states[component]

        # Base health score
        base_health = state.get("health", 1.0)

        # Performance penalties
        response_time = state.get("response_time", 0.0)
        error_rate = state.get("error_rate", 0.0)

        # Calculate penalties
        response_penalty = 0.0
        if response_time > self.performance_thresholds["response_time_warning"]:
            response_penalty = min(0.3, (response_time - self.performance_thresholds["response_time_warning"]) / 5000.0)

        error_penalty = min(0.4, error_rate / 10.0)  # Max 0.4 penalty for 10% error rate

        # Apply penalties
        health_score = max(0.0, base_health - response_penalty - error_penalty)

        return health_score

    async def _calculate_framework_coherence(self) -> float:
        """Calculate how well Constellation components work together"""

        if len(self.constellation_interactions) < 10:
            return 1.0

        # Analyze recent interactions
        recent_interactions = [
            i for i in self.constellation_interactions if (datetime.now(timezone.utc) - i.timestamp).total_seconds() < 3600  # Last hour
        ]

        if not recent_interactions:
            return 1.0

        # Calculate success rate across components
        successful_interactions = len([i for i in recent_interactions if i.success])
        success_rate = successful_interactions / len(recent_interactions)

        # Calculate response time consistency
        response_times = [i.response_time for i in recent_interactions]
        avg_response_time = statistics.mean(response_times)
        response_time_variance = statistics.variance(response_times) if len(response_times) > 1 else 0

        # Normalize variance (lower variance = better coherence)
        coherence_from_consistency = max(
            0.0,
            1.0 - (response_time_variance / (avg_response_time**2) if avg_response_time > 0 else 0),
        )

        # Combine metrics
        overall_coherence = (success_rate * 0.7) + (coherence_from_consistency * 0.3)

        return min(1.0, max(0.0, overall_coherence))

    async def _calculate_sync_score(self, component1: ConstellationComponent, component2: ConstellationComponent) -> float:
        """Calculate synchronization score between two components"""

        # Find interactions between these components
        recent_interactions = [
            i
            for i in self.constellation_interactions
            if (datetime.now(timezone.utc) - i.timestamp).total_seconds() < 1800  # Last 30 minutes
            and (
                (i.source_component == component1 and i.target_component == component2)
                or (i.source_component == component2 and i.target_component == component1)
            )
        ]

        if not recent_interactions:
            return 1.0  # Assume good sync if no recent interactions

        # Calculate metrics
        successful_interactions = len([i for i in recent_interactions if i.success])
        success_rate = successful_interactions / len(recent_interactions)

        # Calculate response time performance
        response_times = [i.response_time for i in recent_interactions]
        avg_response_time = statistics.mean(response_times)

        # Good sync means fast, successful interactions
        response_score = max(0.0, 1.0 - (avg_response_time / 5000.0))  # Normalize against 5s

        # Combine scores
        sync_score = (success_rate * 0.8) + (response_score * 0.2)

        return min(1.0, max(0.0, sync_score))

    async def _calculate_authentication_metrics(self) -> dict[str, Any]:
        """Calculate authentication system metrics"""

        # Analyze recent authentication events
        recent_events = [
            e for e in self.authentication_events if (datetime.now(timezone.utc) - e.timestamp).total_seconds() < 3600  # Last hour
        ]

        if not recent_events:
            return {"success_rate": 100.0, "response_time": 0.0, "incidents": 0}

        # Calculate success rate
        successful_events = len([e for e in recent_events if e.success])
        success_rate = (successful_events / len(recent_events)) * 100.0

        # Calculate average response time
        response_times = [e.processing_time for e in recent_events]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0

        # Count security incidents
        incidents = len([e for e in recent_events if e.anomaly_detected or not e.success])

        return {
            "success_rate": success_rate,
            "response_time": avg_response_time,
            "incidents": incidents,
        }

    async def _calculate_api_metrics(self) -> dict[str, Any]:
        """Calculate API performance metrics"""

        # Analyze recent API metrics
        recent_metrics = [
            m for m in self.api_metrics if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 3600  # Last hour
        ]

        if not recent_metrics:
            return {
                "average_response_time": 0.0,
                "total_throughput": 0.0,
                "error_rate": 0.0,
                "availability": 100.0,
                "performance_score": 1.0,
            }

        # Calculate metrics
        response_times = [m.response_time for m in recent_metrics]
        avg_response_time = statistics.mean(response_times)

        throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
        total_throughput = sum(throughputs)

        error_count = len([m for m in recent_metrics if m.error_rate > 0])
        error_rate = (error_count / len(recent_metrics)) * 100.0

        # Calculate availability (based on successful requests)
        successful_requests = len([m for m in recent_metrics if m.status_code < 400])
        availability = (successful_requests / len(recent_metrics)) * 100.0

        # Calculate performance score
        response_score = max(0.0, 1.0 - (avg_response_time / 5000.0))
        error_score = max(0.0, 1.0 - (error_rate / 100.0))
        performance_score = (response_score * 0.6) + (error_score * 0.4)

        return {
            "average_response_time": avg_response_time,
            "total_throughput": total_throughput,
            "error_rate": error_rate,
            "availability": availability,
            "performance_score": performance_score,
        }

    async def _calculate_compliance_score(self) -> float:
        """Calculate Constellation Framework compliance score"""

        # Base compliance score
        base_score = 1.0

        # Penalize for security incidents
        recent_incidents = len(
            [
                e
                for e in self.authentication_events
                if (datetime.now(timezone.utc) - e.timestamp).total_seconds() < 86400  # Last 24 hours
                and (e.anomaly_detected or not e.success)
            ]
        )

        incident_penalty = min(0.3, recent_incidents * 0.05)  # Max 30% penalty

        # Penalize for high error rates
        recent_api_errors = len(
            [
                m
                for m in self.api_metrics
                if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 3600 and m.error_rate > 0  # Last hour
            ]
        )

        if recent_api_errors > 0:
            total_recent_api = len(
                [m for m in self.api_metrics if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 3600]
            )

            api_error_rate = recent_api_errors / max(1, total_recent_api)
            error_penalty = min(0.2, api_error_rate * 0.5)  # Max 20% penalty
        else:
            error_penalty = 0.0

        compliance_score = max(0.0, base_score - incident_penalty - error_penalty)

        return compliance_score

    async def _update_component_state(self, component: ConstellationComponent, interaction: ConstellationInteraction):
        """Update component state based on interaction"""

        if component not in self.component_states:
            return

        state = self.component_states[component]

        # Update response time (rolling average)
        current_rt = state.get("response_time", 0.0)
        state["response_time"] = (current_rt * 0.9) + (interaction.response_time * 0.1)

        # Update error rate
        if not interaction.success:
            current_er = state.get("error_rate", 0.0)
            state["error_rate"] = min(100.0, current_er + 1.0)
        else:
            # Slowly decrease error rate on success
            current_er = state.get("error_rate", 0.0)
            state["error_rate"] = max(0.0, current_er * 0.95)

        # Update interaction count
        state["recent_interactions"] = state.get("recent_interactions", 0) + 1
        state["last_update"] = datetime.now(timezone.utc)

    async def _analyze_component_interactions(self):
        """Analyze Constellation component interaction patterns"""

        # Analyze recent interaction patterns
        recent_interactions = [
            i
            for i in self.constellation_interactions
            if (datetime.now(timezone.utc) - i.timestamp).total_seconds() < 1800  # Last 30 minutes
        ]

        if len(recent_interactions) < 5:
            return

        # Group interactions by type
        interaction_types = defaultdict(list)
        for interaction in recent_interactions:
            interaction_types[interaction.interaction_type].append(interaction)

        # Analyze each type
        for interaction_type, interactions in interaction_types.items():
            avg_response_time = statistics.mean([i.response_time for i in interactions])
            success_rate = len([i for i in interactions if i.success]) / len(interactions)

            # Log patterns that need attention
            if avg_response_time > self.performance_thresholds["response_time_warning"]:
                logger.warning(f"⭐ Slow {interaction_type.value} interactions: {avg_response_time:.1f}ms avg")

            if success_rate < 0.95:
                logger.warning(f"⭐ Low success rate for {interaction_type.value}: {success_rate:.1%}")

    async def _monitor_authentication_activity(self):
        """Monitor authentication system activity"""

        # This would integrate with actual authentication systems
        # For now, simulate some authentication events

        # Check for authentication anomalies in recent events
        recent_events = [
            e
            for e in self.authentication_events
            if (datetime.now(timezone.utc) - e.timestamp).total_seconds() < 300  # Last 5 minutes
        ]

        if not recent_events:
            return

        # Check for suspicious patterns
        failed_attempts = len([e for e in recent_events if not e.success])
        high_risk_events = len([e for e in recent_events if e.risk_score > 0.7])

        if failed_attempts > 5:
            logger.warning(f"🔐 High authentication failure rate: {failed_attempts} failures in 5 minutes")

        if high_risk_events > 0:
            logger.warning(f"🔐 High-risk authentication events detected: {high_risk_events}")

    async def _collect_api_performance_metrics(self):
        """Collect API performance metrics"""

        # This would integrate with actual API monitoring
        # For now, simulate some API metrics
        pass

    async def _analyze_cross_component_performance(self):
        """Analyze performance correlations between Constellation components"""

        if len(self.health_snapshots) < 10:
            return

        # Analyze recent health snapshots
        recent_snapshots = list(self.health_snapshots)[-20:]

        # Extract component health scores
        identity_scores = [s.identity_health for s in recent_snapshots]
        consciousness_scores = [s.consciousness_health for s in recent_snapshots]
        guardian_scores = [s.guardian_health for s in recent_snapshots]

        # Calculate correlations (simplified)
        if len(identity_scores) > 5:
            # Check if components are declining together (indicating system-wide issue)
            identity_trend = identity_scores[-1] - identity_scores[0]
            consciousness_trend = consciousness_scores[-1] - consciousness_scores[0]
            guardian_trend = guardian_scores[-1] - guardian_scores[0]

            if identity_trend < -0.1 and consciousness_trend < -0.1 and guardian_trend < -0.1:
                logger.warning("⭐ System-wide Constellation Framework health decline detected")

            # Check for sync issues
            avg_sync = (
                statistics.mean(
                    [
                        s.identity_consciousness_sync + s.consciousness_guardian_sync + s.guardian_identity_sync
                        for s in recent_snapshots
                    ]
                )
                / 3.0
            )

            if avg_sync < 0.8:
                logger.warning(f"⭐ Constellation component synchronization issues: {avg_sync:.2f}")

    async def _cleanup_old_monitoring_data(self):
        """Clean up old monitoring data"""

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.interaction_retention_hours)

        # Clean interactions
        while self.constellation_interactions and self.constellation_interactions[0].timestamp < cutoff_time:
            self.constellation_interactions.popleft()

        # Clean authentication events
        auth_cutoff = datetime.now(timezone.utc) - timedelta(hours=self.performance_retention_hours)
        while self.authentication_events and self.authentication_events[0].timestamp < auth_cutoff:
            self.authentication_events.popleft()

        # Clean API metrics
        while self.api_metrics and self.api_metrics[0].timestamp < cutoff_time:
            self.api_metrics.popleft()

    async def get_constellation_health_status(self) -> dict[str, Any]:
        """Get current Constellation Framework health status"""

        if not self.current_health:
            return {"status": "no_data", "timestamp": datetime.now(timezone.utc).isoformat()}

        health = self.current_health

        return {
            "timestamp": health.timestamp.isoformat(),
            "overall_health": health.overall_health,
            "framework_coherence": health.framework_coherence,
            # Component health (Constellation Framework)
            "constellation_components": {
                "identity": {  # ⚛️
                    "health": health.identity_health,
                    "status": (
                        "excellent"
                        if health.identity_health > 0.9
                        else "good" if health.identity_health > 0.7 else "degraded"
                    ),
                },
                "consciousness": {  # 🧠
                    "health": health.consciousness_health,
                    "status": (
                        "excellent"
                        if health.consciousness_health > 0.9
                        else "good" if health.consciousness_health > 0.7 else "degraded"
                    ),
                },
                "guardian": {  # 🛡️
                    "health": health.guardian_health,
                    "status": (
                        "excellent"
                        if health.guardian_health > 0.9
                        else "good" if health.guardian_health > 0.7 else "degraded"
                    ),
                },
            },
            # Inter-component synchronization
            "component_synchronization": {
                "identity_consciousness": health.identity_consciousness_sync,
                "consciousness_guardian": health.consciousness_guardian_sync,
                "guardian_identity": health.guardian_identity_sync,
            },
            # Performance metrics
            "performance": {
                "average_response_time": health.average_response_time,
                "total_throughput": health.total_throughput,
                "system_error_rate": health.system_error_rate,
            },
            # Authentication health
            "authentication": {
                "success_rate": health.authentication_success_rate,
                "response_time": health.authentication_response_time,
                "security_incidents": health.security_incidents,
            },
            # API health
            "api": {
                "availability": health.api_availability,
                "performance_score": health.api_performance_score,
                "error_rate": health.api_error_rate,
            },
            # Compliance
            "compliance": {
                "score": health.compliance_score,
                "active_violations": health.active_violations,
            },
            # Alerts and issues
            "alerts": {
                "active": health.active_alerts,
                "critical": health.critical_issues,
                "warnings": health.warnings,
            },
        }

    async def get_constellation_report(self, time_period: Optional[tuple[datetime, datetime]] = None) -> ConstellationReport:
        """Generate comprehensive Constellation Framework report"""

        if not time_period:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            time_period = (start_time, end_time)

        # Filter data for time period
        period_interactions = [i for i in self.constellation_interactions if time_period[0] <= i.timestamp <= time_period[1]]

        period_auth_events = [e for e in self.authentication_events if time_period[0] <= e.timestamp <= time_period[1]]

        period_api_metrics = [m for m in self.api_metrics if time_period[0] <= m.timestamp <= time_period[1]]

        period_health_snapshots = [h for h in self.health_snapshots if time_period[0] <= h.timestamp <= time_period[1]]

        # Calculate overall framework health
        if period_health_snapshots:
            health_scores = [h.overall_health for h in period_health_snapshots]
            overall_framework_health = statistics.mean(health_scores)

            # Determine trend
            if len(health_scores) > 5:
                recent_avg = statistics.mean(health_scores[-5:])
                earlier_avg = statistics.mean(health_scores[:5])
                if recent_avg > earlier_avg * 1.05:
                    health_trend = "improving"
                elif recent_avg < earlier_avg * 0.95:
                    health_trend = "declining"
                else:
                    health_trend = "stable"
            else:
                health_trend = "stable"
        else:
            overall_framework_health = 1.0
            health_trend = "stable"

        # Generate report
        report = ConstellationReport(
            report_id=f"constellation_report_{uuid.uuid4().hex[:12]}",
            generated_at=datetime.now(timezone.utc),
            time_period=time_period,
            overall_framework_health=overall_framework_health,
            health_trend=health_trend,
        )

        # Component performance analysis
        for component in ConstellationComponent:
            component_interactions = [
                i for i in period_interactions if i.source_component == component or i.target_component == component
            ]

            if component_interactions:
                avg_response_time = statistics.mean([i.response_time for i in component_interactions])
                success_rate = len([i for i in component_interactions if i.success]) / len(component_interactions)

                report.component_performance[component] = {
                    "average_response_time": avg_response_time,
                    "success_rate": success_rate,
                    "total_interactions": len(component_interactions),
                }

        # Authentication analysis
        if period_auth_events:
            auth_success_rate = len([e for e in period_auth_events if e.success]) / len(period_auth_events)
            auth_avg_time = statistics.mean([e.processing_time for e in period_auth_events])
            security_incidents = len([e for e in period_auth_events if e.anomaly_detected])

            report.authentication_metrics = {
                "success_rate": auth_success_rate,
                "average_response_time": auth_avg_time,
                "total_events": len(period_auth_events),
                "security_incidents": security_incidents,
            }

        # API performance analysis
        if period_api_metrics:
            api_avg_response = statistics.mean([m.response_time for m in period_api_metrics])
            api_error_rate = len([m for m in period_api_metrics if m.error_rate > 0]) / len(period_api_metrics)

            # Find slowest endpoints
            endpoint_performance = defaultdict(list)
            for metric in period_api_metrics:
                endpoint_performance[metric.endpoint].append(metric.response_time)

            slowest_endpoints = []
            for endpoint, times in endpoint_performance.items():
                avg_time = statistics.mean(times)
                slowest_endpoints.append({"endpoint": endpoint, "average_response_time": avg_time})

            slowest_endpoints.sort(key=lambda x: x["average_response_time"], reverse=True)

            report.api_performance_summary = {
                "average_response_time": api_avg_response,
                "error_rate": api_error_rate,
                "total_requests": len(period_api_metrics),
            }

            report.slowest_endpoints = slowest_endpoints[:10]  # Top 10 slowest

        # Generate recommendations
        if overall_framework_health < 0.8:
            report.performance_recommendations.append("Investigate Constellation Framework component health issues")

        if period_auth_events and len([e for e in period_auth_events if not e.success]) > 10:
            report.security_recommendations.append(
                "Review authentication failures and implement additional security measures"
            )

        if period_api_metrics and statistics.mean([m.response_time for m in period_api_metrics]) > 1000:
            report.optimization_opportunities.append(
                "API response times are elevated - consider performance optimization"
            )

        return report

    async def get_monitoring_metrics(self) -> dict[str, Any]:
        """Get Constellation monitoring system metrics"""

        self.framework_metrics["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.framework_metrics["monitoring_uptime"] = (
            (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(self.framework_metrics["last_updated"].replace("T", " ").replace("Z", ""))
            ).total_seconds()
            if "last_updated" in self.framework_metrics
            else 0.0
        )

        return self.framework_metrics.copy()

    async def shutdown(self):
        """Shutdown Constellation Framework monitoring"""

        self.monitoring_active = False
        logger.info("🛑 Constellation Framework Monitor shutdown initiated")


# Export main classes
__all__ = [
    "APIPerformanceMetric",
    "AuthenticationEvent",
    "ConstellationComponent",
    "ConstellationFrameworkMonitor",
    "ConstellationHealthStatus",
    "ConstellationInteraction",
    "ConstellationReport",
    "InteractionType",
    "PerformanceMetric",
]
