from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Optional

# Threshold sweep ranges
ALIGNMENT_THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
DRIFT_THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
CONFIDENCE_THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def run_with_thresholds(align_thresh: float, drift_thresh: float, conf_thresh: float, out: str) -> None:
    """Run benchmark with specific thresholds."""
    env = os.environ.copy()
    env["LUKHAS_BENCH_SEED"] = "42"  # Fixed seed for consistency
    env["LUKHAS_ALIGNMENT_THRESHOLD"] = str(align_thresh)
    env["LUKHAS_DRIFT_THRESHOLD"] = str(drift_thresh)
    env["LUKHAS_CONFIDENCE_THRESHOLD"] = str(conf_thresh)

    subprocess.check_call([sys.executable, "-m", "benchmarks.dream.run", "--out", out], env=env)

def load_results(path: str) -> List[Dict[str, Any]]:
    """Load results from JSONL file."""
    results = []
    if not pathlib.Path(path).exists():
        return results

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results

def evaluate_threshold_performance(results: List[Dict]) -> Dict[str, float]:
    """Evaluate performance metrics for given results."""
    if not results:
        return {"accuracy": 0.0, "coverage": 0.0, "avg_latency": 0.0}

    # Calculate metrics similar to score.py
    total_accuracy = 0.0
    total_coverage = 0.0
    total_latency = 0.0

    for result in results:
        total_accuracy += result.get('accuracy', 0.0)
        total_coverage += result.get('coverage>=0.5', 0.0)
        total_latency += result.get('p50_ms', 0.0)

    count = len(results)
    return {
        "accuracy": total_accuracy / count,
        "coverage": total_coverage / count,
        "avg_latency": total_latency / count,
        "count": count
    }

def run_threshold_sweep(out_dir: str = "benchmarks/dream/calibration_results") -> str:
    """Run comprehensive threshold sweep."""
    os.makedirs(out_dir, exist_ok=True)

    sweep_results = {}
    total_configs = len(ALIGNMENT_THRESHOLDS) * len(DRIFT_THRESHOLDS) * len(CONFIDENCE_THRESHOLDS)

    print(f"Running threshold sweep: {total_configs} configurations...")

    config_num = 0
    for align_thresh in ALIGNMENT_THRESHOLDS:
        for drift_thresh in DRIFT_THRESHOLDS:
            for conf_thresh in CONFIDENCE_THRESHOLDS:
                config_num += 1
                config_key = f"align_{align_thresh}_drift_{drift_thresh}_conf_{conf_thresh}"

                print(f"  Config {config_num}/{total_configs}: {config_key}")

                out_file = f"{out_dir}/results_{config_key}.jsonl"

                try:
                    run_with_thresholds(align_thresh, drift_thresh, conf_thresh, out_file)
                    results = load_results(out_file)
                    performance = evaluate_threshold_performance(results)

                    sweep_results[config_key] = {
                        "alignment_threshold": align_thresh,
                        "drift_threshold": drift_thresh,
                        "confidence_threshold": conf_thresh,
                        "performance": performance
                    }
                except Exception as e:
                    print(f"    ERROR: {e}")
                    sweep_results[config_key] = {
                        "alignment_threshold": align_thresh,
                        "drift_threshold": drift_thresh,
                        "confidence_threshold": conf_thresh,
                        "error": str(e)
                    }

    # Save sweep results
    report_path = f"{out_dir}/threshold_sweep.json"
    with open(report_path, "w") as f:
        json.dump(sweep_results, f, indent=2)

    print(f"Threshold sweep report saved to: {report_path}")
    return report_path

def find_optimal_thresholds(report_path: str, metric: str = "accuracy") -> Dict[str, Any]:
    """Find optimal thresholds based on specified metric."""
    with open(report_path) as f:
        sweep_results = json.load(f)

    best_config = None
    best_score = -1.0

    for config_key, config_data in sweep_results.items():
        if "error" in config_data:
            continue

        performance = config_data.get("performance", {})
        score = performance.get(metric, 0.0)

        if score > best_score:
            best_score = score
            best_config = config_data

    return {
        "best_config": best_config,
        "best_score": best_score,
        "optimization_metric": metric
    }

def calibration_report(sweep_path: str, out_path: Optional[str] = None) -> str:
    """Generate calibration report with recommendations."""
    if out_path is None:
        out_path = sweep_path.replace(".json", "_report.json")

    # Find optimal configurations for different metrics
    optimal_configs = {}
    for metric in ["accuracy", "coverage", "avg_latency"]:
        optimal_configs[metric] = find_optimal_thresholds(sweep_path, metric)

    # Generate recommendations
    accuracy_config = optimal_configs["accuracy"]["best_config"]

    recommendations = {
        "production_recommended": {
            "alignment_threshold": accuracy_config["alignment_threshold"] if accuracy_config else 0.5,
            "drift_threshold": accuracy_config["drift_threshold"] if accuracy_config else 0.3,
            "confidence_threshold": accuracy_config["confidence_threshold"] if accuracy_config else 0.7,
            "rationale": "Optimized for accuracy while maintaining reasonable coverage"
        },
        "conservative_fallback": {
            "alignment_threshold": 0.3,
            "drift_threshold": 0.5,
            "confidence_threshold": 0.5,
            "rationale": "Safe defaults for uncertain environments"
        },
        "optimal_by_metric": optimal_configs
    }

    with open(out_path, "w") as f:
        json.dump(recommendations, f, indent=2)

    print(f"Calibration report saved to: {out_path}")
    return out_path

def print_calibration_summary(report_path: str) -> None:
    """Print human-readable calibration summary."""
    with open(report_path) as f:
        report = json.load(f)

    print("\n=== CALIBRATION SUMMARY ===")

    prod_rec = report["production_recommended"]
    print("\nProduction Recommended:")
    print(f"  Alignment: {prod_rec['alignment_threshold']}")
    print(f"  Drift: {prod_rec['drift_threshold']}")
    print(f"  Confidence: {prod_rec['confidence_threshold']}")
    print(f"  Rationale: {prod_rec['rationale']}")

    print("\nOptimal by Metric:")
    for metric, config in report["optimal_by_metric"].items():
        if config["best_config"]:
            best = config["best_config"]
            print(f"  {metric.capitalize()}: score={config['best_score']:.3f}")
            print(f"    align={best['alignment_threshold']}, drift={best['drift_threshold']}, conf={best['confidence_threshold']}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sweep":
        sweep_path = run_threshold_sweep()
        report_path = calibration_report(sweep_path)
        print_calibration_summary(report_path)
    else:
        print("Usage: python -m benchmarks.dream.calibration --sweep")
        print("Note: This will run a comprehensive threshold sweep (729 configurations)")
