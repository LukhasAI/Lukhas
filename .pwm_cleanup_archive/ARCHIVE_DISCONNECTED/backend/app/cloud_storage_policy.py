"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : cloud_storage_policy.py                        │
│ DESCRIPTION : Symbolic cloud storage quota + policy manager  │
│ TYPE        : Storage Policy + Quota Engine                  │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

# ── Symbolic Quotas and Storage Rules ─────────────────────────

TIER_QUOTAS_MB = {
    1: 512,  # Tier 1: 512 MB
    2: 2048,  # Tier 2: 2 GB
    3: 8192,  # Tier 3: 8 GB
    4: 32768,  # Tier 4: 32 GB + Secrets Vault (personal vault tier)
}

RETENTION_POLICY = {
    "default_retention_days": 365,  # Keep symbolic vaults 1 year minimum
    "inactive_account_cleanup_days": 730,  # 2 years symbolic inactivity triggers warning
}

# ── Symbolic Policy Functions ─────────────────────────────────


def get_quota_for_tier(tier: int) -> int:
    """
    Get allowed cloud storage quota in MB based on user's symbolic tier.
    """
    return TIER_QUOTAS_MB.get(tier, 512)


def get_default_retention_period() -> int:
    """
    Return symbolic default retention period in days.
    """
    return RETENTION_POLICY["default_retention_days"]


def get_inactive_cleanup_period() -> int:
    """
    Return symbolic cleanup trigger period for inactive accounts.
    """
    return RETENTION_POLICY["inactive_account_cleanup_days"]


# ===============================================================
# 💾 HOW TO USE
# ===============================================================
# ▶️ IMPORT THIS MODULE:
#     from backend.app.cloud_storage_policy import get_quota_for_tier, get_default_retention_period, get_inactive_cleanup_period
#
# 🧠 WHAT THIS MODULE DOES:
# - Returns cloud storage quota limits per user tier
# - Defines symbolic vault retention and cleanup rules
#
# 🧑‍🏫 GOOD FOR:
# - Storage dashboards
# - Compliance-driven data lifecycle management
# - Symbolic memory preservation policies
# ===============================================================
