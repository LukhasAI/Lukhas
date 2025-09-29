# path: qi/learning/adaptive_engine.py
from __future__ import annotations

# Safe I/O
import builtins
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

_ORIG_OPEN = builtins.open
_ORIG_MAKEDIRS = os.makedirs

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
LEARN_DIR = os.path.join(STATE, "learning")
_ORIG_MAKEDIRS(LEARN_DIR, exist_ok=True)
EPISODES = os.path.join(LEARN_DIR, "episodes.jsonl")  # ring buffer of task runs
CANDIDATES = os.path.join(LEARN_DIR, "candidates.jsonl")  # proposed configs + scores

# Approvals & sandbox reuse
import contextlib

from qi.autonomy.self_healer import observe_signals


def _now() -> float:
    return time.time()


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass
class Episode:
    run_id: str
    task: str
    input_hash: str
    output_hash: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    reward: float  # normalized [0,1]
    ctx: dict[str, Any]
    ts: float


@dataclass
class CandidateConfig:
    id: str
    base_path: str  # config file to tweak (YAML/JSON)
    patch: dict[str, Any]  # structured change
    score_offline: float | None = None
    trials: int = 0
    meta: dict[str, Any] = None


class AdaptiveLearningEngine:
    """
    Continuously improves cognitive components based on experience.
    - Records episodes (task outcomes)
    - Analyzes patterns
    - Proposes candidate patches to config/routers
    - Offline-evaluates candidates on a holdout set
    - Surfaces proposals to HITL approver for apply
    """

    def record_episode(
        self,
        *,
        run_id: str,
        task: str,
        input_hash: str,
        output_hash: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: int,
        reward: float,
        ctx: dict[str, Any],
    ):
        ep = Episode(
            run_id,
            task,
            input_hash,
            output_hash,
            tokens_in,
            tokens_out,
            latency_ms,
            float(reward),
            ctx,
            _now(),
        )
        with _ORIG_OPEN(EPISODES, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(ep)) + "\n")

    def analyze_performance_patterns(self, *, window: int = 2000) -> dict[str, Any]:
        """Find task segments with below-target reward/latency patterns."""
        eps = self._tail(EPISODES, window)
        by_task: dict[str, list[Episode]] = {}
        for e in eps:
            by_task.setdefault(e["task"], []).append(e)
        stats = {}
        for t, arr in by_task.items():
            if not arr:
                continue
            r = [x["reward"] for x in arr]
            l = [x["latency_ms"] for x in arr if x.get("latency_ms") is not None]
            stats[t] = {
                "n": len(arr),
                "reward_mean": round(sum(r) / len(r), 4),
                "lat_p50": int(sorted(l)[len(l) // 2]) if l else None,
                "lat_p90": int(sorted(l)[int(0.9 * len(l)) - 1]) if l else None,
            }
        return {"by_task": stats, "window": window, "ts": _now()}

    def evolve_node_parameters(
        self, *, target_file: str, tasks_focus: list[str] | None = None
    ) -> list[CandidateConfig]:
        """
        Suggest numeric tweaks (e.g., router thresholds) based on low-reward tasks.
        """
        pat = self.analyze_performance_patterns()
        low = sorted(
            [(t, s["reward_mean"]) for t, s in pat["by_task"].items() if s["n"] >= 10],
            key=lambda x: x[1],
        )[:3]
        if tasks_focus:
            low = [x for x in low if x[0] in tasks_focus]
        cands: list[CandidateConfig] = []
        for t, _ in low:
            for delta in (-0.05, -0.02, 0.02, 0.05):
                patch = {"router": {"task_specific": {t: {"threshold": ("$add", delta)}}}}
                cid = _sha({"t": t, "delta": delta, "file": target_file, "ts": int(_now())})
                cands.append(
                    CandidateConfig(
                        id=cid,
                        base_path=target_file,
                        patch=patch,
                        meta={"task": t, "kind": "param_shift", "delta": delta},
                    )
                )
        self._queue_candidates(cands)
        return cands

    def discover_new_node_combinations(
        self, *, target_file: str, tasks_focus: list[str] | None = None
    ) -> list[CandidateConfig]:
        """
        Explore novel tool combos: try enabling backup tool or reranker for weak tasks.
        """
        pat = self.analyze_performance_patterns()
        low = sorted(
            [(t, s["reward_mean"]) for t, s in pat["by_task"].items() if s["n"] >= 10],
            key=lambda x: x[1],
        )[:3]
        if tasks_focus:
            low = [x for x in low if x[0] in tasks_focus]
        cands = []
        for t, _ in low:
            for tool in ("reranker", "web_search", "policy_explain"):
                patch = {"router": {"task_specific": {t: {"tools": {"enable": {tool: True}}}}}}
                cid = _sha({"t": t, "tool": tool, "file": target_file, "ts": int(_now())})
                cands.append(
                    CandidateConfig(
                        id=cid,
                        base_path=target_file,
                        patch=patch,
                        meta={"task": t, "kind": "tool_enable", "tool": tool},
                    )
                )
        self._queue_candidates(cands)
        return cands

    # ---------- Offline evaluation (toy scoring; plug in your judge here) ----------
    def offline_score(self, cand: CandidateConfig, *, holdout_n: int = 200) -> float:
        """
        Score a candidate against last N episodes of its focus task using a simple proxy:
        reward uplift estimate minus latency penalty. Replace with true judge.
        """
        eps = self._tail(EPISODES, holdout_n)
        t = cand.meta.get("task") if cand.meta else None
        sub = [e for e in eps if (t is None or e["task"] == t)]
        if not sub:
            return 0.0
        base_r = sum(e["reward"] for e in sub) / len(sub)
        # heuristic: param shift/tool enable => expect small uplift
        uplift = 0.02 if cand.meta.get("kind") == "param_shift" else 0.03
        score = max(0.0, min(1.0, base_r + uplift))
        return round(score, 6)

    def batch_offline_eval(self, *, top_k: int = 6) -> list[CandidateConfig]:
        cands = self._read_candidates()[-50:]
        ranked = []
        for c in cands:
            s = self.offline_score(CandidateConfig(**c))
            c["score_offline"] = s
            ranked.append(c)
        ranked.sort(key=lambda x: x.get("score_offline", 0), reverse=True)
        self._write_candidates(ranked)
        return [CandidateConfig(**x) for x in ranked[:top_k]]

    # ---------- Propose → Approve → Apply (HITL) ----------
    def propose_best(self, *, config_targets: list[str]) -> list[str]:
        """
        Send 1–3 top candidates through self_healer's governance/approval flow as config_patch proposals.
        """
        top = self.batch_offline_eval(top_k=3)
        # Merge patches per target (simple one-by-one for clarity)
        planned = []
        for cand in top:
            # self_healer.plan_proposals already computes a safe patch; we replace its patch with ours per target
            observe_signals()
            # We inject our specific candidate patch by temporarily writing a one-off plan around target
            from qi.autonomy.self_healer import (  # type: ignore
                ChangeProposal,
                _attest,
                _queue_proposal,
            )

            for tgt in config_targets:
                pid = _sha({"cand": cand.id, "tgt": tgt, "ts": int(_now())})
                prop = ChangeProposal(
                    id=pid,
                    ts=_now(),
                    author="system:adaptive",
                    risk="medium",
                    ttl_sec=3600,
                    kind="config_patch",
                    target_path=tgt,
                    current_checksum=None,
                    patch=cand.patch,
                    rationale=f"Adaptive candidate {cand.id} (offline={cand.score_offline})",
                )
                prop.attestation = (
                    _attest([{"phase": "adaptive", "candidate": asdict(cand)}]) if "_attest" in globals() else None
                )
                _queue_proposal(prop)
                planned.append(pid)
        return planned

    # ---------- Internals ----------
    def _tail(self, path: str, n: int) -> list[dict]:
        if not os.path.exists(path):
            return []
        sz = os.path.getsize(path)
        chunk = min(1024 * 1024, sz)
        with _ORIG_OPEN(path, "rb") as f:
            f.seek(max(0, sz - chunk))
            text = f.read().decode("utf-8", "ignore")
        lines = [x for x in text.strip().splitlines() if x.strip()][-n:]
        out = []
        for ln in lines:
            with contextlib.suppress(Exception):
                out.append(json.loads(ln))
        return out

    def _queue_candidates(self, cands: list[CandidateConfig]):
        with _ORIG_OPEN(CANDIDATES, "a", encoding="utf-8") as f:
            for c in cands:
                f.write(json.dumps(asdict(c)) + "\n")

    def _read_candidates(self) -> list[dict]:
        if not os.path.exists(CANDIDATES):
            return []
        return [
            json.loads(ln) for ln in _ORIG_OPEN(CANDIDATES, "r", encoding="utf-8").read().splitlines() if ln.strip()
        ]

    def _write_candidates(self, arr: list[dict]):
        tmp = CANDIDATES + ".tmp"
        with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
            for x in arr:
                f.write(json.dumps(x) + "\n")
        os.replace(tmp, CANDIDATES)
