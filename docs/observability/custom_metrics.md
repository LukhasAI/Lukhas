# Custom Business Metrics

This document provides details on the custom business metrics implemented in `lukhas/observability/custom_metrics.py`. These metrics are essential for monitoring the health and performance of key LUKHAS systems.

## QRG Signatures Total

- **Name:** `qrg_signatures_total`
- **Type:** Counter
- **Description:** Tracks the total number of Quantum Resonance Glyph (QRG) signatures generated. This metric is crucial for monitoring the activity and usage of the QRG security feature.
- **Labels:**
  - `credential_id`: The unique identifier for the credential that generated the signature.

## Guardian Vetoes Total

- **Name:** `guardian_vetoes_total`
- **Type:** Counter
- **Description:** Records the total number of vetoes issued by the Guardian system. This is a critical metric for understanding the effectiveness of the AI safety and governance policies.
- **Labels:**
  - `policy_id`: The identifier of the policy that triggered the veto.
  - `decision`: The outcome of the veto (e.g., `allow`, `deny`).

## Dream Drift

- **Name:** `dream_drift`
- **Type:** Gauge
- **Description:** Measures the current drift value of a dream. This metric is used to monitor the stability and coherence of the dream state, which is vital for the Consciousness subsystem.
- **Labels:**
  - `dream_id`: The unique identifier for the dream being monitored.

## Memory Fold Rate

- **Name:** `memory_fold_rate`
- **Type:** Gauge
- **Description:** Represents the current fold rate of the memory system. This metric provides insight into the efficiency and performance of the memory indexing and retrieval processes.
- **Labels:**
  - `index_name`: The name of the memory index being monitored.
