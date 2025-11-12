#!/usr/bin/env python3
"""
Sync TODO/by-agent/ views from MASTER_LOG.md.

Usage:
    python3 scripts/todo/sync_agents.py [--agent jules] [--dry-run]

Reads MASTER_LOG.md and updates agent-specific task views:
- TODO/by-agent/jules.md
- TODO/by-agent/claude-code.md
- TODO/by-agent/codex.md
- TODO/by-agent/human.md

Options:
    --agent: Sync specific agent only (default: all)
    --dry-run: Show what would be done without making changes
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import ClassVar, Dict, List

# ANSI colors
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


class AgentViewSyncer:
    """Sync agent-specific views from MASTER_LOG."""

    AGENTS: ClassVar[list[object]] = ['jules', 'claude-code', 'codex', 'human']

    def __init__(self, dry_run: bool = False):
        self.master_log_path = Path("TODO/MASTER_LOG.md")
        self.by_agent_dir = Path("TODO/by-agent")
        self.dry_run = dry_run
        self.tasks_by_agent: Dict[str, List[Dict]] = defaultdict(list)
        self.tasks_by_priority: Dict[str, List[Dict]] = defaultdict(list)

    def sync(self, specific_agent: str = None):
        """Sync agent views from MASTER_LOG."""
        if not self.master_log_path.exists():
            print(f"MASTER_LOG not found: {self.master_log_path}")
            return

        # Parse MASTER_LOG
        self._parse_master_log()

        # Sync specified agent or all agents
        agents_to_sync = [specific_agent] if specific_agent else self.AGENTS

        for agent in agents_to_sync:
            self._sync_agent_view(agent)

    def _parse_master_log(self):
        """Parse MASTER_LOG and categorize tasks by agent and priority."""
        content = self.master_log_path.read_text()

        # Find priority sections
        current_priority = None
        task_pattern = re.compile(
            r'\|\s*([A-Z\d]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*'
            r'([^|]+)\s*\|\s*([SML])\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|'
        )

        for line in content.split('\n'):
            # Check for priority section headers
            priority_match = re.match(r'## Priority (\d+)', line)
            if priority_match:
                current_priority = f"P{priority_match.group(1)}"
                continue

            # Parse task rows
            task_match = task_pattern.match(line)
            if task_match and current_priority:
                task = {
                    'id': task_match.group(1).strip(),
                    'description': task_match.group(2).strip(),
                    'owner': task_match.group(3).strip().lower(),
                    'status': task_match.group(4).strip(),
                    'effort': task_match.group(5).strip(),
                    'pr': task_match.group(6).strip(),
                    'notes': task_match.group(7).strip(),
                    'priority': current_priority,
                }

                # Add to agent's task list
                owner = task['owner'].lower()
                if owner in self.AGENTS or owner == 'copilot':
                    # Normalize Copilot to copilot
                    if owner == 'copilot':
                        owner = 'copilot'
                    self.tasks_by_agent[owner].append(task)
                    self.tasks_by_priority[current_priority].append(task)

    def _sync_agent_view(self, agent: str):
        """Generate and write agent-specific view."""
        agent_file = self.by_agent_dir / f"{agent}.md"
        tasks = self.tasks_by_agent.get(agent, [])

        # Group by priority
        p0_tasks = [t for t in tasks if t['priority'] == 'P0']
        p1_tasks = [t for t in tasks if t['priority'] == 'P1']
        p2_tasks = [t for t in tasks if t['priority'] == 'P2']
        p3_tasks = [t for t in tasks if t['priority'] == 'P3']

        # Generate content
        content = self._generate_agent_view(agent, p0_tasks, p1_tasks, p2_tasks, p3_tasks)

        if self.dry_run:
            print(f"\n{BLUE}[DRY RUN] Would update {agent_file}:{RESET}")
            print(f"  P0 tasks: {len(p0_tasks)}")
            print(f"  P1 tasks: {len(p1_tasks)}")
            print(f"  P2 tasks: {len(p2_tasks)}")
            print(f"  P3 tasks: {len(p3_tasks)}")
        else:
            agent_file.write_text(content)
            print(f"{GREEN}✓{RESET} Synced {agent}: {len(tasks)} tasks")

    def _generate_agent_view(
        self,
        agent: str,
        p0_tasks: List[Dict],
        p1_tasks: List[Dict],
        p2_tasks: List[Dict],
        p3_tasks: List[Dict]
    ) -> str:
        """Generate markdown content for agent view."""
        agent_names = {
            'jules': 'Jules (Google AI Agent)',
            'claude-code': 'Claude Code (Anthropic)',
            'codex': 'CODEX (Deep System Infrastructure)',
            'human': 'Human Team',
        }

        specialties = {
            'jules': 'CI/CD, observability, security, monitoring',
            'claude-code': 'Testing, documentation, DSL validation, edge cases',
            'codex': 'Python infrastructure, registries, orchestrator, performance',
            'human': 'Strategic decisions, architecture review, priority assignment',
        }

        content = f"""# {agent_names.get(agent, agent.title())} Tasks

