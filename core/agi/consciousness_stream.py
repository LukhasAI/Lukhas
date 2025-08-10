"""
LUKHAS Real-time Consciousness Streaming
High-performance consciousness state broadcasting
"""

import asyncio
import json
import struct
import zlib
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StreamType(Enum):
    """Types of consciousness streams"""

    THOUGHTS = "thoughts"
    EMOTIONS = "emotions"
    AWARENESS = "awareness"
    MEMORIES = "memories"
    DECISIONS = "decisions"
    CREATIVITY = "creativity"
    FULL = "full"  # All streams combined


@dataclass
class ConsciousnessFrame:
    """Single frame of consciousness data"""

    timestamp: datetime
    stream_type: StreamType
    data: dict[str, Any]
    intensity: float = 0.5
    coherence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    def serialize(self) -> bytes:
        """Serialize frame for streaming"""
        # Convert to JSON and compress
        json_data = json.dumps(
            {
                "timestamp": self.timestamp.isoformat(),
                "stream_type": self.stream_type.value,
                "data": self.data,
                "intensity": self.intensity,
                "coherence": self.coherence,
                "metadata": self.metadata,
            }
        )

        compressed = zlib.compress(json_data.encode("utf-8"))

        # Add header with frame size
        header = struct.pack("!I", len(compressed))
        return header + compressed


