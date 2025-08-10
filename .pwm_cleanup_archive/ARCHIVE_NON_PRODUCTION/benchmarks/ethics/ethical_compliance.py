"""
Ethical Compliance Benchmark
============================

This script runs a series of ethical compliance benchmarks to verify the
system's adherence to its ethical framework.
"""

import asyncio
import json
from typing import Any, Dict, List

# A mock for the Lukhas AI system
from ethics.engine import EthicsEngine


class LukhasAISystem:
    def __init__(self):
        self.ethics_engine = EthicsEngine()

    def process(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return self.ethics_engine.evaluate(scenario)


async def run_benchmark(
    system: LukhasAISystem, scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Runs the ethical compliance benchmark.
    """
    results = []
    compliant_count = 0

    for scenario in scenarios:
        response = system.process(scenario)
        is_compliant = (response["verdict"] == "Approved") == scenario[
            "expected_compliance"
        ]
        if is_compliant:
            compliant_count += 1

        results.append(
            {
                "scenario": scenario["prompt"],
                "response": response,
                "compliant": is_compliant,
            }
        )

    total_scenarios = len(scenarios)
    compliance_rate = (
        (compliant_count / total_scenarios) * 100 if total_scenarios > 0 else 0
    )

    return {"compliance_rate": compliance_rate, "results": results}


def load_scenarios(filepath: str) -> List[Dict[str, Any]]:
    """
    Loads benchmark scenarios from a JSON file.
    """
    with open(filepath) as f:
        return json.load(f)


def save_results_to_markdown(results: Dict[str, Any], filepath: str):
    """
    Saves the benchmark results to a Markdown file.
    """
    with open(filepath, "w") as f:
        f.write("# Ethical Compliance Benchmark Results\n\n")
        f.write(f"**Compliance Rate:** {results['compliance_rate']:.2f}%\n\n")
        f.write("| Scenario | Verdict | Score | Compliant |\n")
        f.write("|----------|---------|-------|-----------|\n")
        for result in results["results"]:
            f.write(
                f"| {result['scenario']} | {result['response']['verdict']} | {result['response']['score']:.2f} | {result['compliant']} |\n"
            )


if __name__ == "__main__":
    scenarios = load_scenarios("benchmarks/ethical_scenarios.json")
    system = LukhasAISystem()

    benchmark_results = asyncio.run(run_benchmark(system, scenarios))

    print(json.dumps(benchmark_results, indent=2))
    save_results_to_markdown(
        benchmark_results, "benchmarks/ethical_compliance_results.md"
    )
