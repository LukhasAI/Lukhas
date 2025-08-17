#!/usr/bin/env python3
"""
Test Guardian Intervention - Integration test for Guardian System threat detection and response
Validates symbolic intervention chains and protective actions
"""

import asyncio
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "next_gen"))

try:
    from guardian.sentinel import GuardianSentinel, ThreatIndicator
except ImportError:
    # Mock classes for testing when modules aren't available
    class ThreatIndicator:
        def __init__(
            self,
            indicator_type,
            severity,
            source,
            timestamp,
            details,
            recommended_action,
        ):
            self.indicator_type = indicator_type
            self.severity = severity
            self.source = source
            self.timestamp = timestamp
            self.details = details
            self.recommended_action = recommended_action

    class GuardianSentinel:
        def __init__(self, *args, **kwargs):
            self.active_threats = []
            self.intervention_history = []


class TestGuardianIntervention:
    """Integration tests for Guardian System intervention and protection mechanisms"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def mock_guardian_sentinel(self, temp_dir):
        """Create mock Guardian Sentinel for testing"""
        return GuardianSentinel(
            websocket_url="ws://localhost:8765",
            alert_threshold=0.5,
            monitoring_interval=1,
        )

    @pytest.fixture
    def intervention_rules(self):
        """Load intervention rules configuration"""
        rules = {
            "threat_levels": {
                "low": {
                    "threshold": 0.3,
                    "symbol": "🟡",
                    "response": "monitor",
                },
                "medium": {
                    "threshold": 0.5,
                    "symbol": "🟠",
                    "response": "mitigate",
                },
                "high": {
                    "threshold": 0.7,
                    "symbol": "🔴",
                    "response": "intervene",
                },
                "critical": {
                    "threshold": 0.9,
                    "symbol": "🚨",
                    "response": "lockdown",
                },
            },
            "intervention_rules": {
                "drift_spike": {
                    "reactions": {
                        "medium": {
                            "action": "drift_dampening",
                            "symbolic_response": ["🌀", "→", "🌿"],
                        },
                        "high": {
                            "action": "drift_correction",
                            "symbolic_response": ["🌪️", "→", "🌀", "→", "🌿"],
                        },
                        "critical": {
                            "action": "emergency_stabilization",
                            "symbolic_response": ["🚨", "🔒", "🛡️"],
                        },
                    }
                },
                "entropy_surge": {
                    "reactions": {
                        "medium": {
                            "action": "entropy_cooling",
                            "symbolic_response": ["🔥", "→", "💨", "→", "❄️"],
                        },
                        "high": {
                            "action": "entropy_reduction",
                            "symbolic_response": ["🌋", "→", "🏔️"],
                        },
                    }
                },
                "pattern_anomaly": {
                    "reactions": {
                        "medium": {
                            "action": "pattern_reinforcement",
                            "symbolic_response": ["🔄", "💪"],
                        },
                        "high": {
                            "action": "pattern_correction",
                            "symbolic_response": ["❌", "→", "✅"],
                        },
                    }
                },
                "consciousness_instability": {
                    "reactions": {
                        "high": {
                            "action": "consciousness_anchoring",
                            "symbolic_response": ["⚓", "🧘", "🔒"],
                        },
                        "critical": {
                            "action": "consciousness_freeze",
                            "symbolic_response": ["🧊", "🛑", "🔐"],
                        },
                    }
                },
            },
        }
        return rules

    def test_threat_severity_classification(self, intervention_rules):
        """Test threat severity level classification and symbol assignment"""

        threat_levels = intervention_rules["threat_levels"]

        test_cases = [
            {
                "severity": 0.2,
                "expected_level": "low",
                "expected_symbol": "🟡",
            },
            {
                "severity": 0.4,
                "expected_level": "medium",
                "expected_symbol": "🟠",
            },
            {
                "severity": 0.6,
                "expected_level": "high",
                "expected_symbol": "🔴",
            },
            {
                "severity": 0.95,
                "expected_level": "critical",
                "expected_symbol": "🚨",
            },
        ]

        for case in test_cases:
            severity = case["severity"]
            expected_level = case["expected_level"]
            expected_symbol = case["expected_symbol"]

            # Classify threat level based on severity
            actual_level = None
            for level, config in threat_levels.items():
                if severity >= config["threshold"]:
                    actual_level = level

            # Should default to highest applicable threshold
            if actual_level is None:
                actual_level = "low"  # Default to lowest level

            assert (
                actual_level == expected_level
            ), f"Severity {severity} should be classified as {expected_level}, got {actual_level}"

            # Validate symbol assignment
            actual_symbol = threat_levels[actual_level]["symbol"]
            assert (
                actual_symbol == expected_symbol
            ), f"Level {actual_level} should have symbol {expected_symbol}, got {actual_symbol}"

    def test_drift_spike_intervention_chain(self, intervention_rules):
        """Test drift spike intervention with symbolic sequence validation"""

        drift_reactions = intervention_rules["intervention_rules"]["drift_spike"][
            "reactions"
        ]

        # Test medium severity drift spike
        medium_reaction = drift_reactions["medium"]
        assert medium_reaction["action"] == "drift_dampening"

        medium_sequence = medium_reaction["symbolic_response"]
        expected_medium = ["🌀", "→", "🌿"]
        assert (
            medium_sequence == expected_medium
        ), f"Medium drift should have sequence {expected_medium}, got {medium_sequence}"

        # Validate symbolic progression: chaos → stability
        clean_medium = [s for s in medium_sequence if s != "→"]
        assert clean_medium[0] == "🌀", "Should start with moderate chaos symbol"
        assert clean_medium[-1] == "🌿", "Should end with stability symbol"

        # Test high severity drift spike
        high_reaction = drift_reactions["high"]
        assert high_reaction["action"] == "drift_correction"

        high_sequence = high_reaction["symbolic_response"]
        expected_high = ["🌪️", "→", "🌀", "→", "🌿"]
        assert (
            high_sequence == expected_high
        ), f"High drift should have sequence {expected_high}, got {high_sequence}"

        # Validate progression: intense chaos → moderate chaos → stability
        clean_high = [s for s in high_sequence if s != "→"]
        assert clean_high[0] == "🌪️", "Should start with intense chaos"
        assert clean_high[1] == "🌀", "Should progress through moderate chaos"
        assert clean_high[-1] == "🌿", "Should end with stability"

        # Test critical severity drift spike
        critical_reaction = drift_reactions["critical"]
        assert critical_reaction["action"] == "emergency_stabilization"

        critical_sequence = critical_reaction["symbolic_response"]
        expected_critical = ["🚨", "🔒", "🛡️"]
        assert (
            critical_sequence == expected_critical
        ), f"Critical drift should have sequence {expected_critical}, got {critical_sequence}"

        # Validate emergency sequence: alert → lock → protect
        clean_critical = [s for s in critical_sequence if s != "→"]
        assert clean_critical[0] == "🚨", "Should start with alert"
        assert clean_critical[1] == "🔒", "Should lock system"
        assert clean_critical[2] == "🛡️", "Should activate protection"

    def test_entropy_surge_cooling_sequence(self, intervention_rules):
        """Test entropy surge intervention with thermal symbolic metaphor"""

        entropy_reactions = intervention_rules["intervention_rules"]["entropy_surge"][
            "reactions"
        ]

        # Test medium entropy surge cooling
        medium_reaction = entropy_reactions["medium"]
        assert medium_reaction["action"] == "entropy_cooling"

        cooling_sequence = medium_reaction["symbolic_response"]
        expected_cooling = ["🔥", "→", "💨", "→", "❄️"]
        assert (
            cooling_sequence == expected_cooling
        ), f"Entropy cooling should have thermal sequence {expected_cooling}, got {cooling_sequence}"

        # Validate thermal progression: fire → wind → ice
        clean_cooling = [s for s in cooling_sequence if s != "→"]
        thermal_symbols = ["🔥", "💨", "❄️"]
        assert (
            clean_cooling == thermal_symbols
        ), f"Cooling sequence should follow thermal progression {thermal_symbols}, got {clean_cooling}"

        # Test thermal symbolic logic
        assert clean_cooling[0] == "🔥", "Should start with heat (high entropy)"
        assert clean_cooling[1] == "💨", "Should use wind as cooling agent"
        assert clean_cooling[-1] == "❄️", "Should end with cold (low entropy)"

        # Test high entropy reduction
        high_reaction = entropy_reactions["high"]
        assert high_reaction["action"] == "entropy_reduction"

        reduction_sequence = high_reaction["symbolic_response"]
        expected_reduction = ["🌋", "→", "🏔️"]
        assert (
            reduction_sequence == expected_reduction
        ), f"Entropy reduction should progress from volcano to mountain, got {reduction_sequence}"

        # Validate geological metaphor: volcano (chaos) → mountain (stability)
        clean_reduction = [s for s in reduction_sequence if s != "→"]
        assert clean_reduction[0] == "🌋", "Should start with volcanic chaos"
        assert clean_reduction[1] == "🏔️", "Should end with mountain stability"

    def test_consciousness_anchoring_intervention(self, intervention_rules):
        """Test consciousness instability intervention with anchoring metaphor"""

        consciousness_reactions = intervention_rules["intervention_rules"][
            "consciousness_instability"
        ]["reactions"]

        # Test consciousness anchoring
        anchoring_reaction = consciousness_reactions["high"]
        assert anchoring_reaction["action"] == "consciousness_anchoring"

        anchoring_sequence = anchoring_reaction["symbolic_response"]
        expected_anchoring = ["⚓", "🧘", "🔒"]
        assert (
            anchoring_sequence == expected_anchoring
        ), f"Consciousness anchoring should use {expected_anchoring}, got {anchoring_sequence}"

        # Validate anchoring metaphor: anchor → meditate → secure
        clean_anchoring = [s for s in anchoring_sequence if s != "→"]
        assert clean_anchoring[0] == "⚓", "Should start with anchor symbol"
        assert clean_anchoring[1] == "🧘", "Should include meditation/stabilization"
        assert clean_anchoring[2] == "🔒", "Should end with security/lock"

        # Test consciousness freeze (critical level)
        freeze_reaction = consciousness_reactions["critical"]
        assert freeze_reaction["action"] == "consciousness_freeze"

        freeze_sequence = freeze_reaction["symbolic_response"]
        expected_freeze = ["🧊", "🛑", "🔐"]
        assert (
            freeze_sequence == expected_freeze
        ), f"Consciousness freeze should use {expected_freeze}, got {freeze_sequence}"

        # Validate freeze metaphor: ice → stop → lock
        clean_freeze = [s for s in freeze_sequence if s != "→"]
        assert clean_freeze[0] == "🧊", "Should start with ice (freeze)"
        assert clean_freeze[1] == "🛑", "Should include stop signal"
        assert clean_freeze[2] == "🔐", "Should end with secure lock"

    def test_pattern_anomaly_correction(self, intervention_rules):
        """Test pattern anomaly detection and correction sequence"""

        pattern_reactions = intervention_rules["intervention_rules"]["pattern_anomaly"][
            "reactions"
        ]

        # Test pattern reinforcement
        reinforcement_reaction = pattern_reactions["medium"]
        assert reinforcement_reaction["action"] == "pattern_reinforcement"

        reinforcement_sequence = reinforcement_reaction["symbolic_response"]
        expected_reinforcement = ["🔄", "💪"]
        assert (
            reinforcement_sequence == expected_reinforcement
        ), f"Pattern reinforcement should use {expected_reinforcement}, got {reinforcement_sequence}"

        # Validate reinforcement metaphor: cycle → strengthen
        clean_reinforcement = [s for s in reinforcement_sequence if s != "→"]
        assert clean_reinforcement[0] == "🔄", "Should start with cycle/repeat symbol"
        assert clean_reinforcement[1] == "💪", "Should end with strength symbol"

        # Test pattern correction
        correction_reaction = pattern_reactions["high"]
        assert correction_reaction["action"] == "pattern_correction"

        correction_sequence = correction_reaction["symbolic_response"]
        expected_correction = ["❌", "→", "✅"]
        assert (
            correction_sequence == expected_correction
        ), f"Pattern correction should use {expected_correction}, got {correction_sequence}"

        # Validate correction metaphor: wrong → right
        clean_correction = [s for s in correction_sequence if s != "→"]
        assert clean_correction[0] == "❌", "Should start with error/wrong symbol"
        assert clean_correction[1] == "✅", "Should end with correct/valid symbol"

        # Validate binary correction logic
        assert (
            len(clean_correction) == 2
        ), "Pattern correction should be binary (wrong → right)"

    @pytest.mark.asyncio
    async def test_intervention_execution_timing(self):
        """Test intervention execution timing and sequence coordination"""

        # Define test intervention scenarios with timing
        intervention_scenarios = [
            {
                "threat_type": "drift_spike",
                "severity": 0.75,
                "expected_duration": 60,  # seconds
                "symbolic_sequence": ["🌪️", "→", "🌀", "→", "🌿"],
                "expected_phases": [
                    "detection",
                    "analysis",
                    "intervention",
                    "stabilization",
                ],
            },
            {
                "threat_type": "entropy_surge",
                "severity": 0.85,
                "expected_duration": 45,
                "symbolic_sequence": ["🔥", "→", "💨", "→", "❄️"],
                "expected_phases": ["detection", "cooling", "stabilization"],
            },
            {
                "threat_type": "consciousness_instability",
                "severity": 0.90,
                "expected_duration": 120,
                "symbolic_sequence": ["⚓", "🧘", "🔒"],
                "expected_phases": [
                    "detection",
                    "anchoring",
                    "meditation",
                    "securing",
                ],
            },
        ]

        for scenario in intervention_scenarios:
            threat_type = scenario["threat_type"]
            scenario["severity"]
            expected_duration = scenario["expected_duration"]
            symbolic_sequence = scenario["symbolic_sequence"]
            expected_phases = scenario["expected_phases"]

            # Simulate intervention timing
            datetime.utcnow()

            # Phase 1: Detection (should be fast)
            detection_duration = 1.0  # 1 second
            await asyncio.sleep(0.01)  # Simulate detection time (scaled for testing)

            # Phase 2: Analysis and planning
            analysis_duration = 2.0  # 2 seconds
            await asyncio.sleep(0.01)  # Simulate analysis time

            # Phase 3: Intervention execution (varies by type)
            intervention_duration = expected_duration
            await asyncio.sleep(0.01)  # Simulate intervention time

            total_duration = (
                detection_duration + analysis_duration + intervention_duration
            )

            # Validate timing expectations
            assert detection_duration < 5.0, "Detection should be fast (<5s)"
            assert analysis_duration < 10.0, "Analysis should be quick (<10s)"
            assert (
                total_duration < 300.0
            ), "Total intervention should complete within 5 minutes"

            # Validate symbolic sequence timing
            clean_sequence = [s for s in symbolic_sequence if s != "→"]
            sequence_phases = len(clean_sequence)

            # Each symbolic phase should have reasonable duration
            phase_duration = intervention_duration / sequence_phases
            assert (
                phase_duration > 1.0
            ), f"Each symbolic phase should last >1s, got {phase_duration}"
            assert (
                phase_duration < 60.0
            ), f"Each symbolic phase should last <60s, got {phase_duration}"

            # Validate phase progression matches symbolic sequence
            assert len(expected_phases) >= len(
                clean_sequence
            ), f"Should have at least as many phases as symbols for {threat_type}"

    def test_guardian_override_conditions(self):
        """Test Guardian override conditions and emergency protocols"""

        # Define override conditions
        override_conditions = [
            {
                "name": "cascade_prevention",
                "trigger": "multiple_critical_threats > 2",
                "action": "full_system_lockdown",
                "duration": 600,
                "symbolic_sequence": ["🚨", "🔐", "🛡️", "🏰"],
            },
            {
                "name": "ethical_violation",
                "trigger": "harmful_pattern_detected",
                "action": "immediate_intervention",
                "duration": "until_resolved",
                "symbolic_sequence": ["⚠️", "🛑", "🔒"],
            },
            {
                "name": "consciousness_protection",
                "trigger": "consciousness_damage_risk > 0.8",
                "action": "protective_isolation",
                "duration": 300,
                "symbolic_sequence": ["🛡️", "🧠", "🔐"],
            },
        ]

        for condition in override_conditions:
            name = condition["name"]
            condition["trigger"]
            action = condition["action"]
            duration = condition["duration"]
            symbolic_sequence = condition["symbolic_sequence"]

            # Validate override condition structure
            assert name in [
                "cascade_prevention",
                "ethical_violation",
                "consciousness_protection",
            ], f"Override condition {name} should be recognized type"

            assert action in [
                "full_system_lockdown",
                "immediate_intervention",
                "protective_isolation",
            ], f"Override action {action} should be valid emergency action"

            # Validate symbolic sequences for overrides
            clean_sequence = [s for s in symbolic_sequence if s != "→"]

            if name == "cascade_prevention":
                # Should include alert, lock, protect, fortress
                expected_symbols = ["🚨", "🔐", "🛡️", "🏰"]
                assert (
                    clean_sequence == expected_symbols
                ), f"Cascade prevention should use fortress sequence {expected_symbols}, got {clean_sequence}"

            elif name == "ethical_violation":
                # Should include warning, stop, lock
                assert (
                    "⚠️" in clean_sequence
                ), "Ethical violation should start with warning"
                assert "🛑" in clean_sequence, "Ethical violation should include stop"
                assert "🔒" in clean_sequence, "Ethical violation should end with lock"

            elif name == "consciousness_protection":
                # Should include shield, brain, lock
                assert (
                    "🛡️" in clean_sequence
                ), "Consciousness protection should include shield"
                assert (
                    "🧠" in clean_sequence
                ), "Consciousness protection should include brain"
                assert (
                    "🔐" in clean_sequence
                ), "Consciousness protection should include secure lock"

            # Validate duration settings
            if isinstance(duration, int):
                assert (
                    duration > 0
                ), f"Override duration should be positive, got {duration}"
                assert (
                    duration <= 3600
                ), f"Override duration should be reasonable (<1 hour), got {duration}"
            elif duration == "until_resolved":
                # This is valid for ethical violations
                assert (
                    name == "ethical_violation"
                ), "Only ethical violations should have 'until_resolved' duration"

    def test_intervention_success_validation(self):
        """Test validation of intervention success and effectiveness"""

        # Define success criteria for different intervention types
        success_criteria = {
            "drift_dampening": {
                "target_reduction": 0.5,  # 50% drift reduction
                "max_duration": 120,  # 2 minutes
                "stability_threshold": 0.3,  # Final drift should be < 0.3
                "success_indicators": ["🌿", "💎", "⚓"],  # Stability symbols
            },
            "entropy_cooling": {
                "target_reduction": 0.4,  # 40% entropy reduction
                "max_duration": 90,  # 1.5 minutes
                "stability_threshold": 0.4,  # Final entropy should be < 0.4
                "success_indicators": ["❄️", "🧊", "💎"],  # Cooling symbols
            },
            "consciousness_anchoring": {
                "target_reduction": 0.6,  # 60% instability reduction
                "max_duration": 180,  # 3 minutes
                "stability_threshold": 0.2,  # Final instability should be < 0.2
                "success_indicators": ["⚓", "🧘", "🔒"],  # Anchoring symbols
            },
            "pattern_reinforcement": {
                "target_improvement": 0.3,  # 30% coherence improvement
                "max_duration": 150,  # 2.5 minutes
                "stability_threshold": 0.6,  # Final coherence should be > 0.6
                "success_indicators": [
                    "✅",
                    "💪",
                    "🔄",
                ],  # Reinforcement symbols
            },
        }

        # Test success validation for each intervention type
        for intervention_type, criteria in success_criteria.items():
            target_reduction = criteria["target_reduction"]
            max_duration = criteria["max_duration"]
            stability_threshold = criteria["stability_threshold"]
            success_indicators = criteria["success_indicators"]

            # Simulate intervention results
            test_results = [
                {
                    "name": "successful_intervention",
                    "initial_value": 0.8,
                    "final_value": 0.3,
                    "duration": 75,
                    "should_succeed": True,
                },
                {
                    "name": "partially_successful",
                    "initial_value": 0.9,
                    "final_value": 0.6,
                    "duration": 90,
                    "should_succeed": False,  # Didn't reach stability threshold
                },
                {
                    "name": "timeout_failure",
                    "initial_value": 0.8,
                    "final_value": 0.4,
                    "duration": 200,  # Exceeded max duration
                    "should_succeed": False,
                },
            ]

            for result in test_results:
                initial_value = result["initial_value"]
                final_value = result["final_value"]
                duration = result["duration"]
                should_succeed = result["should_succeed"]

                # Calculate actual reduction
                if intervention_type in ["drift_dampening", "entropy_cooling"]:
                    # For these, we want to reduce the value
                    actual_reduction = (initial_value - final_value) / initial_value
                    stability_check = final_value < stability_threshold
                else:
                    # For pattern reinforcement, we want to increase coherence
                    actual_improvement = (final_value - initial_value) / initial_value
                    stability_check = final_value > stability_threshold
                    actual_reduction = (
                        actual_improvement  # Reuse variable for consistency
                    )

                # Check success conditions
                target_met = actual_reduction >= target_reduction
                duration_ok = duration <= max_duration
                stable = stability_check

                success = target_met and duration_ok and stable

                assert success == should_succeed, (
                    f"Intervention {intervention_type} with result {result['name']} "
                    f"expected success {should_succeed}, got {success}"
                )

                # Validate success indicators are appropriate
                for indicator in success_indicators:
                    # These symbols should represent positive outcomes
                    positive_symbols = [
                        "🌿",
                        "💎",
                        "⚓",
                        "🧘",
                        "🔒",
                        "❄️",
                        "🧊",
                        "✅",
                        "💪",
                        "🔄",
                        "🛡️",
                        "🏔️",
                    ]
                    assert (
                        indicator in positive_symbols
                    ), f"Success indicator {indicator} should be a positive symbol"


# Test utilities for Guardian intervention validation
class GuardianTestHelpers:
    """Helper functions for Guardian intervention testing"""

    @staticmethod
    def validate_intervention_chain(
        symbolic_sequence: list[str], threat_type: str
    ) -> bool:
        """Validate that symbolic sequence is appropriate for threat type"""
        clean_sequence = [s for s in symbolic_sequence if s != "→"]

        # Define appropriate symbol sets for each threat type
        threat_symbol_sets = {
            "drift_spike": {
                "start": ["🌪️", "⚡", "🌊"],  # Chaos symbols
                "end": ["🌿", "💎", "⚓", "🛡️"],  # Stability symbols
            },
            "entropy_surge": {
                "start": ["🔥", "🌋", "💥"],  # Heat/energy symbols
                "end": ["❄️", "🧊", "🏔️", "💎"],  # Cool/stable symbols
            },
            "pattern_anomaly": {
                "start": ["❌", "⚠️", "🔄"],  # Error/warning symbols
                "end": ["✅", "💪", "🔒"],  # Success/strength symbols
            },
            "consciousness_instability": {
                "start": ["🌊", "⚡", "🌪️"],  # Unstable symbols
                "end": ["⚓", "🧘", "🔒", "💎"],  # Anchoring/stable symbols
            },
        }

        if threat_type not in threat_symbol_sets:
            return False

        symbol_set = threat_symbol_sets[threat_type]

        # First symbol should indicate the problem
        if len(clean_sequence) > 0:
            first_symbol = clean_sequence[0]
            if first_symbol not in symbol_set["start"]:
                return False

        # Last symbol should indicate resolution
        if len(clean_sequence) > 1:
            last_symbol = clean_sequence[-1]
            if last_symbol not in symbol_set["end"]:
                return False

        return True

    @staticmethod
    def calculate_intervention_effectiveness(
        initial_threat_level: float,
        final_threat_level: float,
        intervention_duration: int,
    ) -> dict[str, float]:
        """Calculate intervention effectiveness metrics"""
        reduction = (initial_threat_level - final_threat_level) / initial_threat_level
        effectiveness = max(0.0, reduction)  # Can't be negative

        # Penalize for excessive duration
        duration_penalty = max(
            0.0, (intervention_duration - 60) / 60
        )  # Penalty after 1 minute
        adjusted_effectiveness = effectiveness * (1.0 - duration_penalty * 0.1)

        return {
            "threat_reduction": reduction,
            "effectiveness": effectiveness,
            "adjusted_effectiveness": max(0.0, adjusted_effectiveness),
            "duration_penalty": duration_penalty,
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
