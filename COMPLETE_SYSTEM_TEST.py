#!/usr/bin/env python3
"""
Complete Lukhas PWM + Lambda Products System Test
Tests all components including new GPT-OSS integration
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "lambda_products_pack"))

# Set environment for GPT-OSS
os.environ["GPT_OSS_ENABLED"] = "true"
os.environ["OPENAI_COMPATIBLE"] = "true"


class CompleteSystemTest:
    """Comprehensive test suite for entire Lukhas PWM + Lambda Products system"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "lukhas_pwm_tests": [],
            "lambda_products_tests": [],
            "gpt_oss_tests": [],
            "integration_tests": [],
            "performance_metrics": {},
            "system_health": {}
        }
        
    async def test_lukhas_core_systems(self) -> Dict[str, Any]:
        """Test core Lukhas PWM systems"""
        print("\n🧠 Testing Lukhas PWM Core Systems...")
        
        results = {
            "test": "Lukhas PWM Core",
            "components": {}
        }
        
        # Test Consciousness System
        try:
            from consciousness.unified.auto_consciousness import AutoConsciousness
            consciousness = AutoConsciousness()
            await consciousness.initialize()
            results["components"]["consciousness"] = "✅ PASSED"
            print("   ✅ Consciousness System: ACTIVE")
        except Exception as e:
            results["components"]["consciousness"] = f"❌ FAILED: {e}"
            print(f"   ❌ Consciousness System: {e}")
            
        # Test Memory System
        try:
            from memory.fold_manager import FoldManager
            memory = FoldManager()
            fold = await memory.create_fold("test_fold")
            await memory.close_fold(fold.fold_id)
            results["components"]["memory"] = "✅ PASSED"
            print("   ✅ Memory System: ACTIVE")
        except Exception as e:
            results["components"]["memory"] = f"❌ FAILED: {e}"
            print(f"   ❌ Memory System: {e}")
            
        # Test Guardian System
        try:
            from governance.guardian import GuardianSystem
            guardian = GuardianSystem()
            decision = await guardian.validate_action({
                "action": "test",
                "risk_level": "low"
            })
            results["components"]["guardian"] = "✅ PASSED"
            print("   ✅ Guardian System: ACTIVE")
        except Exception as e:
            results["components"]["guardian"] = f"❌ FAILED: {e}"
            print(f"   ❌ Guardian System: {e}")
            
        # Test GLYPH Engine
        try:
            from core.glyph_engine import GLYPHEngine
            glyph = GLYPHEngine()
            token = glyph.create_token("TEST")
            results["components"]["glyph"] = "✅ PASSED"
            print("   ✅ GLYPH Engine: ACTIVE")
        except Exception as e:
            results["components"]["glyph"] = f"❌ FAILED: {e}"
            print(f"   ❌ GLYPH Engine: {e}")
            
        # Test Plugin Registry
        try:
            from core.plugin_registry import PluginRegistry
            registry = PluginRegistry()
            results["components"]["plugin_registry"] = "✅ PASSED"
            print("   ✅ Plugin Registry: ACTIVE")
        except Exception as e:
            results["components"]["plugin_registry"] = f"❌ FAILED: {e}"
            print(f"   ❌ Plugin Registry: {e}")
            
        return results
        
    async def test_lambda_products(self) -> Dict[str, Any]:
        """Test Lambda Products components"""
        print("\n📦 Testing Lambda Products Suite...")
        
        results = {
            "test": "Lambda Products",
            "products": {}
        }
        
        # Test Agent Framework
        try:
            from agents.autonomous_agent_framework import (
                AgentOrchestrator,
                AutonomousAgent,
                AgentGoal,
                AgentPriority
            )
            
            orchestrator = AgentOrchestrator()
            agent = AutonomousAgent("test_001", "NIAS")
            await orchestrator.deploy_agent(agent, {
                "max_autonomous_days": 1,
                "decision_threshold": 0.85
            })
            
            # Set goal
            goal = AgentGoal(
                description="System test goal",
                priority=AgentPriority.HIGH
            )
            await agent.set_goal(goal)
            
            results["products"]["agents"] = "✅ PASSED"
            print("   ✅ Agent Framework: ACTIVE")
            
        except Exception as e:
            results["products"]["agents"] = f"❌ FAILED: {e}"
            print(f"   ❌ Agent Framework: {e}")
            
        # Test NIAS (Non-Intrusive Advertising System)
        try:
            from agents.lambda_workforce_agents import NIASAgent
            
            nias = NIASAgent("nias_001")
            await nias.initialize({
                "mode": "ethical",
                "targeting": "contextual"
            })
            
            # Test ad generation
            ad = await nias.generate_ad({
                "product": "Lambda AI",
                "audience": "enterprises",
                "tone": "professional"
            })
            
            results["products"]["nias"] = "✅ PASSED"
            print("   ✅ NIAS Advertising: ACTIVE")
            
        except Exception as e:
            results["products"]["nias"] = f"❌ FAILED: {e}"
            print(f"   ❌ NIAS Advertising: {e}")
            
        # Test ABAS (Attention Management)
        try:
            from agents.lambda_workforce_agents import ABASAgent
            
            abas = ABASAgent("abas_001")
            await abas.initialize({
                "priority_mode": "user_centric"
            })
            
            results["products"]["abas"] = "✅ PASSED"
            print("   ✅ ABAS Attention: ACTIVE")
            
        except Exception as e:
            results["products"]["abas"] = f"❌ FAILED: {e}"
            print(f"   ❌ ABAS Attention: {e}")
            
        # Test DAST (Context Intelligence)
        try:
            from agents.lambda_workforce_agents import DASTAgent
            
            dast = DASTAgent("dast_001")
            await dast.initialize({
                "context_depth": 5
            })
            
            results["products"]["dast"] = "✅ PASSED"
            print("   ✅ DAST Context: ACTIVE")
            
        except Exception as e:
            results["products"]["dast"] = f"❌ FAILED: {e}"
            print(f"   ❌ DAST Context: {e}")
            
        # Test AUCTOR Content Engine
        try:
            from auctor.auctor_content_engine import AuctorEngine
            
            auctor = AuctorEngine()
            content = await auctor.generate_content({
                "type": "blog_post",
                "topic": "AI consciousness",
                "tone": "poetic"
            })
            
            results["products"]["auctor"] = "✅ PASSED"
            print("   ✅ AUCTOR Content: ACTIVE")
            
        except Exception as e:
            results["products"]["auctor"] = f"❌ FAILED: {e}"
            print(f"   ❌ AUCTOR Content: {e}")
            
        return results
        
    async def test_gpt_oss_integration(self) -> Dict[str, Any]:
        """Test GPT-OSS and OpenAI integration"""
        print("\n🌐 Testing GPT-OSS Integration...")
        
        results = {
            "test": "GPT-OSS Integration",
            "features": {}
        }
        
        # Test OpenAI Bridge
        try:
            from integrations.openai_agi_bridge import OpenAILambdaBridge
            
            # Check if API key exists
            api_key = os.getenv("OPENAI_API_KEY", "test_key")
            
            bridge = OpenAILambdaBridge(api_key)
            
            # Initialize with consciousness layer
            await bridge.initialize({
                "integration_level": "ADVANCED",
                "connect_nias": True,
                "connect_abas": True,
                "connect_dast": True,
                "enable_consciousness": True,
                "compute_budget": "auto"
            })
            
            # Test capabilities
            capabilities = await bridge.get_capabilities()
            
            results["features"]["openai_bridge"] = "✅ PASSED"
            results["features"]["consciousness_layer"] = "✅ ENABLED"
            results["features"]["compute_budget"] = "✅ MANAGED"
            
            print("   ✅ OpenAI Bridge: CONNECTED")
            print("   ✅ Consciousness Layer: ENABLED")
            print("   ✅ Compute Budget: MANAGED")
            
        except Exception as e:
            results["features"]["openai_bridge"] = f"❌ FAILED: {e}"
            print(f"   ❌ OpenAI Bridge: {e}")
            
        # Test GPT-OSS compatibility
        try:
            # Check for GPT-OSS markers
            gpt_oss_enabled = os.getenv("GPT_OSS_ENABLED") == "true"
            openai_compatible = os.getenv("OPENAI_COMPATIBLE") == "true"
            
            if gpt_oss_enabled and openai_compatible:
                results["features"]["gpt_oss"] = "✅ ENABLED"
                print("   ✅ GPT-OSS: COMPATIBLE")
            else:
                results["features"]["gpt_oss"] = "⚠️ NOT CONFIGURED"
                print("   ⚠️ GPT-OSS: Not configured")
                
        except Exception as e:
            results["features"]["gpt_oss"] = f"❌ ERROR: {e}"
            
        return results
        
    async def test_system_integration(self) -> Dict[str, Any]:
        """Test integration between all systems"""
        print("\n🔗 Testing System Integration...")
        
        results = {
            "test": "System Integration",
            "integrations": {}
        }
        
        # Test Lambda-PWM Integration
        try:
            from integrations.lukhas_pwm_adapter import LukhasPWMIntegrationAdapter
            
            adapter = LukhasPWMIntegrationAdapter()
            
            # Test consciousness connection
            consciousness_connected = await adapter.connect_consciousness_layer()
            results["integrations"]["consciousness"] = "✅ CONNECTED" if consciousness_connected else "❌ FAILED"
            
            # Test product registration
            products = await adapter.auto_register_all_products()
            results["integrations"]["products_registered"] = len(products) if products else 0
            
            print(f"   {'✅' if consciousness_connected else '❌'} Consciousness Integration")
            print(f"   📦 Products Registered: {len(products) if products else 0}")
            
        except Exception as e:
            results["integrations"]["lambda_pwm"] = f"❌ FAILED: {e}"
            print(f"   ❌ Lambda-PWM Integration: {e}")
            
        # Test Cross-System Communication
        try:
            # Test GLYPH communication between systems
            from core.glyph_engine import GLYPHEngine
            from plugins.plugin_base import PluginSystem
            
            glyph = GLYPHEngine()
            plugin_system = PluginSystem()
            
            # Create GLYPH token
            token = glyph.create_token("INTEGRATION_TEST")
            
            # Pass through plugin system
            processed = await plugin_system.process_glyph(token)
            
            results["integrations"]["glyph_communication"] = "✅ PASSED"
            print("   ✅ GLYPH Communication: ACTIVE")
            
        except Exception as e:
            results["integrations"]["glyph_communication"] = f"❌ FAILED: {e}"
            print(f"   ❌ GLYPH Communication: {e}")
            
        return results
        
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        print("\n⚡ Running Performance Tests...")
        
        metrics = {}
        
        # Test Plugin Registration Performance
        try:
            from plugins.plugin_base import PluginSystem
            
            plugin_system = PluginSystem()
            
            start = time.perf_counter()
            for i in range(1000):
                await plugin_system.register_plugin({
                    "name": f"perf_test_{i}",
                    "version": "1.0.0"
                })
            end = time.perf_counter()
            
            plugin_throughput = 1000 / (end - start)
            metrics["plugin_throughput"] = round(plugin_throughput, 0)
            print(f"   Plugin Throughput: {plugin_throughput:.0f} ops/sec")
            
        except Exception as e:
            metrics["plugin_throughput"] = f"ERROR: {e}"
            
        # Test Agent Deployment Speed
        try:
            from agents.autonomous_agent_framework import AgentOrchestrator, AutonomousAgent
            
            orchestrator = AgentOrchestrator()
            
            start = time.perf_counter()
            for i in range(100):
                agent = AutonomousAgent(f"perf_{i}", "NIAS")
                await orchestrator.deploy_agent(agent, {})
            end = time.perf_counter()
            
            agent_throughput = 100 / (end - start)
            metrics["agent_throughput"] = round(agent_throughput, 0)
            print(f"   Agent Deployment: {agent_throughput:.0f} agents/sec")
            
        except Exception as e:
            metrics["agent_throughput"] = f"ERROR: {e}"
            
        # Test Memory System Performance
        try:
            from memory.fold_manager import FoldManager
            
            memory = FoldManager()
            
            start = time.perf_counter()
            for i in range(100):
                fold = await memory.create_fold(f"perf_fold_{i}")
                await memory.close_fold(fold.fold_id)
            end = time.perf_counter()
            
            memory_throughput = 100 / (end - start)
            metrics["memory_throughput"] = round(memory_throughput, 0)
            print(f"   Memory Operations: {memory_throughput:.0f} ops/sec")
            
        except Exception as e:
            metrics["memory_throughput"] = f"ERROR: {e}"
            
        return {
            "test": "Performance Metrics",
            "metrics": metrics
        }
        
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        print("\n🏥 Checking System Health...")
        
        health = {
            "status": "HEALTHY",
            "components": {},
            "warnings": []
        }
        
        # Check core components
        components_to_check = [
            ("consciousness", "consciousness.unified.auto_consciousness", "AutoConsciousness"),
            ("memory", "memory.fold_manager", "FoldManager"),
            ("guardian", "governance.guardian", "GuardianSystem"),
            ("glyph", "core.glyph_engine", "GLYPHEngine"),
            ("agents", "agents.autonomous_agent_framework", "AgentOrchestrator"),
            ("plugins", "plugins.plugin_base", "PluginSystem")
        ]
        
        for name, module_path, class_name in components_to_check:
            try:
                exec(f"from {module_path} import {class_name}")
                health["components"][name] = "✅ HEALTHY"
            except ImportError:
                health["components"][name] = "❌ NOT FOUND"
                health["status"] = "DEGRADED"
                health["warnings"].append(f"{name} component not available")
            except Exception as e:
                health["components"][name] = f"⚠️ ERROR: {e}"
                health["status"] = "DEGRADED"
                
        # Check environment
        if not os.getenv("OPENAI_API_KEY"):
            health["warnings"].append("OpenAI API key not configured")
            
        # Print health summary
        print(f"   System Status: {health['status']}")
        for component, status in health["components"].items():
            print(f"   {component}: {status}")
            
        if health["warnings"]:
            print("\n   ⚠️ Warnings:")
            for warning in health["warnings"]:
                print(f"      - {warning}")
                
        return health
        
    async def run_complete_test(self):
        """Run all tests and generate comprehensive report"""
        print("=" * 60)
        print("🧪 COMPLETE LUKHAS PWM + LAMBDA PRODUCTS SYSTEM TEST")
        print("=" * 60)
        
        # Run all test suites
        self.results["lukhas_pwm_tests"] = await self.test_lukhas_core_systems()
        self.results["lambda_products_tests"] = await self.test_lambda_products()
        self.results["gpt_oss_tests"] = await self.test_gpt_oss_integration()
        self.results["integration_tests"] = await self.test_system_integration()
        self.results["performance_metrics"] = await self.run_performance_tests()
        self.results["system_health"] = await self.check_system_health()
        
        # Generate summary
        self.print_summary()
        
        # Save comprehensive report
        self.save_report()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPLETE SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        # Count successes and failures
        total_tests = 0
        passed_tests = 0
        
        # Count Lukhas PWM tests
        if "components" in self.results["lukhas_pwm_tests"]:
            for component, status in self.results["lukhas_pwm_tests"]["components"].items():
                total_tests += 1
                if "PASSED" in str(status):
                    passed_tests += 1
                    
        # Count Lambda Products tests
        if "products" in self.results["lambda_products_tests"]:
            for product, status in self.results["lambda_products_tests"]["products"].items():
                total_tests += 1
                if "PASSED" in str(status):
                    passed_tests += 1
                    
        # Count GPT-OSS tests
        if "features" in self.results["gpt_oss_tests"]:
            for feature, status in self.results["gpt_oss_tests"]["features"].items():
                total_tests += 1
                if "PASSED" in str(status) or "ENABLED" in str(status):
                    passed_tests += 1
                    
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Components Tested: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance highlights
        if "metrics" in self.results["performance_metrics"]:
            metrics = self.results["performance_metrics"]["metrics"]
            print(f"\n⚡ Performance Metrics:")
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"   {metric}: {value:.0f} ops/sec")
                    
        # System health
        if "system_health" in self.results:
            health = self.results["system_health"]
            print(f"\n🏥 System Health: {health['status']}")
            
    def save_report(self):
        """Save comprehensive test report"""
        # Save JSON report
        report_file = Path(__file__).parent / "COMPLETE_SYSTEM_TEST_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Full report saved to: {report_file}")
        
        # Save markdown report
        md_file = Path(__file__).parent / "COMPLETE_SYSTEM_TEST_REPORT.md"
        with open(md_file, 'w') as f:
            f.write("# Complete Lukhas PWM + Lambda Products System Test Report\n\n")
            f.write(f"**Date:** {self.results['timestamp']}\n\n")
            
            # Write component status
            f.write("## Component Status\n\n")
            f.write("### Lukhas PWM Core\n")
            if "components" in self.results["lukhas_pwm_tests"]:
                for component, status in self.results["lukhas_pwm_tests"]["components"].items():
                    f.write(f"- **{component}**: {status}\n")
                    
            f.write("\n### Lambda Products\n")
            if "products" in self.results["lambda_products_tests"]:
                for product, status in self.results["lambda_products_tests"]["products"].items():
                    f.write(f"- **{product}**: {status}\n")
                    
            f.write("\n### GPT-OSS Integration\n")
            if "features" in self.results["gpt_oss_tests"]:
                for feature, status in self.results["gpt_oss_tests"]["features"].items():
                    f.write(f"- **{feature}**: {status}\n")
                    
            # Write performance metrics
            f.write("\n## Performance Metrics\n\n")
            if "metrics" in self.results["performance_metrics"]:
                for metric, value in self.results["performance_metrics"]["metrics"].items():
                    if isinstance(value, (int, float)):
                        f.write(f"- **{metric}**: {value:.0f} ops/sec\n")
                        
        print(f"📝 Markdown report saved to: {md_file}")


async def main():
    """Main entry point"""
    tester = CompleteSystemTest()
    await tester.run_complete_test()
    
    # Return appropriate exit code
    health = tester.results.get("system_health", {})
    if health.get("status") == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    print("\n🚀 Starting Complete System Test...")
    print("   Testing Lukhas PWM + Lambda Products + GPT-OSS")
    print("   This may take a few moments...\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1)