#!/bin/bash
# Run tests with artifact generation for self-healing test loop
set -e

# Create reports directory if it doesn't exist
mkdir -p reports

echo "Running tests with JUnit XML output..."
pytest -q --junitxml=reports/junit.xml

echo "Generating coverage XML..."
pytest --cov=. --cov-report=xml:reports/coverage.xml

echo "Normalizing JUnit XML to events..."
python tools/normalize_junit.py --in reports/junit.xml --out reports/events.ndjson

echo "Artifacts generated:"
echo "  - reports/junit.xml"
echo "  - reports/coverage.xml"
echo "  - reports/events.ndjson"
