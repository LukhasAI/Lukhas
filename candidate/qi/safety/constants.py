# path: qi/safety/constants.py
"""
LUKHAS Safety Constants

Single source of truth for safety bounds and guardrails.
"""

# Maximum threshold shift for feedback-driven adjustments
MAX_THRESHOLD_SHIFT = 0.05

# Allowed style values for policy patches
ALLOWED_STYLES = {"concise", "narrative", "technical", "empathetic"}

# Calibration cold-start threshold
MIN_SAMPLES_FOR_TASK_CALIBRATION = 50

# Feedback deduplication window (minutes)
FEEDBACK_DEDUP_WINDOW_MINUTES = 5

# Minimum cluster size for promotion
MIN_CLUSTER_SIZE = 3

# Maximum explanation depth
MAX_EXPLAIN_DEPTH = 5

# Calibration weight bounds
CALIBRATION_WEIGHT_MAX = 0.2
CALIBRATION_WEIGHT_ALPHA = 0.5

# Proposal TTL defaults (seconds)
DEFAULT_PROPOSAL_TTL_SEC = 3600
MAX_PROPOSAL_TTL_SEC = 86400  # 24 hours

# Rate limiting
FEEDBACK_RATE_LIMIT_PER_IP = 100  # per hour
FEEDBACK_RATE_LIMIT_PER_USER = 50  # per hour
FEEDBACK_BURST_DECAY_SECONDS = 60

# Data retention (days)
FEEDBACK_RETENTION_DAYS = 90
MERKLE_DIGEST_RETENTION_DAYS = None  # Keep forever

# Cryptographic profiles
CRYPTO_PROFILE_DEV = "development"
CRYPTO_PROFILE_PROD = "production"

# SLO targets
SLO_INGESTION_SUCCESS_RATE = 0.999
SLO_PROPOSAL_APPLY_LATENCY_P95_MS = 2000
