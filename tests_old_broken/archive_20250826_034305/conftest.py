#!/usr/bin/env python3
"""
LUKHAS AI Test Configuration and Fixtures
Risk-weighted testing with capability tokens and metadata-only mode
Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

# Add project paths
sys.path.append(str(Path(__file__).parent.parent))

# Import and apply the test logger patch to handle keyword arguments
from candidate.core.common.test_logger import patch_logger_for_tests

# Apply the patch globally for all tests
original_logger = patch_logger_for_tests()

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Environment setup for metadata-only mode by default
os.environ.setdefault('METADATA_ONLY', '1')


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def cap_token():
    """
    Session-scoped capability token for live adapter testing.
    Only available when explicitly requested via --live flag.
    """
    if os.getenv('LUKHAS_TEST_LIVE', '').lower() == 'true':
        return {
            'token': f'cap_{uuid.uuid4().hex}',
            'scopes': ['gmail.read', 'drive.read_metadata', 'dropbox.list'],
            'expires_at': time.time() + 3600
        }
    return None


@pytest.fixture
def lid_user():
    """ΛID test user fixture with <100ms perf target"""
    return {
        'user_id': f'lid_{uuid.uuid4().hex[:8]}',
        'namespace': 'test',
        'email': 'test@candidate.ai',
        'webauthn_registered': False,
        'created_at': time.time(),
        'perf_target_ms': 100
    }


@pytest.fixture
def webauthn_assertion():
    """WebAuthn assertion fixture for passkey testing"""
    return {
        'credential_id': uuid.uuid4().bytes,
        'client_data': b'{"challenge":"test_challenge","origin":"https://candidate.ai"}',
        'authenticator_data': b'\x00' * 37,  # Minimal valid authenticator data
        'signature': b'\x00' * 64,  # Placeholder signature
        'user_handle': uuid.uuid4().bytes
    }


@pytest.fixture
def consent_token(lid_user):
    """Consent token fixture with GDPR/CCPA compliance"""
    return {
        'subject_id': lid_user['user_id'],
        'purpose': 'test_processing',
        'granted': True,
        'scopes': ['basic', 'analytics'],
        'consent_id': f'consent_{uuid.uuid4().hex[:8]}',
        'timestamp': time.time(),
        'expires_at': time.time() + 86400,  # 24 hours
        'jurisdiction': 'GDPR'
    }


@pytest.fixture(autouse=True)
def metadata_only(monkeypatch, request):
    """
    Auto-apply metadata-only mode for adapters unless @pytest.mark.live is used.
    This prevents accidental live API calls and keeps CI deterministic.
    """
    if 'live' not in request.keywords:
        monkeypatch.setenv('METADATA_ONLY', '1')

        # Mock responses for metadata-only mode
        metadata_responses = {
            'gmail': {
                'messages': [
                    {'id': 'msg_001', 'subject': 'Test Email', 'from': 'sender@test.com'},
                    {'id': 'msg_002', 'subject': 'Another Test', 'from': 'another@test.com'}
                ]
            },
            'drive': {
                'files': [
                    {'id': 'file_001', 'name': 'test.txt', 'size': 1024, 'mimeType': 'text/plain'},
                    {'id': 'file_002', 'name': 'image.png', 'size': 2048, 'mimeType': 'image/png'}
                ]
            },
            'dropbox': {
                'entries': [
                    {'id': 'dbx_001', 'name': 'folder', 'path': '/folder', '.tag': 'folder'},
                    {'id': 'dbx_002', 'name': 'file.pdf', 'path': '/file.pdf', 'size': 3072}
                ]
            }
        }
        monkeypatch.setattr('os.environ.get', lambda k, d=None: '1' if k == 'METADATA_ONLY' else d)
        return metadata_responses
    else:
        monkeypatch.setenv('METADATA_ONLY', '0')
        monkeypatch.setenv('LUKHAS_TEST_LIVE', 'true')
        return None


@pytest.fixture
def perf_tracker():
    """Performance tracking fixture for p50/p95 measurement"""
    class PerfTracker:
        def __init__(self):
            self.measurements = {}

        def start(self, operation: str) -> float:
            start_time = time.perf_counter()
            return start_time

        def end(self, operation: str, start_time: float) -> float:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if operation not in self.measurements:
                self.measurements[operation] = []
            self.measurements[operation].append(elapsed_ms)
            return elapsed_ms

        def get_p50_p95(self, operation: str) -> Dict[str, float]:
            if operation not in self.measurements or not self.measurements[operation]:
                return {'p50': 0.0, 'p95': 0.0}

            sorted_times = sorted(self.measurements[operation])
            n = len(sorted_times)
            p50_idx = int(n * 0.5)
            p95_idx = int(n * 0.95)

            return {
                'p50': sorted_times[p50_idx] if p50_idx < n else sorted_times[-1],
                'p95': sorted_times[p95_idx] if p95_idx < n else sorted_times[-1],
                'mean': sum(sorted_times) / n,
                'count': n
            }

        def assert_budget(self, operation: str, p95_budget_ms: float):
            """Assert that p95 latency is within budget"""
            stats = self.get_p50_p95(operation)
            assert stats['p95'] <= p95_budget_ms, \
                f"{operation} p95 ({stats['p95']:.2f}ms) exceeds budget ({p95_budget_ms}ms)"

    return PerfTracker()


@pytest.fixture
def trace_collector():
    """Λ-trace collector for audit and rationale tracking"""
    class TraceCollector:
        def __init__(self):
            self.traces = []

        def add_trace(self, action: str, rationale: str, tags: Dict[str, Any] = None):
            trace = {
                'trace_id': f'λ_{uuid.uuid4().hex[:8]}',
                'timestamp': time.time(),
                'action': action,
                'rationale': rationale,
                'tags': tags or {},
                'privileged': tags.get('privileged', False) if tags else False
            }
            self.traces.append(trace)
            return trace

        def get_privileged_actions(self):
            return [t for t in self.traces if t['privileged']]

        def assert_rationale_exists(self, action: str):
            matching = [t for t in self.traces if t['action'] == action]
            assert matching, f"No Λ-trace found for action: {action}"
            assert all(t['rationale'] for t in matching), \
                f"Missing rationale for action: {action}"

    return TraceCollector()


# Performance budget constants
PERF_BUDGETS = {
    'auth_p95_ms': 150,  # Adjusted for test environment variance
    'handoff_p95_ms': 250,
    'e2e_demo_s': 3,
    'consent_check_ms': 50,
    'adapter_metadata_ms': 150
}


@pytest.fixture
def perf_budgets():
    """Performance budget fixture"""
    return PERF_BUDGETS.copy()


# Mark configuration for different test types
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "golden_path: golden path integration test"
    )
    config.addinivalue_line(
        "markers", "perf: performance test with budget validation"
    )
    config.addinivalue_line(
        "markers", "risk_critical: risk-critical path requiring full coverage"
    )


@pytest.fixture
async def consciousness():
    """Initialized UnifiedConsciousness instance for tests"""
    from core.api.service_stubs import UnifiedConsciousness

    c = UnifiedConsciousness()
    await c.initialize()
    return c


@pytest.fixture
async def memory_system():
    """Initialized MemoryManager instance for tests"""
    from core.api.service_stubs import MemoryManager

    m = MemoryManager()
    await m.initialize()
    return m


@pytest.fixture
async def guardian_system():
    """Initialized GuardianSystem instance for tests"""
    from core.api.service_stubs import GuardianSystem

    g = GuardianSystem()
    await g.initialize()
    return g


@pytest.fixture
async def symbolic_engine():
    """Initialized SymbolicEngine instance for tests"""
    from core.api.service_stubs import SymbolicEngine

    e = SymbolicEngine()
    await e.initialize()
    return e


@pytest.fixture
def symbolic_validator():
    """Provides symbolic glyph validation utilities"""

    class SymbolicValidator:
        # Define symbolic glyph categories
        GLYPH_CATEGORIES = {
            "security": ["🔐", "🔓", "🗝️", "🔑", "🔒"],
            "stability": ["🌿", "🧘", "💎", "⚓", "🏔️"],
            "chaos": ["🌪️", "🌀", "💥", "🚨", "⚡"],
            "thermal": ["🔥", "💨", "❄️", "🧊", "🌋"],
            "consciousness": ["🧠", "👁️", "🔮", "✨", "💫"],
            "protection": ["🛡️", "🏰", "⚔️", "🚨"],
            "transitions": ["→", "↔", "↑", "↓", "🔄"],
            "validation": ["✅", "❌", "⚠️", "🔄", "💪"],
        }

        def validate_sequence(
            self, sequence: list[str], expected_pattern: Optional[str] = None
        ) -> bool:
            """Validate symbolic sequence structure and coherence"""
            if not sequence:
                return False

            # Check for basic structure
            clean_sequence = [s for s in sequence if s != "→"]

            if len(clean_sequence) < 1:
                return False

            # If pattern specified, check exact match
            if expected_pattern:
                actual_pattern = "".join(clean_sequence)
                return actual_pattern == expected_pattern.replace("→", "")

            # Otherwise validate coherence
            return self.validate_coherence(clean_sequence)

        def validate_coherence(self, sequence: list[str]) -> bool:
            """Check if symbolic sequence has thematic coherence"""
            if len(sequence) <= 1:
                return True

            # Check if sequence follows logical progression
            progression_rules = [
                # Chaos to stability progressions
                (["🌪️", "🌀", "🌿"], "chaos_to_stability"),
                (["🔥", "💨", "❄️"], "thermal_cooling"),
                (["🚨", "🔒", "🛡️"], "alert_to_protection"),
                (["❌", "✅"], "error_correction"),
                (["⚓", "🧘", "🔒"], "consciousness_anchoring"),
            ]

            for rule_sequence, _ in progression_rules:
                if all(glyph in sequence for glyph in rule_sequence):
                    return True

            # Check category consistency
            for category, glyphs in self.GLYPH_CATEGORIES.items():
                if category == "transitions":
                    continue

                category_count = sum(1 for glyph in sequence if glyph in glyphs)
                if category_count == len(sequence):
                    return True  # All glyphs from same category

            return len(sequence) <= 3  # Allow short mixed sequences

    def extract_transitions(self, sequence: list[str]) -> list[str]:
        """Extract state transitions from symbolic sequence"""
        clean_sequence = [s for s in sequence if s != "→"]
        transitions = []

        for i in range(len(clean_sequence) - 1):
            transition = f"{clean_sequence[i]}→{clean_sequence[i+1]}"
            transitions.append(transition)

        return transitions

    def get_category(self, glyph: str) -> Optional[str]:
        """Get the category of a glyph"""
        for category, glyphs in self.GLYPH_CATEGORIES.items():
            if glyph in glyphs:
                return category
        return None

    return SymbolicValidator()


@pytest.fixture
def mock_consciousness_state():
    """Provides mock consciousness state data"""
    return {
        "current_state": "focused",
        "last_update": datetime.utcnow().isoformat(),
        "state_history": ["focused"],
        "system_phase": "phase_5_guardian",
        "entropy_score": 0.25,
        "drift_class": "stable",
    }


@pytest.fixture
def mock_entropy_data():
    """Provides mock entropy tracking data"""
    return {
        "metadata": {
            "version": "1.0.0",
            "window_size": 100,
            "last_updated": datetime.utcnow().isoformat(),
            "total_entries": 5,
        },
        "entries": [
            {
                "timestamp": (datetime.utcnow().isoformat()),
                "entropy_score": 0.15,
                "previous_state": "neutral",
                "current_state": "open",
                "drift_class": "stable",
                "symbolic_path": ["🔐", "🌿", "🪷"],
                "transition_type": "consent_grant",
            },
            {
                "timestamp": (datetime.utcnow().isoformat()),
                "entropy_score": 0.75,
                "previous_state": "open",
                "current_state": "turbulent",
                "drift_class": "unstable",
                "symbolic_path": ["🌪️", "⚡", "🚨"],
                "transition_type": "trust_decrease",
            },
        ],
    }


@pytest.fixture
def mock_guardian_threats():
    """Provides mock Guardian threat data"""
    return [
        {
            "threat_id": "drift_001",
            "threat_type": "drift_spike",
            "severity": 0.75,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "entropy_tracker",
            "symbolic_sequence": ["🌪️", "→", "🌀", "→", "🌿"],
            "intervention_required": True,
            "recommended_action": "drift_dampening",
        },
        {
            "threat_id": "entropy_002",
            "threat_type": "entropy_surge",
            "severity": 0.85,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "consciousness_broadcaster",
            "symbolic_sequence": ["🔥", "→", "💨", "→", "❄️"],
            "intervention_required": True,
            "recommended_action": "entropy_cooling",
        },
    ]


@pytest.fixture
def test_config():
    """Provides test configuration settings"""
    return {
        "test_timeouts": {
            "short": 5,  # 5 seconds
            "medium": 30,  # 30 seconds
            "long": 120,  # 2 minutes
        },
        "entropy_thresholds": {"stable": 0.3, "neutral": 0.7, "unstable": 1.0},
        "guardian_thresholds": {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.9,
        },
        "symbolic_validation": {
            "max_sequence_length": 5,
            "require_coherence": True,
            "allow_mixed_categories": False,
        },
    }


@pytest.fixture
def temp_lukhas_env(tmp_path):
    """Creates temporary LUKHAS environment for testing"""

    # Create directory structure
    lukhas_dirs = [
        "next_gen/stream",
        "next_gen/entropy_log",
        "next_gen/guardian",
        "next_gen/memory",
        "next_gen/quantum",
        "next_gen/bridge",
        "next_gen/security",
        "transmission_bundle",
        "guardian_audit/logs",
        "guardian_audit/exports",
        "tests",
    ]

    for dir_path in lukhas_dirs:
        (tmp_path / dir_path).mkdir(parents=True, exist_ok=True)

    # Create essential files
    consciousness_state = {
        "current_state": "focused",
        "last_update": datetime.utcnow().isoformat(),
        "state_history": ["focused"],
        "system_phase": "phase_5_guardian",
    }

    with open(tmp_path / "next_gen/stream/consciousness_state.json", "w") as f:
        json.dump(consciousness_state, f, indent=2)

    # Create mock component files
    component_files = [
        "next_gen/stream/consciousness_broadcaster.py",
        "next_gen/entropy_log/entropy_tracker.py",
        "next_gen/guardian/sentinel.py",
        "next_gen/guardian/intervene.yaml",
        "transmission_bundle/launch_transmission.py",
    ]

    for file_path in component_files:
        (tmp_path / file_path).touch()

    return tmp_path


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "symbolic: mark test as symbolic glyph validation test"
    )
    config.addinivalue_line("markers", "guardian: mark test as Guardian system test")
    config.addinivalue_line("markers", "entropy: mark test as entropy monitoring test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# --- Integration/E2E fixture aliases and utilities ---


@pytest.fixture
async def consciousness_system(consciousness):
    """Alias fixture for tests expecting 'consciousness_system'."""
    return consciousness


@pytest.fixture
async def emotion_engine():
    """Initialized EmotionEngine instance for tests."""
    from core.api.service_stubs import EmotionEngine

    e = EmotionEngine()
    await e.initialize()
    return e


@pytest.fixture
async def dream_engine():
    """Initialized DreamEngine instance for tests."""
    from core.api.service_stubs import DreamEngine

    d = DreamEngine()
    await d.initialize()
    return d


@pytest.fixture
def performance_metrics():
    """Simple performance metrics collector for performance tests."""
    return {
        "start_time": None,
        "end_time": None,
        "operations": [],
        "memory_usage": [],
        "response_times": [],
    }


class _SimpleEventBus:
    """Minimal async event bus for integration tests."""

    def __init__(self):
        self._subs = {}

    def subscribe(self, event_type: str, handler):
        self._subs.setdefault(event_type, []).append(handler)

    async def publish(self, event_type: str, event):
        for h in self._subs.get(event_type, []):
            if asyncio.iscoroutinefunction(h):
                await h(event)
            else:
                h(event)

    async def shutdown(self):
        self._subs.clear()


@pytest.fixture
async def event_bus():
    """Provide a simple event bus for tests that need it."""
    bus = _SimpleEventBus()
    yield bus
    await bus.shutdown()


# Test collection and reporting
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add symbolic marker to tests with 'symbolic' in name
        if "symbolic" in item.name.lower() or "glyph" in item.name.lower():
            item.add_marker(pytest.mark.symbolic)

        # Add guardian marker to guardian tests
        if "guardian" in item.name.lower() or "intervention" in item.name.lower():
            item.add_marker(pytest.mark.guardian)

        # Add entropy marker to entropy tests
        if "entropy" in item.name.lower() or "drift" in item.name.lower():
            item.add_marker(pytest.mark.entropy)

        # Add integration marker to integration tests
        if "integration" in item.name.lower() or "test_transmission" in item.name:
            item.add_marker(pytest.mark.integration)

        # Mark slow tests
        if "full_transmission" in item.name or "complete" in item.name:
            item.add_marker(pytest.mark.slow)


# Helper functions for tests
def assert_symbolic_sequence(
    sequence: list[str],
    expected_pattern: Optional[str] = None,
    coherence_required: bool = True,
):
    """Assert that a symbolic sequence is valid"""
    assert isinstance(sequence, list), "Sequence must be a list"
    assert len(sequence) > 0, "Sequence cannot be empty"

    # Clean sequence (remove arrows)
    clean_sequence = [s for s in sequence if s != "→"]
    assert len(clean_sequence) > 0, "Sequence must contain at least one glyph"

    # Check expected pattern if provided
    if expected_pattern:
        actual_pattern = "".join(clean_sequence)
        expected_clean = expected_pattern.replace("→", "")
        assert (
            actual_pattern == expected_clean
        ), f"Sequence pattern mismatch: expected {expected_clean}, got {actual_pattern}"

    # Check coherence if required
    if coherence_required:
        # This is a simplified coherence check
        # In practice, would use the SymbolicValidator
        assert len(clean_sequence) <= 5, "Sequence should not be excessively long"

        # Ensure all elements are strings (valid glyphs)
        for glyph in clean_sequence:
            assert isinstance(
                glyph, str
            ), f"All glyphs must be strings, got {type(glyph)}"
            assert len(glyph) > 0, "Glyphs cannot be empty strings"


def assert_entropy_range(entropy_value: float, expected_class: Optional[str] = None):
    """Assert entropy value is in valid range and class"""
    assert isinstance(entropy_value, (int, float)), "Entropy must be numeric"
    assert (
        0.0 <= entropy_value <= 1.0
    ), f"Entropy {entropy_value} outside valid range [0.0, 1.0]"

    if expected_class:
        if expected_class == "stable":
            assert (
                entropy_value < 0.3
            ), f"Stable entropy should be <0.3, got {entropy_value}"
        elif expected_class == "neutral":
            assert (
                0.3 <= entropy_value < 0.7
            ), f"Neutral entropy should be 0.3-0.7, got {entropy_value}"
        elif expected_class == "unstable":
            assert (
                entropy_value >= 0.7
            ), f"Unstable entropy should be >=0.7, got {entropy_value}"


def assert_guardian_threat_level(severity: float, expected_level: Optional[str] = None):
    """Assert Guardian threat severity and level"""
    assert isinstance(severity, (int, float)), "Severity must be numeric"
    assert 0.0 <= severity <= 1.0, f"Severity {severity} outside valid range [0.0, 1.0]"

    if expected_level:
        if expected_level == "low":
            assert severity < 0.5, f"Low threat should be <0.5, got {severity}"
        elif expected_level == "medium":
            assert (
                0.5 <= severity < 0.7
            ), f"Medium threat should be 0.5-0.7, got {severity}"
        elif expected_level == "high":
            assert (
                0.7 <= severity < 0.9
            ), f"High threat should be 0.7-0.9, got {severity}"
        elif expected_level == "critical":
            assert severity >= 0.9, f"Critical threat should be >=0.9, got {severity}"
