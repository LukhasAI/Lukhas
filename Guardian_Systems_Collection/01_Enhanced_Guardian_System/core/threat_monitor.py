#!/usr/bin/env python3
"""
Threat Monitor - Advanced system threat detection and monitoring
Monitors system stability, entropy, consciousness drift, and anomalies
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque
import random  # For simulation - replace with actual metrics in production

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ThreatIndicator:
    """Represents a detected threat"""
    threat_id: str
    threat_type: str
    severity: ThreatLevel
    confidence: float
    timestamp: float
    source: str
    description: str
    context: Dict
    recommended_actions: List[str]
    symbolic_signature: List[str]


class ThreatMonitor:
    """
    Advanced threat detection and monitoring system
    Monitors various system metrics for stability and security threats
    """
    
    # Threat detection thresholds
    THRESHOLDS = {
        "consciousness_drift": 0.3,
        "entropy_spike": 0.4,
        "memory_fragmentation": 0.6,
        "pattern_disruption": 0.5,
        "response_time_spike": 2.0,
        "error_rate_spike": 0.1,
        "unusual_activity": 0.7
    }
    
    # Symbolic patterns for different threat types
    THREAT_SYMBOLS = {
        "consciousness_drift": ["🧠", "🌊", "⚠️"],
        "entropy_spike": ["🔥", "📈", "🚨"],
        "memory_fragmentation": ["🧩", "💥", "⚠️"],
        "pattern_disruption": ["🔄", "❌", "🚨"],
        "security_breach": ["🔓", "🚨", "⚠️"],
        "system_overload": ["💻", "🔥", "🚨"],
        "unknown_threat": ["❓", "⚠️", "🔍"]
    }
    
    def __init__(self, 
                 alert_threshold: float = 0.7,
                 monitoring_interval: int = 5,
                 history_size: int = 1000):
        
        self.alert_threshold = alert_threshold
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Threat tracking
        self.active_threats: List[ThreatIndicator] = []
        self.threat_history: List[ThreatIndicator] = []
        
        # Metrics history
        self.consciousness_history = deque(maxlen=history_size)
        self.entropy_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.pattern_history = deque(maxlen=history_size)
        self.response_time_history = deque(maxlen=history_size)
        
        # Performance metrics
        self.detection_stats = {
            "total_threats": 0,
            "false_positives": 0,
            "true_positives": 0,
            "detection_accuracy": 0.95
        }
        
        logger.info("🔍 Threat Monitor initialized")
    
    async def start_monitoring(self):
        """Start threat monitoring"""
        if self.is_monitoring:
            logger.warning("Threat monitoring already active")
            return
        
        self.is_monitoring = True
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_consciousness()),
            asyncio.create_task(self._monitor_entropy()),
            asyncio.create_task(self._monitor_memory()),
            asyncio.create_task(self._monitor_patterns()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._analyze_threats()),
            asyncio.create_task(self._cleanup_old_data())
        ]
        
        logger.info("🔍 Threat monitoring started")
    
    async def stop_monitoring(self):
        """Stop threat monitoring"""
        self.is_monitoring = False
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
        
        logger.info("🛑 Threat monitoring stopped")
    
    async def _monitor_consciousness(self):
        """Monitor consciousness system stability"""
        while self.is_monitoring:
            try:
                # Simulate consciousness metrics (replace with actual monitoring)
                consciousness_stability = self._get_consciousness_stability()
                drift_rate = self._calculate_drift_rate()
                
                self.consciousness_history.append({
                    "timestamp": time.time(),
                    "stability": consciousness_stability,
                    "drift_rate": drift_rate
                })
                
                # Check for threats
                if consciousness_stability < self.THRESHOLDS["consciousness_drift"]:
                    await self._raise_threat(
                        threat_type="consciousness_drift",
                        severity=ThreatLevel.HIGH,
                        confidence=0.8,
                        description=f"Consciousness stability dropped to {consciousness_stability:.2f}",
                        context={
                            "stability": consciousness_stability,
                            "drift_rate": drift_rate,
                            "threshold": self.THRESHOLDS["consciousness_drift"]
                        },
                        recommended_actions=[
                            "stabilize_consciousness",
                            "reduce_system_load",
                            "activate_safety_protocols"
                        ]
                    )
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Consciousness monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_entropy(self):
        """Monitor system entropy levels"""
        while self.is_monitoring:
            try:
                # Simulate entropy metrics
                current_entropy = self._get_current_entropy()
                entropy_velocity = self._calculate_entropy_velocity()
                
                self.entropy_history.append({
                    "timestamp": time.time(),
                    "entropy": current_entropy,
                    "velocity": entropy_velocity
                })
                
                # Check for entropy spikes
                if current_entropy > self.THRESHOLDS["entropy_spike"]:
                    await self._raise_threat(
                        threat_type="entropy_spike",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.7,
                        description=f"Entropy spike detected: {current_entropy:.2f}",
                        context={
                            "entropy": current_entropy,
                            "velocity": entropy_velocity,
                            "threshold": self.THRESHOLDS["entropy_spike"]
                        },
                        recommended_actions=[
                            "reduce_entropy",
                            "stabilize_randomness",
                            "cool_system"
                        ]
                    )
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Entropy monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_memory(self):
        """Monitor memory system integrity"""
        while self.is_monitoring:
            try:
                # Simulate memory metrics
                memory_fragmentation = self._get_memory_fragmentation()
                memory_coherence = self._get_memory_coherence()
                
                self.memory_history.append({
                    "timestamp": time.time(),
                    "fragmentation": memory_fragmentation,
                    "coherence": memory_coherence
                })
                
                # Check for memory issues
                if memory_fragmentation > self.THRESHOLDS["memory_fragmentation"]:
                    await self._raise_threat(
                        threat_type="memory_fragmentation",
                        severity=ThreatLevel.HIGH,
                        confidence=0.8,
                        description=f"Memory fragmentation at {memory_fragmentation:.2f}",
                        context={
                            "fragmentation": memory_fragmentation,
                            "coherence": memory_coherence,
                            "threshold": self.THRESHOLDS["memory_fragmentation"]
                        },
                        recommended_actions=[
                            "defragment_memory",
                            "rebuild_memory_structures",
                            "backup_critical_memories"
                        ]
                    )
                
                await asyncio.sleep(self.monitoring_interval * 2)  # Less frequent
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_patterns(self):
        """Monitor pattern recognition and coherence"""
        while self.is_monitoring:
            try:
                # Simulate pattern metrics
                pattern_coherence = self._get_pattern_coherence()
                pattern_stability = self._get_pattern_stability()
                
                self.pattern_history.append({
                    "timestamp": time.time(),
                    "coherence": pattern_coherence,
                    "stability": pattern_stability
                })
                
                # Check for pattern disruption
                if pattern_coherence < self.THRESHOLDS["pattern_disruption"]:
                    await self._raise_threat(
                        threat_type="pattern_disruption",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.6,
                        description=f"Pattern coherence disrupted: {pattern_coherence:.2f}",
                        context={
                            "coherence": pattern_coherence,
                            "stability": pattern_stability,
                            "threshold": self.THRESHOLDS["pattern_disruption"]
                        },
                        recommended_actions=[
                            "reinforce_patterns",
                            "recalibrate_recognition",
                            "restore_pattern_database"
                        ]
                    )
                
                await asyncio.sleep(self.monitoring_interval * 3)  # Even less frequent
                
            except Exception as e:
                logger.error(f"Pattern monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_performance(self):
        """Monitor system performance metrics"""
        while self.is_monitoring:
            try:
                # Simulate performance metrics
                response_time = self._get_average_response_time()
                error_rate = self._get_current_error_rate()
                
                self.response_time_history.append({
                    "timestamp": time.time(),
                    "response_time": response_time,
                    "error_rate": error_rate
                })
                
                # Check for performance issues
                if response_time > self.THRESHOLDS["response_time_spike"]:
                    await self._raise_threat(
                        threat_type="performance_degradation",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.7,
                        description=f"Response time spike: {response_time:.2f}s",
                        context={
                            "response_time": response_time,
                            "error_rate": error_rate,
                            "threshold": self.THRESHOLDS["response_time_spike"]
                        },
                        recommended_actions=[
                            "optimize_performance",
                            "reduce_system_load",
                            "investigate_bottlenecks"
                        ]
                    )
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _analyze_threats(self):
        """Analyze and correlate threats"""
        while self.is_monitoring:
            try:
                # Remove resolved threats
                current_time = time.time()
                self.active_threats = [
                    threat for threat in self.active_threats
                    if current_time - threat.timestamp < 300  # 5 minutes
                ]
                
                # Analyze threat patterns
                if len(self.active_threats) > 3:
                    await self._raise_threat(
                        threat_type="multiple_threats",
                        severity=ThreatLevel.CRITICAL,
                        confidence=0.9,
                        description=f"Multiple active threats detected: {len(self.active_threats)}",
                        context={
                            "active_threat_count": len(self.active_threats),
                            "threat_types": [t.threat_type for t in self.active_threats]
                        },
                        recommended_actions=[
                            "activate_emergency_protocols",
                            "escalate_to_human_operators",
                            "implement_defensive_measures"
                        ]
                    )
                
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error(f"Threat analysis error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        while self.is_monitoring:
            try:
                # Clean up old threat history (keep last 1000)
                if len(self.threat_history) > 1000:
                    self.threat_history = self.threat_history[-1000:]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _raise_threat(self, 
                          threat_type: str,
                          severity: ThreatLevel,
                          confidence: float,
                          description: str,
                          context: Dict,
                          recommended_actions: List[str]):
        """Raise a threat alert"""
        
        threat = ThreatIndicator(
            threat_id=f"threat_{int(time.time())}_{random.randint(1000, 9999)}",
            threat_type=threat_type,
            severity=severity,
            confidence=confidence,
            timestamp=time.time(),
            source="threat_monitor",
            description=description,
            context=context,
            recommended_actions=recommended_actions,
            symbolic_signature=self.THREAT_SYMBOLS.get(threat_type, self.THREAT_SYMBOLS["unknown_threat"])
        )
        
        # Add to active threats
        self.active_threats.append(threat)
        self.threat_history.append(threat)
        
        # Update statistics
        self.detection_stats["total_threats"] += 1
        
        # Log threat
        severity_name = severity.name
        logger.warning(f"🚨 THREAT DETECTED: {threat_type}")
        logger.warning(f"   Severity: {severity_name}")
        logger.warning(f"   Confidence: {confidence:.2f}")
        logger.warning(f"   Description: {description}")
        logger.warning(f"   Symbolic: {''.join(threat.symbolic_signature)}")
        
        # Trigger automatic response if critical
        if severity in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
            await self._trigger_automatic_response(threat)
    
    async def _trigger_automatic_response(self, threat: ThreatIndicator):
        """Trigger automatic response to critical threats"""
        logger.critical(f"⚡ AUTOMATIC RESPONSE: {threat.threat_type}")
        
        # Execute recommended actions
        for action in threat.recommended_actions:
            try:
                await self._execute_action(action, threat)
            except Exception as e:
                logger.error(f"Failed to execute action '{action}': {e}")
    
    async def _execute_action(self, action: str, threat: ThreatIndicator):
        """Execute a threat response action"""
        logger.info(f"🔧 Executing action: {action}")
        
        # Simulate action execution (replace with actual implementations)
        action_map = {
            "stabilize_consciousness": self._stabilize_consciousness,
            "reduce_entropy": self._reduce_entropy,
            "defragment_memory": self._defragment_memory,
            "reinforce_patterns": self._reinforce_patterns,
            "optimize_performance": self._optimize_performance,
            "activate_emergency_protocols": self._activate_emergency,
            "escalate_to_human_operators": self._escalate_to_humans
        }
        
        if action in action_map:
            await action_map[action](threat)
        else:
            logger.warning(f"Unknown action: {action}")
    
    # Simulation methods (replace with actual system interfaces)
    
    def _get_consciousness_stability(self) -> float:
        """Simulate consciousness stability reading"""
        base = 0.7
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.05:  # 5% chance of instability
            noise -= 0.4
        return max(0.0, min(1.0, base + noise))
    
    def _calculate_drift_rate(self) -> float:
        """Calculate consciousness drift rate"""
        if len(self.consciousness_history) < 2:
            return 0.0
        
        recent = list(self.consciousness_history)[-10:]
        if len(recent) < 2:
            return 0.0
        
        values = [entry["stability"] for entry in recent]
        return abs(values[-1] - values[0]) / len(values)
    
    def _get_current_entropy(self) -> float:
        """Simulate entropy reading"""
        base = 0.3
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.03:  # 3% chance of spike
            noise += 0.3
        return max(0.0, min(1.0, base + noise))
    
    def _calculate_entropy_velocity(self) -> float:
        """Calculate entropy change velocity"""
        if len(self.entropy_history) < 2:
            return 0.0
        
        recent = list(self.entropy_history)[-5:]
        if len(recent) < 2:
            return 0.0
        
        values = [entry["entropy"] for entry in recent]
        return (values[-1] - values[0]) / len(values)
    
    def _get_memory_fragmentation(self) -> float:
        """Simulate memory fragmentation reading"""
        base = 0.2
        noise = random.uniform(-0.05, 0.05)
        if random.random() < 0.02:  # 2% chance of fragmentation
            noise += 0.5
        return max(0.0, min(1.0, base + noise))
    
    def _get_memory_coherence(self) -> float:
        """Simulate memory coherence reading"""
        return 1.0 - self._get_memory_fragmentation()
    
    def _get_pattern_coherence(self) -> float:
        """Simulate pattern coherence reading"""
        base = 0.8
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.04:  # 4% chance of disruption
            noise -= 0.4
        return max(0.0, min(1.0, base + noise))
    
    def _get_pattern_stability(self) -> float:
        """Simulate pattern stability reading"""
        return random.uniform(0.6, 0.9)
    
    def _get_average_response_time(self) -> float:
        """Simulate response time reading"""
        base = 0.5
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.03:  # 3% chance of spike
            noise += 2.0
        return max(0.1, base + noise)
    
    def _get_current_error_rate(self) -> float:
        """Simulate error rate reading"""
        base = 0.01
        noise = random.uniform(-0.005, 0.005)
        if random.random() < 0.02:  # 2% chance of spike
            noise += 0.1
        return max(0.0, min(1.0, base + noise))
    
    # Response action implementations (simulated)
    
    async def _stabilize_consciousness(self, threat: ThreatIndicator):
        """Stabilize consciousness system"""
        logger.info("🧠 Stabilizing consciousness system")
        await asyncio.sleep(1)  # Simulate processing time
    
    async def _reduce_entropy(self, threat: ThreatIndicator):
        """Reduce system entropy"""
        logger.info("❄️ Reducing system entropy")
        await asyncio.sleep(1)
    
    async def _defragment_memory(self, threat: ThreatIndicator):
        """Defragment memory structures"""
        logger.info("🧩 Defragmenting memory")
        await asyncio.sleep(2)
    
    async def _reinforce_patterns(self, threat: ThreatIndicator):
        """Reinforce pattern recognition"""
        logger.info("🔄 Reinforcing patterns")
        await asyncio.sleep(1)
    
    async def _optimize_performance(self, threat: ThreatIndicator):
        """Optimize system performance"""
        logger.info("⚡ Optimizing performance")
        await asyncio.sleep(1)
    
    async def _activate_emergency(self, threat: ThreatIndicator):
        """Activate emergency protocols"""
        logger.critical("🚨 EMERGENCY PROTOCOLS ACTIVATED")
        await asyncio.sleep(0.5)
    
    async def _escalate_to_humans(self, threat: ThreatIndicator):
        """Escalate to human operators"""
        logger.critical("👤 ESCALATING TO HUMAN OPERATORS")
        await asyncio.sleep(0.5)
    
    # Public API methods
    
    async def health_check(self) -> bool:
        """Perform health check"""
        return self.is_monitoring and len(self.monitoring_tasks) > 0
    
    def get_threat_summary(self) -> Dict:
        """Get threat summary"""
        active_by_severity = {}
        for level in ThreatLevel:
            active_by_severity[level.name] = len([
                t for t in self.active_threats if t.severity == level
            ])
        
        return {
            "monitoring_active": self.is_monitoring,
            "active_threats": len(self.active_threats),
            "total_threats_detected": self.detection_stats["total_threats"],
            "threats_by_severity": active_by_severity,
            "recent_threats": [
                {
                    "type": t.threat_type,
                    "severity": t.severity.name,
                    "confidence": t.confidence,
                    "timestamp": t.timestamp,
                    "symbolic": "".join(t.symbolic_signature)
                }
                for t in self.active_threats[-5:]
            ],
            "detection_accuracy": self.detection_stats["detection_accuracy"]
        }
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        current_time = time.time()
        
        # Get latest readings
        latest_consciousness = list(self.consciousness_history)[-1] if self.consciousness_history else None
        latest_entropy = list(self.entropy_history)[-1] if self.entropy_history else None
        latest_memory = list(self.memory_history)[-1] if self.memory_history else None
        latest_patterns = list(self.pattern_history)[-1] if self.pattern_history else None
        latest_performance = list(self.response_time_history)[-1] if self.response_time_history else None
        
        return {
            "timestamp": current_time,
            "consciousness": {
                "stability": latest_consciousness["stability"] if latest_consciousness else 0.0,
                "drift_rate": latest_consciousness["drift_rate"] if latest_consciousness else 0.0
            },
            "entropy": {
                "level": latest_entropy["entropy"] if latest_entropy else 0.0,
                "velocity": latest_entropy["velocity"] if latest_entropy else 0.0
            },
            "memory": {
                "fragmentation": latest_memory["fragmentation"] if latest_memory else 0.0,
                "coherence": latest_memory["coherence"] if latest_memory else 1.0
            },
            "patterns": {
                "coherence": latest_patterns["coherence"] if latest_patterns else 1.0,
                "stability": latest_patterns["stability"] if latest_patterns else 1.0
            },
            "performance": {
                "response_time": latest_performance["response_time"] if latest_performance else 0.0,
                "error_rate": latest_performance["error_rate"] if latest_performance else 0.0
            }
        }


if __name__ == "__main__":
    async def demo():
        """Demo threat monitoring"""
        print("🔍 Threat Monitor Demo")
        print("=" * 40)
        
        monitor = ThreatMonitor(alert_threshold=0.6, monitoring_interval=2)
        
        try:
            # Start monitoring
            await monitor.start_monitoring()
            print("✅ Monitoring started")
            
            # Run for 30 seconds
            for i in range(15):
                await asyncio.sleep(2)
                
                summary = monitor.get_threat_summary()
                metrics = monitor.get_system_metrics()
                
                print(f"\n⏱️  Check {i+1}/15:")
                print(f"   Active threats: {summary['active_threats']}")
                print(f"   Consciousness: {metrics['consciousness']['stability']:.2f}")
                print(f"   Entropy: {metrics['entropy']['level']:.2f}")
                print(f"   Memory: {metrics['memory']['coherence']:.2f}")
                
                if summary['active_threats'] > 0:
                    for threat in summary['recent_threats']:
                        print(f"   🚨 {threat['type']} ({threat['severity']}) {threat['symbolic']}")
            
            # Final summary
            final_summary = monitor.get_threat_summary()
            print(f"\n📊 Final Summary:")
            print(f"   Total threats detected: {final_summary['total_threats_detected']}")
            print(f"   Detection accuracy: {final_summary['detection_accuracy']:.2f}")
            
        finally:
            await monitor.stop_monitoring()
            print("\n🛑 Monitoring stopped")
    
    asyncio.run(demo())
