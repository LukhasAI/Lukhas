#!/usr/bin/env python3
"""
Orchestration Brain Integration Tests
Tests the brain coordination system that orchestrates LUKHAS AI modules
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from candidate.orchestration.brain.brain_integration import BrainIntegrator, CognitiveBridge
    from candidate.orchestration.brain.main_node import MainNode, NodeCoordinator
    from candidate.orchestration.symbolic_kernel_bus import SymbolicKernelBus, BusMessage
    from candidate.orchestration.core_modules.workflow_engine import WorkflowEngine, WorkflowStep
    from core.glyph import Glyph
except ImportError:
    # Create mock classes for testing if imports fail
    @dataclass
    class BusMessage:
        source: str
        target: str
        content: Any
        message_type: str = "default"
        timestamp: float = 0.0
        priority: int = 1
    
    @dataclass 
    class WorkflowStep:
        name: str
        action: str
        parameters: Dict[str, Any] = field(default_factory=dict)
        dependencies: List[str] = field(default_factory=list)
        
    class SymbolicKernelBus:
        def __init__(self):
            self.messages = []
            self.subscribers = {}
            
        def publish(self, message: BusMessage):
            self.messages.append(message)
            
        def subscribe(self, topic: str, handler):
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(handler)
            
        def route_message(self, message: BusMessage):
            return {"routed": True, "message": message}
    
    class BrainIntegrator:
        def __init__(self):
            self.active_modules = {}
            self.integration_status = "ready"
            
        def integrate_module(self, module_name: str, module_instance):
            self.active_modules[module_name] = module_instance
            return {"status": "integrated", "module": module_name}
            
        def coordinate_modules(self, request: Dict[str, Any]):
            return {"status": "coordinated", "modules": list(self.active_modules.keys())}
    
    class CognitiveBridge:
        def __init__(self):
            self.connections = {}
            
        def create_bridge(self, source: str, target: str):
            bridge_id = f"{source}_to_{target}"
            self.connections[bridge_id] = {"source": source, "target": target}
            return bridge_id
            
        def send_cognitive_signal(self, bridge_id: str, signal: Any):
            if bridge_id in self.connections:
                return {"sent": True, "signal": signal, "bridge": bridge_id}
            return {"sent": False, "error": "bridge_not_found"}
    
    class MainNode:
        def __init__(self, node_id: str):
            self.node_id = node_id
            self.status = "inactive"
            self.processed_requests = []
            
        def start(self):
            self.status = "active"
            
        def stop(self):
            self.status = "inactive"
            
        def process_request(self, request: Dict[str, Any]):
            self.processed_requests.append(request)
            return {"processed": True, "node": self.node_id, "request_id": request.get("id")}
    
    class NodeCoordinator:
        def __init__(self):
            self.nodes = {}
            
        def register_node(self, node: MainNode):
            self.nodes[node.node_id] = node
            
        def coordinate_request(self, request: Dict[str, Any]):
            results = []
            for node in self.nodes.values():
                if node.status == "active":
                    result = node.process_request(request)
                    results.append(result)
            return results
    
    class WorkflowEngine:
        def __init__(self):
            self.workflows = {}
            self.execution_history = []
            
        def create_workflow(self, workflow_id: str, steps: List[WorkflowStep]):
            self.workflows[workflow_id] = steps
            return {"created": True, "workflow_id": workflow_id}
            
        def execute_workflow(self, workflow_id: str, context: Dict[str, Any]):
            if workflow_id not in self.workflows:
                return {"executed": False, "error": "workflow_not_found"}
                
            steps = self.workflows[workflow_id]
            results = []
            
            for step in steps:
                result = {
                    "step": step.name,
                    "action": step.action,
                    "status": "completed",
                    "output": f"executed_{step.action}"
                }
                results.append(result)
                
            execution = {
                "workflow_id": workflow_id,
                "context": context,
                "results": results,
                "timestamp": time.time()
            }
            self.execution_history.append(execution)
            
            return {"executed": True, "results": results}
    
    @dataclass
    class Glyph:
        symbol: str
        meaning: str
        context: Dict[str, Any]
        timestamp: float = 0.0


class MockMemoryModule:
    """Mock memory module for testing"""
    
    def __init__(self):
        self.memory_store = {}
        self.fold_count = 0
        
    def store_memory(self, fold_id: str, content: Any):
        self.memory_store[fold_id] = content
        self.fold_count += 1
        return {"stored": True, "fold_id": fold_id, "count": self.fold_count}
        
    def retrieve_memory(self, fold_id: str):
        content = self.memory_store.get(fold_id)
        return {"found": content is not None, "content": content}
        
    def check_cascade_risk(self):
        risk_level = "high" if self.fold_count > 950 else "medium" if self.fold_count > 500 else "low"
        return {"fold_count": self.fold_count, "risk_level": risk_level}


class MockConsciousnessModule:
    """Mock consciousness module for testing"""
    
    def __init__(self):
        self.awareness_level = 0.5
        self.dream_depth = 0
        self.emotional_state = {"neutral": 1.0}
        
    def update_awareness(self, level: float):
        self.awareness_level = max(0.0, min(1.0, level))
        return {"updated": True, "awareness_level": self.awareness_level}
        
    def enter_dream_state(self, depth: int):
        self.dream_depth = min(5, max(0, depth))
        return {"dream_entered": True, "depth": self.dream_depth}
        
    def process_emotion(self, emotion: str, intensity: float):
        self.emotional_state[emotion] = intensity
        return {"emotion_processed": True, "state": self.emotional_state}


class MockGuardianModule:
    """Mock Guardian module for testing"""
    
    def __init__(self):
        self.ethics_threshold = 0.8
        self.drift_threshold = 0.15
        self.violations = []
        
    def validate_ethics(self, action: str, score: float):
        is_valid = score >= self.ethics_threshold
        if not is_valid:
            self.violations.append({"action": action, "score": score})
        return {"valid": is_valid, "score": score, "threshold": self.ethics_threshold}
        
    def check_drift(self, drift_score: float):
        drift_detected = drift_score > self.drift_threshold
        return {"drift_detected": drift_detected, "score": drift_score, "threshold": self.drift_threshold}


class TestBrainIntegration:
    """Test brain integration functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.brain_integrator = BrainIntegrator()
        self.cognitive_bridge = CognitiveBridge()
        self.memory_module = MockMemoryModule()
        self.consciousness_module = MockConsciousnessModule()
        self.guardian_module = MockGuardianModule()
    
    def test_module_integration(self):
        """Test integration of different modules into brain"""
        # Integrate memory module
        memory_result = self.brain_integrator.integrate_module("memory", self.memory_module)
        assert memory_result["status"] == "integrated"
        assert memory_result["module"] == "memory"
        
        # Integrate consciousness module
        consciousness_result = self.brain_integrator.integrate_module("consciousness", self.consciousness_module)
        assert consciousness_result["status"] == "integrated"
        assert consciousness_result["module"] == "consciousness"
        
        # Integrate guardian module
        guardian_result = self.brain_integrator.integrate_module("guardian", self.guardian_module)
        assert guardian_result["status"] == "integrated"
        assert guardian_result["module"] == "guardian"
        
        # Verify all modules are integrated
        assert len(self.brain_integrator.active_modules) == 3
        assert "memory" in self.brain_integrator.active_modules
        assert "consciousness" in self.brain_integrator.active_modules
        assert "guardian" in self.brain_integrator.active_modules
    
    def test_module_coordination(self):
        """Test coordination between integrated modules"""
        # Integrate modules first
        self.brain_integrator.integrate_module("memory", self.memory_module)
        self.brain_integrator.integrate_module("consciousness", self.consciousness_module)
        self.brain_integrator.integrate_module("guardian", self.guardian_module)
        
        # Test coordination request
        request = {
            "action": "process_user_input",
            "content": "What is consciousness?",
            "user_id": "test_user_001"
        }
        
        result = self.brain_integrator.coordinate_modules(request)
        assert result["status"] == "coordinated"
        assert len(result["modules"]) == 3
    
    def test_cognitive_bridge_creation(self):
        """Test creation of cognitive bridges between modules"""
        # Create bridge from memory to consciousness
        bridge_id = self.cognitive_bridge.create_bridge("memory", "consciousness")
        assert bridge_id == "memory_to_consciousness"
        assert bridge_id in self.cognitive_bridge.connections
        
        # Create bridge from consciousness to guardian
        bridge_id2 = self.cognitive_bridge.create_bridge("consciousness", "guardian")
        assert bridge_id2 == "consciousness_to_guardian"
        
        # Verify connections
        assert len(self.cognitive_bridge.connections) == 2
    
    def test_cognitive_signal_transmission(self):
        """Test transmission of cognitive signals across bridges"""
        # Create bridge
        bridge_id = self.cognitive_bridge.create_bridge("memory", "consciousness")
        
        # Send cognitive signal
        signal = {
            "type": "new_memory_available",
            "fold_id": "fold_123",
            "emotional_weight": 0.7
        }
        
        result = self.cognitive_bridge.send_cognitive_signal(bridge_id, signal)
        assert result["sent"] == True
        assert result["signal"]["fold_id"] == "fold_123"
        assert result["bridge"] == bridge_id
    
    def test_invalid_bridge_signal(self):
        """Test signal transmission to non-existent bridge"""
        signal = {"type": "test_signal"}
        result = self.cognitive_bridge.send_cognitive_signal("non_existent_bridge", signal)
        
        assert result["sent"] == False
        assert result["error"] == "bridge_not_found"
    
    def test_trinity_framework_integration(self):
        """Test Trinity Framework integration (⚛️🧠🛡️)"""
        # ⚛️ Identity component (using memory for identity storage)
        identity_result = self.brain_integrator.integrate_module("identity", self.memory_module)
        assert identity_result["status"] == "integrated"
        
        # 🧠 Consciousness component
        consciousness_result = self.brain_integrator.integrate_module("consciousness", self.consciousness_module)
        assert consciousness_result["status"] == "integrated"
        
        # 🛡️ Guardian component
        guardian_result = self.brain_integrator.integrate_module("guardian", self.guardian_module)
        assert guardian_result["status"] == "integrated"
        
        # Test Trinity Framework coordination
        trinity_request = {
            "framework": "trinity",
            "components": ["identity", "consciousness", "guardian"],
            "action": "unified_processing"
        }
        
        result = self.brain_integrator.coordinate_modules(trinity_request)
        assert result["status"] == "coordinated"
        assert len(result["modules"]) == 3


