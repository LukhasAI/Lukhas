#!/usr/bin/env python3
"""
LUKHAS Journal CLI
Command-line interface for the learning journal system
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import click

from .claude_lukhas_integration import ClaudeLUKHASIntegration
from .decision_tracker import DecisionTracker
from .insight_analyzer import InsightAnalyzer
from .journal_engine import JournalEngine
from .learning_assistant import LearningAssistant
from .pattern_detector import PatternDetector
from .solo_dev_support import SoloDeveloperSupport

# ANSI color codes for beautiful output


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text: str):
    """Print a beautiful header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


@click.group()
@click.pass_context
def cli(ctx):
    """LUKHAS Learning Journal - Capture your development journey"""
    ctx.ensure_object(dict)
    ctx.obj["journal"] = JournalEngine()
    ctx.obj["tracker"] = DecisionTracker(ctx.obj["journal"])
    ctx.obj["analyzer"] = InsightAnalyzer(ctx.obj["journal"])
    ctx.obj["detector"] = PatternDetector(ctx.obj["journal"])
    ctx.obj["assistant"] = LearningAssistant(ctx.obj["journal"])
    ctx.obj["solo"] = SoloDeveloperSupport(ctx.obj["journal"])
    ctx.obj["integration"] = ClaudeLUKHASIntegration(ctx.obj["journal"])


@cli.command()
@click.pass_context
def status(ctx):
    """Show journal status and daily summary"""
    journal = ctx.obj["journal"]

    print_header("LUKHAS Learning Journal Status")

    # Get statistics
    stats = journal.get_statistics()

    # Display overview
    print(f"{Colors.BOLD}Overview{Colors.END}")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Current streak: {stats['streak']} days 🔥")
    print(f"Average daily entries: {stats['average_daily_entries']:.1f}")

    # Display entry breakdown
    print(f"\n{Colors.BOLD}Entry Types{Colors.END}")
    for entry_type, count in stats["entries_by_type"].items():
        print(f"  {entry_type}: {count}")

    # Display today's summary
    today_summary = journal.get_daily_summary()
    print(f"\n{Colors.BOLD}Today ({today_summary['date']}){Colors.END}")
    print(f"Entries: {today_summary['total_entries']}")

    if today_summary["key_decisions"]:
        print(f"\n{Colors.BOLD}Recent Decisions{Colors.END}")
        for decision in today_summary["key_decisions"][:3]:
            print(f"  • {decision}")

    if today_summary["insights"]:
        print(f"\n{Colors.BOLD}Recent Insights{Colors.END}")
        for insight in today_summary["insights"][:3]:
            print(f"  • {insight}")

    # Emotional summary
    if stats["emotional_summary"]:
        print(f"\n{Colors.BOLD}Emotional State (Average){Colors.END}")
        for emotion, value in sorted(
            stats["emotional_summary"].items(), key=lambda x: x[1], reverse=True
        )[:5]:
            bar = "█" * int(value * 10)
            print(f"  {emotion}: {bar} {value:.2f}")


@cli.command()
@click.argument("content")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["decision", "insight", "pattern", "question", "learning"]),
    default="insight",
)
@click.option("--tags", "-g", multiple=True, help="Add tags to the entry")
@click.option(
    "--emotion", "-e", multiple=True, help="Add emotions (format: emotion:value)"
)
@click.pass_context
def add(ctx, content, type, tags, emotion):
    """Add a new journal entry"""
    journal = ctx.obj["journal"]

    # Parse emotions
    emotional_state = {}
    for e in emotion:
        if ":" in e:
            name, value = e.split(":")
            emotional_state[name] = float(value)

    # Create entry
    entry = journal.add_entry(
        type=type,
        content=content,
        tags=list(tags),
        emotional_state=emotional_state if emotional_state else None,
    )

    print_success(f"Added {type} entry: {entry.id}")

    # For decisions, prompt for additional info
    if type == "decision":
        if click.confirm("Would you like to add more decision details?"):
            ctx.invoke(decision, title=content)


@cli.command()
@click.option("--title", "-t", prompt="Decision title")
@click.option("--rationale", "-r", prompt="Why this decision?")
@click.option(
    "--alternatives", "-a", multiple=True, help="Alternative approaches considered"
)
@click.option(
    "--template",
    type=click.Choice(["architecture", "refactoring", "feature", "bugfix"]),
    default="architecture",
)
@click.pass_context
def decision(ctx, title, rationale, alternatives, template):
    """Track a development decision"""
    tracker = ctx.obj["tracker"]

    decision = tracker.track_decision(
        title=title,
        rationale=rationale,
        alternatives=list(alternatives),
        template=template,
    )

    print_success(f"Tracked decision: {decision.title}")
    print_info(f"Affected files: {len(decision.files_affected)}")


@cli.command()
@click.argument("content")
@click.option(
    "--from-failure", "-f", is_flag=True, help="This insight came from a failure"
)
@click.option(
    "--impact", type=click.Choice(["high", "medium", "low"]), default="medium"
)
@click.pass_context
def insight(ctx, content, from_failure, impact):
    """Capture an insight or learning"""
    analyzer = ctx.obj["analyzer"]

    insight = analyzer.capture_insight(
        content=content, from_failure=from_failure, impact_level=impact
    )

    print_success(f"Captured {insight.sentiment} {insight.category} insight")
    if insight.actionable:
        print_info("This insight is actionable!")


