import time
from orchestration.symbolic_kernel_bus import kernel_bus


def test_capability_and_task_announcements():
    bus = EventBus()
    received = []

    def handler(event_type, event):
        received.append((event_type, event))

    bus.subscribe("CAPABILITY_ANNOUNCEMENT", handler)
    bus.subscribe("TASK_ANNOUNCEMENT", handler)

    bus.announce_capability("agent1", {"skill": "analysis"})
    bus.announce_task({"agent_id": "client1", "task": "data_analysis"})

    # Allow async threads to process
    time.sleep(0.1)

    assert bus.capabilities_registry["agent1"] == {"skill": "analysis"}
    assert any(evt[0] == "CAPABILITY_ANNOUNCEMENT" for evt in received)
    assert any(evt[0] == "TASK_ANNOUNCEMENT" for evt in received)
