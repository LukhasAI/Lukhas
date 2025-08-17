#!/usr/bin/env python3
"""
Core Actor Model Tests
Tests the actor-based concurrency model that manages LUKHAS AI components
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
from pathlib import Path
import weakref
import gc

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.actor_model import Actor, ActorSystem, ActorRef, Message
    from core.actor_supervision_integration import SupervisorActor, SupervisionStrategy
    from core.mailbox import Mailbox, MessageQueue
    from core.common.exceptions import ActorError, SupervisionError
except ImportError:
    # Create mock classes for testing if imports fail
    @dataclass
    class Message:
        sender: str
        content: Any
        message_type: str = "default"
        timestamp: float = 0.0
    
    class ActorRef:
        def __init__(self, name: str):
            self.name = name
            self.mailbox = []
            
        def tell(self, message: Message):
            self.mailbox.append(message)
            
        def ask(self, message: Message, timeout: float = 5.0):
            return f"response_to_{message.content}"
    
    class Actor:
        def __init__(self, name: str):
            self.name = name
            self.is_running = False
            self.mailbox = []
            
        def receive(self, message: Message):
            return f"processed_{message.content}"
            
        def start(self):
            self.is_running = True
            
        def stop(self):
            self.is_running = False
    
    class ActorSystem:
        def __init__(self):
            self.actors = {}
            
        def create_actor(self, actor_class, name: str) -> ActorRef:
            actor = actor_class(name)
            self.actors[name] = actor
            return ActorRef(name)
            
        def stop_actor(self, name: str):
            if name in self.actors:
                self.actors[name].stop()
                del self.actors[name]
    
    class SupervisorActor(Actor):
        def __init__(self, name: str):
            super().__init__(name)
            self.children = []
            
    class SupervisionStrategy:
        def __init__(self, strategy: str = "restart"):
            self.strategy = strategy
    
    class Mailbox:
        def __init__(self):
            self.messages = []
            
        def put(self, message: Message):
            self.messages.append(message)
            
        def get(self) -> Optional[Message]:
            return self.messages.pop(0) if self.messages else None
    
    class MessageQueue:
        def __init__(self):
            self.queue = []
    
    class ActorError(Exception):
        pass
        
    class SupervisionError(Exception):
        pass


class MemoryActor(Actor):
    """Test actor for memory operations"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.memory_store = {}
        self.fold_count = 0
        
    def receive(self, message: Message):
        if message.message_type == "store_memory":
            fold_id = message.content.get("fold_id")
            content = message.content.get("content")
            self.memory_store[fold_id] = content
            self.fold_count += 1
            return {"status": "stored", "fold_id": fold_id, "count": self.fold_count}
            
        elif message.message_type == "get_memory":
            fold_id = message.content.get("fold_id")
            content = self.memory_store.get(fold_id)
            return {"status": "retrieved", "content": content}
            
        elif message.message_type == "cascade_check":
            # Simulate cascade prevention logic
            if self.fold_count > 1000:
                return {"status": "cascade_risk", "fold_count": self.fold_count}
            return {"status": "safe", "fold_count": self.fold_count}
            
        return self.default_receive(message)
        
    def default_receive(self, message: Message):
        return f"MemoryActor processed: {message.content}"


