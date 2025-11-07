#!/bin/bash

set -e

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --module)
            MODULE="$2"
            shift
            shift
            ;; 
        --outdir)
            OUTDIR="$2"
            shift
            shift
            ;; 
        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;; 
    esac
done

if [ -z "$MODULE" ] || [ -z "$OUTDIR" ]; then
    echo "Usage: $0 --module <module_name> --outdir <output_directory>"
    exit 1
fi

ARTIFACT="$OUTDIR/$MODULE.tar.gz"
ATTESTATION="$OUTDIR/$MODULE-attestation.json"

# Create a dummy artifact for now
# In a real scenario, this would be the actual build artifact
tar -czf "$ARTIFACT" "$MODULE"

ARTIFACT_HASH=$(sha256sum "$ARTIFACT" | awk '{print $1}')

# Create in-toto link
cat > "$ATTESTATION" <<EOF
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [
    {
      "name": "$MODULE.tar.gz",
      "digest": {
        "sha256": "$ARTIFACT_HASH"
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "predicate": {
    "builder": {
      "id": "https://github.com/LukhasAI/Lukhas/.github/workflows/slsa-attest-matrix.yml@refs/heads/main"
    },
    "buildType": "https://github.com/slsa-framework/slsa-github-generator/generic@v1",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/LukhasAI/Lukhas@refs/heads/main",
        "digest": {
          "sha1": "$(git rev-parse HEAD)"
        },
        "entryPoint": ".github/workflows/slsa-attest-matrix.yml"
      }
    },
    "materials": [
      {
        "uri": "git+https://github.com/LukhasAI/Lukhas@refs/heads/main",
        "digest": {
          "sha1": "$(git rev-parse HEAD)"
        }
      }
    ]
  }
}
EOF

# Sign the attestation
cosign sign-blob --key "$COSIGN_KEY" --output-signature "$ATTESTATION.sig" "$ATTESTATION"

# For simplicity of the PoC, we'll bundle the signature inside the attestation file
# A better approach might be to keep them separate
cat >> "$ATTESTATION" <<EOF
, "signature": "$(base64 -w 0 "$ATTESTATION.sig")"
}
EOF

# A bit of a hack to make the JSON valid again
# This is because we are appending the signature to the JSON file
# A better approach would be to use a proper JSON library to add the signature
sed -i 's/}, "signature"/}, "signature"/g' "$ATTESTATION"
sed -i 's/EOF, "signature": "$(base64 -w 0 $ATTESTATION.sig)"//g' "$ATTESTATION"

# Final JSON structure adjustment
# This is a hacky way to combine the signature into the JSON. 
# In a real implementation, a proper JSON tool should be used.
# For this PoC, we'll manipulate the string to form the final JSON.
SIG_CONTENT=$(base64 -w 0 "$ATTESTATION.sig")
JSON_CONTENT=$(cat "$ATTESTATION" | sed 's/}$//') # Remove closing brace
echo "$JSON_CONTENT, \"signature\": \"$SIG_CONTENT\"}" > "$ATTESTATION"



echo "Attestation for $MODULE created at $ATTESTATION"
