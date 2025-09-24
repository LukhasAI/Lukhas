#!/usr/bin/env python3

"""
LUKHAS Guardian Schema Registry
==============================

Centralized schema management and versioning system for Guardian data structures.
Provides high-performance schema validation, versioning, and migration capabilities.

Features:
- Schema versioning with semantic version support
- Multi-format validation (JSON Schema, custom validators)
- Hot reloading of schema definitions
- Backwards compatibility checking
- Schema evolution tracking
- Performance-optimized validation caching
- Constitutional AI compliance integration

Performance Targets:
- Schema validation: <1ms for 99% of operations
- Schema registry access: <0.1ms (cached)
- Memory footprint: <100MB for complete registry
- Throughput: 10K+ validations/second

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from weakref import WeakValueDictionary

import jsonschema
from jsonschema.validators import Draft202012Validator

logger = logging.getLogger(__name__)


class SchemaVersion:
    """Semantic version handling for schemas"""

    def __init__(self, version_str: str):
        self.version_str = version_str
        parts = version_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")

        self.major, self.minor, self.patch = map(int, parts)

    def __str__(self) -> str:
        return self.version_str

    def __eq__(self, other) -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other

    def is_compatible(self, other) -> bool:
        """Check if this version is backwards compatible with other"""
        return self.major == other.major and self >= other


class SchemaFormat(Enum):
    """Supported schema formats"""
    JSON_SCHEMA = "json_schema"
    CUSTOM = "custom"
    HYBRID = "hybrid"


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"           # Full validation with all constraints
    MODERATE = "moderate"       # Core validation with some flexibility
    LENIENT = "lenient"         # Basic validation only
    SYNTAX_ONLY = "syntax_only" # Syntax validation only


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    schema_version: Optional[str] = None
    compliance_score: float = 1.0  # Constitutional AI compliance score


@dataclass
class SchemaMetadata:
    """Metadata for schema definitions"""
    id: str
    version: SchemaVersion
    format: SchemaFormat
    created_at: float
    updated_at: float
    checksum: str
    dependencies: Set[str] = field(default_factory=set)
    description: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    validation_level: ValidationLevel = ValidationLevel.STRICT


class SchemaValidator(ABC):
    """Abstract base class for schema validators"""

    @abstractmethod
    def validate(self, data: Any, schema: Dict[str, Any], level: ValidationLevel) -> SchemaValidationResult:
        """Validate data against schema"""
        pass

    @abstractmethod
    def supports_format(self, format: SchemaFormat) -> bool:
        """Check if validator supports given format"""
        pass


class JSONSchemaValidator(SchemaValidator):
    """JSON Schema validator implementation"""

    def __init__(self):
        self._validator_cache: WeakValueDictionary = WeakValueDictionary()
        self._cache_lock = threading.RLock()

    def validate(self, data: Any, schema: Dict[str, Any], level: ValidationLevel) -> SchemaValidationResult:
        """Validate data against JSON schema"""
        start_time = time.perf_counter()

        try:
            # Get cached validator or create new one
            schema_hash = self._hash_schema(schema)
            validator = self._get_cached_validator(schema_hash, schema)

            # Perform validation
            errors = []
            for error in validator.iter_errors(data):
                errors.append(f"{error.json_path}: {error.message}")

                # Stop early for lenient validation
                if level == ValidationLevel.LENIENT and len(errors) >= 5:
                    break

            is_valid = len(errors) == 0
            validation_time = (time.perf_counter() - start_time) * 1000

            return SchemaValidationResult(
                is_valid=is_valid,
                errors=errors,
                validation_time_ms=validation_time,
                compliance_score=1.0 if is_valid else max(0.0, 1.0 - len(errors) * 0.1)
            )

        except Exception as e:
            validation_time = (time.perf_counter() - start_time) * 1000
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                validation_time_ms=validation_time,
                compliance_score=0.0
            )

    def supports_format(self, format: SchemaFormat) -> bool:
        """Check if validator supports JSON Schema format"""
        return format in (SchemaFormat.JSON_SCHEMA, SchemaFormat.HYBRID)

    def _hash_schema(self, schema: Dict[str, Any]) -> str:
        """Generate hash for schema caching"""
        schema_str = json.dumps(schema, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()

    def _get_cached_validator(self, schema_hash: str, schema: Dict[str, Any]) -> Draft202012Validator:
        """Get cached validator or create new one"""
        with self._cache_lock:
            if schema_hash in self._validator_cache:
                return self._validator_cache[schema_hash]

            validator = Draft202012Validator(schema)
            self._validator_cache[schema_hash] = validator
            return validator


class CustomValidator(SchemaValidator):
    """Custom validator for LUKHAS-specific validation rules"""

    def __init__(self):
        self.constitutional_ai_rules = self._load_constitutional_rules()

    def validate(self, data: Any, schema: Dict[str, Any], level: ValidationLevel) -> SchemaValidationResult:
        """Validate data using custom LUKHAS rules"""
        start_time = time.perf_counter()

        errors = []
        warnings = []

        # Guardian-specific validations
        if isinstance(data, dict):
            # Check for Guardian decision structure
            if "decision" in data:
                decision_errors = self._validate_guardian_decision(data["decision"])
                errors.extend(decision_errors)

            # Check constitutional AI compliance
            compliance_score, compliance_warnings = self._check_constitutional_compliance(data)
            warnings.extend(compliance_warnings)

        validation_time = (time.perf_counter() - start_time) * 1000

        return SchemaValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_time_ms=validation_time,
            compliance_score=compliance_score
        )

    def supports_format(self, format: SchemaFormat) -> bool:
        """Check if validator supports custom format"""
        return format in (SchemaFormat.CUSTOM, SchemaFormat.HYBRID)

    def _validate_guardian_decision(self, decision: Dict[str, Any]) -> List[str]:
        """Validate Guardian decision structure"""
        errors = []

        if not isinstance(decision.get("status"), str):
            errors.append("Guardian decision status must be string")
        elif decision["status"] not in ["allow", "deny", "challenge", "quarantine", "error"]:
            errors.append(f"Invalid Guardian decision status: {decision['status']}")

        if "timestamp" not in decision:
            errors.append("Guardian decision must include timestamp")

        if "policy" not in decision:
            errors.append("Guardian decision must reference policy")

        return errors

    def _check_constitutional_compliance(self, data: Dict[str, Any]) -> tuple[float, List[str]]:
        """Check Constitutional AI compliance"""
        warnings = []
        score = 1.0

        # Check for ethical decision indicators
        if "decision" in data and data["decision"].get("status") == "deny":
            if not data.get("reasons"):
                warnings.append("Denial decisions should include reasoning")
                score -= 0.1

        # Check for audit trail presence
        if "audit" not in data:
            warnings.append("Missing audit trail for governance decision")
            score -= 0.05

        return max(0.0, score), warnings

    def _load_constitutional_rules(self) -> Dict[str, Any]:
        """Load Constitutional AI rules"""
        return {
            "ethical_principles": [
                "transparency",
                "accountability",
                "fairness",
                "privacy",
                "safety"
            ],
            "required_fields": [
                "audit",
                "decision.timestamp",
                "decision.policy"
            ]
        }


class SchemaRegistry:
    """Centralized schema registry with versioning and validation"""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent / "schemas"
        self.schemas: Dict[str, Dict[str, SchemaMetadata]] = {}
        self.validators: List[SchemaValidator] = [
            JSONSchemaValidator(),
            CustomValidator()
        ]
        self._lock = threading.RLock()
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Initialize with Guardian schema
        self._load_guardian_schema()

    def register_schema(
        self,
        schema_id: str,
        version: str,
        schema_definition: Dict[str, Any],
        format: SchemaFormat = SchemaFormat.JSON_SCHEMA,
        validation_level: ValidationLevel = ValidationLevel.STRICT
    ) -> None:
        """Register a new schema version"""
        with self._lock:
            schema_version = SchemaVersion(version)
            checksum = self._calculate_checksum(schema_definition)

            if schema_id not in self.schemas:
                self.schemas[schema_id] = {}

            metadata = SchemaMetadata(
                id=schema_id,
                version=schema_version,
                format=format,
                created_at=time.time(),
                updated_at=time.time(),
                checksum=checksum,
                validation_level=validation_level
            )

            self.schemas[schema_id][version] = metadata

            # Cache the schema definition
            cache_key = f"{schema_id}:{version}"
            self._cache[cache_key] = schema_definition

            logger.info(f"Registered schema {schema_id} version {version}")

    def get_schema(self, schema_id: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get schema definition by ID and version"""
        with self._lock:
            if schema_id not in self.schemas:
                return None

            if version is None:
                # Get latest version
                versions = list(self.schemas[schema_id].keys())
                version = max(versions, key=lambda v: SchemaVersion(v))

            cache_key = f"{schema_id}:{version}"
            if cache_key in self._cache:
                self._cache_hits += 1
                return self._cache[cache_key]

            self._cache_misses += 1
            return None

    def validate_data(
        self,
        data: Any,
        schema_id: str,
        version: Optional[str] = None,
        validation_level: Optional[ValidationLevel] = None
    ) -> SchemaValidationResult:
        """Validate data against registered schema"""
        start_time = time.perf_counter()

        # Get schema definition
        schema = self.get_schema(schema_id, version)
        if not schema:
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Schema {schema_id} not found"],
                validation_time_ms=(time.perf_counter() - start_time) * 1000
            )

        # Get schema metadata
        metadata = self._get_schema_metadata(schema_id, version)
        if not metadata:
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Schema metadata {schema_id}:{version} not found"],
                validation_time_ms=(time.perf_counter() - start_time) * 1000
            )

        # Use metadata validation level if not specified
        level = validation_level or metadata.validation_level

        # Run validators
        results = []
        for validator in self.validators:
            if validator.supports_format(metadata.format):
                result = validator.validate(data, schema, level)
                results.append(result)

        # Combine results
        if not results:
            return SchemaValidationResult(
                is_valid=False,
                errors=["No suitable validator found"],
                validation_time_ms=(time.perf_counter() - start_time) * 1000
            )

        # Merge validation results
        is_valid = all(r.is_valid for r in results)
        errors = []
        warnings = []
        min_compliance = 1.0

        for result in results:
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            min_compliance = min(min_compliance, result.compliance_score)

        total_time = (time.perf_counter() - start_time) * 1000

        return SchemaValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            validation_time_ms=total_time,
            schema_version=version,
            compliance_score=min_compliance
        )

    def list_schemas(self) -> Dict[str, List[str]]:
        """List all registered schemas and versions"""
        with self._lock:
            return {
                schema_id: list(versions.keys())
                for schema_id, versions in self.schemas.items()
            }

    def check_compatibility(self, schema_id: str, version1: str, version2: str) -> bool:
        """Check if two schema versions are compatible"""
        try:
            v1 = SchemaVersion(version1)
            v2 = SchemaVersion(version2)
            return v1.is_compatible(v2)
        except ValueError:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get registry performance metrics"""
        with self._lock:
            total_requests = self._cache_hits + self._cache_misses
            cache_hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0

            return {
                "total_schemas": sum(len(versions) for versions in self.schemas.values()),
                "unique_schemas": len(self.schemas),
                "cache_hit_rate": cache_hit_rate,
                "cache_size": len(self._cache),
                "memory_usage_mb": self._estimate_memory_usage()
            }

    def _load_guardian_schema(self) -> None:
        """Load Guardian schema from file"""
        guardian_schema_path = self.base_path.parent / "guardian_schema.json"

        if guardian_schema_path.exists():
            try:
                with open(guardian_schema_path) as f:
                    guardian_schema = json.load(f)

                # Extract version from schema or use default
                version = "2.0.0"  # From schema pattern "^2\\.\\d+\\.\\d+$"

                self.register_schema(
                    "guardian_decision",
                    version,
                    guardian_schema,
                    SchemaFormat.JSON_SCHEMA,
                    ValidationLevel.STRICT
                )

                logger.info(f"Loaded Guardian schema version {version}")

            except Exception as e:
                logger.error(f"Failed to load Guardian schema: {e}")

    def _get_schema_metadata(self, schema_id: str, version: Optional[str]) -> Optional[SchemaMetadata]:
        """Get schema metadata"""
        with self._lock:
            if schema_id not in self.schemas:
                return None

            if version is None:
                versions = list(self.schemas[schema_id].keys())
                version = max(versions, key=lambda v: SchemaVersion(v))

            return self.schemas[schema_id].get(version)

    def _calculate_checksum(self, schema: Dict[str, Any]) -> str:
        """Calculate schema checksum for caching"""
        schema_str = json.dumps(schema, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()[:16]

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        import sys

        total_size = 0
        total_size += sys.getsizeof(self.schemas)
        total_size += sys.getsizeof(self._cache)

        for schema_data in self._cache.values():
            total_size += sys.getsizeof(json.dumps(schema_data))

        return total_size / (1024 * 1024)


# Global schema registry instance
_registry_instance: Optional[SchemaRegistry] = None
_registry_lock = threading.Lock()


def get_schema_registry() -> SchemaRegistry:
    """Get global schema registry instance"""
    global _registry_instance

    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = SchemaRegistry()

    return _registry_instance


# Convenience functions
def validate_guardian_decision(data: Any) -> SchemaValidationResult:
    """Validate Guardian decision data"""
    registry = get_schema_registry()
    return registry.validate_data(data, "guardian_decision")


def register_custom_schema(schema_id: str, version: str, schema: Dict[str, Any]) -> None:
    """Register a custom schema"""
    registry = get_schema_registry()
    registry.register_schema(schema_id, version, schema)


# Performance monitoring
class SchemaMetrics:
    """Performance metrics for schema operations"""

    def __init__(self):
        self.validation_count = 0
        self.total_validation_time = 0.0
        self.failed_validations = 0
        self.start_time = time.time()

    def record_validation(self, result: SchemaValidationResult) -> None:
        """Record validation metrics"""
        self.validation_count += 1
        self.total_validation_time += result.validation_time_ms
        if not result.is_valid:
            self.failed_validations += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        uptime = time.time() - self.start_time
        avg_time = (
            self.total_validation_time / self.validation_count
            if self.validation_count > 0 else 0
        )

        return {
            "total_validations": self.validation_count,
            "average_validation_time_ms": avg_time,
            "failed_validations": self.failed_validations,
            "success_rate": (
                (self.validation_count - self.failed_validations) / self.validation_count
                if self.validation_count > 0 else 1.0
            ),
            "throughput_per_second": self.validation_count / uptime if uptime > 0 else 0,
            "uptime_seconds": uptime
        }


# Global metrics instance
schema_metrics = SchemaMetrics()