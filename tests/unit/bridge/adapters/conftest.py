import sys
from unittest.mock import MagicMock

# Mock the '_bridgeutils' module.
mock_bridgeutils = MagicMock()

# The __init__.py in the adapters directory unpacks the result of bridge(),
# so we must configure the mock to return a 3-tuple to avoid a ValueError.
mock_bridgeutils.bridge.return_value = (MagicMock(), MagicMock(), [])

sys.modules["_bridgeutils"] = mock_bridgeutils