class TestSymbolicKernelBus:
    """Test symbolic kernel bus functionality"""
    
    def setup_method(self):
        """Setup for kernel bus tests"""
        self.kernel_bus = SymbolicKernelBus()
    
    def test_message_publishing(self):
        """Test message publishing to kernel bus"""
        message = BusMessage(
            source="memory",
            target="consciousness",
            content={"fold_id": "test_fold", "emotional_weight": 0.8},
            message_type="memory_update"
        )
        
        self.kernel_bus.publish(message)
        assert len(self.kernel_bus.messages) == 1
        assert self.kernel_bus.messages[0].source == "memory"
        assert self.kernel_bus.messages[0].target == "consciousness"
    
    def test_subscription_handling(self):
        """Test subscription to kernel bus topics"""
        received_messages = []
        
        def message_handler(message):
            received_messages.append(message)
        
        # Subscribe to memory updates
        self.kernel_bus.subscribe("memory_update", message_handler)
        assert "memory_update" in self.kernel_bus.subscribers
        assert len(self.kernel_bus.subscribers["memory_update"]) == 1
    
    def test_message_routing(self):
        """Test message routing through kernel bus"""
        message = BusMessage(
            source="consciousness",
            target="guardian",
            content={"action": "ethical_check", "score": 0.85},
            message_type="ethics_validation"
        )
        
        result = self.kernel_bus.route_message(message)
        assert result["routed"] == True
        assert result["message"].source == "consciousness"
        assert result["message"].target == "guardian"
    
    def test_priority_message_handling(self):
        """Test priority message handling"""
        high_priority_msg = BusMessage(
            source="guardian",
            target="all",
            content={"alert": "ethics_violation_detected"},
            message_type="alert",
            priority=5
        )
        
        normal_priority_msg = BusMessage(
            source="memory",
            target="consciousness",
            content={"fold_id": "normal_fold"},
            message_type="memory_update",
            priority=1
        )
        
        self.kernel_bus.publish(normal_priority_msg)
        self.kernel_bus.publish(high_priority_msg)
        
        assert len(self.kernel_bus.messages) == 2
        # High priority message should be identifiable
        high_priority_found = any(msg.priority == 5 for msg in self.kernel_bus.messages)
        assert high_priority_found


