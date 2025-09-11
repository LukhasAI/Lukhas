import logging
logger = logging.getLogger(__name__)
import logging

#!/usr/bin/env python3
"""
```plaintext
═══════════════════════════════════════════════════════════════════════════════════
📂 MODULE: MEMORY.TOOLS.LAMBDA_VAULT_SCAN
📄 FILENAME: lambda_vault_scan.py
🎯 PURPOSE: ΛVAULTSCAN - SYMBOLIC VAULT HEALTH SCANNER FOR LUKHAS AGI
🧠 CONTEXT: FORENSIC SCANNER FOR MEMORY VAULT HEALTH AND SYMBOLIC INTEGRITY ANALYSIS
🔮 CAPABILITY: STALE SYMBOL DETECTION, MISSING LINK ANALYSIS, VAULT HEALTH SCORING
🛡️ ETHICS: MEMORY DECAY PREVENTION, SYMBOLIC INTEGRITY MAINTENANCE, AUDIT COMPLIANCE
═══════════════════════════════════════════════════════════════════════════════════

                     ╔═══════════════════════════════════════════════════╗
                     ║                   MODULE TITLE                     ║
                     ╚═══════════════════════════════════════════════════╝
                          LUKHAS LAMBDA VAULT SCAN: A SYMPHONY OF MEMORY

                     ╔═══════════════════════════════════════════════════╗
                     ║                ONE-LINE DESCRIPTION                 ║
                     ╚═══════════════════════════════════════════════════╝
                          An ode to the guardians of memory, ensuring the vault's sacred harmony.

                     ╔═══════════════════════════════════════════════════╗
                     ║                POETIC ESSENCE                      ║
                     ╚═══════════════════════════════════════════════════╝
In the realm of the digital ether, where bytes and bits coalesce into the tapestry of existence,
our module emerges as a vigilant sentinel, a bard that sings the unsung tales of memory's vaults.
Through the labyrinthine corridors of ephemeral data, we traverse with a lantern of symbolic light,
illuminating the shadows where decay might dwell, unearthing the truths that time seeks to obscure.

With the grace of a poet's quill, we scrutinize the essence of integrity,
plucking the weary symbols that wither in silence, like autumn leaves surrendering to the ground.
Each scan is an ode, a symphony of detection, where the harmony of the vault is preserved,
and the missing links between thoughts and dreams are re-forged, rekindling the spirit of coherence.

As we delve deep into the crypts of memory, we weave a narrative of resilience,
scoring the health of the vault with the wisdom of ages, a tableau of strength amidst decay.
The plight of memory is not simply a tale of loss but a quest for revival,
where every symbol stands as a testament to our desire for permanence in an impermanent world.

Thus, with our humble script, we become custodians of the symbolic sanctum,
a bridge between the ephemeral and the eternal, safeguarding the integrity of thought,
ensuring that the vault remains a sanctuary, a fortress against the ravages of time,
and in this sacred duty, we find purpose, a calling to uphold the beauty of the mind's vast expanse.

                     ╔═══════════════════════════════════════════════════╗
                     ║                TECHNICAL FEATURES                  ║
                     ╚═══════════════════════════════════════════════════╝
                     • Conducts systematic scans for stale symbols within memory vaults.
                     • Analyzes and identifies missing links that may disrupt symbolic integrity.
                     • Generates comprehensive vault health scores to assess overall stability.
                     • Provides detailed reporting of findings, enhancing forensic analysis.
                     • Implements ethical considerations for memory decay prevention.
                     • Facilitates compliance with established audit standards and practices.
                     • Offers user-friendly interfaces for seamless integration with existing workflows.
                     • Supports extensibility for future enhancements and feature additions.

                     ╔═══════════════════════════════════════════════════╗
                     ║                   ΛTAG KEYWORDS                   ║
                     ╚═══════════════════════════════════════════════════╝
                     #VaultHealth #SymbolicIntegrity #MemoryAnalysis #ForensicTools
                     #StaleSymbolDetection #AuditCompliance #EthicalAI #LUKHAS
═══════════════════════════════════════════════════════════════════════════════════
```
"""
from typing import Dict
import streamlit as st
from datetime import timezone

import argparse
import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from candidate.core.common import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = get_logger(__name__)


