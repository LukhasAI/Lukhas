import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.actor_system import AIAgentActor, get_global_actor_system
from core.p2p_communication import MessageType


class P2PActor(AIAgentActor):
    async def pre_start(self):
        await super().pre_start()
        p2p_node = await self.actor_system.get_p2p_node(self.actor_id)
        if p2p_node:

            async def handle_data(node, message):
                print(
                    f"Actor {self.actor_id} received P2P message from {message.sender_id}: {message.payload}"
                )

            p2p_node.register_handler(MessageType.DATA, handle_data)


async def main():
    system = await get_global_actor_system()

    # Create two actors
    actor1_ref = await system.create_actor(P2PActor, "p2p-actor-1")
    actor2_ref = await system.create_actor(P2PActor, "p2p-actor-2")

    # Get their P2P nodes
    node1 = await system.get_p2p_node("p2p-actor-1")
    node2 = await system.get_p2p_node("p2p-actor-2")

    # Actor 1 connects to Actor 2
    response = await actor1_ref.ask(
        "p2p_connect", {"address": node2.host, "port": node2.port}
    )
    print(f"P2P connect response: {response}")

    if response["status"] == "connected":
        peer_id = response["peer_id"]

        # Actor 1 sends a P2P message to Actor 2
        response = await actor1_ref.ask(
            "p2p_send", {"peer_id": peer_id, "payload": {"data": "Hello from Actor 1"}}
        )
        print(f"P2P send response: {response}")

    await asyncio.sleep(1)
    await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
