#!/usr/bin/env python3
"""
Matrix Schema v3 Presence Tests

Validates that all Matrix contracts contain the required v3 placeholders
with expected types and default values.
"""

import glob
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Expected v3 sections and their required properties
V3_SECTIONS = {
    "tokenization": {
        "enabled": bool,
        "network": str,
        "standard": str,
        "mint_address": (str, type(None)),
        "token_id": (str, type(None)),
        "anchor_txid": (str, type(None)),
        "anchor_block": (int, type(None)),
        "anchor_digest": (str, type(None)),
        "anchor_merkle_root": (str, type(None)),
        "issuer": (str, type(None)),
        "policy_version": (str, type(None)),
        "proof_uri": (str, type(None)),
        "note": (str, type(None))
    },
    "glyph_provenance": {
        "glyph_signature": (str, type(None)),
        "entropy_phase": (str, type(None)),
        "drift_index": (float, int, type(None)),
        "attractor_state": (str, type(None))
    },
    "dream_provenance": {
        "last_dream_cid": (str, type(None)),
        "drift_delta": (float, int, type(None)),
        "recurrence_score": (float, int, type(None)),
        "dream_depth": (int, type(None)),
        "coherence_index": (float, int, type(None))
    },
    "guardian_check": {
        "enabled": bool,
        "policy_ref": str,
        "dissonance_threshold": (float, int),
        "last_check_timestamp": (str, type(None)),
        "drift_detection": (bool, type(None))
    },
    "biosymbolic_map": {
        "compound": str,
        "role": str,
        "state": str,
        "pathway_coupling": (list, type(None)),
        "symbolic_ph": (float, int, type(None))
    },
    "quantum_proof": {
        "zkp_circuit": (str, type(None)),
        "merkle_dag_root": (str, type(None)),
        "post_quantum_sig": (str, type(None)),
        "lattice_commitment": (str, type(None)),
        "entanglement_witness": (str, type(None)),
        "superposition_state": (str, type(None))
    }
}


def get_all_contracts() -> List[Path]:
    """Get all Matrix contract files."""
    return [Path(p) for p in sorted(glob.glob("contracts/matrix_*.json"))]


def load_contract(contract_path: Path) -> Dict[str, Any]:
    """Load a contract file as JSON."""
    with open(contract_path, encoding='utf-8') as f:
        return json.load(f)


class TestMatrixV3Presence:
    """Test that all Matrix contracts have v3 placeholders."""

    @pytest.mark.parametrize("contract_path", get_all_contracts())
    def test_v3_sections_present(self, contract_path: Path):
        """Test that all v3 sections are present in each contract."""
        contract = load_contract(contract_path)

        for section_name in V3_SECTIONS:
            assert section_name in contract, (
                f"Contract {contract_path.name} missing v3 section: {section_name}"
            )

    @pytest.mark.parametrize("contract_path", get_all_contracts())
    def test_v3_properties_present(self, contract_path: Path):
        """Test that all v3 properties are present with correct types."""
        contract = load_contract(contract_path)

        for section_name, expected_props in V3_SECTIONS.items():
            section = contract.get(section_name, {})

            for prop_name, expected_types in expected_props.items():
                assert prop_name in section, (
                    f"Contract {contract_path.name} missing property {section_name}.{prop_name}"
                )

                actual_value = section[prop_name]
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)

                assert isinstance(actual_value, expected_types), (
                    f"Contract {contract_path.name} property {section_name}.{prop_name} "
                    f"has type {type(actual_value).__name__}, expected one of: "
                    f"{[t.__name__ for t in expected_types]}"
                )

    def test_tokenization_defaults(self):
        """Test that tokenization has safe defaults."""
        contracts = get_all_contracts()

        for contract_path in contracts:
            contract = load_contract(contract_path)
            tokenization = contract.get("tokenization", {})

            # Should be disabled by default
            assert tokenization.get("enabled") is False, (
                f"Contract {contract_path.name} tokenization should be disabled by default"
            )

            # Should have a valid network
            network = tokenization.get("network")
            valid_networks = ["solana", "ethereum", "polygon", "base", "arbitrum",
                            "optimism", "near", "avalanche", "cosmos", "celestia", "tezos"]
            assert network in valid_networks, (
                f"Contract {contract_path.name} has invalid network: {network}"
            )

    def test_guardian_check_defaults(self):
        """Test that guardian_check has appropriate defaults."""
        contracts = get_all_contracts()

        for contract_path in contracts:
            contract = load_contract(contract_path)
            guardian = contract.get("guardian_check", {})

            # Should be enabled by default
            assert guardian.get("enabled") is True, (
                f"Contract {contract_path.name} guardian_check should be enabled by default"
            )

            # Should have a valid policy reference
            policy_ref = guardian.get("policy_ref")
            assert policy_ref is not None and isinstance(policy_ref, str), (
                f"Contract {contract_path.name} guardian_check.policy_ref should be a string"
            )

            # Dissonance threshold should be reasonable
            threshold = guardian.get("dissonance_threshold")
            if threshold is not None:
                assert 0 <= threshold <= 1, (
                    f"Contract {contract_path.name} guardian_check.dissonance_threshold "
                    f"should be between 0 and 1, got {threshold}"
                )

    def test_biosymbolic_defaults(self):
        """Test that biosymbolic_map has valid defaults."""
        contracts = get_all_contracts()

        valid_compounds = ["NAD+", "ATP", "NADPH", "CoA", "FAD", "heme", "glucose", "lactate", "null"]
        valid_roles = ["memory_repair", "energy_transfer", "signal_transduction",
                      "stress_response", "homeostasis", "null"]
        valid_states = ["baseline", "stressed", "resilient", "depleted", "saturated", "null"]

        for contract_path in contracts:
            contract = load_contract(contract_path)
            biosymbolic = contract.get("biosymbolic_map", {})

            compound = biosymbolic.get("compound")
            if compound is not None:
                assert compound in valid_compounds, (
                    f"Contract {contract_path.name} has invalid biosymbolic_map.compound: {compound}"
                )

            role = biosymbolic.get("role")
            if role is not None:
                assert role in valid_roles, (
                    f"Contract {contract_path.name} has invalid biosymbolic_map.role: {role}"
                )

            state = biosymbolic.get("state")
            if state is not None:
                assert state in valid_states, (
                    f"Contract {contract_path.name} has invalid biosymbolic_map.state: {state}"
                )

            # symbolic_ph should be valid if present
            ph = biosymbolic.get("symbolic_ph")
            if ph is not None:
                assert 0 <= ph <= 14, (
                    f"Contract {contract_path.name} biosymbolic_map.symbolic_ph "
                    f"should be between 0 and 14, got {ph}"
                )

    def test_contract_count(self):
        """Test that we have the expected number of contracts."""
        contracts = get_all_contracts()
        assert len(contracts) >= 65, (
            f"Expected at least 65 contracts, found {len(contracts)}"
        )

    def test_v3_schema_compliance(self):
        """Test that v3 fields don't break existing validation."""
        # This is a smoke test to ensure the presence of v3 fields
        # doesn't interfere with existing contract validation
        contracts = get_all_contracts()

        for contract_path in contracts:
            contract = load_contract(contract_path)

            # Basic structure requirements should still be met
            assert "schema_version" in contract
            assert "module" in contract
            assert "owner" in contract
            assert "gates" in contract

            # Identity section should still exist (if required)
            if contract.get("identity", {}).get("requires_auth", True):
                identity = contract.get("identity", {})
                assert "required_tiers" in identity or "required_tiers_numeric" in identity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
