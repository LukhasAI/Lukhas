"""
LUKHAS AI - Unified Authentication Integration Bridge
Production integration module for consciousness-aware authentication ecosystem

This module provides the integration points between:
- Consolidated auth system (candidate/governance/identity/auth*)
- WALLET identity management (lambda_products_pack/lambda_core/WALLET)
- QRG advanced authentication (lambda_products_pack/lambda_core/QRG)
- Production nucleus (lukhas/lukhas/identity)
"""

import logging
from pathlib import Path
from typing import Any

# Add paths for dynamic imports
LUKHAS_ROOT = Path(__file__).parent.parent.parent
CANDIDATE_AUTH_PATH = LUKHAS_ROOT / "candidate" / "governance" / "identity"
LAMBDA_CORE_PATH = LUKHAS_ROOT / "lambda_products_pack" / "lambda_core"

# Avoid mutating sys.path at import-time; paths are resolved via filesystem


class AuthenticationIntegration:
    """
    🎖️ LUKHAS Authentication Integration Bridge

    Coordinates between:
    - Consolidated consciousness-aware auth system
    - WALLET identity management
    - QRG advanced authentication flows
    - Production nucleus components
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._components = {}
        self._bridges = {}

    async def initialize(self):
        """Initialize all authentication components and bridges"""
        try:
            # Load consolidated auth components
            await self._load_consolidated_auth()

            # Load WALLET components
            await self._load_wallet_components()

            # Load QRG components
            await self._load_qrg_components()

            # Initialize integration bridges
            await self._initialize_bridges()

            self.logger.info(
                "LUKHAS Authentication Integration initialized successfully"
            )

        except Exception as e:
            self.logger.error("Integration initialization failed: %s", e)
            raise

    async def _load_consolidated_auth(self):
        """Load components from consolidated auth system"""
        try:
            # Core consciousness components
            auth_core_path = CANDIDATE_AUTH_PATH / "auth"
            if auth_core_path.exists():
                self._components["auth_core"] = str(auth_core_path)

            # Backend services
            auth_backend_path = CANDIDATE_AUTH_PATH / "auth_backend"
            if auth_backend_path.exists():
                self._components["auth_backend"] = str(auth_backend_path)

            # Web components
            auth_web_path = CANDIDATE_AUTH_PATH / "auth_web"
            if auth_web_path.exists():
                self._components["auth_web"] = str(auth_web_path)

            # Utility components
            auth_utils_path = CANDIDATE_AUTH_PATH / "auth_utils"
            if auth_utils_path.exists():
                self._components["auth_utils"] = str(auth_utils_path)

            # Integration bridges
            auth_integrations_path = CANDIDATE_AUTH_PATH / "auth_integrations"
            if auth_integrations_path.exists():
                self._components["auth_integrations"] = str(auth_integrations_path)

            self.logger.info("Consolidated auth components loaded")

        except Exception as e:
            self.logger.error("Failed to load consolidated auth: %s", e)
            raise

    async def _load_wallet_components(self):
        """Load WALLET components from lambda_products_pack"""
        try:
            wallet_path = LAMBDA_CORE_PATH / "WALLET"
            if wallet_path.exists():
                self._components["wallet"] = {
                    "path": str(wallet_path),
                    "components": {
                        "identity_manager": wallet_path / "identity_manager.py",
                        "qi_identity_core": wallet_path / "qi_identity_core.py",
                        "symbolic_vault": wallet_path / "symbolic_vault.py",
                        "wallet_core": wallet_path / "wallet_core.py",
                    },
                }
                self.logger.info("WALLET components loaded")
            else:
                self.logger.warning("WALLET path not found: %s", wallet_path)

        except Exception as e:
            self.logger.error("Failed to load WALLET components: %s", e)
            raise

    async def _load_qrg_components(self):
        """Load QRG components from lambda_products_pack"""
        try:
            qrg_path = LAMBDA_CORE_PATH / "QRG"
            if qrg_path.exists():
                self._components["qrg"] = {
                    "path": str(qrg_path),
                    "components": {
                        "qrg_core": qrg_path / "qrg_core.py",
                        "animation_engine": qrg_path / "animation_engine.py",
                        "steganography": qrg_path / "steganography.py",
                        "consciousness_layer": qrg_path / "consciousness_layer.py",
                        "qi_entropy": qrg_path / "qi_entropy.py",
                    },
                }
                self.logger.info("QRG components loaded")
            else:
                self.logger.warning("QRG path not found: %s", qrg_path)

        except Exception as e:
            self.logger.error("Failed to load QRG components: %s", e)
            raise

    async def _initialize_bridges(self):
        """Initialize integration bridges between components"""
        try:
            # Initialize WALLET bridge if available
            if "wallet" in self._components:
                wallet_bridge_path = (
                    CANDIDATE_AUTH_PATH / "auth_integrations" / "wallet_bridge.py"
                )
                if wallet_bridge_path.exists():
                    self._bridges["wallet"] = str(wallet_bridge_path)

            # Initialize QRG bridge if available
            if "qrg" in self._components:
                qrg_bridge_path = (
                    CANDIDATE_AUTH_PATH / "auth_integrations" / "qrg_bridge.py"
                )
                if qrg_bridge_path.exists():
                    self._bridges["qrg"] = str(qrg_bridge_path)

            self.logger.info("Integration bridges initialized")

        except Exception as e:
            self.logger.error("Failed to initialize bridges: %s", e)
            raise

    def get_component_paths(self) -> dict[str, Any]:
        """Get all loaded component paths"""
        return self._components.copy()

    def get_bridge_paths(self) -> dict[str, str]:
        """Get all initialized bridge paths"""
        return self._bridges.copy()

    def get_integration_status(self) -> dict[str, Any]:
        """Get current integration status"""
        return {
            "components_loaded": len(self._components),
            "bridges_initialized": len(self._bridges),
            "components": list(self._components.keys()),
            "bridges": list(self._bridges.keys()),
            "paths": {
                "candidate_auth": str(CANDIDATE_AUTH_PATH),
                "lambda_core": str(LAMBDA_CORE_PATH),
                "lukhas_root": str(LUKHAS_ROOT),
            },
        }


# Global integration instance
_integration = None


async def get_integration() -> AuthenticationIntegration:
    """Get the global authentication integration instance"""
    global _integration
    if _integration is None:
        _integration = AuthenticationIntegration()
        await _integration.initialize()
    return _integration


# Export key components
__all__ = [
    "AuthenticationIntegration",
    "get_integration",
    "LUKHAS_ROOT",
    "CANDIDATE_AUTH_PATH",
    "LAMBDA_CORE_PATH",
]
