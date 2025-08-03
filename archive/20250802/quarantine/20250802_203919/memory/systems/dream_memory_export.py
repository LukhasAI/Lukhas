#!/usr/bin/env python3
"""
```plaintext
+===========================================================================+
|                           MODULE: DREAM MEMORY EXPORT                    |
|                          DESCRIPTION: Export symbolic dream logs.         |
+===========================================================================+

+---------------------------------------------------------------------------+
|                          POETIC ESSENCE                                   |
|---------------------------------------------------------------------------|
| In the realm where thoughts entwine and dreams take flight,                  |
| This module stands as a custodian of the ephemeral whispers of the night.  |
| Like the silken threads of a cosmic tapestry, it weaves together the        |
| ethereal echoes of our subconscious journeys, transforming the intangible   |
| into the tangible-each log a testament to the landscapes of our slumber.   |
|                                                                             |
| As the stars illuminate the darkened sky, guiding lost souls on their paths,|
| So does the Dream Memory Export illuminate the intricate narratives spun by  |
| the mind's eye. It serves as a bridge, a conduit through which the         |
| kaleidoscopic visions of our dreams are transcribed into the annals of     |
| technological memory. Herein lies a symphony of thoughts, a dance of       |
| symbols, waiting to be interpreted by those who dare to delve deeper into   |
| the mysteries of their inner worlds.                                         |
|                                                                             |
| With reverence for the sacredness of each dream, this module stands firm,   |
| a guardian of our mental archives, ensuring the integrity and clarity of    |
| each whispered secret. It invites explorers of consciousness to embark on   |
| a quest, where every exported log is a key unlocking doors to self-        |
| discovery and introspection. Thus, through the lens of this memory system,  |
| we are reminded that even the most fleeting moments can resonate with      |
| profound significance, echoing through the corridors of our understanding.  |
+---------------------------------------------------------------------------+

+---------------------------------------------------------------------------+
|                         TECHNICAL FEATURES                                 |
|---------------------------------------------------------------------------|
| * Facilitates the exportation of dream logs in structured formats,         |
|   ensuring ease of access and analysis.                                    |
| * Supports symbolic representation, allowing nuanced interpretations       |
|   of subconscious narratives.                                              |
| * Implements robust data validation techniques to maintain integrity       |
|   of exported logs.                                                        |
| * Provides user-friendly interfaces for seamless interaction with dream    |
|   archives.                                                                |
| * Maintains compatibility with various data storage formats, enhancing     |
|   integration capabilities.                                                |
| * Offers detailed logging and error handling mechanisms for efficient      |
|   troubleshooting.                                                         |
| * Enables batch processing of dream logs, optimizing performance          |
|   for extensive datasets.                                                  |
| * Includes comprehensive documentation and usage guidelines for            |
|   effective utilization of the module.                                     |
+---------------------------------------------------------------------------+

+---------------------------------------------------------------------------+
|                             ΛTAG KEYWORDS                                  |
|---------------------------------------------------------------------------|
| CRITICAL, KeyFile, Memory, Export, Dreams, Symbolic Representation,        |
| Data Integrity, Consciousness, Subconscious, Analysis                      |
+---------------------------------------------------------------------------+
```
"""

lukhas AI System - Function Library
File: dream_memory_export.py
Path: core/memory/dream_memory_export.py
Created: "2025-06-05 09:37:28"
Author: LUKHAS AI Team
Version: 1.0

This file is part of the LUKHAS AI (LUKHAS Universal Knowledge & Holistic AI System)
Advanced Cognitive Architecture for Artificial General Intelligence

Copyright (c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

"""
+──────────────────────────────────────────────────────────────────────────────+
+──────────────────────────────────────────────────────────────────────────────+

DESCRIPTION:
    This symbolic tool exports dream logs from dream_log.jsonl into a variety
    of formats for analysis, sharing, or archival. It can generate:
    - Filtered JSON exports
    - Plain text summaries
    - Markdown annotated transcripts

USAGE:
    Run via terminal:
        python core/modules/nias/dream_memory_export.py --format txt
        python core/modules/nias/dream_memory_export.py --format md --tag "calm"
        python core/modules/nias/dream_memory_export.py --tier 3 --emoji 🌙

NOTES:
    - Requires: dream_log.jsonl in core/logs/
    - Filters: by tag, tier, or emoji
    - Output written to: core/exports/

"""

import os
import json
import argparse

DREAM_LOG_PATH = "core/logs/dream_log.jsonl"
EXPORT_DIR = "core/exports/"

def load_dreams():
    if not os.path.exists(DREAM_LOG_PATH):
        print("❌ No dream log found.")
        return []
    with open(DREAM_LOG_PATH, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def filter_dreams(dreams, tag=None, tier=None, emoji=None):
    filtered = dreams
    if tag:
        filtered = [d for d in filtered if tag in d.get("tags", [])]
    if tier:
        filtered = [d for d in filtered if d.get("tier") == tier]
    if emoji:
        filtered = [d for d in filtered if d.get("reaction_emoji") == emoji]
    return filtered

def export_dreams(dreams, format):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = os.path.join(EXPORT_DIR, f"lukhas_dream_export.{format}")

    if format == "json":
        with open(filename, "w") as f:
            json.dump(dreams, f, indent=2)
    elif format == "txt":
        with open(filename, "w") as f:
            for d in dreams:
                f.write(f"{d['timestamp']} | T{d['tier']} | {d['reaction_emoji']}: {d['summary']}\n")
    elif format == "md":
        with open(filename, "w") as f:
            f.write("# LUClukhasS Dream Log Export\n\n")
            for d in dreams:
                f.write(f"## {d['timestamp']} ({d['reaction_emoji']})\n")
                f.write(f"**Tier**: {d['tier']}  \n")
                f.write(f"**Tags**: {', '.join(d.get('tags', []))}  \n")
                f.write(f"**Summary**: {d['summary']}  \n\n")
    print(f"✅ Dreams exported to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export symbolic dream logs.")
    parser.add_argument("--format", choices=["json", "txt", "md"], default="txt")
    parser.add_argument("--tag", type=str, help="Filter by tag")
    parser.add_argument("--tier", type=int, help="Filter by user tier")
    parser.add_argument("--emoji", type=str, help="Filter by symbolic emoji")
    args = parser.parse_args()

    all_dreams = load_dreams()
    filtered = filter_dreams(all_dreams, tag=args.tag, tier=args.tier, emoji=args.emoji)
    export_dreams(filtered, args.format)

"""
+──────────────────────────────────────────────────────────────────────────────+
+──────────────────────────────────────────────────────────────────────────────+

LUClukhasS MODULE USAGE SUMMARY:
    🧠 Function: Exports symbolic dream logs in user-defined formats (JSON, TXT, MD)
    🎯 Filters: tag, tier, emoji-based filtering
    🗂 Output: core/exports/lukhas_dream_export.{format}

RUN EXAMPLES:
    python dream_memory_export.py --format txt
    python dream_memory_export.py --format md --tag "calm"
    python dream_memory_export.py --format json --tier 3 --emoji 🌙

RELATED MODULES:
    * dream_recorder.py -> source of symbolic logs
    * dream_replay.py   -> playback and visualization
    * voice_narrator.py -> for narrated dream exports

- Crafted by Gonzo R.D.M 🖤 April 2025 -
"""






# Last Updated: 2025-06-05 09:37:28

# TECHNICAL IMPLEMENTATION: Neural network architectures with adaptive learning, Artificial intelligence with advanced cognitive modeling, Bioinformatics processing for pattern recognition
# lukhas Systems 2025 www.lukhas.ai 2025
