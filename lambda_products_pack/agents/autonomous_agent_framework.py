"""
Lambda Autonomous Agent Framework
Following Sam Altman's vision: "AI agents joining the workforce in 2025"

This framework transforms Lambda Products into autonomous agents that can:
- Work for days without human intervention
- Make decisions independently
- Learn from their actions
- Collaborate with other agents
- Scale to thousands of instances
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent operational states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    COLLABORATING = "collaborating"
    PAUSED = "paused"
    ERROR = "error"


class AgentPriority(Enum):
    """Task priority levels for agents"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class AgentGoal:
    """Represents a high-level goal for an agent"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    priority: AgentPriority = AgentPriority.NORMAL
    progress: float = 0.0
    completed: bool = False
    
    def evaluate_progress(self, metrics: Dict[str, Any]) -> float:
        """Evaluate progress toward goal completion"""
        if not self.success_criteria:
            return 0.0
        
        met_criteria = 0
        for criterion, target in self.success_criteria.items():
            if criterion in metrics:
                if isinstance(target, (int, float)):
                    if metrics[criterion] >= target:
                        met_criteria += 1
                elif metrics[criterion] == target:
                    met_criteria += 1
        
        return met_criteria / len(self.success_criteria) if self.success_criteria else 0.0


@dataclass
class AgentTask:
    """Represents a specific task for an agent to execute"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str = ""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: AgentPriority = AgentPriority.NORMAL
    scheduled_time: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    completed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None


