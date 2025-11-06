"""governance compatibility - forwards to governance or candidate.governance."""

import sys
from lukhas_website.lukhas.governance import schema_registry
sys.modules['governance.schema_registry'] = schema_registry
