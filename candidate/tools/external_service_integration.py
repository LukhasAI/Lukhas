"""
External Service Integration for Tool Executor
=============================================
Integrates tool execution with external service adapters (Gmail, Dropbox, etc.)
"""

import logging
from datetime import datetime
from typing import Any, Optional

# Service Adapter Integration
try:
    from candidate.bridge.adapters.drive_adapter import DriveAdapter
    from candidate.bridge.adapters.dropbox_adapter import DropboxAdapter
    from candidate.bridge.adapters.gmail_adapter import GmailAdapter
    from candidate.bridge.adapters.service_adapter_base import BaseServiceAdapter, CapabilityToken
except ImportError:
    BaseServiceAdapter = None
    CapabilityToken = None
    GmailAdapter = None
    DropboxAdapter = None
    DriveAdapter = None

logger = logging.getLogger("ΛTRACE.tools.external")


class ExternalServiceIntegration:
    """
    🔌 External Service Integration Layer

    Provides unified interface for tool executor to interact with external services
    through secure, authenticated adapters with comprehensive monitoring.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.adapters = {}
        self.service_capabilities = {}

        # Initialize available adapters
        self._initialize_adapters()

        # Integration metrics
        self.integration_metrics = {
            "adapter_initializations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "authentication_attempts": 0,
            "authentication_successes": 0,
            "rate_limit_hits": 0,
            "consent_denials": 0,
        }

        # Service mapping for tool operations
        self.tool_service_mapping = {
            "gmail_send": "gmail",
            "gmail_list": "gmail",
            "gmail_read": "gmail",
            "dropbox_upload": "dropbox",
            "dropbox_download": "dropbox",
            "dropbox_list": "dropbox",
            "drive_upload": "google_drive",
            "drive_download": "google_drive",
            "drive_list": "google_drive",
            "drive_share": "google_drive",
        }

        logger.info(f"External Service Integration initialized with {len(self.adapters)} adapters")

    def _initialize_adapters(self):
        """Initialize all available service adapters"""
        adapter_configs = [
            ("gmail", GmailAdapter, "Gmail"),
            ("dropbox", DropboxAdapter, "Dropbox"),
            ("google_drive", DriveAdapter, "Google Drive"),
        ]

        for service_name, adapter_class, display_name in adapter_configs:
            if adapter_class:
                try:
                    adapter = adapter_class(service_name)
                    self.adapters[service_name] = adapter
                    self.service_capabilities[service_name] = adapter.supported_scopes
                    self.integration_metrics["adapter_initializations"] += 1
                    logger.info(f"Initialized {display_name} adapter")
                except Exception as e:
                    logger.warning(f"Failed to initialize {display_name} adapter: {e}")
            else:
                logger.debug(f"{display_name} adapter not available")

    async def execute_service_operation(
        self,
        operation: str,
        arguments: dict[str, Any],
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute operation on external service through appropriate adapter

        Args:
            operation: Service operation (e.g., 'gmail_send', 'dropbox_upload')
            arguments: Operation arguments
            user_context: User context including authentication info

        Returns:
            Operation result with status and data
        """
        service_name = self.tool_service_mapping.get(operation)
        if not service_name:
            return self._create_error_result(f"Unknown service operation: {operation}")

        adapter = self.adapters.get(service_name)
        if not adapter:
            return self._create_error_result(f"Service adapter not available: {service_name}")

        try:
            # Extract user information
            lid = user_context.get("lid", "anonymous") if user_context else "anonymous"
            credentials = user_context.get("credentials", {}) if user_context else {}

            # Authenticate if needed
            auth_result = await self._ensure_authentication(adapter, lid, credentials)
            if not auth_result["success"]:
                self.integration_metrics["authentication_attempts"] += 1
                return auth_result

            self.integration_metrics["authentication_successes"] += 1

            # Check consent for operation
            consent_granted = await self._check_operation_consent(adapter, lid, operation, arguments)
            if not consent_granted:
                self.integration_metrics["consent_denials"] += 1
                return self._create_error_result(
                    "Operation denied by consent system",
                    {"reason": "consent_denied", "service": service_name},
                )

            # Execute the specific operation
            result = await self._route_service_operation(adapter, operation, arguments, lid)

            if result.get("success", False):
                self.integration_metrics["successful_operations"] += 1
            else:
                self.integration_metrics["failed_operations"] += 1

            return result

        except Exception as e:
            self.integration_metrics["failed_operations"] += 1
            logger.error(f"Service operation failed: {operation}: {e}", exc_info=True)
            return self._create_error_result(str(e))

    async def _ensure_authentication(
        self, adapter: BaseServiceAdapter, lid: str, credentials: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure adapter is authenticated for the user"""
        try:
            # Try identity-based authentication first
            if hasattr(adapter, "authenticate_with_identity"):
                auth_result = await adapter.authenticate_with_identity(lid, credentials)
            else:
                auth_result = await adapter.authenticate(credentials)

            if auth_result.get("error"):
                return {
                    "success": False,
                    "error": "authentication_failed",
                    "details": auth_result.get("error"),
                }

            return {"success": True, "auth_result": auth_result}

        except Exception as e:
            logger.error(f"Authentication failed for {adapter.service_name}: {e}")
            return {
                "success": False,
                "error": "authentication_error",
                "details": str(e),
            }

    async def _check_operation_consent(
        self,
        adapter: BaseServiceAdapter,
        lid: str,
        operation: str,
        arguments: dict[str, Any],
    ) -> bool:
        """Check if user has consented to the operation"""
        try:
            if hasattr(adapter, "check_consent"):
                context = {
                    "operation": operation,
                    "arguments": arguments,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                return await adapter.check_consent(lid, operation, context)
            return True  # Allow if consent checking not available
        except Exception as e:
            logger.warning(f"Consent check failed: {e}")
            return False  # Be conservative on consent check failure

    async def _route_service_operation(
        self,
        adapter: BaseServiceAdapter,
        operation: str,
        arguments: dict[str, Any],
        lid: str,
    ) -> dict[str, Any]:
        """Route operation to specific adapter method"""

        # Gmail operations
        if operation.startswith("gmail_"):
            return await self._handle_gmail_operation(adapter, operation, arguments, lid)

        # Dropbox operations
        elif operation.startswith("dropbox_"):
            return await self._handle_dropbox_operation(adapter, operation, arguments, lid)

        # Google Drive operations
        elif operation.startswith("drive_"):
            return await self._handle_drive_operation(adapter, operation, arguments, lid)

        else:
            return self._create_error_result(f"Unsupported operation: {operation}")

    async def _handle_gmail_operation(
        self, adapter, operation: str, arguments: dict[str, Any], lid: str
    ) -> dict[str, Any]:
        """Handle Gmail-specific operations"""
        try:
            if operation == "gmail_send":
                required_fields = ["to", "subject", "body"]
                missing = [field for field in required_fields if field not in arguments]
                if missing:
                    return self._create_error_result(f"Missing required fields: {missing}")

                # Create capability token for sending email
                token = self._create_capability_token(lid, "gmail", ["write", "send"])

                result = await adapter.send_email(
                    lid=lid,
                    to=arguments["to"],
                    subject=arguments["subject"],
                    body=arguments["body"],
                    attachments=arguments.get("attachments", []),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "gmail_send"}

            elif operation == "gmail_list":
                token = self._create_capability_token(lid, "gmail", ["read", "list"])

                result = await adapter.list_messages(
                    lid=lid,
                    limit=arguments.get("limit", 10),
                    query=arguments.get("query", ""),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "gmail_list"}

            elif operation == "gmail_read":
                if "message_id" not in arguments:
                    return self._create_error_result("Missing required field: message_id")

                token = self._create_capability_token(lid, "gmail", ["read"])

                result = await adapter.get_message(lid=lid, message_id=arguments["message_id"], capability_token=token)

                return {"success": True, "data": result, "operation": "gmail_read"}

            else:
                return self._create_error_result(f"Unsupported Gmail operation: {operation}")

        except Exception as e:
            logger.error(f"Gmail operation failed: {operation}: {e}")
            return self._create_error_result(str(e))

    async def _handle_dropbox_operation(
        self, adapter, operation: str, arguments: dict[str, Any], lid: str
    ) -> dict[str, Any]:
        """Handle Dropbox-specific operations"""
        try:
            if operation == "dropbox_upload":
                required_fields = ["file_path", "content"]
                missing = [field for field in required_fields if field not in arguments]
                if missing return self._create_error_result(f"Missing required fields: {missing}")

                token = self._create_capability_token(lid, "dropbox", ["write"])

                result = await adapter.upload_file(
                    lid=lid,
                    file_path=arguments["file_path"],
                    content=arguments["content"],
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "dropbox_upload"}

            elif operation == "dropbox_download":
                if "file_path" not in arguments:
                    return self._create_error_result("Missing required field: file_path")

                token = self._create_capability_token(lid, "dropbox", ["read"])

                result = await adapter.download_file(lid=lid, file_path=arguments["file_path"], capability_token=token)

                return {
                    "success": True,
                    "data": result,
                    "operation": "dropbox_download",
                }

            elif operation == "dropbox_list":
                token = self._create_capability_token(lid, "dropbox", ["read", "list"])

                result = await adapter.list_files(
                    lid=lid,
                    folder_path=arguments.get("folder_path", "/"),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "dropbox_list"}

            else:
                return self._create_error_result(f"Unsupported Dropbox operation: {operation}")

        except Exception as e:
            logger.error(f"Dropbox operation failed: {operation}: {e}")
            return self._create_error_result(str(e))

    async def _handle_drive_operation(
        self, adapter, operation: str, arguments: dict[str, Any], lid: str
    ) -> dict[str, Any]:
        """Handle Google Drive-specific operations"""
        try:
            if operation == "drive_upload":
                required_fields = ["file_name", "content"]
                missing = [field for field in required_fields if field not in arguments]
                if missing return self._create_error_result(f"Missing required fields: {missing}")

                token = self._create_capability_token(lid, "google_drive", ["write"])

                result = await adapter.upload_file(
                    lid=lid,
                    file_name=arguments["file_name"],
                    content=arguments["content"],
                    folder_id=arguments.get("folder_id"),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "drive_upload"}

            elif operation == "drive_download":
                if "file_id" not in arguments:
                    return self._create_error_result("Missing required field: file_id")

                token = self._create_capability_token(lid, "google_drive", ["read"])

                result = await adapter.download_file(lid=lid, file_id=arguments["file_id"], capability_token=token)

                return {"success": True, "data": result, "operation": "drive_download"}

            elif operation == "drive_list":
                token = self._create_capability_token(lid, "google_drive", ["read", "list"])

                result = await adapter.list_files(
                    lid=lid,
                    folder_id=arguments.get("folder_id"),
                    query=arguments.get("query"),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "drive_list"}

            elif operation == "drive_share":
                required_fields = ["file_id", "email"]
                missing = [field for field in required_fields if field not in arguments]
                if missing return self._create_error_result(f"Missing required fields: {missing}")

                token = self._create_capability_token(lid, "google_drive", ["write", "share"])

                result = await adapter.share_file(
                    lid=lid,
                    file_id=arguments["file_id"],
                    email=arguments["email"],
                    role=arguments.get("role", "reader"),
                    capability_token=token,
                )

                return {"success": True, "data": result, "operation": "drive_share"}

            else:
                return self._create_error_result(f"Unsupported Drive operation: {operation}")

        except Exception as e:
            logger.error(f"Drive operation failed: {operation}: {e}")
            return self._create_error_result(str(e))

    def _create_capability_token(self, lid: str, service: str, scopes: list[str]) -> Optional[CapabilityToken]:
        """Create capability token for service operation"""
        if not CapabilityToken:
            return None

        try:
            token = CapabilityToken(
                token_id=f"tool_executor_{lid}_{int(datetime.now(timezone.utc).timestamp())}",
                lid=lid,
                scope=scopes,
                resource_ids=[service],
                ttl=3600,  # 1 hour
                audience=service,
                issued_at=datetime.now(timezone.utc).isoformat(),
                signature="tool_executor_generated",
            )
            return token
        except Exception as e:
            logger.warning(f"Failed to create capability token: {e}")
            return None

    def _create_error_result(self, error_message: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Create standardized error result"""
        result = {
            "success": False,
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if details:
            result["details"] = details

        return result

    async def get_service_health(self) -> dict[str, Any]:
        """Get health status of all integrated services"""
        health_status = {
            "integration_active": True,
            "adapters_count": len(self.adapters),
            "metrics": self.integration_metrics,
            "services": {},
        }

        for service_name, adapter in self.adapters.items():
            try:
                service_health = adapter.get_health_status()
                health_status["services"][service_name] = service_health
            except Exception as e:
                health_status["services"][service_name] = {
                    "error": str(e),
                    "status": "unhealthy",
                }

        return health_status

    def get_available_operations(self) -> dict[str, list[str]]:
        """Get list of available operations by service"""
        operations = {}

        for service_name in self.adapters:
            service_ops = []

            if service_name == "gmail":
                service_ops = ["gmail_send", "gmail_list", "gmail_read"]
            elif service_name == "dropbox":
                service_ops = ["dropbox_upload", "dropbox_download", "dropbox_list"]
            elif service_name == "google_drive":
                service_ops = [
                    "drive_upload",
                    "drive_download",
                    "drive_list",
                    "drive_share",
                ]

            operations[service_name] = service_ops

        return operations

    def get_integration_metrics(self) -> dict[str, Any]:
        """Get comprehensive integration metrics"""
        return {
            **self.integration_metrics,
            "success_rate": (
                self.integration_metrics["successful_operations"]
                / max(
                    1,
                    self.integration_metrics["successful_operations"] + self.integration_metrics["failed_operations"],
                )
            ),
            "authentication_success_rate": (
                self.integration_metrics["authentication_successes"]
                / max(1, self.integration_metrics["authentication_attempts"])
            ),
            "available_services": list(self.adapters.keys()),
            "total_operations": len(self.tool_service_mapping),
        }


# Global integration instance
_integration: Optional[ExternalServiceIntegration] = None


def get_external_service_integration(
    config: Optional[dict[str, Any]] = None,
) -> ExternalServiceIntegration:
    """Get or create the global external service integration instance"""
    global _integration
    if _integration is None:
        _integration = ExternalServiceIntegration(config)
    return _integration
