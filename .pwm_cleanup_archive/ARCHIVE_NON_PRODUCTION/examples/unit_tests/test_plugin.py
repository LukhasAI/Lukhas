class MockPlugin:
    def __init__(self):
        self.name = "test_plugin"
        self.received_signal = None

    def process_signal(self, signal):
        self.received_signal = signal


plugin = MockPlugin
