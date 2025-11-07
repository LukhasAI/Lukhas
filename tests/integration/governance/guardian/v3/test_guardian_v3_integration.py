import pytest
import sqlite3
import time
import re
import json
from datetime import datetime, timezone
from guardian.emit import (
    emit_guardian_decision,
    validate_dual_approval,
    emit_exemption,
)

# --- Test Infrastructure ---

class SQLiteAdapter:
    """A wrapper for a SQLite connection that translates psycopg2-style named queries."""
    def __init__(self, connection):
        self._connection = connection

    def execute(self, query, params):
        # Find all named parameters like %(key)s
        keys = re.findall(r'%\((\w+)\)s', query)
        # Replace each named parameter with '?'
        new_query = re.sub(r'%\((\w+)\)s', '?', query)
        # Create a tuple of values in the correct order
        new_params = tuple(params.get(key) for key in keys)
        return self._connection.execute(new_query, new_params)

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        return self._connection.commit()

@pytest.fixture
def db_connection():
    """Fixture to set up an in-memory SQLite database for integration testing."""
    conn = sqlite3.connect(":memory:")
    adapter = SQLiteAdapter(conn)

    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE guardian_exemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id TEXT,
        tenant TEXT,
        env TEXT,
        lambda_id TEXT,
        action TEXT,
        rule_name TEXT,
        tags TEXT,
        confidences TEXT,
        band TEXT,
        user_consent_timestamp TEXT,
        consent_method TEXT,
        purpose TEXT,
        retention_days INTEGER,
        justification TEXT,
        override_requested BOOLEAN,
        override_granted BOOLEAN,
        approver1_id TEXT,
        approver2_id TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    yield adapter
    conn.close()

def get_user_tier_for_test(user_id: str) -> int:
    """A concrete implementation of get_tier_fn for testing."""
    if "t4_admin" in user_id:
        return 4
    if "t5_supervisor" in user_id:
        return 5
    if "t3_user" in user_id:
        return 3
    return 0

# --- Integration Tests ---

def test_end_to_end_decision_flow(db_connection):
    """
    Tests the end-to-end flow of emitting a decision and verifying it's written to the database.
    This is an integration test because it verifies the interaction with a real DB (in-memory SQLite).
    """
    plan_id = "test_plan_123"
    lambda_id = "test_lambda_abc"

    emit_guardian_decision(
        db=db_connection,
        plan_id=plan_id,
        lambda_id=lambda_id,
        action="allow",
        rule_name="test_rule",
        tags=["automation", "low_risk"],
        confidences={"automation": 0.9, "low_risk": 0.95},
        band="minor",
    )

    # Verify the record was inserted correctly
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM guardian_exemptions WHERE plan_id = ?", (plan_id,))
    record = cursor.fetchone()

    assert record is not None
    assert record[1] == plan_id
    assert record[5] == "allow"
    assert record[9] == "minor"
    assert "automation" in json.loads(record[7]) # tags are stored as JSON string

def test_threat_detection_and_consent_violation(db_connection):
    """
    Tests the internal logic integration where operations with 'pii' tags
    must have consent, otherwise a ValueError is raised.
    """
    with pytest.raises(ValueError, match="Consent evidence required for FINANCIAL/PII operations"):
        emit_guardian_decision(
            db=db_connection,
            plan_id="pii_violation_plan",
            lambda_id="pii_lambda",
            action="block",
            rule_name="pii_rule",
            tags=["pii", "high_risk"],
            confidences={"pii": 0.99},
            band="critical",
        )

def test_emergency_override_and_dual_approval_flow(db_connection):
    """
    Tests the integration between the dual approval logic and the decision emission system
    for a critical emergency override.
    """
    approver1 = "t4_admin_1"
    approver2 = "t5_supervisor_2"
    plan_id = "emergency_override_plan"

    # 1. First, validate the approvers (cross-module interaction simulation)
    is_valid = validate_dual_approval(approver1, approver2, get_user_tier_for_test)
    assert is_valid

    # 2. If valid, emit the decision with the override granted
    emit_guardian_decision(
        db=db_connection,
        plan_id=plan_id,
        lambda_id="emergency_lambda",
        action="block", # The initial action was 'block'
        rule_name="critical_rule",
        tags=["emergency"],
        confidences={"emergency": 1.0},
        band="critical",
        override_requested=True,
        override_granted=True,
        approver1_id=approver1,
        approver2_id=approver2,
        justification="Emergency override approved."
    )

    # 3. Verify the override was correctly logged in the database
    cursor = db_connection.cursor()
    cursor.execute("SELECT override_granted, approver1_id, approver2_id FROM guardian_exemptions WHERE plan_id = ?", (plan_id,))
    record = cursor.fetchone()

    assert record is not None
    assert record[0] == 1  # override_granted (SQLite uses 1 for True)
    assert record[1] == approver1
    assert record[2] == approver2

def test_multi_agent_coordination_failures():
    """
    Tests the failure modes of the dual approval system. This is a component integration
    test for the validation logic.
    """
    # Failure case 1: Same approver
    with pytest.raises(ValueError, match="Dual approval requires different approvers"):
        validate_dual_approval("t4_admin_1", "t4_admin_1", get_user_tier_for_test)

    # Failure case 2: Insufficient tier - make regex more flexible
    with pytest.raises(PermissionError, match=r"Critical overrides require T4\+ approvers.*"):
        validate_dual_approval("t4_admin_1", "t3_user", get_user_tier_for_test)

def test_performance_of_critical_path(db_connection):
    """
    Tests the performance of the critical emission path against a real (in-memory) database.
    This provides a more realistic performance measure than a mocked object.
    """
    iterations = 100

    start_time = time.time()
    for i in range(iterations):
        emit_guardian_decision(
            db=db_connection,
            plan_id=f"perf_plan_{i}",
            lambda_id="perf_lambda",
            action="allow",
            rule_name="perf_rule",
            tags=["perf_test"],
            confidences={"perf_test": 1.0},
            band="minor"
        )
    end_time = time.time()

    duration = end_time - start_time
    avg_time_ms = (duration / iterations) * 1000

    # The threshold is higher than before because we are now including real DB operations.
    # 10ms is a reasonable starting point for an in-memory DB.
    threshold_ms = 10
    assert avg_time_ms < threshold_ms, f"Average time was {avg_time_ms:.4f}ms, which is over the {threshold_ms}ms threshold."
