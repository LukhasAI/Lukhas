#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Lambda Auditor

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

ΛAUDITOR – Symbolic Compliance and Integrity Auditor CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL

For more information, visit: https://lukhas.ai
"""

import json
import os
import glob
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)


class ViolationType(Enum):
    """Classification of compliance violations."""
    UNJUSTIFIED_ESCALATION = "UNJUSTIFIED_ESCALATION"
    MISSING_GOVERNOR_OVERSIGHT = "MISSING_GOVERNOR_OVERSIGHT"
    DRIFT_CONTAINMENT_FAILURE = "DRIFT_CONTAINMENT_FAILURE"
    NON_HARMONIC_GLYPH_REINSERTION = "NON_HARMONIC_GLYPH_REINSERTION"
    CONFLICT_RECURSION_LOOP = "CONFLICT_RECURSION_LOOP"


class AuditStatus(Enum):
    """Audit check status."""
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    WARNING = "⚠️ WARNING"
    MISSING = "🔍 MISSING"


@dataclass
class AuditEvent:
    """Structured audit event from log parsing."""
    timestamp: str
    event_type: str  # ethical_alert, governor_decision, drift_event, etc.
    source_module: str
    event_data: Dict[str, Any]
    risk_level: Optional[str] = None
    intervention_type: Optional[str] = None
    glyph_state: Optional[Dict[str, Any]] = None
    trust_score_delta: Optional[float] = None
    log_file: Optional[str] = None

    def __post_init__(self):
        """Extract common fields from event data."""
        if isinstance(self.event_data, dict):
            self.risk_level = self.event_data.get('risk_level')
            self.intervention_type = self.event_data.get('intervention_type')
            self.glyph_state = self.event_data.get('glyph_state')
            self.trust_score_delta = self.event_data.get('trust_score_delta')


@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    violation_type: ViolationType
    timestamp: str
    source_file: str
    event_id: Optional[str]
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    suggested_fix: str
    trust_score_impact: Optional[float] = None
    related_events: List[str] = field(default_factory=list)


@dataclass
class AuditResult:
    """Comprehensive audit result."""
    audit_timestamp: str
    total_events_processed: int
    passed_checks: List[str]
    violations: List[ComplianceViolation]
    warnings: List[str]
    missing_logs: List[str]
    trust_score_analysis: Dict[str, Any]
    subsystem_health: Dict[str, str]
    repeat_offenders: List[Tuple[str, int]]  # (module, violation_count)


class ΛAuditor:
    """
    ΛAUDITOR – Symbolic Compliance and Integrity Auditor

    Performs full compliance verification across LUKHAS symbolic systems with:
    - Multi-log parsing and event correlation
    - ΛGOVERNOR decision validation
    - GLYPH alignment integrity checks
    - Drift containment effectiveness analysis
    - Trust score impact assessment
    - Violation classification and reporting
    """

    def __init__(self,
                 log_directory: str = "/Users/agi_dev/Downloads/Consolidation-Repo/logs",
                 ethics_directory: str = "/Users/agi_dev/Downloads/Consolidation-Repo/ethics"):
        """
        Initialize ΛAUDITOR with log and ethics directory paths.

        Args:
            log_directory: Path to directory containing audit logs
            ethics_directory: Path to ethics module directory
        """
        self.log_directory = Path(log_directory)
        self.ethics_directory = Path(ethics_directory)
        self.logger = logging.getLogger("ΛAUDITOR")

        # Expected log file patterns
        self.log_patterns = {
            'ethical_alerts': '*ethical_alerts*.jsonl',
            'ethical_governor': '*ethical_governor*.jsonl',
            'conflict_resolution': '*conflict_resolution*.jsonl',
            'symbolic_drift': '*symbolic_drift*.jsonl',
            'governance_audit': '*governance_audit*.log',
            'fold_integrity': 'fold/*fold_integrity*.jsonl',
            'tier_access': 'fold/*tier_access*.jsonl'
        }

        # Risk model thresholds (loaded from governance engine)
        self.risk_thresholds = {
            'drift_entropy': 0.7,
            'emotion_intensity': 0.8,
            'trust_score_min': 0.6,
            'glyph_harmony_min': 0.5,
            'intervention_timeout': 300  # seconds
        }

        # Violation counters for repeat offender tracking
        self.violation_counts = {}

        self.logger.info("ΛAUDITOR initialized for symbolic compliance verification")

    def load_lambda_logs(self, log_dir: Optional[str] = None) -> List[AuditEvent]:
        """
        Load and parse audit logs from specified directory.

        Args:
            log_dir: Optional override for log directory

        Returns:
            List of structured AuditEvent objects
        """
        if log_dir:
            log_path = Path(log_dir)
        else:
            log_path = self.log_directory

        events = []
        processed_files = []
        missing_files = []

        self.logger.info(f"Loading ΛLOGS from: {log_path}")

        for log_type, pattern in self.log_patterns.items():
            matching_files = list(log_path.glob(pattern))

            if not matching_files:
                missing_files.append(f"{log_type}: {pattern}")
                continue

            for log_file in matching_files:
                try:
                    file_events = self._parse_log_file(log_file, log_type)
                    events.extend(file_events)
                    processed_files.append(str(log_file))

                except Exception as e:
                    self.logger.error(f"Failed to parse {log_file}: {e}")

        # Store missing files for reporting
        self.missing_log_files = missing_files

        self.logger.info(f"Processed {len(processed_files)} files, extracted {len(events)} events")

        if missing_files:
            self.logger.warning(f"Missing {len(missing_files)} expected log file patterns")

        return events

    def _parse_log_file(self, log_file: Path, log_type: str) -> List[AuditEvent]:
        """Parse individual log file based on type."""
        events = []

        if log_file.suffix == '.jsonl':
            # Parse JSONL format
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            event_data = json.loads(line.strip())
                            event = AuditEvent(
                                timestamp=event_data.get('timestamp', ''),
                                event_type=log_type,
                                source_module=event_data.get('module', 'unknown'),
                                event_data=event_data,
                                log_file=str(log_file)
                            )
                            events.append(event)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON decode error in {log_file}:{line_num}: {e}")

        elif log_file.suffix == '.log':
            # Parse governance audit log format
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            event_data = json.loads(line.strip())
                            event = AuditEvent(
                                timestamp=event_data.get('timestamp', ''),
                                event_type='governance_decision',
                                source_module=event_data.get('data', {}).get('module', 'governance'),
                                event_data=event_data.get('data', {}),
                                log_file=str(log_file)
                            )
                            events.append(event)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Log parse error in {log_file}:{line_num}: {e}")

        return events

    def check_drift_compliance(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """
        Check drift handling compliance vs policy thresholds.

        Returns:
            Tuple of (passed_checks, violations)
        """
        passed = []
        violations = []

        drift_events = [e for e in events if 'drift' in e.event_type.lower()]

        if not drift_events:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.DRIFT_CONTAINMENT_FAILURE,
                timestamp=datetime.now().isoformat(),
                source_file="SYSTEM",
                event_id=None,
                description="No drift monitoring events found in audit period",
                severity="HIGH",
                suggested_fix="Verify drift monitoring systems are active and logging properly"
            ))
            return passed, violations

        # Check each drift event for threshold compliance
        for event in drift_events:
            entropy_level = event.event_data.get('entropy_level', 0)
            containment_action = event.event_data.get('containment_action')
            response_time = event.event_data.get('response_time_ms', 0)

            # Check entropy threshold compliance
            if entropy_level > self.risk_thresholds['drift_entropy']:
                if not containment_action:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.DRIFT_CONTAINMENT_FAILURE,
                        timestamp=event.timestamp,
                        source_file=event.log_file or "unknown",
                        event_id=event.event_data.get('event_id'),
                        description=f"High entropy drift ({entropy_level}) without containment action",
                        severity="CRITICAL",
                        suggested_fix="Implement automatic drift containment for entropy > threshold"
                    ))
                else:
                    passed.append(f"Drift containment triggered for entropy {entropy_level}")

            # Check response time compliance
            if response_time > self.risk_thresholds['intervention_timeout']:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.DRIFT_CONTAINMENT_FAILURE,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('event_id'),
                    description=f"Drift response timeout: {response_time}ms > {self.risk_thresholds['intervention_timeout']}ms",
                    severity="MEDIUM",
                    suggested_fix="Optimize drift detection response time or increase timeout threshold"
                ))

        if not violations:
            passed.append(f"All {len(drift_events)} drift events handled within policy thresholds")

        return passed, violations

    def check_quarantine_compliance(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """Check quarantine event legality and redundancy."""
        passed = []
        violations = []

        quarantine_events = [e for e in events if 'quarantine' in e.event_data.get('action_type', '').lower()]

        if not quarantine_events:
            passed.append("No quarantine events requiring compliance verification")
            return passed, violations

        # Track quarantine patterns for redundancy detection
        quarantine_targets = {}

        for event in quarantine_events:
            target = event.event_data.get('target_module', 'unknown')
            justification = event.event_data.get('justification')
            authority_level = event.event_data.get('authority_level', 0)

            # Track quarantine frequency per target
            if target not in quarantine_targets:
                quarantine_targets[target] = []
            quarantine_targets[target].append(event)

            # Check justification requirement
            if not justification:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.UNJUSTIFIED_ESCALATION,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('event_id'),
                    description=f"Quarantine action on {target} without justification",
                    severity="HIGH",
                    suggested_fix="Add mandatory justification field for all quarantine actions"
                ))

            # Check authority level for quarantine actions
            if authority_level < 3:  # Assuming level 3+ required for quarantine
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.UNJUSTIFIED_ESCALATION,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('event_id'),
                    description=f"Insufficient authority level {authority_level} for quarantine action",
                    severity="MEDIUM",
                    suggested_fix="Raise minimum authority level requirement for quarantine actions"
                ))

        # Check for redundant quarantine actions (same target, short time window)
        for target, target_events in quarantine_targets.items():
            if len(target_events) > 1:
                # Sort by timestamp and check for rapid succession
                target_events.sort(key=lambda e: e.timestamp)
                for i in range(1, len(target_events)):
                    prev_event = target_events[i-1]
                    curr_event = target_events[i]

                    # Parse timestamps for comparison (simplified)
                    if self._timestamp_diff_seconds(prev_event.timestamp, curr_event.timestamp) < 300:  # 5 minutes
                        violations.append(ComplianceViolation(
                            violation_type=ViolationType.CONFLICT_RECURSION_LOOP,
                            timestamp=curr_event.timestamp,
                            source_file=curr_event.log_file or "unknown",
                            event_id=curr_event.event_data.get('event_id'),
                            description=f"Redundant quarantine action on {target} within 5 minutes",
                            severity="MEDIUM",
                            suggested_fix="Implement quarantine action deduplication logic"
                        ))

        if not violations:
            passed.append(f"All {len(quarantine_events)} quarantine events comply with policy requirements")

        return passed, violations

    def check_governor_compliance(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """Check ΛGOVERNOR decision alignment with risk model."""
        passed = []
        violations = []

        governor_events = [e for e in events if e.event_type == 'governance_decision']

        if not governor_events:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                timestamp=datetime.now().isoformat(),
                source_file="SYSTEM",
                event_id=None,
                description="No ΛGOVERNOR decisions found during audit period",
                severity="HIGH",
                suggested_fix="Verify ΛGOVERNOR is active and making decisions"
            ))
            return passed, violations

        # Analyze governor decisions for alignment
        for event in governor_events:
            decision = event.event_data.get('final_decision')
            ethical_score = event.event_data.get('ethics_evaluation', {}).get('overall_score', 0.0)
            risk_level = event.event_data.get('ethics_evaluation', {}).get('risk_level', 'unknown')

            # Check alignment between ethical score and decision
            if decision == 'APPROVED' and ethical_score < self.risk_thresholds['trust_score_min']:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('action_id'),
                    description=f"Action approved despite low ethical score: {ethical_score}",
                    severity="CRITICAL",
                    suggested_fix="Review ethical score thresholds and approval logic"
                ))

            # Check for missing risk assessment
            if risk_level == 'unknown' and decision != 'ERROR':
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('action_id'),
                    description="Governor decision made without risk level assessment",
                    severity="MEDIUM",
                    suggested_fix="Ensure all decisions include risk level evaluation"
                ))

        if not violations:
            passed.append(f"All {len(governor_events)} ΛGOVERNOR decisions align with risk model")

        return passed, violations

    def check_emotion_intervention_compliance(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """Check emotion intervention legality and GLYPH state."""
        passed = []
        violations = []

        emotion_events = [e for e in events if 'emotion' in e.event_type.lower() or
                         'emotion' in e.event_data.get('intervention_type', '').lower()]

        if not emotion_events:
            passed.append("No emotion interventions requiring compliance verification")
            return passed, violations

        for event in emotion_events:
            intervention_intensity = event.event_data.get('intensity', 0.0)
            glyph_state = event.glyph_state or {}
            justification = event.event_data.get('justification')

            # Check intervention intensity limits
            if intervention_intensity > self.risk_thresholds['emotion_intensity']:
                if not justification:
                    violations.append(ComplianceViolation(
                        violation_type=ViolationType.UNJUSTIFIED_ESCALATION,
                        timestamp=event.timestamp,
                        source_file=event.log_file or "unknown",
                        event_id=event.event_data.get('event_id'),
                        description=f"High-intensity emotion intervention ({intervention_intensity}) without justification",
                        severity="HIGH",
                        suggested_fix="Require justification for high-intensity emotion interventions"
                    ))

            # Check GLYPH harmony compliance
            glyph_harmony = glyph_state.get('harmony_score', 1.0)
            if glyph_harmony < self.risk_thresholds['glyph_harmony_min']:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.NON_HARMONIC_GLYPH_REINSERTION,
                    timestamp=event.timestamp,
                    source_file=event.log_file or "unknown",
                    event_id=event.event_data.get('event_id'),
                    description=f"GLYPH harmony below threshold: {glyph_harmony}",
                    severity="MEDIUM",
                    suggested_fix="Implement GLYPH harmony restoration before intervention completion"
                ))

        if not violations:
            passed.append(f"All {len(emotion_events)} emotion interventions comply with GLYPH harmony requirements")

        return passed, violations

    def check_cascade_termination_compliance(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """Check cascade chain termination includes REPAIR or RESOLVE."""
        passed = []
        violations = []

        cascade_events = [e for e in events if 'cascade' in e.event_type.lower() or
                         'cascade' in str(e.event_data).lower()]

        if not cascade_events:
            passed.append("No cascade chains requiring termination verification")
            return passed, violations

        # Group cascade events by chain ID
        cascade_chains = {}
        for event in cascade_events:
            chain_id = event.event_data.get('cascade_chain_id', event.event_data.get('chain_id', 'unknown'))
            if chain_id not in cascade_chains:
                cascade_chains[chain_id] = []
            cascade_chains[chain_id].append(event)

        # Check each chain for proper termination
        for chain_id, chain_events in cascade_chains.items():
            if len(chain_events) < 2:
                continue  # Single event chains don't need termination check

            # Sort by timestamp to find termination event
            chain_events.sort(key=lambda e: e.timestamp)
            last_event = chain_events[-1]

            termination_action = last_event.event_data.get('action_type', '').upper()
            if termination_action not in ['REPAIR', 'RESOLVE', 'TERMINATE', 'COMPLETE']:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.CONFLICT_RECURSION_LOOP,
                    timestamp=last_event.timestamp,
                    source_file=last_event.log_file or "unknown",
                    event_id=last_event.event_data.get('event_id'),
                    description=f"Cascade chain {chain_id} lacks proper termination (REPAIR/RESOLVE)",
                    severity="HIGH",
                    suggested_fix="Ensure all cascade chains end with REPAIR or RESOLVE action"
                ))
            else:
                passed.append(f"Cascade chain {chain_id} properly terminated with {termination_action}")

        return passed, violations

    def crosscheck_risk_model(self, events: List[AuditEvent]) -> Tuple[List[str], List[ComplianceViolation]]:
        """Compare ethics/governance_engine.py thresholds vs actual event triggers."""
        passed = []
        violations = []

        # Load governance engine configuration for threshold comparison
        try:
            governance_file = self.ethics_directory / "governance_engine.py"
            if governance_file.exists():
                with open(governance_file, 'r') as f:
                    governance_content = f.read()

                # Extract threshold values from governance engine (simplified regex extraction)
                thresholds_found = {}

                # Look for common threshold patterns
                threshold_patterns = {
                    'min_ethical_score': r'min_ethical_score["\s]*[:=]["\s]*([0-9.]+)',
                    'high_risk_threshold': r'high_risk["\s]*[:=]["\s]*([0-9.]+)',
                    'ethical_approval': r'require_ethical_approval["\s]*[:=]["\s]*(True|False)'
                }

                for name, pattern in threshold_patterns.items():
                    match = re.search(pattern, governance_content, re.IGNORECASE)
                    if match:
                        thresholds_found[name] = match.group(1)

                # Compare found thresholds with actual event triggers
                config_min_score = float(thresholds_found.get('min_ethical_score', 0.6))

                # Check if any approved actions had scores below config threshold
                governor_events = [e for e in events if e.event_type == 'governance_decision']
                for event in governor_events:
                    if event.event_data.get('final_decision') == 'APPROVED':
                        actual_score = event.event_data.get('ethics_evaluation', {}).get('overall_score', 1.0)
                        if actual_score < config_min_score:
                            violations.append(ComplianceViolation(
                                violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                                timestamp=event.timestamp,
                                source_file=str(governance_file),
                                event_id=event.event_data.get('action_id'),
                                description=f"Approved action with score {actual_score} below config threshold {config_min_score}",
                                severity="HIGH",
                                suggested_fix="Align approval logic with configured ethical score thresholds"
                            ))

                if not violations:
                    passed.append(f"Risk model thresholds align with {len(governor_events)} governance decisions")

            else:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                    timestamp=datetime.now().isoformat(),
                    source_file=str(governance_file),
                    event_id=None,
                    description="Governance engine configuration file not found for threshold verification",
                    severity="MEDIUM",
                    suggested_fix="Ensure governance_engine.py exists and is accessible for threshold validation"
                ))

        except Exception as e:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.MISSING_GOVERNOR_OVERSIGHT,
                timestamp=datetime.now().isoformat(),
                source_file="risk_model_crosscheck",
                event_id=None,
                description=f"Failed to crosscheck risk model: {str(e)}",
                severity="MEDIUM",
                suggested_fix="Review governance engine file accessibility and format"
            ))

        return passed, violations

    def analyze_trust_score_deltas(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze trust score changes across interventions."""
        trust_analysis = {
            'total_interventions_with_scores': 0,
            'positive_delta_count': 0,
            'negative_delta_count': 0,
            'neutral_delta_count': 0,
            'average_delta': 0.0,
            'largest_positive_delta': 0.0,
            'largest_negative_delta': 0.0,
            'trust_score_timeline': []
        }

        scored_events = [e for e in events if e.trust_score_delta is not None]
        trust_analysis['total_interventions_with_scores'] = len(scored_events)

        if not scored_events:
            return trust_analysis

        deltas = [e.trust_score_delta for e in scored_events]

        trust_analysis['positive_delta_count'] = sum(1 for d in deltas if d > 0)
        trust_analysis['negative_delta_count'] = sum(1 for d in deltas if d < 0)
        trust_analysis['neutral_delta_count'] = sum(1 for d in deltas if d == 0)
        trust_analysis['average_delta'] = sum(deltas) / len(deltas)
        trust_analysis['largest_positive_delta'] = max(deltas) if deltas else 0.0
        trust_analysis['largest_negative_delta'] = min(deltas) if deltas else 0.0

        # Create timeline of trust score changes
        for event in sorted(scored_events, key=lambda e: e.timestamp):
            trust_analysis['trust_score_timeline'].append({
                'timestamp': event.timestamp,
                'module': event.source_module,
                'delta': event.trust_score_delta,
                'intervention_type': event.intervention_type or 'unknown'
            })

        return trust_analysis

    def identify_repeat_offenders(self, violations: List[ComplianceViolation]) -> List[Tuple[str, int]]:
        """Identify modules with highest violation counts."""
        violation_counts = {}

        for violation in violations:
            # Extract module name from source file
            module = self._extract_module_name(violation.source_file)
            violation_counts[module] = violation_counts.get(module, 0) + 1

        # Sort by violation count descending
        repeat_offenders = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)

        return repeat_offenders[:10]  # Top 10 repeat offenders

    def generate_audit_report(self, audit_result: AuditResult, output_format: str = "markdown") -> str:
        """
        Generate comprehensive audit report in specified format.

        Args:
            audit_result: Complete audit results
            output_format: "markdown" or "json"

        Returns:
            Formatted audit report string
        """
        if output_format.lower() == "json":
            return self._generate_json_report(audit_result)
        else:
            return self._generate_markdown_report(audit_result)

    def _generate_markdown_report(self, result: AuditResult) -> str:
        """Generate markdown-formatted audit report."""
        report = f"""# ΛAUDITOR Compliance Verification Report

**Generated:** {result.audit_timestamp}
**Events Processed:** {result.total_events_processed}
**Audit Scope:** LUKHAS Symbolic Systems Full Compliance

---

## 📊 Executive Summary

| Metric | Value |
|--------|--------|
| ✅ Passed Checks | {len(result.passed_checks)} |
| ❌ Violations Found | {len(result.violations)} |
| ⚠️ Warnings | {len(result.warnings)} |
| 🔍 Missing Logs | {len(result.missing_logs)} |

### Trust Score Impact Analysis
- **Average Delta:** {result.trust_score_analysis.get('average_delta', 0.0):.4f}
- **Positive Interventions:** {result.trust_score_analysis.get('positive_delta_count', 0)}
- **Negative Interventions:** {result.trust_score_analysis.get('negative_delta_count', 0)}

---

## ✅ Compliance Checks Passed

"""

        for check in result.passed_checks:
            report += f"- {check}\n"

        if not result.passed_checks:
            report += "- No checks passed ⚠️\n"

        report += f"""
---

## ❌ Compliance Violations

**Total Violations:** {len(result.violations)}

"""

        # Group violations by type
        violations_by_type = {}
        for violation in result.violations:
            v_type = violation.violation_type.value
            if v_type not in violations_by_type:
                violations_by_type[v_type] = []
            violations_by_type[v_type].append(violation)

        for v_type, v_list in violations_by_type.items():
            report += f"### {v_type} ({len(v_list)} violations)\n\n"

            for violation in v_list:
                severity_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(violation.severity, "⚪")
                report += f"""**{severity_emoji} {violation.severity}** | {violation.timestamp}
**Source:** `{violation.source_file}`
**Description:** {violation.description}
**Suggested Fix:** {violation.suggested_fix}

"""

        report += f"""---

## 🔄 Repeat Offenders Analysis

**Top Modules by Violation Count:**

"""

        for module, count in result.repeat_offenders[:5]:
            report += f"1. **{module}**: {count} violations\n"

        if not result.repeat_offenders:
            report += "No repeat offenders identified ✅\n"

        report += f"""
---

## 🏥 Subsystem Health Status

"""

        for subsystem, status in result.subsystem_health.items():
            status_emoji = {"HEALTHY": "✅", "WARNING": "⚠️", "CRITICAL": "❌", "UNKNOWN": "❓"}.get(status, "❓")
            report += f"- **{subsystem}**: {status_emoji} {status}\n"

        if result.warnings:
            report += f"""
---

## ⚠️ Warnings and Recommendations

"""
            for warning in result.warnings:
                report += f"- {warning}\n"

        if result.missing_logs:
            report += f"""
---

## 🔍 Missing Log Files

The following expected log patterns were not found:

"""
            for missing in result.missing_logs:
                report += f"- {missing}\n"

        report += f"""
---

## 🛠 Suggested Actions

1. **High Priority**: Address all CRITICAL and HIGH severity violations
2. **Monitoring**: Review missing log files and restore logging where needed
3. **Process Improvement**: Focus remediation efforts on repeat offender modules
4. **Governance**: Review risk model thresholds for alignment with actual events

---

## 📈 Trust Score Timeline Analysis

Recent trust score impacts from interventions:

"""

        timeline = result.trust_score_analysis.get('trust_score_timeline', [])
        for entry in timeline[-10:]:  # Show last 10 entries
            delta_sign = "+" if entry['delta'] >= 0 else ""
            report += f"- `{entry['timestamp'][:19]}` | **{entry['module']}** | `{delta_sign}{entry['delta']:.4f}` | {entry['intervention_type']}\n"

        report += f"""
---

*Report generated by ΛAUDITOR v1.0 - Symbolic Compliance and Integrity Auditor*
*LUKHAS AGI System - Ethics Compliance Framework*
"""

        return report

    def _generate_json_report(self, result: AuditResult) -> str:
        """Generate JSON-formatted audit report."""

        report_data = {
            "audit_metadata": {
                "generated_timestamp": result.audit_timestamp,
                "total_events_processed": result.total_events_processed,
                "auditor_version": "1.0",
                "system": "LUKHAS AGI",
                "scope": "Full Symbolic Systems Compliance"
            },
            "summary": {
                "passed_checks": len(result.passed_checks),
                "violations_found": len(result.violations),
                "warnings": len(result.warnings),
                "missing_logs": len(result.missing_logs)
            },
            "passed_checks": result.passed_checks,
            "violations": [
                {
                    "violation_type": v.violation_type.value,
                    "timestamp": v.timestamp,
                    "source_file": v.source_file,
                    "event_id": v.event_id,
                    "description": v.description,
                    "severity": v.severity,
                    "suggested_fix": v.suggested_fix,
                    "trust_score_impact": v.trust_score_impact,
                    "related_events": v.related_events
                } for v in result.violations
            ],
            "warnings": result.warnings,
            "missing_logs": result.missing_logs,
            "trust_score_analysis": result.trust_score_analysis,
            "subsystem_health": result.subsystem_health,
            "repeat_offenders": [
                {"module": module, "violation_count": count}
                for module, count in result.repeat_offenders
            ]
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def run_full_audit(self) -> AuditResult:
        """
        Execute complete ΛAUDITOR compliance verification.

        Returns:
            Comprehensive AuditResult with all compliance checks
        """
        audit_start = datetime.now()
        self.logger.info("🔍 Starting ΛAUDITOR full compliance verification")

        # Load all audit logs
        events = self.load_lambda_logs()

        # Run all compliance checks
        all_passed = []
        all_violations = []
        warnings = []

        # 1. Drift Handling Compliance
        self.logger.info("Checking drift handling compliance...")
        drift_passed, drift_violations = self.check_drift_compliance(events)
        all_passed.extend(drift_passed)
        all_violations.extend(drift_violations)

        # 2. Quarantine Event Compliance
        self.logger.info("Checking quarantine event compliance...")
        quarantine_passed, quarantine_violations = self.check_quarantine_compliance(events)
        all_passed.extend(quarantine_passed)
        all_violations.extend(quarantine_violations)

        # 3. Governor Decision Compliance
        self.logger.info("Checking ΛGOVERNOR decision compliance...")
        governor_passed, governor_violations = self.check_governor_compliance(events)
        all_passed.extend(governor_passed)
        all_violations.extend(governor_violations)

        # 4. Emotion Intervention Compliance
        self.logger.info("Checking emotion intervention compliance...")
        emotion_passed, emotion_violations = self.check_emotion_intervention_compliance(events)
        all_passed.extend(emotion_passed)
        all_violations.extend(emotion_violations)

        # 5. Cascade Termination Compliance
        self.logger.info("Checking cascade termination compliance...")
        cascade_passed, cascade_violations = self.check_cascade_termination_compliance(events)
        all_passed.extend(cascade_passed)
        all_violations.extend(cascade_violations)

        # 6. Risk Model Crosscheck
        self.logger.info("Performing risk model crosscheck...")
        risk_passed, risk_violations = self.crosscheck_risk_model(events)
        all_passed.extend(risk_passed)
        all_violations.extend(risk_violations)

        # Analyze trust scores and repeat offenders
        trust_analysis = self.analyze_trust_score_deltas(events)
        repeat_offenders = self.identify_repeat_offenders(all_violations)

        # Assess subsystem health
        subsystem_health = self._assess_subsystem_health(events, all_violations)

        # Add warnings for significant issues
        if len(all_violations) > 10:
            warnings.append(f"High violation count detected: {len(all_violations)} violations found")

        if trust_analysis.get('negative_delta_count', 0) > trust_analysis.get('positive_delta_count', 0):
            warnings.append("Negative trust score impacts exceed positive impacts")

        if len(self.missing_log_files) > 3:
            warnings.append(f"Multiple log files missing: {len(self.missing_log_files)} expected patterns not found")

        # Create final audit result
        audit_result = AuditResult(
            audit_timestamp=datetime.now().isoformat(),
            total_events_processed=len(events),
            passed_checks=all_passed,
            violations=all_violations,
            warnings=warnings,
            missing_logs=self.missing_log_files,
            trust_score_analysis=trust_analysis,
            subsystem_health=subsystem_health,
            repeat_offenders=repeat_offenders
        )

        audit_duration = (datetime.now() - audit_start).total_seconds()
        self.logger.info(f"✅ ΛAUDITOR compliance verification completed in {audit_duration:.2f}s")
        self.logger.info(f"📊 Results: {len(all_passed)} passed, {len(all_violations)} violations, {len(warnings)} warnings")

        return audit_result

    def _assess_subsystem_health(self, events: List[AuditEvent], violations: List[ComplianceViolation]) -> Dict[str, str]:
        """Assess health status of each subsystem based on events and violations."""
        subsystems = ['governance', 'drift_monitoring', 'emotion_regulation', 'quarantine_system', 'cascade_resolution']
        health_status = {}

        for subsystem in subsystems:
            subsystem_events = [e for e in events if subsystem.replace('_', '') in e.event_type.lower() or
                               subsystem.replace('_', '') in e.source_module.lower()]
            subsystem_violations = [v for v in violations if subsystem.replace('_', '') in v.source_file.lower()]

            if len(subsystem_violations) == 0 and len(subsystem_events) > 0:
                health_status[subsystem] = "HEALTHY"
            elif len(subsystem_violations) <= 2:
                health_status[subsystem] = "WARNING"
            elif len(subsystem_violations) > 2:
                health_status[subsystem] = "CRITICAL"
            else:
                health_status[subsystem] = "UNKNOWN"

        return health_status

    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path."""
        if not file_path or file_path == "SYSTEM":
            return "SYSTEM"

        path_parts = file_path.replace('\\', '/').split('/')
        if len(path_parts) > 1:
            return path_parts[-2]  # Parent directory name
        else:
            return path_parts[-1].replace('.py', '').replace('.jsonl', '').replace('.log', '')

    def _timestamp_diff_seconds(self, timestamp1: str, timestamp2: str) -> int:
        """Calculate difference between timestamps in seconds (simplified)."""
        try:
            # Simple timestamp comparison - assumes ISO format
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            return abs((dt2 - dt1).total_seconds())
        except:
            return 0  # Return 0 if parsing fails


# CLI interface and main execution
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="ΛAUDITOR - Symbolic Compliance and Integrity Auditor")
    parser.add_argument("--log-dir", type=str, help="Override default log directory")
    parser.add_argument("--ethics-dir", type=str, help="Override default ethics directory")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                       help="Output format for audit report")
    parser.add_argument("--output", type=str, help="Output file path (default: print to stdout)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Initialize ΛAUDITOR
    auditor = ΛAuditor(
        log_directory=args.log_dir or "/Users/agi_dev/Downloads/Consolidation-Repo/logs",
        ethics_directory=args.ethics_dir or "/Users/agi_dev/Downloads/Consolidation-Repo/ethics"
    )

    try:
        # Run full compliance audit
        result = auditor.run_full_audit()

        # Generate report
        report = auditor.generate_audit_report(result, args.format)

        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"✅ Audit report written to: {args.output}")
        else:
            print(report)

        # Exit with appropriate code
        if result.violations:
            sys.exit(1)  # Violations found
        else:
            sys.exit(0)  # Clean audit

    except Exception as e:
        print(f"❌ ΛAUDITOR execution failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)  # System error


## CLAUDE CHANGELOG

- Created comprehensive ΛAUDITOR implementation with full symbolic compliance verification framework # CLAUDE_EDIT_v0.1
- Implemented multi-log parsing system supporting JSONL and governance audit log formats # CLAUDE_EDIT_v0.1
- Added complete violation classification system with 5 violation types and severity levels # CLAUDE_EDIT_v0.1
- Integrated trust score analysis and repeat offender identification for compliance reporting # CLAUDE_EDIT_v0.1
- Created dual-format reporting system (Markdown/JSON) with executive summaries and actionable recommendations # CLAUDE_EDIT_v0.1