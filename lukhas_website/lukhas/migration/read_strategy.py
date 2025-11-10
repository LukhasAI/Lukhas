import logging
from typing import Optional

from dna.interfaces import HelixMemory
from migration.legacy_store import LegacyStore

logger = logging.getLogger(__name__)



def read_memory(*, legacy: LegacyStore, dna: HelixMemory, key: str) -> Optional[dict]:
# T4: code=F821 | ticket=SKELETON-E62E981B | owner=lukhas-platform | status=skeleton
# reason: Undefined Flags in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
    cutover = Flags.get_str("DNA_CUTOVER_READ_FROM", "legacy").lower()  # TODO: Flags
# T4: code=F821 | ticket=SKELETON-E62E981B | owner=lukhas-platform | status=skeleton
# reason: Undefined Flags in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
    shadow = Flags.get("DNA_READ_SHADOW", default=False)  # TODO: Flags

    def _cmp(a, b):  # minimalist compare
        if not a or not b:
            return (a is None) == (b is None)
        return (a.get("value") == b.get("value")) and (a.get("version") == b.get("version"))

    if cutover == "dna":
        primary = dna.read(key)
        if shadow:
            legacy_row = legacy.read(key)
            if not _cmp(legacy_row, primary):
                # TODO: replace with your audit/metrics logger
                print(f"[READ-SHADOW] drift key={key} legacy={legacy_row} dna={primary}")
        return primary
    else:
        primary = legacy.read(key)
        if shadow:
            dna_row = dna.read(key)
            if not _cmp(primary, dna_row):
                print(f"[READ-SHADOW] drift key={key} legacy={primary} dna={dna_row}")
        return primary
