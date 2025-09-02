# ARGUS (DΛST) — Unified Security Dashboard

Overview
--------
ARGUS (also referenced as DΛST in roadmap documents) is the Lambda product focused on security observability and automated vulnerability correlation. It aggregates results from multiple scanners (open-source and commercial), correlates findings across time and assets, and surfaces prioritized actions for security operators.

Goals
-----
- Provide a single-pane-of-glass for vulnerability data from heterogeneous scanners.
- Correlate duplicate or related findings across sources to reduce noise.
- Rank and prioritize findings by business impact, exploitability, and asset criticality.
- Support automated remediation workflows and export to ticket systems.

Core components
---------------
- Ingestion layer: pipeline connectors for OWASP ZAP, Nuclei, commercial scanners, SCA tools.
- Normalization & correlation: canonical issue model, deduplication, fingerprinting, and correlation engine.
- Prioritization engine: business context enrichment (asset tags, CVSS, exploit feeds) and scoring.
- Dashboard & API: interactive dashboards for analysts and REST/stream APIs for integrations.

Architecture notes
------------------
- Event-driven ingestion: use Kafka for durable event streaming and NATS for low-latency notifications.
- Storage: time-series + document store for raw findings, and a graph store (ArangoDB) for cross-asset correlation and lineage.
- Correlation workers: horizontally scalable processors (Go/Rust) that compute fingerprints and link related findings.
- Security: all connectors run with least privilege, and data in transit uses mTLS (Linkerd) per the platform policy.

APIs & contract
---------------
- Define an `finding` canonical schema (id, scanner, asset, fingerprint, severity, evidence, timestamp).
- Expose: `GET /api/findings`, `POST /api/findings/ingest`, `POST /api/findings/correlate`, `GET /api/assets/{id}`.

Quickstart (dev)
-----------------
1. Document expected scanner output and provide sample fixtures under `tests/fixtures/`.
2. Implement a simple ingestion worker that accepts ZAP JSON and emits normalized `finding` events to Kafka.

Next steps
----------
- Add detailed ingestion adapters and sample fixtures.
- Implement canonical finding schema and unit tests.
- Wire a minimal web UI prototype and instrument correlation metrics.
- Link implementation milestones back to the roadmap: `lukhas_website/LUKHΛS_STUDIO_IMPLEMENTATION_ROADMAP.md`.

