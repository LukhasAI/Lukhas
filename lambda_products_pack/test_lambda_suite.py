#!/usr/bin/env python3
"""
Lambda Products Test Suite Runner
Comprehensive testing for all Lambda components
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


class LambdaTestSuite:
    """Comprehensive test suite for Lambda Products"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
    async def test_plugin_system(self) -> Dict[str, Any]:
        """Test plugin system initialization and registration"""
        print("\n🔌 Testing Plugin System...")
        test_result = {
            "test_name": "Plugin System",
            "status": "FAILED",
            "details": {}
        }
        
        try:
            from plugins.plugin_base import PluginSystem
            
            # Initialize plugin system
            plugin_system = PluginSystem()
            test_result["details"]["initialization"] = "✅ PASSED"
            
            # Test plugin registration
            test_plugin = {
                "name": "test_plugin",
                "version": "1.0.0",
                "enabled": True
            }
            
            registered = await plugin_system.register_plugin(test_plugin)
            if registered:
                test_result["details"]["registration"] = "✅ PASSED"
            else:
                test_result["details"]["registration"] = "❌ FAILED"
            
            # Test plugin discovery
            plugins = await plugin_system.discover_plugins()
            test_result["details"]["discovery"] = f"Found {len(plugins)} plugins"
            
            test_result["status"] = "PASSED"
            print("   ✅ Plugin System: PASSED")
            
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"   ❌ Plugin System: FAILED - {e}")
            
        return test_result
    
    async def test_agent_framework(self) -> Dict[str, Any]:
        """Test autonomous agent framework"""
        print("\n🤖 Testing Agent Framework...")
        test_result = {
            "test_name": "Agent Framework",
            "status": "FAILED",
            "details": {}
        }
        
        try:
            from agents.autonomous_agent_framework import (
                AgentOrchestrator, 
                AutonomousAgent,
                AgentGoal,
                AgentPriority
            )
            
            # Initialize orchestrator
            orchestrator = AgentOrchestrator()
            test_result["details"]["orchestrator_init"] = "✅ PASSED"
            
            # Create test agent
            agent = AutonomousAgent("test_agent_001", "NIAS")
            test_result["details"]["agent_creation"] = "✅ PASSED"
            
            # Deploy agent
            config = {
                "max_autonomous_days": 1,
                "decision_threshold": 0.85
            }
            await orchestrator.deploy_agent(agent, config)
            test_result["details"]["agent_deployment"] = "✅ PASSED"
            
            # Set agent goal
            goal = AgentGoal(
                description="Test goal execution",
                priority=AgentPriority.HIGH
            )
            await agent.set_goal(goal)
            test_result["details"]["goal_setting"] = "✅ PASSED"
            
            # Check agent status
            status = await agent.get_status()
            test_result["details"]["agent_status"] = status.get("state", "UNKNOWN")
            
            test_result["status"] = "PASSED"
            print("   ✅ Agent Framework: PASSED")
            
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"   ❌ Agent Framework: FAILED - {e}")
            
        return test_result
    
    async def test_lukhas_integration(self) -> Dict[str, Any]:
        """Test Lukhas PWM integration"""
        print("\n🔗 Testing Lukhas PWM Integration...")
        test_result = {
            "test_name": "Lukhas PWM Integration",
            "status": "FAILED",
            "details": {}
        }
        
        try:
            # Check if Lukhas PWM is available
            from core.plugin_registry import PluginRegistry
            test_result["details"]["pwm_available"] = "✅ YES"
            
            # Test adapter
            from integrations.lukhas_pwm_adapter import LukhasPWMIntegrationAdapter
            adapter = LukhasPWMIntegrationAdapter()
            test_result["details"]["adapter_init"] = "✅ PASSED"
            
            # Test product registration
            products = await adapter.auto_register_all_products()
            test_result["details"]["products_registered"] = len(products) if products else 0
            
            # Test consciousness integration
            consciousness_connected = await adapter.connect_consciousness_layer()
            test_result["details"]["consciousness"] = "✅ CONNECTED" if consciousness_connected else "❌ FAILED"
            
            test_result["status"] = "PASSED"
            print("   ✅ Lukhas PWM Integration: PASSED")
            
        except ImportError:
            test_result["details"]["pwm_available"] = "❌ NO"
            test_result["details"]["info"] = "Running in standalone mode"
            test_result["status"] = "SKIPPED"
            print("   ⏭️  Lukhas PWM Integration: SKIPPED (PWM not found)")
            
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"   ❌ Lukhas PWM Integration: FAILED - {e}")
            
        return test_result
    
    async def test_openai_bridge(self) -> Dict[str, Any]:
        """Test OpenAI AGI Bridge"""
        print("\n🌐 Testing OpenAI Bridge...")
        test_result = {
            "test_name": "OpenAI Bridge",
            "status": "FAILED",
            "details": {}
        }
        
        try:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                test_result["details"]["api_key"] = "❌ NOT FOUND"
                test_result["status"] = "SKIPPED"
                print("   ⏭️  OpenAI Bridge: SKIPPED (No API key)")
                return test_result
            
            from integrations.openai_agi_bridge import OpenAILambdaBridge
            
            # Initialize bridge
            bridge = OpenAILambdaBridge(api_key)
            test_result["details"]["bridge_init"] = "✅ PASSED"
            
            # Test connection
            config = {
                "integration_level": "BASIC",
                "connect_nias": True,
                "connect_abas": True,
                "connect_dast": True
            }
            await bridge.initialize(config)
            test_result["details"]["initialization"] = "✅ PASSED"
            
            # Test capabilities
            capabilities = await bridge.get_capabilities()
            test_result["details"]["capabilities"] = len(capabilities) if capabilities else 0
            
            test_result["status"] = "PASSED"
            print("   ✅ OpenAI Bridge: PASSED")
            
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"   ❌ OpenAI Bridge: FAILED - {e}")
            
        return test_result
    
    async def test_performance(self) -> Dict[str, Any]:
        """Test system performance metrics"""
        print("\n📊 Testing Performance Metrics...")
        test_result = {
            "test_name": "Performance",
            "status": "FAILED",
            "details": {}
        }
        
        try:
            from plugins.plugin_base import PluginSystem
            
            # Test plugin registration speed
            plugin_system = PluginSystem()
            
            start_time = time.time()
            for i in range(100):
                await plugin_system.register_plugin({
                    "name": f"perf_test_{i}",
                    "version": "1.0.0"
                })
            registration_time = (time.time() - start_time) * 1000
            
            test_result["details"]["registration_time_ms"] = f"{registration_time:.2f}"
            test_result["details"]["ops_per_sec"] = f"{100 / (registration_time / 1000):.0f}"
            
            # Check against targets
            if registration_time < 200:  # < 2ms per registration
                test_result["details"]["performance"] = "✅ EXCELLENT"
                test_result["status"] = "PASSED"
            elif registration_time < 500:
                test_result["details"]["performance"] = "⚠️ ACCEPTABLE"
                test_result["status"] = "PASSED"
            else:
                test_result["details"]["performance"] = "❌ SLOW"
                
            print(f"   {'✅' if test_result['status'] == 'PASSED' else '❌'} Performance: {test_result['status']}")
            
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"   ❌ Performance: FAILED - {e}")
            
        return test_result
    
    async def run_all_tests(self):
        """Run all tests in the suite"""
        print("=" * 60)
        print("🧪 LAMBDA PRODUCTS COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_plugin_system,
            self.test_agent_framework,
            self.test_lukhas_integration,
            self.test_openai_bridge,
            self.test_performance
        ]
        
        for test_method in test_methods:
            self.results["tests_run"] += 1
            result = await test_method()
            self.results["test_details"].append(result)
            
            if result["status"] == "PASSED":
                self.results["tests_passed"] += 1
            elif result["status"] == "FAILED":
                self.results["tests_failed"] += 1
        
        # Generate summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Tests: {self.results['tests_run']}")
        print(f"   ✅ Passed: {self.results['tests_passed']}")
        print(f"   ❌ Failed: {self.results['tests_failed']}")
        print(f"   ⏭️  Skipped: {self.results['tests_run'] - self.results['tests_passed'] - self.results['tests_failed']}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Details:")
        for test in self.results["test_details"]:
            status_icon = "✅" if test["status"] == "PASSED" else "❌" if test["status"] == "FAILED" else "⏭️"
            print(f"   {status_icon} {test['test_name']}: {test['status']}")
            
    def save_results(self):
        """Save test results to file"""
        results_file = Path(__file__).parent / "test_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n💾 Results saved to: {results_file}")
        
        # Also create a markdown report
        report_file = Path(__file__).parent / "test_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Lambda Products Test Report\n\n")
            f.write(f"**Date:** {self.results['timestamp']}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {self.results['tests_run']}\n")
            f.write(f"- **Passed:** {self.results['tests_passed']}\n")
            f.write(f"- **Failed:** {self.results['tests_failed']}\n")
            f.write(f"- **Success Rate:** {(self.results['tests_passed'] / self.results['tests_run'] * 100):.1f}%\n\n")
            
            f.write("## Test Details\n\n")
            for test in self.results["test_details"]:
                f.write(f"### {test['test_name']}\n")
                f.write(f"**Status:** {test['status']}\n\n")
                if test.get("details"):
                    f.write("**Details:**\n")
                    for key, value in test["details"].items():
                        f.write(f"- {key}: {value}\n")
                f.write("\n")
                
        print(f"📝 Report saved to: {report_file}")


async def main():
    """Main entry point"""
    suite = LambdaTestSuite()
    await suite.run_all_tests()
    
    # Return exit code based on results
    if suite.results["tests_failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1)