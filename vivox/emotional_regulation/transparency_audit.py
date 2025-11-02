"""
VIVOX.ERN Transparency & Audit System
Provides comprehensive audit trails and user transparency for emotional regulation
"""

import logging
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from core.common import get_logger
from .vivox_ern_core import RegulationResponse, RegulationStrategy
        try:
                    try:

logger = logging.getLogger(__name__)

                        event = AuditEvent.from_dict(event_dict)
                        self.audit_events.append(event)
                    except Exception as e:
                        logger.error(f"Error loading audit event: {e}")

            logger.info(f"Loaded {len(self.audit_events)} audit events from storage")

        except Exception as e:
            logger.error(f"Error loading audit events: {e}")

    def get_audit_statistics(self) -> dict[str, Any]:
        """Get overall audit system statistics"""

        return {
            "total_events": len(self.audit_events),
            "unique_users": len(self.user_sessions),
            "event_types": {
                event_type.value: sum(1 for e in self.audit_events if e.event_type == event_type)
                for event_type in AuditEventType
            },
            "privacy_levels": {
                level: sum(1 for e in self.audit_events if e.privacy_level == level)
                for level in ["normal", "sensitive", "private"]
            },
            "retention_days": self.retention_days,
            "storage_path": self.storage_path,
            "auto_archive_enabled": self.auto_archive_enabled,
        }
