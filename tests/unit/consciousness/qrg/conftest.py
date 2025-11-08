import sys
from unittest.mock import MagicMock

# Mock the _bridgeutils module to avoid ImportError during test collection
mock_bridgeutils = MagicMock()
mock_bridgeutils.bridge_from_candidates.return_value = (MagicMock(), MagicMock())
sys.modules['_bridgeutils'] = mock_bridgeutils

# Mock the consciousness.qi module
sys.modules['consciousness.qi'] = MagicMock()

# Mock the lukhas_bridge module
sys.modules['products.security.qrg.lukhas_bridge'] = MagicMock()
