"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: emotion_trend_tracker.py
Advanced: emotion_trend_tracker.py
Integration Date: 2025-05-31T07:55:28.100778
"""

from collections import defaultdict
import json

def analyze_emotion_trends():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 LUCΛS :: EMOTION TREND TRACKER")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    tag_counter = defaultdict(int)
    emoji_counter = defaultdict(int)

    with open('dream_log.jsonl', 'r') as file:
        for line in file:
            entry = json.loads(line)
            tags = entry.get("tags", [])
            for tag in tags:
                tag_counter[tag] += 1
            
            emoji = entry.get("emoji")
            if emoji:
                emoji_counter[emoji] += 1

    print("Emotion Trends:")
    for tag, count in tag_counter.items():
        print(f"  • {tag}: {count}")
    
    print("\n🖼️  Symbolic Emoji Reactions (Dream Log)")
    sorted_emojis = sorted(emoji_counter.items(), key=lambda x: x[1], reverse=True)
    for emj, count in sorted_emojis:
        print(f"  • {emj}: {count}")

    print("\n📈 Top 5 Tags by Frequency")
    sorted_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    for tag, count in sorted_tags:
        print(f"  • {tag}: {count}")

    print("\n⚖️  Joy–Stress Ratio (symbolic mood balance):")
    total_joy = total_stress = 0
    with open('dream_log.jsonl', 'r') as file:
        for line in file:
            entry = json.loads(line)
            vector = entry.get("emotion_vector", {})
            total_joy += vector.get("joy", 0)
            total_stress += vector.get("stress", 0)

    ratio = total_joy / total_stress if total_stress > 0 else "∞"
    print(f"  • Joy: {total_joy:.2f}")
    print(f"  • Stress: {total_stress:.2f}")
    print(f"  • Ratio: {ratio}")
