"""Backoff helpers for consensus/orchestration tests."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Iterator

__all__ = ["ExponentialBackoff", "sleep_with_backoff"]


@dataclass
class ExponentialBackoff:
    base: float = 0.1
    factor: float = 2.0
    max_sleep: float = 2.0
    max_retries: int = 5
    jitter: float = 0.1

    def sequence(self) -> Iterator[float]:
        delay = self.base
        for _ in range(self.max_retries):
            jitter_amount = delay * self.jitter
            yield min(self.max_sleep, max(0.0, random.uniform(delay - jitter_amount, delay + jitter_amount)))
            delay *= self.factor


def sleep_with_backoff(backoff: ExponentialBackoff) -> int:
    for idx, sleep_time in enumerate(backoff.sequence()):
        time.sleep(sleep_time)
    return idx + 1
