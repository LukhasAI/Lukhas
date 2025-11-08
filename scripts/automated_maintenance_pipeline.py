#!/usr/bin/env python3
"""
LUKHAS Automated Schema Maintenance Pipeline
Provides automated validation, monitoring, and maintenance for LUKHAS architecture
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class LUKHASMaintenancePipeline:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.scripts_dir = self.root_path / "scripts"
        self.maintenance_log = []

    def log_action(self, action: str, status: str, details: str = ""):
        """Log maintenance actions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.maintenance_log.append(log_entry)
        print(f"[{status}] {action}: {details}")

    def run_script(self, script_name: str, description: str) -> tuple[bool, str]:
        """Run a maintenance script and capture results"""
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            return False, f"Script {script_name} not found"

        try:
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self.log_action(description, "SUCCESS", "Script completed successfully")
                return True, result.stdout
            else:
                self.log_action(description, "FAILED", f"Script failed: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            self.log_action(description, "TIMEOUT", "Script exceeded 5 minute timeout")
            return False, "Script timeout"
        except Exception as e:
            self.log_action(description, "ERROR", f"Script execution error: {e}")
            return False, str(e)

    def validate_context_sync(self) -> Dict:
        """Validate context file synchronization"""
        success, output = self.run_script(
            "validate_context_sync.py",
            "Context Sync Validation"
        )

        return {
            "validation_passed": success,
            "output": output,
            "critical": True  # Context sync is critical
        }

    def validate_schemas(self) -> Dict:
        """Validate all LUKHAS schemas"""
        success, output = self.run_script(
            "schema_validator.py",
            "Schema Validation"
        )

        # Parse validation results if successful
        validation_details = {}
        if success and "JSON Results:" in output:
            try:
                json_part = output.split("JSON Results:")[1].split("\n==================================================\n")[0]
                validation_details = json.loads(json_part.strip())
            except Exception as e:
                logger.debug(f"Expected optional failure: {e}")
                pass

        return {
            "validation_passed": success,
            "output": output,
            "details": validation_details,
            "critical": True  # Schema validation is critical
        }

    def validate_directory_indexes(self) -> Dict:
        """Validate directory indexes"""
        success, output = self.run_script(
            "validate_directory_indexes.py",
            "Directory Index Validation"
        )

        # Extract validation rate from output
        validation_rate = 0.0
        if "Validation rate:" in output:
            try:
                rate_line = next(line for line in output.split('\n') if 'Validation rate:' in line)
                rate_str = rate_line.split(':')[1].strip().replace('%', '')
                validation_rate = float(rate_str) / 100
            except Exception as e:
                logger.debug(f"Expected optional failure: {e}")
                pass

        return {
            "validation_passed": success and validation_rate > 0.8,  # 80% threshold
            "validation_rate": validation_rate,
            "output": output,
            "critical": False  # Directory indexes are important but not critical
        }

    def validate_consciousness_contracts(self) -> Dict:
        """Validate consciousness component contracts"""
        success, output = self.run_script(
            "validate_consciousness_contracts.py",
            "Consciousness Contract Validation"
        )

        # Extract validation rate from output
        validation_rate = 0.0
        if "Validation rate:" in output:
            try:
                rate_line = next(line for line in output.split('\n') if 'Validation rate:' in line)
                rate_str = rate_line.split(':')[1].strip().replace('%', '')
                validation_rate = float(rate_str) / 100
            except Exception as e:
                logger.debug(f"Expected optional failure: {e}")
                pass

        return {
            "validation_passed": success and validation_rate > 0.95,  # 95% threshold
            "validation_rate": validation_rate,
            "output": output,
            "critical": False  # Contract validation is important but not critical
        }

    def check_git_status(self) -> Dict:
        """Check git repository status"""
        try:
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True, cwd=self.root_path)

            uncommitted_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Check for unpushed commits
            result = subprocess.run(['git', 'log', '--oneline', '@{u}..HEAD'],
                                  capture_output=True, text=True, cwd=self.root_path)

            unpushed_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []

            status = {
                "uncommitted_files": len(uncommitted_files),
                "uncommitted_file_list": uncommitted_files,
                "unpushed_commits": len(unpushed_commits),
                "unpushed_commit_list": unpushed_commits,
                "repository_clean": len(uncommitted_files) == 0 and len(unpushed_commits) == 0
            }

            self.log_action("Git Status Check", "SUCCESS",
                          f"Uncommitted: {len(uncommitted_files)}, Unpushed: {len(unpushed_commits)}")

            return status

        except Exception as e:
            self.log_action("Git Status Check", "ERROR", str(e))
            return {"error": str(e)}

    def check_file_integrity(self) -> Dict:
        """Check integrity of critical LUKHAS files"""
        critical_files = [
            "AI_MANIFEST.yaml",
            "claude.me",
            "lukhas_context.md",
            "docs/LUKHAS_ARCHITECTURE_MASTER.json",
            "docs/CONSCIOUSNESS_CONTRACT_REGISTRY.json",
            "docs/CONSTELLATION_ANALYSIS_SUMMARY.json"
        ]

        file_status = {}
        missing_files = []
        corrupted_files = []

        for file_path in critical_files:
            full_path = self.root_path / file_path

            if not full_path.exists():
                missing_files.append(file_path)
                file_status[file_path] = "MISSING"
            else:
                try:
                    # Check if JSON files are valid
                    if file_path.endswith('.json'):
                        with open(full_path) as f:
                            json.load(f)

                    # Check if files are not empty
                    if full_path.stat().st_size == 0:
                        corrupted_files.append(file_path)
                        file_status[file_path] = "EMPTY"
                    else:
                        file_status[file_path] = "OK"

                except json.JSONDecodeError:
                    corrupted_files.append(file_path)
                    file_status[file_path] = "CORRUPTED"
                except Exception as e:
                    corrupted_files.append(file_path)
                    file_status[file_path] = f"ERROR: {e}"

        integrity_status = {
            "total_files_checked": len(critical_files),
            "missing_files": missing_files,
            "corrupted_files": corrupted_files,
            "file_status": file_status,
            "integrity_passed": len(missing_files) == 0 and len(corrupted_files) == 0
        }

        status_msg = f"Missing: {len(missing_files)}, Corrupted: {len(corrupted_files)}"
        self.log_action("File Integrity Check",
                       "SUCCESS" if integrity_status["integrity_passed"] else "FAILED",
                       status_msg)

        return integrity_status

    def generate_maintenance_report(self) -> Dict:
        """Generate comprehensive maintenance report"""
        report = {
            "maintenance_timestamp": datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "maintenance_log": self.maintenance_log,
            "validation_results": {},
            "system_health": {},
            "recommendations": []
        }

        print("LUKHAS Automated Maintenance Pipeline")
        print("=" * 50)

        # Run all validations
        print("Running validation checks...")

        context_sync = self.validate_context_sync()
        schema_validation = self.validate_schemas()
        directory_indexes = self.validate_directory_indexes()
        contract_validation = self.validate_consciousness_contracts()

        report["validation_results"] = {
            "context_sync": context_sync,
            "schema_validation": schema_validation,
            "directory_indexes": directory_indexes,
            "contract_validation": contract_validation
        }

        print("\nRunning system health checks...")

        git_status = self.check_git_status()
        file_integrity = self.check_file_integrity()

        report["system_health"] = {
            "git_status": git_status,
            "file_integrity": file_integrity
        }

        # Generate overall health score
        critical_checks = [
            context_sync["validation_passed"],
            schema_validation["validation_passed"],
            file_integrity["integrity_passed"]
        ]

        health_score = sum(critical_checks) / len(critical_checks)
        report["overall_health_score"] = health_score

        # Generate recommendations
        if not context_sync["validation_passed"]:
            report["recommendations"].append("CRITICAL: Fix context sync issues immediately")

        if not schema_validation["validation_passed"]:
            report["recommendations"].append("CRITICAL: Resolve schema validation errors")

        if not file_integrity["integrity_passed"]:
            report["recommendations"].append("CRITICAL: Restore missing or corrupted files")

        if contract_validation["validation_rate"] < 0.95:
            report["recommendations"].append("Improve consciousness contract validation rate")

        if directory_indexes["validation_rate"] < 0.8:
            report["recommendations"].append("Fix directory index validation issues")

        if git_status.get("uncommitted_files", 0) > 0:
            report["recommendations"].append("Commit outstanding changes to git repository")

        if git_status.get("unpushed_commits", 0) > 0:
            report["recommendations"].append("Push committed changes to remote repository")

        if health_score == 1.0:
            report["recommendations"].append("System health excellent - consider automated deployment")

        return report

    def run_full_maintenance(self) -> Dict:
        """Run complete maintenance pipeline"""
        return self.generate_maintenance_report()


def main():
    parser = argparse.ArgumentParser(description='LUKHAS Automated Maintenance Pipeline')
    parser.add_argument('--output', '-o', default='maintenance_report.json',
                       help='Output file for maintenance report')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress console output')

    args = parser.parse_args()

    pipeline = LUKHASMaintenancePipeline(".")

    # Run maintenance
    report = pipeline.run_full_maintenance()

    # Print summary
    if not args.quiet:
        print("\nMaintenance Summary:")
        print(f"Overall Health Score: {report['overall_health_score']:.1%}")
        critical_passed = sum([
            report['validation_results']['context_sync']['validation_passed'],
            report['validation_results']['schema_validation']['validation_passed'],
            report['system_health']['file_integrity']['integrity_passed']
        ])
        print(f"Critical Validations: {critical_passed}/3 passed")

        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        print(f"\nDetailed report saved to: {args.output}")

    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)

    # Return exit code based on health score
    return 0 if report['overall_health_score'] >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
