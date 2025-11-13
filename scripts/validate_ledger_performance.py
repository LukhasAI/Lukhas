#!/usr/bin/env python3
"""
LUKHAS Ledger Performance Validation Script
==========================================

CI/CD gate for T4/0.01% excellence compliance:
- Validates append p95 <50ms with 2k samples
- Checks schema validation against ledger.v2.json
- Generates evidence artifacts
- Fails CI if requirements not met
"""

import argparse
import asyncio
import json
import logging
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import jsonschema
from ledger.event_bus import (
    AsyncEventBus,
)
from ledger.events import (
    ConsentGrantedEvent,
    ConsentType,
    validate_event_schema,
)
from ledger.metrics import (
    get_metrics,
    reset_metrics,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[LEDGER-VALIDATION] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LedgerPerformanceValidator:
    """
    T4/0.01% excellence performance validator for ledger operations.

    Implements CI gate requirements:
    - p95 append <50ms (2k samples)
    - 100% schema validation
    - Deterministic replay
    - Evidence generation
    """

    def __init__(self, sample_count: int = 2000, schema_path: Optional[str] = None):
        self.sample_count = sample_count
        self.schema_path = Path(schema_path) if schema_path else project_root / "schemas" / "ledger.v2.json"
        self.temp_dir = None
        self.event_bus = None
        self.metrics = None
        self.validation_results = {}

        logger.info(f"LedgerPerformanceValidator initialized with {sample_count} samples")

    async def __aenter__(self):
        """Async context manager entry"""
        # Setup temporary environment
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ledger_validation_"))

        # Initialize event bus
        event_bus_path = self.temp_dir / "validation_events.db"
        self.event_bus = AsyncEventBus(str(event_bus_path))

        # Reset and get metrics
        reset_metrics()
        self.metrics = get_metrics()

        logger.info(f"Validation environment setup in: {self.temp_dir}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup
        if self.temp_dir:
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Cleanup failed: {e}")

    def load_json_schema(self) -> dict[str, Any]:
        """Load and validate JSON schema"""
        try:
            with open(self.schema_path) as f:
                schema = json.load(f)

            # Validate schema itself
            jsonschema.Draft7Validator.check_schema(schema)
            logger.info(f"Loaded valid JSON schema from {self.schema_path}")
            return schema

        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def generate_test_events(self) -> list[ConsentGrantedEvent]:
        """Generate test events for validation"""
        logger.info(f"Generating {self.sample_count} test events...")

        events = []
        for i in range(self.sample_count):
            event = ConsentGrantedEvent(
                lid=f"USR-{i:06d}",
                consent_id=f"CONSENT-{'a' * 24}{i:08x}",
                resource_type="email" if i % 2 == 0 else "documents",
                scopes=["read", "list"] if i % 3 == 0 else ["read"],
                purpose=f"Test validation {i}",
                lawful_basis="consent",
                consent_type=ConsentType.EXPLICIT,
                data_categories=["email_content"] if i % 2 == 0 else ["document_metadata"],
                third_parties=[] if i % 4 == 0 else ["analytics_service"],
                automated_decision_making=i % 10 == 0,
                profiling=i % 15 == 0,
                children_data=i % 50 == 0,
                sensitive_data=i % 100 == 0,
                trace_id=f"LT-{'b' * 24}{i:08x}",
                correlation_id=f"REQ-{i:08d}",
            )
            events.append(event)

        logger.info(f"Generated {len(events)} test events")
        return events

    async def validate_schema_compliance(self, events: list[ConsentGrantedEvent]) -> dict[str, Any]:
        """Validate all events against JSON schema"""
        logger.info("Validating schema compliance...")

        schema = self.load_json_schema()
        validator = jsonschema.Draft7Validator(schema)

        validation_errors = []
        schema_valid_count = 0

        for i, event in enumerate(events):
            # Test built-in schema validation
            if not validate_event_schema(event):
                validation_errors.append(f"Event {i} failed built-in validation")
                continue

            # Test JSON schema validation
            event_dict = event.to_dict()
            try:
                validator.validate(event_dict)
                schema_valid_count += 1
            except jsonschema.ValidationError as e:
                validation_errors.append(f"Event {i} JSON schema error: {e.message}")

        # Check sample for detailed validation
        if events:
            sample_event = events[0]
            try:
                validator.validate(sample_event.to_dict())
                logger.info("Sample event passes JSON schema validation")
            except jsonschema.ValidationError as e:
                logger.error(f"Sample event schema validation failed: {e}")

        compliance_rate = schema_valid_count / len(events) if events else 0

        result = {
            'total_events': len(events),
            'schema_valid_events': schema_valid_count,
            'compliance_rate': compliance_rate,
            'validation_errors': validation_errors[:10],  # Limit to first 10 errors
            'schema_compliant': compliance_rate == 1.0,
        }

        logger.info(f"Schema compliance: {compliance_rate:.2%} ({schema_valid_count}/{len(events)})")
        return result

    async def validate_append_performance(self, events: list[ConsentGrantedEvent]) -> dict[str, Any]:
        """Validate append performance meets T4 requirements"""
        logger.info(f"Validating append performance with {len(events)} events...")

        append_times = []
        failed_appends = 0

        # Measure append performance
        for i, event in enumerate(events):
            try:
                start_time = time.perf_counter()
                await self.event_bus.append_event(event)
                end_time = time.perf_counter()

                append_time_ms = (end_time - start_time) * 1000
                append_times.append(append_time_ms)

                # Log progress every 500 events
                if (i + 1) % 500 == 0:
                    avg_time = statistics.mean(append_times[-500:])
                    logger.info(f"Processed {i + 1}/{len(events)} events, recent avg: {avg_time:.2f}ms")

            except Exception as e:
                logger.error(f"Failed to append event {i}: {e}")
                failed_appends += 1

        if not append_times:
            return {
                'append_times_ms': [],
                'performance_compliant': False,
                'error': 'No successful appends recorded'
            }

        # Calculate statistics
        p50_ms = statistics.median(append_times)
        p95_ms = statistics.quantiles(append_times, n=20)[18]  # 95th percentile
        p99_ms = statistics.quantiles(append_times, n=100)[98]  # 99th percentile
        avg_ms = statistics.mean(append_times)
        max_ms = max(append_times)
        min_ms = min(append_times)

        # T4/0.01% excellence check
        t4_compliant = p95_ms < 50.0

        result = {
            'total_samples': len(events),
            'successful_appends': len(append_times),
            'failed_appends': failed_appends,
            'append_times_ms': append_times,
            'statistics': {
                'p50_ms': p50_ms,
                'p95_ms': p95_ms,
                'p99_ms': p99_ms,
                'avg_ms': avg_ms,
                'max_ms': max_ms,
                'min_ms': min_ms,
            },
            'performance_compliant': t4_compliant,
            't4_requirement_ms': 50.0,
            'performance_margin_ms': 50.0 - p95_ms,
        }

        logger.info(f"Append performance - P95: {p95_ms:.2f}ms, Avg: {avg_ms:.2f}ms, T4 compliant: {t4_compliant}")
        return result

    async def validate_replay_determinism(self) -> dict[str, Any]:
        """Validate replay determinism (100% requirement)"""
        logger.info("Validating replay determinism...")

        # Perform multiple replays
        replay_results = []

        for attempt in range(3):
            replay_events = []
            start_time = time.perf_counter()

            replay_iterator = await self.event_bus.replay(1)  # From offset 1
            async for event, offset in replay_iterator:
                replay_events.append({
                    'event_id': event.event_id,
                    'offset': offset.offset,
                    'hash': event.compute_hash(),
                    'timestamp': event.timestamp,
                })

            replay_time_ms = (time.perf_counter() - start_time) * 1000

            replay_results.append({
                'attempt': attempt + 1,
                'events': replay_events,
                'replay_time_ms': replay_time_ms,
                'event_count': len(replay_events),
            })

            logger.info(f"Replay attempt {attempt + 1}: {len(replay_events)} events in {replay_time_ms:.2f}ms")

        # Check determinism
        deterministic = True
        first_replay = replay_results[0]['events']

        for i in range(1, len(replay_results)):
            current_replay = replay_results[i]['events']

            if len(first_replay) != len(current_replay):
                deterministic = False
                break

            for j in range(len(first_replay)):
                if (first_replay[j]['event_id'] != current_replay[j]['event_id'] or
                    first_replay[j]['offset'] != current_replay[j]['offset'] or
                    first_replay[j]['hash'] != current_replay[j]['hash']):
                    deterministic = False
                    break

            if not deterministic:
                break

        result = {
            'replay_attempts': len(replay_results),
            'deterministic': deterministic,
            'event_count': len(first_replay) if first_replay else 0,
            'replay_times_ms': [r['replay_time_ms'] for r in replay_results],
            'avg_replay_time_ms': statistics.mean([r['replay_time_ms'] for r in replay_results]),
        }

        logger.info(f"Replay determinism: {deterministic}, {result['event_count']} events replayed")
        return result

    async def generate_evidence_artifact(self) -> dict[str, Any]:
        """Generate evidence artifact for T4 compliance"""
        timestamp = time.time()

        artifact = {
            'validation_metadata': {
                'timestamp': timestamp,
                'iso_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp)),
                'validator_version': '2.0.0',
                'sample_count': self.sample_count,
                'schema_path': str(self.schema_path),
                'environment': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                },
            },
            'validation_results': self.validation_results,
            'compliance_summary': {
                'schema_compliant': self.validation_results.get('schema', {}).get('schema_compliant', False),
                'performance_compliant': self.validation_results.get('performance', {}).get('performance_compliant', False),
                'replay_deterministic': self.validation_results.get('replay', {}).get('deterministic', False),
                'overall_compliant': False,  # Will be calculated
            }
        }

        # Calculate overall compliance
        compliance_checks = [
            artifact['compliance_summary']['schema_compliant'],
            artifact['compliance_summary']['performance_compliant'],
            artifact['compliance_summary']['replay_deterministic'],
        ]
        artifact['compliance_summary']['overall_compliant'] = all(compliance_checks)

        return artifact

    async def run_full_validation(self) -> dict[str, Any]:
        """Run complete validation suite"""
        logger.info("Starting T4/0.01% excellence validation...")

        # Generate test events
        events = self.generate_test_events()

        # Run validation tests
        self.validation_results['schema'] = await self.validate_schema_compliance(events)
        self.validation_results['performance'] = await self.validate_append_performance(events)
        self.validation_results['replay'] = await self.validate_replay_determinism()

        # Generate evidence artifact
        artifact = await self.generate_evidence_artifact()

        # Save evidence artifact
        artifacts_dir = project_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        artifact_filename = f"ledger_validation_{int(time.time())}.json"
        artifact_path = artifacts_dir / artifact_filename

        with open(artifact_path, 'w') as f:
            json.dump(artifact, f, indent=2, default=str)

        logger.info(f"Evidence artifact saved: {artifact_path}")

        # Summary results
        overall_compliant = artifact['compliance_summary']['overall_compliant']
        p95_ms = self.validation_results['performance']['statistics']['p95_ms']
        schema_rate = self.validation_results['schema']['compliance_rate']
        deterministic = self.validation_results['replay']['deterministic']

        logger.info("=" * 60)
        logger.info("T4/0.01% EXCELLENCE VALIDATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Schema Compliance:     {schema_rate:.1%}")
        logger.info(f"Performance P95:       {p95_ms:.2f}ms (target: <50ms)")
        logger.info(f"Replay Deterministic:  {deterministic}")
        logger.info(f"Overall Compliant:     {overall_compliant}")
        logger.info(f"Evidence Artifact:     {artifact_path}")
        logger.info("=" * 60)

        return artifact


async def main():
    """Main validation runner"""
    parser = argparse.ArgumentParser(description="LUKHAS Ledger Performance Validation")
    parser.add_argument("--samples", type=int, default=2000, help="Number of test samples (default: 2000)")
    parser.add_argument("--schema", type=str, help="Path to JSON schema file")
    parser.add_argument("--fail-on-non-compliance", action="store_true", help="Exit with error code if not compliant")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        async with LedgerPerformanceValidator(args.samples, args.schema) as validator:
            artifact = await validator.run_full_validation()

            # Check for CI failure
            if args.fail_on_non_compliance and not artifact['compliance_summary']['overall_compliant']:
                logger.error("VALIDATION FAILED - T4/0.01% excellence requirements not met")
                sys.exit(1)
            else:
                logger.info("VALIDATION COMPLETED SUCCESSFULLY")
                sys.exit(0)

    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
