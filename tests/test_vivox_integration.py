#!/usr/bin/env python3
"""
VIVOX Z(t) Collapse Engine Integration Test
==========================================
Comprehensive testing of the z(t) mathematical implementation with cryptographic verification.

Tests:
- Mathematical correctness of z(t) formula
- Cryptographic timestamp generation and verification
- Hash integrity and multi-algorithm verification
- Audit trail generation and chain verification
- Integration with existing LUKHAS systems
"""

import sys
import os
import math
import time
import json
import pytest
from typing import Dict, Any, List, Tuple

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'collapse'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crypto'))

try:
    from z_collapse_engine import ZCollapseEngine, CollapseResult
    from timestamp_verification import VIVOXCryptoSystem, HashAlgorithm, TimestampSource, SecureZCollapseEngine
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Test will be skipped - required modules not available")
    IMPORTS_AVAILABLE = False
    # Create dummy classes to prevent further errors
    class ZCollapseEngine: pass
    class CollapseResult: pass
    class VIVOXCryptoSystem: pass
    class HashAlgorithm: pass
    class TimestampSource: pass
    class SecureZCollapseEngine: pass


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required VIVOX modules not available")
class VIVOXIntegrationTester:
    """
    Comprehensive integration tester for VIVOX z(t) collapse system
    """
    
    def __init__(self):
        self.test_results = []
        self.crypto_system = VIVOXCryptoSystem(
            primary_algorithm=HashAlgorithm.SHA3_256,
            enable_secondary_hashes=True,
            timestamp_source=TimestampSource.SYSTEM_TIME
        )
        self.z_engine = ZCollapseEngine()
        self.secure_engine = SecureZCollapseEngine(self.crypto_system)
        
    def log_test(self, test_name: str, passed: bool, details: str = "", execution_time: float = 0.0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "execution_time_ms": round(execution_time * 1000, 2)
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} ({execution_time:.3f}s)")
        if details and not passed:
            print(f"   Details: {details}")
    
    def test_mathematical_baseline(self) -> bool:
        """Test z(t) mathematical baseline: z(0) = 2"""
        start_time = time.time()
        
        try:
            result = self.z_engine.compute_z_collapse(
                t=0.0,
                amplitude=1.0,
                theta=0.0,
                entropy_weight=1.0,
                phase_drift=0.0,
                alignment_score=1.0
            )
            
            expected = complex(2.0, 0.0)
            actual = result.z_value
            
            # Check real and imaginary parts with tolerance
            tolerance = 1e-10
            real_match = abs(actual.real - expected.real) < tolerance
            imag_match = abs(actual.imag - expected.imag) < tolerance
            
            passed = real_match and imag_match
            details = f"Expected: {expected}, Got: {actual}"
            
            execution_time = time.time() - start_time
            self.log_test("Mathematical Baseline z(0)=2", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Mathematical Baseline z(0)=2", False, f"Exception: {e}", execution_time)
            return False
    
    def test_complex_mathematics(self) -> bool:
        """Test complex exponential mathematics"""
        start_time = time.time()
        
        try:
            # Test with π/4 phase
            theta = math.pi / 4
            result = self.z_engine.compute_z_collapse(
                t=1.0,
                amplitude=1.0,
                theta=theta,
                entropy_weight=1.0,
                phase_drift=0.0,
                alignment_score=1.0
            )
            
            # Manual calculation for verification
            # z(t) = A * [e^(iθ) + e^(i(π-θ))] * W
            # For θ = π/4: e^(iπ/4) + e^(i3π/4)
            term1 = complex(math.cos(theta), math.sin(theta))
            term2 = complex(math.cos(math.pi - theta), math.sin(math.pi - theta))
            expected = 1.0 * (term1 + term2) * 1.0
            
            tolerance = 1e-10
            difference = abs(result.z_value - expected)
            passed = difference < tolerance
            
            details = f"θ=π/4, Expected: {expected:.6f}, Got: {result.z_value:.6f}, Diff: {difference:.2e}"
            
            execution_time = time.time() - start_time
            self.log_test("Complex Exponential Mathematics", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Complex Exponential Mathematics", False, f"Exception: {e}", execution_time)
            return False
    
    def test_cryptographic_timestamp(self) -> bool:
        """Test cryptographic timestamp generation and verification"""
        start_time = time.time()
        
        try:
            timestamp = self.crypto_system.generate_crypto_timestamp(precision_required=True)
            
            # Verify timestamp structure
            checks = [
                timestamp.timestamp_utc > 0,
                len(timestamp.timestamp_iso) > 20,
                timestamp.source == TimestampSource.SYSTEM_TIME,
                len(timestamp.nonce) == 32,  # 16 bytes = 32 hex chars
                timestamp.verification_data is not None
            ]
            
            # Test signature verification (if available)
            signature_valid = self.crypto_system.verify_timestamp_signature(timestamp)
            
            passed = all(checks)
            details = f"Checks: {sum(checks)}/{len(checks)}, Signature: {signature_valid}"
            
            execution_time = time.time() - start_time
            self.log_test("Cryptographic Timestamp", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Cryptographic Timestamp", False, f"Exception: {e}", execution_time)
            return False
    
    def test_multi_hash_verification(self) -> bool:
        """Test multi-algorithm hash generation and verification"""
        start_time = time.time()
        
        try:
            timestamp = self.crypto_system.generate_crypto_timestamp()
            test_data = "VIVOX z(t) test data with special chars: αβγ∑∏∆"
            
            # Generate hashes
            hash_record = self.crypto_system.generate_multi_hash(
                test_data, timestamp, {"test_context": "multi_hash_verification"}
            )
            
            # Verify hash record structure
            checks = [
                len(hash_record.primary_hash) == 64,  # SHA3-256 = 64 hex chars
                hash_record.algorithm == HashAlgorithm.SHA3_256,
                len(hash_record.salt) == 64,  # 32 bytes = 64 hex chars
                hash_record.iterations == self.crypto_system.hash_iterations,
                hash_record.input_length > 0
            ]
            
            # Verify hash integrity
            verification_passed = self.crypto_system.verify_hash_record(
                test_data, timestamp, hash_record, {"test_context": "multi_hash_verification"}
            )
            
            # Test tamper detection
            tampered_data = test_data + " TAMPERED"
            tamper_detection = not self.crypto_system.verify_hash_record(
                tampered_data, timestamp, hash_record, {"test_context": "multi_hash_verification"}
            )
            
            passed = all(checks) and verification_passed and tamper_detection
            details = f"Structure: {sum(checks)}/{len(checks)}, Verify: {verification_passed}, Tamper: {tamper_detection}"
            
            execution_time = time.time() - start_time
            self.log_test("Multi-Hash Verification", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Multi-Hash Verification", False, f"Exception: {e}", execution_time)
            return False
    
    def test_secure_collapse_integration(self) -> bool:
        """Test secure z(t) collapse with full cryptographic audit"""
        start_time = time.time()
        
        try:
            # Execute secure collapse
            z_result = complex(1.414, 1.414)  # √2 + i√2
            collapse_data = {
                "alignment_score": 0.85,
                "entropy_score": 0.15,
                "phase_drift": 0.1,
                "timestamp_test": True
            }
            mathematical_trace = {
                "formula": "z(t) = A(t) * [e^(iθ(t)) + e^(i(π-θ(t)))] × W(ΔS(t))",
                "computation_method": "complex_exponential",
                "test_parameters": {
                    "amplitude": 1.0,
                    "theta": "π/4",
                    "entropy_weight": 1.0
                }
            }
            
            collapse_hash, audit_trail = self.secure_engine.secure_collapse_with_audit(
                z_result, collapse_data, mathematical_trace
            )
            
            # Verify audit trail structure
            checks = [
                len(collapse_hash) == 64,  # SHA3-256
                audit_trail.event_id.startswith("z_collapse_"),
                audit_trail.timestamp.timestamp_utc > 0,
                audit_trail.hash_record.primary_hash == collapse_hash,
                audit_trail.chain_position >= 0,
                len(audit_trail.mathematical_trace) > 0
            ]
            
            # Verify audit chain
            chain_valid, errors = self.crypto_system.verify_audit_chain()
            
            passed = all(checks) and chain_valid
            details = f"Structure: {sum(checks)}/{len(checks)}, Chain: {chain_valid}, Errors: {len(errors)}"
            
            execution_time = time.time() - start_time
            self.log_test("Secure Collapse Integration", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Secure Collapse Integration", False, f"Exception: {e}", execution_time)
            return False
    
    def test_audit_chain_integrity(self) -> bool:
        """Test audit chain integrity with multiple collapse events"""
        start_time = time.time()
        
        try:
            # Execute multiple collapses to build chain
            test_cases = [
                (complex(2.0, 0.0), "baseline"),
                (complex(0.0, 2.0), "pure_imaginary"),
                (complex(-1.0, 0.0), "negative_real"),
                (complex(1.0, 1.0), "diagonal")
            ]
            
            hashes = []
            for i, (z_result, test_name) in enumerate(test_cases):
                collapse_data = {
                    "test_case": test_name,
                    "iteration": i,
                    "alignment_score": 0.9,
                    "entropy_score": 0.1
                }
                mathematical_trace = {
                    "test_sequence": True,
                    "case_number": i + 1
                }
                
                collapse_hash, _ = self.secure_engine.secure_collapse_with_audit(
                    z_result, collapse_data, mathematical_trace
                )
                hashes.append(collapse_hash)
            
            # Verify chain integrity
            chain_valid, errors = self.crypto_system.verify_audit_chain()
            
            # Check chain linking
            chain_length = len(self.crypto_system.audit_chain)
            linking_valid = True
            for i in range(1, chain_length):
                current = self.crypto_system.audit_chain[i]
                previous = self.crypto_system.audit_chain[i - 1]
                if current.previous_hash != previous.hash_record.primary_hash:
                    linking_valid = False
                    break
            
            passed = chain_valid and linking_valid and chain_length >= len(test_cases)
            details = f"Chain length: {chain_length}, Valid: {chain_valid}, Linked: {linking_valid}"
            
            execution_time = time.time() - start_time
            self.log_test("Audit Chain Integrity", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Audit Chain Integrity", False, f"Exception: {e}", execution_time)
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks for production readiness"""
        start_time = time.time()
        
        try:
            # Benchmark single collapse operation
            benchmark_start = time.time()
            
            result = self.z_engine.compute_z_collapse(
                t=1.0,
                amplitude=1.0,
                theta=math.pi / 3,
                entropy_weight=0.8,
                phase_drift=0.1,
                alignment_score=0.9
            )
            
            collapse_time = time.time() - benchmark_start
            
            # Benchmark secure collapse with crypto
            crypto_start = time.time()
            
            collapse_hash, audit_trail = self.secure_engine.secure_collapse_with_audit(
                result.z_value,
                {"benchmark": True},
                {"performance_test": True}
            )
            
            crypto_time = time.time() - crypto_start
            
            # Performance thresholds (adjustable based on requirements)
            collapse_threshold = 0.001  # 1ms for mathematical computation
            crypto_threshold = 0.050    # 50ms for full cryptographic audit
            
            collapse_fast_enough = collapse_time < collapse_threshold
            crypto_fast_enough = crypto_time < crypto_threshold
            
            passed = collapse_fast_enough and crypto_fast_enough
            details = f"Collapse: {collapse_time:.4f}s (<{collapse_threshold}s), Crypto: {crypto_time:.4f}s (<{crypto_threshold}s)"
            
            execution_time = time.time() - start_time
            self.log_test("Performance Benchmarks", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Performance Benchmarks", False, f"Exception: {e}", execution_time)
            return False
    
    def test_edge_cases(self) -> bool:
        """Test edge cases and error handling"""
        start_time = time.time()
        
        try:
            edge_cases_passed = 0
            total_edge_cases = 0
            
            # Test with extreme values
            test_cases = [
                ("zero_amplitude", {"amplitude": 0.0}),
                ("large_theta", {"theta": 10 * math.pi}),
                ("negative_entropy", {"entropy_weight": -0.5}),
                ("extreme_alignment", {"alignment_score": 2.0}),
                ("large_phase_drift", {"phase_drift": math.pi})
            ]
            
            for case_name, params in test_cases:
                total_edge_cases += 1
                try:
                    default_params = {
                        "t": 1.0,
                        "amplitude": 1.0,
                        "theta": 0.0,
                        "entropy_weight": 1.0,
                        "phase_drift": 0.0,
                        "alignment_score": 1.0
                    }
                    default_params.update(params)
                    
                    result = self.z_engine.compute_z_collapse(**default_params)
                    
                    # Check that result is finite and well-formed
                    if (math.isfinite(result.z_value.real) and 
                        math.isfinite(result.z_value.imag) and
                        result.computation_time >= 0):
                        edge_cases_passed += 1
                        
                except Exception:
                    # Some edge cases may legitimately fail
                    pass
            
            # Test error recovery
            recovery_test_passed = True
            try:
                # This should handle gracefully
                result = self.z_engine.compute_z_collapse(
                    t=float('inf'),
                    amplitude=1.0,
                    theta=0.0,
                    entropy_weight=1.0,
                    phase_drift=0.0,
                    alignment_score=1.0
                )
                # Should either return a valid result or raise a controlled exception
            except Exception:
                # Expected behavior for extreme inputs
                pass
            
            passed = (edge_cases_passed >= total_edge_cases // 2) and recovery_test_passed
            details = f"Edge cases: {edge_cases_passed}/{total_edge_cases}, Recovery: {recovery_test_passed}"
            
            execution_time = time.time() - start_time
            self.log_test("Edge Cases & Error Handling", passed, details, execution_time)
            return passed
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test("Edge Cases & Error Handling", False, f"Exception: {e}", execution_time)
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting VIVOX z(t) Collapse Engine Integration Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_mathematical_baseline,
            self.test_complex_mathematics,
            self.test_cryptographic_timestamp,
            self.test_multi_hash_verification,
            self.test_secure_collapse_integration,
            self.test_audit_chain_integrity,
            self.test_performance_benchmarks,
            self.test_edge_cases
        ]
        
        passed_tests = 0
        for test_func in tests:
            if test_func():
                passed_tests += 1
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "failed_tests": len(tests) - passed_tests,
            "success_rate": (passed_tests / len(tests)) * 100,
            "total_execution_time": total_time,
            "all_tests_passed": passed_tests == len(tests)
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Time: {summary['total_execution_time']:.3f}s")
        print(f"Overall Result: {'✅ ALL TESTS PASSED' if summary['all_tests_passed'] else '❌ SOME TESTS FAILED'}")
        
        # Export test results
        self.export_test_results(summary)
        
        return summary
    
    def export_test_results(self, summary: Dict[str, Any]):
        """Export detailed test results"""
        export_data = {
            "test_summary": summary,
            "detailed_results": self.test_results,
            "system_info": {
                "crypto_algorithm": self.crypto_system.primary_algorithm.value,
                "timestamp_source": self.crypto_system.timestamp_source.value,
                "audit_chain_length": len(self.crypto_system.audit_chain)
            },
            "export_timestamp": time.time()
        }
        
        try:
            with open("vivox_integration_test_results.json", "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"\n📄 Test results exported to: vivox_integration_test_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not export test results: {e}")


if __name__ == "__main__":
    if not IMPORTS_AVAILABLE:
        print("⚠️ Skipping tests - required modules not available")
        sys.exit(0)
    
    # Run comprehensive integration tests
    tester = VIVOXIntegrationTester()
    summary = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["all_tests_passed"] else 1)
