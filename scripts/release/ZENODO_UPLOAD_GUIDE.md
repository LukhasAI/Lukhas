---
status: wip
type: documentation
---
# Zenodo Upload Guide - LUKHAS AI T4/0.01% Infrastructure

**Purpose**: Step-by-step guide for publishing LUKHAS AI releases to Zenodo for long-term archival and citability.

**Target Audience**: Release managers, maintainers, and contributors responsible for creating citable software releases.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Sandbox Testing](#sandbox-testing)
4. [Production Upload](#production-upload)
5. [Post-Publication Steps](#post-publication-steps)
6. [Versioning Strategy](#versioning-strategy)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Zenodo is a free, open-access research repository developed by CERN that provides:
- **Persistent DOIs** for software releases
- **Long-term archival** (minimum 20 years)
- **Version tracking** with concept DOIs
- **Citability** for academic work
- **Discovery** through indexing and search

This guide covers the complete workflow for publishing LUKHAS AI releases to Zenodo, making them citable and preserving them for posterity.

---

## 📋 Prerequisites

### 1. Zenodo Account

**Sandbox (Testing)**:
- Create account: https://sandbox.zenodo.org
- Purpose: Test uploads without affecting production
- Data retention: 30 days

**Production**:
- Create account: https://zenodo.org
- Purpose: Permanent, citable releases
- Data retention: Minimum 20 years

### 2. Personal Access Token

1. Log in to Zenodo (sandbox or production)
2. Go to: Settings → Applications → Personal access tokens
3. Click "New token"
4. Name: `LUKHAS-AI-Upload` (or similar)
5. Scopes: Select `deposit:write` and `deposit:actions`
6. Click "Create"
7. **Copy the token immediately** (it won't be shown again)

### 3. Environment Setup

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Zenodo tokens
export ZENODO_SANDBOX_TOKEN="your-sandbox-token-here"
export ZENODO_PRODUCTION_TOKEN="your-production-token-here"
```

Then reload: `source ~/.bashrc` or `source ~/.zshrc`

### 4. Release Artifacts

Ensure all release files exist:

```bash
cd /path/to/Lukhas

# Check required files
ls -lh RELEASE_MANIFEST.json
ls -lh T4_FINAL_SIGNATURE.sha256
ls -lh docs/releases/v0.02-final-RELEASE_NOTES.md
ls -lh docs/T4_CLOSURE_BRIEF.md
ls -lh docs/T4_INFRASTRUCTURE_SUMMARY.md
ls -lh docs/_generated/META_REGISTRY.json
```

All files should exist before proceeding.

---

## 🧪 Sandbox Testing

**Always test on sandbox first** to verify the upload workflow before publishing to production.

### Step 1: Configure Sandbox Environment

```bash
cd /path/to/Lukhas

export ZENODO_API="https://sandbox.zenodo.org/api"
export ZENODO_TOKEN="$ZENODO_SANDBOX_TOKEN"
```

### Step 2: Verify Metadata

Review `zenodo.metadata.json`:

```bash
cat zenodo.metadata.json | python3 -m json.tool
```

Check:
- ✅ Version matches release tag (e.g., `v0.02-final`)
- ✅ Publication date is correct
- ✅ License is correct (default: MIT)
- ✅ Creators/contributors are accurate
- ✅ Related identifiers point to correct URLs

### Step 3: Run Upload Script

```bash
bash scripts/release/zenodo_upload.sh zenodo.metadata.json
```

**Expected Output**:

```
ℹ Validating environment...
✓ Metadata file found: zenodo.metadata.json
✓ All release files found (6 files)
⚠ Using SANDBOX environment: https://sandbox.zenodo.org/api
Continue with sandbox? (y/N) y
ℹ Creating Zenodo deposition...
✓ Created deposition: 12345
ℹ Uploading 6 files...
  ℹ Uploading: RELEASE_MANIFEST.json
  ✓ RELEASE_MANIFEST.json
  ℹ Uploading: T4_FINAL_SIGNATURE.sha256
  ✓ T4_FINAL_SIGNATURE.sha256
  ...
✓ All files uploaded successfully
ℹ Publishing deposition...
✓ Published successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Zenodo Deposition Published
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deposition ID: 12345
DOI: 10.5072/zenodo.12345
Record URL: https://sandbox.zenodo.org/record/12345
```

### Step 4: Verify Sandbox Deposition

1. Open the Record URL from the output
2. Check all files are present and downloadable
3. Verify metadata display is correct
4. Review citation format

**If issues found**:
- Delete the sandbox deposition
- Fix metadata/files
- Re-upload to sandbox

**If everything looks good**:
- Proceed to production upload

---

## 🚀 Production Upload

**WARNING**: Production uploads are **permanent and immutable**. Once published, you cannot:
- Delete the deposition
- Edit the metadata (only additions allowed)
- Remove uploaded files

### Step 1: Final Pre-Flight Checks

```bash
cd /path/to/Lukhas

# Ensure on correct tag
git checkout v0.02-final

# Verify freeze integrity
make freeze-verify

# Run full validation
make validate-t4-strict

# Verify all artifacts exist
ls -lh RELEASE_MANIFEST.json T4_FINAL_SIGNATURE.sha256 \
  docs/releases/v0.02-final-RELEASE_NOTES.md \
  docs/T4_CLOSURE_BRIEF.md \
  docs/T4_INFRASTRUCTURE_SUMMARY.md \
  docs/_generated/META_REGISTRY.json
```

**All checks must pass** before proceeding.

### Step 2: Configure Production Environment

```bash
export ZENODO_API="https://zenodo.org/api"
export ZENODO_TOKEN="$ZENODO_PRODUCTION_TOKEN"
```

### Step 3: Upload to Production

```bash
bash scripts/release/zenodo_upload.sh zenodo.metadata.json
```

The script will ask for confirmation:

```
ℹ Using PRODUCTION environment: https://zenodo.org/api
This will publish to production Zenodo. Continue? (y/N)
```

Type `y` and press Enter.

### Step 4: Verify Production Deposition

**Expected Output**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Zenodo Deposition Published
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deposition ID: 789012
DOI: 10.5281/zenodo.789012
Record URL: https://zenodo.org/record/789012

Citation (APA):
  Dominguez, G. (2025). LUKHΛS AI — T4/0.01% Infrastructure
  (v0.02-final) [Computer software]. Zenodo.
  https://doi.org/10.5281/zenodo.789012

Badge (Markdown):
  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.789012.svg)](https://doi.org/10.5281/zenodo.789012)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Save these details** - you'll need them for post-publication steps.

---

## 📝 Post-Publication Steps

### Step 1: Update Release Notes

The upload script automatically saves metadata to `docs/releases/v0.02-final-ZENODO.json`.

Update `docs/releases/v0.02-final-RELEASE_NOTES.md`:

```bash
# Replace placeholder with actual DOI
sed -i.bak 's/10.5281\/zenodo.XXXXXXX/10.5281\/zenodo.789012/g' \
  docs/releases/v0.02-final-RELEASE_NOTES.md

# Remove backup
rm docs/releases/v0.02-final-RELEASE_NOTES.md.bak
```

### Step 2: Add DOI Badge to README

Add to the top of `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.789012.svg)](https://doi.org/10.5281/zenodo.789012)
```

### Step 3: Commit Metadata

```bash
git add docs/releases/v0.02-final-ZENODO.json
git add docs/releases/v0.02-final-RELEASE_NOTES.md
git add README.md

git commit -m "docs(release): add Zenodo DOI metadata for v0.02-final

- Added Zenodo deposition metadata
- Updated release notes with DOI citation
- Added DOI badge to README

DOI: 10.5281/zenodo.789012

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### Step 4: Update GitHub Release

1. Go to: https://github.com/LukhasAI/Lukhas/releases/tag/v0.02-final
2. Click "Edit release"
3. Add DOI badge to description:
   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.789012.svg)](https://doi.org/10.5281/zenodo.789012)
   ```
4. Add citation information
5. Click "Update release"

---

## 🔄 Versioning Strategy

Zenodo provides two types of DOIs:

### 1. Version DOI (Specific Release)

Each release gets its own DOI:
- `v0.02-final` → `10.5281/zenodo.789012`
- `v0.03-final` → `10.5281/zenodo.789013`
- `v0.04-final` → `10.5281/zenodo.789014`

**Use for**: Citing a specific version in papers

### 2. Concept DOI (All Versions)

Zenodo automatically creates a concept DOI that always points to the **latest** version:
- Concept DOI: `10.5281/zenodo.789011`
- Always resolves to latest release

**Use for**: General citations, README badges, documentation

### Publishing New Versions

For `v0.03-final`:

1. Update `zenodo.metadata.json`:
   ```json
   {
     "metadata": {
       "version": "v0.03-final",
       "publication_date": "2025-11-15",
       ...
     }
   }
   ```

2. Prepare new release artifacts

3. Run upload script (same process)

4. Zenodo will:
   - Create new version DOI
   - Link to previous versions
   - Update concept DOI to point to v0.03

---

## 🔧 Troubleshooting

### Issue: "Failed to create deposition"

**Cause**: Invalid metadata or authentication

**Solution**:
1. Validate JSON: `cat zenodo.metadata.json | python3 -m json.tool`
2. Check token is set: `echo $ZENODO_TOKEN`
3. Verify token has `deposit:write` scope
4. Check API endpoint: `echo $ZENODO_API`

### Issue: "Failed to upload file"

**Cause**: File doesn't exist or permission denied

**Solution**:
1. Check file exists: `ls -lh RELEASE_MANIFEST.json`
2. Check file permissions: `chmod 644 RELEASE_MANIFEST.json`
3. Try absolute path in `FILES` array

### Issue: "Failed to publish deposition"

**Cause**: Required metadata fields missing

**Solution**:
1. Check metadata has all required fields:
   - `upload_type`
   - `publication_date`
   - `title`
   - `creators` (with name)
   - `description`
   - `access_right`
2. Review Zenodo API error message
3. Fix metadata and upload to sandbox first

### Issue: "Token expired or invalid"

**Cause**: Personal access token expired

**Solution**:
1. Go to Zenodo → Settings → Applications
2. Revoke old token
3. Create new token with same scopes
4. Update `ZENODO_TOKEN` environment variable

### Issue: Uploaded wrong files

**Cause**: Files array in script has incorrect paths

**Solution**:
- **Sandbox**: Delete deposition and re-upload
- **Production**: You cannot delete. Options:
  1. Create new version with correct files
  2. Contact Zenodo support to request deletion (rare cases only)

### Issue: Need to update metadata after publication

**Cause**: Metadata error noticed after publication

**Solution**:
- **Production**: You can only **add** metadata, not edit/delete
- Options:
  1. Use Zenodo UI to add missing information
  2. Create new version with corrected metadata
  3. Contact Zenodo support for critical issues

---

## 📞 Support Resources

### Zenodo Documentation
- User Guide: https://help.zenodo.org
- API Documentation: https://developers.zenodo.org
- Upload Guide: https://help.zenodo.org/#upload

### LUKHAS AI Support
- Release Issues: https://github.com/LukhasAI/Lukhas/issues
- Maintenance Guide: [POST_FREEZE_MAINTENANCE.md](../../docs/POST_FREEZE_MAINTENANCE.md)
- Closure Brief: [T4_CLOSURE_BRIEF.md](../../docs/T4_CLOSURE_BRIEF.md)

### Contact
- Zenodo Support: info@zenodo.org
- GitHub Issues: Tag release manager

---

## ✅ Checklist

Before uploading to production:

- [ ] Tested upload on sandbox successfully
- [ ] Verified all files exist and are correct
- [ ] Ran `make freeze-verify` (all checks pass)
- [ ] Ran `make validate-t4-strict` (8/8 checks pass)
- [ ] Reviewed metadata for accuracy
- [ ] Updated ORCID if applicable
- [ ] Confirmed license is correct
- [ ] Verified related URLs point to correct locations
- [ ] Have production token with correct scopes

After publication:

- [ ] Saved DOI from output
- [ ] Updated release notes with DOI
- [ ] Added DOI badge to README
- [ ] Committed Zenodo metadata file
- [ ] Updated GitHub release description
- [ ] Verified Zenodo record is accessible
- [ ] Tested file downloads from Zenodo
- [ ] Added concept DOI to documentation

---

## 🎓 Best Practices

### Metadata Quality
- Use consistent naming across versions
- Include comprehensive keywords for discoverability
- Link to GitHub releases and repository
- Add detailed description with verification instructions

### File Selection
- Only include essential release artifacts
- Keep total size reasonable (<100MB ideal)
- Include verification files (checksums, signatures)
- Add comprehensive documentation

### Versioning
- Use semantic versioning (e.g., v0.02-final)
- Publish major milestones, not every commit
- Update concept DOI in documentation after each release

### Documentation
- Always include release notes
- Add citation information to README
- Link from GitHub release to Zenodo record
- Document verification procedures

---

## 📊 Release Artifacts Inventory

For v0.02-final, the following files are included in Zenodo deposition:

| File | Size | Description |
|------|------|-------------|
| `RELEASE_MANIFEST.json` | ~15KB | Complete package metadata |
| `T4_FINAL_SIGNATURE.sha256` | ~3KB | Cryptographic signatures |
| `v0.02-final-RELEASE_NOTES.md` | ~10KB | Release notes |
| `T4_CLOSURE_BRIEF.md` | ~15KB | Handoff documentation |
| `T4_INFRASTRUCTURE_SUMMARY.md` | ~20KB | Architecture overview |
| `META_REGISTRY.json` | ~56KB | Unified analytics |

**Total**: ~119KB

All files are under version control and cryptographically verified via `T4_FINAL_SIGNATURE.sha256`.

---

## 🏆 Success Criteria

A successful Zenodo publication should have:

✅ **Persistent DOI** assigned
✅ **All files** downloadable
✅ **Metadata** complete and accurate
✅ **Citation** information correct
✅ **Verification** instructions included
✅ **Badge** added to README
✅ **GitHub release** linked to Zenodo record
✅ **Documentation** updated with DOI

---

**Last Updated**: 2025-10-05
**Version**: 1.0.0
**Maintainer**: LUKHAS AI Engineering Team
