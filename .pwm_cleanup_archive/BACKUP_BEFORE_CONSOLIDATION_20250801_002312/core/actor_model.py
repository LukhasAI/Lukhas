"""
The Actor Model: A Foundation for Concurrent and Distributed Systems
Addresses TODOs 29-42

This module provides a conceptual overview and a simplified implementation
of the Actor Model, which is the foundation for the agents in the Symbiotic Swarm.
"""

import queue
import threading


class Actor:
    """
    A simple implementation of the Actor Model.
    """

    def __init__(self):
        self._mailbox = queue.Queue()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        while True:
            message = self._mailbox.get()
            self.receive(message)

    def receive(self, message):
        """
        This method should be overridden by subclasses to define the actor's behavior.
        """
        raise NotImplementedError

    def send(self, message):
        """
        Sends a message to the actor's mailbox.
        """
        self._mailbox.put(message)


class PingActor(Actor):
    def receive(self, message):
        if message == "ping":
            print("PingActor: Received ping.")
            pong_actor.send("pong")
        else:
            print(f"PingActor: Received unexpected message: {message}")


class PongActor(Actor):
    def receive(self, message):
        if message == "pong":
            print("PongActor: Received pong.")
        else:
            print(f"PongActor: Received unexpected message: {message}")


if __name__ == "__main__":
    ping_actor = PingActor()
    pong_actor = PongActor()

    ping_actor.send("ping")

    # Give the actors some time to process the message
    import time

    time.sleep(1)
