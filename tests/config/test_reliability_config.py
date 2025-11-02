"""
Test suite for reliability configuration validation.

Ensures configs/runtime/reliability.yaml contains valid parameters
within safe operational ranges and SLO-compatible values.
"""

from pathlib import Path

import pytest
import yaml

# Constants
CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "runtime" / "reliability.yaml"
SLO_E2E_MS = 250  # Target p95 latency for consciousness streams (from docs/openai/SLOs.md)


@pytest.fixture
def reliability_config():
    """Load reliability configuration file."""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def test_config_file_exists():
    """Ensure reliability.yaml exists in expected location."""
    assert CONFIG_PATH.exists(), f"Config file not found: {CONFIG_PATH}"


def test_config_file_valid_yaml():
    """Ensure reliability.yaml is valid YAML syntax."""
    try:
        with open(CONFIG_PATH) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML syntax: {e}")


def test_timeouts_section_exists(reliability_config):
    """Ensure 'timeouts' section is present."""
    assert "timeouts" in reliability_config, "Missing 'timeouts' section"


def test_connect_timeout_valid(reliability_config):
    """Validate connect_ms is within safe range (100-10000ms)."""
    connect_ms = reliability_config["timeouts"]["connect_ms"]
    assert isinstance(connect_ms, int), "connect_ms must be integer"
    assert 100 <= connect_ms <= 10000, f"connect_ms ({connect_ms}ms) must be 100-10000ms for reliable operations"


def test_read_timeout_valid(reliability_config):
    """Validate read_ms is within safe range (1000-30000ms)."""
    read_ms = reliability_config["timeouts"]["read_ms"]
    assert isinstance(read_ms, int), "read_ms must be integer"
    assert 1000 <= read_ms <= 30000, f"read_ms ({read_ms}ms) must be 1000-30000ms for reliable operations"


def test_read_timeout_slo_compatible(reliability_config):
    """Ensure read_ms allows meeting SLO with 2× buffer."""
    read_ms = reliability_config["timeouts"]["read_ms"]
    min_required_ms = SLO_E2E_MS * 2
    assert (
        read_ms >= min_required_ms
    ), f"read_ms ({read_ms}ms) must be >= {min_required_ms}ms (2× SLO_E2E_MS) for SLO compliance"


def test_backoff_section_exists(reliability_config):
    """Ensure 'backoff' section is present."""
    assert "backoff" in reliability_config, "Missing 'backoff' section"


def test_backoff_base_valid(reliability_config):
    """Validate base_s is within safe range (0.01-5.0s)."""
    base_s = reliability_config["backoff"]["base_s"]
    assert isinstance(base_s, (int, float)), "base_s must be numeric"
    assert 0.01 <= base_s <= 5.0, f"base_s ({base_s}s) must be 0.01-5.0s for reasonable retry delays"


def test_backoff_factor_valid(reliability_config):
    """Validate factor is within safe range (1.0-5.0)."""
    factor = reliability_config["backoff"]["factor"]
    assert isinstance(factor, (int, float)), "factor must be numeric"
    assert 1.0 <= factor <= 5.0, f"factor ({factor}) must be 1.0-5.0 for exponential backoff"


def test_backoff_jitter_valid(reliability_config):
    """Validate jitter is within safe range (0.0-1.0)."""
    jitter = reliability_config["backoff"]["jitter"]
    assert isinstance(jitter, (int, float)), "jitter must be numeric"
    assert 0.0 <= jitter <= 1.0, f"jitter ({jitter}) must be 0.0-1.0 (fraction of base delay)"


def test_backoff_jitter_recommended(reliability_config):
    """Warn if jitter is 0.0 (thundering herd risk)."""
    jitter = reliability_config["backoff"]["jitter"]
    if jitter == 0.0:
        pytest.skip("WARNING: jitter=0.0 can cause thundering herd. Recommended: 0.1-0.2")


def test_rate_limits_section_exists(reliability_config):
    """Ensure 'rate_limits' section is present."""
    assert "rate_limits" in reliability_config, "Missing 'rate_limits' section"


