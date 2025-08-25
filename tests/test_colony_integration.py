"""
Complete Colony Integration Test Suite
======================================
Tests the full integration of colony systems with Signal Bus,
Personal Symbol Dictionary, Universal Exchange, and GPT orchestration.
"""

import asyncio

import pytest

from core.colonies.consensus_mechanisms import (
    ColonyConsensus,
    ConsensusMethod,
    VoteType,
)
from core.colonies.enhanced_colony import EnhancedReasoningColony
from candidate.orchestration.gpt_colony_orchestrator import (
    GPTColonyOrchestrator,
    OrchestrationMode,
    OrchestrationTask,
)
from candidate.orchestration.signals.homeostasis import HomeostasisController

# Import all our new components
from candidate.orchestration.signals.signal_bus import Signal, SignalBus, SignalType
from symbolic.exchange.universal_exchange import (
    ExchangeProtocol,
    UniversalSymbolExchange,
)
from symbolic.personal.symbol_dictionary import GestureType, PersonalSymbolDictionary

# from candidate.orchestration.signals.feedback_cards import FeedbackCardSystem,
# FeedbackCard  # TODO: implement


class TestSignalBusIntegration:
    """Test Signal Bus integration"""

    def test_signal_bus_creation(self):
        """Test basic signal bus functionality"""
        bus = SignalBus()

        # Test signal publishing
        signal = Signal(
            name=SignalType.NOVELTY,
            source="test",
            level=0.5,
            metadata={"test": True},
        )

        success = bus.publish(signal)
        assert success

        # Test signal retrieval
        active = bus.get_active_signals()
        assert len(active) > 0
        assert active[0].name == SignalType.NOVELTY

    def test_signal_subscription(self):
        """Test signal subscription mechanism"""
        bus = SignalBus()
        received_signals = []

        def handler(signal: Signal):
            received_signals.append(signal)

        # Subscribe to novelty signals
        bus.subscribe(SignalType.NOVELTY, handler)

        # Publish signal
        signal = Signal(name=SignalType.NOVELTY, source="test", level=0.7)
        bus.publish(signal)

        # Check handler received signal
        assert len(received_signals) == 1
        assert received_signals[0].level == 0.7

    def test_homeostasis_controller(self):
        """Test homeostasis oscillation detection"""
        controller = HomeostasisController()

        # Simulate oscillating signals
        signals = []
        for i in range(10):
            level = 0.8 if i % 2 == 0 else 0.2
            signals.append(Signal(name=SignalType.STRESS, source="test", level=level))

        # Process signals
        for signal in signals:
            controller.process_signals([signal])

        # Check state
        state = controller.get_system_state()

        # Should detect oscillation
        assert "oscillating_signals" in state
        assert len(state["oscillating_signals"]) > 0


class TestColonyIntegration:
    """Test Colony system integration"""

    @pytest.mark.asyncio
    async def test_enhanced_colony_creation(self):
        """Test enhanced colony with signal integration"""
        colony = EnhancedReasoningColony("test-colony")

        # Test basic query processing
        result = await colony.process_query("Test query", {"context": "test"})

        assert result is not None
        assert hasattr(result, "consensus_reached")
        assert hasattr(result, "confidence")

    @pytest.mark.asyncio
    async def test_colony_consensus_mechanisms(self):
        """Test different consensus mechanisms"""
        consensus = ColonyConsensus("test-colony")

        # Register agents
        for i in range(5):
            consensus.register_agent(f"agent_{i}", weight=1.0 + i * 0.1)

        # Create proposal
        proposal_id = await consensus.propose(
            content="Test proposal",
            proposer="coordinator",
            method=ConsensusMethod.WEIGHTED_VOTE,
        )

        # Cast votes
        for i in range(5):
            vote_type = VoteType.APPROVE if i > 2 else VoteType.REJECT
            await consensus.vote(proposal_id, f"agent_{i}", vote_type, confidence=0.8)

        # Reach consensus
        outcome = await consensus.reach_consensus(proposal_id)

        assert outcome is not None
        assert outcome.decision in [VoteType.APPROVE, VoteType.REJECT]
        assert outcome.confidence > 0
        assert outcome.participation_rate > 0

    @pytest.mark.asyncio
    async def test_hormone_based_consensus(self):
        """Test hormone-influenced consensus"""
        consensus = ColonyConsensus("hormone-colony")

        # Register agents
        for i in range(3):
            consensus.register_agent(f"agent_{i}")

        # Set high stress hormones
        consensus.update_hormone_levels({"stress": 0.9, "urgency": 0.8, "trust": 0.2})

        # Create proposal
        proposal_id = await consensus.propose(
            content="Risky decision",
            proposer="coordinator",
            method=ConsensusMethod.HORMONE,
        )

        # All agents initially approve
        for i in range(3):
            await consensus.vote(
                proposal_id, f"agent_{i}", VoteType.APPROVE, confidence=0.9
            )

        # Reach consensus with hormone influence
        outcome = await consensus.reach_consensus(proposal_id)

        # High stress should reduce approval confidence
        assert outcome.confidence < 0.9  # Less than original confidence


