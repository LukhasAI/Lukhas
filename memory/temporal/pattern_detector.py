#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


LUKHAS Pattern Detector
Identify repeated behaviors and suggest improvements
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import json
from pathlib import Path
import subprocess
import difflib

from .journal_engine import JournalEngine, JournalEntry

class Pattern:
    """Represents a detected pattern in development behavior"""
    
    def __init__(
        self,
        pattern_type: str,
        description: str,
        occurrences: List[Dict[str, Any]],
        frequency: str,  # daily, weekly, sporadic
        impact: str,  # positive, negative, neutral
        automation_potential: bool,
        suggested_action: Optional[str] = None
    ):
        self.pattern_type = pattern_type
        self.description = description
        self.occurrences = occurrences
        self.frequency = frequency
        self.impact = impact
        self.automation_potential = automation_potential
        self.suggested_action = suggested_action
        self.first_seen = min(o["timestamp"] for o in occurrences)
        self.last_seen = max(o["timestamp"] for o in occurrences)

class PatternDetector:
    """
    Detect patterns in your development behavior
    Suggests automations and improvements
    """
    
    def __init__(self, journal_engine: Optional[JournalEngine] = None):
        self.journal = journal_engine or JournalEngine()
        self.pattern_types = {
            "code_pattern": self._detect_code_patterns,
            "time_pattern": self._detect_time_patterns,
            "error_pattern": self._detect_error_patterns,
            "workflow_pattern": self._detect_workflow_patterns,
            "decision_pattern": self._detect_decision_patterns,
            "emotional_pattern": self._detect_emotional_patterns,
            "file_pattern": self._detect_file_patterns,
            "tool_usage": self._detect_tool_usage_patterns
        }
        self.detected_patterns = []
    
    def detect_all_patterns(self, days: int = 30) -> List[Pattern]:
        """Detect all types of patterns in recent activity"""
        self.detected_patterns = []
        
        # Get recent entries
        start_date = datetime.now() - timedelta(days=days)
        entries = self.journal.search(date_range=(start_date, datetime.now()))
        
        # Get git history for code patterns
        git_history = self._get_git_history(days)
        
        # Run all pattern detectors
        for pattern_type, detector_func in self.pattern_types.items():
            patterns = detector_func(entries, git_history)
            self.detected_patterns.extend(patterns)
        
        # Sort by frequency and impact
        self.detected_patterns.sort(
            key=lambda p: (self._impact_score(p.impact), len(p.occurrences)), 
            reverse=True
        )
        
        return self.detected_patterns
    
    def _impact_score(self, impact: str) -> int:
        """Convert impact to numeric score for sorting"""
        return {"negative": 3, "neutral": 2, "positive": 1}.get(impact, 0)
    
    def _get_git_history(self, days: int) -> List[Dict[str, Any]]:
        """Get git commit history for pattern analysis"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            result = subprocess.run(
                ["git", "log", f"--since={since_date}", "--pretty=format:%H|%ai|%s|%an", "--name-status"],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            current_commit = None
            
            for line in result.stdout.split('\n'):
                if '|' in line:
                    # New commit
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split('|')
                    current_commit = {
                        "hash": parts[0],
                        "timestamp": datetime.fromisoformat(parts[1].split()[0] + " " + parts[1].split()[1]),
                        "message": parts[2],
                        "author": parts[3],
                        "files": []
                    }
                elif line.strip() and current_commit:
                    # File change
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        current_commit["files"].append({
                            "action": parts[0],
                            "path": parts[1]
                        })
            
            if current_commit:
                commits.append(current_commit)
            
            return commits
        except:
            return []
    
    def _detect_code_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in code changes"""
        patterns = []
        
        # Pattern 1: Repeated file modifications
        file_modifications = Counter()
        for commit in git_history:
            for file_info in commit["files"]:
                if file_info["action"] == "M":  # Modified
                    file_modifications[file_info["path"]] += 1
        
        # Find files modified frequently
        hot_files = []
        for file_path, count in file_modifications.most_common(10):
            if count >= 5:  # Modified 5+ times
                occurrences = [
                    {
                        "timestamp": c["timestamp"],
                        "context": f"Modified in: {c['message']}"
                    }
                    for c in git_history
                    if any(f["path"] == file_path and f["action"] == "M" for f in c["files"])
                ]
                
                pattern = Pattern(
                    pattern_type="code_pattern",
                    description=f"Frequently modified file: {file_path}",
                    occurrences=occurrences,
                    frequency="daily" if count > days * 0.3 else "weekly",
                    impact="negative" if count > days * 0.5 else "neutral",
                    automation_potential=True,
                    suggested_action=f"Consider refactoring {file_path} for stability"
                )
                patterns.append(pattern)
        
        # Pattern 2: Similar commit messages
        message_patterns = defaultdict(list)
        for commit in git_history:
            # Extract pattern from message (e.g., "Fix ...", "Add ...", "Update ...")
            match = re.match(r'^(\w+)\s+', commit["message"])
            if match:
                prefix = match.group(1).lower()
                message_patterns[prefix].append(commit)
        
        for prefix, commits in message_patterns.items():
            if len(commits) >= 5:
                occurrences = [
                    {
                        "timestamp": c["timestamp"],
                        "context": c["message"]
                    }
                    for c in commits[:10]  # First 10 examples
                ]
                
                pattern = Pattern(
                    pattern_type="code_pattern",
                    description=f"Repeated commit pattern: '{prefix}' ({len(commits)} times)",
                    occurrences=occurrences,
                    frequency="daily" if len(commits) > days * 0.2 else "weekly",
                    impact="neutral",
                    automation_potential=True,
                    suggested_action=f"Create commit template for '{prefix}' commits"
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_time_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in when you work"""
        patterns = []
        
        # Combine journal entries and git commits for time analysis
        all_timestamps = []
        all_timestamps.extend([(e.timestamp, "journal") for e in entries])
        all_timestamps.extend([(c["timestamp"], "commit") for c in git_history])
        
        # Analyze by hour
        hour_activity = Counter()
        day_activity = Counter()
        
        for timestamp, activity_type in all_timestamps:
            hour_activity[timestamp.hour] += 1
            day_activity[timestamp.strftime("%A")] += 1
        
        # Find peak hours
        peak_hours = hour_activity.most_common(3)
        if peak_hours and peak_hours[0][1] > len(all_timestamps) * 0.2:
            occurrences = [
                {
                    "timestamp": ts,
                    "context": f"{activity_type} at {ts.strftime('%H:%M')}"
                }
                for ts, activity_type in all_timestamps
                if ts.hour == peak_hours[0][0]
            ][:20]  # Sample of 20
            
            pattern = Pattern(
                pattern_type="time_pattern",
                description=f"Peak productivity hour: {peak_hours[0][0]}:00-{peak_hours[0][0]+1}:00",
                occurrences=occurrences,
                frequency="daily",
                impact="positive",
                automation_potential=False,
                suggested_action=f"Schedule important work during {peak_hours[0][0]}:00"
            )
            patterns.append(pattern)
        
        # Find late night coding
        late_night_work = sum(hour_activity[h] for h in range(22, 24)) + sum(hour_activity[h] for h in range(0, 6))
        if late_night_work > len(all_timestamps) * 0.2:
            occurrences = [
                {
                    "timestamp": ts,
                    "context": f"{activity_type} at {ts.strftime('%H:%M')}"
                }
                for ts, activity_type in all_timestamps
                if ts.hour >= 22 or ts.hour < 6
            ][:20]
            
            pattern = Pattern(
                pattern_type="time_pattern",
                description="Frequent late-night work detected",
                occurrences=occurrences,
                frequency="weekly",
                impact="negative",
                automation_potential=False,
                suggested_action="Consider shifting work to daytime for better decision-making"
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_error_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in errors and failures"""
        patterns = []
        
        # Look for failure/error entries
        error_entries = [
            e for e in entries 
            if e.metadata.get("category") in ["failure", "challenge"] or 
            any(word in e.content.lower() for word in ["error", "failed", "broke", "bug", "issue"])
        ]
        
        # Group errors by type
        error_types = defaultdict(list)
        for entry in error_entries:
            # Simple error categorization
            content_lower = entry.content.lower()
            if "import" in content_lower:
                error_types["import_errors"].append(entry)
            elif "type" in content_lower or "typescript" in content_lower:
                error_types["type_errors"].append(entry)
            elif "test" in content_lower:
                error_types["test_failures"].append(entry)
            elif "memory" in content_lower or "performance" in content_lower:
                error_types["performance_issues"].append(entry)
            else:
                error_types["general_errors"].append(entry)
        
        # Create patterns for repeated error types
        for error_type, entries in error_types.items():
            if len(entries) >= 3:
                occurrences = [
                    {
                        "timestamp": e.timestamp,
                        "context": e.content[:100]
                    }
                    for e in entries[:10]
                ]
                
                pattern = Pattern(
                    pattern_type="error_pattern",
                    description=f"Recurring {error_type.replace('_', ' ')}: {len(entries)} occurrences",
                    occurrences=occurrences,
                    frequency="weekly",
                    impact="negative",
                    automation_potential=True,
                    suggested_action=self._suggest_error_fix(error_type)
                )
                patterns.append(pattern)
        
        return patterns
    
    def _suggest_error_fix(self, error_type: str) -> str:
        """Suggest fix for common error types"""
        suggestions = {
            "import_errors": "Set up import aliases and run import fixer tool",
            "type_errors": "Enable strict TypeScript checking and fix incrementally",
            "test_failures": "Set up pre-commit test hooks",
            "performance_issues": "Add performance monitoring and profiling",
            "general_errors": "Improve error handling and logging"
        }
        return suggestions.get(error_type, "Analyze root cause and implement preventive measures")
    
    def _detect_workflow_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in development workflow"""
        patterns = []
        
        # Pattern 1: Decision to implementation time
        decisions = [e for e in entries if e.type == "decision"]
        
        decision_implementation_times = []
        for decision in decisions:
            # Look for related commits after decision
            decision_files = set(decision.linked_files or [])
            if decision_files:
                for commit in git_history:
                    if commit["timestamp"] > decision.timestamp:
                        commit_files = {f["path"] for f in commit["files"]}
                        if decision_files & commit_files:  # Intersection
                            time_to_implement = commit["timestamp"] - decision.timestamp
                            decision_implementation_times.append({
                                "decision": decision.metadata.get("title", "Unknown"),
                                "time": time_to_implement,
                                "timestamp": decision.timestamp
                            })
                            break
        
        if len(decision_implementation_times) >= 3:
            avg_time = sum(d["time"].total_seconds() for d in decision_implementation_times) / len(decision_implementation_times)
            
            occurrences = [
                {
                    "timestamp": d["timestamp"],
                    "context": f"{d['decision']} took {d['time'].days} days to implement"
                }
                for d in decision_implementation_times
            ]
            
            pattern = Pattern(
                pattern_type="workflow_pattern",
                description=f"Average decision to implementation: {avg_time / 86400:.1f} days",
                occurrences=occurrences,
                frequency="weekly",
                impact="neutral",
                automation_potential=False,
                suggested_action="Track implementation progress more closely" if avg_time > 259200 else None  # 3 days
            )
            patterns.append(pattern)
        
        # Pattern 2: Context switching
        daily_topics = defaultdict(set)
        for entry in entries:
            day = entry.timestamp.date()
            daily_topics[day].update(entry.tags)
        
        high_switch_days = []
        for day, topics in daily_topics.items():
            if len(topics) > 5:  # Many different topics in one day
                high_switch_days.append({
                    "timestamp": datetime.combine(day, datetime.min.time()),
                    "topics": topics
                })
        
        if len(high_switch_days) >= 3:
            occurrences = [
                {
                    "timestamp": d["timestamp"],
                    "context": f"Worked on {len(d['topics'])} different topics: {', '.join(list(d['topics'])[:3])}..."
                }
                for d in high_switch_days[:10]
            ]
            
            pattern = Pattern(
                pattern_type="workflow_pattern",
                description="Frequent context switching detected",
                occurrences=occurrences,
                frequency="weekly",
                impact="negative",
                automation_potential=False,
                suggested_action="Try time-blocking to reduce context switches"
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_decision_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in decision-making"""
        patterns = []
        
        decisions = [e for e in entries if e.type == "decision"]
        
        # Pattern 1: Decisions without alternatives
        no_alternatives = []
        for decision in decisions:
            if not decision.metadata.get("has_alternatives", True):
                no_alternatives.append(decision)
        
        if len(no_alternatives) >= 5:
            occurrences = [
                {
                    "timestamp": d.timestamp,
                    "context": d.metadata.get("title", "Decision")
                }
                for d in no_alternatives[:10]
            ]
            
            pattern = Pattern(
                pattern_type="decision_pattern",
                description="Often making decisions without considering alternatives",
                occurrences=occurrences,
                frequency="weekly",
                impact="negative",
                automation_potential=False,
                suggested_action="Use decision template that prompts for alternatives"
            )
            patterns.append(pattern)
        
        # Pattern 2: Rushed decisions (based on emotional state)
        rushed_decisions = []
        for decision in decisions:
            if decision.emotional_vector:
                confidence = decision.emotional_vector.get("confidence", 0.5)
                concern = decision.emotional_vector.get("concern", 0.5)
                if confidence < 0.4 and concern > 0.6:
                    rushed_decisions.append(decision)
        
        if len(rushed_decisions) >= 3:
            occurrences = [
                {
                    "timestamp": d.timestamp,
                    "context": f"{d.metadata.get('title', 'Decision')} - Low confidence"
                }
                for d in rushed_decisions
            ]
            
            pattern = Pattern(
                pattern_type="decision_pattern",
                description="Pattern of low-confidence decisions",
                occurrences=occurrences,
                frequency="weekly",
                impact="negative",
                automation_potential=False,
                suggested_action="Take more time for research before deciding"
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_emotional_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in emotional states"""
        patterns = []
        
        # Collect entries with emotional data
        emotional_entries = [e for e in entries if e.emotional_vector]
        
        if not emotional_entries:
            return patterns
        
        # Pattern 1: Emotional cycles
        daily_emotions = defaultdict(list)
        for entry in emotional_entries:
            day = entry.timestamp.strftime("%A")
            daily_emotions[day].extend(entry.emotional_vector.items())
        
        # Calculate average emotions by day
        day_patterns = {}
        for day, emotions in daily_emotions.items():
            emotion_sums = defaultdict(float)
            emotion_counts = defaultdict(int)
            
            for emotion, value in emotions:
                emotion_sums[emotion] += value
                emotion_counts[emotion] += 1
            
            day_patterns[day] = {
                emotion: emotion_sums[emotion] / emotion_counts[emotion]
                for emotion in emotion_sums
            }
        
        # Find days with distinct patterns
        for day, avg_emotions in day_patterns.items():
            if avg_emotions:
                dominant_emotion = max(avg_emotions.items(), key=lambda x: x[1])
                if dominant_emotion[1] > 0.7:  # Strong pattern
                    occurrences = [
                        {
                            "timestamp": e.timestamp,
                            "context": f"{dominant_emotion[0]}: {e.emotional_vector.get(dominant_emotion[0], 0):.2f}"
                        }
                        for e in emotional_entries
                        if e.timestamp.strftime("%A") == day and dominant_emotion[0] in e.emotional_vector
                    ][:10]
                    
                    pattern = Pattern(
                        pattern_type="emotional_pattern",
                        description=f"{day}s tend to be {dominant_emotion[0]} days",
                        occurrences=occurrences,
                        frequency="weekly",
                        impact="neutral",
                        automation_potential=False,
                        suggested_action=f"Plan accordingly for {dominant_emotion[0]} on {day}s"
                    )
                    patterns.append(pattern)
        
        # Pattern 2: Emotional triggers
        # Look for patterns in what causes certain emotions
        for emotion in ["frustration", "excitement", "concern"]:
            emotion_triggers = []
            for entry in emotional_entries:
                if entry.emotional_vector.get(emotion, 0) > 0.7:
                    emotion_triggers.append(entry)
            
            if len(emotion_triggers) >= 5:
                # Find common words in triggers
                word_counts = Counter()
                for entry in emotion_triggers:
                    words = entry.content.lower().split()
                    word_counts.update(words)
                
                # Find common trigger words
                common_words = [word for word, count in word_counts.most_common(20) 
                               if count >= 3 and len(word) > 4]
                
                if common_words:
                    occurrences = [
                        {
                            "timestamp": e.timestamp,
                            "context": e.content[:100]
                        }
                        for e in emotion_triggers[:10]
                    ]
                    
                    pattern = Pattern(
                        pattern_type="emotional_pattern",
                        description=f"Common {emotion} triggers: {', '.join(common_words[:5])}",
                        occurrences=occurrences,
                        frequency="weekly",
                        impact="negative" if emotion in ["frustration", "concern"] else "positive",
                        automation_potential=False,
                        suggested_action=f"Be aware of {emotion} triggers and prepare coping strategies"
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_file_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in file operations"""
        patterns = []
        
        # Pattern 1: File creation patterns
        created_files = []
        for commit in git_history:
            for file_info in commit["files"]:
                if file_info["action"] == "A":  # Added
                    created_files.append({
                        "path": file_info["path"],
                        "timestamp": commit["timestamp"],
                        "message": commit["message"]
                    })
        
        # Group by directory
        dir_creates = defaultdict(list)
        for file_data in created_files:
            directory = str(Path(file_data["path"]).parent)
            dir_creates[directory].append(file_data)
        
        for directory, files in dir_creates.items():
            if len(files) >= 5:
                occurrences = [
                    {
                        "timestamp": f["timestamp"],
                        "context": f"Created {Path(f['path']).name}"
                    }
                    for f in files[:10]
                ]
                
                pattern = Pattern(
                    pattern_type="file_pattern",
                    description=f"Frequently creating files in {directory}",
                    occurrences=occurrences,
                    frequency="weekly",
                    impact="neutral",
                    automation_potential=True,
                    suggested_action=f"Create file templates for {directory}"
                )
                patterns.append(pattern)
        
        # Pattern 2: File naming patterns
        file_names = [Path(f["path"]).name for f in created_files]
        
        # Look for common prefixes/suffixes
        prefix_counts = Counter()
        suffix_counts = Counter()
        
        for name in file_names:
            # Check prefixes
            for i in range(3, min(len(name), 10)):
                prefix = name[:i]
                if sum(1 for n in file_names if n.startswith(prefix)) >= 3:
                    prefix_counts[prefix] += 1
            
            # Check suffixes (before extension)
            name_without_ext = Path(name).stem
            for i in range(3, min(len(name_without_ext), 10)):
                suffix = name_without_ext[-i:]
                if sum(1 for n in file_names if Path(n).stem.endswith(suffix)) >= 3:
                    suffix_counts[suffix] += 1
        
        # Report common patterns
        common_prefixes = [p for p, c in prefix_counts.most_common(3) if c >= 3]
        if common_prefixes:
            examples = [f for f in created_files if Path(f["path"]).name.startswith(common_prefixes[0])]
            occurrences = [
                {
                    "timestamp": e["timestamp"],
                    "context": Path(e["path"]).name
                }
                for e in examples[:10]
            ]
            
            pattern = Pattern(
                pattern_type="file_pattern",
                description=f"Common file prefix pattern: '{common_prefixes[0]}'",
                occurrences=occurrences,
                frequency="weekly",
                impact="neutral",
                automation_potential=True,
                suggested_action="Create naming convention guide or file generator"
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_tool_usage_patterns(self, entries: List[JournalEntry], git_history: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in tool and command usage"""
        patterns = []
        
        # Look for tool mentions in entries
        tool_mentions = defaultdict(list)
        tools = ["git", "npm", "pip", "docker", "pytest", "eslint", "black", "mypy", "webpack", "vite"]
        
        for entry in entries:
            content_lower = entry.content.lower()
            for tool in tools:
                if tool in content_lower:
                    tool_mentions[tool].append(entry)
        
        # Find frequently used tools
        for tool, mentions in tool_mentions.items():
            if len(mentions) >= 5:
                occurrences = [
                    {
                        "timestamp": m.timestamp,
                        "context": m.content[:100]
                    }
                    for m in mentions[:10]
                ]
                
                # Check if tool usage is often associated with problems
                problem_mentions = [m for m in mentions if any(
                    word in m.content.lower() 
                    for word in ["error", "failed", "issue", "problem"]
                )]
                
                impact = "negative" if len(problem_mentions) > len(mentions) * 0.5 else "neutral"
                
                pattern = Pattern(
                    pattern_type="tool_usage",
                    description=f"Frequent {tool} usage ({len(mentions)} mentions)",
                    occurrences=occurrences,
                    frequency="daily" if len(mentions) > days * 0.3 else "weekly",
                    impact=impact,
                    automation_potential=True,
                    suggested_action=f"Create {tool} aliases or automation scripts" if impact == "negative" else None
                )
                patterns.append(pattern)
        
        return patterns
    
    def suggest_automations(self) -> List[Dict[str, Any]]:
        """Suggest specific automations based on detected patterns"""
        if not self.detected_patterns:
            self.detect_all_patterns()
        
        automations = []
        
        for pattern in self.detected_patterns:
            if pattern.automation_potential and pattern.impact in ["negative", "neutral"]:
                automation = {
                    "pattern": pattern.description,
                    "impact": pattern.impact,
                    "frequency": pattern.frequency,
                    "automation_type": self._determine_automation_type(pattern),
                    "implementation": self._suggest_implementation(pattern),
                    "estimated_time_saved": self._estimate_time_saved(pattern),
                    "priority": self._calculate_priority(pattern)
                }
                automations.append(automation)
        
        # Sort by priority
        automations.sort(key=lambda a: a["priority"], reverse=True)
        
        return automations
    
    def _determine_automation_type(self, pattern: Pattern) -> str:
        """Determine what type of automation would help"""
        if "file" in pattern.pattern_type:
            return "file_template"
        elif "error" in pattern.pattern_type:
            return "validation_hook"
        elif "code_pattern" in pattern.pattern_type:
            if "commit" in pattern.description:
                return "commit_template"
            else:
                return "code_snippet"
        elif "tool" in pattern.pattern_type:
            return "cli_alias"
        else:
            return "workflow_automation"
    
    def _suggest_implementation(self, pattern: Pattern) -> str:
        """Suggest specific implementation for automation"""
        automation_type = self._determine_automation_type(pattern)
        
        implementations = {
            "file_template": "Create file templates using cookiecutter or custom generator",
            "validation_hook": "Add pre-commit hooks for validation",
            "commit_template": "Set up git commit templates with conventional commits",
            "code_snippet": "Create IDE snippets or code generators",
            "cli_alias": "Add shell aliases or create wrapper scripts",
            "workflow_automation": "Use task runners like Make or Just"
        }
        
        return implementations.get(automation_type, "Analyze pattern and create custom automation")
    
    def _estimate_time_saved(self, pattern: Pattern) -> str:
        """Estimate time that could be saved with automation"""
        occurrences_per_week = len(pattern.occurrences) / 4  # Rough estimate
        
        # Estimate time per occurrence based on pattern type
        time_per_occurrence = {
            "file_pattern": 5,  # 5 minutes to create and set up a file
            "error_pattern": 15,  # 15 minutes to debug and fix
            "code_pattern": 3,  # 3 minutes for repetitive code
            "tool_usage": 2,  # 2 minutes for tool commands
        }.get(pattern.pattern_type, 5)
        
        weekly_time = occurrences_per_week * time_per_occurrence
        
        if weekly_time < 30:
            return f"~{weekly_time:.0f} minutes/week"
        else:
            return f"~{weekly_time/60:.1f} hours/week"
    
    def _calculate_priority(self, pattern: Pattern) -> int:
        """Calculate automation priority (0-100)"""
        base_score = 50
        
        # Adjust for impact
        if pattern.impact == "negative":
            base_score += 30
        elif pattern.impact == "neutral":
            base_score += 10
        
        # Adjust for frequency
        if pattern.frequency == "daily":
            base_score += 20
        elif pattern.frequency == "weekly":
            base_score += 10
        
        # Adjust for occurrence count
        occurrence_bonus = min(len(pattern.occurrences) * 2, 20)
        base_score += occurrence_bonus
        
        return min(base_score, 100)
    
    def generate_pattern_report(self) -> str:
        """Generate a comprehensive pattern report"""
        if not self.detected_patterns:
            self.detect_all_patterns()
        
        report = f"""
# Development Pattern Analysis Report
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## Summary
Found {len(self.detected_patterns)} patterns in your development workflow.

## High-Impact Patterns
"""
        
        # Group patterns by impact
        negative_patterns = [p for p in self.detected_patterns if p.impact == "negative"]
        positive_patterns = [p for p in self.detected_patterns if p.impact == "positive"]
        neutral_patterns = [p for p in self.detected_patterns if p.impact == "neutral"]
        
        if negative_patterns:
            report += "\n### ⚠️ Patterns Needing Attention\n"
            for pattern in negative_patterns[:5]:
                report += f"\n**{pattern.description}**\n"
                report += f"- Frequency: {pattern.frequency}\n"
                report += f"- Occurrences: {len(pattern.occurrences)}\n"
                if pattern.suggested_action:
                    report += f"- Suggestion: {pattern.suggested_action}\n"
        
        if positive_patterns:
            report += "\n### ✅ Positive Patterns\n"
            for pattern in positive_patterns[:5]:
                report += f"\n**{pattern.description}**\n"
                report += f"- Keep doing this!\n"
        
        # Automation suggestions
        automations = self.suggest_automations()
        if automations:
            report += "\n## 🤖 Automation Opportunities\n"
            for i, automation in enumerate(automations[:5], 1):
                report += f"\n### {i}. {automation['pattern']}\n"
                report += f"- Type: {automation['automation_type']}\n"
                report += f"- Implementation: {automation['implementation']}\n"
                report += f"- Time saved: {automation['estimated_time_saved']}\n"
                report += f"- Priority: {automation['priority']}/100\n"
        
        # Pattern statistics
        report += "\n## 📊 Pattern Statistics\n"
        report += f"- Total patterns detected: {len(self.detected_patterns)}\n"
        report += f"- Patterns with automation potential: {sum(1 for p in self.detected_patterns if p.automation_potential)}\n"
        report += f"- Negative patterns: {len(negative_patterns)}\n"
        report += f"- Positive patterns: {len(positive_patterns)}\n"
        
        # Recommendations
        report += "\n## 💡 Recommendations\n"
        
        if negative_patterns:
            report += "1. **Address negative patterns first** - They're impacting your productivity\n"
        
        if len(automations) > 3:
            report += "2. **Start with quick automation wins** - Implement the top 3 automations\n"
        
        if any(p.pattern_type == "emotional_pattern" for p in self.detected_patterns):
            report += "3. **Monitor emotional patterns** - Your mood affects your code quality\n"
        
        if any(p.frequency == "daily" for p in negative_patterns):
            report += "4. **Fix daily friction points** - Small daily improvements compound\n"
        
        report += "\n---\n*Use these insights to optimize your development workflow!*"
        
        return report

if __name__ == "__main__":
    # Example usage
    detector = PatternDetector()
    
    # Detect all patterns
    patterns = detector.detect_all_patterns(days=30)
    print(f"Found {len(patterns)} patterns")
    
    # Show top patterns
    for pattern in patterns[:5]:
        print(f"\n{pattern.pattern_type}: {pattern.description}")
        print(f"  Impact: {pattern.impact}, Frequency: {pattern.frequency}")
        print(f"  Occurrences: {len(pattern.occurrences)}")
        if pattern.suggested_action:
            print(f"  Suggestion: {pattern.suggested_action}")
    
    # Get automation suggestions
    automations = detector.suggest_automations()
    print(f"\n\nTop automation opportunities:")
    for auto in automations[:3]:
        print(f"- {auto['pattern']}: {auto['estimated_time_saved']} saved")
    
    # Generate full report
    report = detector.generate_pattern_report()
    print(f"\n{report}")