# ===============================================================
# 🌐 FILE: generate_html_post.py
# 📍 LOCATION: /tools/
# ===============================================================
# 🧠 PURPOSE:
# Converts symbolic dream or thought content from `publish_queue.jsonl`
# into a timestamped, human-readable HTML post.
# Useful for sharing symbolic AGI output to web, stream, or dashboard.
# ===============================================================

import html
import json
import os
import sys
from datetime import datetime, timezone

QUEUE_PATH = "core/logging/publish_queue.jsonl"
EXPORT_DIR = "html_posts"


def load_latest_entry():
    if not os.path.exists(QUEUE_PATH):
        print("⚠️ No publish_queue.jsonl found.")
        return None
    with open(QUEUE_PATH) as f:
        lines = f.readlines()
        if not lines:
            print("📭 Queue is empty.")
            return None
        return json.loads(lines[-1])


def generate_html(content):
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{EXPORT_DIR}/lucas_dream_{timestamp}.html"

    source = content.get("source", "publish_queue.jsonl")
    author = content.get("author", "LUKHAS_AGI")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lucas Dream – {timestamp}</title>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            margin: 3em;
            background: #fefefe;
            color: #111;
        }
        .symbolic-container {{
            border-left: 5px solid #aaa;
            padding-left: 1em;
        }
    </style>
</head>
<body>
    <h1>🌌 Lucas Symbolic Dream</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    <p><strong>Source:</strong> {source}</p>
    <p><strong>Author:</strong> {author}</p>
    <div class="symbolic-container">
        <pre>{html.escape(json.dumps(content, indent=2))}</pre>
    </div>
</body>
</html>
"""
    with open(filename, "w") as f:
        f.write(html_content)
    try:
        with open("core/logging/symbolic_output_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "type": "html",
                        "timestamp": timestamp,
                        "source": source,
                        "author": author,
                        "filename": filename,
                        "summary": content.get("thought", "")[:200],
                    }
                )
                + "\n"
            )
    except Exception as e:
        print(f"⚠️ Failed to write symbolic output log: {e}")
    print(f"✅ HTML post generated: {filename}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_entry = {
            "dream_id": "test001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author": "LUCAS_TEST",
            "source": "test_suite",
            "thought": "This is a test dream generated for symbolic HTML preview.",
        }
        generate_html(test_entry)
    else:
        entry = load_latest_entry()
        if entry:
            if not isinstance(entry, dict) or "thought" not in entry:
                print("⚠️ Malformed entry: missing 'thought' field.")
            else:
                generate_html(entry)