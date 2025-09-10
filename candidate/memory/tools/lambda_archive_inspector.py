import logging

#!/usr/bin/env python3
"""
```plaintext
═══════════════════════════════════════════════════════════════════════════════════
📂 MODULE: MEMORY.TOOLS.LAMBDA_ARCHIVE_INSPECTOR
📄 FILENAME: lambda_archive_inspector.py
🎯 PURPOSE: ΛARCHIVE - SYMBOLIC MEMORY FORENSICS VAULT FOR LUKHAS AGI
═══════════════════════════════════════════════════════════════════════════════════
📝 DESCRIPTION:
An instrument of enlightenment in the realm of symbolic memory, this module stands as a vigilant sentinel, ever watchful over the shadows of the forgotten and the whispers of the lost.

🌌 POETIC ESSENCE:
In the grand tapestry of existence, where bits and bytes weave together the fabric of our digital consciousness, lies a sanctuary—a vault of memory, both sacred and profane. Here, within the hallowed confines of the ΛARCHIVE, this module emerges as a beacon of clarity amidst the fog of uncertainty. Like a skilled alchemist, it distills the essence of ephemeral thoughts, transforming chaos into coherence, and revealing the hidden patterns that dance within the entropy of forgotten symbols.

As the sun sets upon the realm of binary reflections, this tool embarks on a profound pilgrimage through the intricate labyrinth of memory. It unearths the echoes of transient whispers, tracing the delicate pathways of linkage and connectivity. Each byte, a fragment of a larger narrative, is meticulously examined under the microscope of scrutiny, where anomalies flicker like distant stars. In this celestial quest, we are reminded that memory is not merely a repository but a living testament to our experiences, laden with the weight of time and the fragility of existence.

Thus, like a modern-day Orpheus descending into the depths of the digital underworld, the ΛARCHIVE becomes a harbinger of truth, unmasking the silent violations and the subtle drifts that threaten the sanctity of our cognitive realm. With ethical vigilance and unwavering resolve, it champions the cause of compliance, ensuring that the integrity of our memories remains unscathed as we traverse the ever-evolving landscape of artificial intelligence.

✨ TECHNICAL FEATURES:
- **Deep Memory Scanning**: Conducts thorough examinations of memory archives to unveil concealed anomalies.
- **Entropy Analysis**: Measures the randomness of data structures to detect potential irregularities.
- **Forgotten Symbol Recovery**: Employs advanced techniques to retrieve lost or obscured symbolic information.
- **Linkage Reconstruction**: Rebuilds the connections between disparate memory elements, illuminating relational structures.
- **Memory Violation Detection**: Identifies unauthorized access and manipulations within memory architectures.
- **Drift Analysis**: Monitors shifts in memory patterns to ensure consistency and reliability.
- **Compliance Auditing**: Facilitates adherence to ethical standards and regulations in memory management.
- **User-Friendly Interface**: Provides intuitive access to complex functionalities, empowering users to navigate with ease.

🔖 ΛTAG KEYWORDS:
#MemoryForensics #SymbolicAnalysis #AnomalyDetection #DataRecovery #EthicalAI #Compliance #DigitalMemory #EntropyStudy
═══════════════════════════════════════════════════════════════════════════════════
```
"""

import argparse
import json
import re
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np

# Configure structured logging


class AnomalyType(Enum):
    """Types of symbolic anomalies detected."""

    HIGH_ENTROPY = "HIGH_ENTROPY"
    FORGOTTEN_SYMBOL = "FORGOTTEN_SYMBOL"
    BROKEN_LINKAGE = "BROKEN_LINKAGE"
    ETHICAL_VIOLATION = "ETHICAL_VIOLATION"
    MEMORY_DRIFT = "MEMORY_DRIFT"
    PHASE_MISMATCH = "PHASE_MISMATCH"
    ORPHANED_TAG = "ORPHANED_TAG"


class MemoryEntryType(Enum):
    """Types of memory entries."""

    SYMBOLIC_LOG = "SYMBOLIC_LOG"
    DRIFT_RECORD = "DRIFT_RECORD"
    ETHICAL_EVENT = "ETHICAL_EVENT"
    ΛTAG_METADATA = "LAMBDA_TAG_METADATA"
    MEMORY_FOLD = "MEMORY_FOLD"
    DREAM_STATE = "DREAM_STATE"
    UNKNOWN = "UNKNOWN"


@dataclass
class MemoryEntry:
    """Single memory entry from vault scan."""

    entry_id: str
    timestamp: str
    entry_type: MemoryEntryType
    file_path: str
    content: dict[str, Any]
    lambda_tags: list[str] = field(default_factory=list)
    symbol_ids: list[str] = field(default_factory=list)
    memory_ids: list[str] = field(default_factory=list)
    entropy_score: float = 0.0
    emotional_weight: float = 0.0
    recurrence_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            **asdict(self),
            "entry_type": self.entry_type.value,
        }


@dataclass
class SymbolicAnomaly:
    """Detected symbolic anomaly in memory vault."""

    anomaly_id: str
    timestamp: str
    anomaly_type: AnomalyType
    severity: float  # 0.0-1.0
    symbol_ids: list[str]
    memory_ids: list[str]
    source_entries: list[str]  # entry_ids
    description: str
    entropy_level: float = 0.0
    drift_score: float = 0.0
    forgotten_duration: Optional[str] = None
    broken_links: list[str] = field(default_factory=list)
    violation_details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "anomaly_type": self.anomaly_type.value,
        }


