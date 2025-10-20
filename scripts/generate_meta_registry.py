#!/usr/bin/env python3
"""T4/0.01% Meta-Registry Generator
Fuses MODULE_REGISTRY + coverage + benchmarks into single analytics source.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def lane_of(tags: list[str]) -> str:
    """Extract lane from tags."""
    for t in tags or []:
        if t.startswith("lane:"):
            return t.split(":")[1]
    return "L2"


def main():
    root = Path(".")
    registry_path = root / "docs/_generated/MODULE_REGISTRY.json"
    output_path = root / "docs/_generated/META_REGISTRY.json"

    if not registry_path.exists():
        print("❌ MODULE_REGISTRY.json not found. Run: python scripts/generate_module_registry.py")
        return 1

    # Load base registry
    registry = json.loads(registry_path.read_text())
    meta_modules = []

    for mod in registry["modules"]:
        module_name = mod["name"]
        manifest_path = root / mod["manifest"]

        # Load manifest for additional data
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception as e:
            print(f"⚠️  Failed to load manifest for {module_name}: {e}")
            manifest = {}

        # Extract coverage
        testing = manifest.get("testing") or {}
        coverage = testing.get("coverage_observed")
        coverage_target = testing.get("coverage_target")

        # Extract performance
        performance = manifest.get("performance") or {}
        observed = performance.get("observed") or {}
        bench_p50 = observed.get("latency_p50_ms")
        bench_p95 = observed.get("latency_p95_ms")
        bench_p99 = observed.get("latency_p99_ms")
        perf_observed_at = observed.get("observed_at")

        # Extract SLA targets
        sla_targets = performance.get("sla_targets") or {}
        sla_p95 = sla_targets.get("latency_p95_ms")

        # Build meta entry
        meta_entry = {
            "module": module_name,
            "path": mod["path"],
            "lane": lane_of(mod.get("tags", [])),
            "status": mod.get("status", "unknown"),
            "docs_count": len(mod.get("docs", [])),
            "tests_count": len(mod.get("tests", [])),
            "api_count": mod.get("api_count", 0),
            "tags": mod.get("tags", []),
        }

        # Add coverage if available
        if coverage is not None:
            meta_entry["coverage"] = {
                "observed": coverage,
                "target": coverage_target,
                "delta": round(coverage - coverage_target, 2) if coverage_target else None,
                "meets_target": coverage >= coverage_target if coverage_target else None,
            }

        # Add performance if available
        if any([bench_p50, bench_p95, bench_p99]):
            meta_entry["performance"] = {
                "latency_p50_ms": bench_p50,
                "latency_p95_ms": bench_p95,
                "latency_p99_ms": bench_p99,
                "sla_p95_ms": sla_p95,
                "meets_sla": bench_p95 <= sla_p95 if (bench_p95 and sla_p95) else None,
                "observed_at": perf_observed_at,
            }

        # Add health score (0-100)
        health_score = 0
        if coverage is not None:
            # Coverage contributes up to 50 points
            health_score += min(50, coverage / 2)
        if meta_entry.get("performance", {}).get("meets_sla"):
            # Meeting SLA adds 30 points
            health_score += 30
        if mod.get("docs", []):
            # Having docs adds 20 points
            health_score += 20

        meta_entry["health_score"] = round(health_score, 1)

        meta_modules.append(meta_entry)

    # Build meta registry
    meta_registry = {
        "schema_version": "1.0.0",
        "generated_at": utc(),
        "source_registry": str(registry_path.relative_to(root)),
        "module_count": len(meta_modules),
        "modules": sorted(meta_modules, key=lambda m: m["module"]),
        "summary": {
            "total_modules": len(meta_modules),
            "with_coverage": sum(1 for m in meta_modules if "coverage" in m),
            "with_benchmarks": sum(1 for m in meta_modules if "performance" in m),
            "meeting_coverage_target": sum(
                1 for m in meta_modules
                if m.get("coverage", {}).get("meets_target") is True
            ),
            "meeting_sla": sum(
                1 for m in meta_modules
                if m.get("performance", {}).get("meets_sla") is True
            ),
            "avg_health_score": round(
                sum(m["health_score"] for m in meta_modules) / len(meta_modules), 1
            ) if meta_modules else 0,
        },
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(meta_registry, indent=2) + "\n", encoding="utf-8")

    print("✅ Generated META_REGISTRY.json")
    print(f"   Location: {output_path}")
    print(f"   Modules: {meta_registry['module_count']}")
    print(f"   With coverage: {meta_registry['summary']['with_coverage']}")
    print(f"   With benchmarks: {meta_registry['summary']['with_benchmarks']}")
    print(f"   Avg health score: {meta_registry['summary']['avg_health_score']}/100")
    return 0


if __name__ == "__main__":
    exit(main())
