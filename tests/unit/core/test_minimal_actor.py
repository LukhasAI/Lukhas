"""
Tests for core.minimal_actor module

Tests the Actor model implementation including:
- Actor initialization and state management
- Message receiving and handling
- Actor-to-actor communication
- Actor lifecycle management
- Custom message handling patterns
"""

from unittest.mock import patch

import pytest

from core.minimal_actor import Actor


class TestActorInitialization:
    """Test Actor initialization and basic state"""

    def test_actor_creation(self):
        """Test creating an actor with required fields"""
        actor = Actor("actor-001")

        assert actor.actor_id == "actor-001"
        assert actor.mailbox == []
        assert actor.is_active is True

    def test_actor_unique_ids(self):
        """Test that actors can have different IDs"""
        actor1 = Actor("actor-1")
        actor2 = Actor("actor-2")

        assert actor1.actor_id != actor2.actor_id
        assert actor1.actor_id == "actor-1"
        assert actor2.actor_id == "actor-2"


class TestMessageReceiving:
    """Test Actor message receiving functionality"""

    @pytest.fixture
    def actor(self):
        """Provide a test actor"""
        return Actor("test-actor")

    def test_receive_simple_message(self, actor):
        """Test receiving a simple message"""
        message = {"type": "greeting", "content": "hello"}

        result = actor.receive(message)

        assert result is not None
        assert result["status"] == "received"
        assert result["actor_id"] == "test-actor"

    def test_receive_string_message(self, actor):
        """Test receiving string message"""
        message = "test message"

        result = actor.receive(message)

        assert result["status"] == "received"

    def test_receive_complex_message(self, actor):
        """Test receiving complex nested message"""
        message = {
            "type": "task",
            "priority": "high",
            "data": {"key": "value", "nested": {"deep": "data"}},
        }

        result = actor.receive(message)

        assert result is not None

    def test_receive_logging(self, actor):
        """Test that message reception is logged"""
        with patch("core.minimal_actor.logger") as mock_logger:
            message = "test"
            actor.receive(message)

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "test-actor" in call_args
            assert "received message" in call_args


class TestMessageHandling:
    """Test Actor message handling logic"""

    def test_default_handle_message(self):
        """Test default message handling implementation"""
        actor = Actor("handler-actor")
        message = {"data": "test"}

        result = actor._handle_message(message)

        assert result["status"] == "received"
        assert result["actor_id"] == "handler-actor"

    def test_custom_message_handler(self):
        """Test custom message handler via subclass"""

        class CustomActor(Actor):
            def _handle_message(self, message):
                if isinstance(message, dict) and message.get("type") == "compute":
                    return {"result": message["value"] * 2}
                return super()._handle_message(message)

        actor = CustomActor("custom-actor")
        message = {"type": "compute", "value": 21}

        result = actor.receive(message)

        assert result["result"] == 42

    def test_message_handler_with_state(self):
        """Test message handler that maintains state"""

        class StatefulActor(Actor):
            def __init__(self, actor_id):
                super().__init__(actor_id)
                self.counter = 0

            def _handle_message(self, message):
                if message == "increment":
                    self.counter += 1
                    return {"counter": self.counter}
                return super()._handle_message(message)

        actor = StatefulActor("stateful-actor")

        result1 = actor.receive("increment")
        result2 = actor.receive("increment")
        result3 = actor.receive("increment")

        assert result1["counter"] == 1
        assert result2["counter"] == 2
        assert result3["counter"] == 3


class TestActorCommunication:
    """Test actor-to-actor communication"""

    @pytest.fixture
    def sender(self):
        """Provide sender actor"""
        return Actor("sender-001")

    @pytest.fixture
    def receiver(self):
        """Provide receiver actor"""
        return Actor("receiver-001")

    def test_send_message_to_active_actor(self, sender, receiver):
        """Test sending message from one actor to another"""
        with patch.object(receiver, "receive") as mock_receive:
            message = {"type": "test", "data": "hello"}

            sender.send(receiver, message)

            mock_receive.assert_called_once_with(message)

    def test_send_message_to_inactive_actor(self, sender, receiver):
        """Test sending message to stopped actor is rejected"""
        receiver.stop()

        with patch.object(receiver, "receive") as mock_receive:
            with patch("core.minimal_actor.logger") as mock_logger:
                message = "test"

                sender.send(receiver, message)

                mock_receive.assert_not_called()
                mock_logger.warning.assert_called_once()

    def test_bidirectional_communication(self):
        """Test two actors communicating back and forth"""

        class EchoActor(Actor):
            def _handle_message(self, message):
                if isinstance(message, dict) and message.get("echo"):
                    return {"echoed": message["echo"]}
                return super()._handle_message(message)

        actor1 = EchoActor("echo-1")
        actor2 = EchoActor("echo-2")

        with patch.object(actor2, "receive", wraps=actor2.receive) as mock_receive:
            message = {"echo": "hello"}

            actor1.send(actor2, message)

            mock_receive.assert_called_once_with(message)

    def test_chain_communication(self):
        """Test chaining messages through multiple actors"""

        class ForwardingActor(Actor):
            def __init__(self, actor_id, next_actor=None):
                super().__init__(actor_id)
                self.next_actor = next_actor
                self.received_messages = []

            def _handle_message(self, message):
                self.received_messages.append(message)
                if self.next_actor and self.next_actor.is_active:
                    self.send(self.next_actor, message)
                return super()._handle_message(message)

        actor3 = ForwardingActor("actor-3")
        actor2 = ForwardingActor("actor-2", actor3)
        actor1 = ForwardingActor("actor-1", actor2)

        message = "propagate"
        actor1.receive(message)

        assert len(actor1.received_messages) == 1
        assert len(actor2.received_messages) == 1
        assert len(actor3.received_messages) == 1