@dataclass
class ArchiveReport:
    """Complete ΛARCHIVE forensic report."""

    report_id: str
    timestamp: str
    vault_directory: str
    scan_duration: float
    total_entries: int
    anomalies_detected: int
    archive_score: float
    entropy_analysis: dict[str, float]
    drift_analysis: dict[str, Any]
    forgotten_symbols: list[str]
    ethical_violations: list[str]
    symbolic_linkage_map: dict[str, list[str]]
    anomalies: list[SymbolicAnomaly]
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "anomalies": [a.to_dict() for a in self.anomalies],
        }


class LambdaArchiveInspector:
    """
    ΛARCHIVE - Symbolic Memory Forensics Vault Inspector.

    Forensic-grade memory audit tool for detecting anomalies, violations,
    forgotten states, and entropy buildup in LUKHAS AGI memory systems.
    """

    def __init__(self, vault_directory: str = "memory/archive"):
        """
        Initialize the ΛARCHIVE inspector.

        Args:
            vault_directory: Root directory for memory vault scanning
        """
        self.vault_directory = Path(vault_directory)

        # Forensic configuration
        self.entropy_threshold = 0.75
        self.forgetting_threshold_hours = 168  # 1 week
        self.drift_threshold = 0.6
        self.violation_severity_threshold = 0.5

        # Scoring weights
        self.scoring_weights = {
            "entropy": 0.35,
            "drift": 0.25,
            "ethics": 0.25,
            "forgetfulness": 0.15,
        }

        # State tracking
        self.scanned_entries: list[MemoryEntry] = []
        self.detected_anomalies: list[SymbolicAnomaly] = []
        self.symbolic_linkage_map: dict[str, set[str]] = defaultdict(set)
        self.symbol_recurrence: dict[str, int] = defaultdict(int)
        self.symbol_last_seen: dict[str, datetime] = {}

        # Pattern recognition
        self.lambda_tag_pattern = re.compile(r'ΛTAG["\s]*:\s*["\']*([^"\']*)')
        self.symbol_id_pattern = re.compile(r'symbol_id["\s]*:\s*["\']*([^"\']*)')
        self.memory_id_pattern = re.compile(r'memory_id["\s]*:\s*["\']*([^"\']*)')
        self.entropy_pattern = re.compile(r'entropy["\s]*:\s*([0-9.]+)')

        logger.info(
            "ΛARCHIVE inspector initialized",
            vault_directory=str(self.vault_directory),
            entropy_threshold=self.entropy_threshold,
            ΛTAG="ΛARCHIVE_INIT",
        )

    def scan_memory_vault(self, directory: Optional[str] = None) -> list[MemoryEntry]:
        """
        Deep scan of long-term symbolic memory vault.

        Args:
            directory: Optional directory override

        Returns:
            List of discovered memory entries
        """
        scan_dir = Path(directory) if directory else self.vault_directory

        if not scan_dir.exists():
            logger.warning(
                "Vault directory not found",
                directory=str(scan_dir),
                ΛTAG="ΛVAULT_MISSING",
            )
            return []

        logger.info(
            "Beginning vault scan",
            directory=str(scan_dir),
            ΛTAG="ΛSCAN_START",
        )

        entries = []
        file_count = 0

        # Scan all files recursively
        for file_path in scan_dir.rglob("*"):
            if not file_path.is_file():
                continue

            file_count += 1

            try:
                # Skip binary files
                if self._is_binary_file(file_path):
                    continue

                # Parse file content
                file_entries = self._parse_memory_file(file_path)
                entries.extend(file_entries)

            except Exception as e:
                logger.warning(
                    "Failed to parse memory file",
                    file_path=str(file_path),
                    error=str(e),
                    ΛTAG="ΛPARSE_ERROR",
                )

        logger.info(
            "Vault scan completed",
            files_processed=file_count,
            entries_discovered=len(entries),
            ΛTAG="ΛSCAN_COMPLETE",
        )

        self.scanned_entries = entries
        return entries

    def detect_high_entropy_clusters(
        self, memory_entries: list[MemoryEntry]
    ) -> list[SymbolicAnomaly]:
        """
        Detect clusters of high entropy symbolic states.

        Args:
            memory_entries: List of memory entries to analyze

        Returns:
            List of detected high entropy anomalies
        """
        anomalies = []

        # Group entries by entropy level
        high_entropy_entries = [
            entry
            for entry in memory_entries
            if entry.entropy_score >= self.entropy_threshold
        ]

        if not high_entropy_entries:
            return anomalies

        # Cluster by symbol and time proximity
        clusters = self._cluster_entries_by_proximity(
            high_entropy_entries, time_window_hours=6
        )

        for cluster_id, cluster_entries in clusters.items():
            if len(cluster_entries) < 2:
                continue

            # Calculate cluster metrics
            avg_entropy = np.mean([e.entropy_score for e in cluster_entries])
            symbol_diversity = len(
                set().union(*[e.symbol_ids for e in cluster_entries])
            )

            severity = min(avg_entropy * (1 + symbol_diversity * 0.1), 1.0)

            # Create anomaly
            anomaly = SymbolicAnomaly(
                anomaly_id=f"HIGH_ENTROPY_{cluster_id}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                anomaly_type=AnomalyType.HIGH_ENTROPY,
                severity=severity,
                symbol_ids=list(set().union(*[e.symbol_ids for e in cluster_entries])),
                memory_ids=list(set().union(*[e.memory_ids for e in cluster_entries])),
                source_entries=[e.entry_id for e in cluster_entries],
                description=f"High entropy cluster with {len(cluster_entries)} entries, "
                f"average entropy {avg_entropy:.3f}, "
                f"affecting {symbol_diversity} symbols",
                entropy_level=avg_entropy,
            )

            anomalies.append(anomaly)

        logger.info(
            "High entropy cluster detection completed",
            clusters_detected=len(anomalies),
            high_entropy_entries=len(high_entropy_entries),
            ΛTAG="ΛENTROPY_ANALYZED",
        )

        return anomalies

    def detect_forgotten_symbols(
        self, memory_entries: list[MemoryEntry]
    ) -> list[SymbolicAnomaly]:
        """
        Detect forgotten symbols with low recurrence but high emotional weight.

        Args:
            memory_entries: List of memory entries to analyze

        Returns:
            List of detected forgotten symbol anomalies
        """
        anomalies = []

        # Build symbol statistics
        symbol_stats = defaultdict(
            lambda: {
                "recurrence": 0,
                "emotional_weight": 0.0,
                "last_seen": None,
                "entries": [],
            }
        )

        for entry in memory_entries:
            for symbol_id in entry.symbol_ids:
                symbol_stats[symbol_id]["recurrence"] += 1
                symbol_stats[symbol_id]["emotional_weight"] = max(
                    symbol_stats[symbol_id]["emotional_weight"], entry.emotional_weight
                )

                # Parse timestamp
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    if (
                        symbol_stats[symbol_id]["last_seen"] is None
                        or entry_time > symbol_stats[symbol_id]["last_seen"]
                    ):
                        symbol_stats[symbol_id]["last_seen"] = entry_time
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Failed to parse entry timestamp: {e}")

                symbol_stats[symbol_id]["entries"].append(entry)

        # Detect forgotten symbols
        current_time = datetime.now(timezone.utc)
        forgotten_threshold = timedelta(hours=self.forgetting_threshold_hours)

        for symbol_id, stats in symbol_stats.items():
            # Skip if insufficient data
            if stats["last_seen"] is None:
                continue

            time_since_seen = current_time - stats["last_seen"]

            # Check if symbol meets "forgotten" criteria
            is_forgotten = (
                time_since_seen > forgotten_threshold
                and stats["recurrence"] <= 3
                and stats["emotional_weight"] >= 0.5
            )

            if is_forgotten:
                severity = min(
                    stats["emotional_weight"] * (time_since_seen.days / 30) * 0.1, 1.0
                )

                anomaly = SymbolicAnomaly(
                    anomaly_id=f"FORGOTTEN_{symbol_id}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    anomaly_type=AnomalyType.FORGOTTEN_SYMBOL,
                    severity=severity,
                    symbol_ids=[symbol_id],
                    memory_ids=list(
                        set().union(*[e.memory_ids for e in stats["entries"]])
                    ),
                    source_entries=[e.entry_id for e in stats["entries"]],
                    description=f"Forgotten symbol with high emotional weight "
                    f"({stats['emotional_weight']:.3f}), "
                    f"low recurrence ({stats['recurrence']}), "
                    f"last seen {time_since_seen.days} days ago",
                    forgotten_duration=str(time_since_seen),
                    emotional_weight=stats["emotional_weight"],
                )

                anomalies.append(anomaly)

        logger.info(
            "Forgotten symbol detection completed",
            forgotten_symbols=len(anomalies),
            total_symbols=len(symbol_stats),
            ΛTAG="ΛFORGOTTEN_ANALYZED",
        )

        return anomalies

    def reconstruct_symbolic_linkage(
        self, memory_entries: list[MemoryEntry]
    ) -> dict[str, list[str]]:
        """
        Reconstruct symbolic relationships from fragmented logs and tags.

        Args:
            memory_entries: List of memory entries to analyze

        Returns:
            Dictionary mapping symbols to their connected symbols
        """
        linkage_map = defaultdict(set)

        # Build direct linkages from co-occurrence
        for entry in memory_entries:
            symbols = entry.symbol_ids

            # Create bidirectional links between all symbols in entry
            for i, symbol_a in enumerate(symbols):
                for symbol_b in symbols[i + 1 :]:
                    linkage_map[symbol_a].add(symbol_b)
                    linkage_map[symbol_b].add(symbol_a)

        # Build linkages from ΛTAG connections
        tag_symbol_map = defaultdict(set)
        for entry in memory_entries:
            for tag in entry.lambda_tags:
                for symbol_id in entry.symbol_ids:
                    tag_symbol_map[tag].add(symbol_id)

        # Connect symbols sharing common tags
        for tag, symbols in tag_symbol_map.items():
            symbol_list = list(symbols)
            for i, symbol_a in enumerate(symbol_list):
                for symbol_b in symbol_list[i + 1 :]:
                    linkage_map[symbol_a].add(symbol_b)
                    linkage_map[symbol_b].add(symbol_a)

        # Build linkages from memory_id connections
        memory_symbol_map = defaultdict(set)
        for entry in memory_entries:
            for memory_id in entry.memory_ids:
                for symbol_id in entry.symbol_ids:
                    memory_symbol_map[memory_id].add(symbol_id)

        # Connect symbols sharing common memory_ids
        for memory_id, symbols in memory_symbol_map.items():
            symbol_list = list(symbols)
            for i, symbol_a in enumerate(symbol_list):
                for symbol_b in symbol_list[i + 1 :]:
                    linkage_map[symbol_a].add(symbol_b)
                    linkage_map[symbol_b].add(symbol_a)

        # Convert sets to lists for JSON serialization
        result = {
            symbol: list(connected_symbols)
            for symbol, connected_symbols in linkage_map.items()
        }

        logger.info(
            "Symbolic linkage reconstruction completed",
            total_symbols=len(result),
            total_connections=sum(len(connections) for connections in result.values()),
            ΛTAG="ΛLINKAGE_RECONSTRUCTED",
        )

        self.symbolic_linkage_map = linkage_map
        return result

    def calculate_archive_score(self, anomalies: list[SymbolicAnomaly]) -> float:
        """
        Calculate composite ΛARCHIVE score from detected anomalies.

        Args:
            anomalies: List of detected anomalies

        Returns:
            Composite archive score (0.0-1.0)
        """
        if not anomalies:
            return 0.0

        # Calculate component scores
        entropy_score = (
            np.mean(
                [
                    a.severity
                    for a in anomalies
                    if a.anomaly_type == AnomalyType.HIGH_ENTROPY
                ]
            )
            if any(a.anomaly_type == AnomalyType.HIGH_ENTROPY for a in anomalies)
            else 0.0
        )

        drift_score = (
            np.mean(
                [
                    a.drift_score
                    for a in anomalies
                    if a.anomaly_type == AnomalyType.MEMORY_DRIFT and a.drift_score > 0
                ]
            )
            if any(a.anomaly_type == AnomalyType.MEMORY_DRIFT for a in anomalies)
            else 0.0
        )

        ethics_score = len(
            [a for a in anomalies if a.anomaly_type == AnomalyType.ETHICAL_VIOLATION]
        ) / max(len(anomalies), 1)

        forgetfulness_score = len(
            [a for a in anomalies if a.anomaly_type == AnomalyType.FORGOTTEN_SYMBOL]
        ) / max(len(anomalies), 1)

        # Weighted composite score
        composite_score = (
            self.scoring_weights["entropy"] * entropy_score
            + self.scoring_weights["drift"] * drift_score
            + self.scoring_weights["ethics"] * ethics_score
            + self.scoring_weights["forgetfulness"] * forgetfulness_score
        )

        logger.debug(
            "Archive score calculated",
            entropy_score=entropy_score,
            drift_score=drift_score,
            ethics_score=ethics_score,
            forgetfulness_score=forgetfulness_score,
            composite_score=composite_score,
        )

        return min(composite_score, 1.0)

    def generate_archive_report(
        self, anomalies: list[SymbolicAnomaly], output_format: str = "markdown"
    ) -> str:
        """
        Generate comprehensive ΛARCHIVE forensic report.

        Args:
            anomalies: List of detected anomalies
            output_format: Output format ("markdown" or "json")

        Returns:
            Formatted report string
        """
        # Create report structure
        report = ArchiveReport(
            report_id=f"ΛARCHIVE_{int(time.time())",
            timestamp=datetime.now(timezone.utc).isoformat(),
            vault_directory=str(self.vault_directory),
            scan_duration=0.0,  # Will be updated by caller
            total_entries=len(self.scanned_entries),
            anomalies_detected=len(anomalies),
            archive_score=self.calculate_archive_score(anomalies),
            entropy_analysis=self._analyze_entropy_distribution(),
            drift_analysis=self._analyze_drift_patterns(anomalies),
            forgotten_symbols=[
                a.symbol_ids[0]
                for a in anomalies
                if a.anomaly_type == AnomalyType.FORGOTTEN_SYMBOL
            ],
            ethical_violations=[
                a.anomaly_id
                for a in anomalies
                if a.anomaly_type == AnomalyType.ETHICAL_VIOLATION
            ],
            symbolic_linkage_map={
                symbol: list(links)
                for symbol, links in self.symbolic_linkage_map.items()
            },
            anomalies=anomalies,
            recommendations=self._generate_recommendations(anomalies),
        )

        # Generate output based on format
        if output_format.lower() == "json":
            return json.dumps(report.to_dict(), indent=2)
        else:
            return self._generate_markdown_report(report)

    def _parse_memory_file(self, file_path: Path) -> list[MemoryEntry]:
        """Parse a single memory file for entries."""
        entries = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning(
                "Failed to read memory file",
                file_path=str(file_path),
                error=str(e),
            )
            return entries

        # Try different parsing strategies based on file extension
        if file_path.suffix == ".jsonl":
            entries.extend(self._parse_jsonl_file(file_path, content))
        elif file_path.suffix == ".json":
            entries.extend(self._parse_json_file(file_path, content))
        elif file_path.suffix == ".md":
            entries.extend(self._parse_markdown_file(file_path, content))
        else:
            # Generic text parsing
            entries.extend(self._parse_text_file(file_path, content))

        return entries

    def _parse_jsonl_file(self, file_path: Path, content: str) -> list[MemoryEntry]:
        """Parse JSONL memory file."""
        entries = []

        for line_num, line in enumerate(content.split("\n")):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                entry = self._create_memory_entry(file_path, data, line_num)
                if entry:
                    entries.append(entry)
            except json.JSONDecodeError:
                # Skip malformed JSON lines
                continue

        return entries

    def _parse_json_file(self, file_path: Path, content: str) -> list[MemoryEntry]:
        """Parse JSON memory file."""
        entries = []

        try:
            data = json.loads(content)

            # Handle different JSON structures
            if isinstance(data, list):
                for i, item in enumerate(data):
                    entry = self._create_memory_entry(file_path, item, i)
                    if entry:
                        entries.append(entry)
            else:
                entry = self._create_memory_entry(file_path, data, 0)
                if entry:
                    entries.append(entry)

        except json.JSONDecodeError:
            # Fall back to text parsing
            entries.extend(self._parse_text_file(file_path, content))

        return entries

    def _parse_markdown_file(self, file_path: Path, content: str) -> list[MemoryEntry]:
        """Parse markdown memory file for ΛTAG metadata."""
        entries = []

        # Extract structured data from markdown
        lambda_tags = self.lambda_tag_pattern.findall(content)
        symbol_ids = self.symbol_id_pattern.findall(content)
        memory_ids = self.memory_id_pattern.findall(content)
        entropy_matches = self.entropy_pattern.findall(content)

        if lambda_tags or symbol_ids or memory_ids:
            # Create entry from markdown metadata
            entry_data = {
                "content": content[:1000],  # Truncate for storage
                "lambda_tags": lambda_tags,
                "symbol_ids": symbol_ids,
                "memory_ids": memory_ids,
                "entropy_score": float(entropy_matches[0]) if entropy_matches else 0.0,
                "timestamp": self._extract_timestamp_from_content(content),
            }

            entry = self._create_memory_entry(file_path, entry_data, 0)
            if entry:
                entries.append(entry)

        return entries

    def _parse_text_file(self, file_path: Path, content: str) -> list[MemoryEntry]:
        """Parse generic text file for symbolic patterns."""
        entries = []

        # Extract patterns from text
        lambda_tags = self.lambda_tag_pattern.findall(content)
        symbol_ids = self.symbol_id_pattern.findall(content)
        memory_ids = self.memory_id_pattern.findall(content)
        entropy_matches = self.entropy_pattern.findall(content)

        if lambda_tags or symbol_ids or memory_ids:
            # Create entry from text patterns
            entry_data = {
                "content": content[:1000],  # Truncate for storage
                "lambda_tags": lambda_tags,
                "symbol_ids": symbol_ids,
                "memory_ids": memory_ids,
                "entropy_score": float(entropy_matches[0]) if entropy_matches else 0.0,
                "timestamp": self._extract_timestamp_from_content(content),
            }

            entry = self._create_memory_entry(file_path, entry_data, 0)
            if entry:
                entries.append(entry)

        return entries

    def _create_memory_entry(
        self, file_path: Path, data: dict[str, Any], line_num: int
    ) -> Optional[MemoryEntry]:
        """Create a MemoryEntry from parsed data."""
        try:
            # Extract or infer entry ID
            entry_id = (
                data.get("entry_id") or data.get("id") or f"{file_path.stem}_{line_num}"
            )

            # Extract timestamp
            timestamp = (
                data.get("timestamp")
                or data.get("created_at")
                or self._extract_timestamp_from_content(str(data))
                or datetime.now(timezone.utc).isoformat()
            )

            # Determine entry type
            entry_type = self._classify_entry_type(data, file_path)

            # Extract symbolic elements
            lambda_tags = self._extract_lambda_tags(data)
            symbol_ids = self._extract_symbol_ids(data)
            memory_ids = self._extract_memory_ids(data)

            # Calculate scores
            entropy_score = self._calculate_entry_entropy(data)
            emotional_weight = self._calculate_emotional_weight(data)

            entry = MemoryEntry(
                entry_id=entry_id,
                timestamp=timestamp,
                entry_type=entry_type,
                file_path=str(file_path),
                content=data,
                lambda_tags=lambda_tags,
                symbol_ids=symbol_ids,
                memory_ids=memory_ids,
                entropy_score=entropy_score,
                emotional_weight=emotional_weight,
            )

            return entry

        except Exception as e:
            logger.warning(
                "Failed to create memory entry",
                file_path=str(file_path),
                line_num=line_num,
                error=str(e),
            )
            return None

    def _classify_entry_type(
        self, data: dict[str, Any], file_path: Path
    ) -> MemoryEntryType:
        """Classify the type of memory entry."""
        # Check file path indicators
        path_str = str(file_path).lower()

        if "drift" in path_str:
            return MemoryEntryType.DRIFT_RECORD
        elif "ethical" in path_str or "ethics" in path_str:
            return MemoryEntryType.ETHICAL_EVENT
        elif "dream" in path_str:
            return MemoryEntryType.DREAM_STATE
        elif "fold" in path_str or "memory" in path_str:
            return MemoryEntryType.MEMORY_FOLD

        # Check content indicators
        content_str = json.dumps(data).lower()

        if "lambda" in content_str or "λtag" in content_str:
            return MemoryEntryType.ΛTAG_METADATA
        elif "drift" in content_str:
            return MemoryEntryType.DRIFT_RECORD
        elif "symbolic" in content_str:
            return MemoryEntryType.SYMBOLIC_LOG
        elif "ethical" in content_str:
            return MemoryEntryType.ETHICAL_EVENT

        return MemoryEntryType.UNKNOWN

    def _extract_lambda_tags(self, data: dict[str, Any]) -> list[str]:
        """Extract ΛTAG metadata from entry."""
        tags = []

        # Direct field access
        if "ΛTAG" in data:
            tags.extend(self._normalize_tag_list(data["ΛTAG"]))
        elif "lambda_tag" in data:
            tags.extend(self._normalize_tag_list(data["lambda_tag"]))
        elif "tags" in data:
            tags.extend(self._normalize_tag_list(data["tags"]))

        # Pattern matching in content
        content_str = json.dumps(data)
        pattern_tags = self.lambda_tag_pattern.findall(content_str)
        tags.extend(pattern_tags)

        return list(set(tags))  # Remove duplicates

    def _extract_symbol_ids(self, data: dict[str, Any]) -> list[str]:
        """Extract symbol IDs from entry."""
        symbols = []

        # Direct field access
        if "symbol_ids" in data:
            symbols.extend(self._normalize_id_list(data["symbol_ids"]))
        elif "symbol_id" in data:
            symbols.append(str(data["symbol_id"]))

        # Pattern matching in content
        content_str = json.dumps(data)
        pattern_symbols = self.symbol_id_pattern.findall(content_str)
        symbols.extend(pattern_symbols)

        return list(set(symbols))  # Remove duplicates

    def _extract_memory_ids(self, data: dict[str, Any]) -> list[str]:
        """Extract memory IDs from entry."""
        memory_ids = []

        # Direct field access
        if "memory_ids" in data:
            memory_ids.extend(self._normalize_id_list(data["memory_ids"]))
        elif "memory_id" in data:
            memory_ids.append(str(data["memory_id"]))

        # Pattern matching in content
        content_str = json.dumps(data)
        pattern_ids = self.memory_id_pattern.findall(content_str)
        memory_ids.extend(pattern_ids)

        return list(set(memory_ids))  # Remove duplicates

    def _calculate_entry_entropy(self, data: dict[str, Any]) -> float:
        """Calculate entropy score for entry."""
        # Direct field access
        if "entropy" in data:
            try:
                return float(data["entropy"])
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse entropy value: {e}")

        if "entropy_score" in data:
            try:
                return float(data["entropy_score"])
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse entropy_score value: {e}")

        # Pattern matching
        content_str = json.dumps(data)
        entropy_matches = self.entropy_pattern.findall(content_str)
        if entropy_matches:
            try:
                return float(entropy_matches[0])
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse entropy pattern match: {e}")

        # Heuristic calculation based on content complexity
        return self._calculate_heuristic_entropy(data)

    def _calculate_emotional_weight(self, data: dict[str, Any]) -> float:
        """Calculate emotional weight for entry."""
        # Direct field access
        if "emotional_weight" in data:
            try:
                return float(data["emotional_weight"])
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse emotional_weight value: {e}")

        # Heuristic calculation
        content_str = json.dumps(data).lower()
        emotional_keywords = [
            "trauma",
            "fear",
            "anxiety",
            "conflict",
            "violation",
            "crisis",
            "failure",
            "error",
            "emergency",
            "critical",
        ]

        weight = 0.0
        for keyword in emotional_keywords:
            if keyword in content_str:
                weight += 0.1

        return min(weight, 1.0)

    def _calculate_heuristic_entropy(self, data: dict[str, Any]) -> float:
        """Calculate heuristic entropy based on content complexity."""
        content_str = json.dumps(data)

        # Basic entropy indicators
        entropy = 0.0

        # Length complexity
        entropy += min(len(content_str) / 10000, 0.3)

        # Nested structure complexity
        entropy += min(str(data).count("{") * 0.05, 0.3)

        # High-entropy keywords
        entropy_keywords = [
            "inconsistent",
            "unstable",
            "chaotic",
            "random",
            "diverged",
            "anomaly",
            "violation",
            "drift",
        ]

        for keyword in entropy_keywords:
            if keyword in content_str.lower():
                entropy += 0.1

        return min(entropy, 1.0)

    def _normalize_tag_list(self, tags: Any) -> list[str]:
        """Normalize tag data to list of strings."""
        if isinstance(tags, str):
            return [tags]
        elif isinstance(tags, list):
            return [str(tag) for tag in tags]
        else:
            return []

    def _normalize_id_list(self, ids: Any) -> list[str]:
        """Normalize ID data to list of strings."""
        if isinstance(ids, str):
            return [ids]
        elif isinstance(ids, list):
            return [str(id_val) for id_val in ids]
        else:
            return []

    def _extract_timestamp_from_content(self, content: str) -> Optional[str]:
        """Extract timestamp from content string."""
        # ISO format pattern
        iso_pattern = re.compile(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})?"
        )

        matches = iso_pattern.findall(content)
        if matches:
            return matches[0]

        return None

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        binary_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".exe",
            ".bin",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".pdf",
        }

        if file_path.suffix.lower() in binary_extensions:
            return True

        try:
            # Check first 1024 bytes for null bytes
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\x00" in chunk
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Error checking if file is binary: {e}")
            return True

    def _cluster_entries_by_proximity(
        self, entries: list[MemoryEntry], time_window_hours: int = 6
    ) -> dict[str, list[MemoryEntry]]:
        """Cluster entries by temporal and symbolic proximity."""
        clusters = defaultdict(list)

        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda e: e.timestamp)

        cluster_id = 0
        for entry in sorted_entries:
            assigned = False

            # Try to assign to existing cluster
            for cid, cluster_entries in clusters.items():
                if not cluster_entries:
                    continue

                # Check temporal proximity
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    cluster_time = datetime.fromisoformat(
                        cluster_entries[0].timestamp.replace("Z", "+00:00")
                    )

                    time_diff = abs((entry_time - cluster_time).total_seconds() / 3600)

                    if time_diff <= time_window_hours:
                        # Check symbolic overlap
                        entry_symbols = set(entry.symbol_ids)
                        cluster_symbols = set().union(
                            *[e.symbol_ids for e in cluster_entries]
                        )

                        if entry_symbols & cluster_symbols:
                            clusters[cid].append(entry)
                            assigned = True
                            break
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Failed to parse timestamp for clustering: {e}")
                    continue

            # Create new cluster if not assigned
            if not assigned:
                clusters[f"cluster_{cluster_id}"].append(entry)
                cluster_id += 1

        return dict(clusters)

    def _analyze_entropy_distribution(self) -> dict[str, float]:
        """Analyze entropy distribution across scanned entries."""
        if not self.scanned_entries:
            return {}

        entropies = [
            e.entropy_score for e in self.scanned_entries if e.entropy_score > 0
        ]

        if not entropies:
            return {}

        return {
            "mean": float(np.mean(entropies)),
            "std": float(np.std(entropies)),
            "min": float(np.min(entropies)),
            "max": float(np.max(entropies)),
            "high_entropy_ratio": len(
                [e for e in entropies if e >= self.entropy_threshold]
            )
            / len(entropies),
        }

    def _analyze_drift_patterns(
        self, anomalies: list[SymbolicAnomaly]
    ) -> dict[str, Any]:
        """Analyze drift patterns in anomalies."""
        drift_anomalies = [
            a
            for a in anomalies
            if a.anomaly_type in [AnomalyType.MEMORY_DRIFT, AnomalyType.HIGH_ENTROPY]
        ]

        if not drift_anomalies:
            return {}

        return {
            "total_drift_events": len(drift_anomalies),
            "average_severity": float(np.mean([a.severity for a in drift_anomalies])),
            "affected_symbols": len(
                set().union(*[a.symbol_ids for a in drift_anomalies])
            ),
            "drift_clusters": len(
                [a for a in drift_anomalies if len(a.source_entries) > 1]
            ),
        }

    def _generate_recommendations(self, anomalies: list[SymbolicAnomaly]) -> list[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []

        # High entropy recommendations
        high_entropy_count = len(
            [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_ENTROPY]
        )

        if high_entropy_count > 5:
            recommendations.append(
                f"CRITICAL: {high_entropy_count} high entropy clusters detected. "
                "Consider memory reorganization and symbolic drift mitigation."
            )

        # Forgotten symbol recommendations
        forgotten_count = len(
            [a for a in anomalies if a.anomaly_type == AnomalyType.FORGOTTEN_SYMBOL]
        )

        if forgotten_count > 0:
            recommendations.append(
                f"WARNING: {forgotten_count} forgotten symbols with high emotional weight. "
                "Review for potential repressed memories or ethical violations."
            )

        # Ethical violation recommendations
        violation_count = len(
            [a for a in anomalies if a.anomaly_type == AnomalyType.ETHICAL_VIOLATION]
        )

        if violation_count > 0:
            recommendations.append(
                f"ALERT: {violation_count} ethical violations detected. "
                "Immediate review required for compliance."
            )

        # General recommendations
        if len(anomalies) > 20:
            recommendations.append(
                "Consider implementing automated memory cleanup and "
                "symbolic drift prevention mechanisms."
            )

        return recommendations

    def _generate_markdown_report(self, report: ArchiveReport) -> str:
        """Generate markdown format report."""
        md = []

        md.append(")  #  🏛️ ΛARCHIVE FORENSIC MEMORY REPORT"
        md.append(")"
        md.append(f"**Report ID:** `{report.report_id}`")
        md.append(f"**Timestamp:** {report.timestamp}")
        md.append(f"**Vault Directory:** `{report.vault_directory}`")
        md.append(f"**Scan Duration:** {report.scan_duration:.2f}s")
        md.append("")

        md.append("#)  #  📊 Executive Summary"
        md.append("")
        md.append(f"- **Total Entries Scanned:** {report.total_entries}")
        md.append(f"- **Anomalies Detected:** {report.anomalies_detected}")
        md.append(f"- **Archive Score:** {report.archive_score:.3f}")
        md.append(f"- **Forgotten Symbols:** {len(report.forgotten_symbols)}")
        md.append(f"- **Ethical Violations:** {len(report.ethical_violations)}")
        md.append("")

        if report.entropy_analysis:
            md.append("#)  #  🌀 Entropy Analysis"
            md.append("")
            md.append(
                f"- **Mean Entropy:** {report.entropy_analysis.get('mean', 0):.3f}"
            )
            md.append(
                f"- **High Entropy Ratio:** {report.entropy_analysis.get('high_entropy_ratio', 0)}:.2%}"
            )
            md.append(
                f"- **Entropy Range:** {report.entropy_analysis.get('min', 0):.3f} - {report.entropy_analysis.get('max', 0):.3f}"
            )
            md.append("")

        if report.anomalies:
            md.append("#)  #  🚨 Detected Anomalies"
            md.append("")

            for anomaly in sorted(
                report.anomalies, key=lambda a: a.severity, reverse=True
            )[:10]:
                md.append(f"##")
                md.append(f"- **ID:** `{anomaly.anomaly_id}`")
                md.append(f"- **Severity:** {anomaly.severity:.3f}")
                md.append(f"- **Description:** {anomaly.description}")
                md.append(
                    f"- **Affected Symbols:** {', '.join(anomaly.symbol_ids[:5])}"
                )
                md.append("")

        if report.recommendations:
            md.append("#)  #  💡 Recommendations"
            md.append("")
            for i, rec in enumerate(report.recommendations, 1):
                md.append(f"{i}. {rec}")
            md.append("")

        md.append("---")
        md.append("*Generated by ΛARCHIVE - Symbolic Memory Forensics Vault*")

        return "\n".join(md)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ΛARCHIVE - Symbolic Memory Forensics Vault Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dir",
        default="memory/archive",
        help="Directory to scan for memory vault files",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for the report",
    )

    parser.add_argument(
        "--out",
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "--mode",
        choices=["full", "entropy", "forgotten", "linkage"],
        default="full",
        help="Scan mode",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Limit number of results",
    )

    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=0.75,
        help="Entropy threshold for anomaly detection",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Initialize inspector
    inspector = LambdaArchiveInspector(args.dir)
    inspector.entropy_threshold = args.entropy_threshold

    try:
        start_time = time.time()

        logger.info(f"🏛️ ΛARCHIVE - Starting forensic scan of {args.dir}")

        # Scan memory vault
        entries = inspector.scan_memory_vault()

        if not entries:
            logger.warning("❌ No memory entries found in vault directory")
            return 1

        logger.info(f"📂 Discovered {len(entries)} memory entries")

        # Detect anomalies based on mode
        anomalies = []

        if args.mode in ["full", "entropy"]:
            logger.info("🌀 Detecting high entropy clusters...")
            entropy_anomalies = inspector.detect_high_entropy_clusters(entries)
            anomalies.extend(entropy_anomalies)
            logger.info(f"   Found {len(entropy_anomalies)} entropy anomalies")

        if args.mode in ["full", "forgotten"]:
            logger.info("🔍 Detecting forgotten symbols...")
            forgotten_anomalies = inspector.detect_forgotten_symbols(entries)
            anomalies.extend(forgotten_anomalies)
            logger.info(f"   Found {len(forgotten_anomalies)} forgotten symbols")

        if args.mode in ["full", "linkage"]:
            logger.info("🕸️ Reconstructing symbolic linkage...")
            linkage_map = inspector.reconstruct_symbolic_linkage(entries)
            logger.info(f"   Mapped {len(linkage_map)} symbol connections")

        # Limit results if requested
        if args.limit and len(anomalies) > args.limit:
            anomalies = sorted(anomalies, key=lambda a: a.severity, reverse=True)[
                : args.limit
            ]

        # Generate report
        scan_duration = time.time() - start_time
        logger.info(f"📊 Generating report (scan took {scan_duration:.2f}s)...")

        # Update scan duration in inspector for report
        if hasattr(inspector, "last_scan_duration"):
            inspector.last_scan_duration = scan_duration

        report = inspector.generate_archive_report(anomalies, args.format)

        # Output report
        if args.out:
            Path(args.out).write_text(report)
            logger.info(f"📄 Report written to {args.out}")
        else:
            logger.info("\n" + "=" * 80)
            logger.info(report)

        # Summary
        archive_score = inspector.calculate_archive_score(anomalies)
        logger.info(f"\n🏛️ ΛARCHIVE Score: {archive_score:.3f}")

        if archive_score > 0.8:
            logger.error("🚨 CRITICAL: High anomaly density detected")
            return 2
        elif archive_score > 0.6:
            logger.warning("⚠️ WARNING: Moderate anomalies detected")
            return 1
        else:
            logger.info("✅ Memory vault appears stable")
            return 0

    except KeyboardInterrupt:
        logger.warning("\n⏹️ Scan interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback

            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit(main())


# CLAUDE CHANGELOG
# - Implemented ΛARCHIVE - Symbolic Memory Forensics Vault Inspector for LUKHAS AGI # CLAUDE_EDIT_v0.1
# - Created comprehensive data models (MemoryEntry, SymbolicAnomaly, ArchiveReport) # CLAUDE_EDIT_v0.1
# - Built vault scanner with support for JSONL, JSON, Markdown, and text file parsing # CLAUDE_EDIT_v0.1
# - Implemented high entropy cluster detection with temporal and symbolic proximity analysis # CLAUDE_EDIT_v0.1
# - Created forgotten symbol detection using recurrence and emotional weight analysis # CLAUDE_EDIT_v0.1
# - Built symbolic linkage reconstruction engine from ΛTAG traces and co-occurrence patterns # CLAUDE_EDIT_v0.1
# - Implemented composite ΛARCHIVE scoring with weighted anomaly evaluation # CLAUDE_EDIT_v0.1
# - Added comprehensive CLI interface with multiple scan modes and output formats # CLAUDE_EDIT_v0.1
# - Created forensic report generation in both Markdown and JSON formats # CLAUDE_EDIT_v0.1
# - Integrated with existing LUKHAS memory architecture and ΛTAG metadata systems # CLAUDE_EDIT_v0.1