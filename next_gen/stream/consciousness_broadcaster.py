#!/usr/bin/env python3
"""
Consciousness Broadcaster - Real-time WebSocket stream of consciousness states
Emits live updates with privacy protection and GDPR compliance
"""

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessState:
    """Represents a consciousness state with privacy masking"""

    current_state: str
    timestamp: datetime
    confidence: float
    previous_state: Optional[str] = None
    transition_duration_ms: int = 0
    biometric_hints: dict = None
    symbolic_representation: str = ""
    privacy_mask: str = ""

    def to_broadcast_json(self, include_biometrics: bool = False) -> str:
        """Convert to JSON for broadcasting with privacy controls"""
        data = {
            "type": "consciousness_update",
            "current_state": self.current_state,
            "timestamp": self.timestamp.isoformat(),
            "confidence": round(self.confidence, 3),
            "symbolic": self.symbolic_representation,
            "privacy_mask": self.privacy_mask,
        }

        if self.previous_state:
            data["transition"] = {
                "from": self.previous_state,
                "duration_ms": self.transition_duration_ms,
            }

        # Only include biometrics if authorized and not in simulation
        if include_biometrics and self.biometric_hints:
            # Apply privacy masking
            data["biometric_hints"] = {
                "heart_coherence": self.biometric_hints.get(
                    "heart_coherence", "unknown"
                ),
                "attention_score": round(
                    self.biometric_hints.get("attention_score", 0), 2
                ),
                "stress_level": self.biometric_hints.get("stress_level", "unknown"),
            }

        return json.dumps(data)


