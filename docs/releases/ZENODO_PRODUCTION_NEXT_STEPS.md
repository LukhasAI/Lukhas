---
status: wip
type: documentation
owner: unknown
module: releases
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Zenodo Production Upload - Next Steps

**Status**: ✅ Sandbox upload successful | ⏳ Production upload pending

---

## ✅ What We've Accomplished

### Steps 1-3: Complete ✓
- [x] Checked out main branch with all Zenodo infrastructure
- [x] Verified all release files exist
- [x] Ran comprehensive validation (**7/7 checks passed**)

### Step 4: Sandbox Upload Successful ✓
- [x] Successfully uploaded to Zenodo Sandbox
- [x] Obtained sandbox DOI: `10.5072/zenodo.344725`
- [x] All 6 files uploaded correctly:
  - RELEASE_MANIFEST.json
  - T4_FINAL_SIGNATURE.sha256
  - v0.02-final-RELEASE_NOTES.md
  - T4_CLOSURE_BRIEF.md
  - T4_INFRASTRUCTURE_SUMMARY.md
  - META_REGISTRY.json
- [x] Metadata saved to: `docs/releases/v0.02-final-ZENODO.json`
- [x] Verified upload at: https://sandbox.zenodo.org/record/344725

---

## ⏳ Production Upload - Action Required

### Issue Encountered
The access token provided works for **Zenodo Sandbox** but returns `403 Permission denied` for **Production Zenodo**.

This is because:
- Sandbox tokens: https://sandbox.zenodo.org
- Production tokens: https://zenodo.org

**These are separate systems with separate tokens.**

### To Complete Production Upload

#### 1. Get Production Zenodo Token

**Go to**: https://zenodo.org (NOT sandbox)

**Steps**:
1. Log in or create account
2. Navigate to: Settings → Applications → Personal access tokens
3. Click "New token"
4. Name: `LUKHAS-AI-Production-Upload`
5. Scopes: Select **both**:
   - ☑️ `deposit:write`
   - ☑️ `deposit:actions`
6. Click "Create"
7. **Copy token immediately** (won't be shown again)

#### 2. Run Production Upload

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Set production environment
export ZENODO_API="https://zenodo.org/api"
export ZENODO_TOKEN="your-production-token-here"

# Run upload
bash scripts/release/zenodo_upload.sh
```

**When prompted**: Type `y` to confirm production upload

#### 3. Expected Output

```
🎉 Zenodo Deposition Published

Deposition ID: XXXXXX
DOI: 10.5281/zenodo.XXXXXX
Record URL: https://zenodo.org/record/XXXXXX

Citation (APA):
  Dominguez, G. (2025). LUKHΛS AI — T4/0.01% Infrastructure
  (v0.02-final) [Computer software]. Zenodo.
  https://doi.org/10.5281/zenodo.XXXXXX
```

**Save the DOI** - you'll need it for steps 5-7.

---

## 📝 Remaining Steps (After Getting Production DOI)

### Step 5: Update Documentation with DOI

```bash
# Replace XXXXXXX with your actual DOI number
DOI_NUMBER="XXXXXX"  # e.g., 789012

# Update release notes
sed -i.bak "s/10.5281\/zenodo.XXXXXXX/10.5281\/zenodo.$DOI_NUMBER/g" \
  docs/releases/v0.02-final-RELEASE_NOTES.md

# Remove backup
rm docs/releases/v0.02-final-RELEASE_NOTES.md.bak

# Verify update
grep "zenodo" docs/releases/v0.02-final-RELEASE_NOTES.md
```

**Optional**: Add DOI badge to README.md:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)
```

### Step 6: Commit Zenodo Metadata

```bash
# Stage files
git add docs/releases/v0.02-final-ZENODO.json
git add docs/releases/v0.02-final-RELEASE_NOTES.md
git add zenodo.metadata.json  # Updated to remove invalid ORCID
git add README.md  # If you added DOI badge

# Commit
git commit -m "docs(release): add Zenodo DOI metadata for v0.02-final

- Added Zenodo deposition metadata (DOI: 10.5281/zenodo.XXXXXX)
- Updated release notes with citation information
- Fixed zenodo.metadata.json (removed invalid ORCID placeholder)
- Added DOI badge to README

Published to: https://zenodo.org/record/XXXXXX

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to origin
git push origin main
```

### Step 7: Create GitHub Release

1. **Go to**: https://github.com/LukhasAI/Lukhas/releases
2. **Click**: "Draft a new release"
3. **Configure**:
   - Tag: `v0.02-final`
   - Target: `main`
   - Title: `v0.02-final - T4/0.01% Production Freeze with Complete Verification Infrastructure`

4. **Description** (copy and update DOI):

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)

