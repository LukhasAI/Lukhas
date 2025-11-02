    """
    Build, persist locally, and push to configured sinks.
    Returns the JSON dict.

    Supports all build_receipt parameters including:
    - metrics: Dict with calibration data (raw_conf, calibrated_conf, temperature, etc.)
    - feedback_ref: Optional reference to feedback card ID
    - proposal_id: Optional reference to change proposal ID
    """

from __future__ import annotations
import hashlib
import json
import os
import sys
import time
from typing import Any
from qi.provenance.receipt_standard import build_receipt, to_json
import builtins
import contextlib
        from kafka import KafkaProducer  # pip install kafka-python
        import boto3  # pip install boto3
        try:
    import argparse
            try:

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
OUT_DIR = os.path.join(STATE, "provenance", "exec_receipts")
os.makedirs(OUT_DIR, exist_ok=True)
_ORIG_OPEN = builtins.open
def _kafka():
    brokers = os.environ.get("RECEIPTS_KAFKA_BROKERS")
    topic = os.environ.get("RECEIPTS_KAFKA_TOPIC", "provenance.receipts")
    if not brokers:
        return None, None
    try:
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
    except Exception as e:
        raise RuntimeError("S3 sink requested but boto3 not installed") from e
    cli = boto3.client("s3")
    return (cli, (bucket, prefix))
def _stable_key(d: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps({"id": d.get("id")}, sort_keys=True).encode()).hexdigest()
def emit_receipt(**kwargs) -> dict[str, Any]:

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
