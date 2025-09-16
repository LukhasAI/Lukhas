#!/usr/bin/env python3
"""
LUKHAS Decision Tracker
Track and analyze development decisions with context and rationale
"""

import re
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from .journal_engine import JournalEngine, JournalEntry


class Decision:
    """Represents a development decision with full context"""

    def __init__(
        self,
        title: str,
        rationale: str,
        alternatives: list[str],
        chosen_approach: str,
        expected_outcome: str,
        files_affected: list[str],
        commit_hash: Optional[str] = None,
    ):
        self.title = title
        self.rationale = rationale
        self.alternatives = alternatives
        self.chosen_approach = chosen_approach
        self.expected_outcome = expected_outcome
        self.files_affected = files_affected
        self.commit_hash = commit_hash
        self.timestamp = datetime.now(timezone.utc)
        self.outcome = None  # To be filled later
        self.lessons_learned = None  # To be filled later


class DecisionTracker:
    """
    Track development decisions and their outcomes
    Helps you understand why you made certain choices
    """

    def __init__(self, journal_engine: Optional[JournalEngine] = None):
        self.journal = journal_engine or JournalEngine()
        self.pending_decisions = []
        self.decision_templates = self._load_templates()

    def _load_templates(self) -> dict[str, str]:
        """Load decision templates for common scenarios"""
        return {
            "architecture": """
## Architecture Decision: {title}

### Context
What problem are we trying to solve?

### Decision
{chosen_approach}

### Rationale
{rationale}

### Alternatives Considered
{alternatives}

### Expected Outcome
{expected_outcome}

### Risks
What could go wrong?

### Files Affected
{files_affected}
""",
            "refactoring": """
## Refactoring Decision: {title}

### Current State
What's wrong with the current implementation?

### Proposed Change
{chosen_approach}

### Why Now?
{rationale}

### Impact
{expected_outcome}

### Files Affected
{files_affected}
""",
            "feature": """
## Feature Decision: {title}

### User Need
What user need does this address?

### Implementation Approach
{chosen_approach}

### Why This Way?
{rationale}

### Alternatives
{alternatives}

### Success Criteria
{expected_outcome}
""",
            "bugfix": """
## Bugfix Decision: {title}

### Bug Description
What's broken?

### Root Cause
{rationale}

### Fix Approach
{chosen_approach}

### Prevention
How do we prevent this in the future?

### Affected Areas
{files_affected}
""",
        }

    def track_decision(
        self,
        title: str,
        rationale: str,
        alternatives: Optional[list[str]] = None,
        chosen_approach: Optional[str] = None,
        expected_outcome: Optional[str] = None,
        template: str = "architecture",
    ) -> Decision:
        """Track a new decision"""
        # Get affected files from git
        files_affected = self._get_modified_files()

        # Create decision object
        decision = Decision(
            title=title,
            rationale=rationale,
            alternatives=alternatives or [],
            chosen_approach=chosen_approach or "See implementation",
            expected_outcome=expected_outcome or "Successful implementation",
            files_affected=files_affected,
        )

        # Add to journal
        content = self._format_decision(decision, template)

        # Determine emotional state based on decision type
        emotional_state = self._assess_decision_emotions(decision)

        entry = self.journal.add_entry(
            type="decision",
            content=content,
            metadata={
                "title": title,
                "template": template,
                "files_count": len(files_affected),
                "has_alternatives": len(alternatives) > 0 if alternatives else False,
            },
            tags=self._generate_tags(decision, template),
            emotional_state=emotional_state,
            linked_files=files_affected,
        )

        # Store for later outcome tracking
        self.pending_decisions.append((decision, entry.id))

        return decision

    def _get_modified_files(self) -> list[str]:
        """Get list of modified files from git"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = result.stdout.strip().split("\n") if result.stdout else []

            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            modified_files = result.stdout.strip().split("\n") if result.stdout else []

            all_files = list(set(staged_files + modified_files))
            return [f for f in all_files if f]  # Remove empty strings
        except BaseException:
            return []

    def _format_decision(self, decision: Decision, template: str) -> str:
        """Format decision using template"""
        template_content = self.decision_templates.get(template, self.decision_templates["architecture"])

        return template_content.format(
            title=decision.title,
            rationale=decision.rationale,
            alternatives="\n".join(f"- {alt}" for alt in decision.alternatives),
            chosen_approach=decision.chosen_approach,
            expected_outcome=decision.expected_outcome,
            files_affected="\n".join(f"- {f}" for f in decision.files_affected),
        )

    def _assess_decision_emotions(self, decision: Decision) -> dict[str, float]:
        """Assess emotional state based on decision characteristics"""
        emotions = {
            "confidence": 0.5,
            "curiosity": 0.5,
            "concern": 0.3,
            "excitement": 0.5,
        }

        # Adjust based on decision factors
        if len(decision.alternatives) > 2:
            emotions["curiosity"] += 0.2
            emotions["concern"] += 0.1

        if len(decision.files_affected) > 10:
            emotions["concern"] += 0.2
            emotions["confidence"] -= 0.1

        if "experiment" in decision.title.lower() or "try" in decision.rationale.lower():
            emotions["curiosity"] += 0.3
            emotions["excitement"] += 0.2

        if "fix" in decision.title.lower() or "bug" in decision.title.lower():
            emotions["concern"] += 0.3
            emotions["confidence"] += 0.2

        # Normalize to 0-1 range
        for emotion in emotions:
            emotions[emotion] = min(1.0, max(0.0, emotions[emotion]))

        return emotions

    def _generate_tags(self, decision: Decision, template: str) -> list[str]:
        """Generate relevant tags for the decision"""
        tags = [template, "decision"]

        # Add tags based on title keywords
        keywords = [
            "refactor",
            "feature",
            "bug",
            "architecture",
            "api",
            "ui",
            "performance",
            "security",
        ]
        title_lower = decision.title.lower()
        for keyword in keywords:
            if keyword in title_lower:
                tags.append(keyword)

        # Add tags based on scale
        if len(decision.files_affected) > 20:
            tags.append("major-change")
        elif len(decision.files_affected) > 5:
            tags.append("medium-change")
        else:
            tags.append("minor-change")

        return tags

    def quick_decision(self, message: str) -> Decision:
        """Quick decision capture from commit message or simple input"""
        # Parse message for decision info
        title = message.split("\n")[0].strip()

        # Look for "because" or "to" for rationale
        rationale_match = re.search(r"(because|to|for)\s+(.+)", message, re.IGNORECASE)
        rationale = rationale_match.group(2) if rationale_match else "See commit message"

        return self.track_decision(
            title=title,
            rationale=rationale,
            template=("feature" if "add" in title.lower() or "implement" in title.lower() else "refactoring"),
        )

    def track_outcome(self, decision_id: str, outcome: str, lessons_learned: Optional[str] = None):
        """Track the outcome of a previous decision"""
        # Find the decision
        decision_entry = None
        for dec, entry_id in self.pending_decisions:
            if entry_id == decision_id:
                decision_entry = (dec, entry_id)
                break

        if not decision_entry:
            # Search in journal
            entries = self.journal.search(type="decision")
            for entry in entries:
                if entry.id == decision_id:
                    decision_entry = (None, entry.id)
                    break

        if decision_entry:
            decision, entry_id = decision_entry

            # Create outcome entry
            content = f"""