class AutonomousAgent:
    """
    Base class for autonomous Lambda agents
    Implements Sam Altman's vision of AI agents in the workforce
    """
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = AgentState.INITIALIZING
        self.goals: List[AgentGoal] = []
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.learning_memory: Dict[str, Any] = {}
        self.collaborators: Dict[str, 'AutonomousAgent'] = {}
        self.metrics: Dict[str, Any] = {
            "tasks_completed": 0,
            "goals_achieved": 0,
            "uptime_hours": 0,
            "decisions_made": 0,
            "errors_recovered": 0,
            "value_generated": 0
        }
        self.is_running = False
        self.start_time = None
        self.last_human_interaction = datetime.now()
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the agent with configuration"""
        logger.info(f"Initializing {self.agent_type} agent: {self.agent_id}")
        
        self.config = config
        self.max_autonomous_days = config.get("max_autonomous_days", 7)
        self.decision_threshold = config.get("decision_threshold", 0.8)
        self.learning_rate = config.get("learning_rate", 0.1)
        
        self.state = AgentState.IDLE
        self.start_time = datetime.now()
        
        return True
    
    async def set_goal(self, goal: AgentGoal):
        """Set a high-level goal for the agent to achieve"""
        logger.info(f"Agent {self.agent_id} received goal: {goal.description}")
        self.goals.append(goal)
        
        # Decompose goal into tasks
        tasks = await self.decompose_goal(goal)
        for task in tasks:
            await self.add_task(task)
    
    async def decompose_goal(self, goal: AgentGoal) -> List[AgentTask]:
        """Decompose a high-level goal into actionable tasks"""
        # This is where GPT-5 integration would help
        # For now, use rule-based decomposition
        tasks = []
        
        # Example decomposition logic
        if "optimize" in goal.description.lower():
            tasks.append(AgentTask(
                goal_id=goal.id,
                action="analyze_current_state",
                parameters={"target": "performance_metrics"},
                priority=AgentPriority.HIGH
            ))
            tasks.append(AgentTask(
                goal_id=goal.id,
                action="identify_bottlenecks",
                parameters={"threshold": 0.7},
                priority=AgentPriority.HIGH
            ))
            tasks.append(AgentTask(
                goal_id=goal.id,
                action="implement_optimizations",
                parameters={"auto_approve": True},
                priority=AgentPriority.NORMAL
            ))
        
        return tasks
    
    async def add_task(self, task: AgentTask):
        """Add a task to the agent's queue"""
        self.task_queue.append(task)
        # Sort by priority
        self.task_queue.sort(key=lambda t: (t.priority.value, t.scheduled_time or datetime.max))
    
    async def run(self):
        """Main autonomous execution loop"""
        self.is_running = True
        logger.info(f"Agent {self.agent_id} starting autonomous operation")
        
        while self.is_running:
            try:
                # Check if we've exceeded autonomous operation limit
                if await self.should_request_human_input():
                    await self.request_human_oversight()
                
                # Update state
                await self.update_state()
                
                # Execute based on current state
                if self.state == AgentState.IDLE:
                    await self.plan_next_action()
                
                elif self.state == AgentState.PLANNING:
                    await self.execute_planning()
                
                elif self.state == AgentState.EXECUTING:
                    await self.execute_tasks()
                
                elif self.state == AgentState.LEARNING:
                    await self.learn_from_experience()
                
                elif self.state == AgentState.COLLABORATING:
                    await self.collaborate_with_agents()
                
                # Update metrics
                await self.update_metrics()
                
                # Brief pause to prevent CPU overload
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Agent {self.agent_id} encountered error: {e}")
                self.state = AgentState.ERROR
                await self.recover_from_error(e)
    
    async def should_request_human_input(self) -> bool:
        """Determine if human oversight is needed"""
        time_since_human = datetime.now() - self.last_human_interaction
        
        # Request human input if:
        # 1. Been running autonomously for too long
        if time_since_human > timedelta(days=self.max_autonomous_days):
            return True
        
        # 2. Encountered critical decisions with low confidence
        if hasattr(self, 'last_decision_confidence'):
            if self.last_decision_confidence < self.decision_threshold:
                return True
        
        # 3. Error rate is too high
        if self.metrics.get("error_rate", 0) > 0.1:
            return True
        
        return False
    
    async def request_human_oversight(self):
        """Request human oversight for critical decisions"""
        logger.info(f"Agent {self.agent_id} requesting human oversight")
        self.state = AgentState.PAUSED
        # In production, this would send notifications
        # For now, just log
        self.last_human_interaction = datetime.now()
    
    async def update_state(self):
        """Update agent state based on current conditions"""
        if self.state == AgentState.ERROR:
            return
        
        if self.task_queue and self.state == AgentState.IDLE:
            self.state = AgentState.PLANNING
        elif not self.task_queue and self.goals:
            self.state = AgentState.PLANNING
        elif self.should_learn():
            self.state = AgentState.LEARNING
    
    def should_learn(self) -> bool:
        """Determine if agent should enter learning mode"""
        # Learn after every 10 completed tasks
        return len(self.completed_tasks) % 10 == 0 and len(self.completed_tasks) > 0
    
    async def plan_next_action(self):
        """Plan the next action to take"""
        self.state = AgentState.PLANNING
        
        # Review goals
        for goal in self.goals:
            if not goal.completed:
                # Check if we need more tasks for this goal
                goal.progress = goal.evaluate_progress(self.metrics)
                if goal.progress < 1.0:
                    # Generate more tasks
                    new_tasks = await self.decompose_goal(goal)
                    for task in new_tasks:
                        await self.add_task(task)
    
    async def execute_planning(self):
        """Execute planning phase"""
        # Move to execution if we have tasks
        if self.task_queue:
            self.state = AgentState.EXECUTING
        else:
            self.state = AgentState.IDLE
    
    async def execute_tasks(self):
        """Execute tasks from the queue"""
        if not self.task_queue:
            self.state = AgentState.IDLE
            return
        
        task = self.task_queue.pop(0)
        
        try:
            # Execute the task
            result = await self.execute_single_task(task)
            task.result = result
            task.completed = True
            self.completed_tasks.append(task)
            self.metrics["tasks_completed"] += 1
            
            logger.info(f"Agent {self.agent_id} completed task: {task.action}")
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Re-queue the task
                await self.add_task(task)
                logger.warning(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                logger.error(f"Task {task.id} failed after {task.max_retries} retries")
                self.completed_tasks.append(task)
    
    async def execute_single_task(self, task: AgentTask) -> Any:
        """Execute a single task - override in subclasses"""
        # This is where specific Lambda Product logic would go
        await asyncio.sleep(0.1)  # Simulate work
        return {"status": "completed", "task_id": task.id}
    
    async def learn_from_experience(self):
        """Learn from completed tasks to improve future performance"""
        self.state = AgentState.LEARNING
        
        # Analyze completed tasks
        success_rate = sum(1 for t in self.completed_tasks if not t.error) / len(self.completed_tasks)
        
        # Update learning memory
        self.learning_memory["success_rate"] = success_rate
        self.learning_memory["common_errors"] = {}
        
        for task in self.completed_tasks:
            if task.error:
                error_type = task.error.split(":")[0]
                self.learning_memory["common_errors"][error_type] = \
                    self.learning_memory["common_errors"].get(error_type, 0) + 1
        
        # Adjust strategies based on learning
        if success_rate < 0.8:
            self.decision_threshold *= 0.9  # Be more cautious
        else:
            self.decision_threshold = min(0.95, self.decision_threshold * 1.05)
        
        logger.info(f"Agent {self.agent_id} learned: success_rate={success_rate:.2%}")
        
        self.state = AgentState.IDLE
    
    async def collaborate_with_agents(self):
        """Collaborate with other agents"""
        # Share knowledge and coordinate tasks
        for agent_id, agent in self.collaborators.items():
            # Share successful strategies
            if self.learning_memory.get("success_rate", 0) > 0.9:
                await agent.receive_knowledge(self.learning_memory)
    
    async def receive_knowledge(self, knowledge: Dict[str, Any]):
        """Receive knowledge from another agent"""
        # Merge knowledge into our learning memory
        for key, value in knowledge.items():
            if key not in self.learning_memory:
                self.learning_memory[key] = value
    
    async def update_metrics(self):
        """Update agent metrics"""
        if self.start_time:
            uptime = datetime.now() - self.start_time
            self.metrics["uptime_hours"] = uptime.total_seconds() / 3600
        
        # Calculate value generated (domain-specific)
        self.metrics["value_generated"] = self.calculate_value_generated()
    
    def calculate_value_generated(self) -> float:
        """Calculate the value generated by this agent"""
        # Base value on tasks completed and goals achieved
        task_value = self.metrics["tasks_completed"] * 100
        goal_value = self.metrics["goals_achieved"] * 1000
        return task_value + goal_value
    
    async def recover_from_error(self, error: Exception):
        """Recover from an error state"""
        logger.info(f"Agent {self.agent_id} recovering from error: {error}")
        self.metrics["errors_recovered"] += 1
        
        # Clear current task queue
        self.task_queue.clear()
        
        # Reset to idle state
        self.state = AgentState.IDLE
        
        # Log error for learning
        self.learning_memory["last_error"] = str(error)
        self.learning_memory["error_timestamp"] = datetime.now().isoformat()
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        logger.info(f"Shutting down agent {self.agent_id}")
        self.is_running = False
        
        # Save state for resumption
        await self.save_state()
    
    async def save_state(self):
        """Save agent state for later resumption"""
        state_file = Path(f"data/agents/{self.agent_id}_state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "goals": [
                {
                    "id": g.id,
                    "description": g.description,
                    "progress": g.progress,
                    "completed": g.completed
                }
                for g in self.goals
            ],
            "metrics": self.metrics,
            "learning_memory": self.learning_memory,
            "last_save": datetime.now().isoformat()
        }
        
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "goals_active": len([g for g in self.goals if not g.completed]),
            "tasks_pending": len(self.task_queue),
            "tasks_completed": self.metrics["tasks_completed"],
            "uptime_hours": self.metrics["uptime_hours"],
            "value_generated": self.metrics["value_generated"],
            "last_human_interaction": self.last_human_interaction.isoformat()
        }