class TestActorLifecycle:
    """Test Actor lifecycle management"""

    def test_actor_starts_active(self):
        """Test actor is active upon creation"""
        actor = Actor("lifecycle-actor")

        assert actor.is_active is True

    def test_stop_actor(self):
        """Test stopping an actor"""
        actor = Actor("lifecycle-actor")

        with patch("core.minimal_actor.logger") as mock_logger:
            actor.stop()

            assert actor.is_active is False
            mock_logger.info.assert_called_once()

    def test_stopped_actor_rejects_messages(self):
        """Test stopped actor doesn't receive messages"""
        sender = Actor("sender")
        receiver = Actor("receiver")

        receiver.stop()

        with patch.object(receiver, "receive") as mock_receive:
            sender.send(receiver, "test")

            mock_receive.assert_not_called()

    def test_multiple_stop_calls(self):
        """Test calling stop multiple times is safe"""
        actor = Actor("lifecycle-actor")

        actor.stop()
        actor.stop()  # Should not raise error

        assert actor.is_active is False


class TestActorPatterns:
    """Test common actor patterns and use cases"""

    def test_request_response_pattern(self):
        """Test request-response pattern between actors"""

        class RequestActor(Actor):
            def _handle_message(self, message):
                if isinstance(message, dict) and message.get("type") == "request":
                    return {"type": "response", "data": "processed"}
                return super()._handle_message(message)

        responder = RequestActor("responder")

        message = {"type": "request", "data": "input"}
        result = responder.receive(message)

        assert result["type"] == "response"
        assert result["data"] == "processed"

    def test_broadcast_pattern(self):
        """Test broadcasting message to multiple actors"""

        class BroadcastCoordinator(Actor):
            def __init__(self, actor_id):
                super().__init__(actor_id)
                self.subscribers = []

            def subscribe(self, actor):
                self.subscribers.append(actor)

            def broadcast(self, message):
                for subscriber in self.subscribers:
                    self.send(subscriber, message)

        coordinator = BroadcastCoordinator("coordinator")
        subscribers = [Actor(f"subscriber-{i}") for i in range(3)]

        for sub in subscribers:
            coordinator.subscribe(sub)

        with (
            patch.object(subscribers[0], "receive") as mock1,
            patch.object(subscribers[1], "receive") as mock2,
            patch.object(subscribers[2], "receive") as mock3,
        ):
            coordinator.broadcast("broadcast message")

            mock1.assert_called_once()
            mock2.assert_called_once()
            mock3.assert_called_once()

    def test_mailbox_queue_pattern(self):
        """Test using mailbox for message queuing"""

        class QueueingActor(Actor):
            def queue_message(self, message):
                self.mailbox.append(message)

            def process_mailbox(self):
                results = []
                while self.mailbox:
                    message = self.mailbox.pop(0)
                    result = self.receive(message)
                    results.append(result)
                return results

        actor = QueueingActor("queuing-actor")

        # Queue multiple messages
        actor.queue_message("msg1")
        actor.queue_message("msg2")
        actor.queue_message("msg3")

        assert len(actor.mailbox) == 3

        results = actor.process_mailbox()

        assert len(results) == 3
        assert len(actor.mailbox) == 0

    def test_stateful_computation_actor(self):
        """Test actor performing stateful computations"""

        class CalculatorActor(Actor):
            def __init__(self, actor_id):
                super().__init__(actor_id)
                self.accumulator = 0

            def _handle_message(self, message):
                if isinstance(message, dict):
                    op = message.get("operation")
                    value = message.get("value", 0)

                    if op == "add":
                        self.accumulator += value
                    elif op == "subtract":
                        self.accumulator -= value
                    elif op == "multiply":
                        self.accumulator *= value
                    elif op == "reset":
                        self.accumulator = 0

                    return {"accumulator": self.accumulator}

                return super()._handle_message(message)

        calc = CalculatorActor("calculator")

        result1 = calc.receive({"operation": "add", "value": 10})
        result2 = calc.receive({"operation": "multiply", "value": 3})
        result3 = calc.receive({"operation": "subtract", "value": 5})

        assert result1["accumulator"] == 10
        assert result2["accumulator"] == 30
        assert result3["accumulator"] == 25


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_send_to_none_actor(self):
        """Test handling None as target actor"""
        actor = Actor("sender")

        with pytest.raises(AttributeError):
            actor.send(None, "message")

    def test_receive_none_message(self):
        """Test receiving None as message"""
        actor = Actor("receiver")

        result = actor.receive(None)

        assert result is not None
        assert result["status"] == "received"

    def test_empty_actor_id(self):
        """Test actor with empty string ID"""
        actor = Actor("")

        assert actor.actor_id == ""
        assert actor.is_active is True

    def test_actor_with_special_characters_id(self):
        """Test actor ID with special characters"""
        actor_id = "actor-@#$%^&*()-_+=[]{}|;:,.<>?/"
        actor = Actor(actor_id)

        assert actor.actor_id == actor_id
