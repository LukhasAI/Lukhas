"""
lukhas AI System - Function Library
Path: lukhas/core/memory/memoria-checkpoint.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

from datetime import datetime, timezone


class Memoria:
    memory_log = []

    def store(self, input_data, decision):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
            "decision": decision,
        }
        self.memory_log.append(log_entry)
        print(f"[MEMORIA] -> Logged trace: {log_entry}")

    def trace(self):
        print("\n🧠 OXNITUS TRACE LOG:")
        for i, entry in enumerate(self.memory_log, 1):
            print("\n")
            print(f"Timestamp: {entry['timestamp']}")
            print(f"Intent:    {entry['input']}")
            print(f"Decision:  {entry['decision']['justification']}")


# Last Updated: 2025-06-05 09:37:28
