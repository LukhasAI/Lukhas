# path: qi/provenance/receipts_hub.py
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import streamlit as st

from consciousness.qi import qi
from qi.provenance.receipt_standard import build_receipt, to_json

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
OUT_DIR = os.path.join(STATE, "provenance", "exec_receipts")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- safe I/O (avoid sandbox recursion) ----
import builtins
import contextlib

_ORIG_OPEN = builtins.open


# ---- sinks (optional) ----
def _kafka():
    brokers = os.environ.get("RECEIPTS_KAFKA_BROKERS")
    topic = os.environ.get("RECEIPTS_KAFKA_TOPIC", "lukhas.provenance.receipts")
    if not brokers:
        return None, None
    try:
        from kafka import KafkaProducer  # pip install kafka-python
    except Exception as e:
        raise RuntimeError("Kafka sink requested but kafka-python not installed") from e
    prod = KafkaProducer(
        bootstrap_servers=brokers.split(","),
        acks="all",
        linger_ms=50,
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )
    return prod, topic


def _s3():
    bucket = os.environ.get("RECEIPTS_S3_BUCKET")
    prefix = os.environ.get("RECEIPTS_S3_PREFIX", "lukhas/provenance/exec/")
    if not bucket:
        return None, None
    try:
        import boto3  # pip install boto3
    except Exception as e:
        raise RuntimeError("S3 sink requested but boto3 not installed") from e
    cli = boto3.client("s3")
    return (cli, (bucket, prefix))


def _stable_key(d: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps({"id": d.get("id")}, sort_keys=True).encode()).hexdigest()


def emit_receipt(**kwargs) -> dict[str, Any]:
    """
    Build, persist locally, and push to configured sinks.
    Returns the JSON dict.

    Supports all build_receipt parameters including:
    - metrics: Dict with calibration data (raw_conf, calibrated_conf, temperature, etc.)
    - feedback_ref: Optional reference to feedback card ID
    - proposal_id: Optional reference to change proposal ID
    """
    r = build_receipt(**kwargs)
    data = to_json(r)

    # 1) local write (per-id JSON)
    path = os.path.join(OUT_DIR, f"{r.id}.json")
    with _ORIG_OPEN(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 2) Kafka (optional)
    prod, topic = _kafka()
    if prod:
        try:
            prod.send(topic, key=r.id, value=data)
            prod.flush(2.0)
        except Exception:
            pass

    # 3) S3 (optional)
    cli, s3cfg = _s3()
    if cli:
        bucket, prefix = s3cfg
        ymd = time.strftime("%Y%m%d", time.gmtime(data.get("created_at", time.time())))
        key = f"{prefix.rstrip('/')}/{ymd}/{r.id}.json"
        with contextlib.suppress(Exception):
            cli.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data).encode("utf-8"),
                ContentType="application/json",
            )

    return data


# --------- CLI ---------
def _generate_grafana(path: str):
    dash = {
        "title": "Lukhas • Exec Receipts (Longitudinal)",
        "refresh": "10s",
        "timezone": "",
        "schemaVersion": 38,
        "panels": [
            {
                "type": "row",
                "title": "Volume",
                "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0},
            },
            {
                "type": "timeseries",
                "title": "Receipts per second",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 1},
                "targets": [
                    {
                        "expr": 'rate(lukhas_http_requests_total{path="/provenance/:sha/stream"}[5m])',
                        "legendFormat": "streams",
                        "refId": "A",
                    }
                ],
            },
            {
                "type": "timeseries",
                "title": "Risk flags count (by kind)",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 1},
                "targets": [
                    {
                        "expr": "sum(rate(lukhas_prov_stream_requests_total[5m])) by (backend)",
                        "legendFormat": "{{backend}",
                        "refId": "A",
                    }
                ],
            },
            {
                "type": "row",
                "title": "Latency & Tokens",
                "gridPos": {"h": 1, "w": 24, "x": 0, "y": 9},
            },
            {
                "type": "stat",
                "title": "Median latency (ms)",
                "gridPos": {"h": 6, "w": 6, "x": 0, "y": 10},
                "targets": [
                    {
                        "expr": "histogram_quantile(0.5, sum(rate(lukhas_http_request_seconds_bucket[5m])) by (le))",
                        "refId": "A",
                    }
                ],
            },
            {
                "type": "timeseries",
                "title": "Tokens out (app view - wire your exporter)",
                "gridPos": {"h": 8, "w": 12, "x": 6, "y": 10},
                "targets": [{"expr": "0", "refId": "A"}],
            },
        ],
        "time": {"from": "now-6h", "to": "now"},
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _ORIG_OPEN(path, "w", encoding="utf-8") as f:
        json.dump(dash, f, indent=2)
    return path


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Lukhas Receipts Hub (Altman–Amodei–Hassabis)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("emit", help="Emit a single receipt from args (for testing)")
    e.add_argument("--artifact-sha", required=True)
    e.add_argument("--artifact-mime")
    e.add_argument("--artifact-size", type=int)
    e.add_argument("--storage-url")
    e.add_argument("--run-id", required=True)
    e.add_argument("--task", required=True)
    e.add_argument("--started", type=float, required=True)
    e.add_argument("--ended", type=float, required=True)
    e.add_argument("--user-id")
    e.add_argument("--jurisdiction")
    e.add_argument("--context")
    e.add_argument("--policy-id")
    e.add_argument("--consent-id")
    e.add_argument("--lease-id", action="append")
    e.add_argument("--risk-flag", action="append")
    e.add_argument("--tokens-in", type=int)
    e.add_argument("--tokens-out", type=int)
    e.add_argument("--metrics-json", help="JSON string with calibration metrics")

    def _run_emit(a):
        metrics = None
        if a.metrics_json:
            try:
                metrics = json.loads(a.metrics_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing metrics JSON: {e}", file=sys.stderr)
                return

        data = emit_receipt(
            artifact_sha=a.artifact_sha,
            artifact_mime=a.artifact_mime,
            artifact_size=a.artifact_size,
            storage_url=a.storage_url,
            run_id=a.run_id,
            task=a.task,
            started_at=a.started,
            ended_at=a.ended,
            user_id=a.user_id,
            jurisdiction=a.jurisdiction,
            context=a.context,
            policy_decision_id=a.policy_id,
            consent_receipt_id=a.consent_id,
            capability_lease_ids=a.lease_id or [],
            risk_flags=a.risk_flag or [],
            tokens_in=a.tokens_in,
            tokens_out=a.tokens_out,
            metrics=metrics,
        )
        print(json.dumps(data, indent=2))

    e.set_defaults(func=_run_emit)

    g = sub.add_parser("export-grafana", help="Write a starter Grafana dashboard JSON")
    g.add_argument(
        "--out",
        default=os.path.join("ops", "grafana", "lukhas_exec_receipts_dashboard.json"),
    )
    g.set_defaults(func=lambda a: print(_generate_grafana(a.out)))

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
