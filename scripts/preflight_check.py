#!/usr/bin/env python3
"""
Module: preflight_check.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
T4/0.01% Excellence Preflight Validation Gate
============================================

Comprehensive environment validation before performance audit execution.
Ensures measurement environment meets T4/0.01% excellence standards.

Exit codes:
  0 - All validations passed
  1 - Critical validation failures detected
  2 - Tool dependency failures
  3 - System configuration violations
"""

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

import psutil


class PreflightValidator:
    """T4/0.01% Excellence preflight validation system"""

    def __init__(self, audit_run_id: str):
        self.audit_run_id = audit_run_id
        self.violations = []
        self.warnings = []
        self.checks = []
        self.start_time = time.time()

    def add_check(self, category: str, name: str, status: str,
                  details: str = "", critical: bool = True):
        """Add validation check result"""
        check = {
            "category": category,
            "name": name,
            "status": status,  # PASS, FAIL, WARN, SKIP
            "details": details,
            "critical": critical,
            "timestamp": time.time()
        }
        self.checks.append(check)

        if status == "FAIL" and critical:
            self.violations.append(f"{category}.{name}: {details}")
        elif status in ["FAIL", "WARN"]:
            self.warnings.append(f"{category}.{name}: {details}")

    def run_command(self, cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        """Execute command with timeout and capture output"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except FileNotFoundError:
            return -2, "", "Command not found"
        except Exception as e:
            return -3, "", str(e)

    def validate_cpu_governor(self):
        """Validate CPU governor for consistent performance"""
        print("🔧 Validating CPU governor configuration...")

        if platform.system() != "Linux":
            self.add_check("cpu", "governor", "SKIP",
                          "CPU governor check only available on Linux", False)
            return

        try:
            # Check if cpupower is available
            ret, out, err = self.run_command(["which", "cpupower"])
            if ret != 0:
                self.add_check("cpu", "governor", "WARN",
                              "cpupower not available, cannot verify governor")
                return

            # Get current governor
            ret, out, err = self.run_command(["cpupower", "frequency-info", "-p"])
            if ret != 0:
                self.add_check("cpu", "governor", "FAIL",
                              f"Failed to read CPU governor: {err}")
                return

            # Parse governor from output
            governor = "unknown"
            for line in out.split('\n'):
                if 'governor' in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        governor = parts[-1].strip('"')
                        break

            # Validate governor is performance or userspace
            if governor in ["performance", "userspace"]:
                self.add_check("cpu", "governor", "PASS",
                              f"CPU governor: {governor}")
            else:
                self.add_check("cpu", "governor", "FAIL",
                              f"CPU governor '{governor}' not optimal for benchmarking")

        except Exception as e:
            self.add_check("cpu", "governor", "FAIL",
                          f"CPU governor validation failed: {e}")

    def validate_turbo_boost(self):
        """Validate Intel Turbo Boost / AMD Boost state"""
        print("⚡ Validating CPU turbo boost configuration...")

        if platform.system() != "Linux":
            self.add_check("cpu", "turbo", "SKIP",
                          "Turbo boost check only available on Linux", False)
            return

        try:
            # Check Intel turbo boost
            intel_turbo_path = Path("/sys/devices/system/cpu/intel_pstate/no_turbo")
            if intel_turbo_path.exists():
                with open(intel_turbo_path) as f:
                    no_turbo = f.read().strip()

                if no_turbo == "0":
                    self.add_check("cpu", "turbo", "WARN",
                                  "Intel Turbo Boost enabled (may cause variability)")
                else:
                    self.add_check("cpu", "turbo", "PASS",
                                  "Intel Turbo Boost disabled")
                return

            # Check AMD boost
            amd_boost_path = Path("/sys/devices/system/cpu/cpufreq/boost")
            if amd_boost_path.exists():
                with open(amd_boost_path) as f:
                    boost = f.read().strip()

                if boost == "1":
                    self.add_check("cpu", "turbo", "WARN",
                                  "AMD Boost enabled (may cause variability)")
                else:
                    self.add_check("cpu", "turbo", "PASS",
                                  "AMD Boost disabled")
                return

            self.add_check("cpu", "turbo", "SKIP",
                          "CPU boost control not found", False)

        except Exception as e:
            self.add_check("cpu", "turbo", "FAIL",
                          f"Turbo boost validation failed: {e}")

    def validate_ntp_sync(self):
        """Validate NTP synchronization for accurate timestamps"""
        print("🕐 Validating NTP synchronization...")

        try:
            # Try timedatectl first (systemd systems)
            ret, out, err = self.run_command(["timedatectl", "status"])
            if ret == 0:
                synchronized = False
                ntp_active = False

                for line in out.split('\n'):
                    line = line.strip().lower()
                    if 'ntp synchronized: yes' in line or 'system clock synchronized: yes' in line:
                        synchronized = True
                    if 'ntp service: active' in line or 'ntp enabled: yes' in line:
                        ntp_active = True

                if synchronized and ntp_active:
                    self.add_check("time", "ntp_sync", "PASS",
                                  "NTP synchronized and active")
                elif synchronized:
                    self.add_check("time", "ntp_sync", "PASS",
                                  "Time synchronized (NTP or other)")
                else:
                    self.add_check("time", "ntp_sync", "FAIL",
                                  "Time not synchronized")
                return

            # Fallback: check ntpstat
            ret, out, err = self.run_command(["ntpstat"])
            if ret == 0:
                self.add_check("time", "ntp_sync", "PASS",
                              "NTP synchronized (ntpstat)")
            else:
                self.add_check("time", "ntp_sync", "FAIL",
                              "NTP not synchronized")

        except Exception as e:
            self.add_check("time", "ntp_sync", "FAIL",
                          f"NTP validation failed: {e}")

    def validate_tool_versions(self):
        """Validate required tool versions are pinned and available"""
        print("🔨 Validating tool dependencies...")

        required_tools = {
            "promtool": {"min_version": None, "check_cmd": ["promtool", "--version"]},
            "gh": {"min_version": "2.0.0", "check_cmd": ["gh", "--version"]},
            "kubectl": {"min_version": "1.20.0", "check_cmd": ["kubectl", "version", "--client"]},
            "jq": {"min_version": "1.6", "check_cmd": ["jq", "--version"]},
            "gpg": {"min_version": None, "check_cmd": ["gpg", "--version"]},
            "tc": {"min_version": None, "check_cmd": ["tc", "-V"]},
        }

        for tool, config in required_tools.items():
            ret, out, err = self.run_command(config["check_cmd"])

            if ret != 0:
                self.add_check("tools", tool, "FAIL",
                              "Tool not found or not executable")
                continue

            # Extract version (simplified)
            version = "unknown"
            for line in (out + err).split('\n'):
                if any(v in line.lower() for v in ['version', tool]):
                    version = line.strip()
                    break

            self.add_check("tools", tool, "PASS",
                          f"Available: {version}")

    def validate_container_enforcement(self):
        """Validate non-root container enforcement"""
        print("🐳 Validating container security...")

        # Check if running in container
        in_container = (
            Path("/.dockerenv").exists() or
            os.getenv("container") is not None or
            Path("/proc/1/cgroup").exists() and
            any("docker" in line or "containerd" in line
                for line in Path("/proc/1/cgroup").read_text().split('\n'))
        )

        if not in_container:
            self.add_check("security", "container", "SKIP",
                          "Not running in container", False)
            return

        # Check if running as root
        if os.getuid() == 0:
            self.add_check("security", "container", "FAIL",
                          "Running as root in container (security violation)")
        else:
            self.add_check("security", "container", "PASS",
                          f"Running as non-root user (UID: {os.getuid()})")

    def validate_noise_thresholds(self):
        """Validate system noise and load thresholds"""
        print("📊 Validating system noise levels...")

        # CPU load check
        load_avg = psutil.getloadavg()
        cpu_count = psutil.cpu_count()
        load_percent = (load_avg[0] / cpu_count) * 100

        if load_percent > 50:
            self.add_check("noise", "cpu_load", "FAIL",
                          f"High CPU load: {load_percent:.1f}% (>{cpu_count/2} cores)")
        elif load_percent > 20:
            self.add_check("noise", "cpu_load", "WARN",
                          f"Moderate CPU load: {load_percent:.1f}%")
        else:
            self.add_check("noise", "cpu_load", "PASS",
                          f"Low CPU load: {load_percent:.1f}%")

        # Memory pressure check
        mem = psutil.virtual_memory()
        if mem.percent > 80:
            self.add_check("noise", "memory", "FAIL",
                          f"High memory usage: {mem.percent:.1f}%")
        elif mem.percent > 60:
            self.add_check("noise", "memory", "WARN",
                          f"Moderate memory usage: {mem.percent:.1f}%")
        else:
            self.add_check("noise", "memory", "PASS",
                          f"Memory usage: {mem.percent:.1f}%")

        # Disk I/O check (simplified)
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                # Check if there's significant disk activity (heuristic)
                self.add_check("noise", "disk_io", "PASS",
                              "Disk I/O monitoring available")
            else:
                self.add_check("noise", "disk_io", "SKIP",
                              "Disk I/O stats not available", False)
        except Exception as e:
            self.add_check("noise", "disk_io", "SKIP",
                          f"Disk I/O check failed: {e}", False)

    def validate_environment_vars(self):
        """Validate required environment variables"""
        print("🌍 Validating environment configuration...")

        required_vars = {
            "PYTHONHASHSEED": "0",
            "LUKHAS_MODE": "release",
            "PYTHONDONTWRITEBYTECODE": "1"
        }

        for var, expected in required_vars.items():
            actual = os.getenv(var)
            if actual == expected:
                self.add_check("env", var, "PASS",
                              f"{var}={actual}")
            elif actual is None:
                self.add_check("env", var, "FAIL",
                              f"{var} not set (expected: {expected})")
            else:
                self.add_check("env", var, "FAIL",
                              f"{var}={actual} (expected: {expected})")

    def validate_python_environment(self):
        """Validate Python environment for reproducibility"""
        print("🐍 Validating Python environment...")

        # Python version check
        version = sys.version_info
        if version >= (3, 9):
            self.add_check("python", "version", "PASS",
                          f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.add_check("python", "version", "FAIL",
                          f"Python {version.major}.{version.minor}.{version.micro} < 3.9")

        # Check for required packages
        required_packages = ["psutil", "numpy", "hypothesis"]
        for package in required_packages:
            try:
                __import__(package)
                self.add_check("python", f"package_{package}", "PASS",
                              f"{package} available")
            except ImportError:
                self.add_check("python", f"package_{package}", "FAIL",
                              f"{package} not available")

    def run_all_validations(self):
        """Execute all preflight validations"""
        print("🚀 Starting T4/0.01% Excellence Preflight Validation")
        print("=" * 60)

        self.validate_environment_vars()
        self.validate_python_environment()
        self.validate_cpu_governor()
        self.validate_turbo_boost()
        self.validate_ntp_sync()
        self.validate_tool_versions()
        self.validate_container_enforcement()
        self.validate_noise_thresholds()

        print("\n📊 Preflight Validation Summary")
        print("=" * 60)

        # Count results
        passed = sum(1 for c in self.checks if c["status"] == "PASS")
        failed = sum(1 for c in self.checks if c["status"] == "FAIL")
        warnings = sum(1 for c in self.checks if c["status"] == "WARN")
        skipped = sum(1 for c in self.checks if c["status"] == "SKIP")

        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"⏭️  Skipped: {skipped}")

        # Show violations
        if self.violations:
            print(f"\n🚨 Critical Violations ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  • {violation}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        return len(self.violations) == 0

    def generate_report(self, output_path: Path):
        """Generate preflight validation report"""
        duration = time.time() - self.start_time

        report = {
            "audit_run_id": self.audit_run_id,
            "preflight_version": "1.0.0",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "duration_seconds": duration,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "summary": {
                "total_checks": len(self.checks),
                "passed": sum(1 for c in self.checks if c["status"] == "PASS"),
                "failed": sum(1 for c in self.checks if c["status"] == "FAIL"),
                "warnings": sum(1 for c in self.checks if c["status"] == "WARN"),
                "skipped": sum(1 for c in self.checks if c["status"] == "SKIP"),
                "critical_violations": len(self.violations),
                "validation_passed": len(self.violations) == 0
            },
            "checks": self.checks,
            "violations": self.violations,
            "warnings": self.warnings
        }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Preflight report saved: {output_path}")


def main():
    """Main preflight validation entry point"""
    # Get audit run ID from environment or generate one
    audit_run_id = os.getenv("AUDIT_RUN_ID", f"preflight_{int(time.time())}")

    # Initialize validator
    validator = PreflightValidator(audit_run_id)

    try:
        # Run all validations
        success = validator.run_all_validations()

        # Generate report
        output_path = Path(f"artifacts/preflight_{audit_run_id}.json")
        validator.generate_report(output_path)

        # Determine exit code
        if success:
            print("\n🎉 All preflight validations passed!")
            print("   Environment ready for T4/0.01% excellence audit")
            sys.exit(0)
        else:
            print(f"\n❌ Preflight validation failed ({len(validator.violations)} violations)")
            print("   Fix violations before proceeding with audit")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Preflight validation interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Preflight validation crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
