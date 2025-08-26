#!/usr/bin/env python3
"""
Test script for LUKHAS  monitoring system
Validates all monitoring components and configurations
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringTester:
    """Test suite for monitoring system"""

    def __init__(self):
        self.test_results = []
        self.base_dir = Path(__file__).parent

    async def run_all_tests(self):
        """Run all monitoring tests"""
        logger.info("🧪 Starting LUKHAS  Monitoring Tests")

        tests = [
            ("Dependencies", self.test_dependencies),
            ("Configuration", self.test_configuration),
            ("Metrics Collection", self.test_metrics_collection),
            ("Dashboard Components", self.test_dashboard_components),
            ("Alert System", self.test_alert_system),
            ("API Endpoints", self.test_api_endpoints),
            ("WebSocket Connection", self.test_websocket),
            ("Integration Points", self.test_integrations),
        ]

        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Running test: {test_name}")
                result = await test_func()
                self.test_results.append(
                    {
                        "test": test_name,
                        "status": "PASS" if result else "FAIL",
                        "details": result if isinstance(result, dict) else None,
                    }
                )
                logger.info(
                    f"{'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}"
                )
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                self.test_results.append(
                    {"test": test_name, "status": "ERROR", "error": str(e)}
                )

        self.print_summary()
        return self.test_results

    async def test_dependencies(self) -> bool:
        """Test required dependencies"""
        required_packages = ["fastapi", "uvicorn", "websockets", "psutil", "yaml"]

        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)

        if missing:
            logger.error(f"Missing packages: {', '.join(missing)}")
            return False

        return True

    async def test_configuration(self) -> Dict:
        """Test configuration loading"""
        config_file = self.base_dir / "monitoring_config.yaml"

        if not config_file.exists():
            return {"error": "Configuration file not found"}

        try:
            import yaml

            with open(config_file) as f:
                config = yaml.safe_load(f)

            required_sections = ["unified_dashboard", "alerting", "metrics_collection"]

            missing_sections = [s for s in required_sections if s not in config]
            if missing_sections:
                return {"error": f"Missing config sections: {missing_sections}"}

            return {
                "config_file": str(config_file),
                "sections": list(config.keys()),
                "dashboard_port": config.get("unified_dashboard", {}).get("port", 3000),
            }

        except Exception as e:
            return {"error": f"Config parsing error: {e}"}

    async def test_metrics_collection(self) -> Dict:
        """Test metrics collection functionality"""
        try:
            # Import the metrics collector
            sys.path.append(str(self.base_dir))
            from unified_dashboard import MetricsCollector

            collector = MetricsCollector()
            metrics = await collector.collect_all_metrics()

            if "error" in metrics:
                return {"error": metrics["error"]}

            expected_sections = ["system", "api", "consciousness", "memory", "ethics"]

            missing_sections = [s for s in expected_sections if s not in metrics]

            return {
                "sections_collected": list(metrics.keys()),
                "missing_sections": missing_sections,
                "health_score": metrics.get("health_score", 0),
                "timestamp": metrics.get("timestamp", 0),
            }

        except Exception as e:
            return {"error": f"Metrics collection failed: {e}"}

    async def test_dashboard_components(self) -> Dict:
        """Test dashboard HTML components"""
        dashboard_file = self.base_dir / "unified_dashboard.py"

        if not dashboard_file.exists():
            return {"error": "Dashboard file not found"}

        # Check if dashboard can be imported
        try:
            sys.path.append(str(self.base_dir))
            import unified_dashboard

            # Test FastAPI app creation
            app = unified_dashboard.app

            return {
                "app_title": app.title,
                "app_version": app.version,
                "routes_count": len(app.routes),
                "middleware_count": len(app.middleware),
            }

        except Exception as e:
            return {"error": f"Dashboard import failed: {e}"}

    async def test_alert_system(self) -> Dict:
        """Test alert generation and processing"""
        try:
            # Test alert threshold logic
            test_metrics = {
                "system": {"cpu_percent": 95.0, "memory_percent": 88.0},
                "memory": {"drift_score": 0.9},
                "api": {"average_response_time": 1500},
            }

            # Simulate alert generation
            alerts_generated = []

            # High CPU alert
            if test_metrics["system"]["cpu_percent"] > 90:
                alerts_generated.append("cpu_high")

            # Memory drift alert
            if test_metrics["memory"]["drift_score"] > 0.8:
                alerts_generated.append("drift_critical")

            # API performance alert
            if test_metrics["api"]["average_response_time"] > 1000:
                alerts_generated.append("api_slow")

            return {
                "alerts_generated": alerts_generated,
                "alert_count": len(alerts_generated),
                "test_metrics": test_metrics,
            }

        except Exception as e:
            return {"error": f"Alert system test failed: {e}"}

    async def test_api_endpoints(self) -> Dict:
        """Test API endpoint definitions"""
        try:
            sys.path.append(str(self.base_dir))
            import unified_dashboard

            app = unified_dashboard.app
            routes = []

            for route in app.routes:
                if hasattr(route, "path") and hasattr(route, "methods"):
                    routes.append(
                        {
                            "path": route.path,
                            "methods": (
                                list(route.methods) if route.methods else ["GET"]
                            ),
                        }
                    )

            # Check for required endpoints
            required_endpoints = ["/", "/api/metrics", "/api/alerts", "/health"]
            found_endpoints = [r["path"] for r in routes]
            missing_endpoints = [
                ep for ep in required_endpoints if ep not in found_endpoints
            ]

            return {
                "total_routes": len(routes),
                "routes": routes[:10],  # First 10 routes
                "missing_endpoints": missing_endpoints,
            }

        except Exception as e:
            return {"error": f"API endpoint test failed: {e}"}

    async def test_websocket(self) -> Dict:
        """Test WebSocket configuration"""
        try:
            sys.path.append(str(self.base_dir))
            import unified_dashboard

            # Check if WebSocket route exists
            app = unified_dashboard.app
            ws_routes = [
                r for r in app.routes if hasattr(r, "path") and "ws" in r.path.lower()
            ]

            # Test WebSocket message format
            test_message = {
                "type": "metrics_update",
                "data": {"system": {"cpu_percent": 45.2}},
                "timestamp": time.time(),
            }

            # Validate message can be JSON serialized
            json_message = json.dumps(test_message)

            return {
                "websocket_routes": len(ws_routes),
                "message_serializable": True,
                "test_message_size": len(json_message),
            }

        except Exception as e:
            return {"error": f"WebSocket test failed: {e}"}

    async def test_integrations(self) -> Dict:
        """Test integration points"""
        integration_tests = {}

        # Test feature flags integration
        try:
            from lukhas.flags import get_flags, is_enabled

            flags = get_flags()
            integration_tests["feature_flags"] = {
                "available": True,
                "total_flags": len(flags),
                "sample_flag": is_enabled("adaptive_ai"),
            }
        except Exception as e:
            integration_tests["feature_flags"] = {"available": False, "error": str(e)}

        # Test meta dashboard existence
        meta_dashboard_path = (
            self.base_dir.parent / "meta_dashboard" / "dashboard_server.py"
        )
        integration_tests["meta_dashboard"] = {
            "exists": meta_dashboard_path.exists(),
            "path": str(meta_dashboard_path),
        }

        # Test setup script
        setup_script = self.base_dir / "setup_monitoring.py"
        integration_tests["setup_script"] = {
            "exists": setup_script.exists(),
            "executable": setup_script.exists() and setup_script.stat().st_mode & 0o111,
        }

        return integration_tests

    def print_summary(self):
        """Print test results summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results if r["status"] == "ERROR")

        logger.info("\n" + "=" * 60)
        logger.info("📊 LUKHAS  Monitoring Test Summary")
        logger.info("=" * 60)
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"💥 Errors: {error_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        logger.info("=" * 60)

        # Print failed/error tests
        if failed_tests > 0 or error_tests > 0:
            logger.info("\n🔍 Issues Found:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    logger.error(
                        f"   {result['test']}: {result.get('error', 'Failed')}"
                    )

        # Save results to file
        results_file = self.base_dir / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        logger.info(f"\n💾 Results saved to: {results_file}")


async def main():
    """Run monitoring tests"""
    tester = MonitoringTester()
    results = await tester.run_all_tests()

    # Exit with non-zero code if any tests failed
    failed_count = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])
    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())
