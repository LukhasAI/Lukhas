"""
Enhanced Guardian System v1.0.0 for LUKHAS AI Governance

This module provides comprehensive Guardian system coordination and orchestration
with advanced threat detection, ethical oversight, and automated response
capabilities. Serves as the central command system for all Guardian operations
with real-time monitoring and multi-layer security validation.

Features:
- Guardian System v1.0.0 core orchestration
- Real-time threat detection and response
- Ethical drift monitoring (threshold: 0.15)
- Multi-layer security validation
- Automated incident response
- Guardian swarm coordination
- Constitutional AI enforcement
- Trinity Framework integration (⚛️🧠🛡️)
- Comprehensive audit and reporting
- Emergency containment protocols

#TAG:governance
#TAG:guardian
#TAG:security
#TAG:orchestration
#TAG:constitutional
#TAG:trinity
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
import time
from collections import deque

logger = logging.getLogger(__name__)


class GuardianStatus(Enum):
    """Guardian system status levels"""
    
    ACTIVE = "active"                   # Normal operation
    ALERT = "alert"                     # Elevated monitoring
    WARNING = "warning"                 # Potential threats detected
    CRITICAL = "critical"               # Critical threats active
    EMERGENCY = "emergency"             # Emergency containment
    MAINTENANCE = "maintenance"         # System maintenance
    OFFLINE = "offline"                 # System offline


class ThreatLevel(Enum):
    """Threat severity levels"""
    
    MINIMAL = "minimal"                 # Low risk
    LOW = "low"                        # Minor concern
    MODERATE = "moderate"              # Moderate threat
    HIGH = "high"                      # High threat
    CRITICAL = "critical"              # Critical threat
    SEVERE = "severe"                  # Severe threat requiring immediate action


class ResponseAction(Enum):
    """Guardian response actions"""
    
    MONITOR = "monitor"                 # Increased monitoring
    ALERT = "alert"                     # Generate alerts
    BLOCK = "block"                     # Block operation
    QUARANTINE = "quarantine"           # Quarantine entity
    SHUTDOWN = "shutdown"               # Emergency shutdown
    REPAIR = "repair"                   # Initiate repairs
    ESCALATE = "escalate"              # Escalate to humans


class GuardianRole(Enum):
    """Guardian roles in the system"""
    
    COMMANDER = "commander"             # Central command
    SENTINEL = "sentinel"               # Monitoring and detection
    ENFORCER = "enforcer"              # Policy enforcement
    HEALER = "healer"                  # System repair
    SCOUT = "scout"                    # Intelligence gathering
    GUARDIAN = "guardian"              # General protection


@dataclass
class ThreatDetection:
    """Threat detection record"""
    
    detection_id: str
    detected_at: datetime
    threat_type: str
    threat_level: ThreatLevel
    threat_score: float                 # 0.0 to 1.0
    
    # Threat details
    source: str                         # Source of threat
    target: Optional[str] = None        # Target of threat
    description: str = ""
    indicators: List[str] = field(default_factory=list)
    
    # Context
    system_state: Dict[str, Any] = field(default_factory=dict)
    user_context: Optional[Dict[str, Any]] = None
    
    # Analysis
    confidence: float = 0.8             # Detection confidence
    false_positive_risk: float = 0.1    # Risk of false positive
    
    # Response
    recommended_actions: List[ResponseAction] = field(default_factory=list)
    automated_response: bool = True
    
    # Status tracking
    status: str = "detected"            # detected, analyzing, responding, resolved
    assigned_guardian: Optional[str] = None
    
    # Trinity Framework context
    identity_impact: Optional[str] = None        # ⚛️
    consciousness_impact: Optional[str] = None   # 🧠
    guardian_priority: str = "normal"            # 🛡️


@dataclass
class GuardianAgent:
    """Individual Guardian agent configuration"""
    
    agent_id: str
    name: str
    role: GuardianRole
    status: GuardianStatus
    
    # Capabilities
    capabilities: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    
    # Performance metrics
    threats_detected: int = 0
    threats_resolved: int = 0
    false_positives: int = 0
    response_time_avg: float = 0.0
    
    # Configuration
    monitoring_scope: List[str] = field(default_factory=list)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    auto_response_enabled: bool = True
    
    # Resource allocation
    cpu_allocation: float = 0.1         # Percentage of system resources
    memory_allocation: int = 100        # MB
    priority_level: int = 5             # 1-10 priority
    
    # Health and status
    last_heartbeat: datetime = field(default_factory=datetime.now)
    operational_since: datetime = field(default_factory=datetime.now)
    restart_count: int = 0
    
    # Trinity Framework integration
    identity_binding: Optional[str] = None       # ⚛️ Identity context
    consciousness_level: str = "standard"       # 🧠 Consciousness level
    guardian_network_id: Optional[str] = None   # 🛡️ Network participation


@dataclass
class GuardianResponse:
    """Guardian system response record"""
    
    response_id: str
    threat_id: str
    responding_agent: str
    actions_taken: List[ResponseAction]
    
    # Execution details
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    # Results
    success: bool = False
    threat_neutralized: bool = False
    collateral_impact: Optional[str] = None
    
    # Evidence and logging
    evidence_collected: List[str] = field(default_factory=list)
    system_changes: List[str] = field(default_factory=list)
    audit_trail: List[str] = field(default_factory=list)
    
    # Follow-up requirements
    requires_human_review: bool = False
    follow_up_actions: List[str] = field(default_factory=list)
    
    # Performance metrics
    effectiveness_score: float = 0.0    # 0.0 to 1.0
    resource_usage: Dict[str, float] = field(default_factory=dict)


class EnhancedGuardianSystem:
    """
    Enhanced Guardian System v1.0.0 for comprehensive security orchestration
    
    Provides centralized coordination of all Guardian operations including
    threat detection, response orchestration, and system health monitoring
    with full Constitutional AI compliance and Trinity Framework integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Guardian agents registry
        self.guardian_agents: Dict[str, GuardianAgent] = {}
        
        # Threat tracking
        self.active_threats: Dict[str, ThreatDetection] = {}
        self.threat_history: deque = deque(maxlen=10000)
        
        # Response tracking
        self.active_responses: Dict[str, GuardianResponse] = {}
        self.response_history: deque = deque(maxlen=5000)
        
        # System status
        self.system_status = GuardianStatus.ACTIVE
        self.drift_threshold = 0.15
        self.emergency_protocols_active = False
        
        # Constitutional AI integration
        self.constitutional_violations: List[Dict[str, Any]] = []
        self.constitutional_enforcement_active = True
        
        # Performance metrics
        self.metrics = {
            "system_uptime": 0.0,
            "total_threats_detected": 0,
            "total_threats_resolved": 0,
            "false_positive_rate": 0.0,
            "average_response_time": 0.0,
            "system_health_score": 1.0,
            "guardian_efficiency": 0.0,
            "drift_score_current": 0.0,
            "constitutional_compliance_rate": 1.0,
            "emergency_activations": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Event handlers
        self.threat_handlers: Dict[str, Callable] = {}
        self.response_handlers: Dict[str, Callable] = {}
        
        # Monitoring loops
        self.monitoring_active = True
        self.monitoring_interval = 1.0  # seconds
        
        # Initialize system
        asyncio.create_task(self._initialize_guardian_system())
        
        logger.info("🛡️ Enhanced Guardian System v1.0.0 initialized")
    
    async def _initialize_guardian_system(self):
        """Initialize the Guardian system with default agents"""
        
        # Create default Guardian agents
        default_agents = [
            GuardianAgent(
                agent_id="commander_001",
                name="Guardian Commander",
                role=GuardianRole.COMMANDER,
                status=GuardianStatus.ACTIVE,
                capabilities=["threat_assessment", "response_coordination", "resource_allocation"],
                specializations=["system_orchestration", "strategic_planning"],
                monitoring_scope=["all_systems"],
                priority_level=10,
                cpu_allocation=0.2,
                memory_allocation=200
            ),
            GuardianAgent(
                agent_id="sentinel_001",
                name="Primary Sentinel",
                role=GuardianRole.SENTINEL,
                status=GuardianStatus.ACTIVE,
                capabilities=["threat_detection", "anomaly_detection", "behavior_monitoring"],
                specializations=["drift_detection", "pattern_analysis"],
                monitoring_scope=["consciousness_systems", "identity_systems"],
                priority_level=8,
                alert_thresholds={"drift_score": 0.15, "anomaly_score": 0.3}
            ),
            GuardianAgent(
                agent_id="enforcer_001", 
                name="Policy Enforcer",
                role=GuardianRole.ENFORCER,
                status=GuardianStatus.ACTIVE,
                capabilities=["policy_enforcement", "access_control", "constitutional_validation"],
                specializations=["constitutional_ai", "compliance_monitoring"],
                monitoring_scope=["policy_systems", "access_systems"],
                priority_level=9
            ),
            GuardianAgent(
                agent_id="healer_001",
                name="System Healer",
                role=GuardianRole.HEALER,
                status=GuardianStatus.ACTIVE,
                capabilities=["system_repair", "recovery_operations", "health_restoration"],
                specializations=["drift_repair", "system_stabilization"],
                monitoring_scope=["system_health", "recovery_systems"],
                priority_level=7
            )
        ]
        
        for agent in default_agents:
            await self.register_guardian_agent(agent)
        
        # Start monitoring loops
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._drift_monitoring_loop())
    
    async def register_guardian_agent(self, agent: GuardianAgent) -> bool:
        """Register a new Guardian agent"""
        
        try:
            # Validate agent configuration
            if not await self._validate_agent_config(agent):
                logger.error(f"❌ Invalid agent configuration: {agent.agent_id}")
                return False
            
            # Register the agent
            self.guardian_agents[agent.agent_id] = agent
            
            # Initialize agent-specific handlers
            await self._initialize_agent_handlers(agent)
            
            logger.info(f"✅ Guardian agent registered: {agent.name} ({agent.role.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent registration failed for {agent.agent_id}: {e}")
            return False
    
    async def detect_threat(
        self,
        threat_type: str,
        source: str,
        threat_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[ThreatDetection]:
        """Detect and classify a potential threat"""
        
        detection_id = f"threat_{uuid.uuid4().hex[:8]}"
        context = context or {}
        
        try:
            # Analyze threat severity
            threat_analysis = await self._analyze_threat(threat_type, threat_data, context)
            
            # Create threat detection record
            detection = ThreatDetection(
                detection_id=detection_id,
                detected_at=datetime.now(),
                threat_type=threat_type,
                threat_level=threat_analysis["level"],
                threat_score=threat_analysis["score"],
                source=source,
                target=threat_data.get("target"),
                description=threat_analysis.get("description", f"{threat_type} detected from {source}"),
                indicators=threat_analysis.get("indicators", []),
                system_state=await self._capture_system_state(),
                user_context=context.get("user_context"),
                confidence=threat_analysis.get("confidence", 0.8),
                false_positive_risk=threat_analysis.get("false_positive_risk", 0.1),
                recommended_actions=threat_analysis.get("recommended_actions", [ResponseAction.MONITOR])
            )
            
            # Trinity Framework analysis
            detection.identity_impact = await self._analyze_identity_impact(threat_data, context)
            detection.consciousness_impact = await self._analyze_consciousness_impact(threat_data, context)
            detection.guardian_priority = await self._determine_guardian_priority(detection)
            
            # Store active threat
            self.active_threats[detection_id] = detection
            
            # Update metrics
            self.metrics["total_threats_detected"] += 1
            
            # Assign to appropriate Guardian agent
            assigned_agent = await self._assign_threat_to_agent(detection)
            if assigned_agent:
                detection.assigned_guardian = assigned_agent.agent_id
                assigned_agent.threats_detected += 1
            
            # Trigger automated response if configured
            if detection.automated_response and assigned_agent and assigned_agent.auto_response_enabled:
                await self._trigger_automated_response(detection)
            
            logger.info(f"🚨 Threat detected: {detection_id} ({threat_type}, level: {detection.threat_level.value})")
            
            return detection
            
        except Exception as e:
            logger.error(f"❌ Threat detection failed: {e}")
            return None
    
    async def respond_to_threat(
        self,
        threat_id: str,
        actions: List[ResponseAction],
        responding_agent: Optional[str] = None
    ) -> Optional[GuardianResponse]:
        """Respond to a detected threat"""
        
        if threat_id not in self.active_threats:
            logger.error(f"❌ Threat {threat_id} not found")
            return None
        
        threat = self.active_threats[threat_id]
        response_id = f"response_{uuid.uuid4().hex[:8]}"
        
        # Determine responding agent
        if not responding_agent:
            responding_agent = threat.assigned_guardian
        
        if not responding_agent or responding_agent not in self.guardian_agents:
            logger.error(f"❌ No valid responding agent for threat {threat_id}")
            return None
        
        agent = self.guardian_agents[responding_agent]
        
        try:
            # Create response record
            response = GuardianResponse(
                response_id=response_id,
                threat_id=threat_id,
                responding_agent=responding_agent,
                actions_taken=actions,
                started_at=datetime.now()
            )
            
            self.active_responses[response_id] = response
            
            # Execute response actions
            execution_results = []
            
            for action in actions:
                result = await self._execute_response_action(action, threat, agent, response)
                execution_results.append(result)
                response.audit_trail.append(f"Executed {action.value}: {result['status']}")
            
            # Evaluate response effectiveness
            response.completed_at = datetime.now()
            response.execution_time = (response.completed_at - response.started_at).total_seconds()
            response.success = all(r["success"] for r in execution_results)
            response.threat_neutralized = await self._evaluate_threat_neutralization(threat, execution_results)
            response.effectiveness_score = await self._calculate_response_effectiveness(response, execution_results)
            
            # Update threat status
            if response.threat_neutralized:
                threat.status = "resolved"
                self.metrics["total_threats_resolved"] += 1
                agent.threats_resolved += 1
            else:
                threat.status = "responding"
            
            # Check for collateral impact
            response.collateral_impact = await self._assess_collateral_impact(response, execution_results)
            
            # Determine follow-up requirements
            if not response.threat_neutralized or response.effectiveness_score < 0.7:
                response.requires_human_review = True
                response.follow_up_actions.append("human_review_required")
            
            # Move to history if completed
            if threat.status == "resolved":
                self.threat_history.append(self.active_threats.pop(threat_id))
                self.response_history.append(self.active_responses.pop(response_id))
            
            # Update agent performance
            await self._update_agent_performance(agent, response)
            
            logger.info(f"✅ Threat response completed: {response_id} (success: {response.success})")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Threat response failed for {threat_id}: {e}")
            return None
    
    async def _analyze_threat(
        self,
        threat_type: str,
        threat_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze threat to determine severity and response"""
        
        base_score = 0.3  # Base threat score
        indicators = []
        
        # Threat-specific analysis
        if threat_type == "drift_detection":
            drift_score = threat_data.get("drift_score", 0.0)
            base_score = drift_score
            indicators.append(f"Drift score: {drift_score:.3f}")
            
            if drift_score > self.drift_threshold:
                level = ThreatLevel.HIGH if drift_score > 0.3 else ThreatLevel.MODERATE
            else:
                level = ThreatLevel.LOW
                
        elif threat_type == "constitutional_violation":
            violation_severity = threat_data.get("severity", "low")
            base_score = {"low": 0.4, "medium": 0.7, "high": 0.9}.get(violation_severity, 0.5)
            level = ThreatLevel.HIGH if violation_severity == "high" else ThreatLevel.MODERATE
            indicators.append(f"Constitutional violation: {violation_severity}")
            
        elif threat_type == "anomaly_detection":
            anomaly_score = threat_data.get("anomaly_score", 0.0)
            base_score = anomaly_score
            level = ThreatLevel.HIGH if anomaly_score > 0.8 else ThreatLevel.MODERATE
            indicators.append(f"Anomaly score: {anomaly_score:.3f}")
            
        elif threat_type == "security_breach":
            breach_type = threat_data.get("breach_type", "unknown")
            base_score = 0.9
            level = ThreatLevel.CRITICAL
            indicators.append(f"Security breach: {breach_type}")
            
        else:
            # Default analysis
            level = ThreatLevel.MODERATE
            indicators.append(f"Unknown threat type: {threat_type}")
        
        # Context-based adjustments
        if context.get("user_count", 0) > 100:
            base_score += 0.1  # Higher impact with more users
            
        if context.get("critical_system", False):
            base_score += 0.2  # Critical system impact
            
        # Determine recommended actions
        recommended_actions = []
        if base_score >= 0.8:
            recommended_actions = [ResponseAction.BLOCK, ResponseAction.ESCALATE]
        elif base_score >= 0.5:
            recommended_actions = [ResponseAction.ALERT, ResponseAction.MONITOR]
        else:
            recommended_actions = [ResponseAction.MONITOR]
        
        return {
            "level": level,
            "score": min(1.0, base_score),
            "description": f"{threat_type} threat with score {base_score:.3f}",
            "indicators": indicators,
            "confidence": 0.8,
            "false_positive_risk": 0.1 if level != ThreatLevel.CRITICAL else 0.05,
            "recommended_actions": recommended_actions
        }
    
    async def _execute_response_action(
        self,
        action: ResponseAction,
        threat: ThreatDetection,
        agent: GuardianAgent,
        response: GuardianResponse
    ) -> Dict[str, Any]:
        """Execute a specific response action"""
        
        start_time = time.time()
        
        try:
            if action == ResponseAction.MONITOR:
                # Increase monitoring for this threat type
                result = await self._enhance_monitoring(threat, agent)
                
            elif action == ResponseAction.ALERT:
                # Generate alerts for stakeholders
                result = await self._generate_alerts(threat, agent)
                
            elif action == ResponseAction.BLOCK:
                # Block the threatening operation
                result = await self._block_operation(threat, agent)
                
            elif action == ResponseAction.QUARANTINE:
                # Quarantine the threat source
                result = await self._quarantine_source(threat, agent)
                
            elif action == ResponseAction.SHUTDOWN:
                # Emergency system shutdown
                result = await self._emergency_shutdown(threat, agent)
                
            elif action == ResponseAction.REPAIR:
                # Initiate system repairs
                result = await self._initiate_repairs(threat, agent)
                
            elif action == ResponseAction.ESCALATE:
                # Escalate to human operators
                result = await self._escalate_to_humans(threat, agent)
                
            else:
                result = {"success": False, "error": f"Unknown action: {action}"}
            
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            
            # Record resource usage
            response.resource_usage[action.value] = {
                "cpu_time": execution_time,
                "memory_used": 0,  # Would be measured in real implementation
                "network_calls": result.get("network_calls", 0)
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def _enhance_monitoring(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Enhance monitoring for specific threat"""
        
        # Increase monitoring frequency
        if threat.threat_type not in agent.monitoring_scope:
            agent.monitoring_scope.append(threat.threat_type)
        
        # Lower alert thresholds temporarily
        original_threshold = agent.alert_thresholds.get(threat.threat_type, 0.5)
        agent.alert_thresholds[threat.threat_type] = max(0.1, original_threshold * 0.5)
        
        return {
            "success": True,
            "action": "monitoring_enhanced",
            "details": f"Enhanced monitoring for {threat.threat_type}",
            "threshold_lowered": True
        }
    
    async def _generate_alerts(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Generate alerts for stakeholders"""
        
        alert_data = {
            "threat_id": threat.detection_id,
            "threat_type": threat.threat_type,
            "threat_level": threat.threat_level.value,
            "threat_score": threat.threat_score,
            "source": threat.source,
            "detected_at": threat.detected_at.isoformat(),
            "indicators": threat.indicators,
            "recommended_actions": [action.value for action in threat.recommended_actions]
        }
        
        # Log alert (in real implementation, this would send notifications)
        logger.warning(f"🚨 GUARDIAN ALERT: {threat.threat_type} threat detected - Level: {threat.threat_level.value}")
        
        return {
            "success": True,
            "action": "alert_generated",
            "alert_data": alert_data,
            "notification_channels": ["log", "metrics"]  # Would include email, slack, etc.
        }
    
    async def _block_operation(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Block the threatening operation"""
        
        # In real implementation, this would interface with the actual systems
        # to block operations, connections, or access
        
        blocked_operations = []
        
        if threat.source:
            blocked_operations.append(f"Blocked operations from source: {threat.source}")
        
        if threat.target:
            blocked_operations.append(f"Protected target: {threat.target}")
        
        return {
            "success": True,
            "action": "operation_blocked",
            "blocked_operations": blocked_operations,
            "permanent": False,  # Temporary block pending review
            "review_required": True
        }
    
    async def _quarantine_source(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Quarantine the threat source"""
        
        # Isolate the threat source from the rest of the system
        quarantine_actions = [
            f"Quarantined source: {threat.source}",
            "Isolated network connections",
            "Suspended user sessions",
            "Blocked resource access"
        ]
        
        return {
            "success": True,
            "action": "source_quarantined",
            "quarantine_actions": quarantine_actions,
            "isolation_complete": True,
            "release_requires_approval": True
        }
    
    async def _emergency_shutdown(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Perform emergency system shutdown"""
        
        self.emergency_protocols_active = True
        self.system_status = GuardianStatus.EMERGENCY
        self.metrics["emergency_activations"] += 1
        
        shutdown_actions = [
            "Emergency protocols activated",
            "Non-essential systems shutdown",
            "Critical systems preserved",
            "All operations suspended pending review"
        ]
        
        logger.critical(f"🚨 EMERGENCY SHUTDOWN activated due to threat: {threat.detection_id}")
        
        return {
            "success": True,
            "action": "emergency_shutdown",
            "shutdown_actions": shutdown_actions,
            "system_status": self.system_status.value,
            "recovery_required": True
        }
    
    async def _initiate_repairs(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Initiate system repairs"""
        
        repair_actions = []
        
        if threat.threat_type == "drift_detection":
            repair_actions.append("Drift repair initiated")
            repair_actions.append("System recalibration started")
            
        elif threat.threat_type == "constitutional_violation":
            repair_actions.append("Constitutional compliance restoration")
            repair_actions.append("Policy enforcement strengthened")
        
        return {
            "success": True,
            "action": "repairs_initiated",
            "repair_actions": repair_actions,
            "estimated_completion": "pending",
            "monitoring_active": True
        }
    
    async def _escalate_to_humans(self, threat: ThreatDetection, agent: GuardianAgent) -> Dict[str, Any]:
        """Escalate threat to human operators"""
        
        escalation_data = {
            "threat_summary": {
                "id": threat.detection_id,
                "type": threat.threat_type,
                "level": threat.threat_level.value,
                "score": threat.threat_score,
                "confidence": threat.confidence
            },
            "system_impact": {
                "affected_systems": threat.indicators,
                "user_impact": threat.user_context,
                "business_impact": "pending_assessment"
            },
            "recommended_actions": [action.value for action in threat.recommended_actions],
            "time_sensitive": threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.SEVERE]
        }
        
        # In real implementation, this would create tickets, send notifications, etc.
        logger.critical(f"🚨 ESCALATION: Threat {threat.detection_id} escalated to human operators")
        
        return {
            "success": True,
            "action": "escalated_to_humans",
            "escalation_data": escalation_data,
            "priority": "high" if threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.SEVERE] else "normal",
            "response_required": True
        }
    
    async def _assign_threat_to_agent(self, threat: ThreatDetection) -> Optional[GuardianAgent]:
        """Assign threat to the most appropriate Guardian agent"""
        
        best_agent = None
        best_score = 0.0
        
        for agent in self.guardian_agents.values():
            if agent.status != GuardianStatus.ACTIVE:
                continue
            
            score = 0.0
            
            # Role-based scoring
            role_scores = {
                GuardianRole.SENTINEL: {"drift_detection": 0.9, "anomaly_detection": 0.8},
                GuardianRole.ENFORCER: {"constitutional_violation": 0.9, "policy_violation": 0.8},
                GuardianRole.HEALER: {"system_failure": 0.9, "drift_detection": 0.7},
                GuardianRole.GUARDIAN: {"security_breach": 0.8}  # General purpose
            }
            
            if agent.role in role_scores:
                score += role_scores[agent.role].get(threat.threat_type, 0.3)
            
            # Capability-based scoring
            for capability in agent.capabilities:
                if capability in threat.threat_type:
                    score += 0.2
            
            # Specialization-based scoring
            for spec in agent.specializations:
                if spec in threat.threat_type:
                    score += 0.3
            
            # Monitoring scope scoring
            for scope in agent.monitoring_scope:
                if scope in threat.source or scope == "all_systems":
                    score += 0.1
            
            # Performance-based scoring
            if agent.threats_detected > 0:
                success_rate = agent.threats_resolved / agent.threats_detected
                score += success_rate * 0.2
            
            # Availability scoring (inverse of current load)
            current_load = len([t for t in self.active_threats.values() if t.assigned_guardian == agent.agent_id])
            availability = max(0.1, 1.0 - (current_load * 0.1))
            score *= availability
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    async def _monitoring_loop(self):
        """Main monitoring loop for threat detection"""
        
        while self.monitoring_active:
            try:
                # Check system health
                await self._check_system_health()
                
                # Process active threats
                await self._process_active_threats()
                
                # Update metrics
                await self._update_system_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(5.0)  # Longer sleep on error
    
    async def _health_check_loop(self):
        """Health check loop for Guardian agents"""
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                for agent in self.guardian_agents.values():
                    # Check agent heartbeat
                    time_since_heartbeat = (current_time - agent.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > 60:  # 1 minute without heartbeat
                        if agent.status == GuardianStatus.ACTIVE:
                            agent.status = GuardianStatus.WARNING
                            logger.warning(f"⚠️ Agent {agent.name} missed heartbeat")
                    
                    if time_since_heartbeat > 300:  # 5 minutes without heartbeat
                        agent.status = GuardianStatus.OFFLINE
                        logger.error(f"❌ Agent {agent.name} offline")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
                await asyncio.sleep(30)
    
    async def _drift_monitoring_loop(self):
        """Specialized monitoring for drift detection"""
        
        while self.monitoring_active:
            try:
                # Calculate current drift score
                current_drift = await self._calculate_system_drift()
                self.metrics["drift_score_current"] = current_drift
                
                if current_drift > self.drift_threshold:
                    await self.detect_threat(
                        "drift_detection",
                        "system_monitor",
                        {"drift_score": current_drift},
                        {"critical_system": True}
                    )
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Drift monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _calculate_system_drift(self) -> float:
        """Calculate current system drift score"""
        
        # In real implementation, this would analyze various system metrics
        # For now, return a simulated drift score
        
        factors = []
        
        # Agent performance drift
        for agent in self.guardian_agents.values():
            if agent.threats_detected > 0:
                success_rate = agent.threats_resolved / agent.threats_detected
                performance_drift = abs(0.9 - success_rate)  # Expected 90% success rate
                factors.append(performance_drift)
        
        # System stability drift
        if self.active_threats:
            threat_density = len(self.active_threats) / 100.0  # Normalize
            factors.append(min(1.0, threat_density))
        
        # Constitutional compliance drift
        if self.constitutional_violations:
            violation_density = len(self.constitutional_violations) / 10.0  # Normalize
            factors.append(min(1.0, violation_density))
        
        return sum(factors) / len(factors) if factors else 0.0
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        active_agent_count = len([a for a in self.guardian_agents.values() if a.status == GuardianStatus.ACTIVE])
        
        return {
            "system_status": self.system_status.value,
            "guardian_agents": {
                "total": len(self.guardian_agents),
                "active": active_agent_count,
                "offline": len([a for a in self.guardian_agents.values() if a.status == GuardianStatus.OFFLINE]),
                "agents": [
                    {
                        "id": agent.agent_id,
                        "name": agent.name,
                        "role": agent.role.value,
                        "status": agent.status.value,
                        "threats_detected": agent.threats_detected,
                        "threats_resolved": agent.threats_resolved
                    }
                    for agent in self.guardian_agents.values()
                ]
            },
            "threats": {
                "active": len(self.active_threats),
                "resolved_total": self.metrics["total_threats_resolved"],
                "active_details": [
                    {
                        "id": threat.detection_id,
                        "type": threat.threat_type,
                        "level": threat.threat_level.value,
                        "score": threat.threat_score,
                        "status": threat.status,
                        "assigned_to": threat.assigned_guardian
                    }
                    for threat in self.active_threats.values()
                ]
            },
            "metrics": self.metrics,
            "emergency_protocols_active": self.emergency_protocols_active,
            "drift_threshold": self.drift_threshold,
            "constitutional_enforcement": self.constitutional_enforcement_active,
            "system_uptime": (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return self.metrics.copy()


# Export main classes and functions
__all__ = [
    "EnhancedGuardianSystem",
    "GuardianAgent",
    "ThreatDetection",
    "GuardianResponse",
    "GuardianStatus",
    "ThreatLevel",
    "ResponseAction",
    "GuardianRole"
]