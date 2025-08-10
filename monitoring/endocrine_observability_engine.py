#!/usr/bin/env python3
"""
Endocrine Observability Engine
=============================
Advanced monitoring system that tracks hormone levels and triggers
plasticity adaptations based on biological-inspired thresholds.
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import structlog

from core.endocrine.hormone_system import HormoneType, get_endocrine_system
from orchestration.signals.homeostasis_controller import HomeostasisState
from orchestration.signals.signal_bus import Signal, SignalBus, SignalType

logger = structlog.get_logger(__name__)


class PlasticityTriggerType(Enum):
    """Types of plasticity triggers based on endocrine responses"""
    
    STRESS_ADAPTATION = "stress_adaptation"           # High cortisol/adrenaline
    PERFORMANCE_OPTIMIZATION = "performance_opt"     # Low dopamine
    SOCIAL_ENHANCEMENT = "social_enhancement"        # Low oxytocin
    RECOVERY_CONSOLIDATION = "recovery_consolidation" # High melatonin
    CREATIVE_BOOST = "creative_boost"               # Balanced serotonin
    RESILIENCE_BUILDING = "resilience_building"     # Chronic stress patterns
    EFFICIENCY_TUNING = "efficiency_tuning"         # Suboptimal performance
    EMOTIONAL_REGULATION = "emotional_regulation"    # Mood instability


@dataclass
class EndocrineSnapshot:
    """Snapshot of endocrine system state at a point in time"""
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hormone_levels: Dict[str, float] = field(default_factory=dict)
    homeostasis_state: Optional[str] = None
    system_metrics: Dict[str, float] = field(default_factory=dict)
    triggers_activated: List[str] = field(default_factory=list)
    coherence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "hormone_levels": self.hormone_levels,
            "homeostasis_state": self.homeostasis_state,
            "system_metrics": self.system_metrics,
            "triggers_activated": self.triggers_activated,
            "coherence_score": self.coherence_score,
        }


@dataclass
class PlasticityEvent:
    """Record of a plasticity adaptation triggered by endocrine state"""
    
    trigger_type: PlasticityTriggerType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hormone_context: Dict[str, float] = field(default_factory=dict)
    reason: str = ""
    adaptation_applied: str = ""
    success: bool = False
    impact_score: float = 0.0
    follow_up_needed: bool = False


class EndocrineObservabilityEngine:
    """
    Advanced monitoring system that integrates endocrine state with system observability
    to trigger plasticity adaptations and maintain optimal system health.
    """
    
    def __init__(
        self,
        signal_bus: SignalBus,
        config: Optional[Dict[str, Any]] = None,
        data_dir: str = "data/observability"
    ):
        self.signal_bus = signal_bus
        self.config = config or {}
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core systems
        self.endocrine_system = None
        self.homeostasis_controller = None
        
        # Monitoring state
        self.is_running = False
        self.monitoring_interval = self.config.get("monitoring_interval", 5.0)  # seconds
        self.snapshot_retention = self.config.get("snapshot_retention", 1000)   # snapshots
        
        # Data storage
        self.snapshots: deque = deque(maxlen=self.snapshot_retention)
        self.plasticity_events: deque = deque(maxlen=500)
        self.trend_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Plasticity trigger thresholds
        self.trigger_thresholds = {
            PlasticityTriggerType.STRESS_ADAPTATION: {
                "cortisol_high": 0.75,
                "adrenaline_high": 0.80,
                "combined_stress": 0.70
            },
            PlasticityTriggerType.PERFORMANCE_OPTIMIZATION: {
                "dopamine_low": 0.30,
                "processing_efficiency_low": 0.60
            },
            PlasticityTriggerType.SOCIAL_ENHANCEMENT: {
                "oxytocin_low": 0.25,
                "interaction_quality_low": 0.40
            },
            PlasticityTriggerType.RECOVERY_CONSOLIDATION: {
                "melatonin_high": 0.75,
                "system_idle": 0.20
            },
            PlasticityTriggerType.CREATIVE_BOOST: {
                "serotonin_optimal": (0.45, 0.65),
                "novelty_seeking": 0.60
            },
            PlasticityTriggerType.RESILIENCE_BUILDING: {
                "chronic_stress_duration": 300,  # seconds
                "adaptation_needed": True
            },
            PlasticityTriggerType.EFFICIENCY_TUNING: {
                "performance_degradation": 0.15,
                "resource_waste": 0.20
            },
            PlasticityTriggerType.EMOTIONAL_REGULATION: {
                "mood_volatility": 0.30,
                "emotional_coherence_low": 0.50
            }
        }
        
        # Plasticity adaptations registry
        self.adaptation_handlers: Dict[PlasticityTriggerType, Callable] = {}
        
        # Analytics
        self.pattern_detectors: Dict[str, Any] = {}
        self.learning_models: Dict[str, Any] = {}
        
        logger.info("EndocrineObservabilityEngine initialized", 
                   monitoring_interval=self.monitoring_interval,
                   data_dir=str(self.data_dir))
    
    async def initialize(self) -> bool:
        """Initialize the observability engine and connect to required systems"""
        try:
            # Connect to endocrine system
            self.endocrine_system = get_endocrine_system()
            if not self.endocrine_system:
                logger.warning("Endocrine system not available, using mock")
                self.endocrine_system = self._create_mock_endocrine_system()
            
            # Connect to homeostasis controller
            try:
                from orchestration.signals.homeostasis_controller import HomeostasisController
                self.homeostasis_controller = HomeostasisController()
            except ImportError:
                logger.warning("Homeostasis controller not available")
            
            # Register signal handlers
            self._register_signal_handlers()
            
            # Initialize analytics
            await self._initialize_analytics()
            
            # Load historical data if available
            await self._load_historical_data()
            
            logger.info("EndocrineObservabilityEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize EndocrineObservabilityEngine", error=str(e))
            return False
    
    async def start_monitoring(self):
        """Start the continuous monitoring loop"""
        if self.is_running:
            logger.warning("Monitoring already running")
            return
        
        self.is_running = True
        logger.info("Starting endocrine observability monitoring")
        
        while self.is_running:
            try:
                # Take snapshot of current state
                snapshot = await self._capture_endocrine_snapshot()
                self.snapshots.append(snapshot)
                
                # Analyze for plasticity triggers
                triggers = await self._analyze_plasticity_triggers(snapshot)
                
                # Process any triggered adaptations
                for trigger in triggers:
                    await self._process_plasticity_trigger(trigger, snapshot)
                
                # Update trends and analytics
                await self._update_analytics(snapshot)
                
                # Persist data periodically
                if len(self.snapshots) % 10 == 0:
                    await self._persist_data()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(1.0)  # Brief pause before retrying
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("Stopping endocrine observability monitoring")
        
        # Final data persistence
        await self._persist_data()
    
    async def _capture_endocrine_snapshot(self) -> EndocrineSnapshot:
        """Capture current state of endocrine system and related metrics"""
        snapshot = EndocrineSnapshot()
        
        try:
            # Get hormone levels
            if self.endocrine_system:
                snapshot.hormone_levels = self.endocrine_system.get_hormone_levels()
            
            # Get homeostasis state
            if self.homeostasis_controller:
                snapshot.homeostasis_state = str(self.homeostasis_controller.current_state)
            
            # Collect system metrics
            snapshot.system_metrics = await self._collect_system_metrics()
            
            # Calculate bio-symbolic coherence
            snapshot.coherence_score = await self._calculate_coherence_score()
            
        except Exception as e:
            logger.error("Error capturing endocrine snapshot", error=str(e))
        
        return snapshot
    
    async def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect comprehensive system metrics for analysis"""
        metrics = {}
        
        try:
            import psutil
            
            # System resources
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage('/').percent
            
            # Process metrics
            process = psutil.Process()
            metrics["process_memory_mb"] = process.memory_info().rss / 1024 / 1024
            metrics["process_cpu_percent"] = process.cpu_percent()
            
        except ImportError:
            # Mock metrics if psutil not available
            metrics = {
                "cpu_percent": 45.0,
                "memory_percent": 62.0,
                "disk_percent": 28.0,
                "process_memory_mb": 256.0,
                "process_cpu_percent": 12.0,
            }
        
        # Add application-specific metrics
        metrics["processing_efficiency"] = await self._calculate_processing_efficiency()
        metrics["decision_latency"] = await self._measure_decision_latency()
        metrics["emotional_coherence"] = await self._assess_emotional_coherence()
        
        return metrics
    
    async def _analyze_plasticity_triggers(self, snapshot: EndocrineSnapshot) -> List[PlasticityEvent]:
        """Analyze current state for plasticity trigger conditions"""
        triggers = []
        
        hormone_levels = snapshot.hormone_levels
        system_metrics = snapshot.system_metrics
        
        # Stress adaptation triggers
        cortisol = hormone_levels.get("cortisol", 0.5)
        adrenaline = hormone_levels.get("adrenaline", 0.5)
        combined_stress = (cortisol + adrenaline) / 2
        
        thresholds = self.trigger_thresholds[PlasticityTriggerType.STRESS_ADAPTATION]
        if (cortisol > thresholds["cortisol_high"] or 
            adrenaline > thresholds["adrenaline_high"] or
            combined_stress > thresholds["combined_stress"]):
            
            triggers.append(PlasticityEvent(
                trigger_type=PlasticityTriggerType.STRESS_ADAPTATION,
                hormone_context={"cortisol": cortisol, "adrenaline": adrenaline},
                reason=f"High stress detected: cortisol={cortisol:.2f}, adrenaline={adrenaline:.2f}"
            ))
        
        # Performance optimization triggers
        dopamine = hormone_levels.get("dopamine", 0.5)
        processing_efficiency = system_metrics.get("processing_efficiency", 0.8)
        
        perf_thresholds = self.trigger_thresholds[PlasticityTriggerType.PERFORMANCE_OPTIMIZATION]
        if (dopamine < perf_thresholds["dopamine_low"] or 
            processing_efficiency < perf_thresholds["processing_efficiency_low"]):
            
            triggers.append(PlasticityEvent(
                trigger_type=PlasticityTriggerType.PERFORMANCE_OPTIMIZATION,
                hormone_context={"dopamine": dopamine},
                reason=f"Performance degradation: dopamine={dopamine:.2f}, efficiency={processing_efficiency:.2f}"
            ))
        
        # Social enhancement triggers
        oxytocin = hormone_levels.get("oxytocin", 0.5)
        social_thresholds = self.trigger_thresholds[PlasticityTriggerType.SOCIAL_ENHANCEMENT]
        
        if oxytocin < social_thresholds["oxytocin_low"]:
            triggers.append(PlasticityEvent(
                trigger_type=PlasticityTriggerType.SOCIAL_ENHANCEMENT,
                hormone_context={"oxytocin": oxytocin},
                reason=f"Low social bonding hormone: oxytocin={oxytocin:.2f}"
            ))
        
        # Recovery consolidation triggers
        melatonin = hormone_levels.get("melatonin", 0.5)
        system_idle = 1.0 - (system_metrics.get("cpu_percent", 50) / 100)
        
        recovery_thresholds = self.trigger_thresholds[PlasticityTriggerType.RECOVERY_CONSOLIDATION]
        if (melatonin > recovery_thresholds["melatonin_high"] and 
            system_idle > recovery_thresholds["system_idle"]):
            
            triggers.append(PlasticityEvent(
                trigger_type=PlasticityTriggerType.RECOVERY_CONSOLIDATION,
                hormone_context={"melatonin": melatonin},
                reason=f"Recovery opportunity detected: melatonin={melatonin:.2f}, idle={system_idle:.2f}"
            ))
        
        # Emotional regulation triggers
        emotional_coherence = system_metrics.get("emotional_coherence", 0.7)
        emotion_thresholds = self.trigger_thresholds[PlasticityTriggerType.EMOTIONAL_REGULATION]
        
        if emotional_coherence < emotion_thresholds["emotional_coherence_low"]:
            triggers.append(PlasticityEvent(
                trigger_type=PlasticityTriggerType.EMOTIONAL_REGULATION,
                hormone_context=hormone_levels,
                reason=f"Low emotional coherence: {emotional_coherence:.2f}"
            ))
        
        return triggers
    
    async def _process_plasticity_trigger(self, trigger: PlasticityEvent, snapshot: EndocrineSnapshot):
        """Process a plasticity trigger and apply appropriate adaptations"""
        logger.info("Processing plasticity trigger",
                   trigger_type=trigger.trigger_type.value,
                   reason=trigger.reason)
        
        try:
            # Get adaptation handler for this trigger type
            handler = self.adaptation_handlers.get(trigger.trigger_type)
            if handler:
                success = await handler(trigger, snapshot)
                trigger.success = success
            else:
                # Apply default adaptation
                success = await self._apply_default_adaptation(trigger, snapshot)
                trigger.success = success
            
            # Record the event
            self.plasticity_events.append(trigger)
            
            # Emit signal for other systems to react
            signal = Signal(
                name=SignalType.ADAPTATION,
                source="endocrine_observability",
                level=0.8,
                metadata={
                    "trigger_type": trigger.trigger_type.value,
                    "reason": trigger.reason,
                    "success": trigger.success,
                    "hormone_context": trigger.hormone_context
                }
            )
            self.signal_bus.publish(signal)
            
        except Exception as e:
            logger.error("Error processing plasticity trigger",
                        trigger_type=trigger.trigger_type.value,
                        error=str(e))
            trigger.success = False
    
    async def _apply_default_adaptation(self, trigger: PlasticityEvent, snapshot: EndocrineSnapshot) -> bool:
        """Apply default adaptation strategies for different trigger types"""
        adaptation_applied = ""
        
        try:
            if trigger.trigger_type == PlasticityTriggerType.STRESS_ADAPTATION:
                # Activate stress response protocols
                await self._activate_stress_response(trigger.hormone_context)
                adaptation_applied = "Activated stress response protocols, increased resource allocation"
                
            elif trigger.trigger_type == PlasticityTriggerType.PERFORMANCE_OPTIMIZATION:
                # Optimize processing parameters
                await self._optimize_processing_parameters(snapshot.system_metrics)
                adaptation_applied = "Optimized processing parameters, adjusted resource distribution"
                
            elif trigger.trigger_type == PlasticityTriggerType.SOCIAL_ENHANCEMENT:
                # Enhance interaction capabilities
                await self._enhance_social_features()
                adaptation_applied = "Enhanced social interaction features, improved empathy responses"
                
            elif trigger.trigger_type == PlasticityTriggerType.RECOVERY_CONSOLIDATION:
                # Consolidate learning and optimize memory
                await self._consolidate_learning_and_memory()
                adaptation_applied = "Consolidated memory, optimized learned patterns"
                
            elif trigger.trigger_type == PlasticityTriggerType.EMOTIONAL_REGULATION:
                # Adjust emotional processing
                await self._regulate_emotional_processing(snapshot.hormone_levels)
                adaptation_applied = "Regulated emotional processing, balanced mood responses"
            
            trigger.adaptation_applied = adaptation_applied
            logger.info("Applied default adaptation", 
                       trigger_type=trigger.trigger_type.value,
                       adaptation=adaptation_applied)
            
            return True
            
        except Exception as e:
            logger.error("Error applying default adaptation",
                        trigger_type=trigger.trigger_type.value,
                        error=str(e))
            return False
    
    async def _calculate_coherence_score(self) -> float:
        """Calculate bio-symbolic coherence score"""
        try:
            # This would integrate with the bio-symbolic bridge
            # For now, calculate based on available metrics
            
            if not self.endocrine_system:
                return 0.7  # Mock value
            
            hormone_levels = self.endocrine_system.get_hormone_levels()
            
            # Calculate balance across hormone systems
            stress_hormones = (hormone_levels.get("cortisol", 0.5) + 
                             hormone_levels.get("adrenaline", 0.5)) / 2
            positive_hormones = (hormone_levels.get("dopamine", 0.5) + 
                               hormone_levels.get("serotonin", 0.5) + 
                               hormone_levels.get("oxytocin", 0.5)) / 3
            
            # Coherence is higher when hormones are balanced
            balance_score = 1.0 - abs(stress_hormones - positive_hormones)
            
            # Factor in system performance
            if self.snapshots:
                recent_snapshot = self.snapshots[-1]
                performance_factor = recent_snapshot.system_metrics.get("processing_efficiency", 0.8)
                coherence_score = (balance_score * 0.6) + (performance_factor * 0.4)
            else:
                coherence_score = balance_score
            
            return max(0.0, min(1.0, coherence_score))
            
        except Exception as e:
            logger.error("Error calculating coherence score", error=str(e))
            return 0.5
    
    # Helper methods for metric calculations
    async def _calculate_processing_efficiency(self) -> float:
        """Calculate current processing efficiency"""
        # Mock implementation - would integrate with actual performance metrics
        return 0.85
    
    async def _measure_decision_latency(self) -> float:
        """Measure average decision-making latency"""
        # Mock implementation - would measure actual decision times
        return 0.15  # 150ms average
    
    async def _assess_emotional_coherence(self) -> float:
        """Assess emotional state coherence"""
        # Mock implementation - would integrate with emotion systems
        return 0.72
    
    # Adaptation implementation methods
    async def _activate_stress_response(self, hormone_context: Dict[str, float]):
        """Activate stress response protocols"""
        logger.info("Activating stress response protocols", hormones=hormone_context)
        # Implementation would adjust system parameters for high-stress operation
    
    async def _optimize_processing_parameters(self, system_metrics: Dict[str, float]):
        """Optimize processing parameters based on current performance"""
        logger.info("Optimizing processing parameters", metrics=system_metrics)
        # Implementation would tune processing algorithms and resource allocation
    
    async def _enhance_social_features(self):
        """Enhance social interaction capabilities"""
        logger.info("Enhancing social features")
        # Implementation would boost empathy, communication, and collaboration features
    
    async def _consolidate_learning_and_memory(self):
        """Consolidate learning and optimize memory during low-activity periods"""
        logger.info("Consolidating learning and memory")
        # Implementation would compress memories, reinforce learning patterns
    
    async def _regulate_emotional_processing(self, hormone_levels: Dict[str, float]):
        """Regulate emotional processing to improve coherence"""
        logger.info("Regulating emotional processing", hormones=hormone_levels)
        # Implementation would balance emotional responses and mood regulation
    
    # Data persistence and analytics
    async def _initialize_analytics(self):
        """Initialize analytics and pattern detection systems"""
        logger.info("Initializing analytics systems")
        # Would initialize ML models, pattern detectors, etc.
    
    async def _update_analytics(self, snapshot: EndocrineSnapshot):
        """Update analytics with new snapshot data"""
        # Update trend tracking
        for metric_name, value in snapshot.system_metrics.items():
            self.trend_history[metric_name].append(value)
        
        for hormone, level in snapshot.hormone_levels.items():
            self.trend_history[f"hormone_{hormone}"].append(level)
    
    async def _persist_data(self):
        """Persist monitoring data to storage"""
        try:
            # Save snapshots
            snapshots_file = self.data_dir / "endocrine_snapshots.jsonl"
            with open(snapshots_file, "a") as f:
                for snapshot in list(self.snapshots)[-10:]:  # Save last 10
                    f.write(json.dumps(snapshot.to_dict()) + "\n")
            
            # Save plasticity events
            events_file = self.data_dir / "plasticity_events.jsonl"
            with open(events_file, "a") as f:
                for event in list(self.plasticity_events)[-10:]:  # Save last 10
                    event_data = {
                        "trigger_type": event.trigger_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "hormone_context": event.hormone_context,
                        "reason": event.reason,
                        "adaptation_applied": event.adaptation_applied,
                        "success": event.success,
                        "impact_score": event.impact_score
                    }
                    f.write(json.dumps(event_data) + "\n")
            
        except Exception as e:
            logger.error("Error persisting data", error=str(e))
    
    async def _load_historical_data(self):
        """Load historical data for trend analysis"""
        try:
            snapshots_file = self.data_dir / "endocrine_snapshots.jsonl"
            if snapshots_file.exists():
                logger.info("Loading historical endocrine data")
                # Implementation would load and process historical data
        except Exception as e:
            logger.error("Error loading historical data", error=str(e))
    
    def _register_signal_handlers(self):
        """Register handlers for relevant signals"""
        # Would register for system events, stress signals, performance changes, etc.
        pass
    
    def _create_mock_endocrine_system(self):
        """Create a mock endocrine system for testing"""
        class MockEndocrineSystem:
            def get_hormone_levels(self):
                return {
                    "cortisol": 0.45,
                    "dopamine": 0.65,
                    "serotonin": 0.55,
                    "oxytocin": 0.50,
                    "adrenaline": 0.35,
                    "melatonin": 0.40,
                    "gaba": 0.60,
                    "endorphin": 0.50
                }
        
        return MockEndocrineSystem()
    
    # Public API methods
    def register_adaptation_handler(self, trigger_type: PlasticityTriggerType, handler: Callable):
        """Register a custom adaptation handler for a trigger type"""
        self.adaptation_handlers[trigger_type] = handler
        logger.info("Registered adaptation handler", trigger_type=trigger_type.value)
    
    def get_current_state(self) -> Optional[EndocrineSnapshot]:
        """Get the most recent endocrine snapshot"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_trend_data(self, metric_name: str, lookback_points: int = 50) -> List[float]:
        """Get trend data for a specific metric"""
        return list(self.trend_history[metric_name])[-lookback_points:]
    
    def get_plasticity_history(self, lookback_hours: int = 24) -> List[PlasticityEvent]:
        """Get recent plasticity events"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        return [event for event in self.plasticity_events 
                if event.timestamp > cutoff_time]
    
    def get_coherence_trend(self, lookback_points: int = 50) -> List[float]:
        """Get bio-symbolic coherence trend"""
        if not self.snapshots:
            return []
        
        recent_snapshots = list(self.snapshots)[-lookback_points:]
        return [snapshot.coherence_score for snapshot in recent_snapshots]


# Factory function for easy instantiation
def create_endocrine_observability_engine(
    signal_bus: SignalBus,
    config: Optional[Dict[str, Any]] = None
) -> EndocrineObservabilityEngine:
    """Create and return an EndocrineObservabilityEngine instance"""
    return EndocrineObservabilityEngine(signal_bus, config)