**Agent**: {agent_names.get(agent, agent.title())}
**Specialty**: {specialties.get(agent, 'General development')}

**Last Updated**: Auto-synced from TODO/MASTER_LOG.md

---

## Quick Stats

- **P0 (Critical)**: {len(p0_tasks)} tasks
- **P1 (High)**: {len(p1_tasks)} tasks
- **P2 (Medium)**: {len(p2_tasks)} tasks
- **P3 (Low)**: {len(p3_tasks)} tasks
- **Total**: {len(p0_tasks) + len(p1_tasks) + len(p2_tasks) + len(p3_tasks)} tasks

---

"""

        # Add P0 tasks if any
        if p0_tasks:
            content += "## Priority 0 (Critical - Drop Everything) ⚠️\n\n"
            content += "| ID | Task | Status | Effort | Notes |\n"
            content += "|----|------|--------|--------|-------|\n"
            for task in p0_tasks:
                content += f"| {task['id']} | {task['description']} | {task['status']} | {task['effort']} | {task['notes']} |\n"
            content += "\n---\n\n"

        # Add P1 tasks if any
        if p1_tasks:
            content += "## Priority 1 (High - This Sprint) 🔥\n\n"
            content += "| ID | Task | Status | Effort | Notes |\n"
            content += "|----|------|--------|--------|-------|\n"
            for task in p1_tasks:
                content += f"| {task['id']} | {task['description']} | {task['status']} | {task['effort']} | {task['notes']} |\n"
            content += "\n---\n\n"

        # Add P2 tasks if any
        if p2_tasks:
            content += "## Priority 2 (Medium - Next Sprint) 📋\n\n"
            content += "| ID | Task | Status | Effort | Notes |\n"
            content += "|----|------|--------|--------|-------|\n"
            for task in p2_tasks:
                content += f"| {task['id']} | {task['description']} | {task['status']} | {task['effort']} | {task['notes']} |\n"
            content += "\n---\n\n"

        # Add P3 tasks if any
        if p3_tasks:
            content += "## Priority 3 (Low - Backlog) 💭\n\n"
            content += "| ID | Task | Status | Effort | Notes |\n"
            content += "|----|------|--------|--------|-------|\n"
            for task in p3_tasks:
                content += f"| {task['id']} | {task['description']} | {task['status']} | {task['effort']} | {task['notes']} |\n"
            content += "\n---\n\n"

        # Add footer
        content += """## How to Use This View

1. **Pick a task** from the highest priority section with `PENDING` status
2. **Read the full details** in TODO/MASTER_LOG.md
3. **Update status** to `IN_PROGRESS` in MASTER_LOG when you start
4. **Complete the work** following LUKHAS standards
5. **Update status** to `COMPLETED` and add PR link when done
6. **Run sync** to update this view: `python3 scripts/todo/sync_agents.py`

---

**Note**: This file is auto-generated from MASTER_LOG.md. Do not edit manually.
To add or modify tasks, edit TODO/MASTER_LOG.md and run `python3 scripts/todo/sync_agents.py`.

**View more**: [TODO/MASTER_LOG.md](../MASTER_LOG.md) | [TODO/RULES_FOR_AGENTS.md](../RULES_FOR_AGENTS.md)
"""

        return content


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sync agent views from MASTER_LOG')
    parser.add_argument(
        '--agent',
        choices=AgentViewSyncer.AGENTS,
        help='Sync specific agent only'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    syncer = AgentViewSyncer(dry_run=args.dry_run)
    syncer.sync(specific_agent=args.agent)


if __name__ == "__main__":
    main()
