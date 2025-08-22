# path: qi/safety/receipts_sink.py
from __future__ import annotations
import os, sys, time, json, glob, hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, Iterable

STATE_DIR = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECEIPTS_DIR = os.path.join(STATE_DIR, "provenance", "receipts")
OFFSETS_PATH = os.path.join(STATE_DIR, "provenance", "receipts_offsets.json")

# ---------- Optional Kafka ----------
def _maybe_kafka_producer():
    brokers = os.environ.get("RECEIPTS_KAFKA_BROKERS")
    if not brokers:
        return None
    try:
        from kafka import KafkaProducer  # pip install kafka-python
    except Exception as e:
        raise RuntimeError("Kafka sink requested but kafka-python not installed: pip install kafka-python") from e
    return KafkaProducer(
        bootstrap_servers=brokers.split(","),
        acks="all",
        linger_ms=50,
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        api_version_auto_timeout_ms=5000,
    )

# ---------- Optional S3 ----------
def _maybe_s3_client():
    bucket = os.environ.get("RECEIPTS_S3_BUCKET")
    if not bucket:
        return None
    try:
        import boto3  # pip install boto3
    except Exception as e:
        raise RuntimeError("S3 sink requested but boto3 not installed: pip install boto3") from e
    client = boto3.client("s3")
    return client

@dataclass
class SinkConfig:
    kafka_topic: Optional[str]
    s3_bucket: Optional[str]
    s3_prefix: str

def _load_offsets() -> Dict[str, int]:
    try:
        return json.load(open(OFFSETS_PATH, "r", encoding="utf-8"))
    except Exception:
        return {}

def _save_offsets(ofs: Dict[str, int]):
    os.makedirs(os.path.dirname(OFFSETS_PATH), exist_ok=True)
    tmp = OFFSETS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ofs, f, indent=2)
    os.replace(tmp, OFFSETS_PATH)

def _list_receipt_files() -> list[str]:
    return sorted(glob.glob(os.path.join(RECEIPTS_DIR, "*.jsonl")))

def _iter_lines(path: str, start: int) -> Iterable[tuple[int, str]]:
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx < start:
                continue
            yield idx, line

def _rec_key(rec: Dict[str, Any]) -> str:
    # Stable id: sha + event + rounded ts
    h = hashlib.sha256(json.dumps({"sha": rec.get("artifact_sha"), "e": rec.get("event"), "t": int(rec.get("ts", 0))}, sort_keys=True).encode()).hexdigest()
    return h

def ship_once(cfg: SinkConfig, once: bool = False, poll_sec: float = 1.0) -> None:
    if not (os.path.isdir(RECEIPTS_DIR)):
        print(f"[sink] receipts dir not found: {RECEIPTS_DIR}", file=sys.stderr)
        time.sleep(1.0)
        return

    ofs = _load_offsets()
    prod = _maybe_kafka_producer() if cfg.kafka_topic else None
    s3 = _maybe_s3_client() if cfg.s3_bucket else None

    changed = False
    files = _list_receipt_files()
    for path in files:
        start = int(ofs.get(path, 0))
        for idx, line in _iter_lines(path, start):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            key = _rec_key(rec)

            # Ship to Kafka
            if prod is not None:
                try:
                    prod.send(cfg.kafka_topic, key=key, value=rec)
                except Exception as e:
                    print(f"[sink] kafka send failed: {e}", file=sys.stderr)
                    # don't advance offset; retry next iteration
                    break

            # Ship to S3
            if s3 is not None:
                try:
                    # s3 prefix: receipts/YYMMDD/sha[:2]/<key>.json
                    ymd = time.strftime("%Y%m%d", time.gmtime(float(rec.get("ts", time.time()))))
                    sha = (rec.get("artifact_sha") or "unknown")[:2]
                    keypath = f"{cfg.s3_prefix.rstrip('/')}/receipts/{ymd}/{sha}/{key}.json"
                    s3.put_object(
                        Bucket=cfg.s3_bucket,
                        Key=keypath,
                        Body=json.dumps(rec).encode("utf-8"),
                        ContentType="application/json",
                    )
                except Exception as e:
                    print(f"[sink] s3 put failed: {e}", file=sys.stderr)
                    break

            ofs[path] = idx + 1
            changed = True

    if prod is not None:
        try:
            prod.flush(2.0)
        except Exception:
            pass

    if changed:
        _save_offsets(ofs)

    if once:
        return
    time.sleep(poll_sec)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Lukhas receipts sink → Kafka/S3")
    ap.add_argument("--once", action="store_true", help="Process current backlog once and exit")
    ap.add_argument("--poll-sec", type=float, default=1.0)
    # S3 config via env: RECEIPTS_S3_BUCKET, optional RECEIPTS_S3_PREFIX (default lukhas/receipts)
    # Kafka via env: RECEIPTS_KAFKA_BROKERS, RECEIPTS_KAFKA_TOPIC
    args = ap.parse_args()

    kafka_topic = os.environ.get("RECEIPTS_KAFKA_TOPIC")
    s3_bucket = os.environ.get("RECEIPTS_S3_BUCKET")
    s3_prefix = os.environ.get("RECEIPTS_S3_PREFIX", "lukhas/provenance")

    if not kafka_topic and not s3_bucket:
        print("[sink] Nothing to do: set RECEIPTS_KAFKA_TOPIC and/or RECEIPTS_S3_BUCKET", file=sys.stderr)
        sys.exit(1)

    cfg = SinkConfig(kafka_topic=kafka_topic, s3_bucket=s3_bucket, s3_prefix=s3_prefix)

    if args.once:
        ship_once(cfg, once=True, poll_sec=args.poll_sec)
        return

    print(f"[sink] starting receipts sink (dir={RECEIPTS_DIR})")
    while True:
        ship_once(cfg, once=False, poll_sec=args.poll_sec)

if __name__ == "__main__":
    main()