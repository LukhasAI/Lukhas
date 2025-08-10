#!/usr/bin/env python3
"""
Generate performance visualization for quantized thought cycles
"""

import json

import matplotlib.pyplot as plt
import numpy as np

# Load results
with open("benchmarks/quantized_cycles_results.json") as f:
    results = json.load(f)

# Extract data
configs = []
throughputs = []
latencies = []
frequencies = []

for name, data in results["configurations"].items():
    configs.append(name.split("(")[0].strip())
    throughputs.append(data["throughput"]["throughput_per_second"])
    latencies.append(data["latency"]["mean_ms"])
    frequencies.append(data["frequency_hz"])

# Create figure with subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Throughput chart
ax1.bar(configs, throughputs, color=["#FF6B6B", "#4ECDC4", "#45B7D1"])
ax1.set_ylabel("Throughput (thoughts/sec)")
ax1.set_title("Throughput by Configuration")
ax1.grid(True, alpha=0.3)

# Add value labels on bars
for i, v in enumerate(throughputs):
    ax1.text(i, v + 1, f"{v:.1f}", ha="center", va="bottom")

# Latency chart
ax2.bar(configs, latencies, color=["#FF6B6B", "#4ECDC4", "#45B7D1"])
ax2.set_ylabel("Mean Latency (ms)")
ax2.set_title("Latency by Configuration")
ax2.grid(True, alpha=0.3)

# Add value labels on bars
for i, v in enumerate(latencies):
    ax2.text(i, v + 1, f"{v:.1f}", ha="center", va="bottom")

# Overall title
fig.suptitle("Quantized Thought Cycles - Performance Metrics", fontsize=16)

# Adjust layout and save
plt.tight_layout()
plt.savefig("benchmarks/quantized_cycles_performance.png", dpi=150, bbox_inches="tight")
print("📊 Performance chart saved to benchmarks/quantized_cycles_performance.png")

# Create a cycle timing visualization
fig2, ax = plt.subplots(figsize=(10, 6))

# Data for cycle phases (simulated based on our implementation)
phases = ["Bind", "Conform", "Catalyze", "Release"]
phase_times = [1.0, 2.0, 5.0, 1.0]  # milliseconds
colors = ["#96CEB4", "#FFEAA7", "#DDA0DD", "#B2BABB"]

# Create horizontal bar chart
y_pos = np.arange(len(phases))
ax.barh(y_pos, phase_times, color=colors)

# Customize
ax.set_yticks(y_pos)
ax.set_yticklabels(phases)
ax.set_xlabel("Duration (ms)")
ax.set_title("Thought Cycle Phase Timing")
ax.grid(True, alpha=0.3, axis="x")

# Add value labels
for i, v in enumerate(phase_times):
    ax.text(v + 0.1, i, f"{v} ms", va="center")

# Add total cycle time
total_time = sum(phase_times)
ax.text(
    0.5,
    -0.7,
    f"Total Cycle Time: {total_time} ms",
    transform=ax.transAxes,
    ha="center",
    fontsize=12,
    fontweight="bold",
)

plt.tight_layout()
plt.savefig("benchmarks/quantized_cycle_phases.png", dpi=150, bbox_inches="tight")
print("📊 Cycle phase chart saved to benchmarks/quantized_cycle_phases.png")

print("\n✅ Visualization complete!")
