"""
Tests for Decentralized Agent Coordination System
"""

import asyncio
import time

import pytest

from core.actor_system import ActorMessage, ActorRef, ActorSystem
from core.agent_coordination import (
    AnalyticsAgent,
    AutonomousAgent,
    CoordinationHub,
    CoordinationProtocol,
    DataProcessorAgent,
    MessagePriority,
    Skill,
    SkillLevel,
    SkillRegistry,
    TaskAnnouncement,
    WorkingGroup,
)


class TestSkillRegistry:
    """Test skill registry functionality"""

    @pytest.mark.asyncio
    async def test_skill_registration(self):
        """Test registering and finding skills"""
        registry = SkillRegistry()

        # Register skills
        skill1 = Skill("data_cleaning", SkillLevel.EXPERT, success_rate=0.95)
        skill2 = Skill("data_cleaning", SkillLevel.NOVICE, success_rate=0.75)
        skill3 = Skill("analytics", SkillLevel.ADVANCED, success_rate=0.90)

        await registry.register_skill("agent1", skill1)
        await registry.register_skill("agent2", skill2)
        await registry.register_skill("agent1", skill3)

        # Find agents with data cleaning skill
        agents = await registry.find_agents_with_skill("data_cleaning")
        assert len(agents) == 2

        # Should be sorted by level (expert first)
        assert agents[0][0] == "agent1"
        assert agents[0][1].level == SkillLevel.EXPERT

        # Find with minimum level
        experts = await registry.find_agents_with_skill(
            "data_cleaning", SkillLevel.ADVANCED
        )
        assert len(experts) == 1
        assert experts[0][0] == "agent1"

    @pytest.mark.asyncio
    async def test_skill_update(self):
        """Test updating existing skills"""
        registry = SkillRegistry()

        # Register initial skill
        skill1 = Skill("coding", SkillLevel.INTERMEDIATE, success_rate=0.80)
        await registry.register_skill("agent1", skill1)

        # Update skill
        skill2 = Skill("coding", SkillLevel.ADVANCED, success_rate=0.90)
        await registry.register_skill("agent1", skill2)

        # Should have updated skill
        agents = await registry.find_agents_with_skill("coding")
        assert len(agents) == 1
        assert agents[0][1].level == SkillLevel.ADVANCED
        assert agents[0][1].success_rate == 0.90

    @pytest.mark.asyncio
    async def test_agent_unregistration(self):
        """Test removing all skills for an agent"""
        registry = SkillRegistry()

        # Register skills
        await registry.register_skill("agent1", Skill("skill1", SkillLevel.EXPERT))
        await registry.register_skill("agent1", Skill("skill2", SkillLevel.ADVANCED))
        await registry.register_skill("agent2", Skill("skill1", SkillLevel.NOVICE))

        # Unregister agent1
        await registry.unregister_agent("agent1")

        # Should only find agent2's skills
        agents = await registry.find_agents_with_skill("skill1")
        assert len(agents) == 1
        assert agents[0][0] == "agent2"


