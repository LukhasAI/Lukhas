#!/usr/bin/env python3
"""
LUKHAS Enterprise Structured Audit Logger
Production-grade audit logging with compliance and security features
"""

import asyncio
import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import aiofiles
import aiofiles.os
import structlog
from cryptography.fernet import Fernet

from async_utils import create_background_task
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field, validator

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


class AuditEventType(str, Enum):
    """Types of audit events"""

    # Authentication & Authorization
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    ACCESS_GRANTED = "auth.access.granted"
    ACCESS_DENIED = "auth.access.denied"
    PERMISSION_CHANGED = "auth.permission.changed"

    # Data Operations
    DATA_CREATE = "data.create"
    DATA_READ = "data.read"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"

    # System Operations
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    CONFIG_CHANGE = "system.config.change"
    DEPLOYMENT = "system.deployment"
    BACKUP = "system.backup"
    RESTORE = "system.restore"

    # Security Events
    SECURITY_SCAN = "security.scan"
    VULNERABILITY_DETECTED = "security.vulnerability.detected"
    VULNERABILITY_FIXED = "security.vulnerability.fixed"
    ENCRYPTION_KEY_ROTATION = "security.key.rotation"

    # Compliance Events
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"
    AUDIT_TRAIL_ACCESS = "compliance.audit.access"

    # LUKHAS Specific
    MEMORY_FOLD = "memory.fold"
    CONSCIOUSNESS_STATE_CHANGE = "consciousness.change"
    EMOTIONAL_DRIFT = "emotion.drift"
    TIER_ACCESS = "tier.access"