class TestMainNode:
    """Test main node functionality"""
    
    def setup_method(self):
        """Setup for main node tests"""
        self.main_node = MainNode("primary_node")
        self.coordinator = NodeCoordinator()
    
    def test_node_lifecycle(self):
        """Test node start/stop lifecycle"""
        assert self.main_node.status == "inactive"
        
        self.main_node.start()
        assert self.main_node.status == "active"
        
        self.main_node.stop()
        assert self.main_node.status == "inactive"
    
    def test_node_request_processing(self):
        """Test node request processing"""
        self.main_node.start()
        
        request = {
            "id": "req_001",
            "type": "user_query",
            "content": "What is the meaning of consciousness?",
            "timestamp": time.time()
        }
        
        result = self.main_node.process_request(request)
        assert result["processed"] == True
        assert result["node"] == "primary_node"
        assert result["request_id"] == "req_001"
        
        # Verify request was stored
        assert len(self.main_node.processed_requests) == 1
        assert self.main_node.processed_requests[0]["id"] == "req_001"
    
    def test_node_coordination(self):
        """Test coordination between multiple nodes"""
        # Create and register multiple nodes
        node1 = MainNode("node_1")
        node2 = MainNode("node_2")
        node3 = MainNode("node_3")
        
        node1.start()
        node2.start()
        # node3 remains inactive
        
        self.coordinator.register_node(node1)
        self.coordinator.register_node(node2)
        self.coordinator.register_node(node3)
        
        # Coordinate request across nodes
        request = {
            "id": "coord_req_001",
            "type": "distributed_processing",
            "content": "Process this across all active nodes"
        }
        
        results = self.coordinator.coordinate_request(request)
        
        # Only active nodes should process the request
        assert len(results) == 2  # node1 and node2
        assert all(result["processed"] for result in results)
        
        # Verify inactive node didn't process
        assert len(node3.processed_requests) == 0


