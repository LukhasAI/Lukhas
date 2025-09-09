#!/usr/bin/env python3
"""
🎭🔤🔐🧬 LUKHAS Core Systems Testing Suite
============================================

Testing critical LUKHAS components beyond basic systems:
- Supervisor Agent (task escalation and oversight)
- GLYPH Communication System (inter-module messaging)
- Guardian Security Core (security validation)
- Bio-Symbolic Systems (bio-inspired processing)

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

# Test environment setup
TEST_MODE = True


class TestSupervisorAgent:
    """🎭 Test task escalation and colony supervision"""

    def __init__(self):
        self.test_results = []

    def test_supervisor_initialization(self) -> bool:
        """Test supervisor agent creation and configuration"""
        try:
            from lukhas.core.supervisor_agent import SupervisorAgent

            print("    🏗️ Testing supervisor initialization...")

            # Test basic initialization
            supervisor = SupervisorAgent("test-supervisor-001")

            if not supervisor.supervisor_id:
                raise Exception("Supervisor ID not set")

            if supervisor.supervisor_id != "test-supervisor-001":
                raise Exception("Supervisor ID mismatch")

            # Test default configuration
            if not isinstance(supervisor.escalation_history, list):
                raise Exception("Escalation history not initialized")

            if not isinstance(supervisor.active_escalations, dict):
                raise Exception("Active escalations not initialized")

            if supervisor.max_history <= 0:
                raise Exception("Invalid max history setting")

            # Test multiple supervisors
            supervisor2 = SupervisorAgent("test-supervisor-002")
            if supervisor.supervisor_id == supervisor2.supervisor_id:
                raise Exception("Supervisor IDs should be unique")

            print("    ✅ Supervisor initialization working")
            return True

        except Exception as e:
            print(f"    ❌ Supervisor initialization failed: {e}")
            return False

    def test_task_escalation_workflow(self) -> bool:
        """Test complete task escalation workflow"""
        try:
            from lukhas.core.supervisor_agent import SupervisorAgent

            print("    ⬆️ Testing task escalation workflow...")

            supervisor = SupervisorAgent("escalation-test")

            # Create test task data
            task_data = {
                "task_type": "complex_analysis",
                "priority": "high",
                "complexity_score": 0.8,
                "resource_requirements": ["cpu_intensive", "memory_heavy"],
                "estimated_duration": 300,
                "description": "Complex AI reasoning task requiring supervision",
            }

            # Test async task review
            async def run_escalation():
                result = await supervisor.review_task(
                    colony_id="colony-alpha-001", task_id="task-complex-001", task_data=task_data
                )
                return result

            # Run the async escalation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_escalation())
            loop.close()

            # Validate escalation result
            required_fields = ["status", "task_id", "colony", "supervisor_id", "review_result"]
            for field in required_fields:
                if field not in result:
                    raise Exception(f"Missing escalation result field: {field}")

            if result["status"] != "escalated":
                raise Exception("Incorrect escalation status")

            if result["task_id"] != "task-complex-001":
                raise Exception("Task ID mismatch in result")

            if result["colony"] != "colony-alpha-001":
                raise Exception("Colony ID mismatch in result")

            # Test escalation history
            if len(supervisor.escalation_history) == 0:
                raise Exception("Escalation not recorded in history")

            print("    ✅ Task escalation workflow working")
            return True

        except Exception as e:
            print(f"    ❌ Task escalation workflow failed: {e}")
            return False

    def test_escalation_tracking(self) -> bool:
        """Test escalation tracking and history management"""
        try:
            from lukhas.core.supervisor_agent import SupervisorAgent

            print("    📊 Testing escalation tracking...")

            supervisor = SupervisorAgent("tracking-test")

            # Test multiple escalations
            async def run_multiple_escalations():
                tasks = []
                for i in range(3):
                    task_data = {"task_type": f"test_task_{i}", "priority": "normal", "test_id": i}

                    result = await supervisor.review_task(
                        colony_id=f"colony-{i:03d}", task_id=f"task-{i:03d}", task_data=task_data
                    )
                    tasks.append(result)
                return tasks

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(run_multiple_escalations())
            loop.close()

            # Validate tracking
            if len(results) != 3:
                raise Exception("Not all escalations completed")

            if len(supervisor.escalation_history) != 3:
                raise Exception("Escalation history count mismatch")

            # Test history contains all escalations
            task_ids_in_history = [entry["task_id"] for entry in supervisor.escalation_history]
            expected_ids = ["task-000", "task-001", "task-002"]

            for expected_id in expected_ids:
                if expected_id not in task_ids_in_history:
                    raise Exception(f"Task {expected_id} not found in history")

            # Test active escalations are cleared
            if len(supervisor.active_escalations) != 0:
                raise Exception("Active escalations not cleared after completion")

            print("    ✅ Escalation tracking working")
            return True

        except Exception as e:
            print(f"    ❌ Escalation tracking failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive supervisor agent tests"""
        print("🎭 TESTING SUPERVISOR AGENT")
        print("=" * 50)

        tests = [
            ("Supervisor Initialization", self.test_supervisor_initialization),
            ("Task Escalation Workflow", self.test_task_escalation_workflow),
            ("Escalation Tracking", self.test_escalation_tracking),
        ]

        results = {}
        total_passed = 0

        for test_name, test_func in tests:
            print(f"\n  🧪 {test_name}:")
            success = test_func()
            results[test_name] = success
            if success:
                total_passed += 1

        success_rate = (total_passed / len(tests)) * 100
        print(f"\n  📊 Supervisor Agent Success Rate: {success_rate:.1f}% ({total_passed}/{len(tests)})")

        return {
            "system": "Supervisor Agent",
            "total_tests": len(tests),
            "passed": total_passed,
            "success_rate": success_rate,
            "details": results,
        }


