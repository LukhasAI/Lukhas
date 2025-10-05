#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# Zenodo Upload Script for v0.02-final
# ==========================================
#
# Purpose: Upload LUKHAS AI T4/0.01% infrastructure release to Zenodo
#
# Usage:
#   1. Test on sandbox first:
#      export ZENODO_API="https://sandbox.zenodo.org/api"
#      export ZENODO_TOKEN="your-sandbox-token"
#      bash scripts/release/zenodo_upload.sh
#
#   2. Production upload:
#      export ZENODO_API="https://zenodo.org/api"
#      export ZENODO_TOKEN="your-production-token"
#      bash scripts/release/zenodo_upload.sh
#
# Prerequisites:
#   - Zenodo account (https://zenodo.org or https://sandbox.zenodo.org)
#   - Personal access token (Settings → Applications → New token)
#   - Environment variables: ZENODO_API, ZENODO_TOKEN
#
# Output:
#   - Deposition ID
#   - DOI (after publication)
#   - Zenodo record URL

# --- CONFIG ---
ZENODO_API="${ZENODO_API:-https://zenodo.org/api}"
TOKEN="${ZENODO_TOKEN:?Error: Set ZENODO_TOKEN environment variable}"
META_FILE="${1:-zenodo.metadata.json}"

# Files to attach to deposition
FILES=(
  "RELEASE_MANIFEST.json"
  "T4_FINAL_SIGNATURE.sha256"
  "docs/releases/v0.02-final-RELEASE_NOTES.md"
  "docs/T4_CLOSURE_BRIEF.md"
  "docs/T4_INFRASTRUCTURE_SUMMARY.md"
  "docs/_generated/META_REGISTRY.json"
)

# --- COLORS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- HELPER FUNCTIONS ---
log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

# --- VALIDATION ---
log_info "Validating environment..."

# Check if metadata file exists
if [[ ! -f "$META_FILE" ]]; then
  log_error "Metadata file not found: $META_FILE"
  exit 1
fi
log_success "Metadata file found: $META_FILE"

# Check if all files exist
MISSING_FILES=()
for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    MISSING_FILES+=("$f")
  fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
  log_error "Missing release files:"
  for f in "${MISSING_FILES[@]}"; do
    echo "  - $f"
  done
  exit 1
fi
log_success "All release files found (${#FILES[@]} files)"

# Check API endpoint
if [[ "$ZENODO_API" == *"sandbox"* ]]; then
  log_warning "Using SANDBOX environment: $ZENODO_API"
  echo -n "Continue with sandbox? (y/N) "
  read -r response
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
else
  log_info "Using PRODUCTION environment: $ZENODO_API"
  echo -n "This will publish to production Zenodo. Continue? (y/N) "
  read -r response
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# --- CREATE DEPOSITION ---
log_info "Creating Zenodo deposition..."

DEPOSITION=$(curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$ZENODO_API/deposit/depositions" \
  -d @"$META_FILE")

# Check for errors
if echo "$DEPOSITION" | grep -q '"status": 400'; then
  log_error "Failed to create deposition"
  echo "$DEPOSITION" | python3 -m json.tool
  exit 1
fi

# Extract deposition ID
ID=$(echo "$DEPOSITION" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])' 2>/dev/null || echo "")

if [[ -z "$ID" ]]; then
  log_error "Failed to extract deposition ID"
  echo "$DEPOSITION"
  exit 1
fi

log_success "Created deposition: $ID"

# Extract bucket URL for file uploads
BUCKET_URL=$(echo "$DEPOSITION" | python3 -c 'import sys,json;print(json.load(sys.stdin)["links"]["bucket"])' 2>/dev/null || echo "")

if [[ -z "$BUCKET_URL" ]]; then
  log_warning "Using legacy file upload API"
  UPLOAD_URL="$ZENODO_API/deposit/depositions/$ID/files"
else
  log_info "Using bucket upload API: $BUCKET_URL"
  UPLOAD_URL="$BUCKET_URL"
fi

# --- UPLOAD FILES ---
log_info "Uploading ${#FILES[@]} files..."

for f in "${FILES[@]}"; do
  filename=$(basename "$f")
  log_info "  Uploading: $filename"

  if [[ -n "$BUCKET_URL" ]]; then
    # New bucket API
    curl -s -H "Authorization: Bearer $TOKEN" \
      --upload-file "$f" \
      "$BUCKET_URL/$filename" >/dev/null
  else
    # Legacy API
    curl -s -H "Authorization: Bearer $TOKEN" \
      -F "file=@${f}" \
      "$ZENODO_API/deposit/depositions/$ID/files" >/dev/null
  fi

  log_success "  ✓ $filename"
done

log_success "All files uploaded successfully"

# --- PUBLISH ---
log_info "Publishing deposition..."

PUBLISH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  -X POST "$ZENODO_API/deposit/depositions/$ID/actions/publish")

# Check for errors
if echo "$PUBLISH_RESPONSE" | grep -q '"status": 400'; then
  log_error "Failed to publish deposition"
  echo "$PUBLISH_RESPONSE" | python3 -m json.tool
  exit 1
fi

# Extract DOI
DOI=$(echo "$PUBLISH_RESPONSE" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("doi", ""))' 2>/dev/null || echo "")
RECORD_URL=$(echo "$PUBLISH_RESPONSE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["links"]["record_html"])' 2>/dev/null || echo "")

log_success "Published successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Zenodo Deposition Published${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Deposition ID: ${BLUE}$ID${NC}"
if [[ -n "$DOI" ]]; then
  echo -e "DOI: ${BLUE}$DOI${NC}"
fi
if [[ -n "$RECORD_URL" ]]; then
  echo -e "Record URL: ${BLUE}$RECORD_URL${NC}"
fi
echo ""
echo "Citation (APA):"
echo "  Dominguez, G. (2025). LUKHΛS AI — T4/0.01% Infrastructure"
echo "  (v0.02-final) [Computer software]. Zenodo."
if [[ -n "$DOI" ]]; then
  echo "  https://doi.org/$DOI"
fi
echo ""
echo "Badge (Markdown):"
if [[ -n "$DOI" ]]; then
  echo "  [![DOI](https://zenodo.org/badge/DOI/$DOI.svg)](https://doi.org/$DOI)"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# --- SAVE METADATA ---
METADATA_OUTPUT="docs/releases/v0.02-final-ZENODO.json"
echo "$PUBLISH_RESPONSE" | python3 -m json.tool > "$METADATA_OUTPUT" 2>/dev/null || true

if [[ -f "$METADATA_OUTPUT" ]]; then
  log_success "Metadata saved to: $METADATA_OUTPUT"
  echo ""
  echo "Next steps:"
  echo "  1. Add DOI badge to README.md"
  echo "  2. Update citation in documentation"
  echo "  3. Commit metadata file: git add $METADATA_OUTPUT"
  echo "  4. (Optional) Create new version for v0.03 later"
fi
