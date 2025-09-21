"""
Minimal Actor/Agent class for symbiotic multi-agent architecture.
Implements encapsulated state, behavior, and asynchronous message passing.
"""
import queue
import threading


class Actor:
    def __init__(self, behavior, state=None):
        self.state = state or {}
        self.behavior = behavior
        self.mailbox = queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def send(self, message):
        self.mailbox.put(message)

    def _run(self):
        while True:
            message = self.mailbox.get()
            self.behavior(self, message)


# Example behavior function


def echo_behavior(actor, message):
    print(f"Actor received: {message}")
    # Example: update state or send messages
    actor.state["last_message"] = message


# Example usage
if __name__ == "__main__":
    actor = Actor(echo_behavior)
    actor.send("Hello, Cognitive AI world!")