## 🎯 T4/0.01% Infrastructure Release

Complete T4/0.01% quality infrastructure with cryptographic verification, 100% documentation coverage, and formal citability via Zenodo DOI.

### 📦 Release Artifacts

This release includes:
- Complete module registry (149 modules documented)
- Coverage baselines (125/149 modules, 83.9%)
- Cryptographic verification suite
- Real-time freeze monitoring
- Automated quality workflows

### 📖 Citation

\```
Dominguez, G. (2025). LUKHΛS AI — T4/0.01% Infrastructure (v0.02-final)
[Computer software]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXX
\```

### 🔐 Verification

\```bash
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
git checkout v0.02-final
sha256sum -c T4_FINAL_SIGNATURE.sha256
make validate-t4-strict
\```

### 📊 Baseline Metrics

- **Modules**: 149 (100% documented)
- **Coverage**: 83.9% (125/149 modules)
- **Health Score**: 20.3/100 (baseline)
- **Validation**: 7/7 checks passing

### 📚 Documentation

- [Release Notes](docs/releases/v0.02-final-RELEASE_NOTES.md)
- [Closure Brief](docs/T4_CLOSURE_BRIEF.md)
- [Infrastructure Summary](docs/T4_INFRASTRUCTURE_SUMMARY.md)
- [Zenodo Upload Guide](scripts/release/ZENODO_UPLOAD_GUIDE.md)

### 🏆 Achievements

✅ 100% documentation coverage
✅ Cryptographic freeze verification
✅ Real-time integrity monitoring
✅ Formally citable via Zenodo DOI
✅ Complete operational workflows
✅ Institutional-grade quality standards

**Published to Zenodo**: https://zenodo.org/record/XXXXXX
```

5. **Attach Files**:
   - RELEASE_MANIFEST.json
   - T4_FINAL_SIGNATURE.sha256
   - docs/releases/v0.02-final-RELEASE_NOTES.md
   - docs/T4_CLOSURE_BRIEF.md
   - docs/T4_INFRASTRUCTURE_SUMMARY.md
   - docs/_generated/META_REGISTRY.json

6. **Publish**: Click "Publish release" 🎉

---

## ✅ Success Criteria

Publication is complete when:

- [x] Sandbox upload successful (DONE ✓)
- [ ] Production DOI obtained
- [ ] Documentation updated with DOI
- [ ] Metadata committed to repository
- [ ] GitHub release published
- [ ] All 6 artifacts downloadable from both Zenodo and GitHub

---

## 📞 Quick Reference

### Sandbox Upload (Already Complete)
- Record: https://sandbox.zenodo.org/record/344725
- DOI: 10.5072/zenodo.344725
- Status: ✅ Published successfully

### Production Upload (Pending)
- Need: Production Zenodo token from https://zenodo.org
- Command: `bash scripts/release/zenodo_upload.sh`
- Expected: Real DOI (10.5281/zenodo.XXXXXX)

---

## 🎓 What We Validated

The sandbox upload proved:
- ✅ Metadata is valid
- ✅ All files upload correctly
- ✅ Upload script works perfectly
- ✅ Citation information generates correctly
- ✅ Workflow is smooth and automated

**Only difference for production**: Need production token instead of sandbox token.

---

**Last Updated**: 2025-10-05
**Status**: Ready for production upload with production token
**Next Action**: Get production Zenodo token from https://zenodo.org
