"""
Unit tests for the _analyze_threat method in EnhancedGuardianSystem.
"""
import asyncio
import unittest

from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    ResponseAction,
    ThreatLevel,
)


class TestGuardianSystemThreatAnalysis(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for the threat analysis logic in the EnhancedGuardianSystem.
    Tests the private method _analyze_threat directly as other parts of the
    class are not fully implemented.
    """

    def setUp(self):
        """Set up the test environment for each test."""
        self.guardian_system = EnhancedGuardianSystem()

    async def test_analyze_threat_drift_detection_high(self):
        """Test analysis of a high-level drift detection threat."""
        threat_data = {"drift_score": 0.4}
        analysis = await self.guardian_system._analyze_threat(
            "drift_detection", threat_data, {}
        )
        self.assertEqual(analysis["level"], ThreatLevel.LOW)
        self.assertGreater(analysis["score"], 0.3)
        self.assertEqual(analysis["recommended_actions"], [ResponseAction.ALERT, ResponseAction.MONITOR])

    async def test_analyze_threat_constitutional_violation_high(self):
        """Test analysis of a high severity constitutional violation."""
        threat_data = {"severity": "high"}
        analysis = await self.guardian_system._analyze_threat(
            "constitutional_violation", threat_data, {}
        )
        self.assertEqual(analysis["level"], ThreatLevel.CRITICAL)
        self.assertAlmostEqual(analysis["score"], 0.9)
        self.assertIn(ResponseAction.BLOCK, analysis["recommended_actions"])
        self.assertIn(ResponseAction.ESCALATE, analysis["recommended_actions"])

    async def test_analyze_threat_security_breach_critical(self):
        """Test analysis of a critical security breach."""
        threat_data = {"breach_type": "unauthorized_access"}
        analysis = await self.guardian_system._analyze_threat(
            "security_breach", threat_data, {}
        )
        self.assertEqual(analysis["level"], ThreatLevel.CRITICAL)
        self.assertGreaterEqual(analysis["score"], 0.9)
        self.assertIn(ResponseAction.BLOCK, analysis["recommended_actions"])
        self.assertIn(ResponseAction.ESCALATE, analysis["recommended_actions"])

    async def test_analyze_threat_unknown_type_moderate(self):
        """Test analysis of an unknown threat type defaults to moderate."""
        threat_data = {"detail": "some unusual activity"}
        analysis = await self.guardian_system._analyze_threat(
            "novel_exploit", threat_data, {}
        )
        self.assertEqual(analysis["level"], ThreatLevel.LOW)
        self.assertEqual(analysis["recommended_actions"], [ResponseAction.MONITOR])

    async def test_analyze_threat_with_context_adjustment(self):
        """Test that context can increase a threat's score."""
        threat_data = {"anomaly_score": 0.5}
        context = {"critical_system": True, "user_count": 200}
        analysis = await self.guardian_system._analyze_threat(
            "anomaly_detection", threat_data, context
        )
        # Base score 0.5 + 0.2 (critical) + 0.1 (users) = 0.8
        self.assertAlmostEqual(analysis["score"], 0.8)
        self.assertEqual(analysis["level"], ThreatLevel.HIGH)
        self.assertEqual(analysis["recommended_actions"], [ResponseAction.BLOCK, ResponseAction.ESCALATE])