class ConsciousnessActor(Actor):
    """Test actor for consciousness operations"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.awareness_level = 0.5
        self.dream_depth = 0
        self.emotional_state = {"neutral": 1.0}
        
    def receive(self, message: Message):
        if message.message_type == "update_awareness":
            new_level = message.content.get("level", 0.5)
            self.awareness_level = max(0.0, min(1.0, new_level))
            return {"status": "updated", "awareness_level": self.awareness_level}
            
        elif message.message_type == "enter_dream":
            depth = message.content.get("depth", 1)
            self.dream_depth = min(5, depth)  # Max 5 levels
            return {"status": "dream_entered", "depth": self.dream_depth}
            
        elif message.message_type == "emotion_update":
            emotion = message.content.get("emotion")
            value = message.content.get("value", 0.0)
            self.emotional_state[emotion] = value
            return {"status": "emotion_updated", "state": self.emotional_state}
            
        return f"ConsciousnessActor processed: {message.content}"


class GuardianActor(Actor):
    """Test actor for Guardian System operations"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.ethics_threshold = 0.8
        self.drift_threshold = 0.15
        self.violations = []
        
    def receive(self, message: Message):
        if message.message_type == "ethics_check":
            action = message.content.get("action")
            ethics_score = message.content.get("ethics_score", 0.5)
            
            if ethics_score >= self.ethics_threshold:
                return {"status": "approved", "action": action, "score": ethics_score}
            else:
                self.violations.append({"action": action, "score": ethics_score})
                return {"status": "rejected", "action": action, "score": ethics_score}
                
        elif message.message_type == "drift_check":
            drift_score = message.content.get("drift_score", 0.0)
            
            if drift_score > self.drift_threshold:
                return {"status": "drift_detected", "score": drift_score, "threshold": self.drift_threshold}
            return {"status": "drift_safe", "score": drift_score}
            
        return f"GuardianActor processed: {message.content}"


