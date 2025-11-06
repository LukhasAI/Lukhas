"""
Streamlit compatibility shim for CI environment
Provides mock streamlit functions for testing
"""

# Mock streamlit module
import sys

class StreamlitMock:
    """Mock streamlit for CI testing."""

    def __getattr__(self, name):
        def mock_function(*args, **kwargs):
            return None

        return mock_function



sys.modules["streamlit"] = StreamlitMock()


# Common streamlit functions
def write(*args, **kwargs):
    pass


def markdown(*args, **kwargs):
    pass


def header(*args, **kwargs):
    pass


def subheader(*args, **kwargs):
    pass


def text(*args, **kwargs):
    pass


def json(*args, **kwargs):
    pass


def selectbox(*args, **kwargs):
    return None


def button(*args, **kwargs):
    return False
