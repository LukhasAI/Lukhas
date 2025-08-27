import os
import time
import uuid
from typing import Any, Optional

from lukhas.observability.matriz_decorators import instrument

from .registry import get_provider

FEATURE = os.getenv("FEATURE_GOVERNANCE_LEDGER", "false").lower() == "true"


@instrument("CONSENT", label="governance:record", salience=0.6, urgency=0.2)
def record_consent(
    user_id: str, scope: str, metadata: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Minimal, safe consent recording API.
    - Works in DRY_RUN/OFFLINE with builtin provider (no network)
    - When FEATURE_GOVERNANCE_LEDGER=true, registry may supply real provider
    """
    provider = get_provider(enabled=FEATURE)
    entry = {
        "trace_id": str(uuid.uuid4()),
        "ts": int(time.time() * 1000),
        "user_id": user_id,
        "scope": scope,
        "metadata": metadata or {},
    }
    return provider.record(entry)
