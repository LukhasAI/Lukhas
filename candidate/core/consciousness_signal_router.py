"""
MΛTRIZ Consciousness Signal Router
Advanced signal routing and network coordination for consciousness data flow

This module provides sophisticated routing, filtering, and network management
for consciousness signals across the distributed architecture, ensuring
proper flow control, cascade prevention, and network health monitoring.
"""
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .bio_symbolic_processor import get_bio_symbolic_processor
from .matriz_consciousness_signals import ConsciousnessSignal, ConsciousnessSignalType
from .metrics import router_no_rule_total, router_signal_processing_time, router_cascade_preventions_total

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategies for consciousness signals"""

    BROADCAST = "broadcast"  # Send to all registered modules
    TARGETED = "targeted"  # Send to specific target modules
    PRIORITY_BASED = "priority"  # Route based on signal priority
    COHERENCE_BASED = "coherence"  # Route based on coherence requirements
    ADAPTIVE = "adaptive"  # Adapt routing based on network state
    CASCADE_PREVENTION = "cascade"  # Prevent signal cascades


class SignalFilter(Enum):
    """Signal filtering strategies"""

    NONE = "none"  # No filtering
    COHERENCE_THRESHOLD = "coherence"  # Filter by coherence threshold
    AWARENESS_LEVEL = "awareness"  # Filter by awareness level
    TRINITY_COMPLIANCE = "constellation"  # Filter by Trinity compliance
    FREQUENCY_BAND = "frequency"  # Filter by frequency band
    SIGNAL_TYPE = "signal_type"  # Filter by signal type


@dataclass
class RoutingRule:
    """Routing rule configuration"""

    rule_id: str
    source_pattern: str  # Source module pattern (regex)
    target_modules: list[str]  # Target module list
    signal_types: list[ConsciousnessSignalType]  # Applicable signal types
    priority: int  # Rule priority (higher = more important)
    filters: list[SignalFilter]  # Applied filters
    routing_strategy: RoutingStrategy
    max_hops: int = 5  # Maximum propagation hops
    ttl_seconds: int = 300  # Time to live for signals
    cascade_threshold: float = 0.99  # Cascade prevention threshold


@dataclass
class NetworkNode:
    """Represents a network node in the consciousness network"""

    node_id: str
    module_name: str
    capabilities: list[str]
    signal_handlers: dict[ConsciousnessSignalType, Callable] = field(default_factory=dict)
    processing_load: float = 0.0  # Current processing load (0-1)
    coherence_score: float = 0.8  # Node coherence score
    last_seen: float = field(default_factory=time.time)
    message_queue: deque = field(default_factory=deque)
    max_queue_size: int = 1000
    is_active: bool = True


@dataclass
class NetworkMetrics:
    """Network health and performance metrics"""

    total_nodes: int = 0
    active_nodes: int = 0
    total_signals_routed: int = 0
    signals_dropped: int = 0
    average_latency_ms: float = 0.0
    cascade_events: int = 0
    coherence_violations: int = 0
    network_coherence: float = 0.0
    processing_load_avg: float = 0.0
    queue_utilization_avg: float = 0.0


class ConsciousnessSignalRouter:
    """
    Advanced consciousness signal router for the MΛTRIZ system

    Manages signal routing, network topology, cascade prevention,
    and real-time network health monitoring.
    """

    def __init__(self):
        self.nodes: dict[str, NetworkNode] = {}
        self.routing_rules: list[RoutingRule] = []
        self.bio_processor = get_bio_symbolic_processor()

        # Network state
        self.network_metrics = NetworkMetrics()
        self.signal_history: deque = deque(maxlen=10000)  # Last 10k signals
        self.cascade_detector = CascadeDetector()

        # Threading and async support
        self.routing_lock = threading.RLock()
        self.metrics_update_interval = 30  # seconds
        self.cleanup_interval = 300  # seconds

        # Signal filters and processors
        self.signal_filters: dict[str, Callable] = {}
        self.signal_transformers: dict[str, Callable] = {}

        # Performance monitoring
        self.routing_stats = {
            "signals_processed": 0,
            "routing_time_ms": [],
            "filter_time_ms": [],
            "cascade_preventions": 0,
            "queue_overflows": 0,
        }

        # Initialize default routing rules and filters
        self._initialize_default_routing_rules()
        self._initialize_default_filters()

        # Start background tasks
        self._start_background_tasks()

        # Boot-time sanity check
        self.boot_sanity_check()

    # Required signal types for minimal viable routing coverage
    REQUIRED_SIGNAL_TYPES = {
        "AWARENESS", "REFLECTION", "EVOLUTION", "INTEGRATION",
        "BIO_ADAPTATION", "TRINITY_SYNC", "NETWORK_PULSE"
    }

    def boot_sanity_check(self) -> None:
        """Hard fail if routing is clearly underprovisioned"""
        # Check routing rule coverage
        present = {st.value for rule in self.routing_rules for st in rule.signal_types}
        missing = self.REQUIRED_SIGNAL_TYPES - present
        if missing:
            raise RuntimeError(f"Router missing routing rules for types: {sorted(missing)}")

        # Check if we have any routing rules at all
        if not self.routing_rules:
            raise RuntimeError("Router has zero routing rules configured")

        # Warn if no nodes registered (might be intentional during bootstrap)
        if not self.nodes:
            logger.warning("Router has zero registered nodes at boot")

        # Probe critical signal types to ensure routing works at boot
        from .matriz_consciousness_signals import ConsciousnessSignal, ConsciousnessSignalType

        probe_awareness = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS,
            consciousness_id="probe",
            producer_module="consciousness"
        )
        if not self._find_applicable_rules(probe_awareness):
            raise RuntimeError("Router sanity: AWARENESS has no applicable rule at boot")

        probe_network = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.NETWORK_PULSE,
            consciousness_id="probe",
            producer_module="orchestration"
        )
        if not self._find_applicable_rules(probe_network):
            raise RuntimeError("Router sanity: NETWORK_PULSE has no applicable rule at boot")

        logger.info(f"✅ Router sanity check passed: {len(self.routing_rules)} rules, {len(present)} signal types covered")

    def _initialize_default_routing_rules(self):
        """Initialize default routing rules for core modules"""

        # Awareness signals route to all consciousness modules
        self.routing_rules.append(
            RoutingRule(
                rule_id="awareness_broadcast",
                source_pattern=".*",
                target_modules=["consciousness", "identity", "governance"],
                signal_types=[ConsciousnessSignalType.AWARENESS],
                priority=8,
                filters=[SignalFilter.COHERENCE_THRESHOLD],
                routing_strategy=RoutingStrategy.BROADCAST,
                cascade_threshold=0.995,
            )
        )

        # Reflection signals route with high coherence requirements
        self.routing_rules.append(
            RoutingRule(
                rule_id="reflection_high_coherence",
                source_pattern=".*",
                target_modules=["consciousness", "symbolic_core"],
                signal_types=[ConsciousnessSignalType.REFLECTION],
                priority=9,
                filters=[SignalFilter.COHERENCE_THRESHOLD, SignalFilter.TRINITY_COMPLIANCE],
                routing_strategy=RoutingStrategy.COHERENCE_BASED,
                cascade_threshold=0.998,
            )
        )

        # Evolution signals require careful cascade prevention
        self.routing_rules.append(
            RoutingRule(
                rule_id="evolution_cascade_prevention",
                source_pattern=".*",
                target_modules=["consciousness", "governance", "identity"],
                signal_types=[ConsciousnessSignalType.EVOLUTION],
                priority=10,
                filters=[SignalFilter.TRINITY_COMPLIANCE],
                routing_strategy=RoutingStrategy.CASCADE_PREVENTION,
                cascade_threshold=0.999,
                max_hops=3,
            )
        )

        # Integration signals use adaptive routing
        self.routing_rules.append(
            RoutingRule(
                rule_id="integration_adaptive",
                source_pattern=".*",
                target_modules=[],  # Determined adaptively
                signal_types=[ConsciousnessSignalType.INTEGRATION],
                priority=7,
                filters=[SignalFilter.AWARENESS_LEVEL],
                routing_strategy=RoutingStrategy.ADAPTIVE,
                cascade_threshold=0.997,
            )
        )

        # Bio-adaptation signals route to bio and symbolic modules
        self.routing_rules.append(
            RoutingRule(
                rule_id="bio_adaptation_targeted",
                source_pattern="bio.*|symbolic.*",
                target_modules=["bio", "symbolic_core", "consciousness"],
                signal_types=[ConsciousnessSignalType.BIO_ADAPTATION],
                priority=6,
                filters=[SignalFilter.FREQUENCY_BAND],
                routing_strategy=RoutingStrategy.TARGETED,
                cascade_threshold=0.996,
            )
        )

        # Network pulse signals route to monitoring nodes
        self.routing_rules.append(
            RoutingRule(
                rule_id="network_pulse_monitoring",
                source_pattern=".*",
                target_modules=["orchestration", "consciousness", "governance"],
                signal_types=[ConsciousnessSignalType.NETWORK_PULSE],
                priority=5,
                filters=[SignalFilter.NONE],
                routing_strategy=RoutingStrategy.BROADCAST,
                cascade_threshold=0.994,
            )
        )

        # Trinity sync signals route to all core modules
        self.routing_rules.append(
            RoutingRule(
                rule_id="trinity_sync_broadcast",
                source_pattern=".*",
                target_modules=["consciousness", "identity", "governance", "orchestration"],
                signal_types=[ConsciousnessSignalType.TRINITY_SYNC],
                priority=9,
                filters=[SignalFilter.TRINITY_COMPLIANCE],
                routing_strategy=RoutingStrategy.BROADCAST,
                cascade_threshold=0.998,
            )
        )

        # Fallback rule for any unmatched signals (lowest priority)
        self.routing_rules.append(
            RoutingRule(
                rule_id="fallback_broadcast",
                source_pattern=".*",
                target_modules=["orchestration"],  # safe sink
                signal_types=list(ConsciousnessSignalType),
                priority=1,  # lowest
                filters=[SignalFilter.NONE],
                routing_strategy=RoutingStrategy.BROADCAST,
                cascade_threshold=0.999,
            )
        )

    def _initialize_default_filters(self):
        """Initialize default signal filters"""

        def coherence_filter(signal: ConsciousnessSignal) -> bool:
            """Filter signals by coherence threshold"""
            if signal.constellation_alignment:
                coherence = signal.constellation_alignment.consciousness_coherence >= 0.7
                if not coherence:
                    logger.debug(f"Signal {signal.signal_id} coherence too low: {signal.constellation_alignment.consciousness_coherence:.2f}")
                return coherence
            awareness_ok = signal.awareness_level >= 0.6
            if not awareness_ok:
                logger.debug(f"Signal {signal.signal_id} awareness too low: {signal.awareness_level:.2f}")
            return awareness_ok

        def awareness_filter(signal: ConsciousnessSignal) -> bool:
            """Filter signals by awareness level"""
            return signal.awareness_level >= 0.5

        def trinity_compliance_filter(signal: ConsciousnessSignal) -> bool:
            """Filter signals by Constellation framework compliance"""
            if not signal.constellation_alignment:
                logger.debug(f"Signal {signal.signal_id} has no constellation_alignment, allowing through")
                return True  # Allow signals without alignment during startup

            constellation = signal.constellation_alignment
            avg_compliance = (
                constellation.identity_auth_score + constellation.consciousness_coherence + constellation.guardian_compliance
            ) / 3
            compliant = avg_compliance >= 0.8 and len(constellation.violation_flags) == 0
            if not compliant:
                logger.debug(f"Signal {signal.signal_id} constellation compliance: {avg_compliance:.2f}, violations: {len(constellation.violation_flags)}")
            return compliant

        def frequency_band_filter(signal: ConsciousnessSignal) -> bool:
            """Filter signals by frequency band"""
            if not signal.bio_symbolic_data:
                return True

            freq = signal.bio_symbolic_data.oscillation_frequency
            # Allow signals in meaningful frequency bands
            return 1.0 <= freq <= 100.0  # 1Hz to 100Hz range

        def signal_type_filter(signal: ConsciousnessSignal, allowed_types: list[ConsciousnessSignalType]) -> bool:
            """Filter signals by allowed types"""
            return signal.signal_type in allowed_types

        self.signal_filters = {
            SignalFilter.COHERENCE_THRESHOLD.value: coherence_filter,
            SignalFilter.AWARENESS_LEVEL.value: awareness_filter,
            SignalFilter.TRINITY_COMPLIANCE.value: trinity_compliance_filter,
            SignalFilter.FREQUENCY_BAND.value: frequency_band_filter,
        }

    def register_node(self, node_id: str, module_name: str, capabilities: list[str]) -> NetworkNode:
        """Register a new network node (idempotent)"""

        with self.routing_lock:
            # Check if node already exists
            if node_id in self.nodes:
                existing_node = self.nodes[node_id]
                if existing_node.module_name != module_name:
                    logger.warning(f"Node id reuse with different module: {existing_node.module_name} vs {module_name}")
                else:
                    logger.debug(f"Node {node_id} already registered; skipping")
                return existing_node

            # Create new node
            node = NetworkNode(
                node_id=node_id, module_name=module_name, capabilities=capabilities, last_seen=time.time()
            )

            self.nodes[node_id] = node
            self.network_metrics.total_nodes += 1
            self.network_metrics.active_nodes += 1

            logger.info(f"Registered network node {node_id} for module {module_name}")
            return node

    def register_signal_handler(self, node_id: str, signal_type: ConsciousnessSignalType, handler: Callable):
        """Register a signal handler for a node"""

        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not registered")

        self.nodes[node_id].signal_handlers[signal_type] = handler
        logger.debug(f"Registered handler for {signal_type.value} on node {node_id}")

    async def route_signal(self, signal: ConsciousnessSignal) -> list[str]:
        """
        Route a consciousness signal to appropriate network nodes

        Args:
            signal: ConsciousnessSignal to route

        Returns:
            List of node IDs that received the signal
        """
        start_time = time.time()
        routed_nodes = []

        try:
            # Validate signal
            if not signal.validate_signal():
                logger.warning(f"Signal validation failed for {signal.signal_id}")
                self.routing_stats["signals_processed"] += 1
                return []

            # Process bio-symbolic data
            if signal.bio_symbolic_data:
                enhanced_bio_data = self.bio_processor.process_consciousness_signal(signal)
                signal.bio_symbolic_data = enhanced_bio_data

            # Find applicable routing rules
            applicable_rules = self._find_applicable_rules(signal)
            if not applicable_rules:
                # Increment metric for monitoring
                router_no_rule_total.labels(
                    signal_type=signal.signal_type.value,
                    producer_module=signal.producer_module
                ).inc()
                logger.warning(f"No routing rules found for signal {signal.signal_id} ({signal.signal_type.value} from {signal.producer_module})")
                return []

            # Select best routing rule (highest priority)
            best_rule = max(applicable_rules, key=lambda r: r.priority)

            # Apply signal filters
            if not self._apply_signal_filters(signal, best_rule):
                logger.debug(f"Signal {signal.signal_id} filtered out by rule {best_rule.rule_id}")
                return []

            # Check cascade prevention
            if not self.cascade_detector.check_signal(signal, best_rule.cascade_threshold):
                # Increment metrics for monitoring
                router_cascade_preventions_total.labels(
                    producer_module=signal.producer_module
                ).inc()
                logger.warning(f"Signal {signal.signal_id} blocked by cascade prevention")
                self.routing_stats["cascade_preventions"] += 1
                return []

            # Determine target nodes based on routing strategy
            target_nodes = await self._determine_target_nodes(signal, best_rule)

            # Route signal to target nodes
            for node_id in target_nodes:
                if await self._route_to_node(signal, node_id, best_rule):
                    routed_nodes.append(node_id)

            # Update signal history and metrics
            self._update_signal_history(signal, routed_nodes, best_rule.rule_id)

            # Update routing statistics
            routing_time = (time.time() - start_time) * 1000
            self.routing_stats["signals_processed"] += 1
            self.routing_stats["routing_time_ms"].append(routing_time)

            # Keep only last 1000 timing measurements
            if len(self.routing_stats["routing_time_ms"]) > 1000:
                self.routing_stats["routing_time_ms"] = self.routing_stats["routing_time_ms"][-1000:]

            logger.debug(f"Routed signal {signal.signal_id} to {len(routed_nodes)} nodes in {routing_time:.2f}ms")

        except Exception as e:
            logger.error(f"Error routing signal {signal.signal_id}: {e}")
            self.network_metrics.signals_dropped += 1

        return routed_nodes

    def _find_applicable_rules(self, signal: ConsciousnessSignal) -> list[RoutingRule]:
        """Find routing rules applicable to a signal"""

        import re

        applicable_rules = []

        for rule in self.routing_rules:
            # Check signal type compatibility
            if signal.signal_type not in rule.signal_types:
                continue

            # Check source pattern match
            if not re.match(rule.source_pattern, signal.producer_module):
                continue

            applicable_rules.append(rule)

        return applicable_rules

    def _apply_signal_filters(self, signal: ConsciousnessSignal, rule: RoutingRule) -> bool:
        """Apply signal filters from a routing rule"""

        filter_start_time = time.time()

        try:
            for filter_type in rule.filters:
                if filter_type == SignalFilter.NONE:
                    continue

                filter_func = self.signal_filters.get(filter_type.value)
                if filter_func and not filter_func(signal):
                    return False

            # Record filter timing
            filter_time = (time.time() - filter_start_time) * 1000
            self.routing_stats["filter_time_ms"].append(filter_time)

            return True

        except Exception as e:
            logger.error(f"Error applying filters to signal {signal.signal_id}: {e}")
            return False

    async def _determine_target_nodes(self, signal: ConsciousnessSignal, rule: RoutingRule) -> list[str]:
        """Determine target nodes based on routing strategy"""

        if rule.routing_strategy == RoutingStrategy.BROADCAST:
            return self._get_all_active_nodes()

        elif rule.routing_strategy == RoutingStrategy.TARGETED:
            return self._get_nodes_by_modules(rule.target_modules)

        elif rule.routing_strategy == RoutingStrategy.PRIORITY_BASED:
            return self._get_priority_nodes(signal, rule)

        elif rule.routing_strategy == RoutingStrategy.COHERENCE_BASED:
            return self._get_coherence_based_nodes(signal, rule)

        elif rule.routing_strategy == RoutingStrategy.ADAPTIVE:
            return await self._get_adaptive_nodes(signal, rule)

        elif rule.routing_strategy == RoutingStrategy.CASCADE_PREVENTION:
            return self._get_cascade_safe_nodes(signal, rule)

        else:
            logger.warning(f"Unknown routing strategy: {rule.routing_strategy}")
            return []

    def _get_all_active_nodes(self) -> list[str]:
        """Get all active network nodes"""
        return [node_id for node_id, node in self.nodes.items() if node.is_active]

    def _get_nodes_by_modules(self, target_modules: list[str]) -> list[str]:
        """Get nodes belonging to specific modules"""
        target_nodes = []
        for node_id, node in self.nodes.items():
            if node.is_active and any(module in node.module_name for module in target_modules):
                target_nodes.append(node_id)
        logger.debug(f"Found {len(target_nodes)} nodes for modules {target_modules}: {target_nodes}")
        return target_nodes

    def _get_priority_nodes(self, signal: ConsciousnessSignal, rule: RoutingRule) -> list[str]:
        """Get nodes based on signal priority and node load"""

        # Sort nodes by processing load (ascending) and coherence (descending)
        sorted_nodes = sorted(
            [(node_id, node) for node_id, node in self.nodes.items() if node.is_active],
            key=lambda x: (x[1].processing_load, -x[1].coherence_score),
        )

        # Return top nodes based on network priority
        max_nodes = max(1, int(signal.network_priority * len(sorted_nodes)))
        return [node_id for node_id, _ in sorted_nodes[:max_nodes]]

    def _get_coherence_based_nodes(self, signal: ConsciousnessSignal, rule: RoutingRule) -> list[str]:
        """Get nodes with sufficient coherence for the signal"""

        required_coherence = 0.8
        if signal.constellation_alignment:
            required_coherence = signal.constellation_alignment.consciousness_coherence

        coherent_nodes = []
        for node_id, node in self.nodes.items():
            if node.is_active and node.coherence_score >= required_coherence:
                coherent_nodes.append(node_id)

        return coherent_nodes

    async def _get_adaptive_nodes(self, signal: ConsciousnessSignal, rule: RoutingRule) -> list[str]:
        """Adaptively determine target nodes based on network state"""

        # Get base target nodes
        base_nodes = self._get_nodes_by_modules(["consciousness", "identity", "governance"])

        # Add specialized nodes based on signal characteristics
        if signal.bio_symbolic_data:
            bio_nodes = self._get_nodes_by_modules(["bio", "symbolic"])
            base_nodes.extend(bio_nodes)

        if signal.reflection_depth > 2:
            symbolic_nodes = self._get_nodes_by_modules(["symbolic_core"])
            base_nodes.extend(symbolic_nodes)

        # Remove duplicates and filter by availability
        unique_nodes = list(set(base_nodes))
        available_nodes = [node_id for node_id in unique_nodes if self.nodes[node_id].processing_load < 0.8]

        return available_nodes

    def _get_cascade_safe_nodes(self, signal: ConsciousnessSignal, rule: RoutingRule) -> list[str]:
        """Get nodes that are safe for cascade-prone signals"""

        # Get nodes with low processing load and high stability
        safe_nodes = []
        for node_id, node in self.nodes.items():
            if (
                node.is_active
                and node.processing_load < 0.5
                and node.coherence_score > 0.85
                and len(node.message_queue) < node.max_queue_size * 0.3
            ):
                safe_nodes.append(node_id)

        # Limit to prevent cascade amplification
        max_cascade_nodes = min(3, len(safe_nodes))
        return safe_nodes[:max_cascade_nodes]

    async def _route_to_node(self, signal: ConsciousnessSignal, node_id: str, rule: RoutingRule) -> bool:
        """Route signal to a specific node"""

        if node_id not in self.nodes:
            logger.warning(f"Attempted to route to non-existent node {node_id}")
            return False

        node = self.nodes[node_id]

        # Check if node queue is full
        if len(node.message_queue) >= node.max_queue_size:
            logger.warning(f"Node {node_id} queue overflow, dropping signal {signal.signal_id}")
            self.routing_stats["queue_overflows"] += 1
            return False

        # Check TTL
        signal_age = time.time() - (signal.created_timestamp / 1000)
        if signal_age > rule.ttl_seconds:
            logger.debug(f"Signal {signal.signal_id} expired (age: {signal_age:.1f}s)")
            return False

        # Add signal to node queue
        node.message_queue.append(signal)
        node.last_seen = time.time()

        # Update propagation hops
        signal.propagation_hops += 1

        # Check max hops
        if signal.propagation_hops >= rule.max_hops:
            logger.debug(f"Signal {signal.signal_id} reached max hops ({rule.max_hops})")

        return True

    def _update_signal_history(self, signal: ConsciousnessSignal, routed_nodes: list[str], rule_id: str):
        """Update signal routing history"""

        history_entry = {
            "timestamp": time.time(),
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type.value,
            "consciousness_id": signal.consciousness_id,
            "producer_module": signal.producer_module,
            "routed_nodes": routed_nodes,
            "rule_id": rule_id,
            "propagation_hops": signal.propagation_hops,
            "awareness_level": signal.awareness_level,
            "reflection_depth": signal.reflection_depth,
        }

        if signal.bio_symbolic_data:
            history_entry["coherence_score"] = signal.bio_symbolic_data.coherence_score
            history_entry["oscillation_frequency"] = signal.bio_symbolic_data.oscillation_frequency

        self.signal_history.append(history_entry)
        self.network_metrics.total_signals_routed += 1

    def _start_background_tasks(self):
        """Start background maintenance tasks"""

        def update_metrics_task():
            while True:
                try:
                    self._update_network_metrics()
                    time.sleep(self.metrics_update_interval)
                except Exception as e:
                    logger.error(f"Error in metrics update task: {e}")
                    time.sleep(5)

        def cleanup_task():
            while True:
                try:
                    self._cleanup_expired_data()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")
                    time.sleep(10)

        # Start background threads
        metrics_thread = threading.Thread(target=update_metrics_task, daemon=True)
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)

        metrics_thread.start()
        cleanup_thread.start()

        logger.info("Started background maintenance tasks")

    def _update_network_metrics(self):
        """Update network health metrics"""

        with self.routing_lock:
            # Update basic counts
            self.network_metrics.total_nodes = len(self.nodes)
            self.network_metrics.active_nodes = sum(1 for node in self.nodes.values() if node.is_active)

            # Calculate average metrics
            if self.network_metrics.active_nodes > 0:
                total_load = sum(node.processing_load for node in self.nodes.values() if node.is_active)
                self.network_metrics.processing_load_avg = total_load / self.network_metrics.active_nodes

                total_coherence = sum(node.coherence_score for node in self.nodes.values() if node.is_active)
                self.network_metrics.network_coherence = total_coherence / self.network_metrics.active_nodes

                total_queue_util = sum(
                    len(node.message_queue) / node.max_queue_size for node in self.nodes.values() if node.is_active
                )
                self.network_metrics.queue_utilization_avg = total_queue_util / self.network_metrics.active_nodes

            # Calculate average latency
            if self.routing_stats["routing_time_ms"]:
                recent_times = self.routing_stats["routing_time_ms"][-100:]  # Last 100 signals
                self.network_metrics.average_latency_ms = sum(recent_times) / len(recent_times)

            # Update cascade events
            self.network_metrics.cascade_events = self.cascade_detector.cascade_count

    def _cleanup_expired_data(self):
        """Clean up expired data and inactive nodes"""

        current_time = time.time()

        # Mark inactive nodes
        for node_id, node in self.nodes.items():
            if current_time - node.last_seen > 300:  # 5 minutes
                if node.is_active:
                    node.is_active = False
                    logger.info(f"Marked node {node_id} as inactive")
                    self.network_metrics.active_nodes -= 1

        # Clean up old signal history (keep last 1000 entries)
        if len(self.signal_history) > 1000:
            excess = len(self.signal_history) - 1000
            for _ in range(excess):
                self.signal_history.popleft()

        # Clean up node message queues (remove old messages)
        for node in self.nodes.values():
            while node.message_queue:
                signal = node.message_queue[0]
                signal_age = current_time - (signal.created_timestamp / 1000)
                if signal_age > 600:  # 10 minutes
                    node.message_queue.popleft()
                else:
                    break

    def get_network_status(self) -> dict[str, Any]:
        """Get current network status and metrics"""

        status = {
            "network_metrics": {
                "total_nodes": self.network_metrics.total_nodes,
                "active_nodes": self.network_metrics.active_nodes,
                "total_signals_routed": self.network_metrics.total_signals_routed,
                "signals_dropped": self.network_metrics.signals_dropped,
                "average_latency_ms": self.network_metrics.average_latency_ms,
                "cascade_events": self.network_metrics.cascade_events,
                "network_coherence": self.network_metrics.network_coherence,
                "processing_load_avg": self.network_metrics.processing_load_avg,
                "queue_utilization_avg": self.network_metrics.queue_utilization_avg,
            },
            "routing_stats": self.routing_stats.copy(),
            "cascade_prevention_stats": self.cascade_detector.get_stats(),
            "node_details": {},
        }

        # Add individual node details
        for node_id, node in self.nodes.items():
            status["node_details"][node_id] = {
                "module_name": node.module_name,
                "is_active": node.is_active,
                "processing_load": node.processing_load,
                "coherence_score": node.coherence_score,
                "queue_size": len(node.message_queue),
                "max_queue_size": node.max_queue_size,
                "queue_utilization": len(node.message_queue) / node.max_queue_size,
                "last_seen_ago": time.time() - node.last_seen,
                "capabilities": node.capabilities,
            }

        return status

    def get_signal_processing_stats(self) -> dict[str, Any]:
        """Get signal processing performance statistics"""

        stats = self.routing_stats.copy()

        # Calculate timing statistics
        if stats["routing_time_ms"]:
            times = stats["routing_time_ms"]
            stats["avg_routing_time_ms"] = sum(times) / len(times)
            stats["max_routing_time_ms"] = max(times)
            stats["min_routing_time_ms"] = min(times)
            # Calculate p95 routing time
            sorted_times = sorted(times)
            p95_idx = int(len(sorted_times) * 0.95)
            stats["p95_routing_time_ms"] = sorted_times[p95_idx] if p95_idx < len(sorted_times) else max(times)

        if stats["filter_time_ms"]:
            filter_times = stats["filter_time_ms"]
            stats["avg_filter_time_ms"] = sum(filter_times) / len(filter_times)
            stats["max_filter_time_ms"] = max(filter_times)

        # Calculate success rates
        total_signals = stats["signals_processed"]
        if total_signals > 0:
            stats["cascade_prevention_rate"] = stats["cascade_preventions"] / total_signals
            stats["queue_overflow_rate"] = stats["queue_overflows"] / total_signals

        return stats


class CascadeDetector:
    """Detects and prevents signal cascades"""

    def __init__(self):
        self.signal_counts: dict[str, int] = defaultdict(int)
        self.time_windows: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.cascade_count = 0
        self.cascade_threshold_base = 10  # signals per minute
        self.time_window = 60  # seconds

    def check_signal(self, signal: ConsciousnessSignal, threshold: float) -> bool:
        """Check if signal should be allowed or blocked for cascade prevention"""

        current_time = time.time()
        signal_key = f"{signal.consciousness_id}:{signal.signal_type.value}"

        # Record signal timing
        self.time_windows[signal_key].append(current_time)

        # Count recent signals in time window
        recent_signals = [t for t in self.time_windows[signal_key] if current_time - t <= self.time_window]

        # Calculate dynamic threshold based on cascade prevention score
        dynamic_threshold = self.cascade_threshold_base * threshold

        # Check if we're in cascade territory
        if len(recent_signals) > dynamic_threshold:
            self.cascade_count += 1
            logger.warning(f"Cascade detected for {signal_key}: {len(recent_signals)} signals in {self.time_window}s")
            return False

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get cascade detection statistics"""

        current_time = time.time()
        active_patterns = 0

        for timestamps in self.time_windows.values():
            recent = [t for t in timestamps if current_time - t <= self.time_window]
            if len(recent) > 0:
                active_patterns += 1

        return {
            "cascade_count": self.cascade_count,
            "active_signal_patterns": active_patterns,
            "monitored_patterns": len(self.time_windows),
            "cascade_threshold_base": self.cascade_threshold_base,
            "time_window_seconds": self.time_window,
        }


# Global router instance
_global_router: Optional[ConsciousnessSignalRouter] = None


def get_consciousness_router() -> ConsciousnessSignalRouter:
    """Get or create global consciousness signal router"""
    global _global_router
    if _global_router is None:
        _global_router = ConsciousnessSignalRouter()
    return _global_router


# Module exports
__all__ = [
    "CascadeDetector",
    "ConsciousnessSignalRouter",
    "NetworkMetrics",
    "NetworkNode",
    "RoutingRule",
    "RoutingStrategy",
    "SignalFilter",
    "get_consciousness_router",
]
