"""

#TAG:memory
#TAG:consolidation
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: compliance_digest.py
Advanced: compliance_digest.py
Integration Date: 2025-05-31T07:55:27.746797
"""

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: compliance_digest.py
# 🧾 PURPOSE: Generate a weekly symbolic compliance digest from emergency override logs
# 🛡️ OUTPUT: Governance summary + symbolic insights
# ════════════════════════════════════════════════════════════════════════

import json
import os
from collections import Counter
from datetime import datetime

import matplotlib.pyplot as plt

LOG_PATH = "logs/emergency_log.jsonl"
DIGEST_OUTPUT = "logs/weekly_compliance_digest.md"


def load_emergency_logs():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def generate_digest():
    logs = load_emergency_logs()
    if not logs:
        return "No emergency events logged this week."

    reasons = Counter()
    users = Counter()
    tiers = Counter()
    compliance_flags = Counter()
    total_entries = len(logs)

    for entry in logs:
        reasons[entry.get("reason", "unknown")] += 1
        users[entry.get("user", "unknown")] += 1
        tiers[entry.get("tier", 0)] += 1
        for tag, value in entry.get("institutional_compliance", {}).items():
            if value:
                compliance_flags[tag] += 1

    def plot_bar(data_dict, title, xlabel, ylabel, filename):
        labels, values = zip(*data_dict.items())
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color=")  # 4e79a7"
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join("logs", filename))
        plt.close()

    # Plot: Tier Distribution
    plot_bar(tiers, "Tier Distribution", "Tier", "Events", "tier_breakdown.png")

    # Plot: User Trigger Count
    plot_bar(users, "User Trigger Count", "User", "Events", "user_trigger_count.png")

    # Plot: Emergency Reasons (Top 5)
    top_reasons = dict(reasons.most_common(5))
    plot_bar(
        top_reasons,
        "Top Emergency Triggers",
        "Reason",
        "Occurrences",
        "top_emergency_reasons.png",
    )

    timestamp = datetime.now(timezone.utc).isoformat()
    top_reason = reasons.most_common(1)[0] if reasons else ("none", 0)

    digest = (
        f"""# 📊 Lukhas AGI — Weekly Compliance Digest
**Generated:** {timestamp}

## Summary:
- 🧠 Total Emergency Events: {total_entries}
- 📌 Most Common Trigger: **{top_reason[0]}** ({top_reason[1]} occurrences)

## Tier Breakdown:
"""
        + "\n".join([f"- Tier {k}: {v}" for k, v in tiers.items()])
        + """

## User Trigger Count:
"""
        + "\n".join([f"- {u}: {c} events" for u, c in users.items()])
        + """

## Compliance Flag Stats:
"""
        + "\n".join([f"- {k}: ✅ {v} confirmed" for k, v in compliance_flags.items()])
        + """

## 📈 Visual Reports Saved:
- `tier_breakdown.png`
- `user_trigger_count.png`
- `top_emergency_reasons.png`

---

*All emergency logs are audit-safe and reviewed under institutional symbolic policy.*
"""
    )

    os.makedirs("logs", exist_ok=True)
    with open(DIGEST_OUTPUT, "w") as f:
        f.write(digest)
    return digest


# Generate and print to console
if __name__ == "__main__":
    report = generate_digest()
    print(report)
