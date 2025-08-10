"""
#ΛTRACE
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: trace_tools.py
Advanced: trace_tools.py
Integration Date: 2025-05-31T07:55:28.016528
"""

"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : trace_tools.py                                            │
│ 🧾 DESCRIPTION : Symbolic trace utility functions for auditing & dashboards│
│ 🧩 TYPE        : Utility Module           🔧 VERSION: v0.1.0                │
│ 🖋️ AUTHOR      : LUKHAS SYSTEMS           📅 UPDATED: 2025-05-05             │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - pandas                                                                │
│   - Used by: research_dashboard.py, compliance_dashboard.py               │
└────────────────────────────────────────────────────────────────────────────┘
"""


from pathlib import Path
import pandas as pd


def load_symbolic_trace_dashboard(
    csv_path="logs/symbolic_trace_dashboard.csv",
):
    """
    Load the symbolic trace CSV file with default filters.
    Returns: pandas DataFrame or None
    """
    path = Path(csv_path)
    if not path.exists():
        return None

    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[TraceTools] Failed to load symbolic trace: {e}")
        return None


def filter_trace_by_column(df, column, values):
    """
    Filter a symbolic trace DataFrame by a column and list of values.
    Returns filtered DataFrame.
    """
    if column not in df.columns:
        return df
    return df[df[column].isin(values)]


def get_summary_stats(df):
    """
    Generate basic stats from the symbolic trace log:
    - count per status
    - most flagged module
    - most common tag
    """
    if df is None or df.empty:
        return {}

    summary = {
        "status_counts": (
            df["status"].value_counts().to_dict() if "status" in df else {}
        ),
        "most_flagged_module": (
            df["module"].value_counts().idxmax() if "module" in df else None
        ),
        "most_common_tag": (df["tag"].value_counts().idxmax() if "tag" in df else None),
    }
    return summary


def export_filtered_trace_jsonl(df, out_path="logs/exported_trace.jsonl", filters=None):
    """
    Export filtered trace entries to JSONL for audit trail or cross-platform sharing.
    Args:
        df: Original DataFrame
        out_path: Destination path for JSONL file
        filters: Dict of {column: [accepted_values]} to apply before export
    """
    if filters:
        for col, vals in filters.items():
            if col in df.columns:
                df = df[df[col].isin(vals)]
    try:
        with open(out_path, "w") as f:
            for _, row in df.iterrows():
                f.write(row.to_json() + "\n")
        print(f"[TraceTools] Exported filtered trace to {out_path}")
    except Exception as e:
        print(f"[TraceTools] Failed to export JSONL: {e}")
