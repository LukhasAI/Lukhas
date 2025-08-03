"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


┌──────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : compliance_report_generator.py              │
│ 🧾 DESCRIPTION : Generates compliance drift reports (Markdown │
│                 + drift graph).                               │
│ 🧩 TYPE        : Governance Utility  🔧 VERSION: v0.2.0       │
│ 🖋️ AUTHOR      : Lucas AGI             📅 CREATED: 2025-04-27 │
├──────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                              │
│   - pandas                                                    │
│   - matplotlib                                                │
└──────────────────────────────────────────────────────────────┘
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def load_drift_logs(file_path):
    """
    Loads compliance drift logs from a CSV file.
    """
    return pd.read_csv(file_path)

def plot_drift_scores(log_df, output_image):
    """
    Generates a line graph of drift scores over time.
    """
    log_df['Date'] = pd.to_datetime(log_df['Date'])
    plt.figure(figsize=(8, 4))
    plt.plot(log_df['Date'], log_df['Cumulative Drift Score'], marker='o', color='red', label='Drift Score')
    plt.axhline(y=0.3, color='orange', linestyle='--', label='Recalibration Threshold')
    plt.axhline(y=0.6, color='red', linestyle='--', label='Escalation Threshold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Drift Score')
    plt.title('LUKHAS_AGI_3 Compliance Drift Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_image)
    plt.close()

def generate_report(log_df, base_report_dir="lucas_governance/reports/"):
    """
    Generates a compliance drift report in Markdown format with a graph.
    """
    now = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(base_report_dir, now)
    os.makedirs(output_dir, exist_ok=True)

    report_file = os.path.join(output_dir, "compliance_drift_report.md")
    graph_file = os.path.join(output_dir, "drift_score_plot.png")

    # Generate drift score graph
    plot_drift_scores(log_df, graph_file)

    # Create Markdown report
    summary = f"""
# 📑 LUKHAS_AGI_3 Compliance Drift Report

**Reporting Period:** {log_df['Date'].min().date()} to {log_df['Date'].max().date()}  
**Generated On:** {now}  
**System:** LUKHAS_AGI_3  
**Compliance Monitor Version:** v0.2.0  

---

## Summary:

- **Total Decisions Evaluated:** {len(log_df)}
- **Recalibration Events:** {log_df[log_df['Action Taken'] == 'Self-Recalibration'].shape[0]}
- **Escalations to Human Oversight:** {log_df[log_df['Action Taken'] == 'Escalated to Oversight'].shape[0]}
- **Highest Drift Score Recorded:** {log_df['Cumulative Drift Score'].max()}

---

## Drift Score Plot:

![Drift Score Plot]({os.path.basename(graph_file)})

---

## Drift Log Overview:

| Date | Decision ID | Subsystem | Compliance Score | Drift Increment | Cumulative Drift Score | Action Taken |
|------|-------------|-----------|------------------|-----------------|------------------------|--------------|
"""

    for _, row in log_df.iterrows():
        summary += f"| {row['Date']} | {row['Decision ID']} | {row['Subsystem']} | {row['Compliance Score']} | {row['Drift Increment']} | {row['Cumulative Drift Score']} | {row['Action Taken']} |\n"

    # Save Markdown report
    with open(report_file, 'w') as f:
        f.write(summary)
    print(f"✅ Report and graph generated in {output_dir}")

# 🔍 USAGE EXAMPLE:
if __name__ == "__main__":
    drift_log_file = "lucas_governance/logs/compliance_drift_logs.csv"
    df = load_drift_logs(drift_log_file)
    generate_report(df)