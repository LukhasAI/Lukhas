import unittest
from unittest.mock import MagicMock

from core.coordination import ContractNetInitiator, ContractNetParticipant
from core.fault_tolerance import SupervisionStrategy, Supervisor
from core.swarm import SwarmHub


class TestSupervisor(unittest.TestCase):
    def test_restart_strategy(self):
        supervisor = Supervisor(
            strategy=SupervisionStrategy.RESTART, max_restarts=1, restart_delay=0
        )
        actor_ref = MagicMock()
        supervisor.add_child("actor1", actor_ref)

        supervisor.handle_failure("actor1", Exception("Test failure"))
        # In a real system, we would check if the actor was restarted.
        # Here, we just check that the supervisor doesn't crash.
        self.assertIn("actor1", supervisor.children)

    def test_stop_strategy(self):
        supervisor = Supervisor(strategy=SupervisionStrategy.STOP)
        actor_ref = MagicMock()
        supervisor.add_child("actor1", actor_ref)

        supervisor.handle_failure("actor1", Exception("Test failure"))
        self.assertNotIn("actor1", supervisor.children)

    def test_escalate_strategy(self):
        supervisor = Supervisor(strategy=SupervisionStrategy.ESCALATE)
        actor_ref = MagicMock()
        supervisor.add_child("actor1", actor_ref)

        with self.assertRaises(Exception):
            supervisor.handle_failure("actor1", Exception("Test failure"))


class TestContractNet(unittest.TestCase):
    def test_contract_net(self):
        initiator = ContractNetInitiator({"type": "test_task"})
        participant1 = ContractNetParticipant("participant1", ["test_task"])
        participant2 = ContractNetParticipant("participant2", ["other_task"])

        initiator.call_for_proposals()

        proposal1 = participant1.handle_call_for_proposals(initiator.task)
        if proposal1:
            initiator.receive_proposal(proposal1)

        proposal2 = participant2.handle_call_for_proposals(initiator.task)
        if proposal2:
            initiator.receive_proposal(proposal2)

        winner = initiator.award_contract()
        self.assertEqual(winner["participant_id"], "participant1")


class TestSwarm(unittest.TestCase):
    def test_swarm_creation(self):
        swarm_hub = SwarmHub()
        colony = swarm_hub.register_colony("colony1", "symbolic:colony1")
        self.assertIn("colony1", swarm_hub.colonies)

        agent = colony.create_agent("agent1")
        self.assertIn("agent1", colony.agents)


if __name__ == "__main__":
    unittest.main()
