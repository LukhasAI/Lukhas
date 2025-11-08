def jittered_exponential(
    base: float, factor: float, attempt: int, jitter: float = 0.1
) -> tuple[float, float]:
    window = base * (factor**attempt)
    lo = max(0.0, window * (1 - jitter))
    hi = window * (1 + jitter)
    return lo, hi
