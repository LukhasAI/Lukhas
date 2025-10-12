from lukhas.core.reliability.backoff import jittered_exponential
from lukhas.core.reliability.ratelimit import rate_limit_error

def test_jittered_exponential_ranges():
    # attempt=3 => base_window * 2**3 +/- jitter
    lo, hi = jittered_exponential(base=0.1, factor=2, attempt=3, jitter=0.1)
    assert 0 < lo < hi
    assert hi/lo < 5  # bounded jitter

def test_rate_limit_shape_and_headers():
    err = rate_limit_error(retry_after_s=5)
    assert err["error"]["type"] == "rate_limit_exceeded"
    assert err["headers"]["Retry-After"] == "5"