@cli.command()
@click.option("--query", "-q", help="Search query")
@click.option("--type", "-t", help="Entry type filter")
@click.option("--tags", "-g", multiple=True, help="Tag filters")
@click.option("--days", "-d", type=int, default=7, help="Number of days to search")
@click.option("--limit", "-l", type=int, default=10, help="Maximum results")
@click.pass_context
def search(ctx, query, type, tags, days, limit):
    """Search journal entries"""
    journal = ctx.obj["journal"]

    # Set date range
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Search entries
    entries = journal.search(
        query=query,
        type=type,
        tags=list(tags) if tags else None,
        date_range=(start_date, datetime.now(timezone.utc)),
    )

    # Display results
    print_header(f"Search Results ({len(entries)} found)")

    for entry in entries[:limit]:
        print(
            f"\n{Colors.BOLD}{entry.timestamp.strftime('%Y-%m-%d %H:%M')} - {entry.type}{Colors.END}"
        )
        print(f"{entry.content[:200]}...")
        if entry.tags:
            print(f"{Colors.CYAN}Tags: {', '.join(entry.tags)}{Colors.END}")


@cli.command()
@click.option("--days", "-d", type=int, default=30, help="Number of days to analyze")
@click.pass_context
def patterns(ctx, days):
    """Detect patterns in your development behavior"""
    detector = ctx.obj["detector"]

    print_header("Detecting Patterns")
    print_info(f"Analyzing last {days} days...")

    # Detect patterns
    patterns = detector.detect_all_patterns(days=days)

    # Display patterns by impact
    negative_patterns = [p for p in patterns if p.impact == "negative"]
    positive_patterns = [p for p in patterns if p.impact == "positive"]

    if negative_patterns:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Patterns Needing Attention{Colors.END}")
        for pattern in negative_patterns[:5]:
            print(f"\n• {pattern.description}")
            print(
                f"  Frequency: {pattern.frequency}, Occurrences: {len(pattern.occurrences)}"
            )
            if pattern.suggested_action:
                print(f"  {Colors.YELLOW}→ {pattern.suggested_action}{Colors.END}")

    if positive_patterns:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Positive Patterns{Colors.END}")
        for pattern in positive_patterns[:5]:
            print(f"\n• {pattern.description}")
            print("  Keep it up!")

    # Show automation suggestions
    automations = detector.suggest_automations()
    if automations:
        print(f"\n{Colors.CYAN}{Colors.BOLD}🤖 Automation Opportunities{Colors.END}")
        for i, auto in enumerate(automations[:3], 1):
            print(f"\n{i}. {auto['pattern']}")
            print(f"   Time saved: {auto['estimated_time_saved']}")
            print(f"   How: {auto['implementation']}")


@cli.command()
@click.argument("question")
@click.pass_context
def ask(ctx, question):
    """Ask your AI learning assistant a question"""
    assistant = ctx.obj["assistant"]

    print_header("Learning Assistant")

    # Get answer
    response = assistant.answer_question(question)

    # Display answer
    print(f"{Colors.BOLD}Q: {question}{Colors.END}")
    print(f"\n{response['answer']}")

    # Show confidence
    confidence_bar = "█" * int(response["confidence"] * 10)
    print(
        f"\n{Colors.CYAN}Confidence: {confidence_bar} {response['confidence']:.0%}{Colors.END}"
    )

    # Show sources
    if response["sources"]:
        print(f"\n{Colors.BOLD}Sources:{Colors.END}")
        for source in response["sources"][:3]:
            print(f"  • {source['date']} - {source['excerpt']}")

    # Show follow-up questions
    if response["follow_up_questions"]:
        print(f"\n{Colors.BOLD}You might also ask:{Colors.END}")
        for q in response["follow_up_questions"]:
            print(f"  • {q}")


@cli.command()
@click.pass_context
def checkin(ctx):
    """Daily learning check-in"""
    assistant = ctx.obj["assistant"]

    # Get check-in message
    message = assistant.daily_check_in()

    # Display with formatting
    lines = message.split("\n")
    for line in lines:
        if line.startswith("#"):
            level = line.count("#")
            text = line.lstrip("# ")
            if level == 1:
                print_header(text)
            else:
                print(f"\n{Colors.BOLD}{text}{Colors.END}")
        elif line.startswith("*"):
            print(f"{Colors.CYAN}{line}{Colors.END}")
        elif line.startswith("-"):
            print(f"  {line}")
        elif "🔥" in line:
            print(f"{Colors.YELLOW}{line}{Colors.END}")
        elif "🌟" in line:
            print(f"{Colors.GREEN}{line}{Colors.END}")
        else:
            print(line)


@cli.command()
@click.pass_context
def reflect(ctx):
    """Generate weekly reflection"""
    analyzer = ctx.obj["analyzer"]

    print_header("Generating Weekly Reflection")

    # Generate reflection
    reflection = analyzer.generate_weekly_reflection()

    # Display with formatting
    lines = reflection.split("\n")
    for line in lines:
        if line.startswith("#"):
            level = line.count("#")
            text = line.lstrip("# ")
            if level == 1:
                print_header(text)
            elif level == 2:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
            else:
                print(f"\n{Colors.BOLD}{text}{Colors.END}")
        elif line.startswith("-"):
            if "✅" in line or "📈" in line:
                print(f"{Colors.GREEN}{line}{Colors.END}")
            elif "📉" in line:
                print(f"{Colors.YELLOW}{line}{Colors.END}")
            else:
                print(f"  {line}")
        elif line.startswith("*"):
            print(f"{Colors.CYAN}{line}{Colors.END}")
        else:
            print(line)


