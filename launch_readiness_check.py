#!/usr/bin/env python3
"""
🚀 LUKHAS Launch Readiness Checker
===================================
Final pre-production validation checklist.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import httpx

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class LaunchReadinessChecker:
    """Validates production readiness"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:8000"
        self.checks_passed = []
        self.checks_failed = []
        
    async def check_api_health(self) -> bool:
        """Check API server is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/tools/registry")
                return response.status_code == 200
        except:
            return False
    
    async def check_metrics_endpoint(self) -> bool:
        """Check Prometheus metrics are exposed"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/metrics")
                return response.status_code == 200 and b"lukhas_" in response.content
        except:
            return False
    
    async def check_incidents_clean(self) -> bool:
        """Check no critical incidents in last 24h"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/tools/incidents")
                if response.status_code != 200:
                    return False
                
                data = response.json()
                incidents = data.get("incidents", [])
                
                # Check for recent critical incidents
                now = datetime.now().timestamp()
                critical_count = 0
                for incident in incidents:
                    if now - incident.get("timestamp", 0) < 86400:  # 24 hours
                        if incident.get("severity") == "critical":
                            critical_count += 1
                
                return critical_count == 0
        except:
            return False
    
    def check_env_vars(self) -> dict:
        """Check required environment variables"""
        required = ["OPENAI_API_KEY"]
        optional = ["LUKHAS_FEEDBACK_DIR", "LUKHAS_AUDIT_DIR", "LOG_LEVEL"]
        
        results = {}
        for var in required:
            results[var] = {"set": bool(os.getenv(var)), "required": True}
        
        for var in optional:
            results[var] = {"set": bool(os.getenv(var)), "required": False}
        
        return results
    
    def check_directories(self) -> dict:
        """Check required directories exist"""
        dirs = {
            ".lukhas_audit": Path(".lukhas_audit"),
            ".lukhas_feedback": Path(".lukhas_feedback"),
            "lukhas_pwm": Path("lukhas_pwm"),
            "tests": Path("tests")
        }
        
        results = {}
        for name, path in dirs.items():
            results[name] = {
                "exists": path.exists(),
                "writable": path.exists() and os.access(path, os.W_OK)
            }
        
        return results
    
    def check_python_deps(self) -> dict:
        """Check Python dependencies"""
        deps = {}
        
        try:
            import openai
            deps["openai"] = {"installed": True, "version": openai.__version__}
        except ImportError:
            deps["openai"] = {"installed": False}
        
        try:
            import fastapi
            deps["fastapi"] = {"installed": True}
        except ImportError:
            deps["fastapi"] = {"installed": False}
        
        try:
            import prometheus_client
            deps["prometheus_client"] = {"installed": True}
        except ImportError:
            deps["prometheus_client"] = {"installed": False}
        
        return deps
    
    async def run_checks(self):
        """Run all readiness checks"""
        print(f"\n{GREEN}🚀 LUKHAS LAUNCH READINESS CHECK{RESET}")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: Production")
        print()
        
        # 1. API Health
        print(f"{BLUE}▶ Checking API Health...{RESET}")
        api_healthy = await self.check_api_health()
        self._report_check("API Server Running", api_healthy)
        
        # 2. Metrics
        print(f"\n{BLUE}▶ Checking Metrics...{RESET}")
        metrics_ok = await self.check_metrics_endpoint()
        self._report_check("Prometheus Metrics Available", metrics_ok)
        
        # 3. Incidents
        print(f"\n{BLUE}▶ Checking Security Incidents...{RESET}")
        incidents_clean = await self.check_incidents_clean()
        self._report_check("No Critical Incidents (24h)", incidents_clean)
        
        # 4. Environment
        print(f"\n{BLUE}▶ Checking Environment...{RESET}")
        env_vars = self.check_env_vars()
        for var, info in env_vars.items():
            if info["required"]:
                self._report_check(f"ENV: {var}", info["set"])
            else:
                status = "✅" if info["set"] else "⚠️"
                print(f"  {status} {var}: {'Set' if info['set'] else 'Not set (optional)'}")
        
        # 5. Directories
        print(f"\n{BLUE}▶ Checking Directories...{RESET}")
        dirs = self.check_directories()
        for name, info in dirs.items():
            self._report_check(f"Directory: {name}", info["exists"] and info["writable"])
        
        # 6. Dependencies
        print(f"\n{BLUE}▶ Checking Dependencies...{RESET}")
        deps = self.check_python_deps()
        for name, info in deps.items():
            self._report_check(f"Package: {name}", info["installed"])
        
        # Summary
        self._print_summary()
    
    def _report_check(self, name: str, passed: bool):
        """Report individual check result"""
        if passed:
            print(f"  ✅ {name}")
            self.checks_passed.append(name)
        else:
            print(f"  ❌ {name}")
            self.checks_failed.append(name)
    
    def _print_summary(self):
        """Print launch readiness summary"""
        total = len(self.checks_passed) + len(self.checks_failed)
        passed = len(self.checks_passed)
        
        print(f"\n{GREEN}═══ LAUNCH GATE SUMMARY ═══{RESET}")
        print("=" * 60)
        
        print(f"\nScore: {passed}/{total} checks passed")
        
        if self.checks_failed:
            print(f"\n{RED}Failed Checks:{RESET}")
            for check in self.checks_failed:
                print(f"  ❌ {check}")
        
        # Critical checks
        critical = [
            "API Server Running",
            "No Critical Incidents (24h)",
            "ENV: OPENAI_API_KEY"
        ]
        
        critical_ok = all(c in self.checks_passed for c in critical)
        
        print(f"\n{BLUE}Critical Systems:{RESET}")
        for check in critical:
            status = "✅" if check in self.checks_passed else "❌"
            print(f"  {status} {check}")
        
        # Final verdict
        print(f"\n{GREEN}═══ LAUNCH DECISION ═══{RESET}")
        if critical_ok and passed >= total * 0.8:  # 80% threshold
            print(f"{GREEN}✅ SYSTEM READY FOR PRODUCTION{RESET}")
            print("\nNext steps:")
            print("1. Run live smoke test: python3 live_openai_smoke_test.py")
            print("2. Monitor metrics: http://127.0.0.1:8000/metrics")
            print("3. Watch incidents: http://127.0.0.1:8000/tools/incidents")
            print("4. Begin gradual rollout")
        else:
            print(f"{YELLOW}⚠️  NOT READY - ADDRESS FAILED CHECKS{RESET}")
            print("\nRequired fixes:")
            for check in self.checks_failed:
                if check in critical:
                    print(f"  🔴 CRITICAL: {check}")
                else:
                    print(f"  ⚠️  {check}")


async def main():
    """Run launch readiness check"""
    checker = LaunchReadinessChecker()
    await checker.run_checks()


if __name__ == "__main__":
    asyncio.run(main())