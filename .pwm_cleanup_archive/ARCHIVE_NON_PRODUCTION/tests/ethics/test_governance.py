"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - GOVERNANCE TESTS
║ Tests for the governance checker and sandbox runner modules.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_governance.py
║ Path: tests/ethics/test_governance.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Ethics Team | Jules Agent
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains tests for the governance checker and sandbox runner modules.
║ It validates that the safety logic is working as expected.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import os

from ethics.governance_checker import (
    is_fine_tunable,
    log_governance_trace,
    validate_symbolic_integrity,
)
from tools.sandbox_runner import list_forks, propose_fork


def test_is_fine_tunable():
    assert is_fine_tunable("dream") == True
    assert is_fine_tunable("core") == False


def test_validate_symbolic_integrity():
    assert validate_symbolic_integrity("dream", {"param": "value"}) == True
    assert validate_symbolic_integrity("core", {"param": "value"}) == False
    assert validate_symbolic_integrity("dream", {"SID": "some_id"}) == False


def test_propose_fork():
    user_id = "test_user"
    module_name = "dream"
    adjustment = {"param": "value"}

    # Clean up previous test runs
    if os.path.exists("lukhas/tools/user_fork_proposals.jsonl"):
        os.remove("lukhas/tools/user_fork_proposals.jsonl")

    assert propose_fork(user_id, module_name, adjustment) == True

    forks = list_forks()
    assert len(forks) == 1
    assert forks[0]["user_id"] == user_id
    assert forks[0]["module"] == module_name
    assert forks[0]["adjustment"] == adjustment


def test_propose_fork_invalid():
    user_id = "test_user"
    module_name = "core"
    adjustment = {"param": "value"}

    # Clean up previous test runs
    if os.path.exists("lukhas/tools/user_fork_proposals.jsonl"):
        os.remove("lukhas/tools/user_fork_proposals.jsonl")

    assert propose_fork(user_id, module_name, adjustment) == False
    assert len(list_forks()) == 0


def test_log_governance_trace():
    user_id = "test_user"
    module_name = "memory"
    adjustment = {"param": "new_value"}

    # Clean up previous test runs
    if os.path.exists("lukhas/ethics/governance_trace_log.md"):
        os.remove("lukhas/ethics/governance_trace_log.md")

    log_governance_trace(user_id, module_name, adjustment)

    with open("lukhas/ethics/governance_trace_log.md") as f:
        content = f.read()
        assert user_id in content
        assert module_name in content
        assert str(adjustment) in content


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: This file
║   - Coverage: 100%
║   - Linting: N/A
║
║ MONITORING:
║   - Metrics: N/A
║   - Logs: N/A
║   - Alerts: N/A
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: N/A
║   - Safety: N/A
║
║ REFERENCES:
║   - Docs: lukhas/docs/SAFETY_LOGIC_OVERVIEW.md
║   - Issues: N/A
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
