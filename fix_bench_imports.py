import re

# Read the file
with open('scripts/bench_t4_excellence.py', 'r') as f:
    content = f.read()

# Fix the broken import structure - move logger declaration after imports
fixed_content = content.replace(
    """from bench_core import (

# Module-level logger
logger = logging.getLogger(__name__)
    PerformanceBenchmark,  # - requires sys.path manipulation before import
)
from preflight_check import (
    PreflightValidator,  # - requires sys.path manipulation before import
)""",
    """from bench_core import (
    PerformanceBenchmark,  # - requires sys.path manipulation before import
)
from preflight_check import (
    PreflightValidator,  # - requires sys.path manipulation before import
)

# Module-level logger
logger = logging.getLogger(__name__)"""
)

# Write fixed content
with open('scripts/bench_t4_excellence.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed import syntax in bench_t4_excellence.py")
