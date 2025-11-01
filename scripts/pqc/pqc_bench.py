#!/usr/bin/env python3
"""Dilithium2 signing/verification benchmark used by CI.

The script exercises liboqs via the python-oqs bindings and emits latency
statistics for Dilithium2 signature operations.  By default it enforces the
service level objectives that the sign p95 is below 50ms and the verify p95 is
below 10ms.  When the ``--json`` flag is supplied, the resulting metrics are
written as JSON so that GitHub Actions can parse them easily.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List

try:
    import oqs  # type: ignore
except ImportError as exc:  # pragma: no cover - import guard for CI diagnostics
    raise SystemExit(
        "python-oqs module is not available. Ensure liboqs and liboqs-python "
        "are installed on the runner."
    ) from exc


@dataclass(frozen=True)
class BenchmarkResult:
    """Container for the benchmark output."""

    algorithm: str
    iterations: int
    sign_p50: float
    sign_p95: float
    verify_p50: float
    verify_p95: float
    sign_threshold_ms: float
    verify_threshold_ms: float

    @property
    def sign_pass(self) -> bool:
        return self.sign_p95 < self.sign_threshold_ms

    @property
    def verify_pass(self) -> bool:
        return self.verify_p95 < self.verify_threshold_ms

    def to_json(self) -> str:
        payload = {
            "algorithm": self.algorithm,
            "iterations": self.iterations,
            "sign_p50": self.sign_p50,
            "sign_p95": self.sign_p95,
            "verify_p50": self.verify_p50,
            "verify_p95": self.verify_p95,
            "sign_threshold_ms": self.sign_threshold_ms,
            "verify_threshold_ms": self.verify_threshold_ms,
            "sign_pass": self.sign_pass,
            "verify_pass": self.verify_pass,
        }
        return json.dumps(payload, indent=2)


def percentile(values: Iterable[float], pct: float) -> float:
    data: List[float] = sorted(values)
    if not data:
        raise ValueError("cannot compute percentile of empty data")
    if pct <= 0:
        return data[0]
    if pct >= 100:
        return data[-1]

    k = (len(data) - 1) * pct / 100.0
    lower = math.floor(k)
    upper = math.ceil(k)
    if lower == upper:
        return data[int(k)]
    return data[lower] + (data[upper] - data[lower]) * (k - lower)


def bench(
    algorithm: str,
    iterations: int,
    sign_threshold_ms: float,
    verify_threshold_ms: float,
    message: bytes,
) -> BenchmarkResult:
    sign_timings: List[float] = []
    verify_timings: List[float] = []

    with oqs.Signature(algorithm) as sig:
        public_key = sig.generate_keypair()

        for _ in range(iterations):
            start = time.perf_counter()
            signature = sig.sign(message)
            sign_timings.append((time.perf_counter() - start) * 1000)

        for _ in range(iterations):
            start = time.perf_counter()
            is_valid = sig.verify(message, signature, public_key)
            verify_timings.append((time.perf_counter() - start) * 1000)
            if not is_valid:
                raise RuntimeError("signature verification failed")

    return BenchmarkResult(
        algorithm=algorithm,
        iterations=iterations,
        sign_p50=percentile(sign_timings, 50),
        sign_p95=percentile(sign_timings, 95),
        verify_p50=percentile(verify_timings, 50),
        verify_p95=percentile(verify_timings, 95),
        sign_threshold_ms=sign_threshold_ms,
        verify_threshold_ms=verify_threshold_ms,
    )


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--algorithm",
        default="Dilithium2",
        help="Signature algorithm to benchmark (default: %(default)s)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of sign/verify iterations (default: %(default)s)",
    )
    parser.add_argument(
        "--sign-threshold-ms",
        type=float,
        default=50.0,
        help="Sign p95 latency budget in milliseconds (default: %(default)s)",
    )
    parser.add_argument(
        "--verify-threshold-ms",
        type=float,
        default=10.0,
        help="Verify p95 latency budget in milliseconds (default: %(default)s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output for consumption by CI",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to write JSON output when --json is provided",
    )
    parser.add_argument(
        "--no-threshold-enforce",
        action="store_true",
        help="Do not exit with an error when thresholds are violated",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    result = bench(
        algorithm=args.algorithm,
        iterations=args.iterations,
        sign_threshold_ms=args.sign_threshold_ms,
        verify_threshold_ms=args.verify_threshold_ms,
        message=b"LUKHAS Dilithium2 benchmark payload",
    )

    if args.json:
        payload = result.to_json()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        print(payload)
    else:
        print(f"Benchmark results for {result.algorithm} ({result.iterations} iterations)")
        print(
            f"  Sign   - p50: {result.sign_p50:.2f}ms, "
            f"p95: {result.sign_p95:.2f}ms (budget < {result.sign_threshold_ms}ms)"
        )
        print(
            f"  Verify - p50: {result.verify_p50:.2f}ms, "
            f"p95: {result.verify_p95:.2f}ms (budget < {result.verify_threshold_ms}ms)"
        )
        print()
        print(f"  Sign threshold met:   {'yes' if result.sign_pass else 'no'}")
        print(f"  Verify threshold met: {'yes' if result.verify_pass else 'no'}")

    if args.no_threshold_enforce:
        return 0

    if not result.sign_pass or not result.verify_pass:
        print("Performance thresholds were not met", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main(sys.argv[1:]))
