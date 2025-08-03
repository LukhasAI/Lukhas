"""
Tests for the LUKHAS Endocrine System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from core.endocrine import (
    HormoneType, HormoneLevel, HormoneInteraction,
    EndocrineSystem, get_endocrine_system,
    trigger_stress, trigger_reward, get_neuroplasticity
)

class TestHormoneLevel:
    """Test hormone level functionality"""
    
    def test_hormone_level_initialization(self):
        """Test hormone level creates with correct defaults"""
        hormone = HormoneLevel(
            hormone_type=HormoneType.DOPAMINE,
            baseline=0.5,
            production_rate=0.15,
            decay_rate=0.1
        )
        
        assert hormone.level == 0.5
        assert hormone.baseline == 0.5
        assert hormone.production_rate == 0.15
        assert hormone.decay_rate == 0.1
        
    def test_hormone_decay(self):
        """Test hormone decays towards baseline"""
        hormone = HormoneLevel(
            hormone_type=HormoneType.CORTISOL,
            level=0.8,
            baseline=0.3,
            decay_rate=0.1
        )
        
        # Update for 1 second
        new_level = hormone.update(1.0)
        
        # Should decay towards baseline
        assert new_level < 0.8
        assert new_level > 0.3
        
    def test_hormone_bounds(self):
        """Test hormone levels stay within bounds"""
        hormone = HormoneLevel(
            hormone_type=HormoneType.DOPAMINE,
            level=0.95,
            baseline=0.5,
            decay_rate=0.5
        )
        
        # Even with high decay, should not go below 0
        hormone.level = 0.1
        hormone.baseline = 0.9
        hormone.update(10.0)
        assert hormone.level >= 0.0
        
        # Should not exceed 1.0
        hormone.level = 1.5
        hormone.update(0.1)
        assert hormone.level <= 1.0

class TestEndocrineSystem:
    """Test the endocrine system"""
    
    def test_system_initialization(self):
        """Test endocrine system initializes correctly"""
        system = EndocrineSystem()
        
        # Check all hormones are initialized
        assert len(system.hormones) == 8
        assert HormoneType.CORTISOL in system.hormones
        assert HormoneType.DOPAMINE in system.hormones
        assert HormoneType.SEROTONIN in system.hormones
        assert HormoneType.OXYTOCIN in system.hormones
        assert HormoneType.ADRENALINE in system.hormones
        assert HormoneType.MELATONIN in system.hormones
        assert HormoneType.GABA in system.hormones
        assert HormoneType.ENDORPHIN in system.hormones
        
        # Check interactions are set up
        assert len(system.interactions) > 0
        
    def test_hormone_interactions(self):
        """Test hormone interactions work correctly"""
        system = EndocrineSystem()
        
        # Set high cortisol
        system.hormones[HormoneType.CORTISOL].level = 0.8
        
        # Get initial serotonin level
        initial_serotonin = system.hormones[HormoneType.SEROTONIN].level
        
        # Apply interactions
        system._apply_interactions()
        
        # Cortisol should suppress serotonin
        final_serotonin = system.hormones[HormoneType.SEROTONIN].level
        assert final_serotonin < initial_serotonin
        
    def test_stress_response(self):
        """Test stress response trigger"""
        system = EndocrineSystem()
        
        # Get initial levels
        initial_cortisol = system.hormones[HormoneType.CORTISOL].level
        initial_adrenaline = system.hormones[HormoneType.ADRENALINE].level
        
        # Trigger stress
        system.trigger_stress_response(intensity=0.7)
        
        # Check hormones increased
        assert system.hormones[HormoneType.CORTISOL].level > initial_cortisol
        assert system.hormones[HormoneType.ADRENALINE].level > initial_adrenaline
        
        # Check effect history
        assert len(system.effect_history) == 1
        assert system.effect_history[0]["type"] == "stress_response"
        assert system.effect_history[0]["intensity"] == 0.7
        
    def test_reward_response(self):
        """Test reward response trigger"""
        system = EndocrineSystem()
        
        # Get initial levels
        initial_dopamine = system.hormones[HormoneType.DOPAMINE].level
        initial_endorphin = system.hormones[HormoneType.ENDORPHIN].level
        initial_serotonin = system.hormones[HormoneType.SEROTONIN].level
        
        # Trigger reward
        system.trigger_reward_response(intensity=0.6)
        
        # Check hormones increased
        assert system.hormones[HormoneType.DOPAMINE].level > initial_dopamine
        assert system.hormones[HormoneType.ENDORPHIN].level > initial_endorphin
        assert system.hormones[HormoneType.SEROTONIN].level > initial_serotonin
        
    def test_social_bonding(self):
        """Test social bonding response"""
        system = EndocrineSystem()
        
        # Set some initial stress
        system.hormones[HormoneType.CORTISOL].level = 0.7
        initial_cortisol = system.hormones[HormoneType.CORTISOL].level
        initial_oxytocin = system.hormones[HormoneType.OXYTOCIN].level
        
        # Trigger social bonding
        system.trigger_social_bonding(intensity=0.5)
        
        # Check oxytocin increased, cortisol decreased
        assert system.hormones[HormoneType.OXYTOCIN].level > initial_oxytocin
        assert system.hormones[HormoneType.CORTISOL].level < initial_cortisol
        
    def test_rest_cycle(self):
        """Test rest cycle trigger"""
        system = EndocrineSystem()
        
        # Set high activity hormones
        system.hormones[HormoneType.ADRENALINE].level = 0.8
        system.hormones[HormoneType.CORTISOL].level = 0.7
        
        initial_melatonin = system.hormones[HormoneType.MELATONIN].level
        initial_gaba = system.hormones[HormoneType.GABA].level
        initial_adrenaline = system.hormones[HormoneType.ADRENALINE].level
        
        # Trigger rest cycle
        system.trigger_rest_cycle(intensity=0.6)
        
        # Check rest hormones increased, activity decreased
        assert system.hormones[HormoneType.MELATONIN].level > initial_melatonin
        assert system.hormones[HormoneType.GABA].level > initial_gaba
        assert system.hormones[HormoneType.ADRENALINE].level < initial_adrenaline
        
    def test_calculate_effects(self):
        """Test effect calculation"""
        system = EndocrineSystem()
        
        # Set specific hormone levels
        system.hormones[HormoneType.CORTISOL].level = 0.8
        system.hormones[HormoneType.DOPAMINE].level = 0.3
        system.hormones[HormoneType.SEROTONIN].level = 0.4
        system.hormones[HormoneType.OXYTOCIN].level = 0.7
        
        effects = system._calculate_effects()
        
        # Check calculated effects
        assert "stress_level" in effects
        assert effects["stress_level"] > 0.5  # High cortisol
        assert "mood_valence" in effects
        assert "social_engagement" in effects
        assert effects["social_engagement"] == 0.7  # Equals oxytocin
        assert "neuroplasticity" in effects
        
    def test_neuroplasticity_calculation(self):
        """Test neuroplasticity calculation"""
        system = EndocrineSystem()
        
        # Test high stress reduces neuroplasticity
        system.hormones[HormoneType.CORTISOL].level = 0.9
        high_stress_np = system._calculate_neuroplasticity()
        
        # Reset and test balanced state
        system.hormones[HormoneType.CORTISOL].level = 0.3
        system.hormones[HormoneType.DOPAMINE].level = 0.6
        system.hormones[HormoneType.SEROTONIN].level = 0.6
        balanced_np = system._calculate_neuroplasticity()
        
        assert balanced_np > high_stress_np
        assert 0.1 <= high_stress_np <= 1.0
        assert 0.1 <= balanced_np <= 1.0
        
    def test_dominant_state_detection(self):
        """Test dominant hormonal state detection"""
        system = EndocrineSystem()
        
        # Test stressed state
        system.hormones[HormoneType.CORTISOL].level = 0.9
        system.hormones[HormoneType.CORTISOL].baseline = 0.3
        assert system._determine_dominant_state() == "stressed"
        
        # Test motivated state
        system.hormones[HormoneType.CORTISOL].level = 0.3
        system.hormones[HormoneType.DOPAMINE].level = 0.8
        system.hormones[HormoneType.DOPAMINE].baseline = 0.5
        assert system._determine_dominant_state() == "motivated"
        
    def test_hormone_profile(self):
        """Test comprehensive hormone profile generation"""
        system = EndocrineSystem()
        
        # Set some hormone levels
        system.trigger_stress_response(0.5)
        
        profile = system.get_hormone_profile()
        
        assert "levels" in profile
        assert "effects" in profile
        assert "timestamp" in profile
        assert "dominant_state" in profile
        assert "summary" in profile
        
        # Check summary is human-readable
        assert isinstance(profile["summary"], str)
        assert len(profile["summary"]) > 10
        
    def test_receptor_registration(self):
        """Test module receptor registration"""
        system = EndocrineSystem()
        
        received_effects = []
        
        async def test_receptor(effects):
            received_effects.append(effects)
            
        # Register receptor
        system.register_receptor("test_module", test_receptor)
        
        assert "test_module" in system.receptors
        assert len(system.receptors["test_module"]) == 1
        
    @pytest.mark.asyncio
    async def test_update_loop(self):
        """Test the update loop runs correctly"""
        system = EndocrineSystem()
        
        # Start the system
        await system.start()
        assert system.active is True
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop the system
        await system.stop()
        assert system.active is False
        
    def test_global_convenience_functions(self):
        """Test global convenience functions"""
        # Get global system
        system1 = get_endocrine_system()
        system2 = get_endocrine_system()
        
        # Should be same instance
        assert system1 is system2
        
        # Test neuroplasticity getter
        np_level = get_neuroplasticity()
        assert 0.1 <= np_level <= 1.0
        
    def test_hormone_summary_generation(self):
        """Test human-readable summary generation"""
        system = EndocrineSystem()
        
        # Test high stress summary
        system.hormones[HormoneType.CORTISOL].level = 0.85
        system.active_effects = system._calculate_effects()
        summary = system._generate_summary()
        assert "High stress detected" in summary
        
        # Test positive mood summary
        system.hormones[HormoneType.CORTISOL].level = 0.3
        system.hormones[HormoneType.DOPAMINE].level = 0.8
        system.hormones[HormoneType.SEROTONIN].level = 0.8
        system.active_effects = system._calculate_effects()
        summary = system._generate_summary()
        assert "Positive mood state" in summary
        
        # Test rest needed summary
        system.hormones[HormoneType.MELATONIN].level = 0.8
        system.active_effects = system._calculate_effects()
        summary = system._generate_summary()
        assert "resting state" in summary or "Rest cycle recommended" in summary