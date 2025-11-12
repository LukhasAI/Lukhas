"""LUKHAS business metrics."""

from observability.prometheus_registry import counter, gauge

QRG_SIGNATURES_TOTAL = counter(
    "qrg_signatures_total",
    "Total number of QRG signatures generated.",
    ["credential_id"],
)

GUARDIAN_VETOES_TOTAL = counter(
    "guardian_vetoes_total",
    "Total number of Guardian vetoes.",
    ["policy_id", "decision"],
)

DREAM_DRIFT = gauge(
    "dream_drift",
    "Current dream drift value.",
    ["dream_id"],
)

MEMORY_FOLD_RATE = gauge(
    "memory_fold_rate",
    "Current memory fold rate.",
    ["index_name"],
)
