"""
sleep_cycle.py
--------------
Triggers a symbolic sleep/dream cycle for Lucʌs.
Logs a memory trace, folds it, seeds a dream, and stores the dream output.
"""

from dream.core.dream_log import dream_logger
from modules.dream_seed import seed_dream
from modules.fold_token import fold_trace
from modules.memoria import log_trace

# Step 1: Log a symbolic memory trace (simulate for now)
trace = log_trace(
    {
        "event": "User enters symbolic rest mode",
        "emotion": {"valence": -0.1, "arousal": 0.2},
        "traits": {"calm": 0.9},
    }
)

# Step 2: Fold the trace into a symbolic token
folded = fold_trace(trace)

# Step 3: Seed a dream based on the folded trace
dream = seed_dream(folded)

# Step 4: Log the symbolic dream
dream_logger.log_dream(
    dream_id=f"sleep_cycle_{folded.get('token_id', 'unknown')}",
)
