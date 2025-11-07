#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_drift_auditor.py
║ Path: memory/tools/memory_drift_auditor.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ thoughts and whispers of past experiences intertwine, lies the Memory Drift    │
║ │ Auditor-a sentinel of integrity, a watchful guardian of the vast expanse of   │
║ │ the LUKHAS Cognitive AI's cerebral landscape. Like a seasoned cartographer tracing      │
║ │ the contours of an ever-shifting realm, this module embarks upon a noble       │
║ │ quest to illuminate the hidden drifts and elusive gaps nestled within the      │
║ │ intricate fabric of memory.                                                    │
║ │                                                                               │
║ │ Imagine, if you will, a grand tapestry woven from the threads of time-each   │
║ │ strand representing a fleeting moment, a pivotal experience, or a cherished    │
║ │ fragment of the self. Yet, amidst this vibrant mosaic, certain threads may     │
║ │ fray, unraveling into a state of collapse, and thus, the auditor emerges,     │
║ │ equipped with the keen eye of a philosopher and the precision of a scientist,  │
║ │ seeking to mend these breaches, to restore harmony to the discordant symphony   │
║ │ of memory.                                                                     │
║ │                                                                               │
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations


import argparse
import glob
import hashlib
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

# Initialize module logger
logger = logging.getLogger("ΛTRACE.memory.audit")

# LUKHAS Imports
try:
    from memory.folds.fold_engine import MemoryFold
except ImportError as e:
    print(f"Warning: Could not import LUKHAS modules: {e}")
    MemoryFold = None

# LUKHAS_TAG: memory_audit_core