## Outcome for: {decision.title if decision else "Previous Decision"}

### What Actually Happened
{outcome}

### Lessons Learned
{lessons_learned or "To be determined"}

### Decision Quality Assessment
Was this the right decision? Why or why not?
"""

            self.journal.add_entry(
                type="insight",
                content=content,
                metadata={
                    "decision_id": decision_id,
                    "outcome_type": "decision_outcome",
                },
                tags=["outcome", "learning"],
                emotional_state=self._assess_outcome_emotions(outcome),
            )

    def _assess_outcome_emotions(self, outcome: str) -> dict[str, float]:
        """Assess emotions based on outcome description"""
        emotions = {"satisfaction": 0.5, "surprise": 0.3, "learning": 0.7}

        outcome_lower = outcome.lower()

        # Positive indicators
        if any(word in outcome_lower for word in ["success", "worked", "great", "perfect", "solved"]):
            emotions["satisfaction"] += 0.3

        # Negative indicators
        if any(word in outcome_lower for word in ["failed", "broke", "wrong", "issue", "problem"]):
            emotions["satisfaction"] -= 0.3
            emotions["learning"] += 0.2

        # Surprise indicators
        if any(word in outcome_lower for word in ["unexpected", "surprise", "didn't expect", "turned out"]):
            emotions["surprise"] += 0.3

        # Normalize
        for emotion in emotions:
            emotions[emotion] = min(1.0, max(0.0, emotions[emotion]))

        return emotions

    def analyze_decision_patterns(self, days: int = 30) -> dict[str, Any]:
        """Analyze patterns in recent decisions"""
        # Get recent decisions
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        decisions = self.journal.search(type="decision", date_range=(start_date, datetime.now(timezone.utc)))

        analysis = {
            "total_decisions": len(decisions),
            "decisions_per_day": len(decisions) / days if days > 0 else 0,
            "common_tags": {},
            "decision_complexity": [],
            "emotional_patterns": {},
            "file_change_patterns": [],
            "time_patterns": self._analyze_time_patterns(decisions),
        }

        # Analyze each decision
        tag_counts = {}
        total_emotions = {}
        emotion_counts = {}

        for decision in decisions:
            # Count tags
            for tag in decision.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Analyze complexity (based on metadata)
            if "files_count" in decision.metadata:
                analysis["decision_complexity"].append(decision.metadata["files_count"])

            # Aggregate emotions
            if decision.emotional_vector:
                for emotion, value in decision.emotional_vector.items():
                    total_emotions[emotion] = total_emotions.get(emotion, 0) + value
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate averages
        analysis["common_tags"] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        for emotion, total in total_emotions.items():
            analysis["emotional_patterns"][emotion] = total / emotion_counts[emotion]

        # Find decision hotspots (times when you make most decisions)
        analysis["peak_decision_hours"] = self._find_peak_hours(decisions)

        # Identify rushed decisions (low confidence, high concern)
        analysis["potentially_rushed"] = self._identify_rushed_decisions(decisions)

        return analysis

    def _analyze_time_patterns(self, decisions: list[JournalEntry]) -> dict[str, Any]:
        """Analyze when decisions are made"""
        patterns = {"by_hour": {}, "by_day_of_week": {}, "by_week_of_month": {}}

        for decision in decisions:
            hour = decision.timestamp.hour
            dow = decision.timestamp.strftime("%A")
            week = (decision.timestamp.day - 1) // 7 + 1

            patterns["by_hour"][hour] = patterns["by_hour"].get(hour, 0) + 1
            patterns["by_day_of_week"][dow] = patterns["by_day_of_week"].get(dow, 0) + 1
            patterns["by_week_of_month"][f"Week {week}"] = patterns["by_week_of_month"].get(f"Week {week}", 0) + 1

        return patterns

    def _find_peak_hours(self, decisions: list[JournalEntry]) -> list[int]:
        """Find hours when most decisions are made"""
        hour_counts = {}
        for decision in decisions:
            hour = decision.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        # Sort by count and return top 3 hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]

    def _identify_rushed_decisions(self, decisions: list[JournalEntry]) -> list[str]:
        """Identify potentially rushed decisions based on emotional patterns"""
        rushed = []

        for decision in decisions:
            if decision.emotional_vector:
                confidence = decision.emotional_vector.get("confidence", 0.5)
                concern = decision.emotional_vector.get("concern", 0.5)

                # Low confidence + high concern = potentially rushed
                if confidence < 0.4 and concern > 0.6:
                    rushed.append(decision.metadata.get("title", decision.id))

        return rushed

    def suggest_decision_improvements(self) -> list[str]:
        """Suggest improvements based on decision patterns"""
        analysis = self.analyze_decision_patterns()
        suggestions = []

        # Check decision frequency
        if analysis["decisions_per_day"] < 0.5:
            suggestions.append("Consider documenting more decisions - even small ones help track your thinking")
        elif analysis["decisions_per_day"] > 5:
            suggestions.append("You're making many decisions - consider batching or delegating some")

        # Check for rushed decisions
        if analysis["potentially_rushed"]:
            suggestions.append(
                f"Review these potentially rushed decisions: {', '.join(analysis['potentially_rushed'][:3])}"
            )

        # Check emotional patterns
        emotions = analysis.get("emotional_patterns", {})
        if emotions.get("confidence", 0.5) < 0.5:
            suggestions.append("Your confidence seems low - consider seeking feedback or doing more research")
        if emotions.get("concern", 0.5) > 0.7:
            suggestions.append("High concern levels detected - consider breaking down complex decisions")

        # Check time patterns
        peak_hours = analysis.get("peak_decision_hours", [])
        if peak_hours and all(h >= 22 or h <= 6 for h in peak_hours):
            suggestions.append("You make many decisions late at night - consider revisiting important ones when fresh")

        return suggestions


if __name__ == "__main__":
    # Example usage
    tracker = DecisionTracker()

    # Track a decision
    decision = tracker.track_decision(
        title="Use memory_fold pattern for journal storage",
        rationale="Maintains consistency with LUKHAS architecture and preserves emotional context",
        alternatives=["SQLite database", "Plain JSON files", "MongoDB"],
        chosen_approach="Implement custom memory_fold storage with emotional vectors",
        expected_outcome="Unified storage approach that integrates with existing LUKHAS concepts",
    )

    print(f"Decision tracked: {decision.title}")

    # Quick decision from commit
    quick = tracker.quick_decision(
        "Add decision tracking to journal system because we need to remember why we made choices"
    )
    print(f"Quick decision: {quick.title}")

    # Analyze patterns
    analysis = tracker.analyze_decision_patterns()
    print(f"Decision analysis: {analysis}")

    # Get suggestions
    suggestions = tracker.suggest_decision_improvements()
    print(f"Suggestions: {suggestions}")
