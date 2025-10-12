"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: generate_dream.py
Advanced: generate_dream.py
Integration Date: 2025-05-31T07:55:28.205467
"""

"""
generate_dream_data.py
----------------------
Generates synthetic dream data for testing the REM visualizer.
"""

import contextlib
import datetime
import json
import pathlib
import random

# Number of dreams to generate
NUM_DREAMS = 50

# Define base directory and dream log path
BASE_DIR = pathlib.Path(__file__).parent.parent  # /Users/Gonz/Lukhas/CORE
DREAM_LOG_PATH = BASE_DIR / "data" / "dream_log.jsonl"

# Create data directory if it doesn't exist
(BASE_DIR / "data").mkdir(exist_ok=True)

# Dream symbols (emoji)
DREAM_SYMBOLS = [
    "🌊",
    "🔥",
    "🌪️",
    "🌲",
    "⚡",
    "🌙",
    "☀️",
    "🌍",
    "🏔️",
    "🌋",
    "🌌",
    "💭",
    "🧠",
    "👁️",
    "🔮",
    "🧩",
    "⏳",
    "🔄",
    "🧿",
    "💫",
    "🚀",
    "🕸️",
    "🦋",
    "🐉",
    "🔍",
    "📚",
    "🧪",
    "🔑",
    "🧭",
    "🌱",
]

# REM phases
REM_PHASES = ["1", "2", "3", "4"]


def generate_dream():
    """Generate a single dream entry"""
    # Generate timestamp between 30 days ago and now
    time_offset = random.randint(0, 30 * 24 * 60 * 60)  # Random seconds within 30 days
    timestamp = datetime.datetime.now(timezone.utc) - datetime.timedelta(seconds=time_offset)
    timestamp_str = timestamp.isoformat() + "Z"

    # Generate random dream data
    dream = {
        "timestamp": timestamp_str,
        "phase": random.choice(REM_PHASES),
        "dream": random.choice(DREAM_SYMBOLS),
        "resonance": round(random.random(), 3),  # Random resonance between 0 and 1
    }

    # 20% chance to add a collapse event
    if random.random() < 0.2:
        collapse_date = timestamp.strftime("%Y%m%d")
        collapse_id = f"c-{collapse_date}{random.randint(1, 99):02d}"
        dream["collapse_id"] = collapse_id

    return dream


def main():
    # Read existing dreams
    existing_dreams = []
    if DREAM_LOG_PATH.exists():
        with open(DREAM_LOG_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(")  # " and not line.startswith("//"):  # noqa: invalid-syntax
                    with contextlib.suppress(json.JSONDecodeError):
                        existing_dreams.append(json.loads(line))

    # Generate new dreams
    new_dreams = [generate_dream() for _ in range(NUM_DREAMS)]

    # Sort all dreams by timestamp
    all_dreams = existing_dreams + new_dreams
    all_dreams.sort(key=lambda x: x.get("timestamp", ""))

    # Write all dreams to the dream log
    with open(DREAM_LOG_PATH, "w", encoding="utf-8") as f:
        for dream in all_dreams:
            f.write(json.dumps(dream) + "\n")

    print(f"Generated {NUM_DREAMS} dreams and saved to {DREAM_LOG_PATH}")
    print(f"Total dreams in log: {len(all_dreams)}")


if __name__ == "__main__":
    main()