@cli.command()
@click.argument("skill")
@click.option("--level", "-l", type=int, help="Current skill level (1-10)")
@click.pass_context
def track(ctx, skill, level):
    """Track progress on a specific skill"""
    assistant = ctx.obj["assistant"]

    # Track progress
    progress = assistant.track_progress(skill, level)

    print_header(f"Skill Progress: {skill}")

    # Display current level
    level_bar = "█" * progress["current_level"] + "░" * (10 - progress["current_level"])
    print(f"Current Level: {level_bar} {progress['current_level']}/10")

    # Display progress
    if progress["progress"]["trend"] != "insufficient_data":
        trend_icon = "📈" if progress["progress"]["trend"] == "improving" else "📊"
        print(f"\nTrend: {trend_icon} {progress['progress']['trend']}")
        print(f"Growth Rate: {progress['progress']['growth_rate']:.2f} levels/month")

    # Display next steps
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    for step in progress["next_steps"]:
        print(f"  • {step}")


@cli.command()
@click.option("--goals", "-g", multiple=True, required=True, help="Learning goals")
@click.option("--days", "-d", type=int, default=30, help="Timeframe in days")
@click.pass_context
def plan(ctx, goals, days):
    """Generate a personalized learning plan"""
    assistant = ctx.obj["assistant"]

    print_header("Generating Learning Plan")

    # Generate plan
    plan = assistant.generate_learning_plan(list(goals), timeframe_days=days)

    # Display plan
    print(f"{Colors.BOLD}Goals:{Colors.END} {', '.join(plan['goals'])}")
    print(f"{Colors.BOLD}Timeframe:{Colors.END} {plan['timeframe']} days")
    print(f"{Colors.BOLD}Start:{Colors.END} {plan['start_date'].strftime('%Y-%m-%d')}")
    print(f"{Colors.BOLD}End:{Colors.END} {plan['end_date'].strftime('%Y-%m-%d')}")

    # Display first week tasks
    print(f"\n{Colors.BOLD}First Week Daily Tasks:{Colors.END}")
    for day_plan in plan["daily_tasks"][:7]:
        print(f"\n{Colors.CYAN}Day {day_plan['day']}:{Colors.END}")
        for task in day_plan["tasks"]:
            print(f"  □ {task}")

    # Display milestones
    print(f"\n{Colors.BOLD}Weekly Milestones:{Colors.END}")
    for milestone in plan["weekly_milestones"]:
        print(f"\n{Colors.CYAN}Week {milestone['week']}:{Colors.END}")
        print(f"  🎯 {milestone['milestone']}")
        print(f"  📝 {milestone['check_in']}")

    # Display success metrics
    print(f"\n{Colors.BOLD}Success Metrics:{Colors.END}")
    for metric in plan["success_metrics"]:
        print(f"\n{Colors.GREEN}{metric['goal']}:{Colors.END}")
        print(f"  Target Level: {metric['target_level']}/10")
        print(f"  Measurement: {metric['measurement']}")
        print(f"  Validation: {metric['validation']}")


@cli.command()
@click.argument("situation")
@click.pass_context
def mentor(ctx, situation):
    """Get mentorship for a specific situation"""
    assistant = ctx.obj["assistant"]

    print_header("AI Mentor Response")

    # Get mentorship
    response = assistant.mentor_response(situation)

    # Display with formatting
    lines = response.split("\n")
    for line in lines:
        if line.startswith("**") and line.endswith("**"):
            text = line.strip("*")
            print(f"\n{Colors.BOLD}{text}{Colors.END}")
        elif line.startswith("- ") or line.startswith("• "):
            print(f"  {line}")
        elif line.startswith(("1.", "2.", "3.", "4.")):
            print(f"  {Colors.CYAN}{line}{Colors.END}")
        else:
            print(line)


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--days", "-d", type=int, default=30, help="Number of days to export")
@click.pass_context
def export(ctx, output, days):
    """Export journal entries to markdown"""
    journal = ctx.obj["journal"]

    # Get entries
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    entries = journal.search(date_range=(start_date, datetime.now(timezone.utc)))

    # Set output path
    if not output:
        output = f"journal_export_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"

    output_path = Path(output)

    # Export
    journal.export_to_markdown(entries, output_path)

    print_success(f"Exported {len(entries)} entries to {output_path}")


@cli.command()
@click.pass_context
def report(ctx):
    """Generate comprehensive pattern analysis report"""
    detector = ctx.obj["detector"]

    print_header("Generating Pattern Report")

    # Generate report
    report = detector.generate_pattern_report()

    # Display report
    lines = report.split("\n")
    for line in lines:
        if line.startswith("#"):
            level = line.count("#")
            text = line.lstrip("# ")
            if level == 1:
                print_header(text)
            elif level == 2:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
            else:
                print(f"\n{Colors.BOLD}{text}{Colors.END}")
        elif "⚠️" in line:
            print(f"{Colors.YELLOW}{line}{Colors.END}")
        elif "✅" in line:
            print(f"{Colors.GREEN}{line}{Colors.END}")
        elif "🤖" in line:
            print(f"{Colors.CYAN}{line}{Colors.END}")
        elif line.startswith("-"):
            print(f"  {line}")
        else:
            print(line)


