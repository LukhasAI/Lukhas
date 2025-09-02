"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_news_dispatcher.py
Advanced: lukhas_news_dispatcher.py
Integration Date: 2025-05-31T07:55:30.492297
"""

import argparse
import json
import os

# TODO: Replace this hack with proper Python packaging imports once
# structure is finalized
import sys
from datetime import datetime
from uuid import uuid4

from modules.voice.lukhas_voice_agent import speak

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# 📄 MODULE: lukhas_news_dispatcher.py
# 🔎 PURPOSE: Dispatch symbolic cognition from queue into simulated publication stream
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-04-30 • ✍️ AUTHOR: LUKHAS AGI

QUEUE_PATH = "logs/publication_simulation/publish_queue.jsonl"
DISPATCH_LOG = "logs/publication_simulation/published_posts.jsonl"

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["voice", "web", "log"], default="log")
args = parser.parse_args()


def load_pending_posts():
    if not os.path.exists(QUEUE_PATH):
        return []
    with open(QUEUE_PATH, encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    for e in entries:
        if "id" not in e:
            e["id"] = str(uuid4())
    return [e for e in entries if not e.get("published")]


def simulate_publish(post):
    post["source_trace"] = post.get("source_trace", "unknown")
    post["image_prompt"] = post.get("image_prompt", "symbolic cognition visual")
    post["image_url"] = f"https://lukhasweb.ai/media/{post['id']}.png"
    post["html_url"] = (
        post.get("html_url") or f"https://lukhasweb.ai/posts/{post['id']}.html"
    )
    print(f"\n📰 Dispatching: {post['theme']}")
    print(post["summary"])
    print(f"📎 Link: {post['html_url']}\n")
    post["published"] = True
    post["published_at"] = datetime.utcnow().isoformat() + "Z"
    return post


def update_dispatch_log(post):
    with open(DISPATCH_LOG, "a", encoding="utf-8") as f:
        json.dump(post, f)
        f.write("\n")


def rewrite_queue(posts):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        for post in posts:
            json.dump(post, f)
            f.write("\n")


if __name__ == "__main__":
    posts = load_pending_posts()
    if not posts:
        print("📭 No new symbolic posts to dispatch.")
    else:
        for post in posts:
            published = simulate_publish(post)
            if args.mode == "voice":
                speak(published["summary"])
            elif args.mode == "web":
                os.system("python3 narration/post_agent.py")
            update_dispatch_log(published)
        rewrite_queue(posts)
        print(
            f"\n✅ {len(posts)} symbolic cognition(s) dispatched to LUKHAS news queue."
        )
