# Alignment SLO Dashboard

This document provides an overview of the Grafana dashboard for monitoring Alignment SLOs (Service Level Objectives).

## Dashboard Purpose

The Alignment SLO dashboard provides a real-time view of key metrics related to the alignment of the LUKHAS AI system. It is designed to help engineers and researchers monitor the system's performance against its defined alignment goals.

## Panels

The dashboard consists of the following panels:

### Drift μ/σ timeline

*   **Description:** This panel displays the timeline of the drift μ/σ (micro-sigma), a measure of the deviation of the system's behavior from its baseline alignment. A lower value is better.
*   **Prometheus Query:** `lukhas_drift_microsigma`
*   **Interpretation:** A sudden spike in this value may indicate a significant deviation from the intended alignment, and should be investigated.

### QRG coverage %

*   **Description:** This panel shows the percentage of the system's responses that are covered by the Quantum Resonance Glyph (QRG) system. QRG is a key component of the alignment system.
*   **Prometheus Query:** `lukhas_qrg_coverage_percentage`
*   **Interpretation:** A high percentage indicates that the QRG system is effectively monitoring the system's outputs. A drop in this value could indicate a problem with the QRG system.

### Mesh coherence

*   **Description:** This panel displays the mesh coherence, a measure of the consistency and stability of the relationships between different components of the AI system. The SLO for this metric is > 0.90.
*   **Prometheus Query:** `lukhas_mesh_coherence > 0.90`
*   **Interpretation:** A value below 0.90 indicates a potential problem with the system's internal coherence, which could be a sign of misalignment.

### Dream validation failures

*   **Description:** This panel shows the rate of dream validation failures. The dream validation process is a critical part of the system's self-assessment and alignment correction mechanisms.
*   **Prometheus Query:** `sum(rate(lukhas_dream_validation_failures_total[5m]))`
*   **Interpretation:** An increase in the rate of dream validation failures can indicate that the system is struggling to maintain its alignment.
