"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : compliance.py                                  │
│ DESCRIPTION : LucasID compliance registry + policy interface │
│ TYPE        : Compliance API                                 │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()

# ── Symbolic Compliance Table ─────────────────────────────────

COMPLIANCE_MATRIX = {
    "GDPR": {
        "status": "✅",
        "description": "Data minimization, right to erasure, consent enforcement",
    },
    "EU AI ACT": {
        "status": "✅",
        "description": "Risk classification, transparency, human oversight",
    },
    "OECD AI": {
        "status": "✅",
        "description": "Human-centered values, accountability, robustness",
    },
    "ISO/IEC 27001": {
        "status": "⚡",
        "description": "Security governance (in progress)",
    },
    "ISO/IEC 42001": {"status": "⚡", "description": "AI management systems (planned)"},
    "NIST AI RISK FRAMEWORK": {
        "status": "⚡",
        "description": "Explainability, adversarial robustness, fairness",
    },
}

# ── API Routes ────────────────────────────────────────────────


@router.get("/compliance/status")
def get_compliance_status():
    """
    Return the full symbolic compliance matrix.
    """
    return COMPLIANCE_MATRIX


@router.get("/compliance/{framework}")
def get_framework_status(framework: str):
    """
    Return the status and description of a specific compliance framework.
    """
    key = framework.upper()
    if key not in COMPLIANCE_MATRIX:
        raise HTTPException(status_code=404, detail="Framework not tracked.")
    return COMPLIANCE_MATRIX[key]