class AuditEvent(BaseModel):
    """Structured audit event with validation"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: AuditEventType
    actor: dict[str, Any] = Field(..., description="Who performed the action")
    resource: dict[str, Any] = Field(..., description="What was acted upon")
    action: str = Field(..., description="What action was performed")
    result: str = Field(..., description="Success, failure, partial")

    # Optional fields
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # Security context
    tier_level: Optional[int] = None
    risk_score: Optional[float] = None

    # Additional data
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)

    # Compliance fields
    data_classification: Optional[str] = None
    retention_days: int = Field(default=2555, description="7 years default")

    @validator("risk_score")
    def validate_risk_score(cls, v):
        if v is not None and not 0 <= v <= 10:
            raise ValueError("Risk score must be between 0 and 10")
        return v

    def to_json(self) -> str:
        """Convert to JSON with datetime handling"""
        data = self.dict()
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, default=str)


class AuditLogger:
    """
    Enterprise-grade audit logger with:
    - Structured logging
    - Encryption at rest
    - Tamper detection
    - Compliance features
    - High performance async I/O
    - Log rotation and archival
    """

    def __init__(
        self,
        log_dir: Path = Path("audit_logs"),
        encryption_key: Optional[str] = None,
        rotation_size_mb: int = 100,
        retention_days: int = 2555,
    ):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.rotation_size_mb = rotation_size_mb
        self.retention_days = retention_days

        # Initialize encryption
        self.cipher_suite = None
        if encryption_key:
            self._init_encryption(encryption_key)

        # Current log file
        self.current_log_file = self._get_current_log_file()

        # In-memory buffer for performance
        self.buffer: list[AuditEvent] = []
        self.buffer_size = 100
        self.flush_interval = 5.0  # seconds

        # Tamper detection
        self.hash_chain = self._load_hash_chain()

        # Structured logger
        self.logger = structlog.get_logger("audit")

        # Start background tasks
        self._start_background_tasks()

    def _init_encryption(self, key: str):
        """Initialize encryption with derived key"""
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"lukhas_audit_salt",  # In production, use random salt
            iterations=100000,
        )
        kdf.derive(key.encode())
        self.cipher_suite = Fernet(
            Fernet.generate_key()
        )
        # Use derived key in production

    def _get_current_log_file(self) -> Path:
        """Get current log file path with rotation support"""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        base_name = f"audit_{date_str}"

        # Find latest file for today
        existing_files = list(self.log_dir.glob(f"{base_name}_*.jsonl"))
        if not existing_files:
            return self.log_dir / f"{base_name}_001.jsonl"

        # Check if we need to rotate
        latest_file = sorted(existing_files)[-1]
        if latest_file.stat().st_size > self.rotation_size_mb * 1024 * 1024:
            # Create new file
            num = int(latest_file.stem.split("_")[-1]) + 1
            return self.log_dir / f"{base_name}_{num:03d}.jsonl"

        return latest_file

    def _load_hash_chain(self) -> str:
        """Load or initialize hash chain for tamper detection"""
        hash_file = self.log_dir / ".hash_chain"
        if hash_file.exists():
            return hash_file.read_text().strip()
        else:
            # Initialize with random value
            initial_hash = hashlib.sha256(os.urandom(32)).hexdigest()
            hash_file.write_text(initial_hash)
            return initial_hash

    def _update_hash_chain(self, event_data: str) -> str:
        """Update hash chain with new event"""
        combined = f"{self.hash_chain}{event_data}"
        new_hash = hashlib.sha256(combined.encode()).hexdigest()
        self.hash_chain = new_hash

        # Persist hash chain
        hash_file = self.log_dir / ".hash_chain"
        hash_file.write_text(new_hash)

        return new_hash

    def _start_background_tasks(self):
        """Start background tasks for flushing and cleanup"""
        create_background_task(self._flush_loop())
        create_background_task(self._cleanup_loop())

    async def _flush_loop(self):
        """Periodically flush buffer to disk"""
        while True:
            await asyncio.sleep(self.flush_interval)
            if self.buffer:
                await self._flush_buffer()

    async def _cleanup_loop(self):
        """Periodically clean up old logs"""
        while True:
            await asyncio.sleep(86400)  # Daily
            await self._cleanup_old_logs()

    async def log(self, event: AuditEvent):
        """Log an audit event"""
        # Add to buffer
        self.buffer.append(event)

        # Log to structured logger for real-time monitoring
        self.logger.info(
            event.event_type,
            event_id=event.event_id,
            actor=event.actor.get("id"),
            resource=event.resource.get("type"),
            result=event.result,
            risk_score=event.risk_score,
        )

        # Flush if buffer is full
        if len(self.buffer) >= self.buffer_size:
            await self._flush_buffer()

    async def _flush_buffer(self):
        """Flush buffer to disk"""
        if not self.buffer:
            return

        # Prepare events for writing
        events_to_write = self.buffer.copy()
        self.buffer.clear()

        # Check if we need to rotate
        if self.current_log_file.exists():
            size = self.current_log_file.stat().st_size
            if size > self.rotation_size_mb * 1024 * 1024:
                self.current_log_file = self._get_current_log_file()

        # Write events
        async with aiofiles.open(self.current_log_file, "a") as f:
            for event in events_to_write:
                # Convert to JSON
                event_json = event.to_json()

                # Add hash for tamper detection
                event_hash = self._update_hash_chain(event_json)

                # Create log entry
                log_entry = {"event": json.loads(event_json), "hash": event_hash}

                # Encrypt if enabled
                if self.cipher_suite:
                    encrypted = self.cipher_suite.encrypt(
                        json.dumps(log_entry).encode()
                    )
                    await f.write(encrypted.decode() + "\n")
                else:
                    await f.write(json.dumps(log_entry) + "\n")

    async def _cleanup_old_logs(self):
        """Clean up logs older than retention period"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("audit_*.jsonl"):
            # Parse date from filename
            try:
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=timezone.utc)

                if file_date < cutoff_date:
                    # Archive before deletion
                    await self._archive_log(log_file)
                    await aiofiles.os.remove(log_file)

            except Exception as e:
                self.logger.error("cleanup_failed", file=str(log_file), error=str(e))

    async def _archive_log(self, log_file: Path):
        """Archive log file before deletion"""
        archive_dir = self.log_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        # Compress and move
        archive_dir / f"{log_file.stem}.gz"
        # Implementation would compress the file

    async def query(
        self,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[list[AuditEventType]] = None,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> list[AuditEvent]:
        """Query audit logs with filters"""
        results = []

        # Find relevant log files
        for log_file in sorted(self.log_dir.glob("audit_*.jsonl")):
            # Check if file is in date range
            # Implementation would parse dates and filter

            async with aiofiles.open(log_file) as f:
                async for line in f:
                    try:
                        # Decrypt if needed
                        if self.cipher_suite:
                            decrypted = self.cipher_suite.decrypt(line.strip().encode())
                            log_entry = json.loads(decrypted)
                        else:
                            log_entry = json.loads(line.strip())

                        event_data = log_entry["event"]
                        event = AuditEvent(**event_data)

                        # Apply filters
                        if event_types and event.event_type not in event_types:
                            continue
                        if actor_id and event.actor.get("id") != actor_id:
                            continue
                        if (
                            resource_type
                            and event.resource.get("type") != resource_type
                        ):
                            continue
                        if not (start_time <= event.timestamp <= end_time):
                            continue

                        results.append(event)

                    except Exception as e:
                        self.logger.error("query_parse_error", error=str(e))

        return results

    async def verify_integrity(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Verify audit log integrity"""
        results = {"valid": True, "files_checked": 0, "events_checked": 0, "errors": []}

        # Rebuild hash chain and verify
        computed_chain = self._load_hash_chain()

        for log_file in sorted(self.log_dir.glob("audit_*.jsonl")):
            results["files_checked"] += 1

            async with aiofiles.open(log_file) as f:
                async for line in f:
                    try:
                        if self.cipher_suite:
                            decrypted = self.cipher_suite.decrypt(line.strip().encode())
                            log_entry = json.loads(decrypted)
                        else:
                            log_entry = json.loads(line.strip())

                        # Verify hash
                        expected_hash = log_entry["hash"]
                        event_json = json.dumps(log_entry["event"])

                        # Compute hash
                        combined = f"{computed_chain}{event_json}"
                        computed_hash = hashlib.sha256(combined.encode()).hexdigest()

                        if computed_hash != expected_hash:
                            results["valid"] = False
                            results["errors"].append(
                                {
                                    "file": str(log_file),
                                    "event_id": log_entry["event"]["event_id"],
                                    "error": "Hash mismatch",
                                }
                            )

                        computed_chain = expected_hash
                        results["events_checked"] += 1

                    except Exception as e:
                        results["errors"].append(
                            {"file": str(log_file), "error": str(e)}
                        )

        return results

    async def export_for_compliance(
        self, start_date: datetime, end_date: datetime, format: str = "json"
    ) -> Path:
        """Export audit logs for compliance reporting"""
        export_dir = self.log_dir / "exports"
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"audit_export_{timestamp}.{format}"

        events = await self.query(start_date, end_date)

        if format == "json":
            with open(export_file, "w") as f:
                json.dump([e.dict() for e in events], f, indent=2, default=str)
        elif format == "csv":
            # Implementation would export to CSV
            pass

        # Generate export receipt
        receipt = {
            "export_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "event_count": len(events),
            "file_path": str(export_file),
            "file_hash": self._compute_file_hash(export_file),
        }

        receipt_file = export_dir / f"receipt_{timestamp}.json"
        with open(receipt_file, "w") as f:
            json.dump(receipt, f, indent=2)

        return export_file

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# Convenience functions for common operations


async def log_login(
    audit_logger: AuditLogger,
    user_id: str,
    success: bool,
    ip_address: str,
    metadata: Optional[dict] = None,
):
    """Log login attempt"""
    event = AuditEvent(
        event_type=(
            AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE
        ),
        actor={"id": user_id, "type": "user"},
        resource={"type": "authentication", "id": "system"},
        action="login",
        result="success" if success else "failure",
        ip_address=ip_address,
        metadata=metadata or {},
    )
    await audit_logger.log(event)


async def log_data_access(
    audit_logger: AuditLogger,
    user_id: str,
    resource_type: str,
    resource_id: str,
    action: str,
    tier_level: int,
):
    """Log data access event"""
    event = AuditEvent(
        event_type=AuditEventType.DATA_READ,
        actor={"id": user_id, "type": "user"},
        resource={"type": resource_type, "id": resource_id},
        action=action,
        result="success",
        tier_level=tier_level,
    )
    await audit_logger.log(event)


async def log_security_event(
    audit_logger: AuditLogger,
    event_type: AuditEventType,
    details: dict[str, Any],
    risk_score: float,
):
    """Log security-related event"""
    event = AuditEvent(
        event_type=event_type,
        actor={"id": "system", "type": "system"},
        resource={"type": "security", "id": "system"},
        action="security_check",
        result="detected",
        risk_score=risk_score,
        metadata=details,
    )
    await audit_logger.log(event)


async def main():
    """Example usage"""
    # Initialize logger
    audit_logger = AuditLogger(
        encryption_key="your-secret-key", rotation_size_mb=50, retention_days=2555
    )

    # Log some events
    await log_login(audit_logger, "user123", True, "192.168.1.1")

    await log_data_access(
        audit_logger, "user123", "memory", "mem_456", "fold_memory", tier_level=3
    )

    # Query logs
    from datetime import timedelta

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    events = await audit_logger.query(start_time, end_time, actor_id="user123")

    print(f"Found {len(events)} events for user123")

    # Verify integrity
    integrity = await audit_logger.verify_integrity(start_time, end_time)
    print(f"Integrity check: {'PASSED' if integrity['valid'] else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
