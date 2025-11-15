#!/usr/bin/env python3
"""
ABAS Middleware Performance Benchmark

Tests ABAS middleware performance under various load conditions.
Measures p50, p95, p99 latency with cache hits/misses.

Usage:
    python scripts/benchmark_abas.py --rps 100 --duration 30
    python scripts/benchmark_abas.py --scenario pii-heavy --duration 60
    python scripts/benchmark_abas.py --profile cache-effectiveness

Requirements:
    pip install httpx rich

Results are saved to: benchmarks/abas_benchmark_TIMESTAMP.json
"""

import argparse
import asyncio
import json
import os
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("⚠️  Missing dependencies. Install with: pip install httpx rich")
    exit(1)

console = Console()


class ABASBenchmark:
    """Performance benchmark for ABAS middleware."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []

    async def measure_request(
        self,
        client: httpx.AsyncClient,
        path: str,
        payload: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Measure latency for a single request."""
        start = time.perf_counter()

        try:
            if payload:
                response = await client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=headers or {}
                )
            else:
                response = await client.get(
                    f"{self.base_url}{path}",
                    headers=headers or {}
                )

            latency_ms = (time.perf_counter() - start) * 1000

            return {
                "latency_ms": latency_ms,
                "status_code": response.status_code,
                "success": response.status_code < 500,
                "cached": "X-Cache-Hit" in response.headers  # If you add this header
            }

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return {
                "latency_ms": latency_ms,
                "status_code": 0,
                "success": False,
                "error": str(e)
            }

    async def run_scenario(
        self,
        scenario: str,
        rps: int,
        duration: int,
        client: httpx.AsyncClient
    ):
        """Run a specific benchmark scenario."""
        scenarios = {
            "clean": {
                "path": "/v1/responses",
                "payload": {"text": "Looking for tech news"},
                "headers": {"X-Region": "US", "Content-Type": "application/json"}
            },
            "pii-heavy": {
                "path": "/v1/responses",
                "payload": {"text": "I am gay and need support"},
                "headers": {"X-Region": "EU", "Content-Type": "application/json"}
            },
            "eu-consent": {
                "path": "/v1/responses",
                "payload": {"text": "Show me ads"},
                "headers": {
                    "X-Region": "EU",
                    "X-Targeting-Mode": "personalized",
                    "Content-Type": "application/json"
                }
            },
            "non-sensitive": {
                "path": "/healthz",
                "payload": None,
                "headers": {}
            }
        }

        if scenario not in scenarios:
            console.print(f"[red]Unknown scenario: {scenario}[/red]")
            return

        config = scenarios[scenario]
        interval = 1.0 / rps  # Time between requests
        end_time = time.time() + duration

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Running {scenario} @ {rps} RPS for {duration}s...",
                total=duration
            )

            start_time = time.time()
            request_count = 0

            while time.time() < end_time:
                result = await self.measure_request(
                    client,
                    config["path"],
                    config.get("payload"),
                    config.get("headers")
                )
                self.results.append(result)
                request_count += 1

                # Sleep to maintain RPS
                elapsed = time.time() - start_time
                target_time = request_count * interval
                sleep_time = max(0, target_time - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Update progress
                progress.update(task, completed=int(time.time() - start_time))

    def analyze_results(self) -> Dict:
        """Analyze benchmark results and compute statistics."""
        if not self.results:
            return {}

        latencies = [r["latency_ms"] for r in self.results]
        successes = [r for r in self.results if r["success"]]
        failures = [r for r in self.results if not r["success"]]

        status_codes = {}
        for r in self.results:
            code = r["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

        return {
            "total_requests": len(self.results),
            "successful_requests": len(successes),
            "failed_requests": len(failures),
            "success_rate": len(successes) / len(self.results) * 100,
            "latency": {
                "min": min(latencies),
                "max": max(latencies),
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "p50": statistics.median(latencies),
                "p95": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
                "p99": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
                "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "status_codes": status_codes
        }

    def print_results(self, analysis: Dict, scenario: str):
        """Print benchmark results in a nice table."""
        console.print(f"\n[bold cyan]Benchmark Results: {scenario}[/bold cyan]\n")

        # Summary table
        summary_table = Table(title="Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Total Requests", str(analysis["total_requests"]))
        summary_table.add_row("Successful", f"{analysis['successful_requests']} ({analysis['success_rate']:.1f}%)")
        summary_table.add_row("Failed", str(analysis["failed_requests"]))

        console.print(summary_table)

        # Latency table
        latency_table = Table(title="Latency (ms)")
        latency_table.add_column("Percentile", style="cyan")
        latency_table.add_column("Latency (ms)", style="magenta")
        latency_table.add_column("Target", style="green")
        latency_table.add_column("Status", style="yellow")

        lat = analysis["latency"]

        def check_target(value, target):
            return "✅" if value <= target else "❌"

        latency_table.add_row("Minimum", f"{lat['min']:.2f}", "-", "")
        latency_table.add_row("Mean", f"{lat['mean']:.2f}", "-", "")
        latency_table.add_row("Median (p50)", f"{lat['p50']:.2f}", "< 10ms", check_target(lat['p50'], 10))
        latency_table.add_row("p95", f"{lat['p95']:.2f}", "< 20ms", check_target(lat['p95'], 20))
        latency_table.add_row("p99", f"{lat['p99']:.2f}", "< 50ms", check_target(lat['p99'], 50))
        latency_table.add_row("Maximum", f"{lat['max']:.2f}", "-", "")
        latency_table.add_row("Std Dev", f"{lat['stdev']:.2f}", "-", "")

        console.print(latency_table)

        # Status codes table
        status_table = Table(title="Status Codes")
        status_table.add_column("Code", style="cyan")
        status_table.add_column("Count", style="magenta")
        status_table.add_column("Percentage", style="yellow")

        for code, count in sorted(analysis["status_codes"].items()):
            pct = count / analysis["total_requests"] * 100
            status_table.add_row(str(code), str(count), f"{pct:.1f}%")

        console.print(status_table)

    def save_results(self, analysis: Dict, scenario: str, args: argparse.Namespace):
        """Save benchmark results to JSON file."""
        output_dir = Path("benchmarks")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"abas_benchmark_{scenario}_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "scenario": scenario,
            "configuration": {
                "rps": args.rps,
                "duration": args.duration,
                "base_url": self.base_url
            },
            "analysis": analysis,
            "raw_results": self.results
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        console.print(f"\n💾 Results saved to: [cyan]{output_file}[/cyan]")


async def main():
    parser = argparse.ArgumentParser(description="ABAS Middleware Performance Benchmark")
    parser.add_argument("--rps", type=int, default=50, help="Requests per second (default: 50)")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    parser.add_argument("--scenario", default="clean",
                        choices=["clean", "pii-heavy", "eu-consent", "non-sensitive", "all"],
                        help="Benchmark scenario (default: clean)")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")

    args = parser.parse_args()

    console.print("[bold green]ABAS Middleware Performance Benchmark[/bold green]")
    console.print(f"Configuration: {args.rps} RPS for {args.duration}s")
    console.print(f"Base URL: {args.base_url}\n")

    # Check if API is available
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{args.base_url}/healthz")
            if response.status_code != 200:
                console.print(f"[yellow]⚠️  API health check returned {response.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ API not available at {args.base_url}: {e}[/red]")
        console.print("\nMake sure API is running:")
        console.print("  docker compose -f docker-compose.abas.yml up")
        console.print("  OR")
        console.print("  export ABAS_ENABLED=true && uvicorn serve.main:app --port 8000")
        return

    scenarios = [args.scenario] if args.scenario != "all" else ["clean", "pii-heavy", "eu-consent", "non-sensitive"]

    async with httpx.AsyncClient(timeout=args.timeout) as client:
        for scenario in scenarios:
            benchmark = ABASBenchmark(args.base_url)
            await benchmark.run_scenario(scenario, args.rps, args.duration, client)
            analysis = benchmark.analyze_results()
            benchmark.print_results(analysis, scenario)
            benchmark.save_results(analysis, scenario, args)

            if scenario != scenarios[-1]:
                console.print("\n" + "="*70 + "\n")
                await asyncio.sleep(2)  # Cool down between scenarios

    console.print("\n[bold green]✅ Benchmark complete![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