class TestSymbolDictionary:
    """Test Personal Symbol Dictionary"""

    def test_symbol_dictionary_creation(self):
        """Test creating personal symbol dictionary"""
        dictionary = PersonalSymbolDictionary("test_user")

        # Should be locked initially
        assert dictionary.is_locked

        # Unlock with passphrase
        success = dictionary.unlock("test_passphrase")
        assert success
        assert not dictionary.is_locked

        # Should have base symbols
        assert len(dictionary.mappings) > 0

    def test_gesture_mapping(self):
        """Test gesture to symbol mapping"""
        dictionary = PersonalSymbolDictionary("test_user")
        dictionary.unlock("test_passphrase")

        # Add custom gesture mapping
        success = dictionary.add_symbol(
            symbol="🎯",
            meaning="focus_mode",
            gesture_type=GestureType.HAND,
            context="productivity",
            gesture_sequence=["👆", "👆", "👏"],
        )
        assert success

        # Test gesture detection
        detected = dictionary.detect_gesture(["👆", "👆", "👏"])
        assert detected == "🎯"

        # Test meaning retrieval
        meaning = dictionary.get_meaning("🎯")
        assert meaning == "focus_mode"

    def test_symbol_evolution(self):
        """Test symbol evolution based on feedback"""
        dictionary = PersonalSymbolDictionary("test_user")
        dictionary.unlock("test_passphrase")

        # Add symbol
        dictionary.add_symbol(
            symbol="💫",
            meaning="excitement",
            gesture_type=GestureType.COMPOSITE,
        )

        # Evolve with positive feedback
        dictionary.evolve_symbol(
            "💫", new_meaning="extreme_excitement", feedback_score=0.9
        )

        # Check evolution
        meaning = dictionary.get_meaning("💫")
        assert meaning == "extreme_excitement"

        mapping = dictionary.mappings["💫"]
        assert len(mapping.evolution_history) > 0


class TestUniversalExchange:
    """Test Universal Symbol Exchange"""

    @pytest.mark.asyncio
    async def test_exchange_session(self):
        """Test creating exchange session"""
        exchange = UniversalSymbolExchange()

        # Initiate session
        session_id = await exchange.initiate_exchange(
            initiator_id="alice",
            participant_ids=["bob", "charlie"],
            protocol=ExchangeProtocol.HASHED,
        )

        assert session_id is not None
        assert session_id in exchange.active_sessions

    @pytest.mark.asyncio
    async def test_privacy_preserving_exchange(self):
        """Test privacy-preserving symbol exchange"""
        exchange = UniversalSymbolExchange()

        # Create session with differential privacy
        session_id = await exchange.initiate_exchange(
            initiator_id="alice",
            participant_ids=["bob", "charlie", "diana"],
            protocol=ExchangeProtocol.DIFFERENTIAL,
        )

        # Each user contributes symbols
        users_symbols = {
            "alice": {"🎯": "hash_focus", "💪": "hash_strength"},
            "bob": {"🎯": "hash_focus", "🌟": "hash_star"},
            "charlie": {"🎯": "hash_focus", "💪": "hash_strength"},
            "diana": {"💪": "hash_strength", "🌟": "hash_star"},
        }

        for user, symbols in users_symbols.items():
            await exchange.contribute_symbols(session_id, user, symbols)

        # Check k-anonymity preserved
        stats = exchange.get_universal_stats()

        # Should have discovered some symbols
        assert stats["total_candidates"] > 0

        # Check privacy metrics
        privacy = exchange.get_privacy_metrics(session_id)
        assert privacy["k_anonymity"] >= 3
        assert privacy["privacy_preservation_rate"] > 0


class TestGPTColonyOrchestration:
    """Test GPT-Colony Orchestration"""

    @pytest.mark.asyncio
    async def test_orchestrator_creation(self):
        """Test creating GPT-Colony orchestrator"""
        orchestrator = GPTColonyOrchestrator()

        # Register colony
        colony = EnhancedReasoningColony("test-colony")
        orchestrator.register_colony("test-colony", colony)

        assert "test-colony" in orchestrator.colonies
        assert "test-colony" in orchestrator.colony_consensus

    @pytest.mark.asyncio
    async def test_parallel_orchestration(self):
        """Test parallel GPT-Colony processing"""
        orchestrator = GPTColonyOrchestrator()

        # Register colony
        colony = EnhancedReasoningColony("parallel-colony")
        orchestrator.register_colony("parallel-colony", colony)

        # Create parallel task
        task = OrchestrationTask(
            task_id="parallel_test",
            content="Should we optimize for speed or accuracy?",
            mode=OrchestrationMode.PARALLEL,
            context={"current_metric": "balanced"},
        )

        # Process task
        result = await orchestrator.process_task(task)

        assert result is not None
        assert result.task_id == "parallel_test"
        assert result.mode_used == OrchestrationMode.PARALLEL
        assert result.processing_time > 0

    @pytest.mark.asyncio
    async def test_competitive_orchestration(self):
        """Test competitive orchestration mode"""
        orchestrator = GPTColonyOrchestrator()

        # Register colony
        colony = EnhancedReasoningColony("competitive-colony")
        orchestrator.register_colony("competitive-colony", colony)

        # Create competitive task
        task = OrchestrationTask(
            task_id="competitive_test",
            content="Choose the best algorithm",
            mode=OrchestrationMode.COMPETITIVE,
            context={"options": ["A", "B", "C"]},
        )

        # Process task
        result = await orchestrator.process_task(task)

        assert result is not None
        assert result.mode_used == OrchestrationMode.COMPETITIVE

        # Should have competition scores in metadata
        if "competition_scores" in result.metadata:
            assert "gpt" in result.metadata["competition_scores"]
            assert "colony" in result.metadata["competition_scores"]


