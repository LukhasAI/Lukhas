#!/bin/bash

# This script archives the MATRIZ migration artifacts.
# It should be run after the MATRIZ migration is complete.

set -e

# Create the migration_artifacts directory
mkdir -p migration_artifacts

# Move codemod scripts to the migration_artifacts directory
mv scripts/codemods/* migration_artifacts/

# Create the rollback documentation
cat > migration_artifacts/ROLLBACK.md <<EOL
# Rollback Plan for MATRIZ Migration

This document outlines the steps to roll back the MATRIZ migration.

## Steps

1.  **Revert the codemod scripts.**
    The codemod scripts that were archived in this directory should be moved back to their original locations.

2.  **Run the codemod scripts in reverse.**
    The codemod scripts should be run in the reverse order that they were applied.

3.  **Revert the infrastructure changes.**
    Any infrastructure changes that were made as part of the migration should be reverted.

4.  **Revert the data migrations.**
    Any data migrations that were made as part of the migration should be reverted.
EOL

echo "Migration artifacts archived to migration_artifacts/"
echo "Rollback documentation created at migration_artifacts/ROLLBACK.md"
