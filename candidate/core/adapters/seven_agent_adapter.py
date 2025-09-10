"""
Seven Agent Architecture Integration Adapter
Bridges the new 7-agent modules with the existing LUKHAS system
Trinity Framework: ⚛️🧠🛡️
"""
import logging
from typing import Any, Optional

from lukhas.core.container.service_container import ServiceLifetime, injectable
from lukhas.core.interfaces.services import (
    IBridgeService,
    IGovernanceService,
    IIdentityService,
)

try:
    from lukhas.core.telemetry import AgentSpans, instrument
except ImportError:
    # Fallback if telemetry not available
    class AgentSpans:
        @staticmethod
        def lid_issue(*args, **kwargs):
            from contextlib import nullcontext

            return nullcontext()

        @staticmethod
        def lid_verify(*args, **kwargs):
            from contextlib import nullcontext

            return nullcontext()

        @staticmethod
        def consent_record(*args, **kwargs):
            from contextlib import nullcontext

            return nullcontext()

        @staticmethod
        def consent_check(*args, **kwargs):
            from contextlib import nullcontext

            return nullcontext()

        @staticmethod
        def adapter_metadata(*args, **kwargs):
            from contextlib import nullcontext

            return nullcontext()

    def instrument(func):
        return func


logger = logging.getLogger(__name__)


@injectable(ServiceLifetime.SINGLETON)
class LambdaIdentityServiceAdapter(IIdentityService):
    """Adapts the new ΛID Core Identity System to IIdentityService interface"""

    def __init__(self):
        self._identity_module = None
        self._initialized = False

    async def initialize(self) -> None:
        """Lazy load ΛID identity module"""
        if not self._initialized:
            try:
                from candidate.core.identity.lambda_id_core import (
                    IdentityNamespace,
                    LukhasIdentityService,
                    OIDCProvider,
                    WebAuthnManager,
                )

                self._identity_service = LukhasIdentityService()
                self._oidc_provider = OIDCProvider()
                self._webauthn = WebAuthnManager()

                self._initialized = True
                logger.info("ΛID Identity service adapter initialized - ⚛️")
            except ImportError as e:
                logger.error(f"Failed to import ΛID modules: {e}")
                self._initialized = False

    @instrument
    async def authenticate(self, credentials: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Authenticate using ΛID system with <100ms target"""
        await self.initialize()
        if not self._identity_service:
            return None

        try:
            with AgentSpans.lid_issue(
                user_id=credentials.get("user_id", "unknown"),
                namespace=credentials.get("namespace", "default"),
            ):
                # Use the ΛID authentication
                result = self._identity_service.authenticate_namespace(
                    namespace=credentials.get("namespace", "default"),
                    token=credentials.get("token"),
                )
                return result
        except Exception as e:
            logger.error(f"ΛID authentication failed: {e}")
            return None

    async def verify_identity(self, token: str) -> bool:
        """Verify identity token"""
        await self.initialize()
        if not self._identity_service:
            return False

        try:
            with AgentSpans.lid_verify(token=token):
                return self._identity_service.validate_token(token)
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return False

    async def create_identity(self, user_data: dict[str, Any]) -> str:
        """Create new identity"""
        await self.initialize()
        if not self._identity_service:
            return ""

        try:
            namespace = self._identity_service.create_namespace(
                name=user_data.get("username", "user"), metadata=user_data
            )
            return namespace.namespace_id
        except Exception as e:
            logger.error(f"Failed to create identity: {e}")
            return ""

    async def get_identity(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get identity information"""
        await self.initialize()
        if not self._identity_service:
            return None

        try:
            return self._identity_service.get_namespace(user_id)
        except Exception as e:
            logger.error(f"Failed to get identity: {e}")
            return None

    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""
        self._initialized = False
        self._identity_service = None

    def get_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "LambdaIdentityService",
            "initialized": self._initialized,
            "status": "healthy" if self._initialized else "not_initialized",
        }


