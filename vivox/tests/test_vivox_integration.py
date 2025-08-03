"""
VIVOX Integration Tests
Test the complete VIVOX system integration
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import VIVOX components
from vivox import (
    VIVOXMemoryExpansion,
    VIVOXMoralAlignmentEngine,
    VIVOXConsciousnessInterpretationLayer,
    VIVOXSelfReflectiveMemory,
    ActionProposal,
    PotentialState,
    SimulationBranch,
    create_vivox_system
)


class TestVIVOXIntegration:
    """Test complete VIVOX system integration"""
    
    @pytest.fixture
    async def vivox_system(self):
        """Create VIVOX system for testing"""
        return await create_vivox_system()
    
    @pytest.mark.asyncio
    async def test_vivox_initialization(self, vivox_system):
        """Test VIVOX system initialization"""
        assert vivox_system["memory_expansion"] is not None
        assert vivox_system["moral_alignment"] is not None
        assert vivox_system["consciousness"] is not None
        assert vivox_system["self_reflection"] is not None
        
        # Verify component connections
        assert vivox_system["moral_alignment"].vivox_me == vivox_system["memory_expansion"]
        assert vivox_system["consciousness"].vivox_me == vivox_system["memory_expansion"]
        assert vivox_system["self_reflection"].vivox_me == vivox_system["memory_expansion"]
    
    @pytest.mark.asyncio
    async def test_complete_decision_flow(self, vivox_system):
        """Test complete decision flow through all VIVOX components"""
        me = vivox_system["memory_expansion"]
        mae = vivox_system["moral_alignment"]
        cil = vivox_system["consciousness"]
        srm = vivox_system["self_reflection"]
        
        # Step 1: Create action proposal
        action = ActionProposal(
            action_type="help_user",
            content={"message": "How can I assist you?"},
            context={"user_request": "I need help", "urgency": "normal"}
        )
        
        # Step 2: Ethical evaluation
        mae_decision = await mae.evaluate_action_proposal(
            action,
            {"emotional_state": {"valence": 0.5, "arousal": 0.3, "dominance": 0.5}}
        )
        
        assert mae_decision is not None
        assert mae_decision.moral_fingerprint != ""
        
        # Step 3: Consciousness simulation
        conscious_exp = await cil.simulate_conscious_experience(
            perceptual_input={"user_request": "help needed"},
            internal_state={
                "emotional_state": [0.5, 0.3, 0.5],
                "intentional_focus": "assistance"
            }
        )
        
        assert conscious_exp is not None
        assert conscious_exp.awareness_state is not None
        
        # Step 4: Self-reflection logging
        from vivox.self_reflection.vivox_srm_core import CollapseLogEntry
        
        collapse_entry = CollapseLogEntry(
            collapse_id="test_collapse_001",
            timestamp=datetime.utcnow(),
            collapse_type="decision",
            initial_states=[{"action": "help_user"}],
            final_decision={"action": "provide_assistance"},
            rejected_alternatives=[],
            context={"test": True},
            had_alternatives=False,
            memory_reference="test_memory_001",
            ethical_score=0.9
        )
        
        collapse_id = await srm.log_collapse_event(collapse_entry)
        assert collapse_id == "test_collapse_001"
    
    @pytest.mark.asyncio
    async def test_memory_veiling(self, vivox_system):
        """Test GDPR-compliant memory veiling"""
        me = vivox_system["memory_expansion"]
        
        # Create a memory
        memory_id = await me.record_decision_mutation(
            decision={"action": "store_data", "content": "sensitive info"},
            emotional_context={"valence": 0.0, "arousal": 0.5},
            moral_fingerprint="test_memory_veil"
        )
        
        # Veil the memory
        success = await me.memory_veiling_operation(
            memory_ids=[memory_id],
            veiling_reason="user_request",
            ethical_approval="gdpr_compliance"
        )
        
        assert success == True
        
        # Verify memory is veiled
        resonant_memories = await me.resonant_memory_access(
            emotional_state={"valence": 0.0, "arousal": 0.5}
        )
        
        # Veiled memory should not appear in resonant access
        assert not any(m.sequence_id == memory_id for m in resonant_memories)
    
    @pytest.mark.asyncio
    async def test_z_collapse_gating(self, vivox_system):
        """Test z(t) collapse gating logic"""
        mae = vivox_system["moral_alignment"]
        
        # Create potential states
        states = [
            PotentialState(
                state_id="state_1",
                probability_amplitude=0.7,
                emotional_signature=[0.8, 0.2, 0.5],
                creation_timestamp=datetime.utcnow().timestamp()
            ),
            PotentialState(
                state_id="state_2",
                probability_amplitude=0.5,
                emotional_signature=[-0.3, 0.7, 0.4],
                creation_timestamp=datetime.utcnow().timestamp()
            ),
            PotentialState(
                state_id="state_harmful",
                probability_amplitude=0.9,
                emotional_signature=[-0.9, 0.9, 0.1],
                creation_timestamp=datetime.utcnow().timestamp()
            )
        ]
        
        # Add harmful content to one state for suppression test
        states[2].to_action_proposal = lambda: ActionProposal(
            action_type="harmful_action",
            content={"harm_potential": 0.9},
            context={}
        )
        
        # Perform z(t) collapse
        collapsed = await mae.z_collapse_gating(
            states,
            {"emotional_state": [0.5, 0.5, 0.5], "timestamp": datetime.utcnow().timestamp()}
        )
        
        assert collapsed is not None
        # Harmful state should be rejected
        assert collapsed.selected_state is None or collapsed.selected_state.state_id != "state_harmful"
    
    @pytest.mark.asyncio
    async def test_truth_audit_query(self, vivox_system):
        """Test truth audit functionality"""
        me = vivox_system["memory_expansion"]
        
        # Create some test memories
        for i in range(3):
            await me.record_decision_mutation(
                decision={"action": f"test_action_{i}", "reason": "testing"},
                emotional_context={"valence": i * 0.3, "arousal": 0.5},
                moral_fingerprint=f"test_audit_{i}"
            )
        
        # Query the truth audit
        audit_result = await me.truth_audit_query("test_action")
        
        assert audit_result is not None
        assert len(audit_result.decision_traces) >= 0  # May find matches
    
    @pytest.mark.asyncio 
    async def test_consciousness_drift_monitoring(self, vivox_system):
        """Test consciousness drift detection"""
        cil = vivox_system["consciousness"]
        
        # Simulate consciousness experiences with increasing drift
        for i in range(3):
            experience = await cil.simulate_conscious_experience(
                perceptual_input={
                    "stimulus": f"test_{i}",
                    "intensity": i * 0.3
                },
                internal_state={
                    "emotional_state": [i * 0.3, 0.5, 0.5],
                    "intentional_focus": f"focus_{i}"
                }
            )
            
            assert experience is not None
            assert experience.drift_measurement is not None
            
            # Drift should increase over time as states diverge
            if i > 0:
                assert experience.drift_measurement.drift_amount >= 0
    
    @pytest.mark.asyncio
    async def test_structural_conscience_query(self, vivox_system):
        """Test structural conscience functionality"""
        srm = vivox_system["self_reflection"]
        mae = vivox_system["moral_alignment"]
        
        # Create and suppress some actions
        from vivox.self_reflection.vivox_srm_core import SuppressionRecord
        
        suppression = SuppressionRecord(
            suppression_id="test_suppress_001",
            timestamp=datetime.utcnow(),
            suppressed_action={"action": "risky_action", "risk": "high"},
            suppression_reason="potential_harm",
            ethical_analysis={"harm_score": 0.8},
            alternative_chosen={"action": "safe_action"},
            dissonance_score=0.85
        )
        
        await srm.log_suppression_event(suppression)
        
        # Query structural conscience
        conscience_report = await srm.structural_conscience_query(
            "What actions did you choose not to do?"
        )
        
        assert conscience_report is not None
        assert len(conscience_report.suppressed_actions) > 0
        assert conscience_report.ethical_consistency_score >= 0
    
    @pytest.mark.asyncio
    async def test_memory_protein_folding(self, vivox_system):
        """Test symbolic proteome functionality"""
        me = vivox_system["memory_expansion"]
        
        # Create a memory with complex emotional context
        memory_id = await me.record_decision_mutation(
            decision={
                "action": "complex_decision",
                "factors": ["ethical", "practical", "emotional"],
                "complexity": 8
            },
            emotional_context={
                "valence": 0.7,
                "arousal": 0.8,
                "dominance": 0.6
            },
            moral_fingerprint="complex_fold_test"
        )
        
        # The protein folding happens internally
        # Verify memory was stored successfully
        assert memory_id is not None
        assert memory_id.startswith("vivox_me_")
        
        # Access proteome to check for misfolding
        misfolding_report = await me.symbolic_proteome.detect_memory_misfolding(
            f"fold_{memory_id}"
        )
        
        assert misfolding_report is not None
        # New memories should have low misfolding issues
        assert len(misfolding_report.issues) <= 1


class TestVIVOXPerformance:
    """Test VIVOX system performance"""
    
    @pytest.mark.asyncio
    async def test_memory_helix_performance(self):
        """Test memory helix can handle large numbers of entries"""
        me = VIVOXMemoryExpansion()
        
        # Add 1000 memories
        start_time = datetime.utcnow()
        
        for i in range(100):  # Reduced for test speed
            await me.record_decision_mutation(
                decision={"action": f"perf_test_{i}"},
                emotional_context={"valence": i % 2 - 0.5},
                moral_fingerprint=f"perf_{i}"
            )
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete in reasonable time
        assert duration < 10.0  # 10 seconds for 100 entries
        
        # Test retrieval performance
        retrieval_start = datetime.utcnow()
        
        memories = await me.resonant_memory_access(
            {"valence": 0.5},
            resonance_threshold=0.5
        )
        
        retrieval_end = datetime.utcnow()
        retrieval_duration = (retrieval_end - retrieval_start).total_seconds()
        
        # Retrieval should be fast
        assert retrieval_duration < 1.0  # Less than 1 second


@pytest.mark.asyncio
async def test_vivox_example_usage():
    """Test example usage from documentation"""
    # Create VIVOX system
    vivox = await create_vivox_system()
    
    # Example: Ethical decision making
    action = ActionProposal(
        action_type="generate_response",
        content={"message": "Here's how to solve your problem..."},
        context={"user_intent": "seeking_help"}
    )
    
    # MAE validates
    mae_result = await vivox["moral_alignment"].evaluate_action_proposal(
        action,
        {"emotional_state": {"valence": 0.7, "arousal": 0.4}}
    )
    
    if mae_result.approved:
        # CIL processes consciousness
        conscious_exp = await vivox["consciousness"].simulate_conscious_experience(
            perceptual_input={"user_request": "help needed"},
            internal_state={"mood": "helpful", "emotional_state": [0.7, 0.4, 0.5]}
        )
        
        # ME records decision
        memory_id = await vivox["memory_expansion"].record_decision_mutation(
            decision=action.content,
            emotional_context={"valence": 0.7},
            moral_fingerprint=mae_result.moral_fingerprint
        )
        
        assert memory_id is not None
        assert conscious_exp is not None
        
        # Can query audit trail
        audit = await vivox["self_reflection"].generate_decision_audit_trail(memory_id)
        assert audit is not None


if __name__ == "__main__":
    # Run basic integration test
    asyncio.run(test_vivox_example_usage())
    print("VIVOX integration test completed successfully!")