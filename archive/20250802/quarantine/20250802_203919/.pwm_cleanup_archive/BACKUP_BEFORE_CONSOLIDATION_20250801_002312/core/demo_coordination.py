#!/usr/bin/env python3
"""
Demonstration of Decentralized Agent Coordination
Shows how agents autonomously form working groups to solve complex tasks
"""

import asyncio
import logging
from typing import List

from actor_system import *  # TODO: Specify imports
from agent_coordination import *  # TODO: Specify imports
    CoordinationHub, AutonomousAgent, DataProcessorAgent,
    AnalyticsAgent, MLModelAgent, Skill, SkillLevel, MessagePriority
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ProjectManagerAgent(AutonomousAgent):
    """Agent that manages complex projects by coordinating other agent"""

    def __init__(self, agent_id: str):
        skills = [
            Skill("project_planning", SkillLevel.EXPERT, success_rate=0.95),
            Skill("task_decomposition", SkillLevel.EXPERT, success_rate=0.93),
            Skill("coordination", SkillLevel.ADVANCED, success_rate=0.90)
        ]
        super().__init__(agent_id, skills)

    async def manage_ml_pipeline(self):
        """Coordinate a complete ML pipeline project"""
        print(f"\n🎯 {self.actor_id}: Starting ML Pipeline Project")

        # Phase 1: Data preparation
        print("\n📊 Phase 1: Data Preparation")
        task1_id = await self.announce_task(
            description="Prepare customer dataset for ML training",
            required_skills=[
                ("data_cleaning", SkillLevel.INTERMEDIATE),
                ("data_validation", SkillLevel.INTERMEDIATE),
                ("etl_pipeline", SkillLevel.NOVICE)
            ],
            priority=MessagePriority.HIGH,
            metadata={"phase": 1, "dataset": "customers_2024"}
        )
        print(f"   ✓ Announced data preparation task: {task1_id}")

        # Wait for phase 1 completion
        await asyncio.sleep(3)

        # Phase 2: Analysis
        print("\n📈 Phase 2: Statistical Analysis")
        task2_id = await self.announce_task(
            description="Perform exploratory data analysis and feature engineering",
            required_skills=[
                ("statistical_analysis", SkillLevel.ADVANCED),
                ("anomaly_detection", SkillLevel.INTERMEDIATE),
                ("report_generation", SkillLevel.NOVICE)
            ],
            priority=MessagePriority.NORMAL,
            metadata={"phase": 2, "depends_on": task1_id}
        )
        print(f"   ✓ Announced analysis task: {task2_id}")

        await asyncio.sleep(3)

        # Phase 3: Model development
        print("\n🤖 Phase 3: Model Development")
        task3_id = await self.announce_task(
            description="Train and evaluate customer churn prediction model",
            required_skills=[
                ("model_training", SkillLevel.INTERMEDIATE),
                ("model_evaluation", SkillLevel.ADVANCED),
                ("hyperparameter_tuning", SkillLevel.INTERMEDIATE)
            ],
            priority=MessagePriority.HIGH,
            metadata={"phase": 3, "model_type": "churn_prediction"}
        )
        print(f"   ✓ Announced model development task: {task3_id}")

        print("\n✅ All project phases initiated!")