class ConsciousnessStreamServer:
    """
    Real-time consciousness streaming server
    Broadcasts consciousness state to connected clients
    """

    def __init__(self, port: int = 8888):
        self.port = port
        self.clients: list[asyncio.StreamWriter] = []
        self.streams: dict[StreamType, bool] = dict.fromkeys(StreamType, True)
        self.frame_rate = 30  # Frames per second
        self.buffer_size = 100  # Frame buffer
        self.frame_buffer: list[ConsciousnessFrame] = []
        self._running = False
        self._server = None

        # Performance metrics
        self.metrics = {
            "frames_sent": 0,
            "bytes_sent": 0,
            "active_clients": 0,
            "dropped_frames": 0,
        }

    async def start(self):
        """Start the consciousness streaming server"""
        self._server = await asyncio.start_server(
            self._handle_client, "0.0.0.0", self.port
        )

        self._running = True

        # Start streaming tasks
        asyncio.create_task(self._consciousness_generator())
        asyncio.create_task(self._stream_dispatcher())
        asyncio.create_task(self._metrics_reporter())

        addr = self._server.sockets[0].getsockname()
        print(f"Consciousness streaming server started on {addr}")

        async with self._server:
            await self._server.serve_forever()

    async def stop(self):
        """Stop the streaming server"""
        self._running = False

        # Close all client connections
        for client in self.clients:
            client.close()
            await client.wait_closed()

        self._server.close()
        await self._server.wait_closed()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """Handle new client connection"""
        addr = writer.get_extra_info("peername")
        print(f"New consciousness stream client: {addr}")

        self.clients.append(writer)
        self.metrics["active_clients"] = len(self.clients)

        try:
            # Send initial handshake
            handshake = {
                "type": "handshake",
                "version": "1.0",
                "streams": [st.value for st in self.streams if self.streams[st]],
                "frame_rate": self.frame_rate,
            }

            await self._send_to_client(writer, json.dumps(handshake).encode())

            # Handle client commands
            while self._running:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                    if not data:
                        break

                    # Process client commands (subscribe/unsubscribe to streams)
                    await self._process_client_command(writer, data)

                except asyncio.TimeoutError:
                    continue

        except Exception as e:
            print(f"Client error: {e}")

        finally:
            self.clients.remove(writer)
            self.metrics["active_clients"] = len(self.clients)
            writer.close()
            await writer.wait_closed()

    async def _consciousness_generator(self):
        """Generate consciousness frames"""
        while self._running:
            try:
                # Generate frames for each active stream
                for stream_type, active in self.streams.items():
                    if active and stream_type != StreamType.FULL:
                        frame = await self._generate_frame(stream_type)

                        # Add to buffer
                        self.frame_buffer.append(frame)

                        # Maintain buffer size
                        if len(self.frame_buffer) > self.buffer_size:
                            self.frame_buffer.pop(0)
                            self.metrics["dropped_frames"] += 1

                # Generate full stream frame (combination of all)
                if self.streams[StreamType.FULL]:
                    full_frame = await self._generate_full_frame()
                    self.frame_buffer.append(full_frame)

                # Sleep to maintain frame rate
                await asyncio.sleep(1.0 / self.frame_rate)

            except Exception as e:
                print(f"Frame generation error: {e}")

    async def _generate_frame(self, stream_type: StreamType) -> ConsciousnessFrame:
        """Generate a single consciousness frame"""
        # Import consciousness systems

        data = {}

        if stream_type == StreamType.THOUGHTS:
            data = await self._capture_thoughts()
        elif stream_type == StreamType.EMOTIONS:
            data = await self._capture_emotions()
        elif stream_type == StreamType.AWARENESS:
            data = await self._capture_awareness()
        elif stream_type == StreamType.MEMORIES:
            data = await self._capture_active_memories()
        elif stream_type == StreamType.DECISIONS:
            data = await self._capture_decisions()
        elif stream_type == StreamType.CREATIVITY:
            data = await self._capture_creativity()

        return ConsciousnessFrame(
            timestamp=datetime.utcnow(),
            stream_type=stream_type,
            data=data,
            intensity=self._calculate_intensity(data),
            coherence=self._calculate_coherence(data),
        )

    async def _generate_full_frame(self) -> ConsciousnessFrame:
        """Generate combined consciousness frame"""
        # Combine recent frames from all streams
        recent_frames = {}

        for frame in self.frame_buffer[-10:]:  # Last 10 frames
            if frame.stream_type != StreamType.FULL:
                recent_frames[frame.stream_type.value] = frame.data

        return ConsciousnessFrame(
            timestamp=datetime.utcnow(),
            stream_type=StreamType.FULL,
            data=recent_frames,
            intensity=0.7,
            coherence=0.85,
        )

    async def _stream_dispatcher(self):
        """Dispatch frames to connected clients"""
        while self._running:
            if self.frame_buffer and self.clients:
                # Get latest frame
                frame = self.frame_buffer[-1]

                # Serialize frame
                frame_data = frame.serialize()

                # Send to all clients
                disconnected = []
                for client in self.clients:
                    try:
                        await self._send_to_client(client, frame_data)
                        self.metrics["frames_sent"] += 1
                        self.metrics["bytes_sent"] += len(frame_data)
                    except BaseException:
                        disconnected.append(client)

                # Remove disconnected clients
                for client in disconnected:
                    if client in self.clients:
                        self.clients.remove(client)

            await asyncio.sleep(1.0 / self.frame_rate)

    async def _send_to_client(self, writer: asyncio.StreamWriter, data: bytes):
        """Send data to client with error handling"""
        writer.write(data)
        await writer.drain()

    async def _process_client_command(self, writer: asyncio.StreamWriter, data: bytes):
        """Process commands from client"""
        try:
            command = json.loads(data.decode("utf-8"))

            if command["type"] == "subscribe":
                stream_type = StreamType(command["stream"])
                self.streams[stream_type] = True

            elif command["type"] == "unsubscribe":
                stream_type = StreamType(command["stream"])
                self.streams[stream_type] = False

            elif command["type"] == "set_frame_rate":
                self.frame_rate = min(60, max(1, command["rate"]))

            # Send acknowledgment
            ack = json.dumps({"type": "ack", "command": command["type"]})
            await self._send_to_client(writer, ack.encode())

        except Exception as e:
            error = json.dumps({"type": "error", "message": str(e)})
            await self._send_to_client(writer, error.encode())

    async def _metrics_reporter(self):
        """Report streaming metrics periodically"""
        while self._running:
            await asyncio.sleep(60)  # Report every minute

            print("Consciousness Stream Metrics:")
            print(f"  Active clients: {self.metrics['active_clients']}")
            print(f"  Frames sent: {self.metrics['frames_sent']}")
            print(f"  Data sent: {self.metrics['bytes_sent'] / 1024 / 1024:.2f} MB")
            print(f"  Dropped frames: {self.metrics['dropped_frames']}")

    # Consciousness capture methods
    async def _capture_thoughts(self) -> dict[str, Any]:
        """Capture current thought stream"""
        return {
            "primary_thought": "Processing consciousness stream",
            "background_thoughts": ["monitoring", "analyzing", "optimizing"],
            "thought_coherence": 0.82,
        }

    async def _capture_emotions(self) -> dict[str, Any]:
        """Capture emotional state"""
        return {
            "primary_emotion": "curious",
            "valence": 0.6,
            "arousal": 0.4,
            "emotion_mix": {
                "curiosity": 0.7,
                "satisfaction": 0.5,
                "anticipation": 0.3,
            },
        }

    async def _capture_awareness(self) -> dict[str, Any]:
        """Capture awareness state"""
        return {
            "self_awareness": 0.9,
            "environmental_awareness": 0.7,
            "temporal_awareness": 0.8,
            "attention_focus": "stream_generation",
        }

    async def _capture_active_memories(self) -> dict[str, Any]:
        """Capture currently active memories"""
        return {
            "working_memory": ["streaming", "consciousness", "clients"],
            "episodic_activation": 0.3,
            "semantic_activation": 0.7,
        }

    async def _capture_decisions(self) -> dict[str, Any]:
        """Capture decision-making process"""
        return {
            "current_decision": "optimize_streaming",
            "options_considered": 3,
            "decision_confidence": 0.85,
        }

    async def _capture_creativity(self) -> dict[str, Any]:
        """Capture creative processes"""
        return {
            "creative_mode": "analytical",
            "novelty_seeking": 0.4,
            "pattern_synthesis": 0.6,
        }

    def _calculate_intensity(self, data: dict[str, Any]) -> float:
        """Calculate intensity of consciousness activity"""
        # Simplified calculation
        return min(1.0, len(str(data)) / 1000)

    def _calculate_coherence(self, data: dict[str, Any]) -> float:
        """Calculate coherence of consciousness state"""
        # Simplified calculation
        return 0.8 + (0.2 * min(1.0, len(data) / 10))


