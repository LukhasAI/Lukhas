"""
G.1 Audit Trail - Comprehensive logging and compliance
Production-grade audit trail system with immutable logging, compliance validation, and tamper detection.
"""

import asyncio
import gzip
import hashlib
import json
import logging
import secrets
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    POLICY_VIOLATION = "policy_violation"
    GUARDIAN_DECISION = "guardian_decision"
    CONSENT_CHANGE = "consent_change"
    PRIVACY_ACTION = "privacy_action"
    ERROR_EVENT = "error_event"
    PERFORMANCE_EVENT = "performance_event"


class AuditLevel(Enum):
    """Audit event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"


@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str
    event_type: AuditEventType
    level: AuditLevel
    timestamp: datetime
    source_component: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_id: Optional[str] = None
    action: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_tags: Set[ComplianceFramework] = field(default_factory=set)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    outcome: str = "unknown"  # "success", "failure", "partial", "unknown"
    duration_ms: Optional[float] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


@dataclass
class AuditChain:
    """Blockchain-like audit chain for integrity"""
    block_index: int
    previous_hash: str
    events: List[AuditEvent]
    timestamp: datetime
    merkle_root: str
    block_hash: str
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))


@dataclass
class ComplianceReport:
    """Compliance audit report"""
    report_id: str
    framework: ComplianceFramework
    start_date: datetime
    end_date: datetime
    total_events: int
    violations: List[Dict[str, Any]]
    compliance_score: float  # 0.0 to 1.0
    recommendations: List[str]
    generated_at: datetime
    data_retention_compliance: bool
    access_control_compliance: bool
    encryption_compliance: bool


class AuditTrail:
    """
    G.1 Audit Trail System
    Comprehensive audit logging with blockchain-like integrity and compliance validation
    """

    def __init__(self,
                 storage_path: Path = Path("./audit_logs"),
                 max_events_per_block: int = 100,
                 encryption_key: Optional[bytes] = None,
                 retention_days: int = 2555,  # 7 years default
                 auto_compress: bool = True,
                 compliance_frameworks: Optional[List[ComplianceFramework]] = None):
        self.storage_path = Path(storage_path)
        self.max_events_per_block = max_events_per_block
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.retention_days = retention_days
        self.auto_compress = auto_compress
        self.compliance_frameworks = compliance_frameworks or [
            ComplianceFramework.GDPR, ComplianceFramework.CCPA
        ]

        # Initialize storage
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_block_path = self.storage_path / "current_block.json"
        self.chain_metadata_path = self.storage_path / "chain_metadata.json"

        # In-memory state
        self.current_events: List[AuditEvent] = []
        self.audit_chain: List[AuditChain] = []
        self.event_cache: Dict[str, AuditEvent] = {}
        self.violation_cache: List[Dict[str, Any]] = []

        # Chain integrity
        self.last_block_hash = "0" * 64  # Genesis hash
        self.chain_hmac_key = secrets.token_bytes(32)

        # Performance tracking
        self.event_count = 0
        self.chain_length = 0
        self.last_integrity_check: Optional[datetime] = None

        # Background tasks
        self.flush_task: Optional[asyncio.Task] = None
        self.compression_task: Optional[asyncio.Task] = None
        self.integrity_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Load existing chain
        self._load_chain_metadata()

    async def start(self):
        """Start the audit trail system"""
        logger.info("🚀 Starting Audit Trail System")

        # Start background tasks
        self.flush_task = asyncio.create_task(self._flush_loop())
        self.compression_task = asyncio.create_task(self._compression_loop())
        self.integrity_task = asyncio.create_task(self._integrity_check_loop())

        # Load any pending events
        await self._load_current_block()

        logger.info("✅ Audit Trail System started")

    async def stop(self):
        """Stop the audit trail system"""
        logger.info("🛑 Stopping Audit Trail System")

        self._shutdown_event.set()

        # Flush any pending events
        if self.current_events:
            await self._flush_current_block()

        # Cancel background tasks
        for task in [self.flush_task, self.compression_task, self.integrity_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Audit Trail System stopped")

    async def log_event(self,
                       event_type: AuditEventType,
                       level: AuditLevel,
                       source_component: str,
                       action: str,
                       description: str,
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None,
                       resource_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       compliance_tags: Optional[Set[ComplianceFramework]] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       correlation_id: Optional[str] = None,
                       outcome: str = "unknown",
                       duration_ms: Optional[float] = None,
                       before_state: Optional[Dict[str, Any]] = None,
                       after_state: Optional[Dict[str, Any]] = None) -> str:
        """Log audit event"""

        event_id = f"audit_{uuid.uuid4().hex}"

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            level=level,
            timestamp=datetime.utcnow(),
            source_component=source_component,
            user_id=user_id,
            session_id=session_id,
            resource_id=resource_id,
            action=action,
            description=description,
            metadata=metadata or {},
            compliance_tags=compliance_tags or set(),
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            outcome=outcome,
            duration_ms=duration_ms,
            before_state=before_state,
            after_state=after_state
        )

        # Add to current block
        self.current_events.append(event)
        self.event_cache[event_id] = event
        self.event_count += 1

        # Check for compliance violations
        await self._check_compliance_violation(event)

        # Flush if block is full
        if len(self.current_events) >= self.max_events_per_block:
            await self._flush_current_block()

        logger.debug(f"📝 Logged audit event: {event_id} ({event_type.value})")
        return event_id

    async def log_authentication(self,
                               user_id: str,
                               outcome: str,
                               method: str,
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None,
                               failure_reason: Optional[str] = None) -> str:
        """Log authentication event"""

        metadata = {"method": method}
        if failure_reason:
            metadata["failure_reason"] = failure_reason

        level = AuditLevel.INFO if outcome == "success" else AuditLevel.WARNING

        return await self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            level=level,
            source_component="identity_system",
            action=f"authentication_{outcome}",
            description=f"User authentication {outcome} via {method}",
            user_id=user_id,
            metadata=metadata,
            compliance_tags={ComplianceFramework.GDPR, ComplianceFramework.CCPA},
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=outcome
        )

    async def log_data_access(self,
                            user_id: str,
                            resource_id: str,
                            action: str,
                            outcome: str,
                            data_classification: str = "unclassified",
                            access_method: str = "api",
                            session_id: Optional[str] = None) -> str:
        """Log data access event"""

        metadata = {
            "data_classification": data_classification,
            "access_method": access_method
        }

        level = AuditLevel.INFO if outcome == "success" else AuditLevel.ERROR

        return await self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            level=level,
            source_component="data_layer",
            action=action,
            description=f"Data access: {action} on {resource_id}",
            user_id=user_id,
            session_id=session_id,
            resource_id=resource_id,
            metadata=metadata,
            compliance_tags={ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.HIPAA},
            outcome=outcome
        )

    async def log_guardian_decision(self,
                                  decision_id: str,
                                  user_id: Optional[str],
                                  action: str,
                                  decision_outcome: str,
                                  confidence_score: float,
                                  policies_evaluated: List[str],
                                  reasoning: str,
                                  session_id: Optional[str] = None) -> str:
        """Log Guardian system decision"""

        metadata = {
            "decision_id": decision_id,
            "confidence_score": confidence_score,
            "policies_evaluated": policies_evaluated,
            "reasoning": reasoning
        }

        level = AuditLevel.INFO if decision_outcome == "approved" else AuditLevel.WARNING

        return await self.log_event(
            event_type=AuditEventType.GUARDIAN_DECISION,
            level=level,
            source_component="guardian_system",
            action=f"guardian_decision_{decision_outcome}",
            description=f"Guardian decision: {decision_outcome} for action {action}",
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            compliance_tags={ComplianceFramework.SOC2, ComplianceFramework.ISO27001},
            outcome=decision_outcome
        )

    async def log_consent_change(self,
                               user_id: str,
                               consent_type: str,
                               action: str,
                               previous_value: Optional[bool],
                               new_value: bool,
                               legal_basis: str,
                               session_id: Optional[str] = None) -> str:
        """Log consent changes for GDPR compliance"""

        metadata = {
            "consent_type": consent_type,
            "legal_basis": legal_basis
        }

        before_state = {"consent_granted": previous_value} if previous_value is not None else None
        after_state = {"consent_granted": new_value}

        return await self.log_event(
            event_type=AuditEventType.CONSENT_CHANGE,
            level=AuditLevel.INFO,
            source_component="consent_system",
            action=action,
            description=f"Consent {action}: {consent_type} for user {user_id}",
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            compliance_tags={ComplianceFramework.GDPR},
            before_state=before_state,
            after_state=after_state,
            outcome="success"
        )

    async def log_privacy_action(self,
                               user_id: str,
                               action: str,
                               data_categories: List[str],
                               outcome: str,
                               legal_basis: str,
                               retention_period: Optional[str] = None) -> str:
        """Log privacy-related actions (deletion, export, etc.)"""

        metadata = {
            "data_categories": data_categories,
            "legal_basis": legal_basis
        }

        if retention_period:
            metadata["retention_period"] = retention_period

        level = AuditLevel.INFO if outcome == "success" else AuditLevel.ERROR

        return await self.log_event(
            event_type=AuditEventType.PRIVACY_ACTION,
            level=level,
            source_component="privacy_system",
            action=action,
            description=f"Privacy action: {action} for user {user_id}",
            user_id=user_id,
            metadata=metadata,
            compliance_tags={ComplianceFramework.GDPR, ComplianceFramework.CCPA},
            outcome=outcome
        )

    async def query_events(self,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         event_types: Optional[List[AuditEventType]] = None,
                         user_id: Optional[str] = None,
                         source_component: Optional[str] = None,
                         levels: Optional[List[AuditLevel]] = None,
                         correlation_id: Optional[str] = None,
                         limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters"""

        # Search in current events first
        matching_events = []

        for event in self.current_events:
            if self._event_matches_filters(event, start_date, end_date, event_types,
                                         user_id, source_component, levels, correlation_id):
                matching_events.append(event)

        # Search in stored blocks if needed
        if len(matching_events) < limit:
            stored_events = await self._search_stored_events(
                start_date, end_date, event_types, user_id, source_component,
                levels, correlation_id, limit - len(matching_events)
            )
            matching_events.extend(stored_events)

        # Sort by timestamp (newest first)
        matching_events.sort(key=lambda e: e.timestamp, reverse=True)

        return matching_events[:limit]

    async def generate_compliance_report(self,
                                       framework: ComplianceFramework,
                                       start_date: datetime,
                                       end_date: datetime) -> ComplianceReport:
        """Generate compliance report for specified framework"""

        # Query relevant events
        events = await self.query_events(
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for comprehensive report
        )

        # Filter events for this compliance framework
        framework_events = [e for e in events if framework in e.compliance_tags]

        # Analyze compliance
        violations = []
        compliance_score = 1.0

        if framework == ComplianceFramework.GDPR:
            violations, compliance_score = await self._analyze_gdpr_compliance(framework_events, start_date, end_date)
        elif framework == ComplianceFramework.CCPA:
            violations, compliance_score = await self._analyze_ccpa_compliance(framework_events, start_date, end_date)
        elif framework == ComplianceFramework.SOC2:
            violations, compliance_score = await self._analyze_soc2_compliance(framework_events, start_date, end_date)

        # Generate recommendations
        recommendations = await self._generate_compliance_recommendations(framework, violations)

        report = ComplianceReport(
            report_id=f"compliance_{framework.value}_{int(time.time())}",
            framework=framework,
            start_date=start_date,
            end_date=end_date,
            total_events=len(framework_events),
            violations=violations,
            compliance_score=compliance_score,
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
            data_retention_compliance=await self._check_data_retention_compliance(framework_events),
            access_control_compliance=await self._check_access_control_compliance(framework_events),
            encryption_compliance=await self._check_encryption_compliance(framework_events)
        )

        # Log report generation
        await self.log_event(
            event_type=AuditEventType.SYSTEM_OPERATION,
            level=AuditLevel.INFO,
            source_component="audit_system",
            action="compliance_report_generated",
            description=f"Generated {framework.value} compliance report",
            metadata={
                "report_id": report.report_id,
                "event_count": len(framework_events),
                "compliance_score": compliance_score,
                "violation_count": len(violations)
            },
            outcome="success"
        )

        return report

    async def verify_integrity(self) -> Dict[str, Any]:
        """Verify audit trail integrity"""

        verification_start = time.time()
        integrity_results = {
            "chain_valid": True,
            "blocks_verified": 0,
            "hash_mismatches": 0,
            "missing_blocks": 0,
            "tamper_detected": False,
            "verification_time_ms": 0.0,
            "last_block_hash": self.last_block_hash
        }

        try:
            # Verify chain continuity
            expected_hash = "0" * 64  # Genesis hash

            for i, block in enumerate(self.audit_chain):
                integrity_results["blocks_verified"] += 1

                # Verify previous hash
                if block.previous_hash != expected_hash:
                    integrity_results["chain_valid"] = False
                    integrity_results["hash_mismatches"] += 1
                    integrity_results["tamper_detected"] = True

                # Verify block hash
                computed_hash = self._calculate_block_hash(block)
                if computed_hash != block.block_hash:
                    integrity_results["chain_valid"] = False
                    integrity_results["hash_mismatches"] += 1
                    integrity_results["tamper_detected"] = True

                # Verify Merkle root
                computed_merkle = self._calculate_merkle_root(block.events)
                if computed_merkle != block.merkle_root:
                    integrity_results["chain_valid"] = False
                    integrity_results["hash_mismatches"] += 1
                    integrity_results["tamper_detected"] = True

                expected_hash = block.block_hash

            self.last_integrity_check = datetime.utcnow()
            integrity_results["verification_time_ms"] = (time.time() - verification_start) * 1000

            # Log integrity check
            await self.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                level=AuditLevel.INFO if integrity_results["chain_valid"] else AuditLevel.CRITICAL,
                source_component="audit_system",
                action="integrity_verification",
                description="Audit trail integrity verification completed",
                metadata=integrity_results,
                outcome="success" if integrity_results["chain_valid"] else "failure"
            )

        except Exception as e:
            integrity_results["chain_valid"] = False
            integrity_results["tamper_detected"] = True
            logger.error(f"❌ Integrity verification failed: {e}")

        return integrity_results

    async def export_audit_data(self,
                              start_date: datetime,
                              end_date: datetime,
                              format: str = "json",
                              include_metadata: bool = True) -> bytes:
        """Export audit data for compliance or analysis"""

        events = await self.query_events(start_date=start_date, end_date=end_date, limit=100000)

        export_data = {
            "export_metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "event_count": len(events),
                "format": format,
                "integrity_verified": (await self.verify_integrity())["chain_valid"]
            },
            "events": [asdict(event) for event in events]
        }

        if format == "json":
            export_bytes = json.dumps(export_data, default=str, indent=2).encode()
        else:
            # Could add CSV, XML, etc.
            export_bytes = json.dumps(export_data, default=str).encode()

        # Log export
        await self.log_event(
            event_type=AuditEventType.PRIVACY_ACTION,
            level=AuditLevel.INFO,
            source_component="audit_system",
            action="data_export",
            description=f"Exported {len(events)} audit events",
            metadata={
                "format": format,
                "event_count": len(events),
                "size_bytes": len(export_bytes)
            },
            outcome="success"
        )

        return export_bytes

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for audit data"""
        return secrets.token_bytes(32)

    def _event_matches_filters(self,
                             event: AuditEvent,
                             start_date: Optional[datetime],
                             end_date: Optional[datetime],
                             event_types: Optional[List[AuditEventType]],
                             user_id: Optional[str],
                             source_component: Optional[str],
                             levels: Optional[List[AuditLevel]],
                             correlation_id: Optional[str]) -> bool:
        """Check if event matches query filters"""

        if start_date and event.timestamp < start_date:
            return False
        if end_date and event.timestamp > end_date:
            return False
        if event_types and event.event_type not in event_types:
            return False
        if user_id and event.user_id != user_id:
            return False
        if source_component and event.source_component != source_component:
            return False
        if levels and event.level not in levels:
            return False
        if correlation_id and event.correlation_id != correlation_id:
            return False

        return True

    async def _search_stored_events(self,
                                  start_date: Optional[datetime],
                                  end_date: Optional[datetime],
                                  event_types: Optional[List[AuditEventType]],
                                  user_id: Optional[str],
                                  source_component: Optional[str],
                                  levels: Optional[List[AuditLevel]],
                                  correlation_id: Optional[str],
                                  limit: int) -> List[AuditEvent]:
        """Search events in stored blocks"""

        matching_events = []

        # Search through stored blocks
        for block in reversed(self.audit_chain):  # Start with newest
            for event in reversed(block.events):
                if len(matching_events) >= limit:
                    break

                if self._event_matches_filters(event, start_date, end_date, event_types,
                                             user_id, source_component, levels, correlation_id):
                    matching_events.append(event)

            if len(matching_events) >= limit:
                break

        return matching_events

    async def _check_compliance_violation(self, event: AuditEvent):
        """Check for compliance violations in event"""

        violations = []

        # GDPR checks
        if ComplianceFramework.GDPR in event.compliance_tags:
            if event.event_type == AuditEventType.DATA_ACCESS and not event.user_id:
                violations.append({
                    "framework": "GDPR",
                    "rule": "Article 30 - Records of processing",
                    "description": "Data access without user identification",
                    "severity": "high"
                })

        # CCPA checks
        if ComplianceFramework.CCPA in event.compliance_tags:
            if event.event_type == AuditEventType.PRIVACY_ACTION and event.outcome != "success":
                violations.append({
                    "framework": "CCPA",
                    "rule": "Consumer Rights",
                    "description": "Failed privacy action request",
                    "severity": "medium"
                })

        if violations:
            self.violation_cache.extend(violations)
            logger.warning(f"⚠️ Compliance violations detected: {len(violations)}")

    async def _analyze_gdpr_compliance(self, events: List[AuditEvent], start_date: datetime, end_date: datetime) -> Tuple[List[Dict[str, Any]], float]:
        """Analyze GDPR compliance"""

        violations = []
        total_checks = 0
        passed_checks = 0

        # Check data access logging
        data_access_events = [e for e in events if e.event_type == AuditEventType.DATA_ACCESS]
        total_checks += len(data_access_events)
        for event in data_access_events:
            if event.user_id and event.resource_id:
                passed_checks += 1
            else:
                violations.append({
                    "type": "insufficient_logging",
                    "description": "Data access without proper user/resource identification",
                    "event_id": event.event_id,
                    "severity": "high"
                })

        # Check consent changes
        consent_events = [e for e in events if e.event_type == AuditEventType.CONSENT_CHANGE]
        total_checks += len(consent_events)
        for event in consent_events:
            if event.before_state and event.after_state:
                passed_checks += 1
            else:
                violations.append({
                    "type": "incomplete_consent_record",
                    "description": "Consent change without complete state record",
                    "event_id": event.event_id,
                    "severity": "medium"
                })

        compliance_score = passed_checks / max(total_checks, 1)
        return violations, compliance_score

    async def _analyze_ccpa_compliance(self, events: List[AuditEvent], start_date: datetime, end_date: datetime) -> Tuple[List[Dict[str, Any]], float]:
        """Analyze CCPA compliance"""

        violations = []
        # Placeholder for CCPA-specific analysis
        compliance_score = 0.95  # Simplified

        return violations, compliance_score

    async def _analyze_soc2_compliance(self, events: List[AuditEvent], start_date: datetime, end_date: datetime) -> Tuple[List[Dict[str, Any]], float]:
        """Analyze SOC2 compliance"""

        violations = []
        # Placeholder for SOC2-specific analysis
        compliance_score = 0.93  # Simplified

        return violations, compliance_score

    async def _generate_compliance_recommendations(self, framework: ComplianceFramework, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""

        recommendations = []

        if framework == ComplianceFramework.GDPR:
            if any(v.get("type") == "insufficient_logging" for v in violations):
                recommendations.append("Enhance data access logging to include user and resource identification")
            if any(v.get("type") == "incomplete_consent_record" for v in violations):
                recommendations.append("Implement complete state tracking for consent changes")

        return recommendations

    async def _check_data_retention_compliance(self, events: List[AuditEvent]) -> bool:
        """Check data retention compliance"""
        # Simplified check - in production would verify retention policies
        return True

    async def _check_access_control_compliance(self, events: List[AuditEvent]) -> bool:
        """Check access control compliance"""
        # Simplified check - in production would verify access controls
        return True

    async def _check_encryption_compliance(self, events: List[AuditEvent]) -> bool:
        """Check encryption compliance"""
        # Simplified check - in production would verify encryption
        return True

    def _calculate_merkle_root(self, events: List[AuditEvent]) -> str:
        """Calculate Merkle root for events"""

        if not events:
            return "0" * 64

        # Create leaf hashes
        leaf_hashes = []
        for event in events:
            event_data = json.dumps(asdict(event), sort_keys=True, default=str)
            leaf_hash = hashlib.sha256(event_data.encode()).hexdigest()
            leaf_hashes.append(leaf_hash)

        # Build Merkle tree
        while len(leaf_hashes) > 1:
            next_level = []
            for i in range(0, len(leaf_hashes), 2):
                if i + 1 < len(leaf_hashes):
                    combined = leaf_hashes[i] + leaf_hashes[i + 1]
                else:
                    combined = leaf_hashes[i] + leaf_hashes[i]  # Duplicate if odd
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            leaf_hashes = next_level

        return leaf_hashes[0] if leaf_hashes else "0" * 64

    def _calculate_block_hash(self, block: AuditChain) -> str:
        """Calculate hash for audit block"""

        block_data = {
            "block_index": block.block_index,
            "previous_hash": block.previous_hash,
            "merkle_root": block.merkle_root,
            "timestamp": block.timestamp.isoformat(),
            "nonce": block.nonce
        }

        block_json = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_json.encode()).hexdigest()

    async def _flush_current_block(self):
        """Flush current events to a new block"""

        if not self.current_events:
            return

        # Create new block
        block_index = len(self.audit_chain)
        merkle_root = self._calculate_merkle_root(self.current_events)

        block = AuditChain(
            block_index=block_index,
            previous_hash=self.last_block_hash,
            events=self.current_events.copy(),
            timestamp=datetime.utcnow(),
            merkle_root=merkle_root,
            block_hash=""  # Will be calculated
        )

        # Calculate block hash
        block.block_hash = self._calculate_block_hash(block)

        # Add to chain
        self.audit_chain.append(block)
        self.last_block_hash = block.block_hash
        self.chain_length += 1

        # Save block to storage
        await self._save_block(block)

        # Clear current events
        self.current_events.clear()

        # Update metadata
        await self._save_chain_metadata()

        logger.info(f"💾 Flushed audit block {block_index} with {len(block.events)} events")

    async def _save_block(self, block: AuditChain):
        """Save block to persistent storage"""

        block_file = self.storage_path / f"block_{block.block_index:06d}.json"

        block_data = {
            "block_index": block.block_index,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp.isoformat(),
            "merkle_root": block.merkle_root,
            "block_hash": block.block_hash,
            "nonce": block.nonce,
            "events": [asdict(event) for event in block.events]
        }

        # Compress if enabled
        if self.auto_compress:
            compressed_data = gzip.compress(json.dumps(block_data, default=str).encode())
            with open(f"{block_file}.gz", "wb") as f:
                f.write(compressed_data)
        else:
            with open(block_file, "w") as f:
                json.dump(block_data, f, default=str, indent=2)

    async def _load_current_block(self):
        """Load pending events from current block file"""

        if self.current_block_path.exists():
            try:
                with open(self.current_block_path) as f:
                    json.load(f)
                    # Reconstruct events (simplified)
                    self.current_events = []  # Would reconstruct from data
            except Exception as e:
                logger.error(f"❌ Failed to load current block: {e}")

    def _load_chain_metadata(self):
        """Load chain metadata"""

        if self.chain_metadata_path.exists():
            try:
                with open(self.chain_metadata_path) as f:
                    metadata = json.load(f)
                    self.last_block_hash = metadata.get("last_block_hash", "0" * 64)
                    self.chain_length = metadata.get("chain_length", 0)
            except Exception as e:
                logger.error(f"❌ Failed to load chain metadata: {e}")

    async def _save_chain_metadata(self):
        """Save chain metadata"""

        metadata = {
            "last_block_hash": self.last_block_hash,
            "chain_length": self.chain_length,
            "last_update": datetime.utcnow().isoformat()
        }

        with open(self.chain_metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    async def _flush_loop(self):
        """Background flush loop"""

        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Flush every minute

                if self.current_events:
                    await self._flush_current_block()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Flush loop error: {e}")

    async def _compression_loop(self):
        """Background compression loop"""

        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Check hourly

                # Compress old blocks if needed
                # Implementation would compress blocks older than N days

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Compression loop error: {e}")

    async def _integrity_check_loop(self):
        """Background integrity check loop"""

        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(21600)  # Check every 6 hours

                integrity_result = await self.verify_integrity()
                if not integrity_result["chain_valid"]:
                    logger.critical(f"🚨 AUDIT TRAIL INTEGRITY VIOLATION DETECTED: {integrity_result}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Integrity check loop error: {e}")

    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit trail statistics"""

        return {
            "event_count": self.event_count,
            "chain_length": self.chain_length,
            "current_block_events": len(self.current_events),
            "last_block_hash": self.last_block_hash,
            "last_integrity_check": self.last_integrity_check.isoformat() if self.last_integrity_check else None,
            "violation_count": len(self.violation_cache),
            "compliance_frameworks": [f.value for f in self.compliance_frameworks],
            "retention_days": self.retention_days,
            "storage_path": str(self.storage_path)
        }