class TestWorkingGroup:
    """Test working group functionality"""

    def test_group_formation(self):
        """Test basic group formation"""
        from core.actor_system import ActorRef

        # Create mock announcement
        # Create a minimal mock system for ActorRef
        class MockSystem:
            pass

        mock_system = MockSystem()
        initiator_ref = ActorRef("initiator", mock_system)

        announcement = TaskAnnouncement(
            task_id="test-task",
            description="Test task",
            required_skills=[
                ("skill1", SkillLevel.INTERMEDIATE),
                ("skill2", SkillLevel.ADVANCED),
            ],
            initiator=initiator_ref,
        )

        group = WorkingGroup(
            group_id="test-group",
            task=announcement,
            leader=announcement.initiator,
            members={},
            skills_covered={},
        )

        # Add members
        agent1_ref = ActorRef("agent1", mock_system)
        agent1_skills = [Skill("skill1", SkillLevel.EXPERT)]
        group.add_member("agent1", agent1_ref, agent1_skills)

        assert "agent1" in group.members
        assert "skill1" in group.skills_covered
        assert "agent1" in group.skills_covered["skill1"]

        # Not all skills covered yet
        assert not group.all_skills_covered()

        # Add agent with second skill
        agent2_ref = ActorRef("agent2", mock_system)
        agent2_skills = [Skill("skill2", SkillLevel.ADVANCED)]
        group.add_member("agent2", agent2_ref, agent2_skills)

        # Now all skills covered
        assert group.all_skills_covered()

    def test_task_expiry(self):
        """Test task announcement expiry"""

        class MockSystem:
            pass

        announcement = TaskAnnouncement(
            task_id="test",
            description="Test",
            required_skills=[],
            initiator=ActorRef("test", MockSystem()),
            deadline=time.time() - 1,  # Already expired
        )

        assert announcement.is_expired()

        # Test default expiry
        old_announcement = TaskAnnouncement(
            task_id="old",
            description="Old task",
            required_skills=[],
            initiator=ActorRef("test", MockSystem()),
            announced_at=time.time() - 400,  # Over 5 minutes ago
        )

        assert old_announcement.is_expired()


class TestCoordinationHub:
    """Test coordination hub functionality"""

    @pytest.mark.asyncio
    async def test_hub_lifecycle(self):
        """Test hub start/stop"""
        system = ActorSystem()
        await system.start()

        hub_ref = await system.create_actor(CoordinationHub, "test_hub")
        hub = system.get_actor("test_hub")

        # Verify hub is running
        assert hub._running
        assert hub._maintenance_task is not None

        # Stop hub
        await hub.stop()
        assert not hub._running

        await system.stop()

    @pytest.mark.asyncio
    async def test_task_announcement(self):
        """Test task announcement handling"""
        system = ActorSystem()
        await system.start()

        hub_ref = await system.create_actor(CoordinationHub, "hub")
        hub = system.get_actor("hub")

        # Create test announcement
        initiator_ref = await system.create_actor(AutonomousAgent, "initiator")

        result = await hub_ref.ask(
            CoordinationProtocol.TASK_ANNOUNCE,
            {
                "task_id": "test-123",
                "description": "Test task",
                "required_skills": [["test_skill", SkillLevel.INTERMEDIATE.value]],
                "initiator": initiator_ref.to_dict(),
                "priority": MessagePriority.NORMAL.value,
            },
        )

        assert result["status"] == "announced"
        assert "test-123" in hub.active_announcements

        await system.stop()

    @pytest.mark.asyncio
    async def test_skill_offer_handling(self):
        """Test handling skill offers from agents"""
        system = ActorSystem()
        await system.start()

        hub_ref = await system.create_actor(CoordinationHub, "hub")
        initiator_ref = await system.create_actor(AutonomousAgent, "initiator")
        agent_ref = await system.create_actor(DataProcessorAgent, "agent1")

        # First announce a task
        task_id = "test-task-456"
        await hub_ref.ask(
            CoordinationProtocol.TASK_ANNOUNCE,
            {
                "task_id": task_id,
                "description": "Process data",
                "required_skills": [["data_cleaning", SkillLevel.INTERMEDIATE.value]],
                "initiator": initiator_ref.to_dict(),
                "max_group_size": 3,
            },
        )

        # Make skill offer
        result = await hub_ref.ask(
            CoordinationProtocol.SKILL_OFFER,
            {
                "agent_ref": agent_ref.to_dict(),
                "agent_id": "agent1",
                "offered_skills": [
                    Skill(
                        name="data_cleaning", level=SkillLevel.EXPERT, success_rate=0.95
                    )
                ],
                "availability": 0.8,
                "estimated_time": 30.0,
            },
            correlation_id=task_id,
        )

        assert result["status"] == "processed"

        # Check that working group was created
        hub = system.get_actor("hub")
        assert task_id in hub.working_groups

        await system.stop()

    @pytest.mark.asyncio
    async def test_task_cancellation(self):
        """Test task cancellation"""
        system = ActorSystem()
        await system.start()

        hub_ref = await system.create_actor(CoordinationHub, "hub")
        initiator_ref = await system.create_actor(AutonomousAgent, "initiator")

        # Announce task
        task_id = "cancel-test"
        await hub_ref.ask(
            CoordinationProtocol.TASK_ANNOUNCE,
            {
                "task_id": task_id,
                "description": "Task to cancel",
                "required_skills": [],
                "initiator": initiator_ref.to_dict(),
            },
        )

        hub = system.get_actor("hub")
        assert task_id in hub.active_announcements

        # Cancel task
        result = await hub_ref.ask(
            CoordinationProtocol.TASK_CANCEL, {"task_id": task_id}
        )
        assert result["status"] == "cancelled"
        assert task_id not in hub.active_announcements

        await system.stop()


