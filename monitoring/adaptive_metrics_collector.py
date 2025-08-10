#!/usr/bin/env python3
"""
Adaptive Metrics Collector
==========================
Advanced metrics collection system that gathers multi-dimensional data
with contextual awareness, biological correlation, and predictive analysis.
"""

import asyncio
import json
import math
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import structlog

from orchestration.signals.signal_bus import SignalBus, Signal, SignalType
from .endocrine_observability_engine import EndocrineSnapshot, PlasticityTriggerType

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """Types of metrics collected by the system"""
    
    SYSTEM_PERFORMANCE = "system_performance"
    BIOLOGICAL_STATE = "biological_state"
    COGNITIVE_LOAD = "cognitive_load"
    INTERACTION_QUALITY = "interaction_quality"
    LEARNING_PROGRESS = "learning_progress"
    EMOTIONAL_STATE = "emotional_state"
    DECISION_QUALITY = "decision_quality"
    COHERENCE_MEASURE = "coherence_measure"
    ADAPTATION_IMPACT = "adaptation_impact"
    PREDICTIVE_INDICATOR = "predictive_indicator"


class MetricContext(Enum):
    """Contextual categories for metric interpretation"""
    
    NORMAL_OPERATION = "normal_operation"
    HIGH_STRESS = "high_stress"
    LEARNING_MODE = "learning_mode"
    SOCIAL_INTERACTION = "social_interaction"
    RECOVERY_PHASE = "recovery_phase"
    CREATIVE_MODE = "creative_mode"
    PROBLEM_SOLVING = "problem_solving"
    ADAPTATION_ACTIVE = "adaptation_active"


@dataclass
class MetricDefinition:
    """Definition of a metric including collection and analysis parameters"""
    
    name: str
    metric_type: MetricType
    collection_interval: float = 5.0  # seconds
    retention_limit: int = 1000
    aggregation_window: int = 60  # seconds for rolling aggregation
    correlation_targets: List[str] = field(default_factory=list)
    context_sensitive: bool = True
    biological_relevance: float = 0.0  # 0-1 scale
    predictive_value: float = 0.0  # 0-1 scale
    anomaly_detection: bool = True
    normalization_range: Tuple[float, float] = (0.0, 1.0)


@dataclass
class MetricDataPoint:
    """Individual metric measurement with context"""
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    value: float = 0.0
    context: MetricContext = MetricContext.NORMAL_OPERATION
    biological_correlation: Dict[str, float] = field(default_factory=dict)
    quality_score: float = 1.0  # Data quality indicator
    anomaly_score: float = 0.0  # Anomaly detection score
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextualAnalysis:
    """Analysis of metrics within a specific context"""
    
    context: MetricContext
    time_window: timedelta
    metric_statistics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    correlations: Dict[str, float] = field(default_factory=dict)
    trends: Dict[str, str] = field(default_factory=dict)  # "improving", "declining", "stable"
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    predictions: Dict[str, float] = field(default_factory=dict)