@injectable(ServiceLifetime.SINGLETON)
class ConsentLedgerServiceAdapter(IGovernanceService):
    """Adapts the Consent Ledger v1 to IGovernanceService interface"""

    def __init__(self):
        self._consent_ledger = None
        self._initialized = False

    async def initialize(self) -> None:
        """Lazy load consent ledger module"""
        if not self._initialized:
            try:
                from lukhas.governance.consent_ledger.ledger_v1 import (
                    ConsentLedgerV1,
                    ConsentRecord,
                    PolicyEngine,
                )

                self._consent_ledger = ConsentLedgerV1()
                self._policy_engine = PolicyEngine()

                self._initialized = True
                logger.info("Consent Ledger v1 adapter initialized - 🛡️")
            except ImportError as e:
                logger.error(f"Failed to import Consent Ledger: {e}")
                self._initialized = False

    @instrument
    async def check_consent(self, user_id: str, action: str) -> bool:
        """Check if user has consented to action"""
        await self.initialize()
        if not self._consent_ledger:
            return False

        try:
            with AgentSpans.consent_check(user_id=user_id, purpose=action):
                return self._consent_ledger.has_valid_consent(subject_id=user_id, purpose=action)
        except Exception as e:
            logger.error(f"Consent check failed: {e}")
            return False

    async def record_consent(self, user_id: str, action: str, granted: bool) -> bool:
        """Record consent decision"""
        await self.initialize()
        if not self._consent_ledger:
            return False

        try:
            with AgentSpans.consent_record(user_id=user_id, purpose=action, granted=granted):
                self._consent_ledger.record_consent(subject_id=user_id, purpose=action, granted=granted)
                return True
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            return False

    async def check_ethics(self, action: str, context: dict[str, Any]) -> bool:
        """Check if action is ethically allowed"""
        await self.initialize()
        if not self._policy_engine:
            return False

        try:
            return self._policy_engine.evaluate_policy(action, context)
        except Exception as e:
            logger.error(f"Ethics check failed: {e}")
            return False

    async def report_violation(self, violation: dict[str, Any]) -> None:
        """Report ethics violation"""
        await self.initialize()
        if self._consent_ledger:
            try:
                self._consent_ledger.log_violation(violation)
            except Exception as e:
                logger.error(f"Failed to report violation: {e}")

    async def get_governance_state(self) -> dict[str, Any]:
        """Get current governance state"""
        await self.initialize()
        if not self._consent_ledger:
            return {"status": "not_initialized"}

        try:
            return {
                "status": "active",
                "consent_records": self._consent_ledger.get_summary(),
                "policy_active": bool(self._policy_engine),
            }
        except Exception as e:
            logger.error(f"Failed to get governance state: {e}")
            return {"status": "error", "error": str(e)}

    async def evaluate_risk(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Evaluate risk of scenario"""
        await self.initialize()
        if not self._policy_engine:
            return {"risk_level": "unknown", "score": 0.5}

        try:
            # Use policy engine to evaluate risk
            risk_score = (
                self._policy_engine.calculate_risk(scenario) if hasattr(self._policy_engine, "calculate_risk") else 0.5
            )
            return {
                "risk_level": ("high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low"),
                "score": risk_score,
                "factors": scenario.get("factors", []),
            }
        except Exception as e:
            logger.error(f"Risk evaluation failed: {e}")
            return {"risk_level": "error", "score": 1.0, "error": str(e)}

    async def apply_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        """Apply governance policy"""
        await self.initialize()
        if not self._policy_engine:
            return {"approved": False, "reason": "Policy engine not initialized"}

        try:
            result = (
                self._policy_engine.apply_policy(request)
                if hasattr(self._policy_engine, "apply_policy")
                else {"approved": False}
            )
            return result
        except Exception as e:
            logger.error(f"Policy application failed: {e}")
            return {"approved": False, "reason": str(e)}

    async def audit_action(self, action: dict[str, Any]) -> None:
        """Audit an action for compliance"""
        await self.initialize()
        if self._consent_ledger:
            try:
                # Record action in audit trail
                (
                    self._consent_ledger.add_audit_entry(action)
                    if hasattr(self._consent_ledger, "add_audit_entry")
                    else None
                )
            except Exception as e:
                logger.error(f"Audit recording failed: {e}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""
        self._initialized = False
        self._consent_ledger = None
        self._policy_engine = None

    def get_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ConsentLedgerV1",
            "initialized": self._initialized,
            "status": "healthy" if self._initialized else "not_initialized",
        }


@injectable(ServiceLifetime.SINGLETON)
class ExternalAdaptersServiceAdapter(IBridgeService):
    """Adapts Gmail, Drive, Dropbox adapters to IBridgeService interface"""

    def __init__(self):
        self._adapters = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Lazy load external adapters"""
        if not self._initialized:
            try:
                from candidate.bridge.adapters.drive_adapter import GoogleDriveAdapter
                from candidate.bridge.adapters.dropbox_adapter import DropboxAdapter
                from candidate.bridge.adapters.gmail_adapter import GmailAdapter

                self._adapters["gmail"] = GmailAdapter()
                self._adapters["drive"] = GoogleDriveAdapter()
                self._adapters["dropbox"] = DropboxAdapter()

                self._initialized = True
                logger.info("External adapters initialized - 🧠")
            except ImportError as e:
                logger.error(f"Failed to import external adapters: {e}")
                self._initialized = False

    async def connect(self, service: str, credentials: dict[str, Any]) -> bool:
        """Connect to external service"""
        await self.initialize()

        adapter = self._adapters.get(service)
        if not adapter:
            logger.error(f"Unknown service: {service}")
            return False

        try:
            return await adapter.connect(credentials)
        except Exception as e:
            logger.error(f"Failed to connect to {service}: {e}")
            return False

    @instrument
    async def fetch_data(self, service: str, query: dict[str, Any]) -> Optional[Any]:
        """Fetch data from external service"""
        await self.initialize()

        adapter = self._adapters.get(service)
        if not adapter:
            return None

        try:
            with AgentSpans.adapter_metadata(service=service, action="fetch"):
                return await adapter.fetch(query)
        except Exception as e:
            logger.error(f"Failed to fetch from {service}: {e}")
            return None

    async def send_data(self, service: str, data: Any) -> bool:
        """Send data to external service"""
        await self.initialize()

        adapter = self._adapters.get(service)
        if not adapter:
            return False

        try:
            return await adapter.send(data)
        except Exception as e:
            logger.error(f"Failed to send to {service}: {e}")
            return False

    async def get_bridge_status(self) -> dict[str, Any]:
        """Get status of all bridges"""
        await self.initialize()

        status = {}
        for name, adapter in self._adapters.items():
            try:
                status[name] = adapter.get_status() if hasattr(adapter, "get_status") else "unknown"
            except Exception as e:
                status[name] = f"error: {e}"

        return status

    async def send_external(self, destination: str, data: Any) -> dict[str, Any]:
        """Send data to external system"""
        # Parse destination format: "service:target" (e.g., "gmail:user@example.com")
        parts = destination.split(":", 1)
        service = parts[0] if parts else destination
        target = parts[1] if len(parts) > 1 else None

        return {"success": await self.send_data(service, {"target": target, "data": data})}

    async def receive_external(self, source: str) -> Optional[Any]:
        """Receive data from external system"""
        # Parse source format: "service:query" (e.g., "gmail:inbox")
        parts = source.split(":", 1)
        service = parts[0] if parts else source
        query = parts[1] if len(parts) > 1 else None

        return await self.fetch_data(service, {"query": query})

    async def translate_protocol(self, data: Any, from_protocol: str, to_protocol: str) -> Any:
        """Translate between protocols"""
        # Basic protocol translation (can be extended)
        if from_protocol == to_protocol:
            return data

        # Example translations
        if from_protocol == "json" and to_protocol == "xml":
            # Would implement JSON to XML conversion
            return f"<data>{data}</data>"
        elif from_protocol == "oauth2" and to_protocol == "api_key":
            # Would implement OAuth to API key translation
            return {"api_key": data.get("access_token")}

        # Default passthrough
        return data

    async def shutdown(self) -> None:
        """Gracefully shutdown the service"""
        for adapter in self._adapters.values():
            if hasattr(adapter, "disconnect"):
                try:
                    await adapter.disconnect()
                except Exception as e:
                    logger.error(f"Failed to disconnect adapter: {e}")

        self._initialized = False
        self._adapters.clear()

    def get_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ExternalAdapters",
            "initialized": self._initialized,
            "adapters": list(self._adapters.keys()),
            "status": "healthy" if self._initialized else "not_initialized",
        }


