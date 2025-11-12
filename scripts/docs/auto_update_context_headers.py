#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automates the update of context file headers.

This script updates the following fields in the YAML frontmatter of all
'claude.me' context files:
- Last-Modified timestamp
- Line count
- Task completion statistics
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
import yaml

# Mock missing lukhas module for now
try:
    from lukhas.common.utils import get_project_root
except ImportError:
    def get_project_root():
        """A simple fallback for finding the git repo root."""
        path = os.getcwd()
        while path != os.path.dirname(path):
            if ".git" in os.listdir(path):
                return path
            path = os.path.dirname(path)
        return None

# --- Constants ---
CONTEXT_FILENAME = "claude.me"
RUNS_DIR = ".lukhas_runs"
MANIFEST_FILENAME = "manifest_v2.json"
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def find_latest_manifest(project_root):
    """Finds the most recent manifest_v2.json in the .lukhas_runs directory."""
    runs_path = os.path.join(project_root, RUNS_DIR)
    latest_run_dir = None
    latest_date = None

    if not os.path.isdir(runs_path):
        return None

    for dirname in os.listdir(runs_path):
        dir_path = os.path.join(runs_path, dirname)
        if os.path.isdir(dir_path):
            try:
                run_date = datetime.strptime(dirname, '%Y-%m-%d')
                if latest_date is None or run_date > latest_date:
                    manifest_path = os.path.join(dir_path, MANIFEST_FILENAME)
                    if os.path.exists(manifest_path):
                        latest_date = run_date
                        latest_run_dir = dir_path
            except ValueError:
                # Ignore directories that don't match the date format
                continue

    if latest_run_dir:
        return os.path.join(latest_run_dir, MANIFEST_FILENAME)
    return None

def find_context_files(root_dir):
    """Finds all 'claude.me' files in the given directory."""
    context_files = []
    for root, _, files in os.walk(root_dir):
        if CONTEXT_FILENAME in files:
            context_files.append(os.path.join(root, CONTEXT_FILENAME))
    return context_files

def get_task_completion_stats(manifest_path):
    """Reads and calculates task completion stats from the manifest."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)

        stats = manifest_data.get("stats", {}).get("by_status", {})
        completed = stats.get("completed", 0)
        total = stats.get("open", 0) + completed

        percentage = (completed / total * 100) if total > 0 else 0
        return f"{completed}/{total} ({percentage:.1f}%)"
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error reading or parsing manifest file {manifest_path}: {e}", file=sys.stderr)
        return "N/A"

def update_file_header(file_path, stats_string):
    """Updates the YAML frontmatter of a single context file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        line_count = len(content.splitlines())
        last_modified_timestamp = datetime.now(timezone.utc).isoformat()

        match = FRONTMATTER_RE.match(content)
        if not match:
            print(f"Warning: No YAML frontmatter found in {file_path}. Skipping.", file=sys.stderr)
            return

        frontmatter_str = match.group(1)
        body = content[match.end():]

        try:
            frontmatter_data = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError as e:
            print(f"Warning: Could not parse YAML in {file_path}. Skipping. Error: {e}", file=sys.stderr)
            return

        frontmatter_data['last_modified'] = last_modified_timestamp
        frontmatter_data['line_count'] = line_count
        frontmatter_data['task_completion_stats'] = stats_string

        updated_frontmatter_str = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False)
        updated_content = f"---\n{updated_frontmatter_str}---\n{body}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"Updated header for: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}", file=sys.stderr)

def main():
    """Main function to update context file headers."""
    print("Starting context header update...")

    project_root = get_project_root()
    if not project_root:
        print("Error: Could not determine project root. Aborting.", file=sys.stderr)
        sys.exit(1)

    latest_manifest_path = find_latest_manifest(project_root)
    if not latest_manifest_path:
        print(f"Error: No '{MANIFEST_FILENAME}' found in any subdirectory of '{RUNS_DIR}'. Aborting.", file=sys.stderr)
        sys.exit(1)

    print(f"Using latest manifest: {latest_manifest_path}")
    task_stats = get_task_completion_stats(latest_manifest_path)

    context_files = find_context_files(project_root)
    print(f"Found {len(context_files)} context files to update.")

    for file_path in context_files:
        update_file_header(file_path, task_stats)

    print("Context header update complete.")

if __name__ == "__main__":
    main()
