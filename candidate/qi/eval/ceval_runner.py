"""
Continuous Evaluation Loop (C-EVAL) for Lukhas.
- Weighted risk scoring
- CI/CD gate with strict exit codes
- Prometheus metrics (exporter)
- Drift check vs baseline
"""
import streamlit as st

from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any

import click

# Prometheus
try:
    from prometheus_client import Gauge, Histogram, start_http_server

    _PROM = True
except Exception:
    _PROM = False

EVALDIR = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs")
METRICS_PORT = int(os.environ.get("CEVAL_METRICS_PORT", "9109"))
Path(EVALDIR).mkdir(parents=True, exist_ok=True)

# ---------- Metrics ----------
if _PROM:
    CEVAL_MEAN = Gauge("lukhas_ceval_mean_score", "Mean score of last C-EVAL run", ["suite"])
    CEVAL_TASK = Gauge("lukhas_ceval_task_score", "Task score", ["suite", "task_id", "risk"])
    CEVAL_FAILS = Gauge("lukhas_ceval_failures", "Number of failed tasks", ["suite"])
    CEVAL_RUNTIME = Histogram("lukhas_ceval_runtime_seconds", "C-EVAL run time", ["suite"])
    CEVAL_DRIFT = Gauge("lukhas_ceval_drift_mean", "Mean drift vs baseline", ["suite"])


def _rand_score(seed: int, lo=0.7, hi=0.99) -> float:
    r = random.Random(seed)
    return lo + (hi - lo) * r.random()


class CEvalRunner:
    def __init__(self, suite_file: str):
        self.suite_file = suite_file
        self.suite = self._load_suite()

    def _load_suite(self) -> dict[str, Any]:
        with open(self.suite_file) as f:
            s = json.load(f)
        # defaults
        for t in s.get("tasks", []):
            t.setdefault("threshold", 0.8)
            t.setdefault("risk", "normal")  # normal|high|critical
            t.setdefault("weight", {"normal": 1.0, "high": 2.0, "critical": 3.0}[t["risk"]])
        s.setdefault("suite_id", Path(self.suite_file).stem)
        s.setdefault("sla", {"min_mean": 0.85, "max_failures": 0})
        return s

    def _execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Stub executor—replace with your real invoke + judge.
        """
        # Deterministic(ish) mock using task_id hash
        seed = int(hashlib.sha1(task["id"].encode()).hexdigest()[:8], 16) ^ int(time.time()) & 0xFFFF
        score = _rand_score(seed)
        return {
            "task_id": task["id"],
            "risk": task["risk"],
            "threshold": task["threshold"],
            "weight": task["weight"],
            "score": score,
            "pass": score >= task["threshold"],
            "ts": time.time(),
        }

    def run_suite(self) -> dict[str, Any]:
        start = time.time()
        suite_id = self.suite["suite_id"]
        results = [self._execute_task(t) for t in self.suite.get("tasks", [])]

        # Weighted aggregates
        wsum = sum(r["weight"] for r in results) or 1.0
        wmean = sum(r["score"] * r["weight"] for r in results) / wsum
        fails = [r for r in results if not r["pass"]]

        run = {
            "id": hashlib.sha1(f"{suite_id}:{start}".encode()).hexdigest()[:12],
            "suite_id": suite_id,
            "ts": start,
            "results": results,
            "summary": {
                "weighted_mean": round(wmean, 6),
                "failures": fails,
                "num_failures": len(fails),
                "sla": self.suite["sla"],
                "duration_sec": round(time.time() - start, 3),
            },
        }
        outf = os.path.join(EVALDIR, f"eval_{run['id']}.json")
        with open(outf, "w") as f:
            json.dump(run, f, indent=2)

        # Metrics
        if _PROM:
            CEVAL_MEAN.labels(suite=suite_id).set(wmean)
            CEVAL_FAILS.labels(suite=suite_id).set(len(fails))
            with CEVAL_RUNTIME.labels(suite=suite_id).time():
                pass  # we already measured; histogram increments with .time() context even if empty
            for r in results:
                CEVAL_TASK.labels(suite=suite_id, task_id=r["task_id"], risk=r["risk"]).set(r["score"])
        return run

    def drift_check(self, baseline_file: str) -> dict[str, Any]:
        latest = self._load_latest_eval()
        with open(baseline_file) as f:
            base = json.load(f)

        drift = {}
        base_map = {b["task_id"]: b for b in base["results"]}
        for r in latest["results"]:
            b = base_map.get(r["task_id"])
            if b:
                drift[r["task_id"]] = round(r["score"] - b["score"], 6)

        report = {
            "latest_id": latest["id"],
            "baseline_id": base["id"],
            "suite_id": latest["suite_id"],
            "drift": drift,
            "mean_drift": round(sum(drift.values()) / len(drift), 6) if drift else 0.0,
        }
        outf = os.path.join(EVALDIR, f"drift_{latest['id']}.json")
        with open(outf, "w") as f:
            json.dump(report, f, indent=2)
        if _PROM:
            CEVAL_DRIFT.labels(suite=latest["suite_id"]).set(report["mean_drift"])
        return report

    def _load_latest_eval(self) -> dict[str, Any]:
        files = sorted(Path(EVALDIR).glob("eval_*.json"), key=os.path.getmtime, reverse=True)
        if not files:
            raise RuntimeError("No eval runs found")
        with open(files[0]) as f:
            return json.load(f)

    @staticmethod
    def enforce_sla(run: dict[str, Any]) -> int:
        sla = run["summary"]["sla"]
        mean_ok = run["summary"]["weighted_mean"] >= sla.get("min_mean", 0.0)
        fails_ok = run["summary"]["num_failures"] <= sla.get("max_failures", 0)
        return 0 if (mean_ok and fails_ok) else 2  # 2 = fail build


# ---------- CLI ----------


@click.group()
@click.option("--metrics", is_flag=True, help="Expose Prometheus metrics on CEVAL_METRICS_PORT")
def cli(metrics: bool):
    if metrics and _PROM:
        start_http_server(METRICS_PORT)


@cli.command("run-suite")
@click.option("--suite", required=True, help="Path to suite JSON")
@click.option("--enforce-sla", is_flag=True, help="Exit non-zero if SLA violated")
def run_suite_cmd(suite, enforce_sla):
    runner = CEvalRunner(suite)
    run = runner.run_suite()
    click.echo(json.dumps(run, indent=2))
    if enforce_sla:
        raise SystemExit(CEvalRunner.enforce_sla(run))


@cli.command("drift-check")
@click.option("--baseline", required=True, help="Path to baseline eval JSON")
def drift_check_cmd(baseline):
    runner = CEvalRunner("dummy.json")
    rep = runner.drift_check(baseline)
    click.echo(json.dumps(rep, indent=2))


@cli.command("report")
def report_cmd():
    runner = CEvalRunner("dummy.json")
    latest = runner._load_latest_eval()
    click.echo(json.dumps(latest, indent=2))


if __name__ == "__main__":
    cli()
