#!/bin/bash
#
# IPLD CAR Generation Demo
#
# Creates a content-addressed archive from run provenance data.
# This demonstrates the provenance track for audit-heavy modules.

set -e

INPUT="sample_run.json"
OUTPUT="sample_run.car"

echo "🔗 Generating IPLD CAR for provenance demo..."
echo "Input: $INPUT"
echo "Output: $OUTPUT"
echo

# Check if we have the LUKHAS CAR generator
if [ -f "../../../tools/generate_car.py" ]; then
    echo "✅ Using LUKHAS generate_car.py tool"

    # Create artifacts dir if it doesn't exist
    mkdir -p ../../../artifacts

    # Generate CAR with the real tool
    python3 ../../../tools/generate_car.py \
        --module memory \
        --gates "$INPUT"

    # Copy the generated CAR to local directory for verification
    # Check local artifacts directory first (created by generate_car.py)
    LATEST_CAR=$(ls -t artifacts/memory_provenance_*.car 2>/dev/null | head -1)
    if [ -f "$LATEST_CAR" ]; then
        cp "$LATEST_CAR" "$OUTPUT"
        echo "📦 CAR copied to local directory: $OUTPUT"
    else
        # Fallback to main artifacts directory
        LATEST_CAR_MAIN=$(ls -t ../../../artifacts/memory_provenance_*.car 2>/dev/null | head -1)
        if [ -f "$LATEST_CAR_MAIN" ]; then
            cp "$LATEST_CAR_MAIN" "$OUTPUT"
            echo "📦 CAR copied from main artifacts: $OUTPUT"
        else
            echo "❌ Could not find generated CAR file"
        fi
    fi
else
    # Fallback: create mock CAR file
    echo "🧪 Creating mock CAR (install tools/generate_car.py for real implementation)"

    # Generate mock CID
    MOCK_CID="bafybei$(echo -n "$(cat $INPUT)" | shasum -a 256 | cut -c1-52)"

    # Create mock CAR structure
    cat > "$OUTPUT" << EOF
{
  "version": 1,
  "roots": ["$MOCK_CID"],
  "blocks": [
    {
      "cid": "$MOCK_CID",
      "data": $(cat "$INPUT")
    }
  ],
  "metadata": {
    "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tool": "demo_generate_car.sh"
  }
}
EOF
fi

echo
echo "🎯 CAR file created!"
echo "   Next step: ./verify_car.sh"
echo "   Production: Pin to IPFS with 'ipfs add $OUTPUT'"