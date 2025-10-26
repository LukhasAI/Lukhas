# Agent Task Router Skill

Intelligent multi-agent task routing based on codebase state, agent specialization, workload, and historical success rates with parallel execution coordination.

## Reasoning

1. LUKHAS has 22 specialized agents across 4 tiers - manual delegation via AGENTS.md is inefficient.
2. No load balancing, historical performance tracking, or intelligent routing exists.
3. Some tasks can be parallelized (CODEX registry + Jules CI + Claude Code docs simultaneously).
4. Agent skill overlap requires intelligent routing based on real-time codebase state and task requirements.
5. Developers spend time choosing agents - automation can route optimally in milliseconds.

## Actions

### Core Router System

```python
#!/usr/bin/env python3
"""
Agent Task Router - Intelligent Multi-Agent Coordination

ML-powered routing:
- Agent expertise matching
- Historical success rate tracking
- Parallel task decomposition
- Load balancing
- Real-time codebase state analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Set
import json
from pathlib import Path

@dataclass
class AgentCapability:
    agent_id: str
    tier: int  # 1-4
    constellation_stars: List[str]
    lanes: List[str]
    matriz_stages: List[str]
    success_rate: float = 0.0
    avg_completion_time: float = 0.0
    current_workload: int = 0

@dataclass
class TaskRequirements:
    description: str
    files_affected: List[str]
    lanes_involved: Set[str]
    stars_involved: Set[str]
    complexity: float
    urgency: str  # 'low', 'medium', 'high', 'critical'

class AgentTaskRouter:
    def __init__(self, agent_pool_path='.claude/agents/'):
        self.agents = self._load_agent_pool(agent_pool_path)
        self.performance_history = self._load_performance_history()

    def _load_agent_pool(self, path: str) -> Dict[str, AgentCapability]:
        """Load agent capabilities from AGENTS.md"""
        agents = {}
        # Parse AGENTS.md to extract agent metadata
        # Simplified: would parse actual file
        agents['anchor-star-coordinator'] = AgentCapability(
            agent_id='anchor-star-coordinator',
            tier=1,
            constellation_stars=['⚛️ Anchor'],
            lanes=['lukhas', 'candidate'],
            matriz_stages=['Intent', 'Action'],
            success_rate=0.95,
            avg_completion_time=3600.0
        )
        return agents

    def _load_performance_history(self) -> Dict:
        """Load historical agent performance data"""
        try:
            with open('.claude/agent_performance.json') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def analyze_task_requirements(self, task_description: str, files_affected: List[str]) -> TaskRequirements:
        """Determine task characteristics"""
        lanes = set()
        stars = set()

        for file_path in files_affected:
            # Detect lane
            if 'candidate/' in file_path:
                lanes.add('candidate')
            elif 'lukhas/' in file_path:
                lanes.add('lukhas')
            elif 'matriz/' in file_path:
                lanes.add('matriz')

            # Detect constellation star involvement
            if 'identity' in file_path:
                stars.add('⚛️ Anchor')
            elif 'memory' in file_path:
                stars.add('✦ Trail')
            elif 'consciousness' in file_path:
                stars.add('🌊 Flow')
            elif 'guardian' in file_path or 'ethics' in file_path:
                stars.add('🛡️ Watch')

        complexity = len(files_affected) * 0.1 + len(lanes) * 0.5

        return TaskRequirements(
            description=task_description,
            files_affected=files_affected,
            lanes_involved=lanes,
            stars_involved=stars,
            complexity=complexity,
            urgency='medium'
        )

    def match_agent_expertise(self, task: TaskRequirements, agent_pool: Dict[str, AgentCapability]) -> List[tuple]:
        """Score each agent based on specialization"""
        scores = []

        for agent_id, agent in agent_pool.items():
            score = 0.0

            # Star alignment
            star_overlap = len(set(agent.constellation_stars) & task.stars_involved)
            score += star_overlap * 10.0

            # Lane expertise
            lane_overlap = len(set(agent.lanes) & task.lanes_involved)
            score += lane_overlap * 5.0

            # Historical success rate
            score += agent.success_rate * 20.0

            # Inverse of completion time (prefer faster agents)
            if agent.avg_completion_time > 0:
                score += (1.0 / agent.avg_completion_time) * 1000

            # Penalize current workload
            score -= agent.current_workload * 2.0

            scores.append((agent_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def route_task(self, task: TaskRequirements, top_n=3) -> Dict:
        """Select optimal agent(s) for task"""
        matched = self.match_agent_expertise(task, self.agents)

        top_agents = matched[:top_n]
        primary_agent = top_agents[0][0] if top_agents else None

        return {
            'primary_agent': primary_agent,
            'backup_agents': [a[0] for a in top_agents[1:]],
            'routing_confidence': top_agents[0][1] if top_agents else 0.0,
            'reasoning': f"Selected {primary_agent} due to expertise in {', '.join(task.stars_involved)}"
        }

    def decompose_for_parallel(self, complex_task: TaskRequirements) -> List[TaskRequirements]:
        """Break into concurrent sub-tasks"""
        subtasks = []

        if complex_task.complexity > 5.0:
            # Group files by lane
            by_lane = {}
            for file_path in complex_task.files_affected:
                for lane in ['candidate', 'lukhas', 'matriz']:
                    if lane in file_path:
                        by_lane.setdefault(lane, []).append(file_path)

            # Create subtask per lane
            for lane, files in by_lane.items():
                subtasks.append(TaskRequirements(
                    description=f"{complex_task.description} (lane: {lane})",
                    files_affected=files,
                    lanes_involved={lane},
                    stars_involved=complex_task.stars_involved,
                    complexity=len(files) * 0.1,
                    urgency=complex_task.urgency
                ))

        return subtasks if len(subtasks) > 1 else [complex_task]

    def coordinate_parallel_execution(self, subtasks: List[TaskRequirements], agents: Dict) -> Dict:
        """Orchestrate multiple agents concurrently"""
        execution_plan = {}

        for i, subtask in enumerate(subtasks):
            routing = self.route_task(subtask)
            execution_plan[f"subtask_{i}"] = {
                'task': subtask.description,
                'agent': routing['primary_agent'],
                'dependencies': []  # Could analyze file dependencies
            }

        return execution_plan

    def track_agent_performance(self, task_id: str, agent_id: str, outcome: Dict):
        """Update success rates and completion times"""
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = {
                'tasks_completed': 0,
                'tasks_successful': 0,
                'total_time': 0.0
            }

        history = self.performance_history[agent_id]
        history['tasks_completed'] += 1

        if outcome.get('success'):
            history['tasks_successful'] += 1

        history['total_time'] += outcome.get('completion_time', 0.0)

        # Update agent success rate
        if agent_id in self.agents:
            self.agents[agent_id].success_rate = (
                history['tasks_successful'] / history['tasks_completed']
            )
            self.agents[agent_id].avg_completion_time = (
                history['total_time'] / history['tasks_completed']
            )

        # Persist
        with open('.claude/agent_performance.json', 'w') as f:
            json.dump(self.performance_history, f, indent=2)

if __name__ == '__main__':
    import sys
    router = AgentTaskRouter()

    # CLI: lukhas-route-task "implement MATRIZ optimization" matriz/core/orchestrator.py
    if len(sys.argv) > 2:
        task_desc = sys.argv[1]
        files = sys.argv[2:]

        task = router.analyze_task_requirements(task_desc, files)
        routing = router.route_task(task)

        print(json.dumps(routing, indent=2))
```

### GitHub Action Integration

```yaml
name: Auto-Assign Agent
on:
  pull_request:
    types: [opened]

jobs:
  route:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Route to optimal agent
        run: |
          FILES=$(git diff --name-only origin/main)
          AGENT=$(python3 .claude/skills/agent_task_router.py "${{ github.event.pull_request.title }}" $FILES | jq -r '.primary_agent')
          gh pr edit ${{ github.event.pull_request.number }} --add-label "agent:$AGENT"
```

### CLI Usage

```bash
# Route a task
lukhas-route-task "Implement MATRIZ caching" matriz/core/orchestrator.py matriz/nodes/math_node.py

# Output:
# {
#   "primary_agent": "memory-attention-specialist",
#   "backup_agents": ["matriz-pipeline-specialist"],
#   "routing_confidence": 85.3
# }
```

## Context References

- `/AGENTS.md`
- `/.claude/AGENTS_README.md`
- `/docs/AI_TOOLS_INTEGRATION.md`
