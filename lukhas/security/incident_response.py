#!/usr/bin/env python3
"""
LUKHAS Security - Incident Response Automation
=============================================

Comprehensive incident response automation system with T4/0.01% excellence.
Provides automated incident detection, classification, containment, and recovery.

Key Features:
- Automated incident detection and classification
- Predefined response playbooks
- Containment and isolation workflows
- Evidence collection and preservation
- Integration with Guardian system
- Real-time escalation and notification
- Compliance-ready audit trails
- Performance optimized for <5ms response time

Constellation Framework: 🛡️ Guardian Excellence - Incident Response
"""

import os
import time
import logging
import hashlib
import threading
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from collections import deque
import uuid

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Incident severity levels."""
    P0_CRITICAL = "p0_critical"      # System down, data breach
    P1_HIGH = "p1_high"              # Significant security event
    P2_MEDIUM = "p2_medium"          # Security concern, service degraded
    P3_LOW = "p3_low"                # Minor security issue
    P4_INFO = "p4_info"              # Informational, no immediate action

class IncidentStatus(Enum):
    """Incident lifecycle status."""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONTAINED = "contained"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentCategory(Enum):
    """Incident categories for classification."""
    DATA_BREACH = "data_breach"
    SYSTEM_COMPROMISE = "system_compromise"
    MALWARE_INFECTION = "malware_infection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    POLICY_VIOLATION = "policy_violation"
    GUARDIAN_ALERT = "guardian_alert"
    SYSTEM_FAILURE = "system_failure"

class ResponseAction(Enum):
    """Automated response actions."""
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    QUARANTINE_FILE = "quarantine_file"
    BACKUP_EVIDENCE = "backup_evidence"
    NOTIFY_TEAM = "notify_team"
    ESCALATE_INCIDENT = "escalate_incident"
    INVOKE_GUARDIAN = "invoke_guardian"
    SNAPSHOT_SYSTEM = "snapshot_system"
    RESET_CREDENTIALS = "reset_credentials"

@dataclass
class IncidentArtifact:
    """Evidence and artifacts collected during incident."""
    id: str
    type: str  # log, file, memory_dump, network_capture, etc.
    source: str
    path: str
    hash_sha256: str
    collected_at: datetime
    size_bytes: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResponseStep:
    """Individual response step in a playbook."""
    id: str
    name: str
    description: str
    action: ResponseAction
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_count: int = 3
    requires_approval: bool = False
    depends_on: List[str] = field(default_factory=list)

@dataclass
class ResponsePlaybook:
    """Response playbook for incident types."""
    id: str
    name: str
    description: str
    incident_categories: List[IncidentCategory]
    severity_levels: List[IncidentSeverity]
    steps: List[ResponseStep] = field(default_factory=list)
    auto_execute: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Incident:
    """Security incident representation."""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    category: IncidentCategory
    source_events: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    artifacts: List[IncidentArtifact] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionResult:
    """Result of response step execution."""
    step_id: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    artifacts_collected: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IncidentResponseSystem:
    """Comprehensive incident response automation system."""

    def __init__(self,
                 guardian_integration: bool = True,
                 auto_containment: bool = True,
                 evidence_retention_days: int = 365):

        self.guardian_integration = guardian_integration
        self.auto_containment = auto_containment
        self.evidence_retention_days = evidence_retention_days

        # Core data
        self.incidents: Dict[str, Incident] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.active_responses: Dict[str, threading.Thread] = {}

        # Evidence storage
        self.evidence_path = os.getenv("LUKHAS_EVIDENCE_PATH", "./evidence")
        os.makedirs(self.evidence_path, exist_ok=True)

        # Performance tracking
        self.response_times: deque = deque(maxlen=1000)
        self.total_incidents = 0
        self.auto_resolved = 0

        # Initialize default playbooks
        self._initialize_default_playbooks()

        # Notification handlers
        self.notification_handlers: Dict[str, Callable] = {}

        logger.info("Incident Response System initialized")

    def _initialize_default_playbooks(self):
        """Initialize default response playbooks."""

        # Data breach response playbook
        data_breach_playbook = ResponsePlaybook(
            id="data_breach_response",
            name="Data Breach Response",
            description="Automated response for data breach incidents",
            incident_categories=[IncidentCategory.DATA_BREACH],
            severity_levels=[IncidentSeverity.P0_CRITICAL, IncidentSeverity.P1_HIGH],
            steps=[
                ResponseStep(
                    id="isolate_affected_systems",
                    name="Isolate Affected Systems",
                    description="Isolate systems involved in data breach",
                    action=ResponseAction.ISOLATE_SYSTEM,
                    parameters={"isolation_level": "network"}
                ),
                ResponseStep(
                    id="backup_evidence",
                    name="Backup Evidence",
                    description="Preserve evidence for forensic analysis",
                    action=ResponseAction.BACKUP_EVIDENCE,
                    depends_on=["isolate_affected_systems"]
                ),
                ResponseStep(
                    id="notify_incident_team",
                    name="Notify Incident Response Team",
                    description="Alert incident response team immediately",
                    action=ResponseAction.NOTIFY_TEAM,
                    parameters={"urgency": "critical", "team": "incident_response"}
                ),
                ResponseStep(
                    id="invoke_guardian",
                    name="Invoke Guardian System",
                    description="Activate Guardian emergency protocols",
                    action=ResponseAction.INVOKE_GUARDIAN,
                    parameters={"emergency_level": "high"}
                )
            ],
            auto_execute=True
        )

        # System compromise playbook
        system_compromise_playbook = ResponsePlaybook(
            id="system_compromise_response",
            name="System Compromise Response",
            description="Automated response for system compromise",
            incident_categories=[IncidentCategory.SYSTEM_COMPROMISE],
            severity_levels=[IncidentSeverity.P0_CRITICAL, IncidentSeverity.P1_HIGH, IncidentSeverity.P2_MEDIUM],
            steps=[
                ResponseStep(
                    id="snapshot_system",
                    name="Create System Snapshot",
                    description="Create forensic snapshot of compromised system",
                    action=ResponseAction.SNAPSHOT_SYSTEM
                ),
                ResponseStep(
                    id="isolate_system",
                    name="Isolate System",
                    description="Isolate compromised system from network",
                    action=ResponseAction.ISOLATE_SYSTEM,
                    depends_on=["snapshot_system"]
                ),
                ResponseStep(
                    id="reset_credentials",
                    name="Reset Credentials",
                    description="Reset credentials for affected accounts",
                    action=ResponseAction.RESET_CREDENTIALS,
                    requires_approval=True
                ),
                ResponseStep(
                    id="escalate_incident",
                    name="Escalate to Security Team",
                    description="Escalate incident to security team",
                    action=ResponseAction.ESCALATE_INCIDENT
                )
            ],
            auto_execute=False  # Requires manual approval
        )

        # Malware infection playbook
        malware_playbook = ResponsePlaybook(
            id="malware_response",
            name="Malware Infection Response",
            description="Automated response for malware infections",
            incident_categories=[IncidentCategory.MALWARE_INFECTION],
            severity_levels=[IncidentSeverity.P1_HIGH, IncidentSeverity.P2_MEDIUM],
            steps=[
                ResponseStep(
                    id="quarantine_file",
                    name="Quarantine Malicious Files",
                    description="Quarantine identified malicious files",
                    action=ResponseAction.QUARANTINE_FILE
                ),
                ResponseStep(
                    id="isolate_infected_system",
                    name="Isolate Infected System",
                    description="Isolate infected system to prevent spread",
                    action=ResponseAction.ISOLATE_SYSTEM,
                    parameters={"isolation_level": "partial"}
                ),
                ResponseStep(
                    id="collect_malware_sample",
                    name="Collect Malware Sample",
                    description="Collect malware sample for analysis",
                    action=ResponseAction.BACKUP_EVIDENCE,
                    parameters={"evidence_type": "malware_sample"}
                )
            ],
            auto_execute=True
        )

        # DoS attack playbook
        dos_playbook = ResponsePlaybook(
            id="dos_response",
            name="DoS Attack Response",
            description="Automated response for denial of service attacks",
            incident_categories=[IncidentCategory.DENIAL_OF_SERVICE],
            severity_levels=[IncidentSeverity.P1_HIGH, IncidentSeverity.P2_MEDIUM],
            steps=[
                ResponseStep(
                    id="block_attacking_ips",
                    name="Block Attacking IPs",
                    description="Block IP addresses involved in DoS attack",
                    action=ResponseAction.BLOCK_IP
                ),
                ResponseStep(
                    id="activate_ddos_protection",
                    name="Activate DDoS Protection",
                    description="Enable additional DDoS protection measures",
                    action=ResponseAction.ISOLATE_SYSTEM,
                    parameters={"protection_level": "enhanced"}
                ),
                ResponseStep(
                    id="notify_operations",
                    name="Notify Operations Team",
                    description="Alert operations team about ongoing attack",
                    action=ResponseAction.NOTIFY_TEAM,
                    parameters={"team": "operations", "urgency": "high"}
                )
            ],
            auto_execute=True
        )

        # Register playbooks
        for playbook in [data_breach_playbook, system_compromise_playbook, malware_playbook, dos_playbook]:
            self.register_playbook(playbook)

    def register_playbook(self, playbook: ResponsePlaybook):
        """Register a response playbook."""
        self.playbooks[playbook.id] = playbook
        logger.info(f"Registered playbook: {playbook.name}")

    def create_incident(self,
                       title: str,
                       description: str,
                       severity: IncidentSeverity,
                       category: IncidentCategory,
                       source_events: Optional[List[str]] = None,
                       affected_systems: Optional[List[str]] = None,
                       affected_users: Optional[List[str]] = None,
                       auto_respond: bool = True) -> str:
        """
        Create a new incident and trigger automated response.

        Args:
            title: Incident title
            description: Detailed description
            severity: Incident severity level
            category: Incident category
            source_events: List of source event IDs
            affected_systems: List of affected system IDs
            affected_users: List of affected user IDs
            auto_respond: Whether to trigger automated response

        Returns:
            Incident ID
        """
        start_time = time.perf_counter()

        # Generate unique incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # Create incident
        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.DETECTED,
            category=category,
            source_events=source_events or [],
            affected_systems=affected_systems or [],
            affected_users=affected_users or [],
            timeline=[{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "incident_created",
                "description": "Incident created and registered",
                "actor": "system"
            }]
        )

        # Store incident
        self.incidents[incident_id] = incident
        self.total_incidents += 1

        # Log incident creation
        logger.critical(f"INCIDENT_CREATED: {incident_id} - {title} [{severity.value}]")

        # Guardian integration
        if self.guardian_integration:
            self._notify_guardian(incident)

        # Trigger automated response
        if auto_respond:
            self._trigger_automated_response(incident)

        # Record performance metrics
        response_time = (time.perf_counter() - start_time) * 1000
        self.response_times.append(response_time)

        # Notifications
        self._send_notifications(incident, "incident_created")

        return incident_id

    def _trigger_automated_response(self, incident: Incident):
        """Trigger automated response for incident."""
        # Find matching playbooks
        matching_playbooks = self._find_matching_playbooks(incident)

        if not matching_playbooks:
            logger.warning(f"No matching playbooks for incident {incident.id}")
            self._add_timeline_entry(incident, "no_playbook", "No matching response playbooks found")
            return

        # Execute playbooks
        for playbook in matching_playbooks:
            if playbook.auto_execute or self.auto_containment:
                logger.info(f"Executing playbook {playbook.name} for incident {incident.id}")
                self._execute_playbook(incident, playbook)
            else:
                logger.info(f"Playbook {playbook.name} requires manual approval for incident {incident.id}")
                self._add_timeline_entry(incident, "playbook_pending", f"Playbook {playbook.name} pending approval")

    def _find_matching_playbooks(self, incident: Incident) -> List[ResponsePlaybook]:
        """Find playbooks matching incident criteria."""
        matching = []

        for playbook in self.playbooks.values():
            # Check category match
            if incident.category not in playbook.incident_categories:
                continue

            # Check severity match
            if incident.severity not in playbook.severity_levels:
                continue

            matching.append(playbook)

        # Sort by specificity (more specific categories first)
        matching.sort(key=lambda p: len(p.incident_categories))
        return matching

    def _execute_playbook(self, incident: Incident, playbook: ResponsePlaybook):
        """Execute response playbook for incident."""
        # Update incident status
        incident.status = IncidentStatus.ANALYZING
        incident.updated_at = datetime.now(timezone.utc)

        self._add_timeline_entry(incident, "playbook_started", f"Started executing playbook: {playbook.name}")

        # Create execution thread
        thread = threading.Thread(
            target=self._execute_playbook_thread,
            args=(incident, playbook),
            name=f"Playbook-{incident.id}",
            daemon=True
        )

        self.active_responses[incident.id] = thread
        thread.start()

    def _execute_playbook_thread(self, incident: Incident, playbook: ResponsePlaybook):
        """Execute playbook in separate thread."""
        try:
            # Build dependency graph
            step_dependencies = self._build_dependency_graph(playbook.steps)
            executed_steps = set()
            failed_steps = set()

            # Execute steps in dependency order
            while len(executed_steps) + len(failed_steps) < len(playbook.steps):
                progress_made = False

                for step in playbook.steps:
                    if step.id in executed_steps or step.id in failed_steps:
                        continue

                    # Check if dependencies are satisfied
                    dependencies_met = all(dep in executed_steps for dep in step.depends_on)

                    if dependencies_met:
                        # Check if step requires approval
                        if step.requires_approval and not self._has_approval(incident, step):
                            logger.info(f"Step {step.name} requires approval for incident {incident.id}")
                            self._request_approval(incident, step)
                            continue

                        # Execute step
                        result = self._execute_response_step(incident, step)

                        if result.success:
                            executed_steps.add(step.id)
                            self._add_timeline_entry(incident, "step_completed",
                                                   f"Completed step: {step.name}", result.metadata)
                        else:
                            failed_steps.add(step.id)
                            self._add_timeline_entry(incident, "step_failed",
                                                   f"Failed step: {step.name} - {result.error}")

                        progress_made = True

                # Break if no progress made (circular dependencies or all remaining need approval)
                if not progress_made:
                    break

            # Update incident status based on execution results
            if failed_steps:
                self._add_timeline_entry(incident, "playbook_partial",
                                       f"Playbook partially completed: {len(executed_steps)}/{len(playbook.steps)}")
                if len(executed_steps) == 0:
                    incident.status = IncidentStatus.DETECTED  # No progress made
                else:
                    incident.status = IncidentStatus.CONTAINED  # Partial containment
            else:
                self._add_timeline_entry(incident, "playbook_completed", "Playbook execution completed successfully")
                incident.status = IncidentStatus.CONTAINED

            incident.updated_at = datetime.now(timezone.utc)

        except Exception as e:
            logger.exception(f"Playbook execution error for incident {incident.id}: {e}")
            self._add_timeline_entry(incident, "playbook_error", f"Playbook execution error: {str(e)}")

        finally:
            # Remove from active responses
            if incident.id in self.active_responses:
                del self.active_responses[incident.id]

    def _build_dependency_graph(self, steps: List[ResponseStep]) -> Dict[str, Set[str]]:
        """Build dependency graph for steps."""
        dependencies = {}
        for step in steps:
            dependencies[step.id] = set(step.depends_on)
        return dependencies

    def _execute_response_step(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Execute individual response step."""
        start_time = time.perf_counter()

        logger.info(f"Executing step {step.name} for incident {incident.id}")

        try:
            # Execute based on action type
            if step.action == ResponseAction.ISOLATE_SYSTEM:
                result = self._isolate_system(incident, step)
            elif step.action == ResponseAction.BLOCK_IP:
                result = self._block_ip(incident, step)
            elif step.action == ResponseAction.DISABLE_ACCOUNT:
                result = self._disable_account(incident, step)
            elif step.action == ResponseAction.QUARANTINE_FILE:
                result = self._quarantine_file(incident, step)
            elif step.action == ResponseAction.BACKUP_EVIDENCE:
                result = self._backup_evidence(incident, step)
            elif step.action == ResponseAction.NOTIFY_TEAM:
                result = self._notify_team(incident, step)
            elif step.action == ResponseAction.ESCALATE_INCIDENT:
                result = self._escalate_incident(incident, step)
            elif step.action == ResponseAction.INVOKE_GUARDIAN:
                result = self._invoke_guardian(incident, step)
            elif step.action == ResponseAction.SNAPSHOT_SYSTEM:
                result = self._snapshot_system(incident, step)
            elif step.action == ResponseAction.RESET_CREDENTIALS:
                result = self._reset_credentials(incident, step)
            else:
                result = ExecutionResult(
                    step_id=step.id,
                    success=False,
                    output="",
                    error=f"Unknown action type: {step.action}"
                )

        except Exception as e:
            result = ExecutionResult(
                step_id=step.id,
                success=False,
                output="",
                error=str(e)
            )

        result.execution_time_ms = (time.perf_counter() - start_time) * 1000
        return result

    def _isolate_system(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Isolate affected systems."""
        isolation_level = step.parameters.get("isolation_level", "network")
        systems_isolated = []

        for system_id in incident.affected_systems:
            try:
                # Simulate system isolation
                logger.critical(f"ISOLATING_SYSTEM: {system_id} (level: {isolation_level})")

                # In production, would integrate with network infrastructure
                # to actually isolate systems (firewall rules, VLAN changes, etc.)

                systems_isolated.append(system_id)

            except Exception as e:
                logger.error(f"Failed to isolate system {system_id}: {e}")

        return ExecutionResult(
            step_id=step.id,
            success=len(systems_isolated) > 0,
            output=f"Isolated {len(systems_isolated)} systems",
            metadata={"isolated_systems": systems_isolated, "isolation_level": isolation_level}
        )

    def _block_ip(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Block malicious IP addresses."""
        blocked_ips = []

        # Extract IPs from incident metadata or parameters
        ips_to_block = step.parameters.get("ip_addresses", [])

        # Also check incident metadata for IPs
        if "source_ips" in incident.metadata:
            ips_to_block.extend(incident.metadata["source_ips"])

        for ip in ips_to_block:
            try:
                logger.critical(f"BLOCKING_IP: {ip}")

                # In production, would integrate with firewall/WAF to block IPs
                blocked_ips.append(ip)

            except Exception as e:
                logger.error(f"Failed to block IP {ip}: {e}")

        return ExecutionResult(
            step_id=step.id,
            success=len(blocked_ips) > 0,
            output=f"Blocked {len(blocked_ips)} IP addresses",
            metadata={"blocked_ips": blocked_ips}
        )

    def _backup_evidence(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Backup evidence for forensic analysis."""
        evidence_type = step.parameters.get("evidence_type", "general")
        collected_artifacts = []

        try:
            # Create evidence directory for incident
            incident_evidence_path = os.path.join(self.evidence_path, incident.id)
            os.makedirs(incident_evidence_path, exist_ok=True)

            # Collect various types of evidence
            if evidence_type in ["general", "logs"]:
                # Collect system logs
                artifact = self._collect_logs(incident, incident_evidence_path)
                if artifact:
                    collected_artifacts.append(artifact)

            if evidence_type in ["general", "memory"]:
                # Collect memory dumps
                artifact = self._collect_memory_dump(incident, incident_evidence_path)
                if artifact:
                    collected_artifacts.append(artifact)

            if evidence_type in ["general", "network"]:
                # Collect network captures
                artifact = self._collect_network_capture(incident, incident_evidence_path)
                if artifact:
                    collected_artifacts.append(artifact)

            # Add artifacts to incident
            incident.artifacts.extend(collected_artifacts)

        except Exception as e:
            return ExecutionResult(
                step_id=step.id,
                success=False,
                output="",
                error=f"Evidence collection failed: {e}"
            )

        return ExecutionResult(
            step_id=step.id,
            success=len(collected_artifacts) > 0,
            output=f"Collected {len(collected_artifacts)} evidence artifacts",
            artifacts_collected=[a.id for a in collected_artifacts]
        )

    def _collect_logs(self, incident: Incident, evidence_path: str) -> Optional[IncidentArtifact]:
        """Collect system logs as evidence."""
        try:
            log_file = os.path.join(evidence_path, f"system_logs_{int(time.time())}.txt")

            # Simulate log collection
            with open(log_file, 'w') as f:
                f.write(f"# System Logs for Incident {incident.id}\n")
                f.write(f"# Collected at: {datetime.now(timezone.utc).isoformat()}\n")
                f.write(f"# Incident: {incident.title}\n\n")
                f.write("Sample log entries would be collected here...\n")

            # Calculate hash
            with open(log_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            stat = os.stat(log_file)

            return IncidentArtifact(
                id=f"logs_{incident.id}_{int(time.time())}",
                type="logs",
                source="system",
                path=log_file,
                hash_sha256=file_hash,
                collected_at=datetime.now(timezone.utc),
                size_bytes=stat.st_size
            )

        except Exception as e:
            logger.error(f"Log collection failed: {e}")
            return None

    def _collect_memory_dump(self, incident: Incident, evidence_path: str) -> Optional[IncidentArtifact]:
        """Collect memory dump as evidence."""
        try:
            dump_file = os.path.join(evidence_path, f"memory_dump_{int(time.time())}.bin")

            # Simulate memory dump collection
            with open(dump_file, 'wb') as f:
                f.write(b"# Memory dump placeholder data\n")
                f.write(f"# Incident: {incident.id}\n".encode())

            with open(dump_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            stat = os.stat(dump_file)

            return IncidentArtifact(
                id=f"memory_{incident.id}_{int(time.time())}",
                type="memory_dump",
                source="system",
                path=dump_file,
                hash_sha256=file_hash,
                collected_at=datetime.now(timezone.utc),
                size_bytes=stat.st_size
            )

        except Exception as e:
            logger.error(f"Memory dump collection failed: {e}")
            return None

    def _collect_network_capture(self, incident: Incident, evidence_path: str) -> Optional[IncidentArtifact]:
        """Collect network capture as evidence."""
        try:
            pcap_file = os.path.join(evidence_path, f"network_capture_{int(time.time())}.pcap")

            # Simulate network capture
            with open(pcap_file, 'wb') as f:
                f.write(b"# Network capture placeholder\n")

            with open(pcap_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            stat = os.stat(pcap_file)

            return IncidentArtifact(
                id=f"network_{incident.id}_{int(time.time())}",
                type="network_capture",
                source="network",
                path=pcap_file,
                hash_sha256=file_hash,
                collected_at=datetime.now(timezone.utc),
                size_bytes=stat.st_size
            )

        except Exception as e:
            logger.error(f"Network capture failed: {e}")
            return None

    def _notify_team(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Notify incident response team."""
        team = step.parameters.get("team", "incident_response")
        urgency = step.parameters.get("urgency", "normal")

        logger.critical(f"TEAM_NOTIFICATION: Team={team}, Urgency={urgency}, Incident={incident.id}")

        # In production, would integrate with notification systems
        # (email, Slack, PagerDuty, etc.)

        return ExecutionResult(
            step_id=step.id,
            success=True,
            output=f"Notified {team} team with {urgency} urgency",
            metadata={"team": team, "urgency": urgency}
        )

    def _escalate_incident(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Escalate incident to higher authority."""
        incident.severity = IncidentSeverity.P0_CRITICAL  # Escalate to critical

        logger.critical(f"INCIDENT_ESCALATED: {incident.id} escalated to P0_CRITICAL")

        return ExecutionResult(
            step_id=step.id,
            success=True,
            output="Incident escalated to P0_CRITICAL",
            metadata={"new_severity": incident.severity.value}
        )

    def _invoke_guardian(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Invoke Guardian system emergency protocols."""
        emergency_level = step.parameters.get("emergency_level", "medium")

        logger.critical(f"GUARDIAN_INVOKED: Emergency level {emergency_level} for incident {incident.id}")

        # In production, would invoke actual Guardian system
        guardian_response = {
            "invoked_at": datetime.now(timezone.utc).isoformat(),
            "emergency_level": emergency_level,
            "protocols_activated": ["containment", "monitoring", "escalation"]
        }

        return ExecutionResult(
            step_id=step.id,
            success=True,
            output="Guardian emergency protocols activated",
            metadata=guardian_response
        )

    def _snapshot_system(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Create system snapshots for forensic analysis."""
        snapshots_created = []

        for system_id in incident.affected_systems:
            snapshot_id = f"snapshot_{system_id}_{int(time.time())}"
            logger.info(f"Creating snapshot {snapshot_id} for system {system_id}")

            # In production, would create actual VM/container snapshots
            snapshots_created.append(snapshot_id)

        return ExecutionResult(
            step_id=step.id,
            success=len(snapshots_created) > 0,
            output=f"Created {len(snapshots_created)} system snapshots",
            metadata={"snapshots": snapshots_created}
        )

    def _reset_credentials(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Reset credentials for affected accounts."""
        credentials_reset = []

        for user_id in incident.affected_users:
            logger.critical(f"RESETTING_CREDENTIALS: {user_id}")

            # In production, would integrate with identity management system
            credentials_reset.append(user_id)

        return ExecutionResult(
            step_id=step.id,
            success=len(credentials_reset) > 0,
            output=f"Reset credentials for {len(credentials_reset)} users",
            metadata={"users_reset": credentials_reset}
        )

    def _quarantine_file(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Quarantine malicious files."""
        files_quarantined = []

        # Get file paths from incident metadata or step parameters
        files_to_quarantine = step.parameters.get("file_paths", [])

        for file_path in files_to_quarantine:
            try:
                logger.critical(f"QUARANTINING_FILE: {file_path}")

                # In production, would move files to secure quarantine location
                files_quarantined.append(file_path)

            except Exception as e:
                logger.error(f"Failed to quarantine file {file_path}: {e}")

        return ExecutionResult(
            step_id=step.id,
            success=len(files_quarantined) > 0,
            output=f"Quarantined {len(files_quarantined)} files",
            metadata={"quarantined_files": files_quarantined}
        )

    def _disable_account(self, incident: Incident, step: ResponseStep) -> ExecutionResult:
        """Disable user accounts."""
        accounts_disabled = []

        for user_id in incident.affected_users:
            logger.critical(f"DISABLING_ACCOUNT: {user_id}")

            # In production, would integrate with identity management system
            accounts_disabled.append(user_id)

        return ExecutionResult(
            step_id=step.id,
            success=len(accounts_disabled) > 0,
            output=f"Disabled {len(accounts_disabled)} accounts",
            metadata={"disabled_accounts": accounts_disabled}
        )

    def _has_approval(self, incident: Incident, step: ResponseStep) -> bool:
        """Check if step has required approval."""
        # In production, would check approval system
        return False  # Require manual approval for demo

    def _request_approval(self, incident: Incident, step: ResponseStep):
        """Request approval for step execution."""
        logger.warning(f"APPROVAL_REQUIRED: Step '{step.name}' requires approval for incident {incident.id}")

        # In production, would integrate with approval workflow system
        self._add_timeline_entry(incident, "approval_requested", f"Approval requested for step: {step.name}")

    def _add_timeline_entry(self, incident: Incident, event: str, description: str, metadata: Optional[Dict[str, Any]] = None):
        """Add entry to incident timeline."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "description": description,
            "actor": "system"
        }

        if metadata:
            entry["metadata"] = metadata

        incident.timeline.append(entry)
        incident.updated_at = datetime.now(timezone.utc)

    def _notify_guardian(self, incident: Incident):
        """Notify Guardian system about incident."""
        if not self.guardian_integration:
            return

        try:
            guardian_payload = {
                "incident_id": incident.id,
                "title": incident.title,
                "severity": incident.severity.value,
                "category": incident.category.value,
                "affected_systems": incident.affected_systems,
                "created_at": incident.created_at.isoformat()
            }

            logger.info(f"GUARDIAN_NOTIFIED: {incident.id}")
            # In production, would send to actual Guardian system

        except Exception as e:
            logger.error(f"Guardian notification failed: {e}")

    def _send_notifications(self, incident: Incident, event_type: str):
        """Send notifications to registered handlers."""
        for handler_name, handler in self.notification_handlers.items():
            try:
                handler(incident, event_type)
            except Exception as e:
                logger.error(f"Notification handler {handler_name} failed: {e}")

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID."""
        return self.incidents.get(incident_id)

    def get_active_incidents(self) -> List[Incident]:
        """Get all active (non-closed) incidents."""
        return [inc for inc in self.incidents.values()
                if inc.status != IncidentStatus.CLOSED]

    def close_incident(self, incident_id: str, resolution: str) -> bool:
        """Close an incident."""
        if incident_id not in self.incidents:
            return False

        incident = self.incidents[incident_id]
        incident.status = IncidentStatus.CLOSED
        incident.resolved_at = datetime.now(timezone.utc)
        incident.updated_at = datetime.now(timezone.utc)

        self._add_timeline_entry(incident, "incident_closed", f"Incident closed: {resolution}")

        logger.info(f"INCIDENT_CLOSED: {incident_id}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get incident response statistics."""
        active_incidents = len(self.get_active_incidents())
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        return {
            "total_incidents": self.total_incidents,
            "active_incidents": active_incidents,
            "auto_resolved": self.auto_resolved,
            "avg_response_time_ms": avg_response_time,
            "performance_target_met": avg_response_time < 5.0,
            "registered_playbooks": len(self.playbooks),
            "active_responses": len(self.active_responses)
        }

# Factory function
def create_incident_response_system(config: Optional[Dict[str, Any]] = None) -> IncidentResponseSystem:
    """Create incident response system with configuration."""
    config = config or {}

    return IncidentResponseSystem(
        guardian_integration=config.get("guardian_integration", True),
        auto_containment=config.get("auto_containment", True),
        evidence_retention_days=config.get("evidence_retention_days", 365)
    )

if __name__ == "__main__":
    # Example usage and testing
    irs = create_incident_response_system()

    print("Incident Response System Test")
    print("=" * 40)

    # Test data breach incident
    print("\n1. Creating Data Breach Incident:")
    breach_id = irs.create_incident(
        title="Customer Database Breach",
        description="Unauthorized access to customer database detected",
        severity=IncidentSeverity.P0_CRITICAL,
        category=IncidentCategory.DATA_BREACH,
        affected_systems=["db-prod-01", "web-app-01"],
        affected_users=["compromised_admin"]
    )
    print(f"Created incident: {breach_id}")

    # Test system compromise
    print("\n2. Creating System Compromise Incident:")
    compromise_id = irs.create_incident(
        title="Server Compromise Detected",
        description="Malicious activity detected on production server",
        severity=IncidentSeverity.P1_HIGH,
        category=IncidentCategory.SYSTEM_COMPROMISE,
        affected_systems=["srv-prod-02"]
    )
    print(f"Created incident: {compromise_id}")

    # Wait for automated response
    print("\n3. Waiting for automated response...")
    time.sleep(3)

    # Check incident status
    breach_incident = irs.get_incident(breach_id)
    if breach_incident:
        print(f"\nBreach Incident Status: {breach_incident.status.value}")
        print(f"Timeline entries: {len(breach_incident.timeline)}")
        print(f"Artifacts collected: {len(breach_incident.artifacts)}")

    # Check statistics
    stats = irs.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total incidents: {stats['total_incidents']}")
    print(f"  Active incidents: {stats['active_incidents']}")
    print(f"  Avg response time: {stats['avg_response_time_ms']:.2f}ms")
    print(f"  Registered playbooks: {stats['registered_playbooks']}")
    print(f"  Performance target met: {stats['performance_target_met']}")

    print("\nIncident Response System test completed")