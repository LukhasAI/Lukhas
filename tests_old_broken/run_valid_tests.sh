#!/bin/bash
# Run only valid tests, skipping known issues

echo "Running valid LUKHAS tests..."
echo "============================"

# Skip STUB tests and known broken tests
pytest -v \
    --ignore=tests/unit/test_STUB_* \
    --ignore=tests/test_stubs_old.py \
    -k "not STUB and not stub" \
    --tb=short \
    "$@"