class TestAutonomousAgent:
    """Test autonomous agent functionality"""

    @pytest.mark.asyncio
    async def test_agent_skills(self):
        """Test agent skill management"""
        skills = [
            Skill("coding", SkillLevel.ADVANCED, success_rate=0.92),
            Skill("testing", SkillLevel.EXPERT, success_rate=0.96),
        ]

        agent = AutonomousAgent("test_agent", skills)
        assert len(agent.skills) == 2
        assert agent.availability == 1.0

    @pytest.mark.asyncio
    async def test_task_announcement_by_agent(self):
        """Test agent announcing a task"""
        system = ActorSystem()
        await system.start()

        # Create hub and agent
        hub_ref = await system.create_actor(CoordinationHub, "hub")
        agent_ref = await system.create_actor(AutonomousAgent, "agent", skills=[])

        agent = system.get_actor("agent")
        agent.coord_hub = hub_ref

        # Announce task
        task_id = await agent.announce_task(
            description="Need help with data processing",
            required_skills=[("data_cleaning", SkillLevel.INTERMEDIATE)],
            priority=MessagePriority.HIGH,
        )

        assert task_id is not None

        # Verify task was announced
        hub = system.get_actor("hub")
        assert any(ann.task_id == task_id for ann in hub.active_announcements.values())

        await system.stop()

    @pytest.mark.asyncio
    async def test_skill_query_response(self):
        """Test agent responding to skill queries"""
        system = ActorSystem()
        await system.start()

        # Create agent with specific skills
        agent_ref = await system.create_actor(DataProcessorAgent, "data_agent")

        # Create a mock task announcement
        initiator_ref = await system.create_actor(AutonomousAgent, "initiator")

        # Send skill query
        result = await agent_ref.ask(
            CoordinationProtocol.SKILL_QUERY,
            {
                "task_id": "test-task",
                "description": "Clean data",
                "required_skills": [("data_cleaning", SkillLevel.INTERMEDIATE)],
                "initiator": initiator_ref.to_dict(),
                "priority": MessagePriority.NORMAL,
            },
        )

        # Agent should offer since it has expert level data_cleaning
        assert result["status"] == "offered"

        await system.stop()

    @pytest.mark.asyncio
    async def test_group_invite_handling(self):
        """Test agent handling group invites"""
        system = ActorSystem()
        await system.start()

        agent_ref = await system.create_actor(AutonomousAgent, "agent")
        hub_ref = await system.create_actor(CoordinationHub, "hub")

        # Send group invite
        result = await hub_ref.ask(
            CoordinationProtocol.GROUP_INVITE,
            {
                "group_id": "test-group",
                "task": {
                    "task_id": "test-task",
                    "description": "Test task",
                    "required_skills": [],
                },
                "role": "member",
                "agent_ref": agent_ref.to_dict(),
            },
        )

        # Default implementation accepts if availability > 0.3
        assert result["status"] == "accepted"

        await system.stop()