class ContextBusEnhancedAdapter:
    """Adapts the enhanced context bus for internal messaging"""

    def __init__(self):
        self._context_bus = None
        self._initialized = False

    async def initialize(self) -> None:
        """Lazy load enhanced context bus"""
        if not self._initialized:
            try:
                from candidate.orchestration.context_bus_enhanced import (
                    ContextBusEnhanced,
                    MessageRouter,
                    PipelineManager,
                )

                self._context_bus = ContextBusEnhanced()
                self._router = MessageRouter()
                self._pipeline = PipelineManager()

                self._initialized = True
                logger.info("Enhanced Context Bus initialized")
            except ImportError as e:
                logger.error(f"Failed to import Context Bus: {e}")
                self._initialized = False

    async def publish(self, topic: str, message: Any) -> None:
        """Publish message to context bus"""
        await self.initialize()
        if self._context_bus:
            await self._context_bus.publish(topic, message)

    async def subscribe(self, topic: str, handler: Any) -> None:
        """Subscribe to topic on context bus"""
        await self.initialize()
        if self._context_bus:
            await self._context_bus.subscribe(topic, handler)


def register_seven_agent_services(container=None):
    """Register all 7-agent services with the service container"""
    from candidate.core.container.service_container import get_container

    container = container or get_container()

    # Register identity service
    container.register_singleton(IIdentityService, LambdaIdentityServiceAdapter)

    # Register governance service (consent ledger)
    # Note: IGovernanceService might already be registered, so we check first
    try:
        container.resolve(IGovernanceService)
        logger.info("IGovernanceService already registered, skipping ConsentLedger registration")
    except:
        container.register_singleton(IGovernanceService, ConsentLedgerServiceAdapter)

    # Register bridge service (external adapters)
    # Note: IBridgeService might already be registered, so we check first
    try:
        container.resolve(IBridgeService)
        logger.info("IBridgeService already registered, skipping ExternalAdapters registration")
    except:
        container.register_singleton(IBridgeService, ExternalAdaptersServiceAdapter)

    logger.info("Seven-agent architecture services registered ⚛️🧠🛡️")
    return container


# Auto-register on import
try:
    from candidate.core.container.service_container import get_container

    register_seven_agent_services(get_container())
except ImportError:
    logger.warning("Service container not available, skipping auto-registration")
