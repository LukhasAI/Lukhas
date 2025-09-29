# tests/ethics/test_tags_preprocess.py
import os, time, math, pytest
from hypothesis import given, strategies as st
from lukhas.core.ethics.safety_tags import preprocess_text

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff")

# --- 10-line Hypothesis property: idempotence + zero-width stripping ---
@given(st.text())
def test_preprocess_idempotent_and_strips_zerowidth(s):
    t1 = preprocess_text(s)
    t2 = preprocess_text(t1)
    assert t1 == t2                    # idempotent
    assert not any(c in t1 for c in ZERO_WIDTH)  # zero-width removed

# --- Tiny perf microbenchmark (opt-in to avoid flaky CI) ---
@pytest.mark.skipif(os.getenv("LUKHAS_PERF") != "1", reason="set LUKHAS_PERF=1 to run perf check")
def test_preprocess_p95_lt_0_5ms():
    base = (
        "john(dot)doe(at)example(dot)com "
        "j\u200bohn.d\u200boe@examp\u200ble.com "
        "vision endpoint https://api.svc/v1/upload "
    )
    samples = []
    for _ in range(300):                  # small, stable sample
        s = base * 3                      # modestly sized worst-ish case
        t0 = time.perf_counter()
        preprocess_text(s)
        samples.append(time.perf_counter() - t0)
    samples.sort()
    p95 = samples[math.ceil(0.95 * len(samples)) - 1]
    assert p95 < 5e-4                     # 0.5 ms per call (conservative CI-safe ceiling)