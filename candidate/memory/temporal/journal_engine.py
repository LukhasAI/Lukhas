#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


LUKHAS Journal Engine
Core functionality for learning and knowledge capture
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class JournalEntry:
    """Represents a single journal entry"""

    id: str
    timestamp: datetime
    type: str  # decision, insight, pattern, question, learning
    content: str
    metadata: dict[str, Any]
    tags: list[str]
    emotional_vector: Optional[dict[str, float]] = None
    linked_files: Optional[list[str]] = None
    causal_chain: Optional[list[str]] = None  # Links to other entries


class JournalEngine:
    """
    Core engine for LUKHAS learning journal
    Integrates with LUKHAS concepts like memory_fold and emotional_vectors
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.home() / ".claude" / "journal"
        self.config_path = Path.home() / ".claude" / "config.yaml"
        self._ensure_directories()
        self.config = self._load_config()
        self.current_session = []

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.base_path,
            self.base_path / "decisions",
            self.base_path / "insights",
            self.base_path / "patterns",
            self.base_path / "questions",
            self.base_path / "knowledge",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from Claude config"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Default configuration if no config file exists"""
        return {
            "lukhas_learning": {
                "journal": {
                    "auto_capture": True,
                    "prompt_on_significant_changes": True,
                },
                "storage": {"format": "json", "compress_old_entries": True},
            }
        }

    def _generate_entry_id(self, content: str, timestamp: datetime) -> str:
        """Generate unique ID for entry using LUKHAS-style hashing"""
        data = f"{content}{timestamp.isoformat()}"
        return f"JE_{hashlib.sha256(data.encode()).hexdigest()}[:12]}"  # noqa: invalid-syntax  # TODO: f-string: single } is not allo...

    def add_entry(
        self,
        type: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        emotional_state: Optional[dict[str, float]] = None,
        linked_files: Optional[list[str]] = None,
    ) -> JournalEntry:
        """Add a new entry to the journal"""
        timestamp = datetime.now(timezone.utc)
        entry_id = self._generate_entry_id(content, timestamp)

        entry = JournalEntry(
            id=entry_id,
            timestamp=timestamp,
            type=type,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            emotional_vector=emotional_state,
            linked_files=linked_files,
        )

        # Add LUKHAS consciousness level if available
        if emotional_state:
            entry.metadata["consciousness_level"] = self._calculate_consciousness_level(
                emotional_state
            )

        # Save entry
        self._save_entry(entry)
        self.current_session.append(entry)

        # Create causal chains if this relates to previous entries
        self._update_causal_chains(entry)

        return entry

    def _calculate_consciousness_level(
        self, emotional_state: dict[str, float]
    ) -> float:
        """Calculate consciousness level from emotional state (LUKHAS concept)"""
        # Simple average for now, can be made more sophisticated
        if not emotional_state:
            return 0.5
        return sum(emotional_state.values()) / len(emotional_state)

    def _save_entry(self, entry: JournalEntry):
        """Save entry to appropriate directory"""
        directory = self.base_path / f"{entry.type}s"
        directory.mkdir(exist_ok=True)

        # Create filename with date for easy browsing
        date_str = entry.timestamp.strftime("%Y-%m-%d")
        filename = f"{date_str}_{entry.id}.json"
        filepath = directory / filename

        # Convert to dict and save
        entry_dict = asdict(entry)
        entry_dict["timestamp"] = entry.timestamp.isoformat()

        with open(filepath, "w") as f:
            json.dump(entry_dict, f, indent=2)

    def _update_causal_chains(self, entry: JournalEntry):
        """Update causal chains between related entries"""
        # Look for related entries in current session
        for previous_entry in self.current_session[-10:]:  # Last 10 entries
            if self._entries_related(previous_entry, entry):
                if entry.causal_chain is None:
                    entry.causal_chain = []
                entry.causal_chain.append(previous_entry.id)

    def _entries_related(self, entry1: JournalEntry, entry2: JournalEntry) -> bool:
        """Determine if two entries are related"""
        # Check for common tags
        common_tags = set(entry1.tags) & set(entry2.tags)
        if common_tags:
            return True

        # Check for file overlap
        if entry1.linked_files and entry2.linked_files:
            common_files = set(entry1.linked_files) & set(entry2.linked_files)
            if common_files:
                return True

        # Check time proximity (within 1 hour)
        time_diff = abs((entry2.timestamp - entry1.timestamp).total_seconds())
        if time_diff < 3600:  # 1 hour
            return True

        return False

    def search(
        self,
        query: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        date_range: Optional[tuple] = None,
        emotional_range: Optional[dict[str, tuple]] = None,
    ) -> list[JournalEntry]:
        """Search journal entries with various filters"""
        results = []

        # Determine which directories to search
        if type:
            search_dirs = [self.base_path / f"{type}s"]
        else:
            search_dirs = [
                self.base_path / "decisions",
                self.base_path / "insights",
                self.base_path / "patterns",
                self.base_path / "questions",
            ]

        for directory in search_dirs:
            if not directory.exists():
                continue

            for filepath in directory.glob("*.json"):
                with open(filepath) as f:
                    entry_dict = json.load(f)

                # Convert back to JournalEntry
                entry_dict["timestamp"] = datetime.fromisoformat(
                    entry_dict["timestamp"]
                )
                entry = JournalEntry(**entry_dict)

                # Apply filters
                if not self._matches_filters(
                    entry, query, tags, date_range, emotional_range
                ):
                    continue

                results.append(entry)

        # Sort by timestamp
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results

    def _matches_filters(
        self,
        entry: JournalEntry,
        query: Optional[str],
        tags: Optional[list[str]],
        date_range: Optional[tuple],
        emotional_range: Optional[dict[str, tuple]],
    ) -> bool:
        """Check if entry matches all filters"""
        # Query filter
        if query and query.lower() not in entry.content.lower():
            return False

        # Tag filter
        if tags:
            entry_tags = set(entry.tags)
            required_tags = set(tags)
            if not required_tags.issubset(entry_tags):
                return False

        # Date range filter
        if date_range:
            start_date, end_date = date_range
            if not (start_date <= entry.timestamp <= end_date):
                return False

        # Emotional range filter
        if emotional_range and entry.emotional_vector:
            for emotion, (min_val, max_val) in emotional_range.items():
                if emotion in entry.emotional_vector:
                    val = entry.emotional_vector[emotion]
                    if not (min_val <= val <= max_val):
                        return False

        return True

    def get_daily_summary(self, date: Optional[datetime] = None) -> dict[str, Any]:
        """Get summary of journal entries for a specific day"""
        if date is None:
            date = datetime.now(timezone.utc)

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        entries = self.search(date_range=(start_of_day, end_of_day))

        summary = {
            "date": date.strftime("%Y-%m-%d"),
            "total_entries": len(entries),
            "entries_by_type": {},
            "tags": set(),
            "emotional_journey": [],
            "key_decisions": [],
            "insights": [],
            "questions": [],
        }

        for entry in entries:
            # Count by type
            entry_type = entry.type
            summary["entries_by_type"][entry_type] = (
                summary["entries_by_type"].get(entry_type, 0) + 1
            )

            # Collect tags
            summary["tags"].update(entry.tags)

            # Track emotional journey
            if entry.emotional_vector:
                summary["emotional_journey"].append(
                    {
                        "time": entry.timestamp.strftime("%H:%M"),
                        "emotions": entry.emotional_vector,
                    }
                )

            # Collect key content
            if entry.type == "decision":
                summary["key_decisions"].append(entry.content[:100] + "...")
            elif entry.type == "insight":
                summary["insights"].append(entry.content[:100] + "...")
            elif entry.type == "question":
                summary["questions"].append(entry.content)

        summary["tags"] = list(summary["tags"])
        return summary

    def create_memory_fold(self, entries: list[JournalEntry]) -> dict[str, Any]:
        """
        Create a LUKHAS-style memory fold from journal entries
        This preserves the emotional context and causal relationships
        """
        if not entries:
            return {}

        memory_fold = {
            "fold_id": f"MF_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
            "time_span": {
                "start": min(e.timestamp for e in entries).isoformat(),
                "end": max(e.timestamp for e in entries).isoformat(),
            },
            "emotional_trajectory": self._calculate_emotional_trajectory(entries),
            "causal_network": self._build_causal_network(entries),
            "key_learnings": self._extract_key_learnings(entries),
            "consciousness_evolution": self._track_consciousness_evolution(entries),
        }

        return memory_fold

    def _calculate_emotional_trajectory(
        self, entries: list[JournalEntry]
    ) -> list[dict[str, Any]]:
        """Calculate how emotions evolved over time"""
        trajectory = []

        for entry in entries:
            if entry.emotional_vector:
                trajectory.append(
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "emotions": entry.emotional_vector,
                        "dominant_emotion": max(
                            entry.emotional_vector.items(), key=lambda x: x[1]
                        )[0],
                    }
                )

        return trajectory

    def _build_causal_network(
        self, entries: list[JournalEntry]
    ) -> dict[str, list[str]]:
        """Build network of causal relationships"""
        network = {}

        for entry in entries:
            if entry.causal_chain:
                network[entry.id] = entry.causal_chain

        return network

    def _extract_key_learnings(self, entries: list[JournalEntry]) -> list[str]:
        """Extract key learnings from insights and patterns"""
        learnings = []

        for entry in entries:
            if entry.type in ["insight", "learning"]:
                # Simple extraction for now - can be made more sophisticated
                learnings.append(entry.content)

        return learnings[:10]  # Top 10 learnings

    def _track_consciousness_evolution(
        self, entries: list[JournalEntry]
    ) -> list[dict[str, Any]]:
        """Track how consciousness level evolved"""
        evolution = []

        for entry in entries:
            if "consciousness_level" in entry.metadata:
                evolution.append(
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "level": entry.metadata["consciousness_level"],
                        "entry_type": entry.type,
                    }
                )

        return evolution

    def export_to_markdown(self, entries: list[JournalEntry], output_path: Path):
        """Export journal entries to markdown format"""
        content = ["# LUKHAS Learning Journal\n"]

        # Group by date
        entries_by_date = {}
        for entry in entries:
            date_key = entry.timestamp.strftime("%Y-%m-%d")
            if date_key not in entries_by_date:
                entries_by_date[date_key] = []
            entries_by_date[date_key].append(entry)

        # Write each day
        for date_key in sorted(entries_by_date.keys(), reverse=True):
            content.append(f"\n#")

            for entry in entries_by_date[date_key]:
                content.append(
                    f"##"%H:%M')} - {entry.type.title()}\n"'  # noqa: invalid-syntax  # TODO: Expected ,, found :
                )
                content.append(f"{entry.content}\n")

                if entry.tags:
                    content.append(f"**Tags**: {', '.join(entry.tags)}\n")

                if entry.emotional_vector:
                    emotions = ", ".join(
                        f"{k}: {v:.2f}" for k, v in entry.emotional_vector.items()
                    )
                    content.append(f"**Emotional State**: {emotions}\n")

                content.append("\n---\n")

        with open(output_path, "w") as f:
            f.write("\n".join(content))

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about journal usage"""
        stats = {
            "total_entries": 0,
            "entries_by_type": {},
            "most_used_tags": {},
            "emotional_summary": {},
            "average_daily_entries": 0,
            "streak": self._calculate_streak(),
        }

        # Collect all entries
        all_entries = self.search()
        stats["total_entries"] = len(all_entries)

        # Analyze entries
        tag_counts = {}
        emotion_sums = {}
        emotion_counts = {}

        for entry in all_entries:
            # Count by type
            stats["entries_by_type"][entry.type] = (
                stats["entries_by_type"].get(entry.type, 0) + 1
            )

            # Count tags
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Sum emotions
            if entry.emotional_vector:
                for emotion, value in entry.emotional_vector.items():
                    emotion_sums[emotion] = emotion_sums.get(emotion, 0) + value
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate most used tags
        stats["most_used_tags"] = dict(
            sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Calculate average emotions
        for emotion, total in emotion_sums.items():
            stats["emotional_summary"][emotion] = total / emotion_counts[emotion]

        # Calculate average daily entries
        if all_entries:
            date_range = (all_entries[-1].timestamp, all_entries[0].timestamp)
            days = (date_range[1] - date_range[0]).days + 1
            stats["average_daily_entries"] = len(all_entries) / days

        return stats

    def _calculate_streak(self) -> int:
        """Calculate current journaling streak in days"""
        today = datetime.now(timezone.utc).date()
        streak = 0

        while True:
            check_date = today - timedelta(days=streak)
            entries = self.search(
                date_range=(
                    datetime.combine(check_date, datetime.min.time()),
                    datetime.combine(check_date, datetime.max.time()),
                )
            )

            if not entries:
                break

            streak += 1

        return streak


if __name__ == "__main__":
    # Example usage
    journal = JournalEngine()

    # Add a decision
    entry = journal.add_entry(
        type="decision",
        content="Decided to use memory_fold pattern for journal storage to maintain consistency with LUKHAS architecture",
        tags=["architecture", "memory_fold"],
        emotional_state={"confidence": 0.8, "curiosity": 0.9},
    )

    print(f"Created entry: {entry.id}")

    # Get daily summary
    summary = journal.get_daily_summary()
    print(f"Today's summary: {summary}")
