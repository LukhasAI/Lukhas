"""
════════════════════════════════════════════════════════════════════════════════
║ 🎤 LUKHAS AI - MESSAGE HANDLER
║ Core message processing for voice interactions
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: message_handler.py
║ Path: lukhas/core/voice_systems/message_handler.py
║ Version: 1.0.0 | Created: 2025-06-20 | Modified: 2025-07-25
║ Authors: LUKHAS AI Voice Team | Codex
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Handles asynchronous voice message processing and dispatch.
╚═══════════════════════════════════════════════════════════════════════════════
"""

import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from candidate.core.common import get_logger

logger = get_logger(__name__)


@dataclass
class VoiceMessage:
    """Represents a voice system message"""

    content: str
    priority: int
    timestamp: datetime = datetime.now()
    metadata: dict[str, Any] = None


class VoiceMessageHandler:
    """Handles voice message queues and routing"""

    def __init__(self):
        """Initialize message queues and handlers"""
        # Message queues
        self.input_queue = queue.PriorityQueue()
        self.output_queue = queue.PriorityQueue()

        # Registered handlers
        self.input_handlers = []
        self.output_handlers = []

        # Control flags
        self.is_running = False
        self._worker_thread = None

    def start(self):
        """Start message processing"""
        if not self.is_running:
            self.is_running = True
            self._worker_thread = threading.Thread(target=self._process_messages, daemon=True)
            self._worker_thread.start()
            logger.info("Voice message handler started")

    def stop(self):
        """Stop message processing"""
        self.is_running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=1.0)

    def enqueue_input(self, text: str, priority: int = 5, metadata: dict[str, Any] = None):
        """Add an input message to the queue"""
        message = VoiceMessage(text, priority, metadata=metadata or {})
        self.input_queue.put((priority, message))

    def enqueue_output(self, text: str, priority: int = 5, metadata: dict[str, Any] = None):
        """Add an output message to the queue"""
        message = VoiceMessage(text, priority, metadata=metadata or {})
        self.output_queue.put((priority, message))

    def register_input_handler(self, handler: Callable[[VoiceMessage], None]):
        """Register a handler for input messages"""
        self.input_handlers.append(handler)

    def register_output_handler(self, handler: Callable[[VoiceMessage], None]):
        """Register a handler for output messages"""
        self.output_handlers.append(handler)

    def _process_messages(self):
        """Main message processing loop"""
        while self.is_running:
            try:
                # Process input messages
                try:
                    _, message = self.input_queue.get_nowait()
                    for handler in self.input_handlers:
                        try:
                            handler(message)
                        except Exception as e:
                            logger.error(f"Input handler error: {e}")
                except queue.Empty:
                    pass

                # Process output messages
                try:
                    _, message = self.output_queue.get_nowait()
                    for handler in self.output_handlers:
                        try:
                            handler(message)
                        except Exception as e:
                            logger.error(f"Output handler error: {e}")
                except queue.Empty:
                    pass

            except Exception as e:
                logger.error(f"Message processing error: {e}")


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/voice_systems/test_message_handler.py
║   - Coverage: N/A
║   - Linting: pylint N/A
║
║ MONITORING:
║   - Metrics: message_queue_depth
║   - Logs: voice_message_events
║   - Alerts: processing_errors
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/core/voice_systems/message_handler.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=message_handler
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════════
"""
