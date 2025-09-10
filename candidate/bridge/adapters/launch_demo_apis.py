#!/usr/bin/env python3
"""
LUKHAS Demo API Launcher
Starts all demo APIs for showcase presentations
"""
import signal
import subprocess
import sys
import time

# API configurations
APIS = [
    {
        "name": "Dream Recall API",
        "script": "apis/create_dream_recall_api.py",
        "port": 8001,
        "priority": 1,
    },
    {
        "name": "Emotional Coherence API",
        "script": "apis/create_emotional_coherence_api.py",
        "port": 8002,
        "priority": 4,
    },
    {
        "name": "Memory Fold API",
        "script": "apis/create_memory_fold_api.py",
        "port": 8003,
        "priority": 2,
    },
    {
        "name": "Colony Consensus API",
        "script": "apis/create_colony_consensus_api.py",
        "port": 8004,
        "priority": 5,
    },
    {
        "name": "Classical Dream API",
        "script": "apis/create_classical_dream_api.py",
        "port": 8005,
        "priority": 6,
    },
    {
        "name": "Classical Emotional API",
        "script": "apis/create_classical_emotional_api.py",
        "port": 8006,
        "priority": 7,
    },
]

processes = []


def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    print("\n🛑 Shutting down LUKHAS demo APIs...")
    for process in processes:
        process.terminate()
    sys.exit(0)


def start_api(api_config):
    """Start a single API"""
    print(f"🚀 Starting {api_config['name']} on port {api_config['port']}...")

    # Modify the script to use the configured port
    env = {"PORT": str(api_config["port"]), "API_NAME": api_config["name"]}

    process = subprocess.Popen(["python", api_config["script"]], env={**env, **dict(os.environ)})

    return process


if __name__ == "__main__":
    import os

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(
        """
╔═══════════════════════════════════════════════════════╗
║           LUKHAS Demo API Launcher v1.0               ║
║                                                       ║
║  Starting all demonstration APIs for showcase...      ║
╚═══════════════════════════════════════════════════════╝
    """
    )

    # Sort by priority
    sorted_apis = sorted(APIS, key=lambda x: x["priority"])

    # Start all APIs
    for api in sorted_apis:
        try:
            process = start_api(api)
            processes.append(process)
            time.sleep(2)  # Give each API time to start
        except Exception as e:
            print(f"❌ Failed to start {api['name']}: {e!s}")

    print(f"\n✅ All {len(processes)} APIs started successfully!")
    print("\n📍 API Endpoints:")
    for api in sorted_apis:
        print(f"   - {api['name']}: http://localhost:{api['port']}")

    print("\n🌐 Demo Dashboard: http://localhost:8000")
    print("\nPress Ctrl+C to stop all APIs\n")

    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    api = sorted_apis[i]
                    print(f"⚠️  {api['name']} stopped unexpectedly. Restarting...")
                    processes[i] = start_api(api)
    except KeyboardInterrupt:
        signal_handler(None, None)