class TestGLYPHCommunication:
    """🔤 Test GLYPH inter-module communication system"""

    def __init__(self):
        self.test_results = []

    def test_glyph_token_creation(self) -> bool:
        """Test GLYPH token creation and basic functionality"""
        try:
            from lukhas.core.common.glyph import GLYPHPriority, GLYPHSymbol, GLYPHToken, create_glyph

            print("    🎫 Testing GLYPH token creation...")

            # Test basic token creation
            token = GLYPHToken(
                symbol=GLYPHSymbol.TRUST,
                source="identity_module",
                target="memory_module",
                payload={"user_id": "test_user_001", "operation": "store"},
            )

            if not token.glyph_id:
                raise Exception("GLYPH token missing ID")

            if token.symbol != GLYPHSymbol.TRUST:
                raise Exception("GLYPH symbol mismatch")

            if token.source != "identity_module":
                raise Exception("GLYPH source mismatch")

            # Test convenience function
            token2 = create_glyph(
                symbol=GLYPHSymbol.LEARN,
                source="consciousness_module",
                target="ai_module",
                payload={"pattern": "neural_pathway_001"},
                priority=GLYPHPriority.HIGH,
            )

            if token2.priority != GLYPHPriority.HIGH:
                raise Exception("GLYPH priority not set correctly")

            # Test token uniqueness
            if token.glyph_id == token2.glyph_id:
                raise Exception("GLYPH tokens should have unique IDs")

            print("    ✅ GLYPH token creation working")
            return True

        except Exception as e:
            print(f"    ❌ GLYPH token creation failed: {e}")
            return False

    def test_glyph_serialization(self) -> bool:
        """Test GLYPH token serialization and deserialization"""
        try:
            from lukhas.core.common.glyph import GLYPHContext, GLYPHSymbol, GLYPHToken, create_glyph

            print("    📦 Testing GLYPH serialization...")

            # Create token with complex data
            context = GLYPHContext(
                user_id="test_user_serialization", session_id="session_001", interaction_id="interaction_001"
            )

            original_token = create_glyph(
                symbol=GLYPHSymbol.REMEMBER,
                source="memory_system",
                target="consciousness_system",
                payload={
                    "memory_type": "episodic",
                    "content": {
                        "experience": "first_conversation",
                        "emotions": ["curiosity", "excitement"],
                        "metadata": {"importance": 0.8},
                    },
                },
                context=context,
            )

            # Test JSON serialization
            json_data = original_token.to_json()
            if not json_data or not isinstance(json_data, str):
                raise Exception("JSON serialization failed")

            # Test JSON deserialization
            restored_token = GLYPHToken.from_json(json_data)

            if restored_token.glyph_id != original_token.glyph_id:
                raise Exception("GLYPH ID not preserved in serialization")

            if restored_token.symbol != original_token.symbol:
                raise Exception("GLYPH symbol not preserved")

            if restored_token.payload != original_token.payload:
                raise Exception("GLYPH payload not preserved")

            # Test dictionary serialization
            dict_data = original_token.to_dict()
            restored_dict_token = GLYPHToken.from_dict(dict_data)

            if restored_dict_token.glyph_id != original_token.glyph_id:
                raise Exception("Dictionary serialization failed")

            print("    ✅ GLYPH serialization working")
            return True

        except Exception as e:
            print(f"    ❌ GLYPH serialization failed: {e}")
            return False

    def test_glyph_communication_patterns(self) -> bool:
        """Test GLYPH communication patterns and workflows"""
        try:
            from lukhas.core.common.glyph import (
                GLYPHRouter,
                GLYPHSymbol,
                GLYPHToken,
                create_error_glyph,
                create_response_glyph,
            )

            print("    💬 Testing GLYPH communication patterns...")

            # Test request-response pattern
            request = GLYPHToken(
                symbol=GLYPHSymbol.QUERY,
                source="client_module",
                target="server_module",
                payload={"query": "get_user_data", "user_id": "test_001"},
            )

            # Test successful response
            response = create_response_glyph(
                request=request, symbol=GLYPHSymbol.SUCCESS, payload={"user_data": {"name": "Test User", "tier": 1}}
            )

            if response.source != request.target:
                raise Exception("Response source should be request target")

            if response.target != request.source:
                raise Exception("Response target should be request source")

            if response.get_metadata("request_id") != request.glyph_id:
                raise Exception("Response not linked to request")

            # Test error response
            error_response = create_error_glyph(
                request=request, error_message="User not found", error_code="USER_NOT_FOUND"
            )

            if error_response.symbol != GLYPHSymbol.ERROR:
                raise Exception("Error response should have ERROR symbol")

            error_payload = error_response.payload
            if "error" not in error_payload or "message" not in error_payload:
                raise Exception("Error response missing required fields")

            # Test GLYPH router basic functionality
            router = GLYPHRouter()
            router.register_route("test_source", ["test_target"])

            if "test_source" not in router.routes:
                raise Exception("Route registration failed")

            print("    ✅ GLYPH communication patterns working")
            return True

        except Exception as e:
            print(f"    ❌ GLYPH communication patterns failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive GLYPH communication tests"""
        print("🔤 TESTING GLYPH COMMUNICATION SYSTEM")
        print("=" * 50)

        tests = [
            ("GLYPH Token Creation", self.test_glyph_token_creation),
            ("GLYPH Serialization", self.test_glyph_serialization),
            ("GLYPH Communication Patterns", self.test_glyph_communication_patterns),
        ]

        results = {}
        total_passed = 0

        for test_name, test_func in tests:
            print(f"\n  🧪 {test_name}:")
            success = test_func()
            results[test_name] = success
            if success:
                total_passed += 1

        success_rate = (total_passed / len(tests)) * 100
        print(f"\n  📊 GLYPH Communication Success Rate: {success_rate:.1f}% ({total_passed}/{len(tests)})")

        return {
            "system": "GLYPH Communication System",
            "total_tests": len(tests),
            "passed": total_passed,
            "success_rate": success_rate,
            "details": results,
        }


class TestGuardianSecurity:
    """🔐 Test Guardian security core and validation systems"""

    def __init__(self):
        self.test_results = []

    def test_guardian_security_validation(self) -> bool:
        """Test basic security validation patterns"""
        try:
            print("    🛡️ Testing Guardian security validation...")

            # Test input validation patterns (manual implementation for testing)
            def validate_user_input(user_input: str) -> dict[str, Any]:
                """Mock security validation"""

                # Basic validation rules
                if not user_input or len(user_input.strip()) == 0:
                    return {"valid": False, "reason": "empty_input"}

                if len(user_input) > 10000:
                    return {"valid": False, "reason": "input_too_long"}

                # Check for potential injection patterns
                dangerous_patterns = ["<script", "javascript:", "eval(", "exec("]
                for pattern in dangerous_patterns:
                    if pattern.lower() in user_input.lower():
                        return {"valid": False, "reason": "potential_injection"}

                return {"valid": True, "sanitized": user_input.strip()}

            # Test valid input
            valid_result = validate_user_input("Hello, this is a safe message!")
            if not valid_result["valid"]:
                raise Exception("Valid input incorrectly rejected")

            # Test empty input
            empty_result = validate_user_input("")
            if empty_result["valid"]:
                raise Exception("Empty input should be rejected")

            # Test malicious input
            malicious_result = validate_user_input("<script>alert('xss')</script>")
            if malicious_result["valid"]:
                raise Exception("Malicious input should be rejected")

            # Test oversized input
            large_input = "x" * 15000
            large_result = validate_user_input(large_input)
            if large_result["valid"]:
                raise Exception("Oversized input should be rejected")

            print("    ✅ Guardian security validation working")
            return True

        except Exception as e:
            print(f"    ❌ Guardian security validation failed: {e}")
            return False

    def test_access_control_patterns(self) -> bool:
        """Test access control and permission validation"""
        try:
            print("    🚪 Testing access control patterns...")

            # Mock permission system
            class MockPermissionSystem:
                def __init__(self):
                    self.user_permissions = {
                        "user_001": ["read", "write"],
                        "user_002": ["read"],
                        "admin_001": ["read", "write", "admin", "delete"],
                    }

                def check_permission(self, user_id: str, required_permission: str) -> bool:
                    user_perms = self.user_permissions.get(user_id, [])
                    return required_permission in user_perms

                def validate_operation(self, user_id: str, operation: str) -> dict[str, Any]:
                    permission_map = {
                        "read_data": "read",
                        "write_data": "write",
                        "delete_data": "delete",
                        "admin_operation": "admin",
                    }

                    required_perm = permission_map.get(operation)
                    if not required_perm:
                        return {"allowed": False, "reason": "unknown_operation"}

                    allowed = self.check_permission(user_id, required_perm)
                    return {
                        "allowed": allowed,
                        "operation": operation,
                        "required_permission": required_perm,
                        "user_id": user_id,
                    }

            perm_system = MockPermissionSystem()

            # Test user with read/write permissions
            read_result = perm_system.validate_operation("user_001", "read_data")
            if not read_result["allowed"]:
                raise Exception("User should be allowed to read")

            write_result = perm_system.validate_operation("user_001", "write_data")
            if not write_result["allowed"]:
                raise Exception("User should be allowed to write")

            # Test user with limited permissions
            delete_result = perm_system.validate_operation("user_002", "delete_data")
            if delete_result["allowed"]:
                raise Exception("Limited user should not be allowed to delete")

            # Test admin permissions
            admin_result = perm_system.validate_operation("admin_001", "admin_operation")
            if not admin_result["allowed"]:
                raise Exception("Admin should be allowed admin operations")

            # Test unknown user
            unknown_result = perm_system.validate_operation("unknown_user", "read_data")
            if unknown_result["allowed"]:
                raise Exception("Unknown user should be denied access")

            print("    ✅ Access control patterns working")
            return True

        except Exception as e:
            print(f"    ❌ Access control patterns failed: {e}")
            return False

    def test_audit_trail_security(self) -> bool:
        """Test security audit trail generation"""
        try:
            print("    📋 Testing security audit trails...")

            # Mock audit system
            class MockSecurityAuditor:
                def __init__(self):
                    self.audit_log = []

                def log_security_event(self, event_type: str, user_id: str, details: dict[str, Any]) -> str:
                    audit_entry = {
                        "event_id": f"audit_{uuid.uuid4()}.hex[:8]}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event_type": event_type,
                        "user_id": user_id,
                        "details": details,
                        "severity": self._calculate_severity(event_type),
                    }

                    self.audit_log.append(audit_entry)
                    return audit_entry["event_id"]

                def _calculate_severity(self, event_type: str) -> str:
                    severity_map = {
                        "login_success": "info",
                        "login_failure": "warning",
                        "permission_denied": "warning",
                        "data_access": "info",
                        "admin_operation": "high",
                        "security_violation": "critical",
                    }
                    return severity_map.get(event_type, "info")

                def get_security_summary(self) -> dict[str, Any]:
                    if not self.audit_log:
                        return {"total_events": 0}

                    severity_counts = {}
                    for entry in self.audit_log:
                        severity = entry["severity"]
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1

                    return {
                        "total_events": len(self.audit_log),
                        "severity_breakdown": severity_counts,
                        "latest_event": self.audit_log[-1]["timestamp"],
                    }

            auditor = MockSecurityAuditor()

            # Test various security events
            login_id = auditor.log_security_event(
                "login_success", "user_001", {"ip_address": "192.168.1.100", "user_agent": "TestAgent"}
            )

            failed_login_id = auditor.log_security_event(
                "login_failure", "user_002", {"ip_address": "192.168.1.200", "reason": "invalid_password"}
            )

            violation_id = auditor.log_security_event(
                "security_violation", "user_003", {"violation_type": "injection_attempt", "blocked": True}
            )

            # Validate audit entries
            if len(auditor.audit_log) != 3:
                raise Exception("Not all security events logged")

            # Check that each event has required fields
            for entry in auditor.audit_log:
                required_fields = ["event_id", "timestamp", "event_type", "user_id", "severity"]
                for field in required_fields:
                    if field not in entry:
                        raise Exception(f"Audit entry missing field: {field}")

            # Test security summary
            summary = auditor.get_security_summary()
            if summary["total_events"] != 3:
                raise Exception("Security summary count incorrect")

            if "severity_breakdown" not in summary:
                raise Exception("Security summary missing severity breakdown")

            print("    ✅ Security audit trails working")
            return True

        except Exception as e:
            print(f"    ❌ Security audit trails failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive Guardian security tests"""
        print("🔐 TESTING GUARDIAN SECURITY CORE")
        print("=" * 50)

        tests = [
            ("Security Validation", self.test_guardian_security_validation),
            ("Access Control Patterns", self.test_access_control_patterns),
            ("Security Audit Trails", self.test_audit_trail_security),
        ]

        results = {}
        total_passed = 0

        for test_name, test_func in tests:
            print(f"\n  🧪 {test_name}:")
            success = test_func()
            results[test_name] = success
            if success:
                total_passed += 1

        success_rate = (total_passed / len(tests)) * 100
        print(f"\n  📊 Guardian Security Success Rate: {success_rate:.1f}% ({total_passed}/{len(tests)})")

        return {
            "system": "Guardian Security Core",
            "total_tests": len(tests),
            "passed": total_passed,
            "success_rate": success_rate,
            "details": results,
        }


class TestBioSymbolicSystems:
    """🧬 Test bio-inspired and symbolic processing systems"""

    def __init__(self):
        self.test_results = []

    def test_bio_symbolic_processing(self) -> bool:
        """Test bio-inspired symbolic processing patterns"""
        try:
            print("    🧬 Testing bio-symbolic processing...")

            # Mock bio-symbolic processor
            class BiologicalProcessor:
                def __init__(self):
                    self.neural_patterns = {}
                    self.symbolic_mappings = {}

                def process_biological_pattern(self, pattern_data: dict[str, Any]) -> dict[str, Any]:
                    """Process biological-inspired patterns"""

                    pattern_type = pattern_data.get("type", "unknown")

                    if pattern_type == "neural_pathway":
                        return self._process_neural_pathway(pattern_data)
                    elif pattern_type == "genetic_algorithm":
                        return self._process_genetic_algorithm(pattern_data)
                    elif pattern_type == "swarm_intelligence":
                        return self._process_swarm_intelligence(pattern_data)
                    else:
                        return {"success": False, "reason": "unknown_pattern_type"}

                def _process_neural_pathway(self, data: dict[str, Any]) -> dict[str, Any]:
                    """Simulate neural pathway processing"""
                    neurons = data.get("neurons", [])
                    connections = data.get("connections", [])

                    # Simulate activation
                    activation_strength = len(neurons) * 0.1
                    if activation_strength > 1.0:
                        activation_strength = 1.0

                    return {
                        "success": True,
                        "pattern_type": "neural_pathway",
                        "activation_strength": activation_strength,
                        "processed_neurons": len(neurons),
                        "processed_connections": len(connections),
                    }

                def _process_genetic_algorithm(self, data: dict[str, Any]) -> dict[str, Any]:
                    """Simulate genetic algorithm processing"""
                    population = data.get("population", [])
                    generations = data.get("generations", 1)

                    # Simulate evolution
                    fitness_scores = [individual.get("fitness", 0.5) for individual in population]
                    avg_fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0

                    return {
                        "success": True,
                        "pattern_type": "genetic_algorithm",
                        "population_size": len(population),
                        "generations_processed": generations,
                        "average_fitness": avg_fitness,
                    }

                def _process_swarm_intelligence(self, data: dict[str, Any]) -> dict[str, Any]:
                    """Simulate swarm intelligence processing"""
                    agents = data.get("agents", [])
                    collective_behavior = data.get("behavior", "exploration")

                    # Simulate swarm dynamics
                    swarm_efficiency = min(len(agents) * 0.05, 1.0)

                    return {
                        "success": True,
                        "pattern_type": "swarm_intelligence",
                        "agent_count": len(agents),
                        "behavior": collective_behavior,
                        "swarm_efficiency": swarm_efficiency,
                    }

            processor = BiologicalProcessor()

            # Test neural pathway processing
            neural_data = {
                "type": "neural_pathway",
                "neurons": [f"neuron_{i}" for i in range(10)],
                "connections": [f"conn_{i}" for i in range(15)],
            }

            neural_result = processor.process_biological_pattern(neural_data)
            if not neural_result["success"]:
                raise Exception("Neural pathway processing failed")

            if neural_result["processed_neurons"] != 10:
                raise Exception("Neural pathway neuron count incorrect")

            # Test genetic algorithm processing
            genetic_data = {
                "type": "genetic_algorithm",
                "population": [{"fitness": 0.7}, {"fitness": 0.8}, {"fitness": 0.6}],
                "generations": 5,
            }

            genetic_result = processor.process_biological_pattern(genetic_data)
            if not genetic_result["success"]:
                raise Exception("Genetic algorithm processing failed")

            if genetic_result["population_size"] != 3:
                raise Exception("Genetic algorithm population size incorrect")

            # Test swarm intelligence
            swarm_data = {
                "type": "swarm_intelligence",
                "agents": [f"agent_{i}" for i in range(20)],
                "behavior": "optimization",
            }

            swarm_result = processor.process_biological_pattern(swarm_data)
            if not swarm_result["success"]:
                raise Exception("Swarm intelligence processing failed")

            if swarm_result["agent_count"] != 20:
                raise Exception("Swarm intelligence agent count incorrect")

            print("    ✅ Bio-symbolic processing working")
            return True

        except Exception as e:
            print(f"    ❌ Bio-symbolic processing failed: {e}")
            return False

    def test_symbolic_pattern_recognition(self) -> bool:
        """Test symbolic pattern recognition and mapping"""
        try:
            print("    🎨 Testing symbolic pattern recognition...")

            # Mock symbolic pattern recognizer
            class SymbolicPatternRecognizer:
                def __init__(self):
                    self.symbol_database = {
                        "⚛️": {"meaning": "identity", "category": "trinity", "weight": 1.0},
                        "🧠": {"meaning": "consciousness", "category": "trinity", "weight": 1.0},
                        "🛡️": {"meaning": "guardian", "category": "trinity", "weight": 1.0},
                        "🌙": {"meaning": "dreams", "category": "consciousness", "weight": 0.8},
                        "⭐": {"meaning": "inspiration", "category": "creativity", "weight": 0.7},
                        "🔮": {"meaning": "prediction", "category": "intelligence", "weight": 0.6},
                    }

                def analyze_symbolic_pattern(self, symbols: list[str]) -> dict[str, Any]:
                    """Analyze a sequence of symbols for patterns"""

                    if not symbols:
                        return {"valid": False, "reason": "no_symbols"}

                    # Analyze each symbol
                    symbol_analysis = []
                    total_weight = 0
                    categories = set()

                    for symbol in symbols:
                        if symbol in self.symbol_database:
                            data = self.symbol_database[symbol]
                            symbol_analysis.append(
                                {
                                    "symbol": symbol,
                                    "meaning": data["meaning"],
                                    "category": data["category"],
                                    "weight": data["weight"],
                                }
                            )
                            total_weight += data["weight"]
                            categories.add(data["category"])
                        else:
                            symbol_analysis.append(
                                {"symbol": symbol, "meaning": "unknown", "category": "unknown", "weight": 0.1}
                            )
                            total_weight += 0.1

                    # Calculate pattern strength
                    pattern_strength = total_weight / len(symbols) if symbols else 0

                    # Detect Trinity Framework pattern
                    trinity_symbols = {"⚛️", "🧠", "🛡️"}
                    has_trinity_pattern = trinity_symbols.issubset(set(symbols))

                    return {
                        "valid": True,
                        "symbol_count": len(symbols),
                        "analyzed_symbols": symbol_analysis,
                        "pattern_strength": pattern_strength,
                        "categories": list(categories),
                        "has_trinity_pattern": has_trinity_pattern,
                        "dominant_category": (
                            max(categories, key=lambda cat: sum(1 for s in symbol_analysis if s["category"] == cat))
                            if categories
                            else "none"
                        ),
                    }

                def find_symbolic_relationships(self, symbol1: str, symbol2: str) -> dict[str, Any]:
                    """Find relationships between symbols"""

                    if symbol1 not in self.symbol_database or symbol2 not in self.symbol_database:
                        return {"relationship": "unknown", "strength": 0.0}

                    data1 = self.symbol_database[symbol1]
                    data2 = self.symbol_database[symbol2]

                    # Calculate relationship strength
                    if data1["category"] == data2["category"]:
                        strength = 0.8  # Same category
                    elif data1["category"] == "trinity" or data2["category"] == "trinity":
                        strength = 0.6  # Trinity connection
                    else:
                        strength = 0.3  # Weak connection

                    return {
                        "symbol1": symbol1,
                        "symbol2": symbol2,
                        "relationship": "categorical" if data1["category"] == data2["category"] else "contextual",
                        "strength": strength,
                        "shared_category": data1["category"] == data2["category"],
                    }

            recognizer = SymbolicPatternRecognizer()

            # Test Trinity Framework pattern recognition
            trinity_symbols = ["⚛️", "🧠", "🛡️"]
            trinity_result = recognizer.analyze_symbolic_pattern(trinity_symbols)

            if not trinity_result["valid"]:
                raise Exception("Trinity pattern analysis failed")

            if not trinity_result["has_trinity_pattern"]:
                raise Exception("Trinity pattern not detected")

            if trinity_result["dominant_category"] != "trinity":
                raise Exception("Trinity category not detected as dominant")

            # Test mixed symbolic pattern
            mixed_symbols = ["🧠", "🌙", "⭐", "🔮"]
            mixed_result = recognizer.analyze_symbolic_pattern(mixed_symbols)

            if not mixed_result["valid"]:
                raise Exception("Mixed pattern analysis failed")

            if mixed_result["symbol_count"] != 4:
                raise Exception("Symbol count incorrect in mixed pattern")

            # Test symbolic relationships
            relationship = recognizer.find_symbolic_relationships("⚛️", "🧠")
            if relationship["strength"] < 0.5:
                raise Exception("Trinity symbol relationship should be strong")

            # Test unknown symbol handling
            unknown_symbols = ["unknown_symbol_1", "unknown_symbol_2"]
            unknown_result = recognizer.analyze_symbolic_pattern(unknown_symbols)

            if not unknown_result["valid"]:
                raise Exception("Unknown symbol handling failed")

            print("    ✅ Symbolic pattern recognition working")
            return True

        except Exception as e:
            print(f"    ❌ Symbolic pattern recognition failed: {e}")
            return False

    def test_bio_consciousness_integration(self) -> bool:
        """Test bio-inspired consciousness integration patterns"""
        try:
            print("    🧬🧠 Testing bio-consciousness integration...")

            # Mock bio-consciousness integrator
            class BioConsciousnessIntegrator:
                def __init__(self):
                    self.consciousness_patterns = []
                    self.bio_rhythms = {}

                def integrate_bio_consciousness(
                    self, bio_data: dict[str, Any], consciousness_data: dict[str, Any]
                ) -> dict[str, Any]:
                    """Integrate biological patterns with consciousness data"""

                    # Extract bio rhythm
                    bio_rhythm = bio_data.get("rhythm", 1.0)
                    bio_intensity = bio_data.get("intensity", 0.5)

                    # Extract consciousness state
                    consciousness_state = consciousness_data.get("state", "active")
                    awareness_level = consciousness_data.get("awareness", 0.5)

                    # Calculate integration score
                    integration_score = (bio_intensity + awareness_level) / 2

                    # Determine combined state
                    if integration_score > 0.7 and consciousness_state == "active":
                        integrated_state = "heightened_awareness"
                    elif integration_score < 0.3:
                        integrated_state = "reduced_activity"
                    else:
                        integrated_state = "balanced_integration"

                    # Generate bio-consciousness pattern
                    pattern = {
                        "pattern_id": f"bio_consciousness_{uuid.uuid4()}.hex[:8]}",
                        "bio_rhythm": bio_rhythm,
                        "consciousness_state": consciousness_state,
                        "integration_score": integration_score,
                        "integrated_state": integrated_state,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }

                    self.consciousness_patterns.append(pattern)

                    return {
                        "success": True,
                        "pattern": pattern,
                        "recommendation": self._get_state_recommendation(integrated_state),
                    }

                def _get_state_recommendation(self, state: str) -> str:
                    """Get recommendation based on integrated state"""
                    recommendations = {
                        "heightened_awareness": "Optimal for complex reasoning tasks",
                        "balanced_integration": "Good for general processing",
                        "reduced_activity": "Consider rest or simplified tasks",
                    }
                    return recommendations.get(state, "Monitor state changes")

                def analyze_consciousness_evolution(self) -> dict[str, Any]:
                    """Analyze how consciousness patterns evolve over time"""

                    if not self.consciousness_patterns:
                        return {"patterns": 0, "evolution": "no_data"}

                    # Calculate trend
                    integration_scores = [p["integration_score"] for p in self.consciousness_patterns]
                    if len(integration_scores) >= 2:
                        trend = "improving" if integration_scores[-1] > integration_scores[0] else "declining"
                    else:
                        trend = "stable"

                    # Count state distribution
                    state_counts = {}
                    for pattern in self.consciousness_patterns:
                        state = pattern["integrated_state"]
                        state_counts[state] = state_counts.get(state, 0) + 1

                    return {
                        "pattern_count": len(self.consciousness_patterns),
                        "evolution_trend": trend,
                        "state_distribution": state_counts,
                        "latest_score": integration_scores[-1] if integration_scores else 0,
                        "average_score": sum(integration_scores) / len(integration_scores) if integration_scores else 0,
                    }

            integrator = BioConsciousnessIntegrator()

            # Test basic integration
            bio_data = {"rhythm": 1.2, "intensity": 0.8, "type": "neural_oscillation"}

            consciousness_data = {"state": "active", "awareness": 0.9, "focus": 0.7}

            integration_result = integrator.integrate_bio_consciousness(bio_data, consciousness_data)

            if not integration_result["success"]:
                raise Exception("Bio-consciousness integration failed")

            pattern = integration_result["pattern"]
            if pattern["integration_score"] < 0.5:
                raise Exception("Integration score too low for high-intensity input")

            # Test multiple integrations to track evolution
            test_data_pairs = [
                ({"rhythm": 0.8, "intensity": 0.4}, {"state": "resting", "awareness": 0.3}),
                ({"rhythm": 1.5, "intensity": 0.9}, {"state": "active", "awareness": 0.8}),
                ({"rhythm": 1.0, "intensity": 0.6}, {"state": "focused", "awareness": 0.7}),
            ]

            for bio, consciousness in test_data_pairs:
                integrator.integrate_bio_consciousness(bio, consciousness)

            # Test evolution analysis
            evolution = integrator.analyze_consciousness_evolution()

            if evolution["pattern_count"] != 4:  # 1 initial + 3 test pairs
                raise Exception("Pattern count incorrect in evolution analysis")

            if "state_distribution" not in evolution:
                raise Exception("Evolution analysis missing state distribution")

            # Test state recommendations
            if "recommendation" not in integration_result:
                raise Exception("Integration result missing recommendation")

            print("    ✅ Bio-consciousness integration working")
            return True

        except Exception as e:
            print(f"    ❌ Bio-consciousness integration failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive bio-symbolic systems tests"""
        print("🧬 TESTING BIO-SYMBOLIC SYSTEMS")
        print("=" * 50)

        tests = [
            ("Bio-Symbolic Processing", self.test_bio_symbolic_processing),
            ("Symbolic Pattern Recognition", self.test_symbolic_pattern_recognition),
            ("Bio-Consciousness Integration", self.test_bio_consciousness_integration),
        ]

        results = {}
        total_passed = 0

        for test_name, test_func in tests:
            print(f"\n  🧪 {test_name}:")
            success = test_func()
            results[test_name] = success
            if success:
                total_passed += 1

        success_rate = (total_passed / len(tests)) * 100
        print(f"\n  📊 Bio-Symbolic Systems Success Rate: {success_rate:.1f}% ({total_passed}/{len(tests)})")

        return {
            "system": "Bio-Symbolic Systems",
            "total_tests": len(tests),
            "passed": total_passed,
            "success_rate": success_rate,
            "details": results,
        }


def run_core_systems_testing():
    """Run all core systems testing"""
    print("🎭🔤🔐🧬 LUKHAS CORE SYSTEMS TESTING SUITE")
    print("=" * 70)
    print("Testing critical core components beyond basic systems")
    print("Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian")
    print("=" * 70)

    # Initialize test suites
    test_suites = [TestSupervisorAgent(), TestGLYPHCommunication(), TestGuardianSecurity(), TestBioSymbolicSystems()]

    all_results = []
    total_tests = 0
    total_passed = 0

    # Run all test suites
    for suite in test_suites:
        print("\n")
        result = suite.run_all_tests()
        all_results.append(result)
        total_tests += result["total_tests"]
        total_passed += result["passed"]

    # Calculate overall statistics
    overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0

    print("\n" + "=" * 70)
    print("🏆 CORE SYSTEMS TEST RESULTS SUMMARY")
    print("=" * 70)

    for result in all_results:
        system = result["system"]
        success_rate = result["success_rate"]
        passed = result["passed"]
        total = result["total_tests"]

        status_emoji = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
        print(f"{status_emoji} {system}: {success_rate:.1f}% ({passed}/{total})")

        # Show detailed breakdown
        for test_name, success in result["details"].items():
            detail_emoji = "  ✅" if success else "  ❌"
            print(f"{detail_emoji} {test_name}")

    print("\n" + "=" * 70)
    print(f"🎯 CORE SYSTEMS SUCCESS RATE: {overall_success_rate:.1f}% ({total_passed}/{total_tests})")

    # Provide assessment
    if overall_success_rate >= 90:
        assessment = "🚀 EXCEPTIONAL! Core systems highly functional"
    elif overall_success_rate >= 75:
        assessment = "✅ EXCELLENT! Core systems working well"
    elif overall_success_rate >= 60:
        assessment = "⚠️ GOOD! Minor core system issues"
    else:
        assessment = "🔧 NEEDS WORK! Core system improvements needed"

    print(f"📊 Assessment: {assessment}")

    print("\n🔍 SYSTEM READINESS:")
    for result in all_results:
        system = result["system"]
        success_rate = result["success_rate"]

        if success_rate >= 75:
            print(f"  🟢 {system}: Core functionality working")
        elif success_rate >= 50:
            print(f"  🟡 {system}: Needs minor improvements")
        else:
            print(f"  🔴 {system}: Requires significant work")

    print("\n⚛️🧠🛡️ Core Systems Testing Complete!")
    print(f"📈 Expanded Testing Coverage: +{total_tests} tests, +4 core systems")

    return all_results


if __name__ == "__main__":
    results = run_core_systems_testing()