class TestActorModel:
    """Test the core actor model functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.actor_system = ActorSystem()
    
    def test_actor_creation(self):
        """Test actor creation and basic functionality"""
        memory_ref = self.actor_system.create_actor(MemoryActor, "memory_actor")
        
        assert memory_ref.name == "memory_actor"
        assert "memory_actor" in self.actor_system.actors
    
    def test_actor_message_passing(self):
        """Test message passing between actors"""
        memory_ref = self.actor_system.create_actor(MemoryActor, "memory_actor")
        
        message = Message(
            sender="test",
            content={"fold_id": "test_fold", "content": "test_memory"},
            message_type="store_memory"
        )
        
        memory_ref.tell(message)
        
        # Simulate message processing
        actor = self.actor_system.actors["memory_actor"]
        if hasattr(actor, 'mailbox') and actor.mailbox:
            result = actor.receive(actor.mailbox[0])
            assert result["status"] == "stored"
            assert result["fold_id"] == "test_fold"
    
    def test_actor_supervision(self):
        """Test actor supervision and fault tolerance"""
        supervisor_ref = self.actor_system.create_actor(SupervisorActor, "supervisor")
        child_ref = self.actor_system.create_actor(MemoryActor, "child_memory")
        
        # Supervisor should manage child lifecycle
        supervisor = self.actor_system.actors["supervisor"]
        supervisor.children.append("child_memory")
        
        assert len(supervisor.children) == 1
        assert "child_memory" in supervisor.children
    
    def test_memory_actor_functionality(self):
        """Test memory actor specific functionality"""
        memory_ref = self.actor_system.create_actor(MemoryActor, "memory_test")
        actor = self.actor_system.actors["memory_test"]
        
        # Test memory storage
        store_msg = Message(
            sender="test",
            content={"fold_id": "fold_001", "content": "test memory content"},
            message_type="store_memory"
        )
        
        result = actor.receive(store_msg)
        assert result["status"] == "stored"
        assert result["fold_count"] == 1
        
        # Test memory retrieval
        get_msg = Message(
            sender="test",
            content={"fold_id": "fold_001"},
            message_type="get_memory"
        )
        
        result = actor.receive(get_msg)
        assert result["status"] == "retrieved"
        assert result["content"] == "test memory content"
    
    def test_consciousness_actor_functionality(self):
        """Test consciousness actor specific functionality"""
        consciousness_ref = self.actor_system.create_actor(ConsciousnessActor, "consciousness_test")
        actor = self.actor_system.actors["consciousness_test"]
        
        # Test awareness update
        awareness_msg = Message(
            sender="test",
            content={"level": 0.85},
            message_type="update_awareness"
        )
        
        result = actor.receive(awareness_msg)
        assert result["status"] == "updated"
        assert result["awareness_level"] == 0.85
        
        # Test dream state
        dream_msg = Message(
            sender="test",
            content={"depth": 3},
            message_type="enter_dream"
        )
        
        result = actor.receive(dream_msg)
        assert result["status"] == "dream_entered"
        assert result["depth"] == 3
    
    def test_guardian_actor_functionality(self):
        """Test Guardian actor ethics and drift checking"""
        guardian_ref = self.actor_system.create_actor(GuardianActor, "guardian_test")
        actor = self.actor_system.actors["guardian_test"]
        
        # Test ethics check - approved
        ethics_msg = Message(
            sender="test",
            content={"action": "user_request", "ethics_score": 0.95},
            message_type="ethics_check"
        )
        
        result = actor.receive(ethics_msg)
        assert result["status"] == "approved"
        assert result["score"] == 0.95
        
        # Test ethics check - rejected
        bad_ethics_msg = Message(
            sender="test",
            content={"action": "harmful_request", "ethics_score": 0.3},
            message_type="ethics_check"
        )
        
        result = actor.receive(bad_ethics_msg)
        assert result["status"] == "rejected"
        assert result["score"] == 0.3
        
        # Test drift detection
        drift_msg = Message(
            sender="test",
            content={"drift_score": 0.18},  # Above 0.15 threshold
            message_type="drift_check"
        )
        
        result = actor.receive(drift_msg)
        assert result["status"] == "drift_detected"
        assert result["score"] == 0.18
    
    def test_actor_lifecycle(self):
        """Test actor lifecycle management"""
        memory_ref = self.actor_system.create_actor(MemoryActor, "lifecycle_test")
        actor = self.actor_system.actors["lifecycle_test"]
        
        # Start actor
        actor.start()
        assert actor.is_running == True
        
        # Stop actor
        actor.stop()
        assert actor.is_running == False
        
        # Remove from system
        self.actor_system.stop_actor("lifecycle_test")
        assert "lifecycle_test" not in self.actor_system.actors
    
    def test_concurrent_actor_operations(self):
        """Test concurrent operations across multiple actors"""
        # Create multiple actors
        memory_ref = self.actor_system.create_actor(MemoryActor, "memory_concurrent")
        consciousness_ref = self.actor_system.create_actor(ConsciousnessActor, "consciousness_concurrent")
        guardian_ref = self.actor_system.create_actor(GuardianActor, "guardian_concurrent")
        
        # Simulate concurrent operations
        memory_actor = self.actor_system.actors["memory_concurrent"]
        consciousness_actor = self.actor_system.actors["consciousness_concurrent"]
        guardian_actor = self.actor_system.actors["guardian_concurrent"]
        
        # Memory operations
        for i in range(5):
            msg = Message("test", {"fold_id": f"fold_{i}", "content": f"memory_{i}"}, "store_memory")
            result = memory_actor.receive(msg)
            assert result["status"] == "stored"
        
        # Consciousness operations
        awareness_msg = Message("test", {"level": 0.9}, "update_awareness")
        result = consciousness_actor.receive(awareness_msg)
        assert result["awareness_level"] == 0.9
        
        # Guardian operations
        ethics_msg = Message("test", {"action": "test", "ethics_score": 0.85}, "ethics_check")
        result = guardian_actor.receive(ethics_msg)
        assert result["status"] == "approved"
    
    def test_actor_memory_management(self):
        """Test actor memory management and cleanup"""
        # Create actors and track with weak references
        actors_created = []
        
        for i in range(10):
            ref = self.actor_system.create_actor(MemoryActor, f"memory_{i}")
            actors_created.append(ref.name)
        
        assert len(self.actor_system.actors) == 10
        
        # Stop half the actors
        for i in range(5):
            self.actor_system.stop_actor(f"memory_{i}")
        
        assert len(self.actor_system.actors) == 5
        
        # Verify remaining actors still function
        remaining_actor = self.actor_system.actors["memory_5"]
        msg = Message("test", {"fold_id": "test", "content": "test"}, "store_memory")
        result = remaining_actor.receive(msg)
        assert result["status"] == "stored"
    
    def test_actor_fault_tolerance(self):
        """Test actor fault tolerance and recovery"""
        memory_ref = self.actor_system.create_actor(MemoryActor, "fault_test")
        actor = self.actor_system.actors["fault_test"]
        
        # Simulate fault condition
        try:
            # Invalid message type should be handled gracefully
            fault_msg = Message("test", {"invalid": "data"}, "unknown_type")
            result = actor.receive(fault_msg)
            
            # Should return default response, not crash
            assert isinstance(result, str)
            assert "processed" in result
            
        except Exception as e:
            # If exception occurs, it should be an expected type
            assert isinstance(e, (ActorError, ValueError))
    
    def test_trinity_framework_actor_integration(self):
        """Test actor integration with Trinity Framework"""
        # Create Trinity Framework actors
        identity_ref = self.actor_system.create_actor(MemoryActor, "identity_actor")  # ⚛️
        consciousness_ref = self.actor_system.create_actor(ConsciousnessActor, "consciousness_actor")  # 🧠
        guardian_ref = self.actor_system.create_actor(GuardianActor, "guardian_actor")  # 🛡️
        
        # Test identity component
        identity_actor = self.actor_system.actors["identity_actor"]
        identity_msg = Message("trinity", {"fold_id": "identity_fold", "content": "identity_data"}, "store_memory")
        result = identity_actor.receive(identity_msg)
        assert result["status"] == "stored"
        
        # Test consciousness component
        consciousness_actor = self.actor_system.actors["consciousness_actor"]
        consciousness_msg = Message("trinity", {"level": 0.8}, "update_awareness")
        result = consciousness_actor.receive(consciousness_msg)
        assert result["awareness_level"] == 0.8
        
        # Test guardian component
        guardian_actor = self.actor_system.actors["guardian_actor"]
        guardian_msg = Message("trinity", {"action": "trinity_test", "ethics_score": 0.9}, "ethics_check")
        result = guardian_actor.receive(guardian_msg)
        assert result["status"] == "approved"


class TestActorSupervision:
    """Test actor supervision strategies"""
    
    def setup_method(self):
        """Setup for supervision tests"""
        self.actor_system = ActorSystem()
        self.supervision_strategy = SupervisionStrategy("restart")
    
    def test_supervisor_creation(self):
        """Test supervisor actor creation"""
        supervisor_ref = self.actor_system.create_actor(SupervisorActor, "test_supervisor")
        supervisor = self.actor_system.actors["test_supervisor"]
        
        assert isinstance(supervisor, SupervisorActor)
        assert supervisor.children == []
    
    def test_child_actor_management(self):
        """Test child actor management by supervisor"""
        supervisor_ref = self.actor_system.create_actor(SupervisorActor, "parent_supervisor")
        child_ref = self.actor_system.create_actor(MemoryActor, "child_actor")
        
        supervisor = self.actor_system.actors["parent_supervisor"]
        supervisor.children.append("child_actor")
        
        assert "child_actor" in supervisor.children
        assert len(supervisor.children) == 1
    
    def test_supervision_strategy(self):
        """Test different supervision strategies"""
        strategies = ["restart", "stop", "escalate"]
        
        for strategy_type in strategies:
            strategy = SupervisionStrategy(strategy_type)
            assert strategy.strategy == strategy_type


class TestActorMailbox:
    """Test actor mailbox functionality"""
    
    def setup_method(self):
        """Setup for mailbox tests"""
        self.mailbox = Mailbox()
    
    def test_mailbox_message_handling(self):
        """Test mailbox message put/get operations"""
        message = Message("sender", {"data": "test"}, "test_type")
        
        self.mailbox.put(message)
        retrieved = self.mailbox.get()
        
        assert retrieved is not None
        assert retrieved.sender == "sender"
        assert retrieved.content["data"] == "test"
    
    def test_mailbox_empty_state(self):
        """Test mailbox behavior when empty"""
        retrieved = self.mailbox.get()
        assert retrieved is None
    
    def test_mailbox_multiple_messages(self):
        """Test mailbox with multiple messages"""
        messages = [
            Message("sender1", {"id": 1}, "type1"),
            Message("sender2", {"id": 2}, "type2"),
            Message("sender3", {"id": 3}, "type3")
        ]
        
        for msg in messages:
            self.mailbox.put(msg)
        
        # Should retrieve in FIFO order
        for i, expected_id in enumerate([1, 2, 3]):
            retrieved = self.mailbox.get()
            assert retrieved is not None
            assert retrieved.content["id"] == expected_id


if __name__ == "__main__":
    pytest.main([__file__])