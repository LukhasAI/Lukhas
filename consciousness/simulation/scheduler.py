from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class JobStatus:
    job_id: str
    state: str
    trace_id: str
    created_ts: float
    started_ts: float | None = None
    finished_ts: float | None = None
    budget_tokens: int = 0
    budget_seconds: float = 0.0
    progress: float = 0.0
    seed: Dict[str, Any] = field(default_factory=dict)

    def model_dump(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "state": self.state,
            "trace_id": self.trace_id,
            "created_ts": self.created_ts,
            "started_ts": self.started_ts,
            "finished_ts": self.finished_ts,
            "budget_tokens": self.budget_tokens,
            "budget_seconds": self.budget_seconds,
            "progress": round(self.progress, 3),
        }

class SimulationScheduler:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobStatus] = {}
        self._events: Dict[str, asyncio.Event] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._runner_task: asyncio.Task | None = None

    async def enqueue(self, job_id: str, seed: Dict[str, Any], trace_id: str) -> None:
        budgets = seed.get("constraints", {}).get("budgets", {})
        js = JobStatus(
            job_id=job_id,
            state="queued",
            trace_id=trace_id,
            created_ts=time.time(),
            budget_tokens=int(budgets.get("tokens", 2000)),
            budget_seconds=float(budgets.get("seconds", 2.0)),
            seed=seed,
        )
        self._jobs[job_id] = js
        self._events[job_id] = asyncio.Event()
        await self._queue.put(job_id)
        if not self._runner_task or self._runner_task.done():
            self._runner_task = asyncio.create_task(self._runner())

    def get(self, job_id: str) -> JobStatus | None:
        return self._jobs.get(job_id)

    async def wait(self, job_id: str) -> None:
        ev = self._events.get(job_id)
        if ev:
            await ev.wait()

    async def _runner(self) -> None:
        while not self._queue.empty():
            job_id = await self._queue.get()
            js = self._jobs[job_id]
            js.state = "running"
            js.started_ts = time.time()
            await asyncio.sleep(min(0.02, js.budget_seconds / 10.0))
            js.progress = 1.0
            js.finished_ts = time.time()
            js.state = "finished"
            self._events[job_id].set()