class TestFullIntegration:
    """Test complete system integration"""

    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test all components working together"""

        # 1. Create Signal Bus
        signal_bus = SignalBus()

        # 2. Create Colony with Signal Integration
        colony = EnhancedReasoningColony("integration-colony")

        # 3. Create Personal Symbol Dictionary
        dictionary = PersonalSymbolDictionary("integration_user")
        dictionary.unlock("secure_pass")
        dictionary.add_symbol("🚀", "launch", GestureType.HAND)

        # 4. Create Universal Exchange
        exchange = UniversalSymbolExchange(signal_bus)

        # 5. Create GPT-Colony Orchestrator
        orchestrator = GPTColonyOrchestrator(signal_bus=signal_bus)
        orchestrator.register_colony("integration-colony", colony)

        # 6. Run integrated workflow

        # Start exchange session
        session_id = await exchange.initiate_exchange(
            initiator_id="user1",
            participant_ids=["user2", "user3"],
            protocol=ExchangeProtocol.COLONY,
        )

        # Process task through orchestrator
        task = OrchestrationTask(
            task_id="integration_task",
            content="Analyze system performance",
            mode=OrchestrationMode.COLLABORATIVE,
            context={
                "symbols": dictionary.export_public_symbols(),
                "exchange_session": session_id,
            },
        )

        result = await orchestrator.process_task(task)

        # Verify integration
        assert result is not None
        assert result.confidence > 0

        # Check signals were emitted
        active_signals = signal_bus.get_active_signals()
        assert len(active_signals) > 0

        # Check performance metrics
        report = orchestrator.get_performance_report()
        assert report["completed_tasks"] > 0

        print("\n✅ Full Integration Test Passed!")
        print(f"   - Signals active: {len(active_signals)}")
        print(f"   - Task confidence: {result.confidence:.2%}")
        print(f"   - Processing time: {result.processing_time:.2f}s")


# Run tests
def run_all_tests():
    """Run all integration tests"""
    print("🧪 Running Colony Integration Tests")
    print("=" * 50)

    # Signal Bus Tests
    print("\n📡 Testing Signal Bus...")
    signal_tests = TestSignalBusIntegration()
    signal_tests.test_signal_bus_creation()
    signal_tests.test_signal_subscription()
    signal_tests.test_homeostasis_controller()
    print("✅ Signal Bus tests passed")

    # Colony Tests
    print("\n🏛️ Testing Colony Systems...")
    colony_tests = TestColonyIntegration()
    asyncio.run(colony_tests.test_enhanced_colony_creation())
    asyncio.run(colony_tests.test_colony_consensus_mechanisms())
    asyncio.run(colony_tests.test_hormone_based_consensus())
    print("✅ Colony tests passed")

    # Symbol Dictionary Tests
    print("\n📖 Testing Symbol Dictionary...")
    symbol_tests = TestSymbolDictionary()
    symbol_tests.test_symbol_dictionary_creation()
    symbol_tests.test_gesture_mapping()
    symbol_tests.test_symbol_evolution()
    print("✅ Symbol Dictionary tests passed")

    # Universal Exchange Tests
    print("\n🌍 Testing Universal Exchange...")
    exchange_tests = TestUniversalExchange()
    asyncio.run(exchange_tests.test_exchange_session())
    asyncio.run(exchange_tests.test_privacy_preserving_exchange())
    print("✅ Universal Exchange tests passed")

    # Orchestration Tests
    print("\n🎭 Testing GPT-Colony Orchestration...")
    orchestration_tests = TestGPTColonyOrchestration()
    asyncio.run(orchestration_tests.test_orchestrator_creation())
    asyncio.run(orchestration_tests.test_parallel_orchestration())
    asyncio.run(orchestration_tests.test_competitive_orchestration())
    print("✅ Orchestration tests passed")

    # Full Integration Test
    print("\n🔗 Testing Full Integration...")
    integration_test = TestFullIntegration()
    asyncio.run(integration_test.test_full_system_integration())

    print("\n" + "=" * 50)
    print("🎉 All Colony Integration Tests Passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
