"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Compliance and ethical systems for the lukhas AI brain.

This module provides ethical compliance and safety mechanisms including:
- Ethical compliance engine
- Safety protocols
- Bias detection and mitigation
"""

# Note: The ComplianceEngine class is currently sourced from ethical_engine.py.
# Other modules (e.g., brain/orchestration/core.py) may have been updated
# to expect this class from a (currently non-existent) compliance_engine.py.
# This __init__.py makes ComplianceEngine available as:
#   from brain.compliance import ComplianceEngine (which sources from ethical_engine.py)
from .ethical_engine import ComplianceEngine

__all__ = ["ComplianceEngine"]