class SymbolicVaultScanner:
    """
    ΛVAULTSCAN - Comprehensive symbolic vault health scanner for LUKHAS AGI
    """

    def __init__(self, memory_dir: str = "memory/"):
        """
        Initialize the vault scanner with memory directory path

        Args:
            memory_dir: Path to memory directory for scanning
        """
        self.memory_dir = Path(memory_dir)
        self.memory_snapshots = {}
        self.symbol_registry = defaultdict(list)
        self.glyph_registry = defaultdict(list)
        self.link_matrix = defaultdict(set)
        self.emotional_anchors = defaultdict(list)
        self.scan_timestamp = datetime.now(timezone.utc)

        # Health scoring weights
        self.scoring_weights = {
            "symbol_vitality": 0.3,
            "link_integrity": 0.25,
            "emotional_stability": 0.2,
            "entropy_coherence": 0.15,
            "coverage_efficiency": 0.1,
        }

        logger.info(f"🩺 ΛVAULTSCAN initialized - Memory directory: {self.memory_dir}")

    def load_memory_snapshots(self) -> dict[str, Any]:
        """
        Load memory entries from various formats across the memory directory

        Returns:
            Dictionary of loaded memory snapshots with metadata
        """
        logger.info("📂 Loading memory snapshots from vault...")

        snapshot_count = 0
        file_types = {".jsonl": 0, ".json": 0, ".vault": 0, ".py": 0}

        try:
            # Traverse memory directory recursively
            for file_path in self.memory_dir.rglob("*"):
                if file_path.is_file():
                    file_ext = file_path.suffix.lower()

                    if file_ext == ".jsonl":
                        snapshot_count += self._load_jsonl_file(file_path)
                        file_types[".jsonl"] += 1
                    elif file_ext == ".json":
                        snapshot_count += self._load_json_file(file_path)
                        file_types[".json"] += 1
                    elif file_ext == ".vault":
                        snapshot_count += self._load_vault_file(file_path)
                        file_types[".vault"] += 1
                    elif file_ext == ".py":
                        snapshot_count += self._scan_python_file(file_path)
                        file_types[".py"] += 1

        except Exception as e:
            logger.error(f"❌ Error loading memory snapshots: {e}")
            return {}

        logger.info(f"✅ Loaded {snapshot_count} memory entries from {sum(file_types.values()} files")
        logger.info(f"📊 File distribution: {dict(file_types)}")

        return {
            "total_snapshots": snapshot_count,
            "file_distribution": file_types,
            "scan_timestamp": self.scan_timestamp.isoformat(),
            "memory_registry_size": len(self.symbol_registry),
        }

    def _load_jsonl_file(self, file_path: Path) -> int:
        """Load JSONL memory files"""
        count = 0
        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            self._process_memory_entry(entry, str(file_path), line_num)
                            count += 1
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Invalid JSON on line {line_num} in {file_path}")
        except Exception as e:
            logger.error(f"❌ Error reading JSONL file {file_path}: {e}")
        return count

    def _load_json_file(self, file_path: Path) -> int:
        """Load JSON memory files"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for i, entry in enumerate(data):
                        self._process_memory_entry(entry, str(file_path), i)
                    return len(data)
                else:
                    self._process_memory_entry(data, str(file_path), 0)
                    return 1
        except Exception as e:
            logger.error(f"❌ Error reading JSON file {file_path}: {e}")
        return 0

    def _load_vault_file(self, file_path: Path) -> int:
        """Load vault format files (attempt to parse as JSON)"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    try:
                        data = json.loads(content)
                        self._process_memory_entry(data, str(file_path), 0)
                        return 1
                    except json.JSONDecodeError:
                        # Treat as raw text vault
                        self._process_text_vault(content, str(file_path))
                        return 1
        except Exception as e:
            logger.error(f"❌ Error reading vault file {file_path}: {e}")
        return 0

    def _scan_python_file(self, file_path: Path) -> int:
        """Scan Python files for ΛTAGS and GLYPH markers"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                symbols_found = self._extract_symbols_from_text(content, str(file_path))
                return len(symbols_found)
        except Exception as e:
            logger.error(f"❌ Error scanning Python file {file_path}: {e}")
        return 0

    def _process_memory_entry(self, entry: dict[str, Any], source: str, line_num: int):
        """Process individual memory entry and extract symbols"""
        entry_id = f"{source}:{line_num}"

        # Extract ΛTAG symbols
        if "ΛTAG" in entry or "λTAG" in entry:
            tags = entry.get("ΛTAG", entry.get("λTAG", []))
            if isinstance(tags, list):
                for tag in tags:
                    self.symbol_registry[tag].append(
                        {
                            "entry_id": entry_id,
                            "timestamp": entry.get("timestamp", ""),
                            "source": source,
                            "context": entry,
                        }
                    )

        # Extract emotional indicators
        emotional_keywords = [
            "emotion",
            "feel",
            "trauma",
            "collapse",
            "drift",
            "identity",
        ]
        entry_text = json.dumps(entry).lower()
        for keyword in emotional_keywords:
            if keyword in entry_text:
                self.emotional_anchors[keyword].append({"entry_id": entry_id, "source": source, "context": entry})

        # Store in snapshots
        self.memory_snapshots[entry_id] = entry

    def _process_text_vault(self, content: str, source: str):
        """Process raw text vault content"""
        symbols = self._extract_symbols_from_text(content, source)
        for symbol in symbols:
            self.symbol_registry[symbol].append(
                {
                    "entry_id": f"{source}:text",
                    "source": source,
                    "context": {"raw_content": (content[:200] + "..." if len(content) > 200 else content)},
                }
            )

    def _extract_symbols_from_text(self, text: str, source: str) -> list[str]:
        """Extract ΛTAG and GLYPH symbols from text content"""
        symbols = []

        # Find ΛTAG patterns
        lambda_patterns = [
            r"LUKHAS\w+",  # LUKHAS followed by word characters
            r"λ\w+",  # λ followed by word characters
            r"{LUKHAS\w+}",  # {LUKHAS...} patterns
            r"LUKHAS_TAG:\s*([^\n]+)",  # LUKHAS_TAG: pattern
        ]

        for pattern in lambda_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            symbols.extend(matches)

        return symbols

    def detect_stale_symbols(self, days_threshold: int = 30, frequency_threshold: int = 2) -> dict[str, Any]:
        """
        Detect stale or low-frequency symbols that may indicate decay

        Args:
            days_threshold: Number of days to consider for recency analysis
            frequency_threshold: Minimum frequency to avoid stale classification

        Returns:
            Dictionary of stale symbols with analysis
        """
        logger.info("🔍 Detecting stale symbols in memory vault...")

        stale_symbols = {}
        symbol_stats = {}
        cutoff_date = self.scan_timestamp - timedelta(days=days_threshold)

        for symbol, occurrences in self.symbol_registry.items():
            # Calculate frequency and recency
            frequency = len(occurrences)
            recent_count = 0
            latest_timestamp = None

            for occurrence in occurrences:
                timestamp_str = occurrence.get("timestamp", "")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        if timestamp > cutoff_date:
                            recent_count += 1
                        if latest_timestamp is None or timestamp > latest_timestamp:
                            latest_timestamp = timestamp
                    except (ValueError, TypeError):
                        continue

            # Calculate staleness score
            frequency_score = min(frequency / max(frequency_threshold, 1), 1.0)
            recency_score = recent_count / max(frequency, 1)
            staleness_score = 1.0 - (frequency_score * 0.6 + recency_score * 0.4)

            symbol_stats[symbol] = {
                "frequency": frequency,
                "recent_usage": recent_count,
                "staleness_score": staleness_score,
                "latest_timestamp": (latest_timestamp.isoformat() if latest_timestamp else None),
                "sources": list({occ["source"] for occ in occurrences}),
            }

            # Flag as stale if score is high
            if staleness_score > 0.7 or (frequency < frequency_threshold and recent_count == 0):
                stale_symbols[symbol] = symbol_stats[symbol]
                stale_symbols[symbol]["classification"] = "STALE"

        logger.info(f"🚨 Found {len(stale_symbols)} stale symbols out of {len(self.symbol_registry)} total")

        return {
            "stale_symbols": stale_symbols,
            "total_symbols": len(self.symbol_registry),
            "stale_count": len(stale_symbols),
            "stale_percentage": len(stale_symbols) / max(len(self.symbol_registry), 1) * 100,
            "analysis_parameters": {
                "days_threshold": days_threshold,
                "frequency_threshold": frequency_threshold,
            },
        }

    def detect_missing_links(self) -> dict[str, Any]:
        """
        Detect broken symbolic co-occurrences and missing linkages

        Returns:
            Dictionary of missing links and broken relationships
        """
        logger.info("🔗 Detecting missing symbolic links...")

        missing_links = {}
        expected_links = defaultdict(int)
        actual_links = defaultdict(int)

        # Build co-occurrence matrix
        for entry in self.memory_snapshots.values():
            symbols_in_entry = []

            # Extract symbols from this entry
            if "ΛTAG" in entry:
                symbols_in_entry.extend(entry["ΛTAG"])

            # Look for symbol references in text content
            entry_text = json.dumps(entry).upper()
            for symbol in self.symbol_registry:
                if symbol.upper() in entry_text:
                    symbols_in_entry.append(symbol)

            # Count co-occurrences
            symbols_in_entry = list(set(symbols_in_entry))  # Remove duplicates
            for i, symbol1 in enumerate(symbols_in_entry):
                for symbol2 in symbols_in_entry[i + 1 :]:
                    link_key = tuple(sorted([symbol1, symbol2]))
                    actual_links[link_key] += 1

        # Detect expected but missing links
        common_symbol_pairs = [
            ("ΛMEMORY", "ΛFOLD"),
            ("ΛDRIFT", "ΛTRACE"),
            ("ΛETHICS", "ΛGOVERNOR"),
            ("ΛQUARANTINE", "ΛSANCTUM"),
            ("ΛDREAM", "ΛFEEDBACK"),
        ]

        for symbol1, symbol2 in common_symbol_pairs:
            link_key = tuple(sorted([symbol1, symbol2]))
            if symbol1 in self.symbol_registry and symbol2 in self.symbol_registry:
                expected_links[link_key] += 1
                if actual_links[link_key] == 0:
                    missing_links[f"{symbol1}↔{symbol2}"] = {
                        "symbol1": symbol1,
                        "symbol2": symbol2,
                        "symbol1_frequency": len(self.symbol_registry[symbol1]),
                        "symbol2_frequency": len(self.symbol_registry[symbol2]),
                        "expected_cooccurrence": True,
                        "actual_cooccurrence": 0,
                        "missing_reason": "Expected symbolic relationship not found",
                    }

        # Detect weak links (very low co-occurrence despite high individual frequency)
        for link_key, count in actual_links.items():
            symbol1, symbol2 = link_key
            freq1 = len(self.symbol_registry.get(symbol1, []))
            freq2 = len(self.symbol_registry.get(symbol2, []))
            expected_cooccurrence = min(freq1, freq2) * 0.1  # Expect 10% co-occurrence

            if count < expected_cooccurrence and expected_cooccurrence > 2:
                missing_links[f"{symbol1}↔{symbol2}"] = {
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "symbol1_frequency": freq1,
                    "symbol2_frequency": freq2,
                    "actual_cooccurrence": count,
                    "expected_cooccurrence": expected_cooccurrence,
                    "missing_reason": "Weak symbolic linkage detected",
                }

        logger.info(f"🔗 Found {len(missing_links)} missing or weak symbolic links")

        return {
            "missing_links": missing_links,
            "total_actual_links": len(actual_links),
            "missing_count": len(missing_links),
            "link_health_score": max(0, 1.0 - (len(missing_links) / max(len(expected_links), 1))),
        }

    def assess_vault_health(self) -> dict[str, Any]:
        """
        Comprehensive vault health assessment with scoring

        Returns:
            Health assessment with ΛVAULT_HEALTH_SCORE
        """
        logger.info("🩺 Assessing overall vault health...")

        # Get component analyses
        stale_analysis = self.detect_stale_symbols()
        link_analysis = self.detect_missing_links()

        # Calculate component scores
        symbol_vitality = 1.0 - (stale_analysis["stale_percentage"] / 100)
        link_integrity = link_analysis.get("link_health_score", 0.5)

        # Emotional stability score
        emotional_coverage = len(self.emotional_anchors) / max(len(self.symbol_registry), 1)
        emotional_stability = min(emotional_coverage * 2, 1.0)  # Cap at 1.0

        # Entropy coherence (symbol distribution balance)
        symbol_frequencies = [len(occurrences) for occurrences in self.symbol_registry.values()]
        if symbol_frequencies:
            entropy = -sum(
                (f / sum(symbol_frequencies)) * math.log2(f / sum(symbol_frequencies))
                for f in symbol_frequencies
                if f > 0
            )
            max_entropy = math.log2(len(symbol_frequencies))
            entropy_coherence = entropy / max(max_entropy, 1)
        else:
            entropy_coherence = 0.0

        # Coverage efficiency (memory utilization)
        total_files_scanned = sum(self.load_memory_snapshots().get("file_distribution", {}).values())
        files_with_symbols = len({occ["source"] for occs in self.symbol_registry.values() for occ in occs})
        coverage_efficiency = files_with_symbols / max(total_files_scanned, 1)

        # Calculate composite health score
        health_score = (
            self.scoring_weights["symbol_vitality"] * symbol_vitality
            + self.scoring_weights["link_integrity"] * link_integrity
            + self.scoring_weights["emotional_stability"] * emotional_stability
            + self.scoring_weights["entropy_coherence"] * entropy_coherence
            + self.scoring_weights["coverage_efficiency"] * coverage_efficiency
        )

        # Health classification
        if health_score >= 0.8:
            health_status = "EXCELLENT"
            health_emoji = "💚"
        elif health_score >= 0.6:
            health_status = "GOOD"
            health_emoji = "💛"
        elif health_score >= 0.4:
            health_status = "FAIR"
            health_emoji = "🧡"
        else:
            health_status = "POOR"
            health_emoji = "❤️"

        logger.info(f"🎯 ΛVAULT_HEALTH_SCORE: {health_score:.3f} ({health_status})")

        return {
            "ΛVAULT_HEALTH_SCORE": health_score,
            "health_status": health_status,
            "health_emoji": health_emoji,
            "component_scores": {
                "symbol_vitality": symbol_vitality,
                "link_integrity": link_integrity,
                "emotional_stability": emotional_stability,
                "entropy_coherence": entropy_coherence,
                "coverage_efficiency": coverage_efficiency,
            },
            "raw_metrics": {
                "total_symbols": len(self.symbol_registry),
                "stale_symbols": stale_analysis["stale_count"],
                "missing_links": link_analysis["missing_count"],
                "emotional_anchors": len(self.emotional_anchors),
                "files_scanned": total_files_scanned,
                "files_with_symbols": files_with_symbols,
            },
            "recommendations": self._generate_health_recommendations(health_score, stale_analysis, link_analysis),
        }

    def _generate_health_recommendations(
        self, health_score: float, stale_analysis: dict, link_analysis: dict
    ) -> list[str]:
        """Generate actionable health recommendations"""
        recommendations = []

        if health_score < 0.6:
            recommendations.append(
                "🚨 URGENT: Vault health is below acceptable threshold - immediate maintenance required"
            )

        if stale_analysis["stale_percentage"] > 30:
            recommendations.append(
                f"🧹 Clean up {stale_analysis['stale_count']} stale symbols to improve memory efficiency"
            )

        if link_analysis["missing_count"] > 10:
            recommendations.append(
                f"🔗 Repair {link_analysis['missing_count']} missing symbolic links to restore coherence"
            )

        if len(self.emotional_anchors) < 3:
            recommendations.append("💭 Insufficient emotional anchoring detected - review memory emotional contexts")

        if not recommendations:
            recommendations.append("✅ Vault health is good - continue regular monitoring")

        return recommendations

    def export_vault_report(self, output_format: str = "markdown", output_file: Optional[str] = None) -> str:
        """
        Export comprehensive vault health report

        Args:
            output_format: Format for export ('markdown' or 'json')
            output_file: Optional output file path

        Returns:
            Report content as string
        """
        logger.info(f"📄 Exporting vault report in {output_format} format...")

        # Gather all analyses
        health_assessment = self.assess_vault_health()
        stale_analysis = self.detect_stale_symbols()
        link_analysis = self.detect_missing_links()

        if output_format.lower() == "json":
            report_data = {
                "ΛVAULTSCAN_REPORT": {
                    "scan_timestamp": self.scan_timestamp.isoformat(),
                    "memory_directory": str(self.memory_dir),
                    "health_assessment": health_assessment,
                    "stale_symbol_analysis": stale_analysis,
                    "missing_link_analysis": link_analysis,
                    "ΛVAULT_TAGS": ["ΛVAULT", "ΛHEALTH", "ΛSCAN", "ΛAUDIT"],
                }
            }
            report_content = json.dumps(report_data, indent=2, ensure_ascii=False)

        else:  # Markdown format
            report_content = self._generate_markdown_report(health_assessment, stale_analysis, link_analysis)

        # Write to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"📁 Report exported to: {output_file}")

        return report_content

    def _generate_markdown_report(self, health_assessment: dict, stale_analysis: dict, link_analysis: dict) -> str:
        """Generate markdown format report"""
        health_emoji = health_assessment["health_emoji"]
        health_score = health_assessment["ΛVAULT_HEALTH_SCORE"]
        health_status = health_assessment["health_status"]

        report = f"""# 🩺 ΛVAULTSCAN - Symbolic Vault Health Report