class AgentOrchestrator:
    """
    Orchestrates multiple autonomous agents
    Implements Sam Altman's vision of AI agent workforce
    """
    
    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.agent_pools: Dict[str, List[AutonomousAgent]] = {}
        
    async def deploy_agent(self, agent: AutonomousAgent, config: Dict[str, Any]):
        """Deploy an autonomous agent"""
        await agent.initialize(config)
        self.agents[agent.agent_id] = agent
        
        # Add to pool
        if agent.agent_type not in self.agent_pools:
            self.agent_pools[agent.agent_type] = []
        self.agent_pools[agent.agent_type].append(agent)
        
        # Start autonomous operation
        asyncio.create_task(agent.run())
        
        logger.info(f"Deployed {agent.agent_type} agent: {agent.agent_id}")
    
    async def deploy_agent_fleet(self, agent_type: str, count: int, config: Dict[str, Any]):
        """Deploy a fleet of agents"""
        for i in range(count):
            agent_id = f"{agent_type}_{i:03d}"
            agent = AutonomousAgent(agent_id, agent_type)
            await self.deploy_agent(agent, config)
    
    async def get_active_agents(self) -> List[AutonomousAgent]:
        """Get list of all active agents"""
        active_agents = []
        for agent in self.agents.values():
            status = agent.get_status()  # get_status() is not async
            if status.get("state") in ["running", "active", "processing"]:
                active_agents.append(agent)
        return active_agents
    
    async def shutdown_all_agents(self):
        """Shutdown all active agents"""
        for agent in self.agents.values():
            await agent.shutdown()
        self.agents.clear()
        self.agent_pools.clear()
    
    def get_fleet_status(self) -> Dict[str, Any]:
        """Get status of entire agent fleet"""
        return {
            "total_agents": len(self.agents),
            "agents_by_type": {
                agent_type: len(agents)
                for agent_type, agents in self.agent_pools.items()
            },
            "total_value_generated": sum(
                agent.metrics["value_generated"]
                for agent in self.agents.values()
            ),
            "total_tasks_completed": sum(
                agent.metrics["tasks_completed"]
                for agent in self.agents.values()
            ),
            "agents_status": [
                agent.get_status()
                for agent in self.agents.values()
            ]
        }
    
    async def scale_fleet(self, agent_type: str, target_count: int):
        """Scale agent fleet up or down"""
        current_count = len(self.agent_pools.get(agent_type, []))
        
        if target_count > current_count:
            # Scale up
            await self.deploy_agent_fleet(
                agent_type,
                target_count - current_count,
                {"auto_scale": True}
            )
        elif target_count < current_count:
            # Scale down
            agents_to_remove = current_count - target_count
            for i in range(agents_to_remove):
                agent = self.agent_pools[agent_type].pop()
                await agent.shutdown()
                del self.agents[agent.agent_id]


# Example usage for Lambda Products as Autonomous Agents
if __name__ == "__main__":
    async def main():
        # Create orchestrator
        orchestrator = AgentOrchestrator()
        
        # Deploy NIΛS agent for emotional intelligence management
        nias_agent = AutonomousAgent("nias_001", "NIΛS")
        await orchestrator.deploy_agent(nias_agent, {
            "max_autonomous_days": 7,
            "decision_threshold": 0.85,
            "learning_rate": 0.15
        })
        
        # Set a goal for the agent
        goal = AgentGoal(
            description="Optimize company-wide emotional well-being",
            success_criteria={
                "employee_satisfaction": 0.9,
                "stress_levels": 0.3,
                "communication_effectiveness": 0.85
            },
            deadline=datetime.now() + timedelta(days=30),
            priority=AgentPriority.HIGH
        )
        
        await nias_agent.set_goal(goal)
        
        # Let agent run autonomously
        await asyncio.sleep(10)
        
        # Check status
        print(json.dumps(orchestrator.get_fleet_status(), indent=2))
    
    asyncio.run(main())