async def simulate_dynamic_environment():
    """Simulate a dynamic environment with multiple concurrent project"""

    print("🌟 Starting Decentralized Agent Coordination Demo")
    print("=" * 60)

    # Create actor system
    system = ActorSystem()
    await system.start()

    # Create coordination hub
    print("\n🏢 Setting up Coordination Hub...")
    hub_ref = await system.create_actor(CoordinationHub, "central_hub")
    hub = system.get_actor("central_hub")

    # Create diverse agent pool
    print("\n👥 Creating Agent Pool...")
    agents = []

    # Data processing specialists
    for i in range(3):
        agent_ref = await system.create_actor(DataProcessorAgent, f"data_specialist_{i}")
        agent = system.get_actor(f"data_specialist_{i}")
        agent.coord_hub = hub_ref
        agents.append((agent_ref, agent))
        print(f"   ✓ Created Data Specialist {i}")

    # Analytics specialists
    for i in range(2):
        agent_ref = await system.create_actor(AnalyticsAgent, f"analytics_expert_{i}")
        agent = system.get_actor(f"analytics_expert_{i}")
        agent.coord_hub = hub_ref
        agents.append((agent_ref, agent))
        print(f"   ✓ Created Analytics Expert {i}")

    # ML specialists
    for i in range(2):
        agent_ref = await system.create_actor(MLModelAgent, f"ml_engineer_{i}")
        agent = system.get_actor(f"ml_engineer_{i}")
        agent.coord_hub = hub_ref
        agents.append((agent_ref, agent))
        print(f"   ✓ Created ML Engineer {i}")

    # Project manager
    pm_ref = await system.create_actor(ProjectManagerAgent, "project_manager")
    pm = system.get_actor("project_manager")
    pm.coord_hub = hub_ref
    print("   ✓ Created Project Manager")

    # Register all skills
    print("\n📋 Registering Agent Skills...")
    for agent_ref, agent in agents:
        for skill in agent.skills:
            await hub.skill_registry.register_skill(agent.actor_id, skill)
            print(f"   ✓ {agent.actor_id}: {skill.name} (Level: {skill.level.name})")

    # Register PM skills
    for skill in pm.skills:
        await hub.skill_registry.register_skill(pm.actor_id, skill)

    print("\n" + "=" * 60)
    print("🚀 STARTING AUTONOMOUS COORDINATION")
    print("=" * 60)

    # Start the ML pipeline project
    await pm.manage_ml_pipeline()

    # Let coordination happen
    print("\n⏳ Agents coordinating autonomously...")
    await asyncio.sleep(5)

    # Show final statistics
    print("\n" + "=" * 60)
    print("📊 COORDINATION STATISTICS")
    print("=" * 60)

    print(f"\n🏢 Hub Statistics:")
    print(f"   * Active Announcements: {len(hub.active_announcements)}")
    print(f"   * Working Groups Formed: {len(hub.working_groups)}")
    print(f"   * Total Agents: {len(agents) + 1}")

    # Show working groups
    if hub.working_groups:
        print(f"\n👥 Working Groups:")
        for task_id, group in hub.working_groups.items():
            print(f"\n   Group {group.group_id[:8]}...")
            print(f"   * Task: {group.task.description}")
            print(f"   * Status: {group.status.value}")
            print(f"   * Members: {len(group.members)}")
            print(f"   * Skills Covered: {list(group.skills_covered.keys())}")

            for member_id in group.members:
                agent_actor = system.get_actor(member_id)
                if agent_actor:
                    print(f"     - {member_id} (Availability: {agent_actor.availability:.1%})")

    # Show skill registry stats
    print(f"\n🎯 Skill Distribution:")
    skill_counts = {}
    for agent_id, skills in hub.skill_registry._skills_by_agent.items():
        for skill in skills:
            if skill.name not in skill_counts:
                skill_counts[skill.name] = 0
            skill_counts[skill.name] += 1

    for skill_name, count in sorted(skill_counts.items()):
        agents_with_skill = await hub.skill_registry.find_agents_with_skill(skill_name)
        avg_level = sum(s.level.value for _, s in agents_with_skill) / len(agents_with_skill)
        print(f"   * {skill_name}: {count} agents (avg level: {avg_level:.1f})")

    print("\n* Demo Complete!")

    # Cleanup
    await system.stop()


async def demonstrate_resilience():
    """Demonstrate system resilience when agents fail"""

    print("\n🛡️ RESILIENCE DEMONSTRATION")
    print("=" * 60)

    system = ActorSystem()
    await system.start()

    # Setup basic system
    hub_ref = await system.create_actor(CoordinationHub, "hub")

    # Create agents with varying reliability
    reliable_agent = await system.create_actor(DataProcessorAgent, "reliable_agent")
    unreliable_agent = await system.create_actor(DataProcessorAgent, "unreliable_agent")

    reliable = system.get_actor("reliable_agent")
    unreliable = system.get_actor("unreliable_agent")

    reliable.coord_hub = hub_ref
    unreliable.coord_hub = hub_ref

    # Modify unreliable agent's skills to have lower success rate
    for skill in unreliable.skills:
        skill.success_rate = 0.5

    print("Created agents with different reliability levels")

    # Announce critical task
    critical_task = await reliable.announce_task(
        description="Critical data processing - needs high reliability",
        required_skills=[("data_cleaning", SkillLevel.INTERMEDIATE)],
        priority=MessagePriority.SYSTEM,
        metadata={"critical": True, "min_success_rate": 0.9}
    )

    print(f"Announced critical task: {critical_task}")

    await asyncio.sleep(2)

    # The system should prefer the reliable agent
    hub = system.get_actor("hub")
    if critical_task in hub.working_groups:
        group = hub.working_groups[critical_task]
        print(f"Working group formed with members: {list(group.members.keys())}")
        print("System selected agents based on reliability metrics!")

    await system.stop()


# Main execution
if __name__ == "__main__":
    print("Decentralized Agent Coordination System Demo")
    print("==========================================\n")

    # Run main demo
    asyncio.run(simulate_dynamic_environment())

    # Run resilience demo
    asyncio.run(demonstrate_resilience())