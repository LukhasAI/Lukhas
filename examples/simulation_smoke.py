#!/usr/bin/env python3
"""
Smoke test for simulation lane.

Note: Current API doesn't use cap_token yet - that's a future enhancement.
This script demonstrates the current schedule → collect flow.
"""
import asyncio
import json
import os

# Ensure feature flag is set
os.environ["SIMULATION_ENABLED"] = "true"

from consciousness.simulation import api

seed = {
    "goal": "Assess ΛID onboarding scenarios",
    "context": {"tenant": "demo"},
    "constraints": {
        "budgets": {"tokens": 500, "seconds": 0.5},
        "consent": {"scopes": ["simulation.read_context"]},
        "flags": {"duress_active": False}
    }
}

async def main():
    # Schedule simulation
    job_id = await api.schedule(seed)
    print(f"✓ Scheduled job: {job_id}")

    # Check status
    status = await api.status(job_id)
    print(f"✓ Status: {status['state']}")

    # Collect results
    result = await api.collect(job_id)
    print(json.dumps({
        "trace_id": result["trace_id"],
        "shards": len(result.get("shards", [])),
        "matada_nodes": len(result.get("matada_nodes", [])),
        "scores": result.get("scores", {})
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
