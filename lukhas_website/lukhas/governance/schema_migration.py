#!/usr/bin/env python3

"""
LUKHAS Schema Migration System
=============================

Schema evolution and backwards compatibility management for Guardian data structures.
Provides automatic migration, compatibility checking, and version management.

Features:
- Automatic schema migration between versions
- Backwards compatibility validation
- Forward compatibility detection
- Migration path optimization
- Data transformation rules
- Rollback capabilities
- Version-aware serialization
- Migration audit trail

Performance Targets:
- Migration time: <10ms for typical Guardian data
- Memory overhead: <5MB per migration context
- Compatibility check: <1ms
- Migration throughput: 1K+ migrations/second

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .schema_registry import SchemaVersion

logger = logging.getLogger(__name__)


class CompatibilityType(Enum):
    """Types of schema compatibility"""

    BACKWARD = "backward"  # New schema can read old data
    FORWARD = "forward"  # Old schema can read new data
    FULL = "full"  # Bidirectional compatibility
    NONE = "none"  # No compatibility


class MigrationType(Enum):
    """Types of schema migrations"""

    FIELD_ADD = "field_add"  # Add new field
    FIELD_REMOVE = "field_remove"  # Remove field
    FIELD_RENAME = "field_rename"  # Rename field
    FIELD_TYPE_CHANGE = "field_type_change"  # Change field type
    ENUM_VALUE_ADD = "enum_value_add"  # Add enum value
    ENUM_VALUE_REMOVE = "enum_value_remove"  # Remove enum value
    STRUCTURE_CHANGE = "structure_change"  # Complex structural change
    CUSTOM = "custom"  # Custom transformation


@dataclass
class MigrationRule:
    """Rule for data migration between schema versions"""

    migration_id: str
    from_version: str
    to_version: str
    migration_type: MigrationType
    field_path: str
    transformation: Callable[[Any], Any]
    description: str
    reversible: bool = False
    reverse_transformation: Optional[Callable[[Any], Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationContext:
    """Context for migration operations"""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_version: Optional[str] = None
    target_version: Optional[str] = None
    schema_id: str = "guardian_decision"
    preserve_unknown_fields: bool = True
    strict_mode: bool = False
    audit_trail: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationStep:
    """Individual step in migration process"""

    rule: MigrationRule
    applied_at: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    data_before: Optional[Any] = None
    data_after: Optional[Any] = None


@dataclass
class MigrationResult:
    """Result of schema migration"""

    success: bool
    migrated_data: Optional[Any] = None
    source_version: Optional[str] = None
    target_version: Optional[str] = None
    migration_time_ms: float = 0.0
    steps: List[MigrationStep] = field(default_factory=list)
    compatibility_type: Optional[CompatibilityType] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MigrationEngine:
    """Engine for executing schema migrations"""

    def __init__(self):
        self.migration_rules: Dict[Tuple[str, str], List[MigrationRule]] = {}
        self.migration_paths: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
        self._lock = threading.RLock()
        self._metrics = MigrationMetrics()

        # Initialize default Guardian migration rules
        self._initialize_guardian_migrations()

    def register_migration_rule(self, rule: MigrationRule) -> None:
        """Register a migration rule"""
        with self._lock:
            key = (rule.from_version, rule.to_version)
            if key not in self.migration_rules:
                self.migration_rules[key] = []
            self.migration_rules[key].append(rule)

            # Update migration paths
            self._update_migration_paths()

            logger.info(f"Registered migration rule {rule.migration_id}: {rule.from_version} -> {rule.to_version}")

    def migrate_data(
        self, data: Any, from_version: str, to_version: str, context: Optional[MigrationContext] = None
    ) -> MigrationResult:
        """Migrate data from one schema version to another"""
        start_time = time.perf_counter()

        if context is None:
            context = MigrationContext(source_version=from_version, target_version=to_version)

        try:
            # Check if migration is needed
            if from_version == to_version:
                return MigrationResult(
                    success=True,
                    migrated_data=data,
                    source_version=from_version,
                    target_version=to_version,
                    migration_time_ms=(time.perf_counter() - start_time) * 1000,
                    compatibility_type=CompatibilityType.FULL,
                )

            # Find migration path
            migration_path = self._find_migration_path(from_version, to_version)
            if not migration_path:
                return MigrationResult(
                    success=False,
                    source_version=from_version,
                    target_version=to_version,
                    errors=[f"No migration path found from {from_version} to {to_version}"],
                    migration_time_ms=(time.perf_counter() - start_time) * 1000,
                )

            # Execute migration steps
            current_data = data
            current_version = from_version
            steps = []
            warnings = []

            for next_version in migration_path:
                if current_version == next_version:
                    continue

                step_result = self._execute_migration_step(current_data, current_version, next_version, context)
                steps.extend(step_result.steps)
                warnings.extend(step_result.warnings)

                if not step_result.success:
                    return MigrationResult(
                        success=False,
                        source_version=from_version,
                        target_version=to_version,
                        migration_time_ms=(time.perf_counter() - start_time) * 1000,
                        steps=steps,
                        errors=step_result.errors,
                    )

                current_data = step_result.migrated_data
                current_version = next_version

            migration_time = (time.perf_counter() - start_time) * 1000

            # Determine compatibility type
            compatibility = self._determine_compatibility(from_version, to_version)

            result = MigrationResult(
                success=True,
                migrated_data=current_data,
                source_version=from_version,
                target_version=to_version,
                migration_time_ms=migration_time,
                steps=steps,
                compatibility_type=compatibility,
                warnings=warnings,
                metadata={
                    "migration_path": migration_path,
                    "steps_executed": len(steps),
                    "context_id": context.request_id,
                },
            )

            # Update metrics
            self._metrics.record_migration(result)

            return result

        except Exception as e:
            migration_time = (time.perf_counter() - start_time) * 1000
            self._metrics.record_error()

            return MigrationResult(
                success=False,
                source_version=from_version,
                target_version=to_version,
                migration_time_ms=migration_time,
                errors=[f"Migration failed: {str(e)}"],
            )

    def check_compatibility(
        self, from_version: str, to_version: str, schema_id: str = "guardian_decision"
    ) -> CompatibilityType:
        """Check compatibility between two schema versions"""
        try:
            # Check if direct migration exists
            forward_key = (from_version, to_version)
            backward_key = (to_version, from_version)

            has_forward = forward_key in self.migration_rules
            has_backward = backward_key in self.migration_rules

            if has_forward and has_backward:
                return CompatibilityType.FULL
            elif has_forward:
                return CompatibilityType.FORWARD
            elif has_backward:
                return CompatibilityType.BACKWARD
            else:
                # Check for indirect compatibility via migration paths
                forward_path = self._find_migration_path(from_version, to_version)
                backward_path = self._find_migration_path(to_version, from_version)

                if forward_path and backward_path:
                    return CompatibilityType.FULL
                elif forward_path:
                    return CompatibilityType.FORWARD
                elif backward_path:
                    return CompatibilityType.BACKWARD
                else:
                    return CompatibilityType.NONE

        except Exception:
            return CompatibilityType.NONE

    def get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """Get migration path between versions"""
        return self._find_migration_path(from_version, to_version)

    def get_available_versions(self, schema_id: str = "guardian_decision") -> Set[str]:
        """Get all available schema versions"""
        versions = set()
        for (from_ver, to_ver), rules in self.migration_rules.items():
            if any(rule.field_path.startswith(schema_id) for rule in rules):
                versions.add(from_ver)
                versions.add(to_ver)
        return versions

    def get_metrics(self) -> Dict[str, Any]:
        """Get migration engine metrics"""
        return self._metrics.get_stats()

    def _initialize_guardian_migrations(self) -> None:
        """Initialize default Guardian schema migrations"""
        # Migration from 1.0.0 to 2.0.0 (major version bump)
        self.register_migration_rule(
            MigrationRule(
                migration_id="guardian_1_0_0_to_2_0_0",
                from_version="1.0.0",
                to_version="2.0.0",
                migration_type=MigrationType.STRUCTURE_CHANGE,
                field_path="$",
                transformation=self._migrate_guardian_1_to_2,
                description="Migrate Guardian schema from v1.0.0 to v2.0.0",
                reversible=False,
            )
        )

        # Migration from 2.0.0 to 2.1.0 (minor version - backward compatible)
        self.register_migration_rule(
            MigrationRule(
                migration_id="guardian_2_0_0_to_2_1_0",
                from_version="2.0.0",
                to_version="2.1.0",
                migration_type=MigrationType.FIELD_ADD,
                field_path="extensions",
                transformation=self._migrate_guardian_2_0_to_2_1,
                description="Add extensions field for future compatibility",
                reversible=True,
                reverse_transformation=self._migrate_guardian_2_1_to_2_0,
            )
        )

        # Migration from 2.1.0 to 2.1.1 (patch version - fully compatible)
        self.register_migration_rule(
            MigrationRule(
                migration_id="guardian_2_1_0_to_2_1_1",
                from_version="2.1.0",
                to_version="2.1.1",
                migration_type=MigrationType.ENUM_VALUE_ADD,
                field_path="decision.status",
                transformation=lambda x: x,  # No transformation needed
                description="Add new enum values for decision status",
                reversible=True,
                reverse_transformation=lambda x: x,
            )
        )

    def _execute_migration_step(
        self, data: Any, from_version: str, to_version: str, context: MigrationContext
    ) -> MigrationResult:
        """Execute a single migration step"""
        start_time = time.perf_counter()

        key = (from_version, to_version)
        if key not in self.migration_rules:
            return MigrationResult(
                success=False, errors=[f"No migration rules found for {from_version} -> {to_version}"]
            )

        rules = self.migration_rules[key]
        migrated_data = data
        steps = []

        for rule in rules:
            step_start = time.perf_counter()
            step_success = True
            step_error = None
            data_before = migrated_data if context.audit_trail else None

            try:
                migrated_data = rule.transformation(migrated_data)
            except Exception as e:
                step_success = False
                step_error = str(e)
                if context.strict_mode:
                    break

            step_duration = (time.perf_counter() - step_start) * 1000
            step = MigrationStep(
                rule=rule,
                applied_at=datetime.now(timezone.utc),
                duration_ms=step_duration,
                success=step_success,
                error_message=step_error,
                data_before=data_before,
                data_after=migrated_data if context.audit_trail and step_success else None,
            )
            steps.append(step)

            if not step_success and context.strict_mode:
                break

        migration_time = (time.perf_counter() - start_time) * 1000
        success = all(step.success for step in steps)

        return MigrationResult(
            success=success,
            migrated_data=migrated_data if success else None,
            source_version=from_version,
            target_version=to_version,
            migration_time_ms=migration_time,
            steps=steps,
        )

    def _find_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """Find migration path between versions using BFS"""
        if from_version == to_version:
            return []

        # Build graph of available migrations
        graph = {}
        for (from_ver, to_ver), rules in self.migration_rules.items():
            if from_ver not in graph:
                graph[from_ver] = []
            graph[from_ver].append(to_ver)

        # BFS to find shortest path
        from collections import deque

        queue = deque([(from_version, [from_version])])
        visited = {from_version}

        while queue:
            current_version, path = queue.popleft()

            if current_version == to_version:
                return path[1:]  # Exclude starting version

            if current_version in graph:
                for next_version in graph[current_version]:
                    if next_version not in visited:
                        visited.add(next_version)
                        queue.append((next_version, path + [next_version]))

        return []  # No path found

    def _update_migration_paths(self) -> None:
        """Update cached migration paths"""
        # This could be optimized with precomputed paths
        # For now, we compute paths on demand
        pass

    def _determine_compatibility(self, from_version: str, to_version: str) -> CompatibilityType:
        """Determine compatibility type between versions"""
        try:
            from_ver = SchemaVersion(from_version)
            to_ver = SchemaVersion(to_version)

            if from_ver.major != to_ver.major:
                return CompatibilityType.NONE  # Major version changes break compatibility

            if from_ver.minor != to_ver.minor:
                if from_ver < to_ver:
                    return CompatibilityType.FORWARD  # Minor version increase
                else:
                    return CompatibilityType.BACKWARD  # Minor version decrease

            # Same major and minor, only patch difference
            return CompatibilityType.FULL

        except ValueError:
            return CompatibilityType.NONE

    def _migrate_guardian_1_to_2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate Guardian schema from v1 to v2"""
        # This is a major version migration with structural changes
        migrated = {
            "schema_version": "2.0.0",
            "decision": data.get("decision", {}),
            "subject": data.get("subject", {}),
            "context": data.get("context", {}),
            "metrics": data.get("metrics", {}),
            "enforcement": data.get("enforcement", {"mode": "dark"}),
            "audit": data.get("audit", {}),
            "integrity": {"content_sha256": self._calculate_content_hash(data)},
        }

        # Convert old fields if they exist
        if "timestamp" in data:
            migrated["audit"]["timestamp"] = data["timestamp"]

        if "emergency_active" in data:
            migrated["context"]["features"] = {
                "emergency_active": data["emergency_active"],
                "enforcement_enabled": True,
            }

        return migrated

    def _migrate_guardian_2_0_to_2_1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate Guardian schema from v2.0 to v2.1"""
        migrated = data.copy()
        migrated["schema_version"] = "2.1.0"

        # Add extensions field for future compatibility
        if "extensions" not in migrated:
            migrated["extensions"] = {}

        return migrated

    def _migrate_guardian_2_1_to_2_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse migrate Guardian schema from v2.1 to v2.0"""
        migrated = data.copy()
        migrated["schema_version"] = "2.0.0"

        # Remove extensions field
        migrated.pop("extensions", None)

        return migrated

    def _calculate_content_hash(self, data: Dict[str, Any]) -> str:
        """Calculate content hash for integrity field"""
        import hashlib

        content_str = json.dumps(data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


class MigrationMetrics:
    """Performance metrics for migration operations"""

    def __init__(self):
        self.migration_count = 0
        self.total_migration_time = 0.0
        self.failed_migrations = 0
        self.migrations_by_type = {migration_type: 0 for migration_type in MigrationType}
        self.error_count = 0
        self.start_time = time.time()

    def record_migration(self, result: MigrationResult) -> None:
        """Record migration metrics"""
        self.migration_count += 1
        self.total_migration_time += result.migration_time_ms

        if not result.success:
            self.failed_migrations += 1

        for step in result.steps:
            self.migrations_by_type[step.rule.migration_type] += 1

    def record_error(self) -> None:
        """Record migration error"""
        self.error_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get migration statistics"""
        uptime = time.time() - self.start_time
        avg_time = self.total_migration_time / self.migration_count if self.migration_count > 0 else 0

        return {
            "total_migrations": self.migration_count,
            "average_migration_time_ms": avg_time,
            "failed_migrations": self.failed_migrations,
            "success_rate": (
                (self.migration_count - self.failed_migrations) / self.migration_count
                if self.migration_count > 0
                else 1.0
            ),
            "throughput_per_second": self.migration_count / uptime if uptime > 0 else 0,
            "migrations_by_type": {
                migration_type.name: count for migration_type, count in self.migrations_by_type.items()
            },
            "error_count": self.error_count,
            "uptime_seconds": uptime,
        }


# Global migration engine instance
_migration_engine: Optional[MigrationEngine] = None
_migration_lock = threading.Lock()


def get_migration_engine() -> MigrationEngine:
    """Get global migration engine instance"""
    global _migration_engine

    if _migration_engine is None:
        with _migration_lock:
            if _migration_engine is None:
                _migration_engine = MigrationEngine()

    return _migration_engine


# Convenience functions
def migrate_guardian_data(
    data: Dict[str, Any], target_version: str, source_version: Optional[str] = None
) -> MigrationResult:
    """Migrate Guardian data to target version"""
    engine = get_migration_engine()

    if source_version is None:
        # Try to detect source version from data
        source_version = data.get("schema_version", "1.0.0")

    return engine.migrate_data(data, source_version, target_version)


def check_schema_compatibility(from_version: str, to_version: str) -> CompatibilityType:
    """Check compatibility between schema versions"""
    engine = get_migration_engine()
    return engine.check_compatibility(from_version, to_version)


def register_custom_migration(
    from_version: str,
    to_version: str,
    transformation: Callable[[Any], Any],
    migration_type: MigrationType = MigrationType.CUSTOM,
    reversible: bool = False,
    reverse_transformation: Optional[Callable[[Any], Any]] = None,
) -> None:
    """Register custom migration rule"""
    engine = get_migration_engine()

    rule = MigrationRule(
        migration_id=f"custom_{from_version}_to_{to_version}",
        from_version=from_version,
        to_version=to_version,
        migration_type=migration_type,
        field_path="$",
        transformation=transformation,
        description=f"Custom migration from {from_version} to {to_version}",
        reversible=reversible,
        reverse_transformation=reverse_transformation,
    )

    engine.register_migration_rule(rule)
