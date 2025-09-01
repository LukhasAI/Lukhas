"""
┌─────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : compliance_drift_monitor.py                         │
│ 🧾 DESCRIPTION : Monitors and mitigates compliance drift             │
│ 🧩 TYPE        : Governance Core        🔧 VERSION: v0.5.0            │
│ 🖋️ AUTHOR      : Lucas AGI              📅 UPDATED: 2025-04-28        │
├─────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                     │
│   - Core Python (datetime, csv, json, os)                            │
│   - Lucas Governance Standards (EU AI Act 2025, GDPR, OECD AI)       │
└─────────────────────────────────────────────────────────────────────┘
"""

import csv
import datetime
import json
import os


class ComplianceMonitor:
    def __init__(self, drift_thresholds=None, log_dir="lucas_governance/logs", moving_average_window=20):
        self.drift_score = 0.0
        self.drift_thresholds = drift_thresholds or {
            "default": {"recalibrate": 0.3, "escalate": 0.6},
            "emotional_oscillator": {"recalibrate": 0.2, "escalate": 0.5},
            "ethics_engine": {"recalibrate": 0.4, "escalate": 0.7},
            "qi_engine": {"recalibrate": 0.35, "escalate": 0.65},
        }
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.csv_log = os.path.join(self.log_dir, "compliance_drift_logs.csv")
        self.json_log = os.path.join(self.log_dir, "compliance_drift_events.json")
        self.compliance_history = []
        self.moving_average_window = moving_average_window

    def evaluate_decision(self, decision_id, compliance_score, subsystem="default", lucas_id="LUCID-000"):
        drift_increment = 0.0
        if self.compliance_history:
            moving_average = sum(self.compliance_history) / len(self.compliance_history)
            deviation = moving_average - compliance_score
            drift_increment = max(0, deviation)
            self.drift_score += drift_increment * 0.5  # Weighted accumulation, increased weight

        # Update compliance history
        self.compliance_history.append(compliance_score)
        if len(self.compliance_history) > self.moving_average_window:
            self.compliance_history.pop(0)

        thresholds = self.drift_thresholds.get(subsystem, self.drift_thresholds["default"])

        # Logging the evaluation
        self._log_decision(decision_id, compliance_score, drift_increment, subsystem, lucas_id)

        # Early entropy warning
        if drift_increment >= 0.25:
            self._log_event(
                f"⚡ Significant compliance drop detected: {drift_increment:.2f}",
                subsystem,
            )

        # Threshold-based actions
        if self.drift_score >= thresholds["escalate"]:
            self.escalate_to_human(subsystem)
        elif self.drift_score >= thresholds["recalibrate"]:
            self.recalibrate(subsystem)

    def recalibrate(self, subsystem):
        self._log_event("⚠️ Drift threshold exceeded. Initiating recalibration...", subsystem)
        self.drift_score *= 0.5  # Basic recalibration (micro-collapse after correction)
        self._log_event(f"Drift score after recalibration: {self.drift_score:.3f}", subsystem)

    def escalate_to_human(self, subsystem):
        self._log_event("🚨 Critical drift detected! Escalating to human oversight.", subsystem)

    def _log_decision(self, decision_id, compliance, drift_increment, subsystem, lucas_id):
        timestamp = datetime.datetime.now().isoformat()
        log_text = (
            f"{timestamp} | Subsystem: {subsystem} | Lucas_ID: {lucas_id} | "
            f"Decision {decision_id} | Compliance: {compliance:.3f} | Drift Increment: {drift_increment:.3f} | "
            f"Cumulative Drift Score: {self.drift_score:.3f}"
        )

        csv_row = [
            timestamp.split("T")[0],
            decision_id,
            subsystem,
            compliance,
            drift_increment,
            round(self.drift_score, 3),
            "None",
            lucas_id,
        ]
        json_entry = {
            "timestamp": timestamp,
            "decision_id": decision_id,
            "subsystem": subsystem,
            "compliance_score": compliance,
            "drift_increment": drift_increment,
            "cumulative_drift_score": round(self.drift_score, 3),
            "lucas_id": lucas_id,
        }

        self._write_log(log_text, csv_row, json_entry)

    def _log_event(self, message, subsystem=None):
        timestamp = datetime.datetime.now().isoformat()
        log_text = f"{timestamp} | {f'Subsystem: {subsystem} | ' if subsystem else ''}{message}"

        json_entry = {
            "timestamp": timestamp,
            "event": message,
            "subsystem": subsystem,
            "cumulative_drift_score": round(self.drift_score, 3),
        }

        self._write_log(log_text, None, json_entry)

    def _write_log(self, text_log, csv_row=None, json_entry=None):
        print(text_log)

        # CSV for audit trail
        if csv_row:
            new_file = not os.path.exists(self.csv_log)
            with open(self.csv_log, "a", newline="") as f_csv:
                writer = csv.writer(f_csv)
                if new_file:
                    writer.writerow(
                        [
                            "Date",
                            "Decision ID",
                            "Subsystem",
                            "Compliance Score",
                            "Drift Increment",
                            "Cumulative Drift Score",
                            "Action Taken",
                            "Lucas_ID",
                        ]
                    )
                writer.writerow(csv_row)

        # JSON for forensic narratives
        if json_entry:
            if os.path.exists(self.json_log):
                with open(self.json_log) as f_json:
                    try:
                        data = json.load(f_json)
                    except json.JSONDecodeError:
                        data = []
            else:
                data = []
            data.append(json_entry)
            with open(self.json_log, "w") as f_json:
                json.dump(data, f_json, indent=4)


# ==============================================================================
# 🔍 USAGE GUIDE (for compliance_drift_monitor.py)
#
# 1. Copy and paste this into lucas_governance/compliance_drift_monitor.py.
# 2. Example execution:
#       from lucas_governance.compliance_drift_monitor import ComplianceMonitor
#       monitor = ComplianceMonitor()
#       monitor.evaluate_decision("E001", 0.75, subsystem="emotional_oscillator", lucas_id="LUCID-001")
#
# 📂 LOG FILES:
#    - compliance_drift_logs.csv (Audit scores)
#    - compliance_drift_events.json (Narrative events)
#
# 🛡 COMPLIANCE:
#    EU AI Act | GDPR | OECD AI | ISO/IEC 27001
#
# 🏷️ GUIDE TAG:
#    #guide:compliance_drift_monitor
# ==============================================================================
