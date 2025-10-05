#!/usr/bin/env python3
"""
Matrix Provenance Smoke Tests

Validates that Matrix v3 provenance generation and verification work correctly
in sandbox mode. Ensures CAR files are generated with proper structure and
root CIDs are present in provenance reports.
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestProvenanceSmoke:
    """Smoke tests for Matrix v3 provenance functionality."""

    def test_provenance_files_exist(self):
        """Test that provenance artifacts exist after generation."""
        car_file = Path("artifacts/provenance.car")
        report_file = Path("artifacts/provenance_report.json")

        assert car_file.exists(), f"CAR file not found: {car_file}"
        assert report_file.exists(), f"Report file not found: {report_file}"

        # Check that files are not empty
        assert car_file.stat().st_size > 0, "CAR file is empty"
        assert report_file.stat().st_size > 0, "Report file is empty"

    def test_provenance_report_structure(self):
        """Test that provenance report has required structure."""
        report_file = Path("artifacts/provenance_report.json")

        assert report_file.exists(), "Provenance report not found"

        with open(report_file, 'r') as f:
            report = json.load(f)

        # Check required top-level fields
        required_fields = [
            "provenance_version",
            "generated",
            "root_cid",
            "summary",
            "contracts",
            "verification"
        ]

        for field in required_fields:
            assert field in report, f"Missing required field: {field}"

        # Validate summary structure
        summary = report["summary"]
        assert "total_contracts" in summary
        assert "total_size" in summary
        assert "v3_sections_present" in summary

        assert summary["total_contracts"] >= 65, "Expected at least 65 contracts"
        assert summary["total_size"] > 0, "Total size should be greater than 0"

        # Validate v3 sections
        v3_sections = summary["v3_sections_present"]
        expected_sections = [
            "tokenization",
            "glyph_provenance",
            "dream_provenance",
            "guardian_check",
            "biosymbolic_map",
            "quantum_proof"
        ]

        for section in expected_sections:
            assert section in v3_sections, f"Missing v3 section: {section}"
            assert v3_sections[section] > 0, f"No contracts have {section} section"

    def test_root_cid_format(self):
        """Test that root CID has correct format."""
        report_file = Path("artifacts/provenance_report.json")

        with open(report_file, 'r') as f:
            report = json.load(f)

        root_cid = report["root_cid"]

        # Basic CID format validation (mock CIDv1 format)
        assert isinstance(root_cid, str), "Root CID should be a string"
        assert root_cid.startswith("bafyrei"), f"Root CID should start with 'bafyrei', got: {root_cid}"
        assert len(root_cid) > 20, f"Root CID seems too short: {root_cid}"

    def test_contract_entries(self):
        """Test that contract entries have required structure."""
        report_file = Path("artifacts/provenance_report.json")

        with open(report_file, 'r') as f:
            report = json.load(f)

        contracts = report["contracts"]
        assert isinstance(contracts, list), "Contracts should be a list"
        assert len(contracts) >= 65, f"Expected at least 65 contracts, got {len(contracts)}"

        # Check structure of first few contracts
        for i, contract in enumerate(contracts[:5]):
            required_fields = ["module", "cid", "sha256", "v3_sections"]

            for field in required_fields:
                assert field in contract, f"Contract {i} missing field: {field}"

            # Validate CID format
            cid = contract["cid"]
            assert isinstance(cid, str), f"Contract {i} CID should be string"
            assert cid.startswith("bafyrei"), f"Contract {i} CID format invalid: {cid}"

            # Validate SHA256 format
            sha256 = contract["sha256"]
            assert isinstance(sha256, str), f"Contract {i} SHA256 should be string"
            assert len(sha256) == 64, f"Contract {i} SHA256 length invalid: {len(sha256)}"

            # Validate v3 sections
            v3_sections = contract["v3_sections"]
            assert isinstance(v3_sections, list), f"Contract {i} v3_sections should be list"
            assert len(v3_sections) == 6, f"Contract {i} should have 6 v3 sections, got {len(v3_sections)}"

    def test_car_file_structure(self):
        """Test that CAR file has expected structure."""
        car_file = Path("artifacts/provenance.car")

        assert car_file.exists(), "CAR file not found"

        # Check file size
        size = car_file.stat().st_size
        assert size > 1000, f"CAR file seems too small: {size} bytes"

        # Read first 100 bytes to check for header
        with open(car_file, 'rb') as f:
            header_bytes = f.read(100)

        # Check that it contains expected header elements
        header_str = header_bytes.decode('utf-8', errors='ignore')
        assert "version" in header_str, "CAR file header should contain 'version'"
        assert "roots" in header_str, "CAR file header should contain 'roots'"

    def test_verification_script_exists(self):
        """Test that verification script exists and is executable."""
        script_path = Path("tools/verify_provenance.sh")

        assert script_path.exists(), "Verification script not found"
        assert script_path.stat().st_mode & 0o111, "Verification script is not executable"

    def test_verification_script_runs(self):
        """Test that verification script runs successfully."""
        script_path = Path("tools/verify_provenance.sh")

        # Run verification script
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        assert result.returncode == 0, f"Verification script failed: {result.stderr}"

        # Check that output contains success message
        assert "verification completed successfully" in result.stdout.lower(), \
            "Verification script didn't report success"

    def test_tokenization_script_exists(self):
        """Test that tokenization script exists and is functional."""
        script_path = Path("tools/matrix_tokenize.py")

        assert script_path.exists(), "Tokenization script not found"

        # Test with a sample contract
        sample_contract = Path("contracts/matrix_identity.json")
        if sample_contract.exists():
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
                tmp_output = Path(tmp.name)

            try:
                result = subprocess.run(
                    ["python3", str(script_path), "--contract", str(sample_contract), "--output", str(tmp_output)],
                    capture_output=True,
                    text=True
                )

                assert result.returncode == 0, f"Tokenization script failed: {result.stderr}"
                assert tmp_output.exists(), "Tokenization script didn't create output file"

                # Check output structure
                with open(tmp_output, 'r') as f:
                    output = json.load(f)

                required_fields = ["contract", "module", "sha256", "txid", "network", "tokenization"]
                for field in required_fields:
                    assert field in output, f"Tokenization output missing field: {field}"

                assert output["txid"].startswith("SOLANA_MOCK_"), "Transaction ID format incorrect"

            finally:
                if tmp_output.exists():
                    tmp_output.unlink()

    def test_provenance_generation_script(self):
        """Test that provenance generation script is functional."""
        script_path = Path("tools/matrix_provenance.py")

        assert script_path.exists(), "Provenance generation script not found"

        # Test with identity contracts using temporary output files
        with tempfile.NamedTemporaryFile(suffix='.car', delete=False) as tmp_car:
            tmp_car_path = Path(tmp_car.name)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_report:
            tmp_report_path = Path(tmp_report.name)

        try:
            result = subprocess.run(
                ["python3", str(script_path),
                 "--contracts", "contracts/matrix_identity*.json",
                 "--output", str(tmp_car_path),
                 "--report", str(tmp_report_path)],
                capture_output=True,
                text=True
            )

            # Should succeed even if we don't have all contracts
            assert result.returncode == 0, f"Provenance script failed: {result.stderr}"

            # Verify output files were created
            assert tmp_car_path.exists(), "CAR file was not created"
            assert tmp_report_path.exists(), "Report file was not created"

        finally:
            # Clean up temporary files
            if tmp_car_path.exists():
                tmp_car_path.unlink()
            if tmp_report_path.exists():
                tmp_report_path.unlink()

    def test_idempotency(self):
        """Test that running provenance generation twice produces consistent results."""
        report_file = Path("artifacts/provenance_report.json")

        # Load initial report
        assert report_file.exists(), "Initial provenance report not found"

        with open(report_file, 'r') as f:
            initial_report = json.load(f)

        initial_root_cid = initial_report["root_cid"]
        initial_contract_count = initial_report["summary"]["total_contracts"]

        # Regenerate provenance
        result = subprocess.run(
            ["python3", "tools/matrix_provenance.py", "--contracts", "contracts/matrix_*.json"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Provenance regeneration failed: {result.stderr}"

        # Load new report
        with open(report_file, 'r') as f:
            new_report = json.load(f)

        new_root_cid = new_report["root_cid"]
        new_contract_count = new_report["summary"]["total_contracts"]

        # Root CID should be the same (deterministic generation)
        assert new_root_cid == initial_root_cid, "Root CID changed between runs (not idempotent)"
        assert new_contract_count == initial_contract_count, "Contract count changed between runs"

    def test_all_v3_sections_present(self):
        """Test that all contracts have v3 sections after upgrade."""
        report_file = Path("artifacts/provenance_report.json")

        with open(report_file, 'r') as f:
            report = json.load(f)

        v3_sections = report["summary"]["v3_sections_present"]
        total_contracts = report["summary"]["total_contracts"]

        expected_sections = [
            "tokenization",
            "glyph_provenance",
            "dream_provenance",
            "guardian_check",
            "biosymbolic_map",
            "quantum_proof"
        ]

        for section in expected_sections:
            assert section in v3_sections, f"v3 section missing from summary: {section}"
            section_count = v3_sections[section]
            assert section_count == total_contracts, \
                f"Not all contracts have {section} section: {section_count}/{total_contracts}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
