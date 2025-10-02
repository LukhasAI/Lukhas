from __future__ import annotations
import os, asyncio, uuid, logging, json
from typing import TypedDict, Optional, Dict, Any
from pathlib import Path

from .scheduler import SimulationScheduler, JobStatus
from .ethics_gate import authorize_or_raise, EthicsError
from .rollout import run_rollouts
from .summarizer import build_dream_result, build_matada_nodes

log = logging.getLogger("lukhas.consciousness.simulation")

class DreamSeed(TypedDict):
    goal: str
    context: Dict[str, Any]
    constraints: Dict[str, Any]

class DreamResult(TypedDict):
    shards: list[dict]
    scores: dict
    trace_id: str
    matada_nodes: list[dict]
    schema_ref: str

class SimulationDisabledError(RuntimeError): ...
class PolicyViolation(RuntimeError): ...

_scheduler: Optional[SimulationScheduler] = None

def _get_scheduler() -> SimulationScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SimulationScheduler()
    return _scheduler

def _require_enabled():
    if os.getenv("SIMULATION_ENABLED", "false").lower() not in ("1","true","yes","on"):
        raise SimulationDisabledError("Simulation lane disabled (SIMULATION_ENABLED is false).")

def _load_schema() -> dict:
    p = Path("schemas/matriz_node_v1.json")
    return json.loads(p.read_text()) if p.exists() else {"$id":"lukhas://schemas/matriz_node_v1.json","type":"object"}

def _jsonschema_validate(instance: dict, schema: dict) -> None:
    try:
        import jsonschema
        jsonschema.validate(instance=instance, schema=schema)
    except ModuleNotFoundError:
        # Soft-degrade if jsonschema not installed; CI should install it.
        log.warning("jsonschema not installed; MATADA validation skipped.")
    except Exception as e:
        raise PolicyViolation(f"MATADA node failed schema validation: {e}") from e

async def schedule(seed: DreamSeed) -> str:
    _require_enabled()
    try:
        authorize_or_raise(seed)
    except EthicsError as e:
        raise PolicyViolation(str(e)) from e

    job_id = str(uuid.uuid4())
    trace_id = f"LT-{job_id[:8]}"
    log.info("Λ-trace seed_scheduled", extra={"trace_id": trace_id, "goal": seed.get("goal")})
    await _get_scheduler().enqueue(job_id, seed, trace_id)
    return job_id

async def status(job_id: str) -> Dict[str, Any]:
    _require_enabled()
    s = _get_scheduler().get(job_id)
    if not s:
        return {"state": "unknown", "job_id": job_id}
    return s.model_dump()

async def collect(job_id: str) -> DreamResult:
    _require_enabled()
    s = _get_scheduler().get(job_id)
    if not s:
        raise KeyError(f"Unknown job_id: {job_id}")
    await _get_scheduler().wait(job_id)

    seed = s.seed
    trace_id = s.trace_id
    rollouts = await run_rollouts(seed, trace_id)

    # MATADA envelope: build nodes & validate against schema
    schema = _load_schema()
    nodes = build_matada_nodes(seed, rollouts, trace_id, schema_ref=schema.get("$id","lukhas://schemas/matriz_node_v1.json"))
    for n in nodes:
        _jsonschema_validate(n, schema)

    base = build_dream_result(seed, rollouts, trace_id)
    result: DreamResult = {
        **base,
        "matada_nodes": nodes,
        "schema_ref": schema.get("$id","lukhas://schemas/matriz_node_v1.json"),
    }
    log.info("Λ-trace seed_collected", extra={"trace_id": trace_id, "num_shards": len(result["shards"])})
    return result
