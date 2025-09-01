"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Identity System Hub
Identity and authentication

This hub coordinates all identity subsystem components and provides
a unified interface for external systems to interact with identity.
"""

import asyncio
import logging
import time
from dataclasses import asdict
from typing import Any, Optional

from identity.deployment_package import DemoOrchestrator, TestOrchestrator
from identity.lukhus_ultimate_test_suite import UltimateTestOrchestrator
from identity.qrg_test_suite import TestQRGCore

from candidate.core.bridges.identity_core_bridge import IdentityCoreBridge
from candidate.core.common import get_logger
from lukhas.governance.identity.auth_backend.trust_scorer import LukhasTrustScorer
from lukhas.governance.identity.core.auth.biometric_integration import (
    BiometricIntegrationManager,
)
from lukhas.governance.identity.core.qrs_manager import QRSManager
from lukhas.governance.identity.core.sent.consent_manager import LambdaConsentManager
from lukhas.governance.identity.core.swarm.tier_aware_swarm_hub import TierAwareSwarmHub
from lukhas.governance.identity.interface import ConsentManager

# Agent 1 Task 3: Add enterprise authentication imports
try:
    from identity.enterprise.auth import (
        AuthenticationMethod,
        AuthenticationResult,
        AuthenticationStatus,
        EnterpriseAuthenticationModule,
        EnterpriseUser,
        LDAPConfiguration,
        OAuthConfiguration,
        SAMLConfiguration,
        UserRole,
    )

    ENTERPRISE_AUTH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enterprise authentication components not available: {e}")

    # Create fallback classes
    class AuthenticationMethod:
        pass

    class UserRole:
        pass

    class AuthenticationStatus:
        pass

    class EnterpriseUser:
        pass

    class AuthenticationResult:
        pass

    class SAMLConfiguration:
        pass

    class OAuthConfiguration:
        pass

    class LDAPConfiguration:
        pass

    class EnterpriseAuthenticationModule:
        def __init__(self):
            self.initialized = False

    ENTERPRISE_AUTH_AVAILABLE = False

# Agent 1 Task 8: Add attention monitor imports
try:
    from lukhas.governance.identity.auth_utils.attention_monitor import (
        AttentionMetrics,
        AttentionMonitor,
        AttentionState,
        EyeTrackingData,
        InputEvent,
        InputModality,
    )

    ATTENTION_MONITOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Attention monitor not available: {e}")

    # Create fallback classes
    class AttentionMonitor:
        def __init__(self, config=None):
            self.initialized = False

        async def start_attention_monitoring(self):
            return False

    class AttentionState:
        pass

    class AttentionMetrics:
        pass

    class InputModality:
        pass

    class EyeTrackingData:
        pass

    class InputEvent:
        pass

    ATTENTION_MONITOR_AVAILABLE = False

# Agent 1 Task 9: Add grid size calculator imports
try:
    from lukhas.governance.identity.auth_utils.grid_size_calculator import (
        GridCalculationResult,
        GridConstraints,
        GridPattern,
        GridSizeCalculator,
        ScreenDimensions,
        SizingMode,
    )

    GRID_SIZE_CALCULATOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Grid size calculator not available: {e}")

    # Create fallback classes
    class GridPattern:
        pass

    class SizingMode:
        pass

    class ScreenDimensions:
        pass

    class GridConstraints:
        pass

    class GridCalculationResult:
        pass

    class GridSizeCalculator:
        def __init__(self, config=None):
            self.initialized = False

        def calculate_optimal_grid_size(
            self,
            content_count,
            cognitive_load_level="moderate",
            screen_dimensions=None,
            accessibility_requirements=None,
        ):
            return None

    GRID_SIZE_CALCULATOR_AVAILABLE = False

# Agent 1 Task 12: Add persona engine imports
try:
    from candidate.core.identity.persona_engine import (
        PersonaEngine,
        create_and_initialize_identity_component,
        create_identity_component,
    )

    PERSONA_ENGINE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Persona engine not available: {e}")

    # Create fallback class
    class PersonaEngine:
        def __init__(self, config=None):
            self.initialized = False
            self.status = "inactive"

        async def initialize(self):
            return False

        async def process(self, data):
            return {"status": "error", "error": "Persona engine not available"}

        def get_status(self):
            return {"status": "unavailable"}

        async def shutdown(self):
            pass

    def create_identity_component(config=None):
        return PersonaEngine(config)

    async def create_and_initialize_identity_component(config=None):
        return PersonaEngine(config)

    PERSONA_ENGINE_AVAILABLE = False

# Task 3B: Add connectivity imports
try:
    from candidate.core.core_hub import get_core_hub
except ImportError:
    get_core_hub = None
    logging.warning("CoreHub not available")

try:
    from consciousness.reflection.memory_hub import MemoryHub
except ImportError:
    MemoryHub = None
    logging.warning("MemoryHub not available")

try:
    from ethics.service import EthicsService
except ImportError:
    EthicsService = None
    logging.warning("EthicsService not available")

# QRG Coverage Integration
try:
    from identity.qrg_coverage_integration import (
        create_qrg_coverage_integration,
    )

    QRG_COVERAGE_AVAILABLE = True
except ImportError as e:
    QRG_COVERAGE_AVAILABLE = False
    logging.warning(f"QRG coverage integration not available: {e}")

# Brain Identity Integration
try:
    from lukhas.governance.identity.core.brain_identity_integration import (
        create_brain_identity_integration,
    )

    BRAIN_IDENTITY_AVAILABLE = True
except ImportError as e:
    BRAIN_IDENTITY_AVAILABLE = False
    logging.warning(f"Brain identity integration not available: {e}")
# from identity.qrg_test_suite import TestQRGCore
# from identity.qrg_test_suite import TestQRGPerformance
# from identity.qrg_test_suite import TestQRGSecurity
# from identity.qrg_test_suite import TestQRGCompliance
# from identity.qrg_integration import QRGType

logger = get_logger(__name__)


class IdentityHub:
    """
    Central coordination hub for the identity system.

    Manages all identity components and provides service discovery,
    coordination, and communication with other systems.
    """

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list] = {}
        self.is_initialized = False

        # Initialize components
        self.testqrg = TestQRGCore()
        self.register_service("testqrg", self.testqrg)
        self.ultimatetestorchestrator = UltimateTestOrchestrator()
        self.register_service("ultimatetestorchestrator", self.ultimatetestorchestrator)
        self.consentmanager = ConsentManager()
        self.register_service("consentmanager", self.consentmanager)
        self.demoorchestrator = DemoOrchestrator()
        self.register_service("demoorchestrator", self.demoorchestrator)
        self.testorchestrator = TestOrchestrator()
        self.register_service("testorchestrator", self.testorchestrator)
        self.lukhastrustsr = LukhasTrustScorer()
        self.register_service("lukhastrustsr", self.lukhastrustsr)
        self.qrsmanager = QRSManager()
        self.register_service("qrsmanager", self.qrsmanager)
        self.tierawareswarm = TierAwareSwarmHub()
        self.register_service("tierawareswarm", self.tierawareswarm)
        self.biometricintegrationmanager = BiometricIntegrationManager()
        self.register_service("biometricintegrationmanager", self.biometricintegrationmanager)
        self.lambdaconsentmanager = LambdaConsentManager()
        self.register_service("lambdaconsentmanager", self.lambdaconsentmanager)
        self.core_bridge = IdentityCoreBridge()
        self.register_service("core_bridge", self.core_bridge)

        # Agent 1 Task 3: Initialize enterprise authentication
        try:
            self.enterprise_auth = EnterpriseAuthenticationModule()
            self.register_service("enterprise_auth", self.enterprise_auth)
            logger.info("Enterprise authentication module registered")
        except Exception as e:
            logger.warning(f"Enterprise auth initialization failed: {e}")

        # Initialize QRG coverage integration
        if QRG_COVERAGE_AVAILABLE:
            try:
                self.qrg_coverage = create_qrg_coverage_integration()
                if self.qrg_coverage:
                    self.register_service("qrg_coverage", self.qrg_coverage)
                    logger.info("QRG coverage integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize QRG coverage integration: {e}")

        # Initialize Brain Identity integration
        if BRAIN_IDENTITY_AVAILABLE:
            try:
                self.brain_identity = create_brain_identity_integration()
                if self.brain_identity:
                    self.register_service("brain_identity", self.brain_identity)
                    logger.info("Brain identity integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize brain identity integration: {e}")

        # Agent 1 Task 8: Initialize attention monitor
        if ATTENTION_MONITOR_AVAILABLE:
            try:
                self.attention_monitor = AttentionMonitor()
                self.register_service("attention_monitor", self.attention_monitor)
                logger.info("Attention monitor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize attention monitor: {e}")

        # Agent 1 Task 9: Initialize grid size calculator
        if GRID_SIZE_CALCULATOR_AVAILABLE:
            try:
                self.grid_size_calculator = GridSizeCalculator()
                self.register_service("grid_size_calculator", self.grid_size_calculator)
                logger.info("Grid size calculator initialized")
            except Exception as e:
                logger.error(f"Failed to initialize grid size calculator: {e}")

        # Agent 1 Task 12: Initialize persona engine
        if PERSONA_ENGINE_AVAILABLE:
            try:
                self.persona_engine = PersonaEngine()
                self.register_service("persona_engine", self.persona_engine)
                logger.info("Persona engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize persona engine: {e}")

        logger.info(f"IdentityHub initialized with {len(self.services)} services")

    async def initialize(self) -> None:
        """Initialize all identity services"""
        if self.is_initialized:
            return

        # Initialize all registered services
        for name, service in self.services.items():
            if hasattr(service, "initialize"):
                try:
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                    logger.debug(f"Initialized {name} service")
                except Exception as e:
                    logger.error(f"Failed to initialize {name}: {e}")

        # Task 3B: Establish connections to other systems
        await self.establish_connections()

        self.is_initialized = True
        logger.info("IdentityHub fully initialized")

    # Agent 1 Task 3: Add enterprise authentication methods to IdentityHub
    async def authenticate_user(
        self,
        username: str,
        password: str,
        method: str = "ldap",
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Authenticate user using enterprise authentication module"""
        if "enterprise_auth" not in self.services:
            logger.error("Enterprise authentication not available")
            return {
                "status": "failed",
                "error": "Enterprise authentication not configured",
            }

        try:
            auth_method = getattr(AuthenticationMethod, method.upper(), None)
            if not auth_method:
                auth_method = AuthenticationMethod.LDAP

            result = await self.services["enterprise_auth"].authenticate_user(
                username, password, auth_method, session_id or "default"
            )

            return {
                "status": (result.status.value if hasattr(result, "status") else "success"),
                "user": (asdict(result.user) if hasattr(result, "user") and result.user else None),
                "access_token": getattr(result, "access_token", None),
                "session_id": getattr(result, "session_id", session_id),
                "permissions": getattr(result, "permissions", []),
                "lambda_id": getattr(result, "lambda_id", None),
            }
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def validate_token(self, token: str) -> dict[str, Any]:
        """Validate authentication token"""
        if "enterprise_auth" not in self.services:
            return {"valid": False, "error": "Enterprise auth not available"}

        try:
            is_valid = await self.services["enterprise_auth"].validate_token(token)
            return {"valid": is_valid}
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": str(e)}

    async def get_user_roles(self, user_id: str) -> list[str]:
        """Get user roles from enterprise authentication"""
        if "enterprise_auth" not in self.services:
            return []

        try:
            roles = await self.services["enterprise_auth"].get_user_roles(user_id)
            return [role.value if hasattr(role, "value") else str(role) for role in roles]
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []

    # Agent 1 Task 3: Additional enterprise authentication methods
    def get_enterprise_auth_config_template(self) -> dict[str, Any]:
        """Get enterprise authentication configuration template"""
        try:
            from identity.enterprise.auth import (
                get_enterprise_auth_config_template,
            )

            return get_enterprise_auth_config_template()
        except Exception as e:
            logger.error(f"Failed to get config template: {e}")
            return {}

    async def configure_enterprise_authentication(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure enterprise authentication with new settings"""
        if "enterprise_auth" not in self.services:
            return {"status": "failed", "error": "Enterprise auth not available"}

        try:
            # Reinitialize with new configuration
            from identity.enterprise.auth import EnterpriseAuthenticationModule

            # Create temporary config file or pass config directly
            self.enterprise_auth = EnterpriseAuthenticationModule()
            self.enterprise_auth.config.update(config)
            self.enterprise_auth._load_authentication_providers()

            # Update service registration
            self.register_service("enterprise_auth", self.enterprise_auth)

            return {"status": "success", "message": "Configuration updated"}
        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def get_authentication_methods(self) -> list[str]:
        """Get available authentication methods"""
        if "enterprise_auth" not in self.services:
            return []

        try:
            # Get configured authentication methods
            config = self.services["enterprise_auth"].config
            return config.get("authentication_methods", [])
        except Exception as e:
            logger.error(f"Failed to get auth methods: {e}")
            return []

    async def get_enterprise_auth_status(self) -> dict[str, Any]:
        """Get enterprise authentication system status"""
        if "enterprise_auth" not in self.services:
            return {"status": "unavailable", "providers": []}

        try:
            auth_service = self.services["enterprise_auth"]
            providers = []

            if hasattr(auth_service, "saml_config") and auth_service.saml_config:
                providers.append("saml")
            if hasattr(auth_service, "oauth_config") and auth_service.oauth_config:
                providers.append("oauth")
            if hasattr(auth_service, "ldap_config") and auth_service.ldap_config:
                providers.append("ldap")

            return {
                "status": "active",
                "providers": providers,
                "mfa_enabled": getattr(auth_service, "mfa_enabled", False),
                "session_count": len(getattr(auth_service, "active_sessions", {})),
                "user_cache_size": len(getattr(auth_service, "user_cache", {})),
            }
        except Exception as e:
            logger.error(f"Failed to get auth status: {e}")
            return {"status": "error", "error": str(e)}

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered {name} service in identityHub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service by name"""
        return self.services.get(name)

    def list_services(self) -> list[str]:
        """List all registered service names"""
        return list(self.services.keys())

    async def process_event(self, event_type: str, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process events from other systems"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_data)
                else:
                    result = handler(event_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Event handler error in identity: {e}")

        return {"results": results, "handled": len(handlers) > 0}

    def register_event_handler(self, event_type: str, handler) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    # QRG Coverage Integration Methods
    async def run_comprehensive_qrg_tests(
        self,
        test_categories: Optional[list[str]] = None,
        custom_config: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Run comprehensive QRG coverage tests"""
        if "qrg_coverage" not in self.services:
            logger.error("QRG coverage integration not available")
            return {"status": "failed", "error": "QRG coverage not configured"}

        try:
            coverage_report = await self.services["qrg_coverage"].run_comprehensive_coverage_tests(
                test_categories, custom_config
            )

            return {
                "status": "completed",
                "coverage_percentage": coverage_report.coverage_percentage,
                "total_tests": coverage_report.total_tests,
                "passed_tests": coverage_report.passed_tests,
                "failed_tests": coverage_report.failed_tests,
                "runtime_seconds": coverage_report.runtime_seconds,
                "areas_covered": coverage_report.areas_covered,
                "timestamp": coverage_report.timestamp.isoformat(),
            }
        except Exception as e:
            logger.error(f"QRG coverage tests failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def validate_qrg_system_readiness(self) -> dict[str, Any]:
        """Validate QRG system readiness for production"""
        if "qrg_coverage" not in self.services:
            return {
                "ready_for_production": False,
                "error": "QRG coverage not available",
            }

        try:
            readiness_result = await self.services["qrg_coverage"].validate_system_readiness()
            return readiness_result
        except Exception as e:
            logger.error(f"QRG readiness validation failed: {e}")
            return {"ready_for_production": False, "error": str(e)}

    async def get_qrg_coverage_statistics(self) -> dict[str, Any]:
        """Get QRG coverage test statistics"""
        if "qrg_coverage" not in self.services:
            return {"available": False, "error": "QRG coverage not configured"}

        try:
            stats = await self.services["qrg_coverage"].get_coverage_statistics()
            return {"available": True, "statistics": stats}
        except Exception as e:
            logger.error(f"Failed to get QRG statistics: {e}")
            return {"available": False, "error": str(e)}

    async def run_targeted_qrg_tests(
        self, test_category: str, specific_tests: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Run targeted QRG tests for specific category"""
        if "qrg_coverage" not in self.services:
            return {"status": "failed", "error": "QRG coverage not available"}

        try:
            result = await self.services["qrg_coverage"].run_targeted_tests(test_category, specific_tests)
            return result
        except Exception as e:
            logger.error(f"Targeted QRG tests failed: {e}")
            return {"status": "failed", "error": str(e)}

    # Brain Identity Integration Methods
    async def authorize_memory_operation(
        self,
        user_id: str,
        operation: str,
        memory_key: str,
        memory_type: Optional[str] = None,
        memory_owner: Optional[str] = None,
        access_policy: Optional[str] = None,
    ) -> dict[str, Any]:
        """Authorize a memory operation through brain identity integration"""
        if "brain_identity" not in self.services:
            logger.error("Brain identity integration not available")
            return {
                "authorized": False,
                "error": "Brain identity integration not configured",
            }

        try:
            result = await self.services["brain_identity"].authorize_memory_operation(
                user_id, operation, memory_key, memory_type, memory_owner, access_policy
            )
            return result
        except Exception as e:
            logger.error(f"Memory operation authorization failed: {e}")
            return {"authorized": False, "error": str(e)}

    async def register_memory_with_identity(
        self,
        memory_key: str,
        memory_owner: str,
        memory_type: str,
        access_policy: str = "tier_based",
        min_tier: int = 1,
    ) -> dict[str, Any]:
        """Register a memory with the identity system"""
        if "brain_identity" not in self.services:
            return {
                "success": False,
                "error": "Brain identity integration not available",
            }

        try:
            result = await self.services["brain_identity"].register_memory(
                memory_key, memory_owner, memory_type, access_policy, min_tier
            )
            return result
        except Exception as e:
            logger.error(f"Memory registration failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_brain_identity_access_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get brain identity access logs"""
        if "brain_identity" not in self.services:
            return []

        try:
            logs = await self.services["brain_identity"].get_access_logs(limit)
            return logs
        except Exception as e:
            logger.error(f"Failed to get brain identity access logs: {e}")
            return []

    async def get_brain_identity_metrics(self) -> dict[str, Any]:
        """Get brain identity access metrics"""
        if "brain_identity" not in self.services:
            return {
                "available": False,
                "error": "Brain identity integration not configured",
            }

        try:
            metrics = await self.services["brain_identity"].get_access_metrics()
            return {"available": True, "metrics": metrics}
        except Exception as e:
            logger.error(f"Failed to get brain identity metrics: {e}")
            return {"available": False, "error": str(e)}

    async def encrypt_memory_content(self, memory_key: str, content: dict[str, Any]) -> dict[str, Any]:
        """Encrypt memory content through brain identity integration"""
        if "brain_identity" not in self.services:
            return content  # Return original content if service not available

        try:
            encrypted_content = await self.services["brain_identity"].encrypt_memory_content(memory_key, content)
            return encrypted_content
        except Exception as e:
            logger.error(f"Memory content encryption failed: {e}")
            return content  # Return original content on error

    async def decrypt_memory_content(self, memory_key: str, content: dict[str, Any]) -> dict[str, Any]:
        """Decrypt memory content through brain identity integration"""
        if "brain_identity" not in self.services:
            return content  # Return original content if service not available

        try:
            decrypted_content = await self.services["brain_identity"].decrypt_memory_content(memory_key, content)
            return decrypted_content
        except Exception as e:
            logger.error(f"Memory content decryption failed: {e}")
            return content  # Return original content on error

    async def establish_connections(self) -> None:
        """Connect identity module to system components"""
        logger.info("Establishing identity module connections...")

        # Core connection for supervision
        if get_core_hub is not None:
            try:
                self.core_hub = get_core_hub()
                await self.core_hub.register_service("identity", self)
                self.register_service("core_hub", self.core_hub)
                logger.info("Successfully connected to CoreHub")
            except Exception as e:
                logger.error(f"Failed to connect to CoreHub: {e}")
        else:
            logger.warning("CoreHub not available - skipping connection")

        # Memory connection for identity storage
        if MemoryHub is not None:
            try:
                self.memory_hub = MemoryHub()
                await self.memory_hub.register_client(
                    "identity",
                    {
                        "data_types": ["biometric", "consciousness", "dream_patterns"],
                        "retention_policy": "permanent",
                        "encryption": "qi_resistant",
                    },
                )
                self.register_service("memory_hub", self.memory_hub)
                logger.info("Successfully connected to MemoryHub")
            except Exception as e:
                logger.error(f"Failed to connect to MemoryHub: {e}")
        else:
            logger.warning("MemoryHub not available - skipping connection")

        # Ethics connection for privacy compliance
        if EthicsService is not None:
            try:
                self.ethics_service = EthicsService()
                await self.ethics_service.register_privacy_handler("identity", self)
                self.register_service("ethics_service", self.ethics_service)
                logger.info("Successfully connected to EthicsService")
            except Exception as e:
                logger.error(f"Failed to connect to EthicsService: {e}")
        else:
            logger.warning("EthicsService not available - skipping connection")

        logger.info("Identity module connections established")

    # Agent 1 Task 8: Attention monitor interface methods
    async def start_attention_monitoring(self, config: Optional[dict[str, Any]] = None) -> bool:
        """Start attention monitoring for user engagement tracking"""
        if not ATTENTION_MONITOR_AVAILABLE:
            logging.warning("Attention monitor not available")
            return False

        try:
            monitor = self.get_service("attention_monitor")
            if monitor:
                if config:
                    monitor.config.update(config)
                return await monitor.start_attention_monitoring()
            else:
                logging.error("Attention monitor service not found")
                return False
        except Exception as e:
            logging.error(f"Failed to start attention monitoring: {e}")
            return False

    async def get_current_attention_state(self) -> dict[str, Any]:
        """Get current user attention state and metrics"""
        if not ATTENTION_MONITOR_AVAILABLE:
            logging.warning("Attention monitor not available")
            return {"state": "unknown", "metrics": {}}

        try:
            monitor = self.get_service("attention_monitor")
            if monitor:
                state, metrics = await monitor.get_current_attention_state()
                return {
                    "state": state.value if hasattr(state, "value") else str(state),
                    "metrics": asdict(metrics) if hasattr(metrics, "__dict__") else {},
                }
            else:
                logging.error("Attention monitor service not found")
                return {"state": "unknown", "metrics": {}}
        except Exception as e:
            logging.error(f"Failed to get attention state: {e}")
            return {"state": "error", "metrics": {}, "error": str(e)}

    async def process_input_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Process input event for attention analysis"""
        if not ATTENTION_MONITOR_AVAILABLE:
            logging.warning("Attention monitor not available")
            return {}

        try:
            monitor = self.get_service("attention_monitor")
            if monitor:
                # Convert dict to InputEvent if needed
                from lukhas.governance.identity.auth_utils.attention_monitor import (
                    InputEvent,
                    InputModality,
                )

                input_event = InputEvent(
                    timestamp=event_data.get("timestamp", time.time()),
                    event_type=InputModality(event_data.get("type", "mouse")),
                    coordinates=(event_data.get("x", 0), event_data.get("y", 0)),
                    processing_time=event_data.get("processing_time", 0),
                    response_time=event_data.get("response_time", 0),
                )
                return await monitor.process_input_event(input_event)
            else:
                logging.error("Attention monitor service not found")
                return {}
        except Exception as e:
            logging.error(f"Failed to process input event: {e}")
            return {"error": str(e)}

    async def get_attention_status(self) -> dict[str, Any]:
        """Get comprehensive attention monitoring status"""
        if not ATTENTION_MONITOR_AVAILABLE:
            logging.warning("Attention monitor not available")
            return {"available": False}

        try:
            monitor = self.get_service("attention_monitor")
            if monitor:
                return await monitor.get_attention_status()
            else:
                logging.error("Attention monitor service not found")
                return {"available": False, "error": "Service not found"}
        except Exception as e:
            logging.error(f"Failed to get attention status: {e}")
            return {"available": False, "error": str(e)}

    # Agent 1 Task 9: Grid size calculator interface methods
    async def calculate_optimal_grid_size(
        self,
        content_count: int,
        cognitive_load_level: str = "moderate",
        screen_dimensions: Optional[dict[str, Any]] = None,
        accessibility_requirements: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Calculate optimal grid size for authentication interface"""
        if not GRID_SIZE_CALCULATOR_AVAILABLE:
            logging.warning("Grid size calculator not available")
            return {"success": False, "error": "Grid size calculator not configured"}

        try:
            calculator = self.get_service("grid_size_calculator")
            if calculator:
                # Convert screen dimensions dict to ScreenDimensions if provided
                screen_dims = None
                if screen_dimensions and GRID_SIZE_CALCULATOR_AVAILABLE:
                    try:
                        screen_dims = ScreenDimensions(
                            width=screen_dimensions.get("width", 390),
                            height=screen_dimensions.get("height", 844),
                            pixel_density=screen_dimensions.get("pixel_density", 3.0),
                            safe_area_insets=screen_dimensions.get(
                                "safe_area_insets",
                                {"top": 44, "bottom": 34, "left": 0, "right": 0},
                            ),
                            orientation=screen_dimensions.get("orientation", "portrait"),
                        )
                    except Exception:
                        # Use None if ScreenDimensions construction fails
                        screen_dims = None

                result = calculator.calculate_optimal_grid_size(
                    content_count,
                    cognitive_load_level,
                    screen_dims,
                    accessibility_requirements,
                )

                if result:
                    return {
                        "success": True,
                        "grid_size": result.grid_size,
                        "pattern": (result.pattern.value if hasattr(result.pattern, "value") else str(result.pattern)),
                        "cell_size": result.cell_size,
                        "spacing": result.spacing,
                        "total_width": result.total_width,
                        "total_height": result.total_height,
                        "cells_per_row": result.cells_per_row,
                        "cells_per_column": result.cells_per_column,
                        "reasoning": result.reasoning,
                        "confidence": result.confidence,
                    }
                else:
                    return {"success": False, "error": "Calculation failed"}
            else:
                logging.error("Grid size calculator service not found")
                return {"success": False, "error": "Service not found"}
        except Exception as e:
            logging.error(f"Failed to calculate optimal grid size: {e}")
            return {"success": False, "error": str(e)}

    async def get_grid_calculator_status(self) -> dict[str, Any]:
        """Get grid size calculator status"""
        if not GRID_SIZE_CALCULATOR_AVAILABLE:
            return {"available": False, "error": "Grid size calculator not configured"}

        try:
            calculator = self.get_service("grid_size_calculator")
            if calculator:
                return {
                    "available": True,
                    "initialized": getattr(calculator, "initialized", True),
                    "constraints": {
                        "min_grid_size": getattr(calculator.constraints, "min_grid_size", 4),
                        "max_grid_size": getattr(calculator.constraints, "max_grid_size", 16),
                        "min_cell_size": getattr(calculator.constraints, "min_cell_size", 40.0),
                        "max_cell_size": getattr(calculator.constraints, "max_cell_size", 120.0),
                    },
                    "supported_patterns": [
                        "square",
                        "rectangle",
                        "circular",
                        "adaptive",
                        "accessibility",
                    ],
                    "supported_modes": [
                        "cognitive_load",
                        "device_size",
                        "accessibility",
                        "performance",
                        "balanced",
                    ],
                }
            else:
                return {"available": False, "error": "Service not found"}
        except Exception as e:
            logging.error(f"Failed to get grid calculator status: {e}")
            return {"available": False, "error": str(e)}

    # Agent 1 Task 12: Persona engine interface methods
    async def process_identity_data(self, data: Any, category: Optional[str] = None) -> dict[str, Any]:
        """Process identity data through the persona engine"""
        if not PERSONA_ENGINE_AVAILABLE:
            return {"status": "error", "error": "Persona engine not available"}

        try:
            persona_engine = self.get_service("persona_engine")
            if persona_engine:
                # Add category to data if provided
                if category and isinstance(data, dict):
                    data["category"] = category

                result = await persona_engine.process(data)
                return result
            else:
                return {"status": "error", "error": "Persona engine service not found"}
        except Exception as e:
            logging.error(f"Failed to process identity data: {e}")
            return {"status": "error", "error": str(e)}

    async def create_identity_component(self, config: Optional[dict] = None) -> dict[str, Any]:
        """Create a new identity component instance"""
        if not PERSONA_ENGINE_AVAILABLE:
            return {"status": "error", "error": "Persona engine not available"}

        try:
            component = create_identity_component(config)
            return {
                "status": "success",
                "component_id": id(component),
                "component_type": "PersonaEngine",
                "config": config or {},
            }
        except Exception as e:
            logging.error(f"Failed to create identity component: {e}")
            return {"status": "error", "error": str(e)}

    async def create_and_initialize_identity_component(self, config: Optional[dict] = None) -> dict[str, Any]:
        """Create and initialize a new identity component instance"""
        if not PERSONA_ENGINE_AVAILABLE:
            return {"status": "error", "error": "Persona engine not available"}

        try:
            component = await create_and_initialize_identity_component(config)
            return {
                "status": "success",
                "component_id": id(component),
                "component_type": "PersonaEngine",
                "initialized": component.is_initialized,
                "config": config or {},
            }
        except Exception as e:
            logging.error("Failed to create and initialize identity component: " + str(e))
            return {"status": "error", "error": str(e)}

    async def validate_persona_engine(self) -> dict[str, Any]:
        """Validate persona engine health and connectivity"""
        if not PERSONA_ENGINE_AVAILABLE:
            return {"available": False, "error": "Persona engine not configured"}

        try:
            persona_engine = self.get_service("persona_engine")
            if persona_engine:
                is_valid = await persona_engine.validate()
                status = persona_engine.get_status()
                return {
                    "available": True,
                    "valid": is_valid,
                    "status": status,
                    "initialized": persona_engine.is_initialized,
                }
            else:
                return {"available": False, "error": "Service not found"}
        except Exception as e:
            logging.error(f"Failed to validate persona engine: {e}")
            return {"available": False, "error": str(e)}

    def get_persona_engine_status(self) -> dict[str, Any]:
        """Get persona engine status and configuration"""
        if not PERSONA_ENGINE_AVAILABLE:
            return {"available": False, "error": "Persona engine not configured"}

        try:
            persona_engine = self.get_service("persona_engine")
            if persona_engine:
                return {
                    "available": True,
                    "status": persona_engine.get_status(),
                    "initialized": persona_engine.is_initialized,
                    "supported_categories": [
                        "consciousness",
                        "governance",
                        "voice",
                        "identity",
                        "quantum",
                        "generic",
                    ],
                    "component_type": "PersonaEngine",
                }
            else:
                return {"available": False, "error": "Service not found"}
        except Exception as e:
            logging.error(f"Failed to get persona engine status: {e}")
            return {"available": False, "error": str(e)}

    async def shutdown(self) -> None:
        """Gracefully shutdown all services"""
        for name, service in self.services.items():
            if hasattr(service, "shutdown"):
                try:
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await service.shutdown()
                    else:
                        service.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {name}: {e}")

        logger.info("IdentityHub shutdown complete")


# Singleton instance
_identity_hub_instance = None


def get_identity_hub() -> IdentityHub:
    """Get or create the identity hub singleton instance"""
    global _identity_hub_instance
    if _identity_hub_instance is None:
        _identity_hub_instance = IdentityHub()
    return _identity_hub_instance


async def initialize_identity_system() -> IdentityHub:
    """Initialize the complete identity system"""
    hub = get_identity_hub()
    await hub.initialize()
    return hub


# Export main components
__all__ = ["IdentityHub", "get_identity_hub", "initialize_identity_system"]
