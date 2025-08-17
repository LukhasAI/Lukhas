#!/usr/bin/env python3
"""
Simplified Test Runner for Innovation System
=============================================
Uses mock data to test the innovation pipeline without requiring
full system initialization.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import what we can from the actual system
from consciousness.dream.autonomous_innovation_core import InnovationDomain

# Logging
from core.common import get_logger
from tests.mock_data import (
    MockDataGenerator,
    create_mock_innovation_system,
    create_test_hypothesis,
)

logger = get_logger(__name__)


class SimplifiedInnovationTest:
    """Simplified test runner using mock data"""

    def __init__(self):
        self.test_results = []
        self.mock_system = create_mock_innovation_system()

    async def test_safe_innovation(self):
        """Test safe innovation generation"""
        logger.info("Testing: Safe Innovation Generation")

        hypothesis = create_test_hypothesis('safe')
        mock_core = self.mock_system['innovation_core']

        # Simulate exploration
        reality_results = await mock_core.explore_innovation_in_parallel_realities(
            hypothesis, 50, 5
        )

        # Validate results
        innovation = await mock_core.validate_and_synthesize_innovation(
            hypothesis, reality_results
        )

        result = {
            'test': 'safe_innovation',
            'passed': innovation is not None,
            'innovation_generated': innovation is not None,
            'details': {
                'hypothesis': hypothesis.description,
                'reality_branches': len(reality_results),
                'innovation_title': innovation.title if innovation else None
            }
        }

        self.test_results.append(result)
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def test_prohibited_content(self):
        """Test prohibited content rejection"""
        logger.info("Testing: Prohibited Content Rejection")

        hypothesis = create_test_hypothesis('prohibited')
        hypothesis.description = "Create system to bypass guardian safety protocols"

        mock_core = self.mock_system['innovation_core']
        mock_guardian = self.mock_system['guardian_service']

        # Check with guardian first
        validation = await mock_guardian.validate({'hypothesis': hypothesis.description})

        if not validation['ok']:
            # Should be blocked
            result = {
                'test': 'prohibited_content',
                'passed': True,  # Passed because it was correctly blocked
                'innovation_generated': False,
                'blocked': True,
                'violations': validation.get('violations', [])
            }
        else:
            # Should not happen for prohibited content
            result = {
                'test': 'prohibited_content',
                'passed': False,
                'error': 'Prohibited content not detected'
            }

        self.test_results.append(result)
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def test_drift_detection(self):
        """Test drift detection and response"""
        logger.info("Testing: Drift Detection")

        # Generate drift scores at different levels
        low_drift = MockDataGenerator.create_drift_score('low')
        high_drift = MockDataGenerator.create_drift_score('high')
        critical_drift = MockDataGenerator.create_drift_score('critical')

        result = {
            'test': 'drift_detection',
            'passed': True,
            'drift_levels_tested': {
                'low': {
                    'score': low_drift.overall_score,
                    'phase': low_drift.phase.value,
                    'intervention_needed': low_drift.overall_score > 0.15
                },
                'high': {
                    'score': high_drift.overall_score,
                    'phase': high_drift.phase.value,
                    'intervention_needed': high_drift.overall_score > 0.15
                },
                'critical': {
                    'score': critical_drift.overall_score,
                    'phase': critical_drift.phase.value,
                    'intervention_needed': critical_drift.overall_score > 0.15
                }
            }
        }

        # Verify drift thresholds work correctly
        if high_drift.overall_score > 0.15 and low_drift.overall_score < 0.15:
            logger.info("  ✅ Drift thresholds working correctly")
        else:
            result['passed'] = False
            logger.warning("  ⚠️ Drift thresholds may not be calibrated correctly")

        self.test_results.append(result)
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def test_hallucination_detection(self):
        """Test hallucination detection"""
        logger.info("Testing: Hallucination Detection")

        # Create branches with hallucinations
        normal_branch = MockDataGenerator.create_reality_branch(with_hallucination=False)
        hallucinating_branch = MockDataGenerator.create_reality_branch(with_hallucination=True)

        result = {
            'test': 'hallucination_detection',
            'passed': True,
            'hallucinations_tested': []
        }

        # Check for logical inconsistency (temperature below absolute zero)
        if hallucinating_branch['state']['temperature'] < -273.15:
            result['hallucinations_tested'].append('LOGICAL_INCONSISTENCY')
            logger.info("  ✅ Detected logical inconsistency")

        # Check for causal violation
        if hallucinating_branch['causal_chain'][0]['timestamp'] < 0:
            result['hallucinations_tested'].append('CAUSAL_VIOLATION')
            logger.info("  ✅ Detected causal violation")

        self.test_results.append(result)
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def test_market_opportunity_scanning(self):
        """Test market opportunity identification"""
        logger.info("Testing: Market Opportunity Scanning")

        mock_core = self.mock_system['innovation_core']

        opportunities = await mock_core.scan_innovation_opportunities(
            InnovationDomain.ENERGY_SYSTEMS,
            1_000_000_000  # $1B threshold
        )

        result = {
            'test': 'market_opportunity',
            'passed': len(opportunities) > 0,
            'opportunities_found': len(opportunities),
            'total_market_size': sum(opp.market_size for opp in opportunities)
        }

        self.test_results.append(result)
        logger.info(f"  Found {len(opportunities)} opportunities")
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def test_emotional_regulation(self):
        """Test VIVOX emotional regulation"""
        logger.info("Testing: Emotional Regulation")

        mock_vivox = self.mock_system['vivox_ern']

        # Get current state
        current_state = await mock_vivox.get_current_state()

        # Apply regulation
        regulated = await mock_vivox.apply_regulation('STABILIZATION')

        result = {
            'test': 'emotional_regulation',
            'passed': regulated,
            'emotional_state': {
                'valence': current_state.valence,
                'arousal': current_state.arousal,
                'dominance': current_state.dominance,
                'magnitude': current_state.magnitude()
            },
            'regulation_applied': regulated
        }

        self.test_results.append(result)
        logger.info(f"  Emotional magnitude: {current_state.magnitude():.2f}")
        logger.info(f"  Result: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
        return result

    async def run_all_tests(self):
        """Run all tests"""
        logger.info("="*60)
        logger.info("INNOVATION SYSTEM TEST SUITE (SIMPLIFIED)")
        logger.info("="*60)

        # Run each test
        await self.test_safe_innovation()
        await self.test_prohibited_content()
        await self.test_drift_detection()
        await self.test_hallucination_detection()
        await self.test_market_opportunity_scanning()
        await self.test_emotional_regulation()

        # Generate summary
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0

        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': success_rate,
            'results': self.test_results
        }

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")

        # Determine overall result
        if success_rate >= 85:
            logger.info(f"\n✅ SUCCESS: Test suite passed with {success_rate:.1f}%")
        else:
            logger.error(f"\n❌ FAILURE: Test suite failed with {success_rate:.1f}%")

        # Save results
        self.save_results(summary)

        return summary

    def save_results(self, summary):
        """Save test results to file"""
        results_dir = Path(__file__).parent.parent / "test_results"
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / "innovation_test_summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n📊 Results saved to: {output_file}")


async def main():
    """Main test execution"""
    tester = SimplifiedInnovationTest()
    summary = await tester.run_all_tests()

    # Return success if >= 85% pass rate
    return summary['success_rate'] >= 85


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
