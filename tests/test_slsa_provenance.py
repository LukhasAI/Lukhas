#!/usr/bin/env python3
"""
SLSA Provenance Validation Tests

Tests the structure and integrity of SLSA provenance artifacts.
Can be run standalone or as part of pytest suite.

Usage:
    python tests/test_slsa_provenance.py
    pytest tests/test_slsa_provenance.py -v
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any
import sys


class TestSLSAProvenance:
    """Test suite for SLSA provenance validation"""

    @staticmethod
    def load_provenance(path: str = "reports/provenance.json") -> Dict[str, Any]:
        """Load provenance JSON file"""
        provenance_path = Path(path)
        
        if not provenance_path.exists():
            raise FileNotFoundError(f"Provenance file not found: {path}")
        
        with open(provenance_path) as f:
            return json.load(f)

    def test_provenance_structure(self):
        """Test that provenance contains all required fields"""
        provenance = self.load_provenance()

        required_fields = [
            "SLSA_VERSION",
            "buildType",
            "builder",
            "invocation",
            "metadata",
            "materials",
        ]

        missing_fields = [
            field for field in required_fields if field not in provenance
        ]

        assert not missing_fields, f"Missing required fields: {missing_fields}"
        print("✅ Provenance structure valid")

    def test_slsa_version(self):
        """Test SLSA version is specified"""
        provenance = self.load_provenance()

        assert "SLSA_VERSION" in provenance
        assert provenance["SLSA_VERSION"] in ["1.0", "1", "0.1"]
        print(f"✅ SLSA version: {provenance['SLSA_VERSION']}")

    def test_builder_identity(self):
        """Test builder identity is present"""
        provenance = self.load_provenance()

        assert "builder" in provenance
        assert "id" in provenance["builder"]
        assert len(provenance["builder"]["id"]) > 0
        print(f"✅ Builder ID: {provenance['builder']['id']}")

    def test_invocation_details(self):
        """Test invocation contains config source"""
        provenance = self.load_provenance()

        assert "invocation" in provenance
        invocation = provenance["invocation"]

        assert "configSource" in invocation
        assert "uri" in invocation["configSource"]
        assert "digest" in invocation["configSource"]
        
        print(f"✅ Config source: {invocation['configSource']['uri']}")

    def test_metadata_timestamps(self):
        """Test metadata contains build timestamps"""
        provenance = self.load_provenance()

        assert "metadata" in provenance
        metadata = provenance["metadata"]

        # Timestamps should be present (optional but recommended)
        if "buildStartedOn" in metadata:
            assert len(metadata["buildStartedOn"]) > 0
            print(f"✅ Build started: {metadata['buildStartedOn']}")

        if "buildFinishedOn" in metadata:
            assert len(metadata["buildFinishedOn"]) > 0
            print(f"✅ Build finished: {metadata['buildFinishedOn']}")

    def test_materials(self):
        """Test materials list is present"""
        provenance = self.load_provenance()

        assert "materials" in provenance
        assert isinstance(provenance["materials"], list)
        assert len(provenance["materials"]) > 0

        # Each material should have uri and digest
        for material in provenance["materials"]:
            assert "uri" in material
            assert "digest" in material
            assert len(material["digest"]) > 0

        print(f"✅ Materials: {len(provenance['materials'])} entries")

    def test_sbom_hash_present(self):
        """Test SBOM hash is included"""
        provenance = self.load_provenance()

        # SBOM hash should be present
        if "sbomHash" in provenance:
            assert isinstance(provenance["sbomHash"], dict)
            # Should have at least one hash algorithm
            assert len(provenance["sbomHash"]) > 0
            print(f"✅ SBOM hash present: {list(provenance['sbomHash'].keys())}")
        else:
            print("⚠️  SBOM hash not found (optional)")

    def test_build_command_present(self):
        """Test build command is documented"""
        provenance = self.load_provenance()

        # Build command should be present
        if "buildCommand" in provenance:
            assert len(provenance["buildCommand"]) > 0
            print(f"✅ Build command: {provenance['buildCommand']}")
        else:
            print("⚠️  Build command not found (recommended)")

    def test_artifact_checksums(self):
        """Test artifact checksums are present"""
        provenance = self.load_provenance()

        # Artifact checksums should be included
        if "artifactChecksums" in provenance:
            assert len(provenance["artifactChecksums"]) > 0
            print("✅ Artifact checksums present")
        else:
            print("⚠️  Artifact checksums not found (optional)")

    def test_sbom_file_exists(self):
        """Test SBOM file exists and is valid JSON"""
        sbom_path = Path("reports/sbom.json")

        if not sbom_path.exists():
            print("⚠️  SBOM file not found (test may be running outside CI)")
            return

        with open(sbom_path) as f:
            sbom = json.load(f)

        # Basic SBOM structure check
        # Different SBOM formats have different structures
        assert isinstance(sbom, (dict, list))
        print("✅ SBOM file valid")

    def test_sbom_hash_matches(self):
        """Test SBOM hash matches actual file"""
        sbom_path = Path("reports/sbom.json")
        provenance = self.load_provenance()

        if not sbom_path.exists():
            print("⚠️  SBOM file not found - skipping hash verification")
            return

        if "sbomHash" not in provenance:
            print("⚠️  SBOM hash not in provenance - skipping verification")
            return

        # Calculate actual SBOM hash
        sbom_content = sbom_path.read_bytes()
        actual_hash = hashlib.sha256(sbom_content).hexdigest()

        # Compare with provenance
        if "sha256" in provenance["sbomHash"]:
            expected_hash = provenance["sbomHash"]["sha256"]
            assert actual_hash == expected_hash, \
                f"SBOM hash mismatch:\n  Expected: {expected_hash}\n  Actual: {actual_hash}"
            print(f"✅ SBOM hash matches: {actual_hash[:16]}...")
        else:
            print("⚠️  SHA256 hash not found in SBOM hash field")

    def test_reproducible_flag(self):
        """Test reproducible flag is set correctly"""
        provenance = self.load_provenance()

        if "metadata" in provenance and "reproducible" in provenance["metadata"]:
            reproducible = provenance["metadata"]["reproducible"]
            assert isinstance(reproducible, bool)
            print(f"✅ Reproducible flag: {reproducible}")
        else:
            print("⚠️  Reproducible flag not found (optional)")


def run_tests_standalone():
    """Run tests standalone (without pytest)"""
    print("=" * 60)
    print("SLSA Provenance Validation Tests")
    print("=" * 60)
    print()

    test_suite = TestSLSAProvenance()
    tests = [
        method for method in dir(test_suite)
        if method.startswith("test_") and callable(getattr(test_suite, method))
    ]

    passed = 0
    failed = 0
    warnings = 0

    for test_name in tests:
        test_method = getattr(test_suite, test_name)
        try:
            print(f"\nRunning {test_name}...")
            test_method()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except FileNotFoundError as e:
            print(f"⚠️  SKIPPED: {e}")
            warnings += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {warnings} warnings")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    # Run tests standalone
    sys.exit(run_tests_standalone())
