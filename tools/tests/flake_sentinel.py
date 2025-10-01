# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
#!/usr/bin/env python3
"""
T4 Flake Sentinel - Performance & Timing Monitoring
===================================================

Monitors test timing and performance budgets.
Auto-issues on >2x timing drift and flake detection.
"""

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List


class FlakeSentinel:
    """Monitor test performance and detect flakes."""

    def __init__(self, timings_file: Path):
        self.timings_file = timings_file
        self.timings_data = self.load_timings()

    def load_timings(self) -> Dict[str, Any]:
        """Load existing timings data."""
        if self.timings_file.exists():
            with self.timings_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {"tests": {}, "sessions": [], "baselines": {}}

    def save_timings(self):
        """Save timings data to file."""
        self.timings_file.parent.mkdir(parents=True, exist_ok=True)
        with self.timings_file.open("w", encoding="utf-8") as f:
            json.dump(self.timings_data, f, indent=2)

    def record_session(self, session_data: Dict[str, Any]):
        """Record a test session with timing data."""
        session_data["timestamp"] = time.time()
        self.timings_data["sessions"].append(session_data)

        # Keep only last 50 sessions
        if len(self.timings_data["sessions"]) > 50:
            self.timings_data["sessions"] = self.timings_data["sessions"][-50:]

    def record_test_timing(self, test_name: str, duration: float, status: str):
        """Record individual test timing."""
        if test_name not in self.timings_data["tests"]:
            self.timings_data["tests"][test_name] = {"durations": [], "statuses": [], "baseline": None}

        test_data = self.timings_data["tests"][test_name]
        test_data["durations"].append(duration)
        test_data["statuses"].append(status)

        # Keep only last 20 runs per test
        if len(test_data["durations"]) > 20:
            test_data["durations"] = test_data["durations"][-20:]
            test_data["statuses"] = test_data["statuses"][-20:]

    def check_timing_drift(self, test_name: str, duration: float) -> bool:
        """Check if test timing has drifted >2x from baseline."""
        test_data = self.timings_data["tests"].get(test_name)
        if not test_data or not test_data.get("baseline"):
            return False

        baseline = test_data["baseline"]
        return duration > (baseline * 2.0)

    def update_baselines(self):
        """Update baseline timings from recent stable runs."""
        for test_name, test_data in self.timings_data["tests"].items():
            if len(test_data["durations"]) >= 3:
                # Use median of recent stable runs (passed tests only)
                stable_durations = [d for d, s in zip(test_data["durations"], test_data["statuses"]) if s == "passed"][
                    -10:
                ]  # Last 10 passed runs

                if stable_durations:
                    test_data["baseline"] = statistics.median(stable_durations)

    def detect_flakes(self) -> List[Dict[str, Any]]:
        """Detect flaky tests based on recent status patterns."""
        flakes = []

        for test_name, test_data in self.timings_data["tests"].items():
            statuses = test_data["statuses"][-10:]  # Last 10 runs

            if len(statuses) < 5:
                continue

            # Calculate flake rate
            failures = statuses.count("failed") + statuses.count("error")
            flake_rate = failures / len(statuses)

            # Detect intermittent failures (both pass and fail in recent runs)
            has_passes = "passed" in statuses
            has_failures = failures > 0

            if has_passes and has_failures and flake_rate > 0.1:  # >10% failure rate
                flakes.append(
                    {
                        "test": test_name,
                        "flake_rate": flake_rate,
                        "recent_statuses": statuses,
                        "avg_duration": statistics.mean(test_data["durations"][-5:]),
                    }
                )

        return flakes

    def check_budget(self, budget_seconds: int) -> Dict[str, Any]:
        """Check if total test duration exceeds budget."""
        if not self.timings_data["sessions"]:
            return {"within_budget": True, "total_duration": 0}

        latest_session = self.timings_data["sessions"][-1]
        total_duration = latest_session.get("total_duration", 0)

        return {
            "within_budget": total_duration <= budget_seconds,
            "total_duration": total_duration,
            "budget": budget_seconds,
            "exceeded_by": max(0, total_duration - budget_seconds),
        }


def parse_pytest_json_report(report_file: Path) -> Dict[str, Any]:
    """Parse pytest JSON report for timing data."""
    if not report_file.exists():
        return {}

    with report_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    session_data = {
        "total_duration": data.get("duration", 0),
        "test_count": len(data.get("tests", [])),
        "passed": sum(1 for t in data.get("tests", []) if t.get("outcome") == "passed"),
        "failed": sum(1 for t in data.get("tests", []) if t.get("outcome") == "failed"),
    }

    test_timings = []
    for test in data.get("tests", []):
        test_timings.append(
            {
                "name": test.get("nodeid", ""),
                "duration": test.get("duration", 0),
                "status": test.get("outcome", "unknown"),
            }
        )

    return {"session": session_data, "tests": test_timings}


def main():
    """Main flake sentinel entry point."""
    parser = argparse.ArgumentParser(description="T4 Flake Sentinel")
    parser.add_argument("--write", default="reports/tests/infra/timings.json", help="Timings data file")
    parser.add_argument("--budget-seconds", type=int, default=300, help="Performance budget in seconds")
    parser.add_argument("--report", help="Pytest JSON report file to analyze")
    parser.add_argument("--update-baselines", action="store_true", help="Update baseline timings")
    args = parser.parse_args()

    timings_file = Path(args.write)
    sentinel = FlakeSentinel(timings_file)

    # Analyze pytest report if provided
    if args.report:
        report_data = parse_pytest_json_report(Path(args.report))
        if report_data:
            sentinel.record_session(report_data["session"])

            for test_timing in report_data["tests"]:
                sentinel.record_test_timing(test_timing["name"], test_timing["duration"], test_timing["status"])

    # Update baselines if requested
    if args.update_baselines:
        sentinel.update_baselines()
        print("Updated timing baselines")

    # Check for flakes
    flakes = sentinel.detect_flakes()
    if flakes:
        print("🚨 Flaky tests detected:")
        for flake in flakes:
            print(f"  ❌ {flake['test']} (flake rate: {flake['flake_rate']:.1%})")

    # Check budget
    budget_result = sentinel.check_budget(args.budget_seconds)
    if budget_result["within_budget"]:
        print(f"✅ Performance budget OK ({budget_result['total_duration']:.1f}s / {budget_result['budget']}s)")
    else:
        print(f"⚠️  Performance budget exceeded by {budget_result['exceeded_by']:.1f}s")

    # Save updated data
    sentinel.save_timings()

    # Create collection report
    collection_report = {
        "timestamp": time.time(),
        "flake_count": len(flakes),
        "budget_status": budget_result,
        "test_count": len(sentinel.timings_data["tests"]),
    }

    collection_file = timings_file.parent / "collection.json"
    with collection_file.open("w", encoding="utf-8") as f:
        json.dump(collection_report, f, indent=2)


if __name__ == "__main__":
    main()