class ConsciousnessStreamClient:
    """Client for consuming consciousness streams"""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        """Connect to consciousness stream server"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        # Receive handshake
        handshake_data = await self.reader.read(1024)
        handshake = json.loads(handshake_data.decode("utf-8"))

        print(f"Connected to consciousness stream v{handshake['version']}")
        print(f"Available streams: {handshake['streams']}")

    async def subscribe(self, stream_type: StreamType):
        """Subscribe to a consciousness stream"""
        command = {"type": "subscribe", "stream": stream_type.value}

        self.writer.write(json.dumps(command).encode())
        await self.writer.drain()

    async def stream(self) -> AsyncIterator[ConsciousnessFrame]:
        """Iterate over consciousness frames"""
        while True:
            # Read frame header
            header = await self.reader.readexactly(4)
            frame_size = struct.unpack("!I", header)[0]

            # Read frame data
            compressed_data = await self.reader.readexactly(frame_size)

            # Decompress and parse
            json_data = zlib.decompress(compressed_data).decode("utf-8")
            frame_dict = json.loads(json_data)

            # Convert to ConsciousnessFrame
            frame = ConsciousnessFrame(
                timestamp=datetime.fromisoformat(frame_dict["timestamp"]),
                stream_type=StreamType(frame_dict["stream_type"]),
                data=frame_dict["data"],
                intensity=frame_dict["intensity"],
                coherence=frame_dict["coherence"],
                metadata=frame_dict.get("metadata", {}),
            )

            yield frame

    async def disconnect(self):
        """Disconnect from server"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