def test_responses_rps_valid(reliability_config):
    """Validate responses_rps is within safe range (1-1000)."""
    responses_rps = reliability_config["rate_limits"]["responses_rps"]
    assert isinstance(responses_rps, int), "responses_rps must be integer"
    assert 1 <= responses_rps <= 1000, f"responses_rps ({responses_rps}) must be 1-1000 RPS for realistic limits"


def test_embeddings_rps_valid(reliability_config):
    """Validate embeddings_rps is within safe range (1-1000)."""
    embeddings_rps = reliability_config["rate_limits"]["embeddings_rps"]
    assert isinstance(embeddings_rps, int), "embeddings_rps must be integer"
    assert 1 <= embeddings_rps <= 1000, f"embeddings_rps ({embeddings_rps}) must be 1-1000 RPS for realistic limits"


def test_embeddings_rps_higher_than_responses(reliability_config):
    """Embeddings typically faster, should have higher RPS limit."""
    responses_rps = reliability_config["rate_limits"]["responses_rps"]
    embeddings_rps = reliability_config["rate_limits"]["embeddings_rps"]

    if embeddings_rps < responses_rps:
        pytest.skip(
            f"INFO: embeddings_rps ({embeddings_rps}) < responses_rps ({responses_rps}). "
            "Typically embeddings are faster and should have higher RPS."
        )


def test_backoff_max_delay_reasonable():
    """Ensure backoff doesn't result in excessive max delays."""
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    base_s = config["backoff"]["base_s"]
    factor = config["backoff"]["factor"]
    max_attempts = 5  # Typical max retry attempts

    # Calculate max delay (without jitter)
    max_delay_s = base_s * (factor ** (max_attempts - 1))

    assert max_delay_s <= 30.0, (
        f"Max backoff delay ({max_delay_s:.1f}s) exceeds 30s. "
        "Users may experience long hangs. Consider reducing base_s or factor."
    )


def test_config_documented():
    """Ensure reliability.yaml has comprehensive inline comments."""
    with open(CONFIG_PATH) as f:
        content = f.read()

    # Check for key documentation markers
    assert "Tuning Guidelines" in content, "Missing tuning guidelines in config"
    assert "milliseconds" in content.lower(), "Missing unit documentation"
    assert "default:" in content.lower(), "Missing default value documentation"


@pytest.mark.parametrize(
    "endpoint,min_rps",
    [
        ("responses", 5),  # Minimum viable RPS for consciousness streams
        ("embeddings", 10),  # Minimum viable RPS for embeddings
    ],
)
def test_minimum_rps_thresholds(reliability_config, endpoint, min_rps):
    """Ensure RPS limits meet minimum viable thresholds."""
    actual_rps = reliability_config["rate_limits"][f"{endpoint}_rps"]
    assert actual_rps >= min_rps, f"{endpoint}_rps ({actual_rps}) below minimum viable threshold ({min_rps})"


def test_config_production_ready():
    """Comprehensive production readiness check."""
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    issues = []

    # Check all required sections
    required_sections = ["timeouts", "backoff", "rate_limits"]
    for section in required_sections:
        if section not in config:
            issues.append(f"Missing required section: {section}")

    # Validate timeout values
    if "timeouts" in config:
        if config["timeouts"].get("connect_ms", 0) < 500:
            issues.append("connect_ms < 500ms may cause issues in cloud environments")
        if config["timeouts"].get("read_ms", 0) < SLO_E2E_MS * 2:
            issues.append(f"read_ms should be >= {SLO_E2E_MS * 2}ms for SLO compliance")

    # Validate backoff configuration
    if "backoff" in config:
        if config["backoff"].get("jitter", 0) == 0:
            issues.append("jitter=0 can cause thundering herd problems")

    if issues:
        pytest.fail("Production readiness issues:\n" + "\n".join(f"  - {i}" for i in issues))


# Integration test (requires running server)
@pytest.mark.integration
def test_config_applied_correctly():
    """Verify config is actually loaded by the application."""
    import requests

    try:
        # Make a request and check for rate limit headers
        response = requests.get("http://localhost:8000/health", timeout=5)

        # Check for rate limit headers (if implemented)
        if "X-RateLimit-Limit" in response.headers:
            limit = int(response.headers["X-RateLimit-Limit"])
            assert limit > 0, "Rate limit header present but invalid"

    except requests.exceptions.ConnectionError:
        pytest.skip("Server not running (expected for unit tests)")
