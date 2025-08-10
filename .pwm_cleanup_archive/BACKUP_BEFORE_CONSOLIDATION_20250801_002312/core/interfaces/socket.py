# ===============================================================
# 📂 FILE: lukhas_socket.py
# 📍 RECOMMENDED PATH: /Users/grdm_admin/LUKHAS_AGI/core/interface/
# ===============================================================
# 🧠 PURPOSE:
# This module enables real-time symbolic input via sockets (CLI, web, agent loop).
# It is designed for future live AGI loops, symbolic chat relay, and reflex response simulation.
#
# 🛡️ SECURITY:
# Tier 4+ access required to trigger publish_queue injection or dream synthesis.
#
# 🧰 FEATURES:
# - Listens on localhost:3030
# - Accepts symbolic JSON with `message`, `tier`, `origin`
# - Logs incoming data to `publish_queue.jsonl` if verified
# ===============================================================

import asyncio
import json
import logging
import time

import websockets

# Initialize logger
logger = logging.getLogger(__name__)

PUBLISH_QUEUE_PATH = "core/logging/publish_queue.jsonl"


async def handle_message(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            symbolic_message = data.get("message", "").strip()
            tier = int(data.get("tier", 0))
            origin = data.get("origin", "unverified")

            logger.info(
                f"Incoming message from {origin} [Tier {tier}]: {symbolic_message}"
            )

            if symbolic_message and tier >= 4:
                with open(PUBLISH_QUEUE_PATH, "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "timestamp": time.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                                ),
                                "message": symbolic_message,
                                "origin": origin,
                                "tier": tier,
                            }
                        )
                        + "\n"
                    )
                logger.info("Symbolic message added to publish_queue.")
            else:
                logger.warning("Tier too low or message empty. Ignored.")

        except Exception as e:
            logger.error(f"Failed to process message: {e}")


async def listen_to_socket(port=3030):
    logger.info(f"Lukhas is listening symbolically on port {port}")
    print("🎧 Lukhas is listening symbolically on port", port)  # Keep UI output
    async with websockets.serve(handle_message, "localhost", port):
        await asyncio.Future()  # run forever


# 🔁 Preview CLI entry
if __name__ == "__main__":
    asyncio.run(listen_to_socket())
