"""
Base classes for the Consciousness module.
"""

import time

class Consciousness:
    """
    A simple representation of a consciousness state.
    """
    def __init__(self, name="LUKHAS"):
        self.name = name
        self.active = False
        self.start_time = None
        self.status = "inactive"

    def activate(self):
        """Activates the consciousness."""
        if not self.active:
            self.active = True
            self.start_time = time.time()
            self.status = "active"
            print(f"{self.name} consciousness activated.")
        else:
            print(f"{self.name} consciousness is already active.")

    def deactivate(self):
        """Deactivates the consciousness."""
        if self.active:
            self.active = False
            self.start_time = None
            self.status = "inactive"
            print(f"{self.name} consciousness deactivated.")
        else:
            print(f"{self.name} consciousness is already inactive.")

    def get_status(self):
        """Returns the current status of the consciousness."""
        if self.active:
            uptime = time.time() - self.start_time
            return f"Status: {self.status}, Uptime: {uptime:.2f} seconds"
        else:
            return f"Status: {self.status}"