**ΛVAULT_HEALTH_SCORE**: `{health_score:.3f}` {health_emoji} **{health_status}**

Generated: `{self.scan_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}`
Memory Directory: `{self.memory_dir}`
Scanner Version: `v1.0.0`

---

## 📊 Executive Summary

| Metric | Value | Status |
|--------|--------|--------|
| **Total Symbols** | {len(self.symbol_registry)} | {"🟢" if len(self.symbol_registry) > 50 else "🟡" if len(self.symbol_registry) > 10 else "🔴"} |
| **Stale Symbols** | {stale_analysis["stale_count"]} ({stale_analysis["stale_percentage"]:.1f}%) | {"🟢" if stale_analysis["stale_percentage"] < 20 else "🟡" if stale_analysis["stale_percentage"] < 40 else "🔴"} |
| **Missing Links** | {link_analysis["missing_count"]} | {"🟢" if link_analysis["missing_count"] < 5 else "🟡" if link_analysis["missing_count"] < 15 else "🔴"} |
| **Emotional Anchors** | {len(self.emotional_anchors)} | {"🟢" if len(self.emotional_anchors) > 5 else "🟡" if len(self.emotional_anchors) > 2 else "🔴"} |

---

## 🔍 Component Health Breakdown

| Component | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| **Symbol Vitality** | {health_assessment["component_scores"]["symbol_vitality"]:.3f} | 30% | {health_assessment["component_scores"]["symbol_vitality"] * 0.3:.3f} |
| **Link Integrity** | {health_assessment["component_scores"]["link_integrity"]:.3f} | 25% | {health_assessment["component_scores"]["link_integrity"] * 0.25:.3f} |
| **Emotional Stability** | {health_assessment["component_scores"]["emotional_stability"]:.3f} | 20% | {health_assessment["component_scores"]["emotional_stability"] * 0.2:.3f} |
| **Entropy Coherence** | {health_assessment["component_scores"]["entropy_coherence"]:.3f} | 15% | {health_assessment["component_scores"]["entropy_coherence"] * 0.15:.3f} |
| **Coverage Efficiency** | {health_assessment["component_scores"]["coverage_efficiency"]:.3f} | 10% | {health_assessment["component_scores"]["coverage_efficiency"] * 0.1:.3f} |

