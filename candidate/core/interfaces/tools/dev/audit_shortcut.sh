

#!/bin/bash

echo "🔧 LUKHAS AGI: Audit + News Shortcut Menu"
echo "----------------------------------------"
echo "1. 🧠 Trigger Audit Logger"
echo "2. 🌐 Publish Lukhas News Opinion"
echo "3. 🌌 Replay Dream & Narrate"
echo "4. 📝 Export DAO Snapshot"
echo "5. 📤 Submit to Publish Queue"
echo "0. ❌ Exit"
echo "----------------------------------------"

read -p "Choose an action (0-5): " option

case $option in
  1)
    echo "🧠 Launching symbolic audit logger..."
    python3 tools/gen_audit_logger_check.py
    ;;
  2)
    echo "🌐 Generating and publishing symbolic news..."
    python3 dashboards/lukhas_public_dashboard.py publish
    ;;
  3)
    echo "🌌 Replaying dream and triggering narration..."
    python3 voice/dream_voice_pipeline.py --replay-latest
    ;;
  4)
    echo "📝 Exporting DAO config snapshot..."
    python3 dao/init_config.py export
    ;;
  5)
    echo "📤 Submitting latest dream to publish_queue.jsonl..."
    python3 utils/publish_queue_manager.py --submit-latest
    ;;
  0)
    echo "👋 Exiting."
    exit 0
    ;;
  *)
    echo "❗ Invalid choice. Please run again."
    ;;
esac
