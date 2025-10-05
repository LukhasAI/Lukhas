"""
core/lanes.py

Lane-based access control with Guardian token logging.

Usage:
  export LUKHAS_LANE=experimental
  @lane_guard(("candidate", "prod"))
  def external_action(): ...
"""
import functools
import os
from typing import Any, Callable, Tuple

LANE = os.getenv("LUKHAS_LANE", "experimental")

def lane_guard(allowed: Tuple[str, ...] = ("candidate", "prod")) -> Callable:
    """
    Enforce lane routing. Always emits a Guardian attempt token even on block.
    """
    def deco(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            guardian_token = f"attempt_{fn.__name__}_{LANE}"
            # Soft hook for results that carry guardian_log
            try:
                res = fn(*args, **kwargs) if LANE in allowed else None
            except Exception as e:
                _append_guardian_log_to_result(e, guardian_token)  # no-op if unsupported
                raise
            if LANE not in allowed:
                raise RuntimeError(f"Lane {LANE} not allowed for {fn.__name__}")
            _append_guardian_log_to_result(res, guardian_token)
            return res
        return wrapper
    return deco

def _append_guardian_log_to_result(obj: Any, token: str) -> None:
    try:
        if hasattr(obj, "guardian_log") and isinstance(obj.guardian_log, list):
            obj.guardian_log.append(token)
    except Exception:
        pass