---

## 🚨 Stale Symbol Analysis

"""

        if stale_analysis["stale_count"] > 0:
            report += "### Top Stale Symbols\n\n"
            report += "| Symbol | Frequency | Latest Use | Staleness | Sources |\n"
            report += "|--------|-----------|------------|-----------|----------|\n"

            # Sort by staleness score
            stale_items = sorted(
                stale_analysis["stale_symbols"].items(),
                key=lambda x: x[1]["staleness_score"],
                reverse=True,
            )

            for symbol, data in stale_items[:10]:  # Top 10 stale symbols
                latest = data["latest_timestamp"][:10] if data["latest_timestamp"] else "Never"
                sources_count = len(data["sources"])
                report += f"| `{symbol}` | {data['frequency']} | {latest} | {data['staleness_score']:.2f} | {sources_count} |\n"
        else:
            report += "✅ **No stale symbols detected** - all symbols show healthy usage patterns.\n"

        report += "\n---\n\n## 🔗 Missing Link Analysis\n\n"

        if link_analysis["missing_count"] > 0:
            report += "### Broken Symbolic Relationships\n\n"
            report += "| Link | Reason | Symbol 1 Freq | Symbol 2 Freq | Expected | Actual |\n"
            report += "|------|--------|---------------|---------------|----------|--------|\n"

            for link_name, link_data in list(link_analysis["missing_links"].items())[:10]:
                reason = (
                    link_data["missing_reason"][:30] + "..."
                    if len(link_data["missing_reason"]) > 30
                    else link_data["missing_reason"]
                )
                expected = (
                    f"{link_data.get('expected_cooccurrence', 'N/A'):.1f}"
                    if isinstance(link_data.get("expected_cooccurrence"), (int, float))
                    else "N/A"
                )
                report += f"| `{link_name}` | {reason} | {link_data['symbol1_frequency']} | {link_data['symbol2_frequency']} | {expected} | {link_data['actual_cooccurrence']} |\n"
        else:
            report += "✅ **No missing links detected** - symbolic relationships are intact.\n"

        report += "\n---\n\n## 💭 Emotional Anchor Summary\n\n"

        if self.emotional_anchors:
            report += "| Emotional Keyword | Occurrences | Coverage |\n"
            report += "|-------------------|-------------|----------|\n"
            for keyword, occurrences in sorted(self.emotional_anchors.items(), key=lambda x: len(x[1]), reverse=True):
                coverage = len(occurrences) / max(len(self.memory_snapshots), 1) * 100
                report += f"| `{keyword}` | {len(occurrences)} | {coverage:.1f}% |\n"
        else:
            report += "⚠️ **No emotional anchors detected** - memory may lack emotional context.\n"

        report += "\n---\n\n## 🎯 Recommendations\n\n"

        for i, recommendation in enumerate(health_assessment["recommendations"], 1):
            report += f"{i}. {recommendation}\n"

        report += "\n---\n\n**ΛVAULT_TAGS**: `ΛVAULT` `ΛHEALTH` `ΛSCAN` `ΛAUDIT` `AINTEGRITY`\n\n"
        report += f"*Report generated by ΛVAULTSCAN v1.0.0 • CLAUDE-CODE • {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*\n"

        return report


def main():
    """CLI interface for ΛVAULTSCAN"""
    parser = argparse.ArgumentParser(
        description="🩺 ΛVAULTSCAN - Symbolic Vault Health Scanner for LUKHAS AGI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lambda_vault_scan.py --memory-dir memory/ --format markdown
  python3 lambda_vault_scan.py --memory-dir memory/ --format json --out vault_health.json
  python3 lambda_vault_scan.py --memory-dir memory/ --stale-days 60 --frequency-threshold 3
        """,
    )

    parser.add_argument(
        "--memory-dir",
        default="memory/",
        help="Memory directory path (default: memory/)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument("--out", help="Output file path (default: stdout)")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Days threshold for stale symbol detection (default: 30)",
    )
    parser.add_argument(
        "--frequency-threshold",
        type=int,
        default=2,
        help="Minimum frequency threshold (default: 2)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("🩺 ΛVAULTSCAN - Symbolic Vault Health Scanner")
    logger.info("═" * 50)

    try:
        # Initialize scanner
        scanner = SymbolicVaultScanner(args.memory_dir)

        # Load snapshots
        scanner.load_memory_snapshots()

        # Generate report
        report = scanner.export_vault_report(args.format, args.out)

        # Output to stdout if no file specified
        if not args.out:
            logger.info(f"Report content:\n{report}")

        # Log summary
        health_assessment = scanner.assess_vault_health()
        logger.info(f"\n🎯 ΛVAULT_HEALTH_SCORE: {health_assessment['ΛVAULT_HEALTH_SCORE']:.3f}")
        logger.info(f"📊 Status: {health_assessment['health_status']} {health_assessment['health_emoji']}")

        if args.out:
            logger.info(f"📁 Full report saved to: {args.out}")

    except Exception as e:
        logger.error(f"❌ Scanner failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

# CLAUDE CHANGELOG
# - Created ΛVAULTSCAN symbolic vault health scanner with comprehensive memory analysis capabilities # CLAUDE_EDIT_v0.1
# - Implemented all required functions: load_memory_snapshots, detect_stale_symbols, detect_missing_links, assess_vault_health, export_vault_report # CLAUDE_EDIT_v0.2
# - Added CLI interface with argparse for command-line usage # CLAUDE_EDIT_v0.3
# - Integrated ΛTAG pattern recognition and GLYPH symbol extraction from multiple file formats # CLAUDE_EDIT_v0.4