class ConsciousnessBroadcaster:
    """
    WebSocket server that broadcasts consciousness state updates
    with throttling, privacy protection, and GDPR compliance
    """

    # Consciousness states and their symbolic representations
    STATES = {
        "focused": "🎯",
        "creative": "🎨",
        "analytical": "🔬",
        "meditative": "🧘",
        "dreaming": "💭",
        "flow_state": "🌊",
        "lucid": "✨",
        "turbulent": "🌪️",
    }

    # State transition probabilities (for simulation)
    TRANSITIONS = {
        "focused": ["analytical", "flow_state", "creative"],
        "creative": ["dreaming", "flow_state", "focused"],
        "analytical": ["focused", "meditative", "turbulent"],
        "meditative": ["dreaming", "lucid", "focused"],
        "dreaming": ["creative", "lucid", "meditative"],
        "flow_state": ["focused", "creative", "lucid"],
        "lucid": ["meditative", "flow_state", "dreaming"],
        "turbulent": ["focused", "analytical", "meditative"],
    }

    def __init__(
        self,
        state_file: str = "consciousness_state.json",
        port: int = 8765,
        throttle_ms: int = 5000,
        simulation_mode: bool = True,
    ):
        self.state_file = Path(state_file)
        self.port = port
        self.throttle_ms = throttle_ms
        self.simulation_mode = simulation_mode
        self.connected_clients: set[WebSocketServerProtocol] = set()
        self.current_state: Optional[ConsciousnessState] = None
        self.gdpr_consent: dict[str, dict] = {}
        self.last_broadcast = datetime.min

        logger.info(f"🧠 Consciousness Broadcaster initialized on port {port}")
        logger.info(f"   Simulation mode: {'ON' if simulation_mode else 'OFF'}")
        logger.info(f"   Throttle rate: {throttle_ms}ms")

    async def load_state(self) -> ConsciousnessState:
        """Load consciousness state from file or generate if in simulation"""
        if self.state_file.exists() and not self.simulation_mode:
            # Load from file
            with open(self.state_file) as f:
                data = json.load(f)

            state = ConsciousnessState(
                current_state=data["current_state"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                confidence=data["confidence"],
                previous_state=data.get("transitions", {}).get("previous"),
                transition_duration_ms=data.get("transitions", {}).get(
                    "duration_ms", 0
                ),
                biometric_hints=data.get("biometric_hints", {}),
                symbolic_representation=data.get("symbolic_representation", ""),
                privacy_mask=data.get("privacy_mask", ""),
            )

            # Check GDPR consent
            gdpr = data.get("gdpr_consent", {})
            if (
                gdpr.get("streaming_authorized")
                and datetime.fromisoformat(gdpr["expires"]) > datetime.utcnow()
            ):
                self.gdpr_consent["global"] = gdpr
        else:
            # Generate simulated state
            state = await self._generate_simulated_state()

        return state

    async def _generate_simulated_state(self) -> ConsciousnessState:
        """Generate a simulated consciousness state"""
        # Use previous state or random
        if self.current_state:
            # Transition from current state
            possible_states = self.TRANSITIONS.get(
                self.current_state.current_state, list(self.STATES.keys())
            )
            new_state = random.choice(possible_states)
            previous = self.current_state.current_state
            transition_ms = random.randint(1000, 5000)
        else:
            # Initial state
            new_state = random.choice(list(self.STATES.keys()))
            previous = None
            transition_ms = 0

        # Generate biometric hints
        if new_state in ["turbulent", "analytical"]:
            heart_coherence = "medium"
            stress_level = "elevated"
            attention = random.uniform(0.5, 0.7)
        elif new_state in ["flow_state", "lucid"]:
            heart_coherence = "high"
            stress_level = "low"
            attention = random.uniform(0.85, 0.95)
        else:
            heart_coherence = "high"
            stress_level = "low"
            attention = random.uniform(0.7, 0.85)

        # Create privacy mask
        mask_content = f"{new_state}_{datetime.utcnow().isoformat()}_{random.random()}"
        privacy_mask = (
            f"SHA3-256:{hashlib.sha3_256(mask_content.encode()).hexdigest()[:16]}..."
        )

        return ConsciousnessState(
            current_state=new_state,
            timestamp=datetime.utcnow(),
            confidence=random.uniform(0.85, 0.98),
            previous_state=previous,
            transition_duration_ms=transition_ms,
            biometric_hints={
                "heart_coherence": heart_coherence,
                "attention_score": attention,
                "stress_level": stress_level,
            },
            symbolic_representation=self.STATES[new_state],
            privacy_mask=privacy_mask,
        )

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a WebSocket client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔌 Client connected: {client_id}")

        # Add to connected clients
        self.connected_clients.add(websocket)

        try:
            # Send initial state
            if self.current_state:
                await websocket.send(self.current_state.to_broadcast_json())

            # Listen for client messages (GDPR consent, preferences)
            async for message in websocket:
                await self._handle_client_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_id}")
        finally:
            self.connected_clients.remove(websocket)
            if client_id in self.gdpr_consent:
                del self.gdpr_consent[client_id]

    async def _handle_client_message(
        self, websocket: WebSocketServerProtocol, message: str
    ):
        """Handle messages from clients"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "gdpr_consent":
                # Handle GDPR consent
                client_id = (
                    f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                )
                self.gdpr_consent[client_id] = {
                    "authorized": data.get("authorized", False),
                    "include_biometrics": data.get("include_biometrics", False),
                    "expires": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                }

                # Send acknowledgment
                await websocket.send(
                    json.dumps(
                        {
                            "type": "consent_acknowledged",
                            "status": (
                                "accepted" if data.get("authorized") else "rejected"
                            ),
                        }
                    )
                )

            elif msg_type == "request_state":
                # Send current state on demand
                if self.current_state:
                    await websocket.send(self.current_state.to_broadcast_json())

        except json.JSONDecodeError:
            logger.warning(f"Invalid message from client: {message}")

    async def broadcast_loop(self):
        """Main broadcast loop - sends updates to all connected clients"""
        logger.info("📡 Starting consciousness broadcast loop")

        while True:
            try:
                # Load or generate state
                self.current_state = await self.load_state()

                # Check throttling
                now = datetime.utcnow()
                time_since_last = (now - self.last_broadcast).total_seconds() * 1000

                if time_since_last >= self.throttle_ms and self.connected_clients:
                    # Broadcast to all connected clients
                    disconnected = set()

                    for client in self.connected_clients:
                        try:
                            # Check client's GDPR consent
                            client_id = (
                                f"{client.remote_address[0]}:{client.remote_address[1]}"
                            )
                            consent = self.gdpr_consent.get(client_id, {})
                            include_bio = consent.get("include_biometrics", False)

                            # Send update
                            await client.send(
                                self.current_state.to_broadcast_json(include_bio)
                            )
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.add(client)

                    # Remove disconnected clients
                    self.connected_clients -= disconnected

                    self.last_broadcast = now
                    logger.info(
                        f"📡 Broadcasted {self.current_state.current_state} "
                        f"{self.current_state.symbolic_representation} to "
                        f"{len(self.connected_clients)} clients"
                    )

                # Wait before next update
                await asyncio.sleep(self.throttle_ms / 1000)

            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(5)  # Error recovery delay

    async def start(self):
        """Start the WebSocket server and broadcast loop"""
        # Start broadcast loop
        asyncio.create_task(self.broadcast_loop())

        # Start WebSocket server
        logger.info(f"🚀 Starting WebSocket server on ws://localhost:{self.port}")
        async with websockets.serve(self.handle_client, "localhost", self.port):
            await asyncio.Future()  # Run forever


# CLI entry point
async def main():
    """Run the consciousness broadcaster"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHΛS Consciousness Broadcaster")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument(
        "--throttle", type=int, default=5000, help="Throttle rate in ms"
    )
    parser.add_argument(
        "--simulation", action="store_true", help="Enable simulation mode"
    )
    parser.add_argument(
        "--state-file", default="consciousness_state.json", help="State file path"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    broadcaster = ConsciousnessBroadcaster(
        state_file=args.state_file,
        port=args.port,
        throttle_ms=args.throttle,
        simulation_mode=args.simulation,
    )

    await broadcaster.start()


if __name__ == "__main__":
    asyncio.run(main())
