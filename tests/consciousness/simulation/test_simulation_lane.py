import asyncio
import importlib
import inspect
import os

os.environ["SIMULATION_ENABLED"] = "true"
from consciousness.simulation import api


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

def _seed(consented: bool = True, duress: bool = False):
    scopes = ["simulation.read_context"] if consented else []
    return {
        "goal": "Evaluate onboarding flow for new ΛID users",
        "context": {"tenant": "demo", "redacted_user_count": 5},
        "constraints": {
            "budgets": {"tokens": 1500, "seconds": 1.0, "max_rollouts": 3},
            "consent": {"scopes": scopes},
            "flags": {"duress_active": duress},
        },
    }

def test_schedule_and_collect_happy_path():
    job_id = run(api.schedule(_seed()))
    st = run(api.status(job_id))
    assert st["state"] in ("queued", "running", "finished")
    result = run(api.collect(job_id))
    assert "shards" in result and len(result["shards"]) == 3
    assert result["scores"]["utility_mean"] > 0.6
    assert result["trace_id"].startswith("LT-")
    assert "matada_nodes" in result and len(result["matada_nodes"]) == 3
    assert all(n["id"].startswith(result["trace_id"]) for n in result["matada_nodes"])

def test_denies_without_consent():
    try:
        run(api.schedule(_seed(consented=False)))
        assert False, "Expected PolicyViolation"
    except api.PolicyViolation:
        pass

def test_denies_under_duress():
    try:
        run(api.schedule(_seed(duress=True)))
        assert False, "Expected PolicyViolation"
    except api.PolicyViolation:
        pass

def test_feature_flag_off_blocks():
    os.environ["SIMULATION_ENABLED"] = "false"
    try:
        run(api.schedule(_seed()))
        assert False, "Expected SimulationDisabledError"
    except api.SimulationDisabledError:
        pass
    finally:
        os.environ["SIMULATION_ENABLED"] = "true"

def test_no_adapter_imports():
    mod = importlib.import_module("consciousness.simulation.api")
    source = inspect.getsource(mod)
    forbidden = ["adapters.", "gmail_", "drive_", "dropbox_", "perplexity_", "openai_", "anthropic_", "gemini_"]
    assert not any(f in source for f in forbidden), "Adapter names found in simulation.api sources"
