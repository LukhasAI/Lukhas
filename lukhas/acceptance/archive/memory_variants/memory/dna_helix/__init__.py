"""
Compatibility shim for DNA Helix Memory Architecture
DEPRECATED - Will be removed after 2025-11-01
"""

import warnings

warnings.warn(
    "Import path deprecated. Use 'from lukhas.acceptance.accepted.dna.helix import ...'",
    DeprecationWarning,
    stacklevel=2,
)

from lukhas.acceptance.accepted.dna.helix.dna_healix import DNAHealix
from lukhas.acceptance.accepted.dna.helix.dna_memory_architecture import (
    DNAMemoryArchitecture,
)
from lukhas.acceptance.accepted.dna.helix.helix_vault import HelixVault

__all__ = ["DNAMemoryArchitecture", "HelixVault", "DNAHealix"]