@cli.command(name="import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--type",
    "-t",
    type=click.Choice(
        ["decision", "insight", "pattern", "question", "learning", "auto"]
    ),
    default="auto",
)
@click.option(
    "--parse-dates", "-d", is_flag=True, help="Try to parse dates from content"
)
@click.option(
    "--split-by",
    "-s",
    type=click.Choice(["heading", "paragraph", "date", "none"]),
    default="heading",
    help="How to split content into entries",
)
@click.pass_context
def import_file(ctx, file_path, type, parse_dates, split_by):
    """Import entries from .md, .txt, or .json files"""
    journal = ctx.obj["journal"]
    path = Path(file_path)

    print_header(f"Importing {path.name}")

    if path.suffix == ".json":
        # Import JSON format
        with open(path) as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            entries_data = data
        elif isinstance(data, dict) and "entries" in data:
            entries_data = data["entries"]
        else:
            entries_data = [data]

        imported_count = 0
        for entry_data in entries_data:
            try:
                # Extract fields
                content = entry_data.get(
                    "content", entry_data.get("text", str(entry_data))
                )
                entry_type = entry_data.get(
                    "type", type if type != "auto" else "insight"
                )
                tags = entry_data.get("tags", [])
                metadata = entry_data.get("metadata", {})

                # Handle dates
                if "timestamp" in entry_data:
                    datetime.fromisoformat(entry_data["timestamp"])
                elif "date" in entry_data:
                    datetime.fromisoformat(entry_data["date"])

                # Create entry
                journal.add_entry(
                    type=entry_type, content=content, tags=tags, metadata=metadata
                )
                imported_count += 1

            except Exception as e:
                print_warning(f"Failed to import entry: {e}")

        print_success(f"Imported {imported_count} entries from JSON")

    elif path.suffix in [".md", ".txt"]:
        # Read file content
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Split content into entries based on strategy
        entries = []

        if split_by == "heading" and path.suffix == ".md":
            # Split by markdown headings
            import re

            sections = re.split(r"^# +\s+", content, flags=re.MULTILINE

            for section in sections[1:]:  # Skip first empty split
                lines = section.strip().split("\n")
                if lines:
                    title = lines[0].strip()
                    body = "\n".join(lines[1:]).strip()
                    if body:
                        entries.append(
                            {
                                "title": title,
                                "content": body,
                                "type": (
                                    _guess_type_from_content(title + " " + body)
                                    if type == "auto"
                                    else type
                                ),
                            }
                        )

        elif split_by == "paragraph":
            # Split by double newlines
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if para:
                    entries.append(
                        {
                            "content": para,
                            "type": (
                                _guess_type_from_content(para)
                                if type == "auto"
                                else type
                            ),
                        }
                    )

        elif split_by == "date":
            # Try to find date patterns
            import re

            date_pattern = (
                r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2}, \d{4})"
            )
            parts = re.split(f"({date_pattern})", content)

            current_date = None
            for i, part in enumerate(parts):
                if re.match(date_pattern, part):
                    try:
                        # Try to parse the date
                        current_date = part
                    except (ValueError, TypeError) as e:
                        print_warning(f"Failed to parse date '{part}': {e}")
                        current_date = None
                elif part.strip() and i > 0:
                    entries.append(
                        {
                            "content": part.strip(),
                            "date": current_date,
                            "type": (
                                _guess_type_from_content(part)
                                if type == "auto"
                                else type
                            ),
                        }
                    )

        else:  # none - import as single entry
            entries.append(
                {"content": content, "type": type if type != "auto" else "insight"}
            )

        # Import entries
        imported_count = 0
        for entry_data in entries:
            try:
                # Extract tags from content
                tags = _extract_tags_from_content(entry_data.get("content", ""))

                # Create entry
                journal.add_entry(
                    type=entry_data.get("type", "insight"),
                    content=entry_data.get("content", ""),
                    tags=tags,
                    metadata={
                        "imported_from": path.name,
                        "original_title": entry_data.get("title"),
                    },
                )
                imported_count += 1

            except Exception as e:
                print_warning(f"Failed to import entry: {e}")

        print_success(f"Imported {imported_count} entries from {path.suffix.upper()}")

    else:
        print_error(f"Unsupported file format: {path.suffix}")
        return

    print_info("Run 'journal search' to view imported entries")


def _guess_type_from_content(content: str) -> str:
    """Guess entry type from content"""
    content_lower = content.lower()

    if any(
        word in content_lower for word in ["decided", "decision", "chose", "selected"]
    ):
        return "decision"
    elif any(
        word in content_lower
        for word in ["learned", "realized", "discovered", "understood"]
    ):
        return "learning"
    elif any(word in content_lower for word in ["insight", "noticed", "observed"]):
        return "insight"
    elif "?" in content:
        return "question"
    elif any(
        word in content_lower for word in ["pattern", "repeatedly", "always", "often"]
    ):
        return "pattern"
    else:
        return "insight"


