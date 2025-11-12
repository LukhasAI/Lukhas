# Restoring Archived GitHub Workflows

This document explains how to restore archived GitHub workflows using the `restore_archived_workflows.sh` script.

## Background

GitHub Actions workflows can be temporarily disabled by moving them to the `.github/workflows.archived` directory. This script provides a convenient way to restore them to the active `.github/workflows` directory.

## Usage

The script is located at `scripts/ci/restore_archived_workflows.sh`.

### Dry Run

To see a list of workflows that would be restored without actually moving any files, use the `--dry-run` flag:

```bash
./scripts/ci/restore_archived_workflows.sh --dry-run
```

This will output a list of changes, for example:

```
[Dry Run] Would move workflow-1.yml to .github/workflows
[Dry Run] Would move workflow-2.yml to .github/workflows
```

### Restoration

To restore the workflows, run the script without any arguments:

```bash
./scripts/ci/restore_archived_workflows.sh
```

This will move all `.yml` files from the archive directory to the workflows directory.
