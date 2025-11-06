"""
Unit tests for QuotaResolver.

Tests quota resolution from config files with per-principal limits,
IP CIDR matching, endpoint multipliers, and fallback to environment.
"""
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from core.reliability.quota_resolver import Quota, QuotaResolver


class TestQuotaResolver:
    """Test suite for QuotaResolver."""

    def test_default_quotas(self):
        """Test resolver returns default quotas when no config present."""
        resolver = QuotaResolver(config_path="/nonexistent/path.yaml")
        quota = resolver.resolve("tenant:unknown")

        assert isinstance(quota, Quota)
        assert quota.rps > 0
        assert quota.burst > 0

    def test_exact_principal_match(self, tmp_path):
        """Test exact principal match from config."""
        config = {
            "version": 1,
            "defaults": {"rps": 20, "burst": 40},
            "principals": [
                {
                    "principal": "tenant:acme-corp",
                    "rps": 100,
                    "burst": 200,
                    "description": "Enterprise tier",
                }
            ],
        }

        config_file = tmp_path / "quotas.yaml"
        config_file.write_text(yaml.dump(config))

        resolver = QuotaResolver(config_path=str(config_file))
        quota = resolver.resolve("tenant:acme-corp")

        assert quota.rps == 100
        assert quota.burst == 200
        assert "Enterprise tier" in quota.description

    def test_ip_cidr_matching(self, tmp_path):
        """Test IP CIDR range matching for IP-based principals."""
        config = {
            "version": 1,
            "defaults": {"rps": 20, "burst": 40},
            "principals": [
                {
                    "principal": "ip:203.0.113.0/24",
                    "rps": 5,
                    "burst": 10,
                    "description": "Public IP range",
                }
            ],
        }

        config_file = tmp_path / "quotas.yaml"
        config_file.write_text(yaml.dump(config))

        resolver = QuotaResolver(config_path=str(config_file))

        # IP within range should match
        quota = resolver.resolve("ip:203.0.113.50")
        assert quota.rps == 5
        assert quota.burst == 10

        # IP outside range should get defaults
        quota = resolver.resolve("ip:192.168.1.1")
        assert quota.rps == 20
        assert quota.burst == 40

    def test_endpoint_multipliers(self, tmp_path):
        """Test endpoint-specific quota multipliers."""
        config = {
            "version": 1,
            "defaults": {"rps": 20, "burst": 40},
            "principals": [
                {"principal": "tenant:test", "rps": 50, "burst": 100}
            ],
            "endpoint_multipliers": {
                "/v1/embeddings": 2.5,
                "/v1/dreams": 0.25,
            },
        }

        config_file = tmp_path / "quotas.yaml"
        config_file.write_text(yaml.dump(config))

        resolver = QuotaResolver(config_path=str(config_file))

        # Embedding endpoint gets 2.5x multiplier
        quota = resolver.resolve("tenant:test", endpoint="/v1/embeddings")
        assert quota.rps == 125  # 50 * 2.5
        assert quota.burst == 250  # 100 * 2.5

        # Dreams endpoint gets 0.25x multiplier (restricted)
        quota = resolver.resolve("tenant:test", endpoint="/v1/dreams")
        assert quota.rps == 12  # 50 * 0.25, truncated to int
        assert quota.burst == 25  # 100 * 0.25

        # No multiplier for other endpoints
        quota = resolver.resolve("tenant:test", endpoint="/v1/responses")
        assert quota.rps == 50
        assert quota.burst == 100

    def test_env_defaults(self, monkeypatch):
        """Test environment variable fallback for defaults when no config file."""
        monkeypatch.setenv("LUKHAS_DEFAULT_RPS", "99")
        monkeypatch.setenv("LUKHAS_DEFAULT_BURST", "199")

        # No config file, should use env defaults
        resolver = QuotaResolver(config_path="/nonexistent/path.yaml")

        # Should use env defaults for unknown principal
        quota = resolver.resolve("tenant:unknown")
        assert quota.rps == 99
        assert quota.burst == 199

    def test_get_quota_for_key(self, tmp_path):
        """Test get_quota_for_key convenience method."""
        config = {
            "version": 1,
            "defaults": {"rps": 20, "burst": 40},
            "principals": [
                {"principal": "tenant:premium", "rps": 100, "burst": 200}
            ],
        }

        config_file = tmp_path / "quotas.yaml"
        config_file.write_text(yaml.dump(config))

        resolver = QuotaResolver(config_path=str(config_file))

        # Key format: "route:principal"
        rps, burst = resolver.get_quota_for_key("/v1/responses:tenant:premium")
        assert rps == 100
        assert burst == 200

        # Unknown principal gets defaults
        rps, burst = resolver.get_quota_for_key("/v1/responses:anonymous")
        assert rps == 20
        assert burst == 40

    def test_invalid_ip_fallback(self, tmp_path):
        """Test graceful fallback for invalid IP addresses."""
        config = {
            "version": 1,
            "defaults": {"rps": 20, "burst": 40},
        }

        config_file = tmp_path / "quotas.yaml"
        config_file.write_text(yaml.dump(config))

        resolver = QuotaResolver(config_path=str(config_file))

        # Invalid IP format should fall back to defaults
        quota = resolver.resolve("ip:invalid-ip")
        assert quota.rps == 20
        assert quota.burst == 40
