"""
Quantum Security Integration Module
Provides integration wrapper for connecting the quantum security system to the quantum hub
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from .ΛBot_quantum_security import (
    QIThreat,
    SecurityAssessment,
    ΛBotQuantumSecurityOrchestrator)

logger = logging.getLogger(__name__)


class QISecurityIntegration:
    """
    Integration wrapper for the Quantum Security System.
    Provides a simplified interface for the quantum hub.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the quantum security integration"""
        self.config = config or {
            "qi_enhanced": True,
            "bio_symbolic_processing": True,
            "adaptive_security": True,
            "post_quantum_crypto": True,
        }

        # Initialize the quantum security orchestrator
        self.security_orchestrator = ΛBotQuantumSecurityOrchestrator(self.config)
        self.is_initialized = False

        # Cache for security assessments
        self.assessment_cache = {}

        logger.info("QISecurityIntegration initialized with config: %s", self.config)

    async def initialize(self):
        """Initialize the quantum security system and its components"""
        if self.is_initialized:
            return

        try:
            logger.info("Initializing quantum security system components...")

            # Initialize post-quantum cryptography
            await self._initialize_post_quantum_crypto()

            # Initialize bio-symbolic threat detection if available
            await self._initialize_bio_symbolic_detection()

            # Load security policies
            await self._load_security_policies()

            self.is_initialized = True
            logger.info("Quantum security system initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize quantum security system: {e}")
            raise

    async def _initialize_post_quantum_crypto(self):
        """Initialize post-quantum cryptography components"""
        # Pre-generate some quantum-resistant keys for faster operations
        logger.info("Pre-generating post-quantum key pairs...")

        for algorithm in ["kyber", "dilithium"]:
            try:
                await self.security_orchestrator.pq_crypto_engine.generate_quantum_resistant_keys(algorithm)
                logger.info(f"Generated {algorithm} keys successfully")
            except Exception as e:
                logger.warning(f"Failed to generate {algorithm} keys: {e}")

    async def _initialize_bio_symbolic_detection(self):
        """Initialize bio-symbolic threat detection if available"""
        if self.security_orchestrator.brain_symphony:
            logger.info("Bio-symbolic threat detection available and initialized")
        else:
            logger.warning("Bio-symbolic threat detection not available - using standard detection")

    async def _load_security_policies(self):
        """Load default security policies"""
        # This would typically load from a configuration file
        self.security_policies = {
            "qi_vulnerability_threshold": 0.7,
            "auto_mitigation_enabled": True,
            "encryption_upgrade_policy": "aggressive",
            "threat_response_mode": "adaptive",
        }

    async def perform_security_assessment(self, target: str, code: Optional[str] = None) -> SecurityAssessment:
        """
        Perform a comprehensive quantum security assessment

        Args:
            target: Target identifier (repository, system, etc.)
            code: Optional code to analyze

        Returns:
            SecurityAssessment with detected threats and recommendations
        """
        if not self.is_initialized:
            await self.initialize()

        # Check cache first
        cache_key = f"{target}:{hash(code)} if code else 'system'}"
        if cache_key in self.assessment_cache:
            cached = self.assessment_cache[cache_key]
            if (datetime.now(timezone.utc) - cached["timestamp"]).seconds < 300:  # 5 min cache
                return cached["assessment"]

        # Perform assessment
        assessment = await self.security_orchestrator.perform_quantum_security_assessment(target, code)

        # Cache the result
        self.assessment_cache[cache_key] = {
            "assessment": assessment,
            "timestamp": datetime.now(timezone.utc),
        }

        return assessment

    async def generate_quantum_resistant_keys(self, algorithm: str = "kyber") -> dict[str, Any]:
        """
        Generate quantum-resistant cryptographic keys

        Args:
            algorithm: Post-quantum algorithm to use

        Returns:
            Dict containing the key pair and metadata
        """
        if not self.is_initialized:
            await self.initialize()

        return await self.security_orchestrator.pq_crypto_engine.generate_quantum_resistant_keys(algorithm)

    async def encrypt_quantum_safe(self, data: bytes, public_key: str, algorithm: str = "kyber") -> dict[str, Any]:
        """
        Encrypt data using quantum-resistant algorithms

        Args:
            data: Data to encrypt
            public_key: Public key for encryption
            algorithm: Post-quantum algorithm to use

        Returns:
            Dict containing encrypted data and metadata
        """
        if not self.is_initialized:
            await self.initialize()

        return await self.security_orchestrator.pq_crypto_engine.qi_encrypt(data, public_key, algorithm)

    async def detect_quantum_threats(self, system_state: dict[str, Any]) -> list[QIThreat]:
        """
        Detect quantum-era security threats in the system

        Args:
            system_state: Current system state to analyze

        Returns:
            List of detected quantum threats
        """
        if not self.is_initialized:
            await self.initialize()

        # Use the vulnerability analyzer to detect threats
        threats = []

        # Check for quantum vulnerabilities
        if self.security_orchestrator.vuln_analyzer:
            vuln_report = await self.security_orchestrator.vuln_analyzer._analyze_quantum_vulnerabilities(
                json.dumps(system_state)
            )

            for vuln in vuln_report.get("vulnerabilities", []):
                threat = QIThreat(
                    threat_id=f"qt_{datetime.now(timezone.utc).timestamp()}",
                    threat_type=vuln["type"],
                    severity=vuln["severity"],
                    description=vuln["description"],
                    qi_signature={},
                    bio_patterns={},
                    confidence=vuln.get("confidence", 0.8),
                    detected_at=datetime.now(timezone.utc).isoformat(),
                )
                threats.append(threat)

        return threats

    async def orchestrate_security_response(self, assessment: SecurityAssessment) -> dict[str, Any]:
        """
        Orchestrate an adaptive security response based on assessment

        Args:
            assessment: Security assessment to respond to

        Returns:
            Dict containing response actions and results
        """
        if not self.is_initialized:
            await self.initialize()

        return await self.security_orchestrator.orchestrate_security_response(assessment)

    def get_security_metrics(self) -> dict[str, Any]:
        """Get current security metrics and statistics"""
        return self.security_orchestrator.security_metrics

    def get_supported_algorithms(self) -> list[str]:
        """Get list of supported post-quantum algorithms"""
        return list(self.security_orchestrator.pq_crypto_engine.pq_standards.keys())

    async def update_security_policies(self, policies: dict[str, Any]):
        """Update security policies"""
        self.security_policies.update(policies)
        logger.info(f"Security policies updated: {list(policies.keys()}")

    async def get_security_status(self) -> dict[str, Any]:
        """Get current security system status"""
        return {
            "initialized": self.is_initialized,
            "post_quantum_ready": True,
            "bio_symbolic_available": self.security_orchestrator.brain_symphony is not None,
            "active_algorithms": self.get_supported_algorithms(),
            "metrics": self.get_security_metrics(),
            "policies": self.security_policies,
        }


# Factory function for creating the integration
def create_quantum_security_integration(
    config: Optional[dict[str, Any]] = None,
) -> QISecurityIntegration:
    """Create and return a quantum security integration instance"""
    return QISecurityIntegration(config)


# Module validation function (for compatibility)
def __validate_module__():
    """Validate that the quantum security module is properly configured"""
    try:
        # Test basic functionality
        create_quantum_security_integration()
        logger.info("Quantum security integration module validated successfully")
        return True
    except Exception as e:
        logger.error(f"Quantum security integration validation failed: {e}")
        return False