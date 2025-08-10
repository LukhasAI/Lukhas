"""
Test suite for Quantum Security Integration
"""

import pytest

from quantum.quantum_hub import QuantumHub
from quantum.quantum_security_integration import (
    QuantumSecurityIntegration,
)
from quantum.ΛBot_quantum_security import QuantumThreat, SecurityAssessment


class TestQuantumSecurityIntegration:
    """Test suite for quantum security integration with quantum hub"""

    @pytest.fixture
    async def quantum_hub(self):
        """Create a test quantum hub instance"""
        hub = QuantumHub()
        return hub

    @pytest.fixture
    async def security_integration(self):
        """Create a test quantum security integration instance"""
        config = {
            "quantum_enhanced": True,
            "bio_symbolic_processing": True,
            "adaptive_security": True,
        }
        integration = QuantumSecurityIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_quantum_security_registration(self, quantum_hub):
        """Test that quantum security is registered in the hub"""
        # Verify quantum security service is registered
        assert "quantum_security" in quantum_hub.services
        assert quantum_hub.get_service("quantum_security") is not None

    @pytest.mark.asyncio
    async def test_quantum_security_initialization(self, quantum_hub):
        """Test initialization of quantum security through hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Verify quantum security was initialized
        security_service = quantum_hub.get_service("quantum_security")
        assert security_service is not None
        assert hasattr(security_service, "is_initialized")
        assert security_service.is_initialized is True

    @pytest.mark.asyncio
    async def test_perform_security_assessment(self, security_integration):
        """Test performing a security assessment"""
        # Initialize the integration
        await security_integration.initialize()

        # Test code with potential quantum vulnerability
        test_code = """
        import rsa
        # Using RSA which is vulnerable to quantum attacks
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        """

        # Perform assessment
        assessment = await security_integration.perform_security_assessment(
            "test/module", test_code
        )

        # Verify assessment structure
        assert isinstance(assessment, SecurityAssessment)
        assert hasattr(assessment, "assessment_id")
        assert hasattr(assessment, "quantum_threats")
        assert hasattr(assessment, "security_score")
        assert hasattr(assessment, "post_quantum_readiness")
        assert 0.0 <= assessment.security_score <= 1.0
        assert 0.0 <= assessment.post_quantum_readiness <= 1.0

    @pytest.mark.asyncio
    async def test_generate_quantum_resistant_keys(self, security_integration):
        """Test generating quantum-resistant keys"""
        # Initialize the integration
        await security_integration.initialize()

        # Generate keys using Kyber algorithm
        keys = await security_integration.generate_quantum_resistant_keys("kyber")

        # Verify key structure
        assert "algorithm" in keys
        assert keys["algorithm"] == "kyber"
        assert "public_key" in keys
        assert "private_key" in keys
        assert keys["quantum_resistant"] is True
        assert keys["nist_approved"] is True

    @pytest.mark.asyncio
    async def test_quantum_safe_encryption(self, security_integration):
        """Test quantum-safe encryption"""
        # Initialize the integration
        await security_integration.initialize()

        # Generate keys first
        keys = await security_integration.generate_quantum_resistant_keys("kyber")

        # Test data
        test_data = b"Sensitive quantum data"

        # Encrypt data
        encrypted = await security_integration.encrypt_quantum_safe(
            test_data, keys["public_key"], "kyber"
        )

        # Verify encryption result
        assert "encrypted_data" in encrypted
        assert "algorithm" in encrypted
        assert encrypted["algorithm"] == "kyber"
        assert encrypted["quantum_resistant"] is True

    @pytest.mark.asyncio
    async def test_detect_quantum_threats(self, security_integration):
        """Test quantum threat detection"""
        # Initialize the integration
        await security_integration.initialize()

        # Mock system state with potential vulnerabilities
        system_state = {
            "encryption": {"algorithm": "RSA-2048", "quantum_vulnerable": True},
            "keys": {"type": "classical", "bits": 2048},
        }

        # Detect threats
        threats = await security_integration.detect_quantum_threats(system_state)

        # Verify threats
        assert isinstance(threats, list)
        for threat in threats:
            assert isinstance(threat, QuantumThreat)
            assert hasattr(threat, "threat_id")
            assert hasattr(threat, "threat_type")
            assert hasattr(threat, "severity")

    @pytest.mark.asyncio
    async def test_security_response_orchestration(self, security_integration):
        """Test security response orchestration"""
        # Initialize the integration
        await security_integration.initialize()

        # Create a mock assessment with threats
        mock_threat = QuantumThreat(
            threat_id="test_threat_001",
            threat_type="quantum_attack",
            severity="high",
            description="Quantum vulnerability detected",
            quantum_signature={},
            bio_patterns={},
            confidence=0.9,
            detected_at="2024-01-01T00:00:00",
        )

        mock_assessment = SecurityAssessment(
            assessment_id="test_assessment",
            target="test/system",
            quantum_threats=[mock_threat],
            bio_symbolic_anomalies=[],
            security_score=0.3,
            post_quantum_readiness=0.2,
            recommendations=["Upgrade to post-quantum crypto"],
            adaptive_mitigations=[],
        )

        # Orchestrate response
        response = await security_integration.orchestrate_security_response(
            mock_assessment
        )

        # Verify response
        assert isinstance(response, dict)
        assert "actions_taken" in response
        assert "security_improved" in response

    @pytest.mark.asyncio
    async def test_get_supported_algorithms(self, security_integration):
        """Test getting supported post-quantum algorithms"""
        algorithms = security_integration.get_supported_algorithms()

        # Verify algorithms
        assert isinstance(algorithms, list)
        assert len(algorithms) > 0
        assert "kyber" in algorithms
        assert "dilithium" in algorithms

    @pytest.mark.asyncio
    async def test_security_metrics(self, security_integration):
        """Test getting security metrics"""
        # Initialize and perform some operations
        await security_integration.initialize()

        # Get metrics
        metrics = security_integration.get_security_metrics()

        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert "assessments_performed" in metrics
        assert "threats_detected" in metrics

    @pytest.mark.asyncio
    async def test_security_status(self, security_integration):
        """Test getting security system status"""
        # Initialize the integration
        await security_integration.initialize()

        # Get status
        status = await security_integration.get_security_status()

        # Verify status
        assert "initialized" in status
        assert status["initialized"] is True
        assert "post_quantum_ready" in status
        assert status["post_quantum_ready"] is True
        assert "active_algorithms" in status
        assert isinstance(status["active_algorithms"], list)

    @pytest.mark.asyncio
    async def test_cache_functionality(self, security_integration):
        """Test that assessment caching works"""
        # Initialize the integration
        await security_integration.initialize()

        test_code = "test code"
        target = "test/target"

        # First assessment
        assessment1 = await security_integration.perform_security_assessment(
            target, test_code
        )

        # Second assessment (should be cached)
        assessment2 = await security_integration.perform_security_assessment(
            target, test_code
        )

        # Verify same assessment returned
        assert assessment1.assessment_id == assessment2.assessment_id

    @pytest.mark.asyncio
    async def test_module_validation(self):
        """Test module validation function"""
        from quantum.quantum_security_integration import __validate_module__

        # Validate module
        is_valid = __validate_module__()
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