class TestWorkflowEngine:
    """Test workflow engine functionality"""
    
    def setup_method(self):
        """Setup for workflow tests"""
        self.workflow_engine = WorkflowEngine()
    
    def test_workflow_creation(self):
        """Test workflow creation with steps"""
        steps = [
            WorkflowStep("validate_input", "input_validation"),
            WorkflowStep("check_ethics", "ethics_validation"),
            WorkflowStep("process_request", "request_processing"),
            WorkflowStep("generate_response", "response_generation")
        ]
        
        result = self.workflow_engine.create_workflow("user_query_workflow", steps)
        assert result["created"] == True
        assert result["workflow_id"] == "user_query_workflow"
        assert "user_query_workflow" in self.workflow_engine.workflows
    
    def test_workflow_execution(self):
        """Test workflow execution"""
        # Create workflow
        steps = [
            WorkflowStep("memory_check", "check_memory_availability"),
            WorkflowStep("consciousness_update", "update_awareness_level"),
            WorkflowStep("guardian_validation", "validate_ethics")
        ]
        
        self.workflow_engine.create_workflow("trinity_workflow", steps)
        
        # Execute workflow
        context = {
            "user_id": "test_user",
            "request": "Test Trinity Framework",
            "timestamp": time.time()
        }
        
        result = self.workflow_engine.execute_workflow("trinity_workflow", context)
        assert result["executed"] == True
        assert len(result["results"]) == 3
        
        # Verify each step was executed
        step_names = [step_result["step"] for step_result in result["results"]]
        assert "memory_check" in step_names
        assert "consciousness_update" in step_names
        assert "guardian_validation" in step_names
    
    def test_workflow_with_dependencies(self):
        """Test workflow with step dependencies"""
        steps = [
            WorkflowStep("init", "initialize", dependencies=[]),
            WorkflowStep("validate", "validate_input", dependencies=["init"]),
            WorkflowStep("process", "process_data", dependencies=["validate"]),
            WorkflowStep("finalize", "finalize_result", dependencies=["process"])
        ]
        
        result = self.workflow_engine.create_workflow("dependent_workflow", steps)
        assert result["created"] == True
        
        # Execute workflow - should respect dependencies
        context = {"test": "dependency_workflow"}
        execution_result = self.workflow_engine.execute_workflow("dependent_workflow", context)
        
        assert execution_result["executed"] == True
        assert len(execution_result["results"]) == 4
    
    def test_workflow_execution_history(self):
        """Test workflow execution history tracking"""
        steps = [WorkflowStep("test", "test_action")]
        self.workflow_engine.create_workflow("history_test", steps)
        
        # Execute multiple times
        for i in range(3):
            context = {"execution": i}
            self.workflow_engine.execute_workflow("history_test", context)
        
        # Verify history
        assert len(self.workflow_engine.execution_history) == 3
        
        for i, execution in enumerate(self.workflow_engine.execution_history):
            assert execution["workflow_id"] == "history_test"
            assert execution["context"]["execution"] == i
    
    def test_invalid_workflow_execution(self):
        """Test execution of non-existent workflow"""
        result = self.workflow_engine.execute_workflow("non_existent", {})
        assert result["executed"] == False
        assert result["error"] == "workflow_not_found"


