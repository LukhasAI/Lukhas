#!/bin/bash
#
# PRISM Verification Demo
#
# Run this to verify memory cascade prevention property.
# Expected: Property is satisfied (≥99.7% probability)

set -e

MODEL="demo_memory_cascade.pm"
PROPERTY="P>=0.997 [F \"safe_operation\"]"

echo "🔮 Running PRISM verification demo..."
echo "Model: $MODEL"
echo "Property: $PROPERTY"
echo

if ! command -v prism &> /dev/null; then
    echo "❌ PRISM not found. Install with:"
    echo "   macOS: brew install prism-model-checker"
    echo "   Linux: apt-get install prism"
    echo "   Or download from: https://www.prismmodelchecker.org/download.php"
    echo
    echo "🧪 Mock result (install PRISM for real verification):"
    cat expected_output.txt
    exit 0
fi

echo "✅ PRISM found, running verification..."
prism "$MODEL" -prop "$PROPERTY"

echo
echo "🎯 If property is satisfied, your verification track is working!"
echo "   Add this model to your module's models/ directory"
echo "   Update your matrix contract with: 'formal.probabilistic.properties'"