class TestIntegration:
    """Integration tests for the coordination system"""

    @pytest.mark.asyncio
    async def test_end_to_end_coordination(self):
        """Test complete coordination flow"""
        system = ActorSystem()
        await system.start()

        # Create hub
        hub_ref = await system.create_actor(CoordinationHub, "hub")
        hub = system.get_actor("hub")

        # Create agents
        agents = []
        for i in range(3):
            if i == 0:
                agent_ref = await system.create_actor(
                    DataProcessorAgent, f"data_agent_{i}"
                )
            else:
                agent_ref = await system.create_actor(
                    AnalyticsAgent, f"analytics_agent_{i}"
                )

            agent = system.get_actor(agent_ref.actor_id)
            agent.coord_hub = hub_ref
            agents.append((agent_ref, agent))

        # Register all agent skills
        for agent_ref, agent in agents:
            for skill in agent.skills:
                await hub.skill_registry.register_skill(agent.actor_id, skill)

        # Agent 0 announces a task
        initiator = agents[0][1]
        task_id = await initiator.announce_task(
            description="Analyze cleaned data",
            required_skills=[
                ("data_cleaning", SkillLevel.INTERMEDIATE),
                ("statistical_analysis", SkillLevel.INTERMEDIATE),
            ],
        )

        # Wait for coordination
        await asyncio.sleep(1)

        # Check that working group was formed
        assert len(hub.working_groups) > 0

        # Verify group has members
        group = next(iter(hub.working_groups.values()))
        assert len(group.members) > 0

        await system.stop()

    @pytest.mark.asyncio
    async def test_skill_metrics_update(self):
        """Test skill metrics updates after task completion"""
        skill = Skill("test_skill", SkillLevel.INTERMEDIATE, success_rate=0.8)

        # Initial metrics
        assert skill.total_tasks == 0
        assert skill.success_rate == 0.8
        assert skill.avg_completion_time == 0.0

        # Successful task
        skill.update_metrics(success=True, completion_time=10.0)
        assert skill.total_tasks == 1
        assert skill.success_rate == 1.0
        assert skill.avg_completion_time == 10.0

        # Failed task
        skill.update_metrics(success=False, completion_time=5.0)
        assert skill.total_tasks == 2
        assert skill.success_rate == 0.5
        assert skill.avg_completion_time == 7.5

        # Another successful task
        skill.update_metrics(success=True, completion_time=15.0)
        assert skill.total_tasks == 3
        assert skill.success_rate == pytest.approx(0.666, rel=0.01)
        assert skill.avg_completion_time == 10.0


class TestSpecializedAgents:
    """Test specialized agent implementations"""

    @pytest.mark.asyncio
    async def test_data_processor_agent(self):
        """Test data processor agent capabilities"""
        agent = DataProcessorAgent("test_processor")

        # Check skills
        skill_names = [s.name for s in agent.skills]
        assert "data_cleaning" in skill_names
        assert "data_transformation" in skill_names
        assert "data_validation" in skill_names
        assert "etl_pipeline" in skill_names

        # All should have reasonable success rates
        for skill in agent.skills:
            assert skill.success_rate >= 0.85

    @pytest.mark.asyncio
    async def test_data_processor_task_handling(self):
        """Test data processor handling specific tasks"""
        system = ActorSystem()
        await system.start()

        hub_ref = await system.create_actor(CoordinationHub, "hub")
        agent_ref = await system.create_actor(DataProcessorAgent, "processor")

        agent = system.get_actor("processor")
        agent.coord_hub = hub_ref

        # Test data cleaning task
        result = await agent._handle_task_start(
            ActorMessage(
                message_id="test",
                sender=hub_ref,
                recipient=agent_ref,
                message_type=CoordinationProtocol.TASK_START,
                payload={
                    "task_type": "clean",
                    "data": [1, 2, 3],
                    "group_id": "test-group",
                },
                timestamp=time.time(),
            )
        )

        assert result["status"] == "completed"
        assert result["result"]["cleaned"] is True

        await system.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