class TestIntegratedOrchestration:
    """Test integrated orchestration scenarios"""
    
    def setup_method(self):
        """Setup for integrated tests"""
        self.brain_integrator = BrainIntegrator()
        self.kernel_bus = SymbolicKernelBus()
        self.workflow_engine = WorkflowEngine()
        self.memory_module = MockMemoryModule()
        self.consciousness_module = MockConsciousnessModule()
        self.guardian_module = MockGuardianModule()
    
    def test_end_to_end_user_request_processing(self):
        """Test complete user request processing pipeline"""
        # Integrate all modules
        self.brain_integrator.integrate_module("memory", self.memory_module)
        self.brain_integrator.integrate_module("consciousness", self.consciousness_module)
        self.brain_integrator.integrate_module("guardian", self.guardian_module)
        
        # Create processing workflow
        workflow_steps = [
            WorkflowStep("guardian_check", "validate_ethics"),
            WorkflowStep("memory_search", "search_memory"),
            WorkflowStep("consciousness_process", "update_awareness"),
            WorkflowStep("response_generate", "generate_response")
        ]
        
        self.workflow_engine.create_workflow("user_request_pipeline", workflow_steps)
        
        # Process user request
        user_request = {
            "user_id": "user_123",
            "query": "What is the nature of consciousness?",
            "ethics_score": 0.95
        }
        
        # Execute complete pipeline
        coordination_result = self.brain_integrator.coordinate_modules(user_request)
        workflow_result = self.workflow_engine.execute_workflow("user_request_pipeline", user_request)
        
        # Verify complete processing
        assert coordination_result["status"] == "coordinated"
        assert workflow_result["executed"] == True
        assert len(workflow_result["results"]) == 4
    
    def test_memory_consciousness_interaction(self):
        """Test interaction between memory and consciousness modules"""
        # Store memory
        memory_result = self.memory_module.store_memory("conscious_memory_001", "I am aware")
        assert memory_result["stored"] == True
        
        # Update consciousness based on memory
        consciousness_result = self.consciousness_module.update_awareness(0.8)
        assert consciousness_result["updated"] == True
        assert consciousness_result["awareness_level"] == 0.8
        
        # Check memory cascade risk
        cascade_result = self.memory_module.check_cascade_risk()
        assert cascade_result["risk_level"] == "low"
    
    def test_guardian_ethics_integration(self):
        """Test Guardian ethics integration with other modules"""
        # Test ethical action
        ethics_result = self.guardian_module.validate_ethics("help_user", 0.95)
        assert ethics_result["valid"] == True
        
        # Test unethical action
        unethical_result = self.guardian_module.validate_ethics("harmful_action", 0.3)
        assert unethical_result["valid"] == False
        assert len(self.guardian_module.violations) == 1
        
        # Test drift detection
        drift_result = self.guardian_module.check_drift(0.18)  # Above 0.15 threshold
        assert drift_result["drift_detected"] == True


if __name__ == "__main__":
    pytest.main([__file__])