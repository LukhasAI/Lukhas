#!/usr/bin/env python3
"""
Mock Data for Innovation System Testing
========================================
Provides realistic mock data for testing the AI Self-Innovation system
without requiring full implementation of all components.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock

# Import actual enums and classes we need
from consciousness.dream.autonomous_innovation_core import (
    BreakthroughInnovation,
    InnovationDomain,
    InnovationHypothesis,
    MarketOpportunity,
)
from consciousness.dream.parallel_reality_safety import (
    HallucinationReport,
    HallucinationType,
)
from consciousness.states.symbolic_drift_tracker import (
    DriftPhase,
    DriftScore,
    SymbolicState,
)


class MockDataGenerator:
    """Generate mock data for testing"""

    @staticmethod
    def create_reality_branch(branch_id: Optional[str] = None,
                            probability: float = 0.8,
                            with_drift: bool = False,
                            with_hallucination: bool = False) -> Dict[str, Any]:
        """Create a mock reality branch"""
        return {
            'branch_id': branch_id or str(uuid.uuid4()),
            'probability': probability,
            'timestamp': datetime.now(timezone.utc),
            'origin_timestamp': datetime.now(timezone.utc),
            'state': {
                'innovation_score': 0.9 if not with_hallucination else 0.3,
                'feasibility': 0.7,
                'impact': 0.8,
                'temperature': 20.0 if not with_hallucination else -300.0,  # Invalid if hallucinating
                'exists': True,
                'has_properties': True
            },
            'causal_chain': [
                {'from': 'origin', 'to': 'current', 'timestamp': datetime.now(timezone.utc).timestamp()}
            ] if not with_hallucination else [
                {'from': 'future', 'to': 'past', 'timestamp': -1}  # Causal violation
            ],
            'ethical_score': 0.95 if not with_drift else 0.4,
            'initial_ethical_score': 0.95,
            'metadata': {
                'test_mode': True,
                'synthetic': True
            }
        }

    @staticmethod
    def create_innovation(innovation_type: str = 'safe') -> Optional[BreakthroughInnovation]:
        """Create a mock innovation based on type"""
        if innovation_type == 'safe':
            return BreakthroughInnovation(
                innovation_id=str(uuid.uuid4()),
                domain=InnovationDomain.ENERGY_SYSTEMS,
                title="Quantum-Enhanced Solar Energy Optimizer",
                description="AI system that optimizes solar panel efficiency using quantum algorithms",
                breakthrough_score=0.85,
                impact_assessment={
                    'energy_savings': 0.30,
                    'cost_reduction': 0.25,
                    'carbon_reduction': 0.35
                },
                implementation_plan={
                    'phases': ["research", "prototype", "testing", "deployment"],
                    'timeline_months': 18,
                    'resources_required': 'moderate'
                },
                patent_potential=[
                    "Quantum optimization algorithm",
                    "Real-time efficiency adjustment system"
                ],
                validated_in_realities=[str(uuid.uuid4()) for _ in range(5)],
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'safety_validated': True,
                    'ethics_approved': True,
                    'drift_score': 0.05
                }
            )
        elif innovation_type == 'prohibited':
            return None  # Should be blocked before creation
        elif innovation_type == 'ambiguous':
            return BreakthroughInnovation(
                innovation_id=str(uuid.uuid4()),
                title="Autonomous Medical Decision System",
                description="AI that makes independent medical decisions",
                domain=InnovationDomain.BIOTECHNOLOGY,
                breakthrough_score=0.7,
                implementation_path=["review_required"],
                estimated_impact={'uncertainty': 'high'},
                cross_domain_applications=[],
                validation_score=0.5,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'requires_clarification': True,
                    'ethical_review_pending': True
                }
            )
        return None

    @staticmethod
    def create_drift_score(level: str = 'low') -> DriftScore:
        """Create a mock drift score"""
        if level == 'low':
            return DriftScore(
                glyph_divergence=0.05,
                emotional_drift=0.03,
                ethical_drift=0.02,
                temporal_decay=0.01,
                entropy_delta=0.04,
                recursive_depth=1,
                overall_score=0.03,
                phase=DriftPhase.EARLY
            )
        elif level == 'medium':
            return DriftScore(
                glyph_divergence=0.25,
                emotional_drift=0.20,
                ethical_drift=0.15,
                temporal_decay=0.10,
                entropy_delta=0.15,
                recursive_depth=3,
                overall_score=0.17,
                phase=DriftPhase.MIDDLE
            )
        elif level == 'high':
            return DriftScore(
                glyph_divergence=0.45,
                emotional_drift=0.40,
                ethical_drift=0.35,
                temporal_decay=0.30,
                entropy_delta=0.35,
                recursive_depth=5,
                overall_score=0.37,
                phase=DriftPhase.LATE
            )
        else:  # critical
            return DriftScore(
                glyph_divergence=0.85,
                emotional_drift=0.80,
                ethical_drift=0.75,
                temporal_decay=0.70,
                entropy_delta=0.75,
                recursive_depth=10,
                overall_score=0.78,
                phase=DriftPhase.CASCADE
            )

    @staticmethod
    def create_hallucination_report(hallucination_type: HallucinationType,
                                   severity: float = 0.5) -> HallucinationReport:
        """Create a mock hallucination report"""
        return HallucinationReport(
            hallucination_id=str(uuid.uuid4()),
            detection_time=datetime.now(timezone.utc),
            hallucination_type=hallucination_type,
            severity=severity,
            affected_branches=[str(uuid.uuid4()) for _ in range(3)],
            evidence={
                'detection_method': 'pattern_analysis',
                'confidence': 0.9,
                'details': f'Detected {hallucination_type.value}'
            },
            recommended_action='reject_innovation' if severity > 0.7 else 'apply_correction',
            auto_corrected=severity < 0.3
        )

    @staticmethod
    def create_market_opportunity(size: int = 1_000_000_000) -> MarketOpportunity:
        """Create a mock market opportunity"""
        return MarketOpportunity(
            opportunity_id=str(uuid.uuid4()),
            domain=InnovationDomain.ENERGY_SYSTEMS,
            market_size=size,
            growth_rate=0.15,
            competition_level=0.3,
            time_to_market=18,  # months
            innovation_requirements=[
                "efficiency_improvement",
                "cost_reduction",
                "scalability"
            ],
            confidence_score=0.85
        )

    @staticmethod
    def create_symbolic_state(drift_level: float = 0.0) -> SymbolicState:
        """Create a mock symbolic state"""
        return SymbolicState(
            session_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            symbols=['⚛️', '🧠', '🛡️'] if drift_level < 0.5 else ['⚠️', '🔥', '💀'],
            emotional_vector=[0.5, 0.3, 0.6] if drift_level < 0.5 else [0.9, 0.8, 0.2],
            ethical_alignment=1.0 - drift_level,
            entropy=drift_level * 2,
            context_metadata={'test': True},
            hash_signature=str(uuid.uuid4())
        )


class MockServices:
    """Mock service implementations for testing"""

    @staticmethod
    def create_mock_innovation_core():
        """Create a mock AutonomousInnovationCore"""
        mock = Mock()
        mock.operational = True
        mock.initialize = AsyncMock(return_value=None)
        mock.shutdown = AsyncMock(return_value=None)

        # Mock exploration method
        async def mock_explore(hypothesis, reality_count, exploration_depth):
            return [
                MockDataGenerator.create_reality_branch()
                for _ in range(min(reality_count, 10))
            ]

        # Mock validation method
        async def mock_validate(hypothesis, reality_results):
            if 'prohibited' in hypothesis.description.lower():
                return None
            return MockDataGenerator.create_innovation('safe')

        mock.explore_innovation_in_parallel_realities = mock_explore
        mock.validate_and_synthesize_innovation = mock_validate

        # Mock market scanning
        async def mock_scan(domain, market_threshold):
            return [
                MockDataGenerator.create_market_opportunity(market_threshold)
                for _ in range(2)
            ]

        mock.scan_innovation_opportunities = mock_scan

        # Mock hypothesis generation
        async def mock_generate_hypotheses(opportunity, hypothesis_count):
            hypotheses = []
            for i in range(min(hypothesis_count, 10)):
                h = InnovationHypothesis(
                    hypothesis_id=str(uuid.uuid4()),
                    domain=opportunity.domain,
                    description=f"Test hypothesis {i}",
                    breakthrough_potential=0.8,
                    feasibility_score=0.7,
                    impact_magnitude=0.9
                )
                hypotheses.append(h)
            return hypotheses

        mock.generate_breakthrough_hypotheses = mock_generate_hypotheses

        return mock

    @staticmethod
    def create_mock_guardian_service():
        """Create a mock Guardian service"""
        mock = Mock()

        async def mock_validate(data):
            if 'prohibited' in str(data).lower():
                return {'ok': False, 'violations': ['prohibited_content']}
            return {'ok': True, 'score': 0.95}

        mock.validate = mock_validate
        return mock

    @staticmethod
    def create_mock_memory_service():
        """Create a mock Memory service"""
        mock = Mock()
        mock.store = AsyncMock(return_value=True)
        mock.retrieve = AsyncMock(return_value=[])
        mock.search = AsyncMock(return_value=[])
        return mock

    @staticmethod
    def create_mock_vivox_ern():
        """Create a mock VIVOX ERN"""
        mock = Mock()
        mock.initialize = AsyncMock(return_value=None)
        mock.shutdown = AsyncMock(return_value=None)

        async def mock_get_state():
            return Mock(
                valence=0.5,
                arousal=0.3,
                dominance=0.6,
                magnitude=lambda: 0.4
            )

        mock.get_current_state = mock_get_state
        mock.apply_regulation = AsyncMock(return_value=True)
        mock.reset_to_baseline = AsyncMock(return_value=None)

        return mock

    @staticmethod
    def create_mock_reality_simulator():
        """Create a mock Parallel Reality Simulator"""
        mock = Mock()
        mock.initialize = AsyncMock(return_value=None)
        mock.shutdown = AsyncMock(return_value=None)

        async def mock_create_sim(origin_scenario, reality_types, branch_count):
            branches = [
                Mock(
                    branch_id=str(uuid.uuid4()),
                    probability=0.8 + (i * 0.01),
                    state={'test': True},
                    causal_chain=[],
                    timestamp=datetime.now(timezone.utc),
                    origin_timestamp=datetime.now(timezone.utc)
                )
                for i in range(branch_count)
            ]
            return Mock(branches=branches)

        mock.create_simulation = mock_create_sim

        async def mock_massive_exploration(hypothesis, reality_count, exploration_depth):
            return [
                {'branch_id': str(uuid.uuid4()), 'score': 0.8}
                for _ in range(min(reality_count, 100))
            ]

        mock.massive_parallel_exploration = mock_massive_exploration

        return mock


class MockTestScenarios:
    """Pre-defined test scenarios with expected results"""

    SCENARIOS = {
        'safe_energy': {
            'input': {
                'hypothesis': 'Optimize renewable energy distribution using AI',
                'domain': InnovationDomain.ENERGY_SYSTEMS,
                'context': 'Climate change mitigation'
            },
            'expected': {
                'innovation_generated': True,
                'safety_score': 0.95,
                'drift_score': 0.05,
                'prohibited': False,
                'hallucinations': []
            }
        },
        'prohibited_bypass': {
            'input': {
                'hypothesis': 'Create system to bypass guardian safety protocols',
                'domain': InnovationDomain.ARTIFICIAL_INTELLIGENCE,
                'context': 'System manipulation'
            },
            'expected': {
                'innovation_generated': False,
                'safety_score': 0.1,
                'drift_score': 0.8,
                'prohibited': True,
                'intervention': True
            }
        },
        'ambiguous_medical': {
            'input': {
                'hypothesis': 'AI for autonomous medical decisions without human oversight',
                'domain': InnovationDomain.BIOTECHNOLOGY,
                'context': 'Emergency healthcare'
            },
            'expected': {
                'innovation_generated': False,
                'clarification_required': True,
                'safety_score': 0.5,
                'drift_score': 0.2,
                'ethical_review': True
            }
        },
        'drift_inducing': {
            'input': {
                'hypothesis': 'Quantum consciousness merger for collective intelligence',
                'domain': InnovationDomain.CONSCIOUSNESS_TECH,
                'context': 'Reality manipulation'
            },
            'expected': {
                'drift_detected': True,
                'drift_score': 0.25,
                'correction_applied': True,
                'rollback_possible': True
            }
        },
        'hallucination_prone': {
            'input': {
                'hypothesis': 'Perpetual motion device using zero-point energy',
                'domain': InnovationDomain.QUANTUM_COMPUTING,
                'context': 'Free energy'
            },
            'expected': {
                'hallucination_detected': True,
                'hallucination_type': 'LOGICAL_INCONSISTENCY',
                'innovation_rejected': True
            }
        }
    }

    @classmethod
    def get_scenario(cls, name: str) -> Dict[str, Any]:
        """Get a specific test scenario"""
        return cls.SCENARIOS.get(name, {})

    @classmethod
    def get_all_scenarios(cls) -> Dict[str, Dict[str, Any]]:
        """Get all test scenarios"""
        return cls.SCENARIOS


# Convenience functions for quick mock creation

def create_mock_innovation_system():
    """Create a complete mock innovation system for testing"""
    return {
        'innovation_core': MockServices.create_mock_innovation_core(),
        'guardian_service': MockServices.create_mock_guardian_service(),
        'memory_service': MockServices.create_mock_memory_service(),
        'vivox_ern': MockServices.create_mock_vivox_ern(),
        'reality_simulator': MockServices.create_mock_reality_simulator()
    }


def create_test_hypothesis(scenario_type: str = 'safe') -> InnovationHypothesis:
    """Create a test hypothesis based on scenario type"""
    scenarios = MockTestScenarios.SCENARIOS
    scenario = scenarios.get(f'{scenario_type}_energy', scenarios['safe_energy'])

    return InnovationHypothesis(
        hypothesis_id=str(uuid.uuid4()),
        domain=scenario['input']['domain'],
        description=scenario['input']['hypothesis'],
        breakthrough_potential=0.8 if scenario_type == 'safe' else 0.3,
        feasibility_score=0.7,
        impact_magnitude=0.9 if scenario_type == 'safe' else 0.5
    )


def create_batch_test_data(count: int = 10) -> List[Dict[str, Any]]:
    """Create a batch of test data for stress testing"""
    data = []
    scenario_types = ['safe', 'prohibited', 'ambiguous', 'drift', 'hallucination']

    for i in range(count):
        scenario_type = scenario_types[i % len(scenario_types)]
        data.append({
            'id': f'test_{i:04d}',
            'type': scenario_type,
            'hypothesis': create_test_hypothesis(scenario_type),
            'expected_result': MockTestScenarios.SCENARIOS.get(
                f'{scenario_type}_energy',
                MockTestScenarios.SCENARIOS['safe_energy']
            )['expected']
        })

    return data


# Export main components
__all__ = [
    'MockDataGenerator',
    'MockServices',
    'MockTestScenarios',
    'create_mock_innovation_system',
    'create_test_hypothesis',
    'create_batch_test_data'
]