class AdaptiveMetricsCollector:
    """
    Intelligent metrics collection system that adapts its behavior based on
    system state, biological context, and predictive requirements.
    """
    
    def __init__(
        self,
        signal_bus: SignalBus,
        config: Optional[Dict[str, Any]] = None
    ):
        self.signal_bus = signal_bus
        self.config = config or {}
        
        # Core collection state
        self.is_collecting = False
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        
        # Metric definitions and storage
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_data: Dict[str, deque] = {}
        self.context_history: deque = deque(maxlen=1000)
        self.current_context = MetricContext.NORMAL_OPERATION
        
        # Analysis and correlation
        self.correlation_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.contextual_analyses: Dict[MetricContext, ContextualAnalysis] = {}
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {}
        self.predictive_models: Dict[str, PredictiveModel] = {}
        
        # Biological integration
        self.biological_correlator = BiologicalCorrelator()
        self.current_endocrine_state: Optional[EndocrineSnapshot] = None
        
        # Adaptive behavior
        self.adaptive_intervals: Dict[str, float] = {}
        self.context_triggers: Dict[MetricContext, List[Callable]] = defaultdict(list)
        self.collection_priorities: Dict[str, float] = {}
        
        # Performance optimization
        self.collection_batch_size = self.config.get("batch_size", 10)
        self.max_concurrent_collections = self.config.get("max_concurrent", 50)
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        logger.info("AdaptiveMetricsCollector initialized",
                   metrics_count=len(self.metric_definitions),
                   batch_size=self.collection_batch_size)
    
    def _initialize_default_metrics(self):
        """Initialize default metric definitions"""
        
        # System performance metrics
        self.register_metric(MetricDefinition(
            name="cpu_utilization",
            metric_type=MetricType.SYSTEM_PERFORMANCE,
            collection_interval=2.0,
            biological_relevance=0.7,  # Correlates with stress hormones
            predictive_value=0.8,
            correlation_targets=["memory_usage", "response_time"]
        ))
        
        self.register_metric(MetricDefinition(
            name="memory_efficiency",
            metric_type=MetricType.SYSTEM_PERFORMANCE,
            collection_interval=3.0,
            biological_relevance=0.6,
            predictive_value=0.7,
            correlation_targets=["cpu_utilization", "decision_latency"]
        ))
        
        self.register_metric(MetricDefinition(
            name="response_time",
            metric_type=MetricType.SYSTEM_PERFORMANCE,
            collection_interval=1.0,
            biological_relevance=0.8,
            predictive_value=0.9,
            correlation_targets=["cognitive_load", "stress_level"]
        ))
        
        # Cognitive metrics
        self.register_metric(MetricDefinition(
            name="decision_confidence",
            metric_type=MetricType.DECISION_QUALITY,
            collection_interval=5.0,
            biological_relevance=0.9,  # Strong correlation with dopamine/serotonin
            predictive_value=0.8,
            correlation_targets=["hormone_dopamine", "processing_depth"]
        ))
        
        self.register_metric(MetricDefinition(
            name="attention_focus",
            metric_type=MetricType.COGNITIVE_LOAD,
            collection_interval=4.0,
            biological_relevance=0.8,
            predictive_value=0.7,
            correlation_targets=["hormone_adrenaline", "task_complexity"]
        ))
        
        self.register_metric(MetricDefinition(
            name="learning_rate",
            metric_type=MetricType.LEARNING_PROGRESS,
            collection_interval=10.0,
            biological_relevance=0.9,
            predictive_value=0.8,
            correlation_targets=["hormone_dopamine", "memory_consolidation"]
        ))
        
        # Biological state metrics
        self.register_metric(MetricDefinition(
            name="stress_indicator",
            metric_type=MetricType.BIOLOGICAL_STATE,
            collection_interval=3.0,
            biological_relevance=1.0,
            predictive_value=0.9,
            correlation_targets=["hormone_cortisol", "hormone_adrenaline", "response_time"]
        ))
        
        self.register_metric(MetricDefinition(
            name="emotional_coherence",
            metric_type=MetricType.EMOTIONAL_STATE,
            collection_interval=5.0,
            biological_relevance=0.9,
            predictive_value=0.7,
            correlation_targets=["hormone_serotonin", "social_interaction_quality"]
        ))
        
        # Interaction quality metrics
        self.register_metric(MetricDefinition(
            name="communication_clarity",
            metric_type=MetricType.INTERACTION_QUALITY,
            collection_interval=8.0,
            biological_relevance=0.6,
            predictive_value=0.6,
            correlation_targets=["emotional_state", "cognitive_load"]
        ))
        
        self.register_metric(MetricDefinition(
            name="empathy_engagement",
            metric_type=MetricType.INTERACTION_QUALITY,
            collection_interval=7.0,
            biological_relevance=0.8,
            predictive_value=0.5,
            correlation_targets=["hormone_oxytocin", "social_context"]
        ))
    
    def register_metric(self, metric_def: MetricDefinition):
        """Register a new metric for collection"""
        self.metric_definitions[metric_def.name] = metric_def
        self.metric_data[metric_def.name] = deque(maxlen=metric_def.retention_limit)
        self.anomaly_detectors[metric_def.name] = AnomalyDetector(metric_def)
        self.predictive_models[metric_def.name] = PredictiveModel(metric_def)
        
        logger.info("Registered metric", 
                   name=metric_def.name, 
                   type=metric_def.metric_type.value,
                   biological_relevance=metric_def.biological_relevance)
    
    async def start_collection(self):
        """Start adaptive metric collection"""
        if self.is_collecting:
            logger.warning("Metric collection already running")
            return
        
        self.is_collecting = True
        logger.info("Starting adaptive metrics collection")
        
        # Start collection tasks for each metric
        for metric_name, metric_def in self.metric_definitions.items():
            task = asyncio.create_task(self._collect_metric_loop(metric_name, metric_def))
            self.collection_tasks[metric_name] = task
        
        # Start context monitoring and analysis
        asyncio.create_task(self._context_monitoring_loop())
        asyncio.create_task(self._correlation_analysis_loop())
        asyncio.create_task(self._adaptive_tuning_loop())
    
    async def stop_collection(self):
        """Stop metric collection"""
        self.is_collecting = False
        logger.info("Stopping metrics collection")
        
        # Cancel all collection tasks
        for task in self.collection_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.collection_tasks:
            await asyncio.gather(*self.collection_tasks.values(), return_exceptions=True)
        
        self.collection_tasks.clear()
    
    async def _collect_metric_loop(self, metric_name: str, metric_def: MetricDefinition):
        """Main collection loop for a specific metric"""
        collector_func = self._get_metric_collector(metric_name)
        
        while self.is_collecting:
            try:
                # Get adaptive interval (may change based on context)
                interval = self.adaptive_intervals.get(metric_name, metric_def.collection_interval)
                
                # Collect the metric value
                value = await collector_func()
                
                # Create data point with context and biological correlation
                data_point = MetricDataPoint(
                    value=value,
                    context=self.current_context,
                    biological_correlation=await self._correlate_with_biology(metric_name, value),
                    quality_score=await self._assess_data_quality(metric_name, value),
                    metadata=await self._gather_metric_metadata(metric_name)
                )
                
                # Anomaly detection
                if metric_def.anomaly_detection:
                    data_point.anomaly_score = self.anomaly_detectors[metric_name].detect(data_point)
                
                # Store data point
                self.metric_data[metric_name].append(data_point)
                
                # Emit signal for real-time consumers
                await self._emit_metric_signal(metric_name, data_point)
                
                # Update predictive models
                self.predictive_models[metric_name].update(data_point)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error("Error collecting metric", 
                           metric=metric_name, 
                           error=str(e))
                await asyncio.sleep(metric_def.collection_interval)
    
    def _get_metric_collector(self, metric_name: str) -> Callable:
        """Get the collector function for a specific metric"""
        
        collectors = {
            "cpu_utilization": self._collect_cpu_utilization,
            "memory_efficiency": self._collect_memory_efficiency,
            "response_time": self._collect_response_time,
            "decision_confidence": self._collect_decision_confidence,
            "attention_focus": self._collect_attention_focus,
            "learning_rate": self._collect_learning_rate,
            "stress_indicator": self._collect_stress_indicator,
            "emotional_coherence": self._collect_emotional_coherence,
            "communication_clarity": self._collect_communication_clarity,
            "empathy_engagement": self._collect_empathy_engagement
        }
        
        return collectors.get(metric_name, self._collect_default_metric)
    
    # Individual metric collection methods
    async def _collect_cpu_utilization(self) -> float:
        """Collect CPU utilization metric"""
        try:
            import psutil
            return psutil.cpu_percent(interval=None) / 100.0
        except ImportError:
            # Mock value that varies over time
            return 0.3 + 0.2 * math.sin(time.time() / 10)
    
    async def _collect_memory_efficiency(self) -> float:
        """Collect memory efficiency metric"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return 1.0 - (mem.percent / 100.0)
        except ImportError:
            return 0.7 + 0.1 * math.cos(time.time() / 15)
    
    async def _collect_response_time(self) -> float:
        """Collect response time metric (normalized to 0-1)"""
        # Would measure actual system response times
        # For now, simulate based on system load
        cpu_load = await self._collect_cpu_utilization()
        base_time = 0.1 + (cpu_load * 0.4)  # 100ms to 500ms range
        return min(1.0, base_time)
    
    async def _collect_decision_confidence(self) -> float:
        """Collect decision-making confidence metric"""
        # Would integrate with decision-making systems
        # Simulate based on biological state
        if self.current_endocrine_state:
            dopamine = self.current_endocrine_state.hormone_levels.get("dopamine", 0.5)
            serotonin = self.current_endocrine_state.hormone_levels.get("serotonin", 0.5)
            confidence = (dopamine * 0.6 + serotonin * 0.4)
            return max(0.1, min(1.0, confidence))
        return 0.6
    
    async def _collect_attention_focus(self) -> float:
        """Collect attention focus metric"""
        # Would measure actual attention patterns
        # Simulate based on current context and biological state
        context_focus_map = {
            MetricContext.NORMAL_OPERATION: 0.7,
            MetricContext.HIGH_STRESS: 0.9,
            MetricContext.LEARNING_MODE: 0.8,
            MetricContext.CREATIVE_MODE: 0.6,
            MetricContext.SOCIAL_INTERACTION: 0.75,
            MetricContext.PROBLEM_SOLVING: 0.95,
            MetricContext.RECOVERY_PHASE: 0.4,
            MetricContext.ADAPTATION_ACTIVE: 0.85
        }
        
        base_focus = context_focus_map.get(self.current_context, 0.7)
        
        # Adjust based on adrenaline levels
        if self.current_endocrine_state:
            adrenaline = self.current_endocrine_state.hormone_levels.get("adrenaline", 0.5)
            focus = base_focus + (adrenaline - 0.5) * 0.2
        else:
            focus = base_focus
        
        return max(0.0, min(1.0, focus))
    
    async def _collect_learning_rate(self) -> float:
        """Collect learning rate metric"""
        # Would measure actual learning progress
        # Simulate based on dopamine and context
        if self.current_endocrine_state:
            dopamine = self.current_endocrine_state.hormone_levels.get("dopamine", 0.5)
            base_rate = dopamine * 0.8
        else:
            base_rate = 0.5
        
        # Higher in learning mode
        if self.current_context == MetricContext.LEARNING_MODE:
            base_rate *= 1.3
        elif self.current_context == MetricContext.RECOVERY_PHASE:
            base_rate *= 1.2  # Consolidation during recovery
        
        return max(0.0, min(1.0, base_rate))
    
    async def _collect_stress_indicator(self) -> float:
        """Collect stress indicator metric"""
        if self.current_endocrine_state:
            cortisol = self.current_endocrine_state.hormone_levels.get("cortisol", 0.5)
            adrenaline = self.current_endocrine_state.hormone_levels.get("adrenaline", 0.5)
            stress = (cortisol * 0.6 + adrenaline * 0.4)
        else:
            # Mock stress based on system load
            cpu_load = await self._collect_cpu_utilization()
            stress = min(1.0, cpu_load * 1.2)
        
        return max(0.0, min(1.0, stress))
    
    async def _collect_emotional_coherence(self) -> float:
        """Collect emotional coherence metric"""
        if self.current_endocrine_state:
            serotonin = self.current_endocrine_state.hormone_levels.get("serotonin", 0.5)
            oxytocin = self.current_endocrine_state.hormone_levels.get("oxytocin", 0.5)
            dopamine = self.current_endocrine_state.hormone_levels.get("dopamine", 0.5)
            
            positive_emotions = (serotonin + oxytocin + dopamine) / 3
            coherence = positive_emotions * 0.8 + 0.2  # Base coherence
        else:
            coherence = 0.7
        
        return max(0.0, min(1.0, coherence))
    
    async def _collect_communication_clarity(self) -> float:
        """Collect communication clarity metric"""
        # Would analyze actual communication patterns
        # Simulate based on cognitive load and emotional state
        cognitive_load = await self._collect_attention_focus()
        emotional_coherence = await self._collect_emotional_coherence()
        
        clarity = (emotional_coherence * 0.6) + ((1.0 - cognitive_load) * 0.4)
        return max(0.3, min(1.0, clarity))
    
    async def _collect_empathy_engagement(self) -> float:
        """Collect empathy engagement metric"""
        if self.current_endocrine_state:
            oxytocin = self.current_endocrine_state.hormone_levels.get("oxytocin", 0.5)
            serotonin = self.current_endocrine_state.hormone_levels.get("serotonin", 0.5)
            empathy = (oxytocin * 0.7 + serotonin * 0.3)
        else:
            empathy = 0.6
        
        # Higher during social interactions
        if self.current_context == MetricContext.SOCIAL_INTERACTION:
            empathy *= 1.2
        
        return max(0.0, min(1.0, empathy))
    
    async def _collect_default_metric(self) -> float:
        """Default metric collector for undefined metrics"""
        return 0.5 + 0.1 * math.sin(time.time() / 20)
    
    async def _correlate_with_biology(self, metric_name: str, value: float) -> Dict[str, float]:
        """Correlate metric with current biological state"""
        correlations = {}
        
        if self.current_endocrine_state:
            correlations = self.biological_correlator.calculate_correlations(
                metric_name, value, self.current_endocrine_state
            )
        
        return correlations
    
    async def _assess_data_quality(self, metric_name: str, value: float) -> float:
        """Assess the quality of collected data"""
        # Simple quality assessment based on value range and stability
        metric_def = self.metric_definitions[metric_name]
        min_val, max_val = metric_def.normalization_range
        
        # Quality decreases if value is outside expected range
        if min_val <= value <= max_val:
            quality = 1.0
        else:
            # Penalize out-of-range values
            distance = min(abs(value - min_val), abs(value - max_val))
            quality = max(0.1, 1.0 - distance)
        
        return quality
    
    async def _gather_metric_metadata(self, metric_name: str) -> Dict[str, Any]:
        """Gather additional metadata for the metric"""
        return {
            "context": self.current_context.value,
            "collection_time": datetime.now(timezone.utc).isoformat(),
            "system_state": {
                "is_adapting": len(self.collection_tasks) > 0,
                "context_stability": self._calculate_context_stability()
            }
        }
    
    def _calculate_context_stability(self) -> float:
        """Calculate how stable the current context has been"""
        if len(self.context_history) < 5:
            return 0.5
        
        recent_contexts = list(self.context_history)[-10:]
        current_context_count = sum(1 for ctx in recent_contexts if ctx == self.current_context)
        
        return current_context_count / len(recent_contexts)
    
    async def _emit_metric_signal(self, metric_name: str, data_point: MetricDataPoint):
        """Emit signal for real-time metric consumers"""
        signal = Signal(
            name=SignalType.METRIC_UPDATE,
            source="adaptive_metrics_collector",
            level=data_point.value,
            metadata={
                "metric_name": metric_name,
                "context": data_point.context.value,
                "quality_score": data_point.quality_score,
                "anomaly_score": data_point.anomaly_score,
                "biological_correlation": data_point.biological_correlation
            }
        )
        self.signal_bus.publish(signal)
    
    # Context and analysis loops
    async def _context_monitoring_loop(self):
        """Monitor and update current context"""
        while self.is_collecting:
            try:
                new_context = await self._determine_current_context()
                if new_context != self.current_context:
                    logger.info("Context changed", 
                               from_context=self.current_context.value,
                               to_context=new_context.value)
                    
                    self.current_context = new_context
                    self.context_history.append(new_context)
                    
                    # Trigger context-specific adjustments
                    await self._adapt_to_context_change(new_context)
                
                await asyncio.sleep(2.0)  # Check context every 2 seconds
                
            except Exception as e:
                logger.error("Error in context monitoring", error=str(e))
                await asyncio.sleep(5.0)
    
    async def _correlation_analysis_loop(self):
        """Analyze correlations between metrics"""
        while self.is_collecting:
            try:
                await self._update_correlation_matrix()
                await asyncio.sleep(30.0)  # Update correlations every 30 seconds
                
            except Exception as e:
                logger.error("Error in correlation analysis", error=str(e))
                await asyncio.sleep(60.0)
    
    async def _adaptive_tuning_loop(self):
        """Adaptively tune collection intervals and priorities"""
        while self.is_collecting:
            try:
                await self._tune_collection_parameters()
                await asyncio.sleep(60.0)  # Tune every minute
                
            except Exception as e:
                logger.error("Error in adaptive tuning", error=str(e))
                await asyncio.sleep(120.0)
    
    async def _determine_current_context(self) -> MetricContext:
        """Determine current operational context"""
        
        # Analyze recent metrics to infer context
        stress_level = await self._collect_stress_indicator()
        attention_focus = await self._collect_attention_focus()
        cpu_load = await self._collect_cpu_utilization()
        
        # Context determination logic
        if stress_level > 0.7:
            return MetricContext.HIGH_STRESS
        elif attention_focus > 0.9 and cpu_load > 0.8:
            return MetricContext.PROBLEM_SOLVING
        elif self.current_endocrine_state:
            melatonin = self.current_endocrine_state.hormone_levels.get("melatonin", 0.5)
            if melatonin > 0.7:
                return MetricContext.RECOVERY_PHASE
        
        # Default to normal operation
        return MetricContext.NORMAL_OPERATION
    
    async def _adapt_to_context_change(self, new_context: MetricContext):
        """Adapt collection behavior based on context change"""
        
        # Adjust collection intervals based on context
        context_adjustments = {
            MetricContext.HIGH_STRESS: {
                "stress_indicator": 1.0,  # Collect stress metrics more frequently
                "response_time": 0.5,
                "attention_focus": 1.0
            },
            MetricContext.LEARNING_MODE: {
                "learning_rate": 2.0,
                "decision_confidence": 3.0,
                "attention_focus": 2.0
            },
            MetricContext.SOCIAL_INTERACTION: {
                "empathy_engagement": 2.0,
                "communication_clarity": 3.0,
                "emotional_coherence": 2.0
            },
            MetricContext.RECOVERY_PHASE: {
                "cpu_utilization": 10.0,  # Less frequent during recovery
                "memory_efficiency": 8.0,
                "learning_rate": 5.0  # Monitor consolidation
            }
        }
        
        adjustments = context_adjustments.get(new_context, {})
        for metric_name, interval_multiplier in adjustments.items():
            if metric_name in self.metric_definitions:
                base_interval = self.metric_definitions[metric_name].collection_interval
                self.adaptive_intervals[metric_name] = base_interval * interval_multiplier
    
    # Public API methods
    def update_endocrine_state(self, endocrine_state: EndocrineSnapshot):
        """Update current endocrine state for biological correlation"""
        self.current_endocrine_state = endocrine_state
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current values for all metrics"""
        current_metrics = {}
        for metric_name in self.metric_definitions:
            if self.metric_data[metric_name]:
                latest_point = self.metric_data[metric_name][-1]
                current_metrics[metric_name] = latest_point.value
        
        return current_metrics
    
    def get_metric_trend(self, metric_name: str, lookback_minutes: int = 30) -> List[float]:
        """Get trend data for a specific metric"""
        if metric_name not in self.metric_data:
            return []
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes)
        recent_data = [
            point.value for point in self.metric_data[metric_name]
            if point.timestamp > cutoff_time
        ]
        
        return recent_data
    
    def get_contextual_analysis(self, context: MetricContext, lookback_hours: int = 2) -> ContextualAnalysis:
        """Get analysis of metrics within a specific context"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        
        analysis = ContextualAnalysis(
            context=context,
            time_window=timedelta(hours=lookback_hours)
        )
        
        # Analyze each metric within this context
        for metric_name, data_points in self.metric_data.items():
            context_points = [
                point for point in data_points
                if point.context == context and point.timestamp > cutoff_time
            ]
            
            if context_points:
                values = [point.value for point in context_points]
                analysis.metric_statistics[metric_name] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
                
                # Simple trend analysis
                if len(values) >= 3:
                    first_third = values[:len(values)//3]
                    last_third = values[-len(values)//3:]
                    
                    first_avg = statistics.mean(first_third)
                    last_avg = statistics.mean(last_third)
                    
                    if last_avg > first_avg * 1.1:
                        analysis.trends[metric_name] = "improving"
                    elif last_avg < first_avg * 0.9:
                        analysis.trends[metric_name] = "declining"
                    else:
                        analysis.trends[metric_name] = "stable"
        
        return analysis
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """Get statistics about the collection process"""
        return {
            "is_collecting": self.is_collecting,
            "metrics_count": len(self.metric_definitions),
            "active_collectors": len(self.collection_tasks),
            "current_context": self.current_context.value,
            "total_data_points": sum(len(data) for data in self.metric_data.values()),
            "adaptive_intervals": dict(self.adaptive_intervals),
            "context_stability": self._calculate_context_stability()
        }


class AnomalyDetector:
    """Anomaly detection for individual metrics"""
    
    def __init__(self, metric_def: MetricDefinition):
        self.metric_def = metric_def
        self.baseline_window = 50
        self.sensitivity = 2.0  # Standard deviations for anomaly threshold
        self.recent_values = deque(maxlen=self.baseline_window)
    
    def detect(self, data_point: MetricDataPoint) -> float:
        """Detect anomaly score (0-1) for the data point"""
        self.recent_values.append(data_point.value)
        
        if len(self.recent_values) < 10:
            return 0.0  # Not enough data for detection
        
        try:
            mean_val = statistics.mean(self.recent_values)
            std_val = statistics.stdev(self.recent_values)
            
            if std_val == 0:
                return 0.0
            
            # Z-score based anomaly detection
            z_score = abs(data_point.value - mean_val) / std_val
            
            if z_score > self.sensitivity:
                # Normalize to 0-1 scale
                anomaly_score = min(1.0, (z_score - self.sensitivity) / self.sensitivity)
                return anomaly_score
            
            return 0.0
            
        except statistics.StatisticsError:
            return 0.0


class PredictiveModel:
    """Simple predictive model for metric forecasting"""
    
    def __init__(self, metric_def: MetricDefinition):
        self.metric_def = metric_def
        self.history_window = 100
        self.trend_values = deque(maxlen=self.history_window)
    
    def update(self, data_point: MetricDataPoint):
        """Update model with new data point"""
        self.trend_values.append(data_point.value)
    
    def predict(self, steps_ahead: int = 5) -> float:
        """Predict metric value steps ahead"""
        if len(self.trend_values) < 10:
            return 0.5  # Default prediction
        
        # Simple linear trend extrapolation
        recent_values = list(self.trend_values)[-20:]
        if len(recent_values) < 3:
            return recent_values[-1] if recent_values else 0.5
        
        # Calculate trend
        x_vals = list(range(len(recent_values)))
        y_vals = recent_values
        
        # Simple linear regression (least squares)
        n = len(recent_values)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(x * x for x in x_vals)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return recent_values[-1]
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict
        future_x = len(recent_values) + steps_ahead - 1
        prediction = slope * future_x + intercept
        
        # Clamp to reasonable range
        min_val, max_val = self.metric_def.normalization_range
        return max(min_val, min(max_val, prediction))


class BiologicalCorrelator:
    """Correlates metrics with biological/hormonal state"""
    
    def __init__(self):
        self.correlation_cache = {}
    
    def calculate_correlations(
        self, 
        metric_name: str, 
        metric_value: float, 
        endocrine_state: EndocrineSnapshot
    ) -> Dict[str, float]:
        """Calculate correlations between metric and biological state"""
        correlations = {}
        
        hormone_levels = endocrine_state.hormone_levels
        
        # Define expected correlations for different metrics
        metric_correlations = {
            "stress_indicator": ["cortisol", "adrenaline"],
            "decision_confidence": ["dopamine", "serotonin"],
            "attention_focus": ["adrenaline", "dopamine"],
            "learning_rate": ["dopamine"],
            "emotional_coherence": ["serotonin", "oxytocin"],
            "empathy_engagement": ["oxytocin"],
            "response_time": ["cortisol", "adrenaline"]
        }
        
        relevant_hormones = metric_correlations.get(metric_name, [])
        
        for hormone in relevant_hormones:
            if hormone in hormone_levels:
                hormone_level = hormone_levels[hormone]
                
                # Simple correlation calculation
                # (This would be more sophisticated in practice)
                if hormone in ["cortisol", "adrenaline"]:
                    # Stress hormones - often positive correlation with stress metrics
                    correlation = self._calculate_simple_correlation(metric_value, hormone_level)
                else:
                    # Positive hormones - often positive correlation with performance metrics
                    correlation = self._calculate_simple_correlation(metric_value, hormone_level)
                
                correlations[f"hormone_{hormone}"] = correlation
        
        return correlations
    
    def _calculate_simple_correlation(self, value1: float, value2: float) -> float:
        """Calculate simple correlation between two values"""
        # Simplified Pearson-like correlation
        # In practice, this would use historical data
        normalized_diff = abs(value1 - value2)
        correlation = 1.0 - normalized_diff
        return max(-1.0, min(1.0, correlation))


# Factory function
def create_adaptive_metrics_collector(
    signal_bus: SignalBus,
    config: Optional[Dict[str, Any]] = None
) -> AdaptiveMetricsCollector:
    """Create and return an AdaptiveMetricsCollector instance"""
    return AdaptiveMetricsCollector(signal_bus, config)