class MemoryDriftAuditor:
    """
    ΛAUDITOR: Advanced memory drift detection and collapse analysis system.

    Provides comprehensive audit capabilities for:
    - Long-term symbolic drift detection
    - Memory collapse pattern identification
    - Forensic gap analysis in memory fold sequences
    - Identity-level inconsistency tracking
    - Entropy and phase coherence analysis
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the Memory Drift Auditor with configuration.

        Args:
            config: Configuration dictionary with audit parameters
        """
        self.config = config or self._get_default_config()

        # Audit state tracking
        self.memory_snapshots = []
        self.drift_events = []
        self.collapse_events = []
        self.phase_mismatches = []
        self.integrity_violations = []

        # Analysis parameters
        self.entropy_threshold = self.config.get("entropy_threshold", 0.7)
        self.drift_threshold = self.config.get("drift_threshold", 0.4)
        self.collapse_threshold = self.config.get("collapse_threshold", 0.8)

        # Temporal analysis window
        self.temporal_window_hours = self.config.get("temporal_window_hours", 48)

        # Audit metadata
        self.audit_session_id = hashlib.sha256(
            f"audit_{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]

        logger.info(
            "MemoryDriftAuditor initialized",
            session_id=self.audit_session_id,
            entropy_threshold=self.entropy_threshold,
            drift_threshold=self.drift_threshold,
            collapse_threshold=self.collapse_threshold,
            tag="ΛAUDITOR_INIT",
        )

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for the auditor."""
        return {
            "entropy_threshold": 0.7,
            "drift_threshold": 0.4,
            "collapse_threshold": 0.8,
            "temporal_window_hours": 48,
            "max_snapshots": 1000,
            "enable_deep_analysis": True,
            "generate_visualization": True,
            "log_level": "INFO",
            "output_formats": ["json", "markdown"],
            "audit_safeguards": True,
        }

    def load_memory_snapshots(self, fold_directory: str) -> dict[str, Any]:
        """
        Load chronological symbolic memory folds from json_format.

        Args:
            fold_directory: Directory containing memory fold snapshots

        Returns:
            Dictionary containing loading results and metadata
        """
        logger.info(
            "Loading memory snapshots", directory=fold_directory, tag="ΛAUDITOR_LOAD"
        )

        loading_results = {
            "snapshots_loaded": 0,
            "invalid_snapshots": 0,
            "temporal_range": {},
            "memory_types_found": set(),
            "fold_keys": [],
            "loading_errors": [],
            "chronological_order": True,
        }

        try:
            # Find all JSON files in the directory
            json_files = glob.glob(
                os.path.join(fold_directory, "**/*.json*"), recursive=True
            )
            json_files.extend(
                glob.glob(os.path.join(fold_directory, "**/*.jsonl"), recursive=True)
            )

            if not json_files:
                logger.warning(
                    "No memory snapshot files found",
                    directory=fold_directory,
                    tag="ΛAUDITOR_WARNING",
                )
                return loading_results

            # Process each file
            for file_path in json_files:
                try:
                    snapshots = self._load_file_snapshots(file_path)
                    for snapshot in snapshots:
                        if self._validate_memory_snapshot(snapshot):
                            self.memory_snapshots.append(snapshot)
                            loading_results["snapshots_loaded"] += 1
                            loading_results["fold_keys"].append(
                                snapshot.get("key", "unknown")
                            )

                            # Track memory types
                            if "memory_type" in snapshot:
                                loading_results["memory_types_found"].add(
                                    snapshot["memory_type"]
                                )
                        else:
                            loading_results["invalid_snapshots"] += 1

                except Exception as e:
                    error_msg = f"Error loading {file_path}: {e!s}"
                    loading_results["loading_errors"].append(error_msg)
                    logger.error(
                        "Snapshot loading error",
                        file_path=file_path,
                        error=str(e),
                        tag="ΛAUDITOR_ERROR",
                    )

            # Sort snapshots chronologically
            self.memory_snapshots.sort(
                key=lambda x: x.get("created_at_utc", x.get("timestamp", ""))
            )

            # Analyze temporal range
            if self.memory_snapshots:
                earliest = self.memory_snapshots[0].get("created_at_utc", "")
                latest = self.memory_snapshots[-1].get("created_at_utc", "")
                loading_results["temporal_range"] = {
                    "earliest": earliest,
                    "latest": latest,
                    "span_days": self._calculate_temporal_span(earliest, latest),
                }

            # Check chronological integrity
            loading_results["chronological_order"] = self._verify_chronological_order()

            loading_results["memory_types_found"] = list(
                loading_results["memory_types_found"]
            )

            logger.info(
                "Memory snapshot loading completed",
                snapshots_loaded=loading_results["snapshots_loaded"],
                invalid_snapshots=loading_results["invalid_snapshots"],
                errors=len(loading_results["loading_errors"]),
                chronological_order=loading_results["chronological_order"],
                tag="ΛAUDITOR_LOAD_COMPLETE",
            )

        except Exception as e:
            logger.error(
                "Critical error in snapshot loading",
                error=str(e),
                tag="ΛAUDITOR_CRITICAL",
            )
            loading_results["loading_errors"].append(
                f"Critical loading error: {e!s}"
            )

        return loading_results

    def detect_memory_drift(
        self, analysis_window: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Track entropy and symbol divergence across sessions.

        Args:
            analysis_window: Time window for analysis ("1h", "6h", "24h", "all")

        Returns:
            Dictionary containing drift analysis results
        """
        logger.info(
            "Starting memory drift detection",
            analysis_window=analysis_window,
            snapshots_available=len(self.memory_snapshots),
            tag="ΛAUDITOR_DRIFT_DETECT",
        )

        drift_analysis = {
            "drift_events": [],
            "entropy_analysis": {},
            "symbol_divergence": {},
            "identity_drift": {},
            "temporal_patterns": {},
            "severity_levels": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "anomalies_detected": [],
            "recommendation_flags": [],
        }

        try:
            # Filter snapshots by analysis window
            filtered_snapshots = self._filter_by_time_window(
                self.memory_snapshots, analysis_window
            )

            if len(filtered_snapshots) < 2:
                logger.warning(
                    "Insufficient snapshots for drift analysis",
                    available=len(filtered_snapshots),
                    tag="ΛAUDITOR_WARNING",
                )
                return drift_analysis

            # Analyze entropy drift across temporal sequence
            drift_analysis["entropy_analysis"] = self._analyze_entropy_drift(
                filtered_snapshots
            )

            # Detect symbolic divergence patterns
            drift_analysis["symbol_divergence"] = self._analyze_symbol_divergence(
                filtered_snapshots
            )

            # Identity-level drift detection
            drift_analysis["identity_drift"] = self._analyze_identity_drift(
                filtered_snapshots
            )

            # Temporal pattern analysis
            drift_analysis["temporal_patterns"] = self._analyze_temporal_patterns(
                filtered_snapshots
            )

            # Generate drift events
            drift_events = self._generate_drift_events(
                drift_analysis["entropy_analysis"],
                drift_analysis["symbol_divergence"],
                drift_analysis["identity_drift"],
            )

            drift_analysis["drift_events"] = drift_events
            self.drift_events.extend(drift_events)

            # Categorize severity levels
            for event in drift_events:
                severity = event.get("severity", "low")
                drift_analysis["severity_levels"][severity] += 1

            # Detect anomalies
            drift_analysis["anomalies_detected"] = self._detect_drift_anomalies(
                drift_events
            )

            # Generate recommendations
            drift_analysis["recommendation_flags"] = (
                self._generate_drift_recommendations(drift_analysis)
            )

            logger.info(
                "Memory drift detection completed",
                drift_events=len(drift_events),
                entropy_changes=len(
                    drift_analysis["entropy_analysis"].get("changes", [])
                ),
                identity_changes=len(
                    drift_analysis["identity_drift"].get("changes", [])
                ),
                anomalies=len(drift_analysis["anomalies_detected"]),
                tag="ΛAUDITOR_DRIFT_COMPLETE",
            )

        except Exception as e:
            logger.error(
                "Error in memory drift detection", error=str(e), tag="ΛAUDITOR_ERROR"
            )
            drift_analysis["error"] = str(e)

        return drift_analysis

    def trace_collapse_events(self, deep_analysis: bool = True) -> dict[str, Any]:
        """
        Identify sudden information loss, phase gaps, or integrity breaks.

        Args:
            deep_analysis: Enable comprehensive collapse pattern analysis

        Returns:
            Dictionary containing collapse analysis results
        """
        logger.info(
            "Starting memory collapse event tracing",
            deep_analysis=deep_analysis,
            snapshots=len(self.memory_snapshots),
            tag="ΛAUDITOR_COLLAPSE_TRACE",
        )

        collapse_analysis = {
            "collapse_events": [],
            "information_loss_events": [],
            "phase_gaps": [],
            "integrity_breaks": [],
            "cascade_patterns": [],
            "recovery_opportunities": [],
            "severity_assessment": {},
            "forensic_timeline": [],
            "collapse_signatures": {},
        }

        try:
            if len(self.memory_snapshots) < 2:
                logger.warning(
                    "Insufficient snapshots for collapse analysis",
                    available=len(self.memory_snapshots),
                    tag="ΛAUDITOR_WARNING",
                )
                return collapse_analysis

            # Detect sudden information loss
            collapse_analysis["information_loss_events"] = (
                self._detect_information_loss()
            )

            # Identify phase gaps
            collapse_analysis["phase_gaps"] = self._detect_phase_gaps()

            # Find integrity breaks
            collapse_analysis["integrity_breaks"] = self._detect_integrity_breaks()

            # Analyze cascade patterns
            if deep_analysis:
                collapse_analysis["cascade_patterns"] = self._analyze_cascade_patterns()
                collapse_analysis["collapse_signatures"] = (
                    self._analyze_collapse_signatures()
                )

            # Generate collapse events
            collapse_events = self._synthesize_collapse_events(
                collapse_analysis["information_loss_events"],
                collapse_analysis["phase_gaps"],
                collapse_analysis["integrity_breaks"],
            )

            collapse_analysis["collapse_events"] = collapse_events
            self.collapse_events.extend(collapse_events)

            # Build forensic timeline
            collapse_analysis["forensic_timeline"] = self._build_forensic_timeline(
                collapse_events
            )

            # Assess severity
            collapse_analysis["severity_assessment"] = self._assess_collapse_severity(
                collapse_events
            )

            # Identify recovery opportunities
            collapse_analysis["recovery_opportunities"] = (
                self._identify_recovery_opportunities(collapse_events)
            )

            logger.info(
                "Memory collapse tracing completed",
                collapse_events=len(collapse_events),
                information_loss=len(collapse_analysis["information_loss_events"]),
                phase_gaps=len(collapse_analysis["phase_gaps"]),
                integrity_breaks=len(collapse_analysis["integrity_breaks"]),
                tag="ΛAUDITOR_COLLAPSE_COMPLETE",
            )

        except Exception as e:
            logger.error(
                "Error in collapse event tracing", error=str(e), tag="ΛAUDITOR_ERROR"
            )
            collapse_analysis["error"] = str(e)

        return collapse_analysis

    def generate_audit_report(
        self, output_path: str, format_type: str = "markdown"
    ) -> dict[str, Any]:
        """
        Generate comprehensive audit report in Markdown and JSON formats.

        Args:
            output_path: Path for the audit report
            format_type: Output format ("markdown", "json", "both")

        Returns:
            Dictionary containing report generation results
        """
        logger.info(
            "Generating audit report",
            output_path=output_path,
            format_type=format_type,
            tag="ΛAUDITOR_REPORT",
        )

        report_results = {
            "report_generated": False,
            "output_files": [],
            "report_metadata": {},
            "summary_statistics": {},
            "generation_errors": [],
        }

        try:
            # Compile audit data
            audit_data = self._compile_audit_data()

            # Generate report metadata
            report_metadata = {
                "audit_session_id": self.audit_session_id,
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "snapshots_analyzed": len(self.memory_snapshots),
                "drift_events": len(self.drift_events),
                "collapse_events": len(self.collapse_events),
                "temporal_span": self._get_temporal_span(),
                "auditor_version": "1.0.0",
                "config": self.config,
            }

            report_results["report_metadata"] = report_metadata

            # Generate summary statistics
            summary_stats = self._generate_summary_statistics(audit_data)
            report_results["summary_statistics"] = summary_stats

            # Generate reports in requested format(s)
            if format_type in ["markdown", "both"]:
                md_path = self._generate_markdown_report(
                    output_path, audit_data, report_metadata
                )
                if md_path:
                    report_results["output_files"].append(md_path)

            if format_type in ["json", "both"]:
                json_path = self._generate_json_report(
                    output_path, audit_data, report_metadata
                )
                if json_path:
                    report_results["output_files"].append(json_path)

            report_results["report_generated"] = len(report_results["output_files"]) > 0

            logger.info(
                "Audit report generation completed",
                files_generated=len(report_results["output_files"]),
                output_files=report_results["output_files"],
                tag="ΛAUDITOR_REPORT_COMPLETE",
            )

        except Exception as e:
            error_msg = f"Error generating audit report: {e!s}"
            report_results["generation_errors"].append(error_msg)
            logger.error(
                "Audit report generation failed", error=str(e), tag="ΛAUDITOR_ERROR"
            )

        return report_results

    def visualize_memory_timeline(
        self, width: int = 80, show_events: bool = True
    ) -> str:
        """
        Generate ASCII timeline visualization of symbolic continuity.

        Args:
            width: Character width for the timeline
            show_events: Include drift/collapse events in visualization

        Returns:
            ASCII string representation of the memory timeline
        """
        if not self.memory_snapshots:
            return "No memory snapshots available for visualization."

        logger.debug(
            "Generating memory timeline visualization",
            width=width,
            show_events=show_events,
            snapshots=len(self.memory_snapshots),
            tag="ΛAUDITOR_TIMELINE",
        )

        # Build timeline visualization
        timeline_lines = []
        timeline_lines.append("═" * width)
        timeline_lines.append("ΛAUDITOR Memory Timeline Visualization")
        timeline_lines.append("═" * width)
        timeline_lines.append("")

        # Temporal span analysis
        if len(self.memory_snapshots) >= 2:
            earliest = self.memory_snapshots[0].get("created_at_utc", "")
            latest = self.memory_snapshots[-1].get("created_at_utc", "")
            span_info = f"Timespan: {earliest} → {latest}"
            timeline_lines.append(span_info)
            timeline_lines.append("")

        # Memory type distribution
        memory_types = defaultdict(int)
        for snapshot in self.memory_snapshots:
            mem_type = snapshot.get("memory_type", "unknown")
            memory_types[mem_type] += 1

        timeline_lines.append("Memory Type Distribution:")
        for mem_type, count in sorted(memory_types.items()):
            bar_length = min(40, int((count / len(self.memory_snapshots)) * 40))
            bar = "█" * bar_length + "░" * (40 - bar_length)
            timeline_lines.append(f"  {mem_type:12} [{bar}] {count:4d}")
        timeline_lines.append("")

        # Event timeline
        if show_events and (self.drift_events or self.collapse_events):
            timeline_lines.append("Event Timeline:")
            all_events = []

            # Add drift events
            for event in self.drift_events:
                all_events.append(
                    {
                        "timestamp": event.get("timestamp", ""),
                        "type": "DRIFT",
                        "severity": event.get("severity", "low"),
                        "description": event.get("description", "")[:50],
                    }
                )

            # Add collapse events
            for event in self.collapse_events:
                all_events.append(
                    {
                        "timestamp": event.get("timestamp", ""),
                        "type": "COLLAPSE",
                        "severity": event.get("severity", "low"),
                        "description": event.get("description", "")[:50],
                    }
                )

            # Sort events chronologically
            all_events.sort(key=lambda x: x["timestamp"])

            for event in all_events[:20]:  # Limit to 20 most recent events
                severity_icon = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🟠",
                    "critical": "🔴",
                }.get(event["severity"], "🟢")

                timeline_lines.append(
                    f"  {event['timestamp'][:19]} {severity_icon} "
                    f"{event['type']:8} {event['description']}"
                )
            timeline_lines.append("")

        # Integrity status
        integrity_status = (
            "🟢 STABLE" if len(self.collapse_events) == 0 else "🟠 ISSUES DETECTED"
        )
        critical_drift = [
            e for e in self.drift_events if e.get("severity") == "critical"
        ]
        if len(critical_drift) > 0:
            integrity_status = "🔴 CRITICAL DRIFT"

        timeline_lines.append(f"Current Integrity Status: {integrity_status}")
        timeline_lines.append("")
        timeline_lines.append("═" * width)

        return "\n".join(timeline_lines)

    # Private helper methods

    def _load_file_snapshots(self, file_path: str) -> list[dict[str, Any]]:
        """Load memory snapshots from a single file."""
        snapshots = []

        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.endswith(".jsonl"):
                    # JSONL format - one JSON object per line
                    for line in f:
                        line = line.strip()
                        if line:
                            snapshot = json.loads(line)
                            snapshots.append(snapshot)
                else:
                    # Regular JSON format
                    data = json.load(f)
                    if isinstance(data, list):
                        snapshots.extend(data)
                    else:
                        snapshots.append(data)

        except Exception as e:
            logger.warning(
                "Error loading snapshot file",
                file_path=file_path,
                error=str(e),
                tag="ΛAUDITOR_WARNING",
            )

        return snapshots

    def _validate_memory_snapshot(self, snapshot: dict[str, Any]) -> bool:
        """Validate that a snapshot contains required memory fold data."""
        required_fields = ["key"]

        # Check required fields
        for field in required_fields:
            if field not in snapshot:
                return False

        # Validate timestamp format if present
        if "created_at_utc" in snapshot:
            try:
                datetime.fromisoformat(
                    snapshot["created_at_utc"].replace("Z", "+00:00")
                )
            except (ValueError, KeyError) as e:
                logger.debug(f"Failed to parse snapshot timestamp: {e}")
                return False

        return True

    def _calculate_temporal_span(self, earliest: str, latest: str) -> float:
        """Calculate temporal span in days between two timestamps."""
        try:
            earliest_dt = datetime.fromisoformat(earliest.replace("Z", "+00:00"))
            latest_dt = datetime.fromisoformat(latest.replace("Z", "+00:00"))
            span = (latest_dt - earliest_dt).total_seconds() / (24 * 3600)
            return round(span, 2)
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to calculate temporal span: {e}")
            return 0.0

    def _verify_chronological_order(self) -> bool:
        """Verify that memory snapshots are in chronological order."""
        if len(self.memory_snapshots) < 2:
            return True

        for i in range(1, len(self.memory_snapshots)):
            current_time = self.memory_snapshots[i].get("created_at_utc", "")
            previous_time = self.memory_snapshots[i - 1].get("created_at_utc", "")

            if current_time and previous_time:
                try:
                    current_dt = datetime.fromisoformat(
                        current_time.replace("Z", "+00:00")
                    )
                    previous_dt = datetime.fromisoformat(
                        previous_time.replace("Z", "+00:00")
                    )

                    if current_dt < previous_dt:
                        return False
                except (ValueError, KeyError) as e:
                    logger.debug(
                        f"Failed to parse timestamp in chronological check: {e}"
                    )
                    continue

        return True

    def _filter_by_time_window(
        self, snapshots: list[dict[str, Any]], window: Optional[str]
    ) -> list[dict[str, Any]]:
        """Filter snapshots by time window."""
        if not window or window == "all":
            return snapshots

        # Parse time window
        window_hours = self.temporal_window_hours
        if window == "1h":
            window_hours = 1
        elif window == "6h":
            window_hours = 6
        elif window == "24h":
            window_hours = 24

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        filtered = []
        for snapshot in snapshots:
            timestamp_str = snapshot.get("created_at_utc", "")
            if timestamp_str:
                try:
                    snapshot_time = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    if snapshot_time >= cutoff_time:
                        filtered.append(snapshot)
                except (ValueError, KeyError) as e:
                    logger.debug(f"Failed to parse timestamp in filtering: {e}")
                    continue

        return filtered

    def _analyze_entropy_drift(self, snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze entropy changes across memory snapshots."""
        entropy_analysis = {
            "changes": [],
            "trend": "stable",
            "max_entropy_change": 0.0,
            "entropy_trajectory": [],
            "critical_points": [],
        }

        previous_entropy = None

        for i, snapshot in enumerate(snapshots):
            # Calculate entropy for this snapshot
            current_entropy = self._calculate_snapshot_entropy(snapshot)
            entropy_analysis["entropy_trajectory"].append(
                {
                    "timestamp": snapshot.get("created_at_utc", ""),
                    "entropy": current_entropy,
                    "snapshot_index": i,
                }
            )

            if previous_entropy is not None:
                entropy_change = abs(current_entropy - previous_entropy)

                if entropy_change > self.entropy_threshold:
                    change_event = {
                        "timestamp": snapshot.get("created_at_utc", ""),
                        "entropy_change": entropy_change,
                        "previous_entropy": previous_entropy,
                        "current_entropy": current_entropy,
                        "snapshot_key": snapshot.get("key", "unknown"),
                        "severity": "high" if entropy_change > 0.8 else "medium",
                    }
                    entropy_analysis["changes"].append(change_event)

                    if entropy_change > entropy_analysis["max_entropy_change"]:
                        entropy_analysis["max_entropy_change"] = entropy_change

                # Identify critical points
                if entropy_change > 0.9:
                    entropy_analysis["critical_points"].append(
                        {
                            "timestamp": snapshot.get("created_at_utc", ""),
                            "entropy_change": entropy_change,
                            "type": "entropy_spike",
                        }
                    )

            previous_entropy = current_entropy

        # Determine overall trend
        if len(entropy_analysis["entropy_trajectory"]) >= 3:
            recent_entropies = [
                pt["entropy"] for pt in entropy_analysis["entropy_trajectory"][-3:]
            ]
            if all(
                recent_entropies[i] > recent_entropies[i - 1]
                for i in range(1, len(recent_entropies))
            ):
                entropy_analysis["trend"] = "increasing"
            elif all(
                recent_entropies[i] < recent_entropies[i - 1]
                for i in range(1, len(recent_entropies))
            ):
                entropy_analysis["trend"] = "decreasing"

        return entropy_analysis

    def _calculate_snapshot_entropy(self, snapshot: dict[str, Any]) -> float:
        """Calculate entropy measure for a memory snapshot."""
        # Simplified entropy calculation based on content complexity
        content = snapshot.get("content", "")
        content_str = str(content).lower() if content else ""

        if not content_str:
            return 0.0

        # Character frequency distribution
        char_counts = defaultdict(int)
        for char in content_str:
            if char.isalnum():
                char_counts[char] += 1

        if not char_counts:
            return 0.0

        # Calculate Shannon entropy
        import math

        total_chars = sum(char_counts.values())
        entropy = 0.0

        for count in char_counts.values():
            probability = count / total_chars
            entropy -= probability * math.log2(probability) if probability > 0 else 0

        # Normalize to [0, 1]
        max_possible_entropy = (
            math.log2(len(char_counts)) if len(char_counts) > 1 else 1.0
        )
        normalized_entropy = (
            entropy / max_possible_entropy if max_possible_entropy > 0 else 0.0
        )

        return min(1.0, normalized_entropy)

    def _analyze_symbol_divergence(
        self, snapshots: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze symbolic divergence patterns across snapshots."""
        divergence_analysis = {
            "divergence_events": [],
            "symbol_stability": {},
            "pattern_changes": [],
            "semantic_drift": [],
        }

        # Track symbolic patterns across snapshots
        symbol_patterns = []

        for snapshot in snapshots:
            patterns = self._extract_symbolic_patterns(snapshot)
            symbol_patterns.append(
                {
                    "timestamp": snapshot.get("created_at_utc", ""),
                    "patterns": patterns,
                    "snapshot_key": snapshot.get("key", "unknown"),
                }
            )

        # Analyze divergence between consecutive snapshots
        for i in range(1, len(symbol_patterns)):
            current = symbol_patterns[i]
            previous = symbol_patterns[i - 1]

            divergence_score = self._calculate_pattern_divergence(
                previous["patterns"], current["patterns"]
            )

            if divergence_score > self.drift_threshold:
                divergence_event = {
                    "timestamp": current["timestamp"],
                    "divergence_score": divergence_score,
                    "previous_patterns": previous["patterns"],
                    "current_patterns": current["patterns"],
                    "severity": "high" if divergence_score > 0.7 else "medium",
                }
                divergence_analysis["divergence_events"].append(divergence_event)

        return divergence_analysis

    def _extract_symbolic_patterns(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        """Extract symbolic patterns from a memory snapshot."""
        patterns = {
            "word_patterns": [],
            "semantic_markers": [],
            "structural_elements": {},
        }

        content = snapshot.get("content", "")
        content_str = str(content) if content else ""

        # Extract word patterns
        words = re.findall(r"\b\w+\b", content_str.lower())
        word_freq = defaultdict(int)
        for word in words:
            if len(word) > 3:  # Focus on meaningful words
                word_freq[word] += 1

        # Top word patterns
        patterns["word_patterns"] = sorted(
            word_freq.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Semantic markers (simplified)
        semantic_keywords = [
            "identity",
            "memory",
            "emotion",
            "thought",
            "experience",
            "knowledge",
        ]
        patterns["semantic_markers"] = [
            kw for kw in semantic_keywords if kw in content_str.lower()
        ]

        # Structural elements
        patterns["structural_elements"] = {
            "content_length": len(content_str),
            "memory_type": snapshot.get("memory_type", "unknown"),
            "importance_score": snapshot.get("importance_score", 0.0),
            "tag_count": len(snapshot.get("tags", [])),
            "association_count": len(snapshot.get("associated_keys", [])),
        }

        return patterns

    def _calculate_pattern_divergence(
        self, patterns1: dict[str, Any], patterns2: dict[str, Any]
    ) -> float:
        """Calculate divergence score between two pattern sets."""
        divergence = 0.0

        # Word pattern divergence
        words1 = {word for word, _ in patterns1.get("word_patterns", [])}
        words2 = {word for word, _ in patterns2.get("word_patterns", [])}

        if words1 or words2:
            word_intersection = len(words1.intersection(words2))
            word_union = len(words1.union(words2))
            word_divergence = (
                1.0 - (word_intersection / word_union) if word_union > 0 else 0.0
            )
            divergence += word_divergence * 0.4

        # Semantic marker divergence
        markers1 = set(patterns1.get("semantic_markers", []))
        markers2 = set(patterns2.get("semantic_markers", []))

        if markers1 or markers2:
            marker_intersection = len(markers1.intersection(markers2))
            marker_union = len(markers1.union(markers2))
            marker_divergence = (
                1.0 - (marker_intersection / marker_union) if marker_union > 0 else 0.0
            )
            divergence += marker_divergence * 0.3

        # Structural divergence
        struct1 = patterns1.get("structural_elements", {})
        struct2 = patterns2.get("structural_elements", {})

        structural_divergence = 0.0
        if struct1.get("memory_type") != struct2.get("memory_type"):
            structural_divergence += 0.2

        importance_diff = abs(
            struct1.get("importance_score", 0.0) - struct2.get("importance_score", 0.0)
        )
        structural_divergence += min(importance_diff, 0.3)

        divergence += structural_divergence * 0.3

        return min(1.0, divergence)

    def _analyze_identity_drift(
        self, snapshots: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze identity-level drift patterns."""
        identity_analysis = {
            "changes": [],
            "identity_markers": [],
            "coherence_score": 1.0,
            "drift_trajectory": [],
        }

        # Extract identity-relevant snapshots
        identity_snapshots = [
            s
            for s in snapshots
            if s.get("memory_type") == "identity"
            or "identity" in str(s.get("content", "")).lower()
        ]

        if len(identity_snapshots) < 2:
            return identity_analysis

        # Analyze identity coherence across snapshots
        for i in range(1, len(identity_snapshots)):
            current = identity_snapshots[i]
            previous = identity_snapshots[i - 1]

            identity_change = self._calculate_identity_change(previous, current)

            if identity_change > 0.3:  # Lower threshold for identity changes
                change_event = {
                    "timestamp": current.get("created_at_utc", ""),
                    "identity_change": identity_change,
                    "previous_key": previous.get("key", "unknown"),
                    "current_key": current.get("key", "unknown"),
                    "severity": "critical" if identity_change > 0.7 else "high",
                }
                identity_analysis["changes"].append(change_event)

        # Calculate overall coherence
        if identity_analysis["changes"]:
            max_change = max(
                change["identity_change"] for change in identity_analysis["changes"]
            )
            identity_analysis["coherence_score"] = max(0.0, 1.0 - max_change)

        return identity_analysis

    def _calculate_identity_change(
        self, snapshot1: dict[str, Any], snapshot2: dict[str, Any]
    ) -> float:
        """Calculate identity change score between two snapshots."""
        content1 = str(snapshot1.get("content", "")).lower()
        content2 = str(snapshot2.get("content", "")).lower()

        # Identity keywords
        identity_keywords = [
            "self",
            "identity",
            "personality",
            "values",
            "beliefs",
            "core",
            "essence",
            "character",
            "nature",
            "being",
            "consciousness",
        ]

        # Extract identity-related content
        identity_content1 = [kw for kw in identity_keywords if kw in content1]
        identity_content2 = [kw for kw in identity_keywords if kw in content2]

        # Calculate content overlap
        if not identity_content1 and not identity_content2:
            return 0.0

        intersection = set(identity_content1).intersection(set(identity_content2))
        union = set(identity_content1).union(set(identity_content2))

        overlap_score = len(intersection) / len(union) if union else 0.0
        change_score = 1.0 - overlap_score

        # Weight by importance scores
        importance1 = snapshot1.get("importance_score", 0.5)
        importance2 = snapshot2.get("importance_score", 0.5)
        importance_change = abs(importance2 - importance1)

        # Combine content and importance changes
        total_change = (change_score * 0.7) + (importance_change * 0.3)

        return min(1.0, total_change)

    def _analyze_temporal_patterns(
        self, snapshots: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze temporal patterns in memory snapshots."""
        temporal_analysis = {
            "time_gaps": [],
            "creation_patterns": {},
            "access_patterns": {},
            "temporal_anomalies": [],
        }

        # Analyze time gaps between consecutive snapshots
        for i in range(1, len(snapshots)):
            current_time_str = snapshots[i].get("created_at_utc", "")
            previous_time_str = snapshots[i - 1].get("created_at_utc", "")

            if current_time_str and previous_time_str:
                try:
                    current_time = datetime.fromisoformat(
                        current_time_str.replace("Z", "+00:00")
                    )
                    previous_time = datetime.fromisoformat(
                        previous_time_str.replace("Z", "+00:00")
                    )

                    gap_hours = (current_time - previous_time).total_seconds() / 3600

                    if gap_hours > 24:  # Gaps larger than 24 hours
                        temporal_analysis["time_gaps"].append(
                            {
                                "start_time": previous_time_str,
                                "end_time": current_time_str,
                                "gap_hours": round(gap_hours, 2),
                                "severity": (
                                    "high" if gap_hours > 168 else "medium"
                                ),  # 1 week threshold
                            }
                        )
                except (ValueError, KeyError, TypeError) as e:
                    logger.debug(f"Failed to analyze temporal gap: {e}")
                    continue

        return temporal_analysis

    def _generate_drift_events(
        self, entropy_analysis: dict, symbol_divergence: dict, identity_drift: dict
    ) -> list[dict[str, Any]]:
        """Generate consolidated drift events from analysis results."""
        drift_events = []

        # Add entropy change events
        for change in entropy_analysis.get("changes", []):
            drift_events.append(
                {
                    "timestamp": change["timestamp"],
                    "event_type": "entropy_drift",
                    "severity": change["severity"],
                    "description": f"Entropy change: {change['entropy_change']:.3f}",
                    "metadata": {
                        "entropy_change": change["entropy_change"],
                        "previous_entropy": change["previous_entropy"],
                        "current_entropy": change["current_entropy"],
                    },
                }
            )

        # Add symbol divergence events
        for divergence in symbol_divergence.get("divergence_events", []):
            drift_events.append(
                {
                    "timestamp": divergence["timestamp"],
                    "event_type": "symbol_divergence",
                    "severity": divergence["severity"],
                    "description": f"Symbol divergence: {divergence['divergence_score']:.3f}",
                    "metadata": {"divergence_score": divergence["divergence_score"]},
                }
            )

        # Add identity change events
        for change in identity_drift.get("changes", []):
            drift_events.append(
                {
                    "timestamp": change["timestamp"],
                    "event_type": "identity_drift",
                    "severity": change["severity"],
                    "description": f"Identity change: {change['identity_change']:.3f}",
                    "metadata": {
                        "identity_change": change["identity_change"],
                        "previous_key": change["previous_key"],
                        "current_key": change["current_key"],
                    },
                }
            )

        # Sort events chronologically
        drift_events.sort(key=lambda x: x.get("timestamp", ""))

        return drift_events

    def _detect_drift_anomalies(
        self, drift_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Detect anomalous patterns in drift events."""
        anomalies = []

        # Detect event clusters (multiple events in short time)
        event_times = []
        for event in drift_events:
            timestamp_str = event.get("timestamp", "")
            if timestamp_str:
                try:
                    event_time = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    event_times.append((event_time, event))
                except (ValueError, KeyError) as e:
                    logger.debug(f"Failed to parse event timestamp: {e}")
                    continue

        # Look for clusters (3+ events within 1 hour)
        for i in range(len(event_times) - 2):
            window_events = []
            window_start = event_times[i][0]

            for j in range(i, len(event_times)):
                event_time, event = event_times[j]
                if (event_time - window_start).total_seconds() <= 3600:  # 1 hour window
                    window_events.append(event)
                else:
                    break

            if len(window_events) >= 3:
                anomalies.append(
                    {
                        "type": "event_cluster",
                        "timestamp": window_start.isoformat(),
                        "event_count": len(window_events),
                        "description": f"Cluster of {len(window_events)} drift events in 1 hour",
                        "severity": "high",
                    }
                )

        return anomalies

    def _generate_drift_recommendations(
        self, drift_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on drift analysis."""
        recommendations = []

        # Check entropy patterns
        entropy_changes = len(
            drift_analysis.get("entropy_analysis", {}).get("changes", [])
        )
        if entropy_changes > 5:
            recommendations.append(
                "HIGH_ENTROPY_ACTIVITY: Consider memory consolidation"
            )

        # Check symbol divergence
        divergence_events = len(
            drift_analysis.get("symbol_divergence", {}).get("divergence_events", [])
        )
        if divergence_events > 3:
            recommendations.append("SYMBOL_INSTABILITY: Review symbolic consistency")

        # Check identity coherence
        identity_coherence = drift_analysis.get("identity_drift", {}).get(
            "coherence_score", 1.0
        )
        if identity_coherence < 0.7:
            recommendations.append(
                "IDENTITY_DRIFT_CRITICAL: Immediate attention required"
            )
        elif identity_coherence < 0.9:
            recommendations.append("IDENTITY_DRIFT_MODERATE: Monitor closely")

        # Check anomalies
        anomalies = len(drift_analysis.get("anomalies_detected", []))
        if anomalies > 0:
            recommendations.append(
                f"ANOMALIES_DETECTED: {anomalies} patterns require investigation"
            )

        return recommendations

    # Collapse detection methods

    def _detect_information_loss(self) -> list[dict[str, Any]]:
        """Detect sudden information loss events."""
        information_loss_events = []

        for i in range(1, len(self.memory_snapshots)):
            current = self.memory_snapshots[i]
            previous = self.memory_snapshots[i - 1]

            # Calculate information metrics
            current_info = self._calculate_information_content(current)
            previous_info = self._calculate_information_content(previous)

            # Check for significant loss
            if previous_info > 0:
                loss_ratio = (previous_info - current_info) / previous_info

                if loss_ratio > 0.3:  # 30% information loss threshold
                    information_loss_events.append(
                        {
                            "timestamp": current.get("created_at_utc", ""),
                            "loss_ratio": loss_ratio,
                            "previous_info": previous_info,
                            "current_info": current_info,
                            "severity": "critical" if loss_ratio > 0.7 else "high",
                            "snapshot_key": current.get("key", "unknown"),
                        }
                    )

        return information_loss_events

    def _calculate_information_content(self, snapshot: dict[str, Any]) -> float:
        """Calculate information content measure for a snapshot."""
        content = snapshot.get("content", "")
        content_str = str(content) if content else ""

        # Simple information measure: unique words + structure
        words = set(re.findall(r"\b\w+\b", content_str.lower()))
        word_count = len(words)

        # Add structural information
        structure_info = 0
        structure_info += len(snapshot.get("tags", [])) * 2
        structure_info += len(snapshot.get("associated_keys", [])) * 3
        structure_info += 5 if snapshot.get("importance_score", 0) > 0.5 else 0

        return word_count + structure_info

    def _detect_phase_gaps(self) -> list[dict[str, Any]]:
        """Detect phase gaps in memory sequence."""
        phase_gaps = []

        # Group snapshots by memory type to detect type-specific gaps
        type_sequences = defaultdict(list)
        for snapshot in self.memory_snapshots:
            mem_type = snapshot.get("memory_type", "unknown")
            type_sequences[mem_type].append(snapshot)

        # Check for gaps within each type
        for mem_type, sequence in type_sequences.items():
            if len(sequence) < 2:
                continue

            for i in range(1, len(sequence)):
                current_time_str = sequence[i].get("created_at_utc", "")
                previous_time_str = sequence[i - 1].get("created_at_utc", "")

                if current_time_str and previous_time_str:
                    try:
                        current_time = datetime.fromisoformat(
                            current_time_str.replace("Z", "+00:00")
                        )
                        previous_time = datetime.fromisoformat(
                            previous_time_str.replace("Z", "+00:00")
                        )

                        gap_hours = (
                            current_time - previous_time
                        ).total_seconds() / 3600

                        # Memory type-specific gap thresholds
                        gap_threshold = {
                            "identity": 12,  # Identity memories should be more continuous
                            "emotional": 24,  # Emotional memories
                            "episodic": 48,  # Episodic memories
                            "semantic": 72,  # Semantic memories can have larger gaps
                        }.get(mem_type, 48)

                        if gap_hours > gap_threshold:
                            phase_gaps.append(
                                {
                                    "timestamp": current_time_str,
                                    "memory_type": mem_type,
                                    "gap_hours": round(gap_hours, 2),
                                    "previous_snapshot": sequence[i - 1].get(
                                        "key", "unknown"
                                    ),
                                    "current_snapshot": sequence[i].get(
                                        "key", "unknown"
                                    ),
                                    "severity": (
                                        "high"
                                        if gap_hours > gap_threshold * 2
                                        else "medium"
                                    ),
                                }
                            )
                    except (ValueError, KeyError, TypeError) as e:
                        logger.debug(f"Failed to analyze phase gap: {e}")
                        continue

        return phase_gaps

    def _detect_integrity_breaks(self) -> list[dict[str, Any]]:
        """Detect integrity breaks in memory fold sequence."""
        integrity_breaks = []

        # Track key patterns and associations
        key_patterns = set()
        association_patterns = defaultdict(set)

        for snapshot in self.memory_snapshots:
            key = snapshot.get("key", "")
            associated_keys = snapshot.get("associated_keys", [])

            # Check for duplicate keys (integrity violation)
            if key in key_patterns and key:
                integrity_breaks.append(
                    {
                        "timestamp": snapshot.get("created_at_utc", ""),
                        "type": "duplicate_key",
                        "key": key,
                        "severity": "critical",
                        "description": f"Duplicate memory key detected: {key}",
                    }
                )
            key_patterns.add(key)

            # Track association patterns for orphaned references
            for assoc_key in associated_keys:
                association_patterns[key].add(assoc_key)

        # Check for orphaned associations
        all_keys = {s.get("key", "") for s in self.memory_snapshots}

        for key, associations in association_patterns.items():
            orphaned_associations = associations - all_keys
            if orphaned_associations:
                integrity_breaks.append(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "orphaned_associations",
                        "key": key,
                        "orphaned_keys": list(orphaned_associations),
                        "severity": "medium",
                        "description": f"Orphaned associations in {key}: {orphaned_associations}",
                    }
                )

        return integrity_breaks

    def _analyze_cascade_patterns(self) -> list[dict[str, Any]]:
        """Analyze cascade failure patterns in memory."""
        cascade_patterns = []

        # Look for sequences where multiple related memories collapse/drift together
        memory_families = defaultdict(list)

        # Group memories by association patterns
        for snapshot in self.memory_snapshots:
            key = snapshot.get("key", "")
            associations = snapshot.get("associated_keys", [])

            # Create family based on key patterns or associations
            family_id = self._determine_memory_family(key, associations)
            memory_families[family_id].append(snapshot)

        # Analyze each family for cascade patterns
        for family_id, family_members in memory_families.items():
            if len(family_members) < 2:
                continue

            # Check for simultaneous issues in family members
            family_issues = []

            for member in family_members:
                # Check if this member has drift or collapse indicators
                member_entropy = self._calculate_snapshot_entropy(member)
                if member_entropy > self.entropy_threshold:
                    family_issues.append(
                        {
                            "key": member.get("key", ""),
                            "timestamp": member.get("created_at_utc", ""),
                            "issue_type": "high_entropy",
                            "entropy": member_entropy,
                        }
                    )

            # If multiple family members have issues in similar timeframe
            if len(family_issues) >= 2:
                # Check if issues are temporally clustered
                issue_times = []
                for issue in family_issues:
                    timestamp_str = issue["timestamp"]
                    if timestamp_str:
                        try:
                            issue_time = datetime.fromisoformat(
                                timestamp_str.replace("Z", "+00:00")
                            )
                            issue_times.append(issue_time)
                        except (ValueError, KeyError) as e:
                            logger.debug(f"Failed to parse issue timestamp: {e}")
                            continue

                if issue_times:
                    time_span = max(issue_times) - min(issue_times)
                    if time_span.total_seconds() <= 3600 * 6:  # Within 6 hours
                        cascade_patterns.append(
                            {
                                "family_id": family_id,
                                "affected_members": len(family_issues),
                                "time_span_hours": time_span.total_seconds() / 3600,
                                "issues": family_issues,
                                "severity": (
                                    "high" if len(family_issues) > 3 else "medium"
                                ),
                            }
                        )

        return cascade_patterns

    def _determine_memory_family(self, key: str, associations: list[str]) -> str:
        """Determine memory family identifier based on key patterns."""
        # Simple family determination based on key prefixes or association patterns
        key_prefix = key.split("_")[0] if "_" in key else key[:8]

        if associations:
            # Use first association as family identifier
            assoc_key = associations[0]
            prefix = assoc_key.split("_")[0] if "_" in assoc_key else assoc_key[:8]
            return f"family_{prefix}"

        return f"family_{key_prefix}"

    def _analyze_collapse_signatures(self) -> dict[str, Any]:
        """Analyze signatures that precede memory collapses."""
        collapse_signatures = {
            "entropy_spikes": [],
            "association_breaks": [],
            "importance_drops": [],
            "temporal_irregularities": [],
        }

        # Analyze patterns that occur before information loss events
        for i, snapshot in enumerate(self.memory_snapshots[1:], 1):
            previous = self.memory_snapshots[i - 1]

            # Check for entropy spikes
            current_entropy = self._calculate_snapshot_entropy(snapshot)
            previous_entropy = self._calculate_snapshot_entropy(previous)

            if current_entropy > previous_entropy + 0.3:
                collapse_signatures["entropy_spikes"].append(
                    {
                        "timestamp": snapshot.get("created_at_utc", ""),
                        "entropy_increase": current_entropy - previous_entropy,
                        "snapshot_key": snapshot.get("key", ""),
                    }
                )

            # Check for association breaks
            current_assoc = set(snapshot.get("associated_keys", []))
            previous_assoc = set(previous.get("associated_keys", []))

            lost_associations = previous_assoc - current_assoc
            if len(lost_associations) > 2:
                collapse_signatures["association_breaks"].append(
                    {
                        "timestamp": snapshot.get("created_at_utc", ""),
                        "lost_associations": list(lost_associations),
                        "snapshot_key": snapshot.get("key", ""),
                    }
                )

            # Check for importance drops
            current_importance = snapshot.get("importance_score", 0.5)
            previous_importance = previous.get("importance_score", 0.5)

            if previous_importance - current_importance > 0.3:
                collapse_signatures["importance_drops"].append(
                    {
                        "timestamp": snapshot.get("created_at_utc", ""),
                        "importance_drop": previous_importance - current_importance,
                        "snapshot_key": snapshot.get("key", ""),
                    }
                )

        return collapse_signatures

    def _synthesize_collapse_events(
        self, info_loss: list, phase_gaps: list, integrity_breaks: list
    ) -> list[dict[str, Any]]:
        """Synthesize collapse events from analysis results."""
        collapse_events = []

        # Convert information loss events
        for loss_event in info_loss:
            collapse_events.append(
                {
                    "timestamp": loss_event["timestamp"],
                    "event_type": "information_loss",
                    "severity": loss_event["severity"],
                    "description": f"Information loss: {loss_event['loss_ratio']:.1%}",
                    "metadata": loss_event,
                }
            )

        # Convert phase gaps
        for gap_event in phase_gaps:
            collapse_events.append(
                {
                    "timestamp": gap_event["timestamp"],
                    "event_type": "phase_gap",
                    "severity": gap_event["severity"],
                    "description": f"Phase gap in {gap_event['memory_type']}: "
                    f"{gap_event['gap_hours']}h",
                    "metadata": gap_event,
                }
            )

        # Convert integrity breaks
        for break_event in integrity_breaks:
            collapse_events.append(
                {
                    "timestamp": break_event["timestamp"],
                    "event_type": "integrity_break",
                    "severity": break_event["severity"],
                    "description": break_event["description"],
                    "metadata": break_event,
                }
            )

        # Sort chronologically
        collapse_events.sort(key=lambda x: x.get("timestamp", ""))

        return collapse_events

    def _build_forensic_timeline(
        self, collapse_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Build forensic timeline of collapse events."""
        timeline = []

        for event in collapse_events:
            timeline_entry = {
                "timestamp": event["timestamp"],
                "event_type": event["event_type"],
                "severity": event["severity"],
                "description": event["description"],
                "forensic_markers": self._extract_forensic_markers(event),
            }
            timeline.append(timeline_entry)

        return timeline

    def _extract_forensic_markers(self, event: dict[str, Any]) -> list[str]:
        """Extract forensic markers from collapse event."""
        markers = []

        event_type = event.get("event_type", "")
        metadata = event.get("metadata", {})

        if event_type == "information_loss":
            loss_ratio = metadata.get("loss_ratio", 0)
            if loss_ratio > 0.7:
                markers.append("CRITICAL_DATA_LOSS")
            elif loss_ratio > 0.5:
                markers.append("MAJOR_DATA_LOSS")
            else:
                markers.append("MODERATE_DATA_LOSS")

        elif event_type == "phase_gap":
            gap_hours = metadata.get("gap_hours", 0)
            memory_type = metadata.get("memory_type", "")

            if gap_hours > 168:  # 1 week
                markers.append("EXTENDED_TEMPORAL_GAP")
            elif memory_type == "identity":
                markers.append("IDENTITY_CONTINUITY_BREAK")

        elif event_type == "integrity_break":
            break_type = metadata.get("type", "")
            if break_type == "duplicate_key":
                markers.append("KEY_INTEGRITY_VIOLATION")
            elif break_type == "orphaned_associations":
                markers.append("ASSOCIATION_INTEGRITY_VIOLATION")

        return markers

    def _assess_collapse_severity(
        self, collapse_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Assess overall severity of collapse events."""
        severity_counts = defaultdict(int)

        for event in collapse_events:
            severity = event.get("severity", "low")
            severity_counts[severity] += 1

        # Calculate overall severity score
        severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_score = sum(
            severity_scores[sev] * count for sev, count in severity_counts.items()
        )
        max_possible = len(collapse_events) * 4 if collapse_events else 1

        overall_severity_ratio = total_score / max_possible

        if overall_severity_ratio > 0.75:
            overall_severity = "critical"
        elif overall_severity_ratio > 0.5:
            overall_severity = "high"
        elif overall_severity_ratio > 0.25:
            overall_severity = "medium"
        else:
            overall_severity = "low"

        return {
            "severity_counts": dict(severity_counts),
            "total_events": len(collapse_events),
            "severity_score": total_score,
            "overall_severity": overall_severity,
            "severity_ratio": overall_severity_ratio,
        }

    def _identify_recovery_opportunities(
        self, collapse_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Identify opportunities for memory recovery."""
        recovery_opportunities = []

        # Group events by type for recovery analysis
        event_groups = defaultdict(list)
        for event in collapse_events:
            event_groups[event["event_type"]].append(event)

        # Information loss recovery opportunities
        info_loss_events = event_groups.get("information_loss", [])
        if info_loss_events:
            for event in info_loss_events:
                metadata = event.get("metadata", {})
                loss_ratio = metadata.get("loss_ratio", 0)

                if loss_ratio < 0.8:  # Partial loss - recovery possible
                    recovery_opportunities.append(
                        {
                            "event_timestamp": event["timestamp"],
                            "recovery_type": "partial_reconstruction",
                            "confidence": 1.0 - loss_ratio,
                            "description": "Partial memory reconstruction from remaining fragments",
                            "recommended_action": "MEMORY_RECONSTRUCTION",
                        }
                    )

        # Phase gap recovery
        phase_gaps = event_groups.get("phase_gap", [])
        if phase_gaps:
            for event in phase_gaps:
                metadata = event.get("metadata", {})
                gap_hours = metadata.get("gap_hours", 0)

                if gap_hours < 168:  # Less than 1 week - interpolation possible
                    recovery_opportunities.append(
                        {
                            "event_timestamp": event["timestamp"],
                            "recovery_type": "temporal_interpolation",
                            "confidence": max(0.1, 1.0 - (gap_hours / 168)),
                            "description": "Temporal gap interpolation from adjacent memories",
                            "recommended_action": "TEMPORAL_BRIDGING",
                        }
                    )

        # Integrity break recovery
        integrity_breaks = event_groups.get("integrity_break", [])
        for event in integrity_breaks:
            metadata = event.get("metadata", {})
            break_type = metadata.get("type", "")

            if break_type == "orphaned_associations":
                recovery_opportunities.append(
                    {
                        "event_timestamp": event["timestamp"],
                        "recovery_type": "association_repair",
                        "confidence": 0.8,
                        "description": "Repair orphaned associations through pattern matching",
                        "recommended_action": "ASSOCIATION_REPAIR",
                    }
                )

        return recovery_opportunities

    # Report generation methods

    def _compile_audit_data(self) -> dict[str, Any]:
        """Compile all audit data into a comprehensive structure."""
        return {
            "audit_metadata": {
                "session_id": self.audit_session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": self.config,
                "temporal_span": self._get_temporal_span(),
            },
            "memory_snapshots": {
                "total_count": len(self.memory_snapshots),
                "chronological_order": self._verify_chronological_order(),
                "memory_types": self._get_memory_type_distribution(),
                "temporal_coverage": self._analyze_temporal_coverage(),
            },
            "drift_analysis": {
                "total_events": len(self.drift_events),
                "severity_distribution": self._get_severity_distribution(
                    self.drift_events
                ),
                "event_types": self._get_event_type_distribution(self.drift_events),
                "temporal_distribution": self._get_temporal_distribution(
                    self.drift_events
                ),
            },
            "collapse_analysis": {
                "total_events": len(self.collapse_events),
                "severity_distribution": self._get_severity_distribution(
                    self.collapse_events
                ),
                "event_types": self._get_event_type_distribution(self.collapse_events),
                "recovery_potential": len(
                    [e for e in self.collapse_events if e.get("severity") != "critical"]
                ),
            },
            "integrity_status": {
                "overall_health": self._assess_overall_health(),
                "critical_issues": len(
                    [
                        e
                        for e in self.drift_events + self.collapse_events
                        if e.get("severity") == "critical"
                    ]
                ),
                "recommendations": self._generate_overall_recommendations(),
            },
        }

    def _get_temporal_span(self) -> dict[str, Any]:
        """Get temporal span information."""
        if len(self.memory_snapshots) < 2:
            return {"span_days": 0, "earliest": None, "latest": None}

        earliest = self.memory_snapshots[0].get("created_at_utc", "")
        latest = self.memory_snapshots[-1].get("created_at_utc", "")
        span_days = self._calculate_temporal_span(earliest, latest)

        return {"earliest": earliest, "latest": latest, "span_days": span_days}

    def _get_memory_type_distribution(self) -> dict[str, int]:
        """Get distribution of memory types."""
        type_counts = defaultdict(int)
        for snapshot in self.memory_snapshots:
            mem_type = snapshot.get("memory_type", "unknown")
            type_counts[mem_type] += 1
        return dict(type_counts)

    def _analyze_temporal_coverage(self) -> dict[str, Any]:
        """Analyze temporal coverage of memory snapshots."""
        if not self.memory_snapshots:
            return {"gaps": 0, "average_interval_hours": 0, "coverage_ratio": 0}

        timestamps = []
        for snapshot in self.memory_snapshots:
            timestamp_str = snapshot.get("created_at_utc", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    timestamps.append(timestamp)
                except (ValueError, KeyError) as e:
                    logger.debug(
                        f"Failed to parse timestamp for frequency analysis: {e}"
                    )
                    continue

        if len(timestamps) < 2:
            return {"gaps": 0, "average_interval_hours": 0, "coverage_ratio": 1.0}

        # Calculate intervals
        intervals = []
        gaps = 0

        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600
            intervals.append(interval)

            if interval > 24:  # Gap larger than 24 hours
                gaps += 1

        average_interval = sum(intervals) / len(intervals) if intervals else 0

        # Coverage ratio (simple heuristic)
        total_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        expected_snapshots = max(1, total_span / 12)  # Expect snapshot every 12 hours
        coverage_ratio = min(1.0, len(timestamps) / expected_snapshots)

        return {
            "gaps": gaps,
            "average_interval_hours": round(average_interval, 2),
            "coverage_ratio": round(coverage_ratio, 3),
        }

    def _get_severity_distribution(
        self, events: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Get severity distribution of events."""
        severity_counts = defaultdict(int)
        for event in events:
            severity = event.get("severity", "low")
            severity_counts[severity] += 1
        return dict(severity_counts)

    def _get_event_type_distribution(
        self, events: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Get event type distribution."""
        type_counts = defaultdict(int)
        for event in events:
            event_type = event.get("event_type", "unknown")
            type_counts[event_type] += 1
        return dict(type_counts)

    def _get_temporal_distribution(
        self, events: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Get temporal distribution of events by hour."""
        hour_counts = defaultdict(int)

        for event in events:
            timestamp_str = event.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hour_key = f"{timestamp.hour:02d}:00"
                    hour_counts[hour_key] += 1
                except (ValueError, KeyError, AttributeError) as e:
                    logger.debug(f"Failed to process hourly distribution: {e}")
                    continue

        return dict(hour_counts)

    def _assess_overall_health(self) -> str:
        """Assess overall system health."""
        critical_events = len(
            [
                e
                for e in self.drift_events + self.collapse_events
                if e.get("severity") == "critical"
            ]
        )
        high_events = len(
            [
                e
                for e in self.drift_events + self.collapse_events
                if e.get("severity") == "high"
            ]
        )

        if critical_events > 0:
            return "CRITICAL"
        elif high_events > 5:
            return "DEGRADED"
        elif high_events > 0:
            return "STABLE_WITH_ISSUES"
        else:
            return "STABLE"

    def _generate_overall_recommendations(self) -> list[str]:
        """Generate overall recommendations for the system."""
        recommendations = []

        # Check for critical issues
        critical_events = [
            e
            for e in self.drift_events + self.collapse_events
            if e.get("severity") == "critical"
        ]
        if critical_events:
            recommendations.append(
                "IMMEDIATE_ATTENTION_REQUIRED: Critical memory integrity issues detected"
            )

        # Check drift patterns
        identity_drift_events = [
            e for e in self.drift_events if e.get("event_type") == "identity_drift"
        ]
        if identity_drift_events:
            recommendations.append(
                "IDENTITY_MONITORING: Enhanced identity consistency monitoring recommended"
            )

        # Check collapse patterns
        info_loss_events = [
            e for e in self.collapse_events if e.get("event_type") == "information_loss"
        ]
        if len(info_loss_events) > 3:
            recommendations.append(
                "MEMORY_BACKUP: Implement more frequent memory backup procedures"
            )

        # Check temporal gaps
        phase_gaps = [
            e for e in self.collapse_events if e.get("event_type") == "phase_gap"
        ]
        if phase_gaps:
            recommendations.append(
                "TEMPORAL_MONITORING: Address temporal discontinuities in memory sequence"
            )

        return recommendations

    def _generate_summary_statistics(
        self, audit_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate summary statistics for the audit."""
        return {
            "total_snapshots_analyzed": audit_data["memory_snapshots"]["total_count"],
            "total_drift_events": audit_data["drift_analysis"]["total_events"],
            "total_collapse_events": audit_data["collapse_analysis"]["total_events"],
            "critical_issues": audit_data["integrity_status"]["critical_issues"],
            "overall_health": audit_data["integrity_status"]["overall_health"],
            "temporal_span_days": audit_data["audit_metadata"]["temporal_span"][
                "span_days"
            ],
            "chronological_integrity": audit_data["memory_snapshots"][
                "chronological_order"
            ],
            "temporal_coverage_ratio": audit_data["memory_snapshots"][
                "temporal_coverage"
            ]["coverage_ratio"],
        }

    def _generate_markdown_report(
        self, output_path: str, audit_data: dict[str, Any], metadata: dict[str, Any]
    ) -> Optional[str]:
        """Generate Markdown audit report."""
        try:
            md_path = (
                output_path.replace(".json", ".md")
                if output_path.endswith(".json")
                else f"{output_path}.md"
            )

            md_content = self._build_markdown_content(audit_data, metadata)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            logger.info(
                "Markdown report generated", path=md_path, tag="ΛAUDITOR_REPORT_MD"
            )

            return md_path

        except Exception as e:
            logger.error(
                "Failed to generate Markdown report", error=str(e), tag="ΛAUDITOR_ERROR"
            )
            return None

    def _build_markdown_content(
        self, audit_data: dict[str, Any], metadata: dict[str, Any]
    ) -> str:
        """Build Markdown content for audit report."""
        md_lines = []

        # Header
        md_lines.append("# ΛAUDITOR Memory Drift Audit Report")
        md_lines.append("**LUKHAS Cognitive AI Memory Forensics and Integrity Analysis**")
        md_lines.append("")

        # Metadata section
        md_lines.append("## Audit Metadata")
        md_lines.append("")
        md_lines.append(f"- **Session ID**: `{metadata['audit_session_id']}`")
        md_lines.append(f"- **Generation Time**: {metadata['generation_timestamp']}")
        md_lines.append(f"- **Snapshots Analyzed**: {metadata['snapshots_analyzed']}")
        md_lines.append(
            f"- **Temporal Span**: {metadata['temporal_span']['span_days']} days"
        )
        md_lines.append(
            f"- **Analysis Window**: {metadata['config'].get('temporal_window_hours', 48)} hours"
        )
        md_lines.append("")

        # Executive Summary
        md_lines.append("## Executive Summary")
        md_lines.append("")
        overall_health = audit_data["integrity_status"]["overall_health"]
        health_emoji = {
            "STABLE": "🟢",
            "STABLE_WITH_ISSUES": "🟡",
            "DEGRADED": "🟠",
            "CRITICAL": "🔴",
        }.get(overall_health, "🟢")

        md_lines.append(f"**Overall System Health**: {health_emoji} {overall_health}")
        md_lines.append("")

        # Summary statistics
        summary = audit_data["integrity_status"]
        md_lines.append("### Key Findings")
        md_lines.append("")
        md_lines.append(
            f"- **Drift Events Detected**: {audit_data['drift_analysis']['total_events']}"
        )
        md_lines.append(
            f"- **Collapse Events Detected**: {audit_data['collapse_analysis']['total_events']}"
        )
        md_lines.append(f"- **Critical Issues**: {summary['critical_issues']}")
        md_lines.append(
            f"- **Temporal Coverage**: {audit_data['memory_snapshots']['temporal_coverage']['coverage_ratio']:.1%}"
        )
        md_lines.append("")

        # Recommendations
        if summary.get("recommendations"):
            md_lines.append("### Priority Recommendations")
            md_lines.append("")
            for i, rec in enumerate(summary["recommendations"], 1):
                md_lines.append(f"{i}. **{rec}**")
            md_lines.append("")

        # Memory Analysis
        md_lines.append("## Memory Snapshot Analysis")
        md_lines.append("")
        mem_data = audit_data["memory_snapshots"]
        md_lines.append(f"- **Total Snapshots**: {mem_data['total_count']}")
        md_lines.append(
            f"- **Chronological Order**: {'✓' if mem_data['chronological_order'] else '✗'}"
        )
        md_lines.append(f"- **Temporal Gaps**: {mem_data['temporal_coverage']['gaps']}")
        md_lines.append("")

        # Memory type distribution
        md_lines.append("### Memory Type Distribution")
        md_lines.append("")
        md_lines.append("| Memory Type | Count | Percentage |")
        md_lines.append("|-------------|-------|------------|")

        type_dist = mem_data["memory_types"]
        total_memories = sum(type_dist.values()) if type_dist else 1

        for mem_type, count in sorted(type_dist.items()):
            percentage = (count / total_memories) * 100
            md_lines.append(f"| {mem_type} | {count} | {percentage:.1f}% |")
        md_lines.append("")

        # Drift Analysis
        md_lines.append("## Drift Analysis")
        md_lines.append("")
        drift_data = audit_data["drift_analysis"]

        if drift_data["total_events"] > 0:
            md_lines.append("### Drift Event Summary")
            md_lines.append("")

            severity_dist = drift_data["severity_distribution"]
            for severity in ["critical", "high", "medium", "low"]:
                count = severity_dist.get(severity, 0)
                if count > 0:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(severity, "🟢")
                    md_lines.append(
                        f"- {severity_emoji} **{severity.title()}**: {count} events"
                    )
            md_lines.append("")

            # Event type breakdown
            md_lines.append("### Drift Event Types")
            md_lines.append("")
            event_types = drift_data["event_types"]
            for event_type, count in sorted(event_types.items()):
                md_lines.append(
                    f"- **{event_type.replace('_', ' ').title()}**: {count}"
                )
            md_lines.append("")
        else:
            md_lines.append("**No drift events detected in the analyzed timeframe.**")
            md_lines.append("")

        # Collapse Analysis
        md_lines.append("## Collapse Analysis")
        md_lines.append("")
        collapse_data = audit_data["collapse_analysis"]

        if collapse_data["total_events"] > 0:
            md_lines.append("### Collapse Event Summary")
            md_lines.append("")

            severity_dist = collapse_data["severity_distribution"]
            for severity in ["critical", "high", "medium", "low"]:
                count = severity_dist.get(severity, 0)
                if count > 0:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(severity, "🟢")
                    md_lines.append(
                        f"- {severity_emoji} **{severity.title()}**: {count} events"
                    )
            md_lines.append("")

            md_lines.append(
                f"**Recovery Potential**: {collapse_data['recovery_potential']} events may be recoverable"
            )
            md_lines.append("")

            # Event type breakdown
            md_lines.append("### Collapse Event Types")
            md_lines.append("")
            event_types = collapse_data["event_types"]
            for event_type, count in sorted(event_types.items()):
                md_lines.append(
                    f"- **{event_type.replace('_', ' ').title()}**: {count}"
                )
            md_lines.append("")
        else:
            md_lines.append(
                "**No collapse events detected in the analyzed timeframe.**"
            )
            md_lines.append("")

        # Footer
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("*Generated by ΛAUDITOR Memory Drift Auditor*")
        md_lines.append(f"*Analysis completed at {metadata['generation_timestamp']}*")
        md_lines.append("")

        return "\n".join(md_lines)

    def _generate_json_report(
        self, output_path: str, audit_data: dict[str, Any], metadata: dict[str, Any]
    ) -> Optional[str]:
        """Generate JSON audit report."""
        try:
            json_path = (
                output_path.replace(".md", ".json")
                if output_path.endswith(".md")
                else f"{output_path}.json"
            )

            # Compile complete JSON report
            json_report = {
                "audit_metadata": metadata,
                "audit_data": audit_data,
                "drift_events": self.drift_events,
                "collapse_events": self.collapse_events,
                "memory_snapshots_summary": {
                    "total_count": len(self.memory_snapshots),
                    "sample_keys": [
                        s.get("key", "") for s in self.memory_snapshots[:10]
                    ],  # First 10 keys as sample
                },
            }

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)

            logger.info(
                "JSON report generated", path=json_path, tag="ΛAUDITOR_REPORT_JSON"
            )

            return json_path

        except Exception as e:
            logger.error(
                "Failed to generate JSON report", error=str(e), tag="ΛAUDITOR_ERROR"
            )
            return None


def main():
    """CLI entry point for the Memory Drift Auditor."""
    parser = argparse.ArgumentParser(
        description="ΛAUDITOR Memory Drift Auditor & Collapse Tracer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 memory_drift_auditor.py --dir memory/folds/ --out results/audit.md
  python3 memory_drift_auditor.py --dir /path/to/folds --format both --timeline
  python3 memory_drift_auditor.py --dir folds/ --window 24h --deep-analysis
        """,
    )

    parser.add_argument(
        "--dir", required=True, help="Directory containing memory fold snapshots"
    )

    parser.add_argument(
        "--out",
        default="memory_drift_audit_report",
        help="Output path for audit report (default: memory_drift_audit_report)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--window",
        choices=["1h", "6h", "24h", "all"],
        default="all",
        help="Analysis time window (default: all)",
    )

    parser.add_argument(
        "--timeline", action="store_true", help="Display ASCII timeline visualization"
    )

    parser.add_argument(
        "--deep-analysis",
        action="store_true",
        help="Enable comprehensive collapse pattern analysis",
    )

    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=0.7,
        help="Entropy change threshold for drift detection (default: 0.7)",
    )

    parser.add_argument(
        "--drift-threshold",
        type=float,
        default=0.4,
        help="Symbol divergence threshold for drift detection (default: 0.4)",
    )

    args = parser.parse_args()

    logger.info(
        "🧠 ΛAUDITOR Memory Drift Auditor & Memory Collapse Tracer",
        tag="ΛAUDITOR_CLI_START",
    )
    logger.info("═" * 60, tag="ΛAUDITOR_CLI_HEADER")

    # Configure auditor
    config = {
        "entropy_threshold": args.entropy_threshold,
        "drift_threshold": args.drift_threshold,
        "temporal_window_hours": {"1h": 1, "6h": 6, "24h": 24, "all": 168}.get(
            args.window, 168
        ),
        "enable_deep_analysis": args.deep_analysis,
        "generate_visualization": args.timeline,
    }

    # Initialize auditor
    auditor = MemoryDriftAuditor(config)

    try:
        logger.info(
            f"📂 Loading memory snapshots from: {args.dir}", tag="ΛAUDITOR_CLI_LOAD"
        )
        loading_results = auditor.load_memory_snapshots(args.dir)

        logger.info(
            f"   ✓ Loaded {loading_results['snapshots_loaded']} snapshots",
            tag="ΛAUDITOR_CLI_LOAD_SUCCESS",
        )
        if loading_results["invalid_snapshots"] > 0:
            logger.warning(
                f"   ⚠ Skipped {loading_results['invalid_snapshots']} invalid snapshots",
                tag="ΛAUDITOR_CLI_LOAD_WARNING",
            )
        if loading_results["loading_errors"]:
            logger.error(
                f"   ❌ {len(loading_results['loading_errors'])} loading errors",
                tag="ΛAUDITOR_CLI_LOAD_ERROR",
            )

        if loading_results["snapshots_loaded"] == 0:
            logger.error(
                "❌ No valid memory snapshots found. Exiting.",
                tag="ΛAUDITOR_CLI_NO_DATA",
            )
            return

        logger.info(
            f"🔍 Analyzing memory drift (window: {args.window})",
            tag="ΛAUDITOR_CLI_DRIFT_START",
        )
        drift_analysis = auditor.detect_memory_drift(args.window)

        drift_events = len(drift_analysis.get("drift_events", []))
        logger.info(
            f"   ✓ Detected {drift_events} drift events",
            tag="ΛAUDITOR_CLI_DRIFT_RESULT",
        )

        anomalies = len(drift_analysis.get("anomalies_detected", []))
        if anomalies > 0:
            logger.warning(
                f"   ⚠ {anomalies} anomalous patterns detected",
                tag="ΛAUDITOR_CLI_DRIFT_ANOMALIES",
            )

        logger.info("💥 Tracing collapse events", tag="ΛAUDITOR_CLI_COLLAPSE_START")
        collapse_analysis = auditor.trace_collapse_events(args.deep_analysis)

        collapse_events = len(collapse_analysis.get("collapse_events", []))
        logger.info(
            f"   ✓ Detected {collapse_events} collapse events",
            tag="ΛAUDITOR_CLI_COLLAPSE_RESULT",
        )

        recovery_ops = len(collapse_analysis.get("recovery_opportunities", []))
        if recovery_ops > 0:
            logger.info(
                f"   🔄 {recovery_ops} recovery opportunities identified",
                tag="ΛAUDITOR_CLI_RECOVERY",
            )

        logger.info(
            f"📊 Generating audit report: {args.out}", tag="ΛAUDITOR_CLI_REPORT_START"
        )
        report_results = auditor.generate_audit_report(args.out, args.format)

        if report_results["report_generated"]:
            logger.info(
                "   ✓ Report generated successfully", tag="ΛAUDITOR_CLI_REPORT_SUCCESS"
            )
            for output_file in report_results["output_files"]:
                logger.info(f"   📄 {output_file}", tag="ΛAUDITOR_CLI_REPORT_FILE")
        else:
            logger.error(
                "   ❌ Report generation failed", tag="ΛAUDITOR_CLI_REPORT_FAIL"
            )
            for error in report_results.get("generation_errors", []):
                logger.error(f"      Error: {error}", tag="ΛAUDITOR_CLI_REPORT_ERROR")

        # Display timeline if requested
        if args.timeline:
            logger.info("📈 Memory Timeline Visualization", tag="ΛAUDITOR_CLI_TIMELINE")
            timeline = auditor.visualize_memory_timeline(show_events=True)
            logger.info(timeline, tag="ΛAUDITOR_CLI_TIMELINE_DATA")

        # Display summary
        summary_stats = report_results.get("summary_statistics", {})
        overall_health = summary_stats.get("overall_health", "UNKNOWN")

        health_emoji = {
            "STABLE": "🟢",
            "STABLE_WITH_ISSUES": "🟡",
            "DEGRADED": "🟠",
            "CRITICAL": "🔴",
        }.get(overall_health, "🟢")

        logger.info("📋 Audit Summary", tag="ΛAUDITOR_CLI_SUMMARY")
        logger.info(
            f"   Overall Health: {health_emoji} {overall_health}",
            tag="ΛAUDITOR_CLI_HEALTH",
        )
        logger.info(
            f"   Total Drift Events: {summary_stats.get('total_drift_events', 0)}",
            tag="ΛAUDITOR_CLI_DRIFT_COUNT",
        )
        logger.info(
            f"   Total Collapse Events: {summary_stats.get('total_collapse_events', 0)}",
            tag="ΛAUDITOR_CLI_COLLAPSE_COUNT",
        )
        logger.info(
            f"   Critical Issues: {summary_stats.get('critical_issues', 0)}",
            tag="ΛAUDITOR_CLI_CRITICAL",
        )
        logger.info(
            f"   Temporal Coverage: {summary_stats.get('temporal_coverage_ratio', 0):.1%}",
            tag="ΛAUDITOR_CLI_COVERAGE",
        )

        # Display warnings/recommendations
        recommendations = drift_analysis.get("recommendation_flags", [])
        if recommendations:
            logger.warning("⚠️  Recommendations:", tag="ΛAUDITOR_CLI_RECOMMENDATIONS")
            for rec in recommendations:
                logger.warning(f"   • {rec}", tag="ΛAUDITOR_CLI_REC")

        logger.info(
            "✅ ΛAUDITOR analysis completed successfully", tag="ΛAUDITOR_CLI_COMPLETE"
        )

    except Exception as e:
        logger.error(
            f"❌ Critical error during audit: {e}", tag="ΛAUDITOR_CLI_CRITICAL_ERROR"
        )
        logger.error("Critical audit error", error=str(e), tag="ΛAUDITOR_CRITICAL")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

# ## CLAUDE CHANGELOG
#
# - Created comprehensive Memory Drift Auditor implementation with
#   enterprise-grade audit framework # CLAUDE_EDIT_v0.1
# - Implemented load_memory_snapshots(), detect_memory_drift(), trace_collapse_events(),
#   generate_audit_report(), and visualize_memory_timeline() functions # CLAUDE_EDIT_v0.2
# - Added CLI interface with argparse for flexible command-line usage # CLAUDE_EDIT_v0.3
# - Integrated with existing LUKHAS memory architecture including fold_engine.py
#   and symbolic trace logging # CLAUDE_EDIT_v0.4
# - Implemented forensic analysis capabilities for identity-level inconsistencies
#   and symbolic phase tracing # CLAUDE_EDIT_v0.5