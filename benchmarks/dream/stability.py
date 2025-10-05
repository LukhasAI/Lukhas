from __future__ import annotations

import json
import os
import pathlib
import statistics
import subprocess
import sys
from typing import Any, Dict, List

SEEDS = [1, 7, 13, 42, 123, 999]

def run_once(seed: int, out: str) -> None:
    """Run benchmark with specific seed."""
    env = os.environ.copy()
    env["LUKHAS_BENCH_SEED"] = str(seed)
    subprocess.check_call([sys.executable, "-m", "benchmarks.dream.run", "--out", out], env=env)

def load_results(path: str) -> List[Dict[str, Any]]:
    """Load results from JSONL file."""
    results = []
    if not pathlib.Path(path).exists():
        return results

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results

def analyze_stability(results_by_seed: Dict[int, List[Dict]]) -> Dict[str, Any]:
    """Analyze stability across seeds."""
    if not results_by_seed:
        return {"error": "No results to analyze"}

    # Group by strategy+objective
    grouped = {}
    for seed, results in results_by_seed.items():
        for result in results:
            key = f"{result['strategy']}_{result.get('use_objective', '0')}"
            if key not in grouped:
                grouped[key] = {}
            grouped[key][seed] = result

    stability_report = {}

    for config, seed_results in grouped.items():
        if len(seed_results) < 2:
            continue

        # Extract accuracy values across seeds
        accuracies = [r.get('accuracy', 0.0) for r in seed_results.values()]
        selected_names = [r.get('selected_name', '') for r in seed_results.values()]

        # Stability metrics
        acc_mean = statistics.mean(accuracies)
        acc_stdev = statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0
        acc_range = max(accuracies) - min(accuracies)

        # Selection consistency
        name_counts = {}
        for name in selected_names:
            name_counts[name] = name_counts.get(name, 0) + 1

        most_common_name = max(name_counts, key=name_counts.get) if name_counts else ""
        selection_consistency = name_counts.get(most_common_name, 0) / len(selected_names)

        stability_report[config] = {
            "seeds_tested": len(seed_results),
            "accuracy_mean": round(acc_mean, 4),
            "accuracy_stdev": round(acc_stdev, 4),
            "accuracy_range": round(acc_range, 4),
            "selection_consistency": round(selection_consistency, 4),
            "most_common_selection": most_common_name,
            "raw_accuracies": accuracies,
            "raw_selections": selected_names
        }

    return stability_report

def run_stability_test(out_dir: str = "benchmarks/dream/stability_results") -> str:
    """Run multi-seed stability test."""
    os.makedirs(out_dir, exist_ok=True)

    results_by_seed = {}

    print(f"Running stability test with {len(SEEDS)} seeds...")

    for i, seed in enumerate(SEEDS, 1):
        print(f"  Seed {seed} ({i}/{len(SEEDS)})")

        out_file = f"{out_dir}/results_seed_{seed}.jsonl"
        run_once(seed, out_file)

        results = load_results(out_file)
        results_by_seed[seed] = results

    # Analyze stability
    stability_report = analyze_stability(results_by_seed)

    # Save report
    report_path = f"{out_dir}/stability_report.json"
    with open(report_path, "w") as f:
        json.dump(stability_report, f, indent=2)

    print(f"Stability report saved to: {report_path}")
    return report_path

def print_stability_summary(report_path: str) -> None:
    """Print human-readable stability summary."""
    with open(report_path, "r") as f:
        report = json.load(f)

    print("\n=== STABILITY SUMMARY ===")
    for config, stats in report.items():
        if "error" in stats:
            print(f"{config}: {stats['error']}")
            continue

        print(f"\n{config}:")
        print(f"  Accuracy: {stats['accuracy_mean']:.3f} ± {stats['accuracy_stdev']:.3f} (range: {stats['accuracy_range']:.3f})")
        print(f"  Selection consistency: {stats['selection_consistency']:.1%}")
        print(f"  Most common: {stats['most_common_selection']}")

if __name__ == "__main__":
    report_path = run_stability_test()
    print_stability_summary(report_path)