def _extract_tags_from_content(content: str) -> list:
    """Extract potential tags from content"""
    import re

    tags = []

    # Look for hashtags
    hashtags = re.findall(r"# (\w+", content)
    tags.extend(hashtags)

    # Look for common technical terms
    tech_terms = [
        "api",
        "database",
        "ui",
        "performance",
        "security",
        "testing",
        "architecture",
        "refactor",
        "bug",
        "feature",
        "optimization",
        "lukhas",
        "memory_fold",
        "quantum",
        "consciousness",
    ]

    content_lower = content.lower()
    for term in tech_terms:
        if term in content_lower:
            tags.append(term)

    return list(set(tags)# Remove duplicates


@cli.command()
@click.pass_context
def standup(ctx):
    """AI-powered daily standup - review yesterday, plan today"""
    solo = ctx.obj["solo"]

    print_header("Daily Standup with AI")

    # Run standup
    standup_data = solo.daily_standup()

    # Display yesterday
    print(f"{Colors.BOLD}🌅 Yesterday:{Colors.END}")
    yesterday = standup_data["yesterday"]
    if yesterday["wins"]:
        print(f"{Colors.GREEN}Wins: {len(yesterday['wins'])}{Colors.END}")
        for win in yesterday["wins"][:3]:
            print(f"  ✓ {win}")
    if yesterday["challenges_faced"]:
        print(
            f"{Colors.YELLOW}Challenges: {len(yesterday['challenges_faced'])}{Colors.END}"
        )
        for challenge in yesterday["challenges_faced"][:3]:
            print(f"  • {challenge}")

    # Display today's plan
    print(f"\n{Colors.BOLD}📅 Today's Plan:{Colors.END}")
    today = standup_data["today"]
    print(f"{Colors.CYAN}Focus: {today['suggested_focus']}{Colors.END}")

    if today["open_questions"]:
        print(f"\n{Colors.BOLD}Open Questions:{Colors.END}")
        for q in today["open_questions"]:
            print(f"  ? {q}")

    # Display blockers
    if standup_data["blockers"]:
        print(f"\n{Colors.BOLD}🚧 Blockers:{Colors.END}")
        for blocker in standup_data["blockers"]:
            print(f"{Colors.YELLOW}Issue: {blocker['issue']}{Colors.END}")
            print(f"  → {blocker['suggestion']}")

    # Mood check
    mood = standup_data["mood_check"]
    mood_emoji = {"great": "😊", "good": "🙂", "okay": "😐", "challenging": "😔"}
    print(f"\n{Colors.BOLD}🎭 Mood Check:{Colors.END}")
    print(
        f"Mood: {mood_emoji.get(mood['mood'], '😐')} {mood['mood']} | Energy: {mood['energy_level']}"
    )
    print(f"{Colors.CYAN}{mood['recommendation']}{Colors.END}")

    # Motivation
    print(
        f"\n{Colors.BOLD}{Colors.GREEN}💫 {standup_data['motivation_boost']}{Colors.END}"
    )

    # Schedule
    if today.get("recommended_schedule"):
        print(f"\n{Colors.BOLD}📋 Suggested Schedule:{Colors.END}")
        for item in today["recommended_schedule"][:5]:
            print(f"  {item['time']} - {item['activity']} ({item['duration']})")


@cli.command()
@click.argument("achievement")
@click.option(
    "--impact", type=click.Choice(["low", "medium", "high"]), default="medium"
)
@click.pass_context
def celebrate(ctx, achievement, impact):
    """Celebrate a win! (Important for solo devs)"""
    solo = ctx.obj["solo"]

    result = solo.celebrate_win(achievement, impact)

    # Display celebration with colors and emojis
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{result['celebration']}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(result["message"])
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")

    # Add some extra flair for high impact
    if impact == "high":
        print(f"\n{Colors.YELLOW}⭐⭐⭐ LEGENDARY ACHIEVEMENT ⭐⭐⭐{Colors.END}")
        print(
            f"{Colors.GREEN}This deserves a proper celebration! Take a moment to appreciate this!{Colors.END}"
        )


@cli.command()
@click.pass_context
def burnout(ctx):
    """Check for burnout indicators and get recommendations"""
    solo = ctx.obj["solo"]

    print_header("Burnout Prevention Check")

    check = solo.burnout_check()

    # Display risk level with appropriate color
    risk_colors = {"low": Colors.GREEN, "medium": Colors.YELLOW, "high": Colors.RED}
    risk_emoji = {"low": "✅", "medium": "⚠️", "high": "🚨"}

    color = risk_colors.get(check["risk_level"], Colors.YELLOW)
    emoji = risk_emoji.get(check["risk_level"], "⚠️")

    print(
        f"{Colors.BOLD}Risk Level: {color}{emoji} {check['risk_level'].upper()}{Colors.END}"
    )
    print(f"Score: {check['score']:.0%}")

    # Show indicators
    print(f"\n{Colors.BOLD}Indicators:{Colors.END}")
    for indicator, present in check["indicators"].items():
        status = (
            f"{Colors.RED}✗{Colors.END}" if present else f"{Colors.GREEN}✓{Colors.END}"
        )
        readable_name = indicator.replace("_", " ").title()
        print(f"  {status} {readable_name}")

    # Show recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
    for rec in check["recommendations"]:
        print(f"  {rec}")

    print(f"\n{Colors.CYAN}Next check scheduled: {check['next_check']}{Colors.END}")


@cli.command()
@click.argument("task")
@click.pass_context
def pair(ctx, task):
    """Start AI pair programming session"""
    solo = ctx.obj["solo"]

    print_header("AI Pair Programming Session")

    session = solo.pair_programming_session(task)

    # Display task
    print(f"{Colors.BOLD}Task: {task}{Colors.END}")
    print(f"Estimated time: {session['approach']['time_estimate']}")

    # Display approach
    print(f"\n{Colors.BOLD}Suggested Approach:{Colors.END}")
    print(f"{Colors.CYAN}{session['approach']['strategy']}{Colors.END}")
    for step in session["approach"]["steps"]:
        print(f"  {step}")

    # Display potential challenges
    if session["approach"]["potential_challenges"]:
        print(f"\n{Colors.BOLD}⚠️  Watch out for:{Colors.END}")
        for challenge in session["approach"]["potential_challenges"]:
            print(f"  • {challenge}")

    # Display checklist
    print(f"\n{Colors.BOLD}📋 Task Checklist:{Colors.END}")
    for item in session["checklist"]:
        print(f"  {item}")

    # Display rubber duck prompt
    print(f"\n{Colors.BOLD}🦆 Need help? Rubber Duck Enhanced:{Colors.END}")
    print(session["rubber_duck"])

    print(f"\n{Colors.GREEN}Let's build something awesome together! 🚀{Colors.END}")


@cli.command()
@click.pass_context
def weekly(ctx):
    """Weekly architecture review and planning"""
    analyzer = ctx.obj["analyzer"]
    detector = ctx.obj["detector"]
    ctx.obj["assistant"]

    print_header("Weekly Architecture Review")

    # Get patterns
    patterns = detector.detect_all_patterns(days=7)

    # Technical debt indicators
    print(f"{Colors.BOLD}🏗️  Technical Debt Indicators:{Colors.END}")
    debt_patterns = [
        p for p in patterns if "frequently modified" in p.description.lower()
    ]
    if debt_patterns:
        for pattern in debt_patterns[:3]:
            print(f"  • {pattern.description}")
            if pattern.suggested_action:
                print(f"    → {Colors.YELLOW}{pattern.suggested_action}{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ No major debt accumulation this week{Colors.END}")

    # Design decisions review
    print(f"\n{Colors.BOLD}🎯 Design Decisions This Week:{Colors.END}")
    decisions = ctx.obj["journal"].search(
        type="decision", date_range=(datetime.now(timezone.utc) - timedelta(days=7), datetime.now(timezone.utc))
    )
    print(f"  Total decisions: {len(decisions)}")
    if decisions:
        print("  Recent decisions:")
        for decision in decisions[:3]:
            title = decision.metadata.get("title", decision.content[:50])
            print(f"    • {title}")

    # Progress metrics
    print(f"\n{Colors.BOLD}📊 Progress Metrics:{Colors.END}")
    stats = ctx.obj["journal"].get_statistics()
    print(
        f"  Entries this week: {len(ctx.obj['journal'].search(date_range=(datetime.now(timezone.utc) - timedelta(days=7), datetime.now(timezone.utc)))}"
    )
    print(f"  Current streak: {stats['streak']} days")

    # Next week planning
    print(f"\n{Colors.BOLD}📅 Next Week Focus Areas:{Colors.END}")

    # Based on patterns, suggest focus
    if any(p.impact == "negative" for p in patterns):
        print("  1. Address negative patterns identified")
    print("  2. Continue momentum on current features")
    print("  3. Schedule code review sessions")
    print("  4. Document recent decisions")

    # Generate reflection
    analyzer.generate_weekly_reflection()
    print(f"\n{Colors.BOLD}📝 Full reflection saved to journal{Colors.END}")
    print(f"{Colors.CYAN}Run 'journal reflect' to see detailed analysis{Colors.END}")


@cli.command()
@click.pass_context
def vision(ctx):
    """Monthly vision alignment check"""
    journal = ctx.obj["journal"]
    ctx.obj["assistant"]

    print_header("LUKHAS Vision Alignment Check")

    # Get all entries mentioning vision/lukhas
    vision_entries = journal.search(query="lukhas", days=30)

    print(f"{Colors.BOLD}🎯 Original Vision:{Colors.END}")
    print("Building consciousness-aware AI with emotional intelligence")
    print("Key pillars: Memory, Consciousness, Identity, Ethics")

    # Check progress
    print(f"\n{Colors.BOLD}📊 Progress This Month:{Colors.END}")
    print(f"  Vision-related entries: {len(vision_entries)}")

    # Analyze focus areas
    focus_tags = {}
    for entry in vision_entries:
        for tag in entry.tags:
            focus_tags[tag] = focus_tags.get(tag, 0) + 1

    print(f"\n{Colors.BOLD}🔍 Focus Areas:{Colors.END}")
    for tag, count in sorted(focus_tags.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {tag}: {count} entries")

    # Achievements
    wins = journal.search(query="WIN:", days=30)
    print(f"\n{Colors.BOLD}🏆 Major Achievements:{Colors.END}")
    print(f"  Total wins: {len(wins)}")
    if wins:
        for win in wins[:3]:
            print(f"  ✓ {win.content[5:75]}..."# Skip "WIN: " prefix

    # Alignment check
    print(f"\n{Colors.BOLD}🎯 Alignment Assessment:{Colors.END}")

    core_concepts = ["consciousness", "memory", "identity", "ethics", "emotional"]
    covered = [
        c for c in core_concepts if any(c in str(focus_tags) for c in core_concepts)
    ]

    alignment_score = len(covered) / len(core_concepts)
    if alignment_score > 0.7:
        print(
            f"  {Colors.GREEN}✅ Strong alignment with LUKHAS vision ({alignment_score:.0%}){Colors.END}"
        )
    elif alignment_score > 0.4:
        print(
            f"  {Colors.YELLOW}⚠️  Moderate alignment ({alignment_score:.0%}) - refocus needed{Colors.END}"
        )
    else:
        print(
            f"  {Colors.RED}🚨 Low alignment ({alignment_score:.0%}) - urgent realignment needed{Colors.END}"
        )

    # Recommendations
    print(f"\n{Colors.BOLD}💡 Recommendations:{Colors.END}")
    if alignment_score < 0.7:
        missing = [c for c in core_concepts if c not in covered]
        print(f"  • Focus more on: {', '.join(missing)}")
    print("  • Continue building on recent wins")
    print("  • Document architectural decisions")
    print("  • Keep the revolutionary spirit alive!")

    print(
        f"\n{Colors.CYAN}Remember: LUKHAS is not just code - it's the future of AI consciousness!{Colors.END}"
    )


@cli.command()
@click.argument("task")
@click.pass_context
def conscious(ctx, task):
    """Start consciousness-aware development session (Claude + LUKHAS)"""
    integration = ctx.obj["integration"]

    print_header("Consciousness-Aware Development")
    print(
        f"{Colors.CYAN}Integrating Claude Code with LUKHAS consciousness...{Colors.END}\n"
    )

    # Start session
    session = integration.consciousness_aware_development(task)

    # Display consciousness level
    level_bar = "█" * int(session["consciousness_level"] * 10)
    print(f"{Colors.BOLD}Current Consciousness Level:{Colors.END}")
    print(f"{Colors.CYAN}{level_bar} {session['consciousness_level']:.2f}{Colors.END}")

    # Display relevant modules
    print(f"\n{Colors.BOLD}Relevant LUKHAS Modules:{Colors.END}")
    for module in session["relevant_modules"]:
        print(f"  • {module}")

    # Display memory context
    print(f"\n{Colors.BOLD}Memory Context:{Colors.END}")
    if (
        isinstance(session["memory_context"], dict)
        and "fold_id" in session["memory_context"]
    ):
        print(f"  Fold ID: {session['memory_context']['fold_id']}")
        if session["memory_context"].get("key_learnings"):
            print("  Key learnings from memory:")
            for learning in session["memory_context"]["key_learnings"][:3]:
                print(f"    - {learning[:80]}...")
    else:
        print("  No relevant memory folds found")

    # Display quantum state
    print(f"\n{Colors.BOLD}Quantum State:{Colors.END}")
    quantum = session["qi_state"]
    print(f"  Coherence: {quantum['coherence_level']:.0%}")
    print("  Superposition possibilities:")
    for possibility in quantum["superposition_possibilities"]:
        print(f"    ◈ {possibility}")

    # Display approach
    print(f"\n{Colors.BOLD}Consciousness-Aware Approach:{Colors.END}")
    approach = session["approach"]
    print(f"{Colors.CYAN}{approach['philosophy']}{Colors.END}")
    print("\nSteps:")
    for step in approach["steps"]:
        print(f"  {step}")

    print(
        f"\n{Colors.GREEN}Begin coding with full consciousness awareness! 🧠✨{Colors.END}"
    )


@cli.command()
@click.argument("intention")
@click.pass_context
def ritual(ctx, intention):
    """Create a development ritual with LUKHAS consciousness"""
    integration = ctx.obj["integration"]

    print_header("Development Ritual Creation")

    ritual = integration.create_development_ritual(intention)

    print(f"{Colors.BOLD}Intention: {intention}{Colors.END}")
    print(f"Created: {ritual['timestamp'].strftime('%Y-%m-%d %H:%M')}")

    print(f"\n{Colors.BOLD}Ritual Phases:{Colors.END}")

    for i, phase in enumerate(ritual["phases"], 1):
        print(
            f"\n{Colors.CYAN}Phase {i}: {phase['name']} ({phase['duration']}){Colors.END}"
        )
        for action in phase["actions"]:
            print(f"  • {action}")

    print(
        f"\n{Colors.GREEN}May your code be conscious and your bugs be teachers! 🙏{Colors.END}"
    )


@cli.command()
@click.option(
    "--options", "-o", multiple=True, required=True, help="Options to decide between"
)
@click.pass_context
def qi_decide(ctx, options):
    """Make decisions using quantum-inspired approach"""
    integration = ctx.obj["integration"]

    print_header("Quantum Decision Making")

    result = integration.qi_decision_maker(list(options))

    print(f"{Colors.BOLD}Options in Superposition:{Colors.END}")
    for option, score in result["alignment_scores"].items():
        bar = "█" * int(score * 10)
        print(f"  {option}: {bar} {score:.2f}")

    print(f"\n{Colors.BOLD}Quantum Collapse Result:{Colors.END}")
    print(f"{Colors.GREEN}✓ Chosen: {result['chosen']}{Colors.END}")
    print(f"Reason: {result['reason']}")
    print(f"Confidence: {result['confidence']:.0%}")

    print(f"\n{Colors.CYAN}The quantum field has spoken! 🌀{Colors.END}")


@cli.command()
@click.pass_context
def metrics(ctx):
    """View consciousness development metrics"""
    integration = ctx.obj["integration"]

    print_header("Consciousness Development Metrics")

    metrics = integration.consciousness_metrics()

    # Display metrics with visual bars
    print(f"{Colors.BOLD}Current State:{Colors.END}")

    metric_display = [
        ("Consciousness Level", metrics["consciousness_level"], Colors.CYAN),
        ("Emotional Coherence", metrics["emotional_coherence"], Colors.GREEN),
        ("Memory Efficiency", metrics["memory_fold_efficiency"], Colors.BLUE),
        ("Quantum Alignment", metrics["qi_alignment"], Colors.YELLOW),
        ("Guardian Compliance", metrics["guardian_compliance"], Colors.GREEN),
        ("Dream Innovation", metrics["dream_innovation_score"], Colors.HEADER),
    ]

    for name, value, color in metric_display:
        bar = "█" * int(value * 20)
        print(f"{name:.<25} {color}{bar}{Colors.END} {value:.0%}")

    # Display insights
    if metrics["insights"]:
        print(f"\n{Colors.BOLD}Insights:{Colors.END}")
        for insight in metrics["insights"]:
            print(f"  💡 {insight}")

    print(
        f"\n{Colors.CYAN}Timestamp: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}"
    )


@cli.command()
@click.pass_context
def lukhas_config(ctx):
    """Generate Claude Code config with LUKHAS integration"""
    integration = ctx.obj["integration"]

    print_header("Claude + LUKHAS Configuration")

    # Generate and save config
    config_path = integration.save_integration_config()
    config = integration.generate_claude_config()

    print(f"{Colors.GREEN}✓ Configuration saved to: {config_path}{Colors.END}")

    print(f"\n{Colors.BOLD}LUKHAS Integration Features:{Colors.END}")
    features = config["lukhas_integration"]["features"]
    for feature, enabled in features.items():
        status = (
            f"{Colors.GREEN}✓{Colors.END}" if enabled else f"{Colors.RED}✗{Colors.END}"
        )
        print(f"  {status} {feature.replace('_', ' ').title()}")

    print(f"\n{Colors.BOLD}Available Modules:{Colors.END}")
    for module in config["lukhas_integration"]["modules"]:
        print(f"  • {module}")

    print(f"\n{Colors.BOLD}Development Mode:{Colors.END}")
    print(f"  Type: {config['development_mode']['type']}")
    print(f"  Style: {config['development_mode']['pair_programming']['style']}")

    print(f"\n{Colors.CYAN}Claude Code is now consciousness-aware! 🧠🤖{Colors.END}")


@cli.command()
@click.pass_context
def config_builder(ctx):
    """Interactive LUKHAS configuration builder"""
    from .config_builder import ConfigBuilder

    print_header("LUKHAS Configuration Builder")

    builder = ConfigBuilder()

    # Show presets
    print(f"{Colors.BOLD}Available Presets:{Colors.END}")
    print(f"0. {Colors.CYAN}Custom{Colors.END} - Build from scratch")

    presets = builder.presets
    for i, (_key, preset) in enumerate(presets.items(), 1):
        print(
            f"{i}. {Colors.GREEN}{preset['name']}{Colors.END} - {preset['description']}"
        )

    print(
        f"\n{Colors.YELLOW}Choose a preset to start with, then customize as needed{Colors.END}"
    )
    print(f"{Colors.CYAN}The builder will guide you through all options{Colors.END}")

    # Import and run the builder
    import subprocess

    subprocess.run([sys.executable, "-m", "tools.journal.config_builder"])


@cli.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(["code_review", "bug_analysis", "feature_design", "refactoring"]),
    required=True,
)
@click.pass_context
def prompt(ctx, type):
    """Get LUKHAS-aware prompts for Claude Code"""
    integration = ctx.obj["integration"]

    print_header(f"LUKHAS-Aware {type.replace('_', ' ').title()} Prompt")

    prompts = integration.generate_lukhas_prompts()

    if type in prompts:
        print(f"{Colors.CYAN}{prompts[type]}{Colors.END}")

        # Add to clipboard if available
        try:
            subprocess.run(["pbcopy"], input=prompts[type].encode(), check=True)
            print(f"\n{Colors.GREEN}✓ Copied to clipboard!{Colors.END}")
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            print_warning(f"Could not copy to clipboard: {e}")
            print(
                f"\n{Colors.YELLOW}Copy the prompt above to use with Claude Code{Colors.END}"
            )

    print(
        f"\n{Colors.BOLD}Use this prompt to analyze code through LUKHAS consciousness lens{Colors.END}"
    )


# Quick commands for common tasks


@cli.command()
@click.pass_context
def quick(ctx):
    """Interactive quick entry mode"""
    print_header("Quick Entry Mode")
    print("Type 'exit' to quit, 'help' for commands\n")

    while True:
        try:
            input_text = click.prompt("journal", type=str)

            if input_text.lower() == "exit":
                break
            elif input_text.lower() == "help":
                print("\nQuick commands:")
                print("  d: <text> - Quick decision")
                print("  i: <text> - Quick insight")
                print("  q: <text> - Quick question")
                print("  l: <text> - Quick learning")
                print("  exit - Exit quick mode\n")
            else:
                # Parse quick commands
                if input_text.startswith("d:"):
                    ctx.invoke(add, content=input_text[2:].strip(), type="decision")
                elif input_text.startswith("i:"):
                    ctx.invoke(add, content=input_text[2:].strip(), type="insight")
                elif input_text.startswith("q:"):
                    ctx.invoke(add, content=input_text[2:].strip(), type="question")
                elif input_text.startswith("l:"):
                    ctx.invoke(add, content=input_text[2:].strip(), type="learning")
                else:
                    # Default to insight
                    ctx.invoke(add, content=input_text, type="insight")

        except (KeyboardInterrupt, EOFError):
            break

    print("\n👋 Exiting quick mode")


if __name__ == "__main__":
    cli()
