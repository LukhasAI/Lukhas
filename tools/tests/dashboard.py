#!/usr/bin/env python3
"""
Streamlit dashboard to inspect latest pytest json report and coverage json.
Run: streamlit run tools/tests/dashboard.py
"""
import json
import os
import subprocess
import streamlit as st
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
REPORT = ROOT / "reports" / "latest" / "pytest-report.json"
COV = ROOT / "reports" / "coverage" / "coverage.json"

st.set_page_config(page_title="LUKHΛS Test Dashboard", layout="wide")

def load_pytest():
    if not REPORT.exists():
        return None
    with REPORT.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def load_cov():
    if not COV.exists():
        return None
    with COV.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def run_pytest(target=None):
    cmd = ["pytest", "--json-report", "--json-report-file=reports/latest/pytest-report.json", "-q"]
    if target:
        cmd = ["pytest", target, "-q", "--json-report", "--json-report-file=reports/latest/pytest-report.json"]
    st.info("Running: " + " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc

st.title("LUKHΛS Tests & Coverage")
pytest_data = load_pytest()
cov_data = load_cov()

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Test Summary")
    if pytest_data:
        totals = pytest_data.get("summary", {})
        st.metric("Total tests", totals.get("total", "N/A"))
        st.metric("Passed", totals.get("passed", "N/A"))
        st.metric("Failed", totals.get("failed", "N/A"))
        st.metric("Skipped", totals.get("skipped", "N/A"))
        st.write("Duration:", pytest_data.get("duration", "N/A"))
        # list of tests
        rows = []
        for item in pytest_data.get("tests", []):
            rows.append([item.get("nodeid"), item.get("outcome"), item.get("duration")])
        st.table(rows[:200])
    else:
        st.warning("No pytest JSON report found. Run tests below.")

    st.button("Run full test suite", on_click=lambda: st.rerun() if run_pytest() and True else None)

with col2:
    st.header("Coverage Summary")
    if cov_data:
        totals = cov_data.get("totals", {})
        st.metric("Overall percent covered", f"{totals.get('percent_covered', 0)}%")
        st.write("Total statements", totals.get("num_statements"))
        # per-file simple table
        file_rows = []
        fdict = cov_data.get("files", {})
        for fp, info in sorted(fdict.items(), key=lambda x: -x[1].get("percent_covered", 0)):
            file_rows.append([fp, info.get("percent_covered"), info.get("executed_lines") and len(info.get("executed_lines"))])
        st.table(file_rows[:200])
    else:
        st.warning("No coverage json found.")

st.header("Run selective tests")
target = st.text_input("pytest target (file or nodeid, leave empty for all)", value="")
if st.button("Run pytest target"):
    proc = run_pytest(target=target if target else None)
    st.text(proc.stdout)
    st.error(proc.stderr)
    st.rerun()
