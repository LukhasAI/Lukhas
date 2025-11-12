# Context File Header Automation

This document describes the `auto_update_context_headers.py` script, which is designed to automate the maintenance of YAML frontmatter in `claude.me` context files.

## Purpose

The script ensures that key metadata in the context files is always up-to-date. This is crucial for providing AI agents with the most current information about the codebase. The script automatically updates the following fields:

- `last_modified`: Sets the current UTC timestamp to indicate when the file was last processed.
- `line_count`: Records the total number of lines in the file.
- `task_completion_stats`: Calculates and records the percentage of completed tasks, sourced from the project's run manifest.

## How it Works

The script performs the following actions:

1.  **Finds Context Files**: It scans the entire repository to locate all files named `claude.me`.
2.  **Reads Task Statistics**: It dynamically finds the latest run directory within `.lukhas_runs/` (by date) and reads the `manifest_v2.json` file from there to get the most current task completion numbers.
3.  **Updates Frontmatter**: For each `claude.me` file that contains a YAML frontmatter block, the script:
    *   Parses the existing frontmatter.
    *   Updates the `last_modified`, `line_count`, and `task_completion_stats` fields.
    *   Rewrites the file with the updated frontmatter, preserving the body of the document.

## Usage

### Manual Execution

To run the script manually, execute the following command from the root of the repository:

```bash
python3 scripts/docs/auto_update_context_headers.py
```

### Pre-commit Hook

This script is intended to be integrated into a pre-commit hook. This ensures that the context file headers are automatically updated every time a commit is made, guaranteeing that the metadata remains fresh without manual intervention.
