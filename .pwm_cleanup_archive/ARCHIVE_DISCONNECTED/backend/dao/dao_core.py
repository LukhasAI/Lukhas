"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : dao_core.py                                               │
│ 🧾 DESCRIPTION : Symbolic DAO evaluation engine for LUKHAS AID proposals    │
│ 🧩 TYPE        : Governance Logic       🔧 VERSION: v1.0.0                  │
│ 🖋️ AUTHOR      : LUKHAS AID SYSTEMS       📅 CREATED: 2025-05-02              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - json, os                                                               │
│   - Requires: proposals/ folder, voters_registry.json, approved_log.json  │
└────────────────────────────────────────────────────────────────────────────┘
"""

import json
import os
from pathlib import Path

PROPOSALS_DIR = Path("dao/proposals/")
VOTERS_FILE = Path("dao/voters_registry.json")
APPROVED_LOG = Path("dao/approved_proposals.json")


def load_registry():
    if VOTERS_FILE.exists():
        with open(VOTERS_FILE) as f:
            return json.load(f)
    else:
        print("[⚠️] Voter registry not found.")
        return {}


def evaluate_proposal(filename: str) -> dict:
    path = PROPOSALS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Proposal not found: {filename}")

    with open(path) as f:
        proposal = json.load(f)

    registry = load_registry()
    quorum = proposal.get("required_quorum", 3)
    votes = proposal.get("votes", {})
    approvals = [k for k, v in votes.items() if v and registry.get(k)]

    proposal["status"] = "approved" if len(approvals) >= quorum else "pending"

    if proposal["status"] == "approved":
        if APPROVED_LOG.exists():
            with open(APPROVED_LOG, "r+") as f:
                approved = json.load(f)
                approved.append(proposal)
                f.seek(0)
                json.dump(approved, f, indent=2)
        else:
            with open(APPROVED_LOG, "w") as f:
                json.dump([proposal], f, indent=2)

        print(f"[✅] Proposal approved: {proposal['id']}")
    else:
        print(f"[⏳] Proposal pending quorum: {proposal['id']}")

    return proposal


if __name__ == "__main__":
    proposals = sorted(os.listdir(PROPOSALS_DIR))
    for file in proposals:
        if file.endswith(".json"):
            result = evaluate_proposal(file)
            print(f"[📋] Evaluated proposal: {file}, Status: {result['status']}")
