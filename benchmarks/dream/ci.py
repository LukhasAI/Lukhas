from __future__ import annotations
import json, subprocess, sys, os
from typing import Dict, Any
import time

class CIRunner:
    """CI integration for Dream Phase NEXT testing."""

    def __init__(self, work_dir: str = "benchmarks/dream"):
        self.work_dir = work_dir
        self.results_dir = f"{work_dir}/ci_results"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_stability_check(self) -> Dict[str, Any]:
        """Run stability testing for CI."""
        print("🔍 Running stability check...")

        try:
            # Run stability test with limited seeds for CI speed
            env = os.environ.copy()
            env["LUKHAS_CI_MODE"] = "1"  # Signal CI mode for faster execution

            result = subprocess.run([
                sys.executable, "-m", "benchmarks.dream.stability"
            ], env=env, capture_output=True, text=True, timeout=300)

            success = result.returncode == 0

            return {
                "test": "stability",
                "success": success,
                "duration_seconds": 0,  # Would measure in real implementation
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "test": "stability",
                "success": False,
                "error": "Timeout after 5 minutes",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "test": "stability",
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def run_benchmark_validation(self) -> Dict[str, Any]:
        """Run benchmark validation for CI."""
        print("📊 Running benchmark validation...")

        try:
            # Run quick benchmark
            result = subprocess.run([
                sys.executable, "-m", "benchmarks.dream.run",
                "--out", f"{self.results_dir}/ci_benchmark.jsonl"
            ], capture_output=True, text=True, timeout=120)

            success = result.returncode == 0

            # If successful, validate results
            if success:
                results_path = f"{self.results_dir}/ci_benchmark.jsonl"
                if os.path.exists(results_path):
                    with open(results_path, 'r') as f:
                        results = []
                        for line in f:
                            line = line.strip()
                            if line:
                                results.append(json.loads(line))

                    # Basic validation
                    if len(results) == 0:
                        success = False
                        return {
                            "test": "benchmark_validation",
                            "success": False,
                            "error": "No benchmark results generated",
                            "exit_code": -1
                        }

                    # Check accuracy threshold
                    avg_accuracy = sum(r.get('accuracy', 0.0) for r in results) / len(results)
                    if avg_accuracy < 0.7:  # CI threshold
                        success = False
                        return {
                            "test": "benchmark_validation",
                            "success": False,
                            "error": f"Average accuracy {avg_accuracy:.3f} below CI threshold 0.7",
                            "results_count": len(results),
                            "avg_accuracy": avg_accuracy
                        }

            return {
                "test": "benchmark_validation",
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "test": "benchmark_validation",
                "success": False,
                "error": "Timeout after 2 minutes",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "test": "benchmark_validation",
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def run_synthetic_generation(self) -> Dict[str, Any]:
        """Test synthetic case generation."""
        print("🎲 Testing synthetic generation...")

        try:
            # Generate small synthetic corpus for testing
            result = subprocess.run([
                sys.executable, "-m", "benchmarks.dream.synthetic",
                "10", "42", f"{self.results_dir}/ci_synthetic.json"
            ], capture_output=True, text=True, timeout=60)

            success = result.returncode == 0

            # Validate generated file
            if success:
                synthetic_path = f"{self.results_dir}/ci_synthetic.json"
                if os.path.exists(synthetic_path):
                    with open(synthetic_path, 'r') as f:
                        synthetic_data = json.load(f)

                    if len(synthetic_data) != 10:
                        success = False
                        return {
                            "test": "synthetic_generation",
                            "success": False,
                            "error": f"Expected 10 cases, got {len(synthetic_data)}",
                            "exit_code": -1
                        }

                    # Check case structure
                    required_fields = ['case_id', 'query_emotion', 'snapshots', 'expected_selection']
                    for case in synthetic_data[:3]:  # Check first 3
                        for field in required_fields:
                            if field not in case:
                                success = False
                                return {
                                    "test": "synthetic_generation",
                                    "success": False,
                                    "error": f"Missing field '{field}' in synthetic case",
                                    "exit_code": -1
                                }

            return {
                "test": "synthetic_generation",
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "test": "synthetic_generation",
                "success": False,
                "error": "Timeout after 1 minute",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "test": "synthetic_generation",
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def run_config_validation(self) -> Dict[str, Any]:
        """Test configuration validation."""
        print("⚙️  Testing config validation...")

        try:
            # Create test config
            test_config = {
                "strategy": "overlap",
                "use_objective": "1",
                "alignment_threshold": 0.5,
                "drift_threshold": 0.3,
                "confidence_threshold": 0.7
            }

            config_path = f"{self.results_dir}/test_config.json"
            with open(config_path, 'w') as f:
                json.dump(test_config, f, indent=2)

            # Test config chooser validation
            from benchmarks.dream.chooser import ConfigChooser
            chooser = ConfigChooser()
            validation = chooser.validate_config(test_config)

            if not validation['valid']:
                return {
                    "test": "config_validation",
                    "success": False,
                    "error": f"Config validation failed: {validation['issues']}",
                    "validation_result": validation
                }

            return {
                "test": "config_validation",
                "success": True,
                "validation_result": validation
            }

        except Exception as e:
            return {
                "test": "config_validation",
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def run_taxonomy_test(self) -> Dict[str, Any]:
        """Test error taxonomy system."""
        print("🏷️  Testing taxonomy system...")

        try:
            # Create mock results for taxonomy testing
            mock_results = [
                {"accuracy": 0.9, "error": ""},
                {"accuracy": 0.3, "error": "low alignment scores"},
                {"accuracy": 0.8, "error": ""}
            ]

            mock_path = f"{self.results_dir}/mock_results.json"
            with open(mock_path, 'w') as f:
                json.dump(mock_results, f, indent=2)

            # Test taxonomy analysis
            result = subprocess.run([
                sys.executable, "-m", "benchmarks.dream.taxonomy",
                mock_path, f"{self.results_dir}/ci_taxonomy.json"
            ], capture_output=True, text=True, timeout=30)

            success = result.returncode == 0

            # Validate taxonomy report was generated
            if success:
                taxonomy_path = f"{self.results_dir}/ci_taxonomy.json"
                if os.path.exists(taxonomy_path):
                    with open(taxonomy_path, 'r') as f:
                        taxonomy_report = json.load(f)

                    required_sections = ['taxonomy_analysis', 'error_patterns']
                    for section in required_sections:
                        if section not in taxonomy_report:
                            success = False
                            return {
                                "test": "taxonomy_test",
                                "success": False,
                                "error": f"Missing section '{section}' in taxonomy report",
                                "exit_code": -1
                            }

            return {
                "test": "taxonomy_test",
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "test": "taxonomy_test",
                "success": False,
                "error": "Timeout after 30 seconds",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "test": "taxonomy_test",
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive CI test suite."""
        start_time = time.time()

        print("🚀 Starting Dream Phase NEXT CI Suite")
        print("=" * 50)

        test_methods = [
            self.run_benchmark_validation,
            self.run_config_validation,
            self.run_synthetic_generation,
            self.run_taxonomy_test,
            # self.run_stability_check,  # Skip for speed in CI
        ]

        results = []
        passed = 0
        failed = 0

        for test_method in test_methods:
            result = test_method()
            results.append(result)

            if result['success']:
                passed += 1
                print(f"✅ {result['test']}")
            else:
                failed += 1
                print(f"❌ {result['test']}: {result.get('error', 'Unknown error')}")

        total_time = time.time() - start_time

        summary = {
            "ci_suite": "dream_phase_next",
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(results) if results else 0.0,
            "total_duration_seconds": total_time,
            "overall_success": failed == 0,
            "test_results": results,
            "timestamp": time.time()
        }

        # Save CI report
        report_path = f"{self.results_dir}/ci_report.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print("=" * 50)
        print(f"CI Summary: {passed}/{len(results)} tests passed")
        print(f"Duration: {total_time:.1f}s")
        print(f"Report: {report_path}")

        return summary

def run_ci_pipeline() -> bool:
    """Run the complete CI pipeline."""
    runner = CIRunner()
    summary = runner.run_all_tests()

    # Exit with appropriate code
    return summary['overall_success']

if __name__ == "__main__":
    success = run_ci_pipeline()
    sys.exit(0 if success else 1)