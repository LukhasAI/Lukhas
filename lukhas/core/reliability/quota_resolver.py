"""
Quota resolver for dynamic rate limit configuration.

Loads per-principal quotas from configs/quotas.yaml and provides
lookup functionality for rate limiting backends. Falls back to
environment variables when principal not found in config.

Phase 3: Guardian enhancements for Redis rate-limit backend integration.
"""
import ipaddress
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Quota:
    """Rate limit quota configuration."""
    rps: int  # Requests per second
    burst: int  # Burst capacity (token bucket size)
    description: str = ""


class QuotaResolver:
    """
    Resolves rate limit quotas for principals from configuration.

    Supports tenant-based, user-based, and IP-based principal lookups
    with fallback to environment variables for principals not in config.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize quota resolver.

        Args:
            config_path: Path to quotas.yaml config file (optional)
        """
        self.defaults: Quota = Quota(rps=20, burst=40, description="system default")
        self.principals: Dict[str, Quota] = {}
        self.endpoint_multipliers: Dict[str, float] = {}

        # Load from config file if provided or use default location
        if config_path is None:
            # Try standard locations
            candidates = [
                Path("configs/quotas.yaml"),
                Path("../configs/quotas.yaml"),
                Path(__file__).parent.parent.parent.parent / "configs/quotas.yaml",
            ]
            for path in candidates:
                if path.exists():
                    config_path = str(path)
                    break

        if config_path and Path(config_path).exists():
            try:
                self._load_config(config_path)
                logger.info(f"Loaded quotas from {config_path}: {len(self.principals)} principals")
            except Exception as e:
                logger.warning(f"Failed to load quotas from {config_path}: {e}, using defaults")
        else:
            logger.warning(f"Quota config not found at {config_path}, using defaults")

        # Load environment variable defaults as fallback
        self._load_env_defaults()

    def _load_config(self, config_path: str) -> None:
        """Load quota configuration from YAML file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Load defaults
        defaults_cfg = config.get("defaults", {})
        self.defaults = Quota(
            rps=defaults_cfg.get("rps", 20),
            burst=defaults_cfg.get("burst", 40),
            description="config default"
        )

        # Load per-principal quotas
        for principal_cfg in config.get("principals", []):
            principal = principal_cfg.get("principal")
            if not principal:
                continue

            self.principals[principal] = Quota(
                rps=principal_cfg.get("rps", self.defaults.rps),
                burst=principal_cfg.get("burst", self.defaults.burst),
                description=principal_cfg.get("description", "")
            )

        # Load endpoint multipliers
        self.endpoint_multipliers = config.get("endpoint_multipliers", {})

    def _load_env_defaults(self) -> None:
        """Load default quotas from environment variables as fallback."""
        try:
            env_rps = int(os.getenv("LUKHAS_DEFAULT_RPS", "20"))
            env_burst = int(os.getenv("LUKHAS_DEFAULT_BURST", "40"))

            # Only override if not already loaded from config
            if self.defaults.description == "system default":
                self.defaults = Quota(
                    rps=env_rps,
                    burst=env_burst,
                    description="env default"
                )
        except ValueError as e:
            logger.warning(f"Invalid env quota values: {e}, keeping current defaults")

    def resolve(self, principal: str, endpoint: Optional[str] = None) -> Quota:
        """
        Resolve quota for a principal and optional endpoint.

        Args:
            principal: Principal identifier (tenant:id, user:id, ip:addr, etc.)
            endpoint: Optional endpoint path for quota multipliers

        Returns:
            Quota configuration with rps and burst limits
        """
        # Try exact principal match
        quota = self.principals.get(principal)

        # Try IP CIDR matching for IP-based principals
        if quota is None and principal.startswith("ip:"):
            quota = self._match_ip_quota(principal)

        # Fallback to defaults
        if quota is None:
            quota = self.defaults

        # Apply endpoint multiplier if specified
        if endpoint and endpoint in self.endpoint_multipliers:
            multiplier = self.endpoint_multipliers[endpoint]
            return Quota(
                rps=int(quota.rps * multiplier),
                burst=int(quota.burst * multiplier),
                description=f"{quota.description} (endpoint x{multiplier})"
            )

        return quota

    def _match_ip_quota(self, principal: str) -> Optional[Quota]:
        """
        Match IP-based principal against CIDR ranges in config.

        Args:
            principal: IP principal string (format: "ip:1.2.3.4")

        Returns:
            Matched quota or None
        """
        if not principal.startswith("ip:"):
            return None

        try:
            ip_str = principal[3:]  # Remove "ip:" prefix
            ip_addr = ipaddress.ip_address(ip_str)

            # Check all configured IP ranges
            for key, quota in self.principals.items():
                if key.startswith("ip:") and "/" in key:
                    # CIDR range like "ip:203.0.113.0/24"
                    cidr_str = key[3:]
                    network = ipaddress.ip_network(cidr_str, strict=False)
                    if ip_addr in network:
                        return quota
        except (ValueError, KeyError) as e:
            logger.debug(f"Failed to match IP quota for {principal}: {e}")

        return None

    def resolve_from_env(self, endpoint: Optional[str] = None) -> Quota:
        """
        Resolve quota purely from environment variables (fallback mode).

        Args:
            endpoint: Optional endpoint path (unused in env fallback)

        Returns:
            Quota from environment or system defaults
        """
        return self.defaults

    def get_quota_for_key(self, key: str) -> Tuple[int, int]:
        """
        Get (rps, burst) tuple for a rate limit key.

        Convenience method for backends that need tuple format.

        Args:
            key: Rate limit key (may contain principal info)

        Returns:
            (rps, burst) tuple
        """
        # Extract principal from key if present
        # Key format: "route:principal" or just "route"
        principal = "anonymous"
        endpoint = None

        if ":" in key:
            parts = key.split(":", 1)
            if len(parts) == 2:
                endpoint = parts[0]
                principal = parts[1]

        quota = self.resolve(principal, endpoint)
        return quota.rps, quota.burst
