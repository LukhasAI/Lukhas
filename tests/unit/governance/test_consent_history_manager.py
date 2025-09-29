from lukhas.governance.identity.core.sent.consent_history import ConsentHistoryManager

# ΛTAG: consent_history_test


class DummyTraceLogger:
    def __init__(self):
        self.logged = []

    def log_activity(self, user_id, activity_type, symbolic_data):
        self.logged.append((user_id, activity_type, symbolic_data))


def test_generate_record_hash_traces_and_is_deterministic():
    logger = DummyTraceLogger()
    manager = ConsentHistoryManager(config={}, trace_logger=logger)
    record = {
        "timestamp": "2025-01-01T00:00:00+00:00",
        "event_type": "granted",
        "scope_data": {"demo": True},
        "metadata": {},
    }
    h1 = manager._generate_record_hash(record, "user-1")
    h2 = manager._generate_record_hash(record, "user-1")
    assert h1 == h2
    assert logger.logged
    user, activity, data = logger.logged[-1]
    assert user == "user-1"
    assert activity == "consent_granted"
    assert data["hash"] == h1
