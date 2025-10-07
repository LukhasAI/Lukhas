---
status: wip
type: documentation
owner: unknown
module: releases
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Zenodo Publication Checklist - v0.02-final

**Purpose**: Step-by-step execution guide for publishing v0.02-final to Zenodo with DOI

**Target**: Complete steps 1-7 for formal publication and external citability

---

## 📋 Pre-Publication Checklist

Before starting, ensure you have:

- [ ] Zenodo account created (https://zenodo.org)
- [ ] Personal access token generated (Settings → Applications → New token)
- [ ] Token scopes: `deposit:write` and `deposit:actions`
- [ ] Token saved to environment: `export ZENODO_TOKEN="your-token"`
- [ ] All commits pushed to main branch
- [ ] v0.02-final tag created (if not already done)

---

## 🚀 Publication Steps (1-7)

### Step 1: Checkout v0.02-final tag

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout v0.02-final
```

**Verification**:
```bash
git describe --tags
# Expected output: v0.02-final

git rev-parse HEAD
# Expected: matches v0.02-final commit SHA
```

**Status**: ⬜ Not started | ✅ Complete

---

### Step 2: Verify cryptographic signatures

```bash
sha256sum -c T4_FINAL_SIGNATURE.sha256
```

**Expected Output**:
```
RELEASE_MANIFEST.json: OK
T4_FINAL_SIGNATURE.sha256: OK
docs/releases/v0.02-final-RELEASE_NOTES.md: OK
docs/T4_CLOSURE_BRIEF.md: OK
docs/T4_INFRASTRUCTURE_SUMMARY.md: OK
docs/_generated/META_REGISTRY.json: OK
... (all files should show OK)
```

**If any file shows FAILED**:
- Stop immediately
- Investigate integrity violation
- Do NOT proceed to Zenodo upload
- Review freeze verification logs

**Status**: ⬜ Not started | ✅ Complete

---

### Step 3: Run comprehensive validation

```bash
make validate-t4-strict
```

**Expected Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 T4/0.01% Validation Checkpoint
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Check 1/8: MODULE_REGISTRY exists and is valid JSON
✅ Check 2/8: META_REGISTRY exists and is valid JSON
✅ Check 3/8: Coverage ledger exists and contains 125 entries
✅ Check 4/8: Benchmark ledger exists
✅ Check 5/8: Trend files generated successfully
✅ Check 6/8: Module count matches: 149
✅ Check 7/8: Average health score: 20.3/100
✅ Check 8/8: All validation checks passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All 8/8 validation checks passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If any check fails**:
- Review failure details
- Fix issues before proceeding
- Re-run validation until 8/8 pass

**Status**: ⬜ Not started | ✅ Complete

---

### Step 4: Upload to Zenodo

#### 4a. Set Zenodo token

```bash
export ZENODO_TOKEN="your-production-token-here"
export ZENODO_API="https://zenodo.org/api"
```

**Verify environment**:
```bash
echo $ZENODO_TOKEN
# Should output your token

echo $ZENODO_API
# Should output: https://zenodo.org/api
```

#### 4b. Run upload script

```bash
bash scripts/release/zenodo_upload.sh
```

**Expected Interaction**:
```
ℹ Validating environment...
✓ Metadata file found: zenodo.metadata.json
✓ All release files found (6 files)
ℹ Using PRODUCTION environment: https://zenodo.org/api
This will publish to production Zenodo. Continue? (y/N)
```

**Type `y` and press Enter**

**Expected Output**:
```
ℹ Creating Zenodo deposition...
✓ Created deposition: 789012
ℹ Uploading 6 files...
  ✓ RELEASE_MANIFEST.json
  ✓ T4_FINAL_SIGNATURE.sha256
  ✓ v0.02-final-RELEASE_NOTES.md
  ✓ T4_CLOSURE_BRIEF.md
  ✓ T4_INFRASTRUCTURE_SUMMARY.md
  ✓ META_REGISTRY.json
✓ All files uploaded successfully
ℹ Publishing deposition...
✓ Published successfully!

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

✓ Metadata saved to: docs/releases/v0.02-final-ZENODO.json
```

#### 4c. Save DOI information

**Copy and save these values**:
- Deposition ID: `_____________`
- DOI: `10.5281/zenodo._____________`
- Record URL: `_____________`
- Badge Markdown: `_____________`

**Status**: ⬜ Not started | ✅ Complete

---

### Step 5: Update documentation with DOI

#### 5a. Wait for DOI confirmation

**Verify Zenodo record**:
1. Open the Record URL from Step 4
2. Confirm all 6 files are downloadable
3. Verify metadata is correct
4. Confirm DOI is active

#### 5b. Update release notes

```bash
# Replace XXXXXXX with actual DOI (e.g., 789012)
sed -i.bak 's/10.5281\/zenodo.XXXXXXX/10.5281\/zenodo.789012/g' \
  docs/releases/v0.02-final-RELEASE_NOTES.md

# Remove backup file
rm docs/releases/v0.02-final-RELEASE_NOTES.md.bak
```

**Manual verification**:
```bash
grep "zenodo" docs/releases/v0.02-final-RELEASE_NOTES.md
# Should show updated DOI, not XXXXXXX
```

#### 5c. Update README (if badge needed)

Add to top of README.md:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.789012.svg)](https://doi.org/10.5281/zenodo.789012)
```

**Status**: ⬜ Not started | ✅ Complete

---

### Step 6: Commit Zenodo metadata

```bash
# Stage files
git add docs/releases/v0.02-final-ZENODO.json
git add docs/releases/v0.02-final-RELEASE_NOTES.md
git add README.md  # if you added DOI badge

# Commit with proper message
git commit -m "docs(release): add Zenodo DOI metadata for v0.02-final

- Added Zenodo deposition metadata (DOI: 10.5281/zenodo.789012)
- Updated release notes with citation information
- Added DOI badge to README

Published to: https://zenodo.org/record/789012

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to main
git push origin main
```

**Verification**:
```bash
git log --oneline -1
# Should show your Zenodo DOI commit

git status
# Should show "nothing to commit, working tree clean"
```

**Status**: ⬜ Not started | ✅ Complete

---

### Step 7: Create GitHub Release

#### 7a. Navigate to GitHub releases

1. Go to: https://github.com/LukhasAI/Lukhas/releases
2. Click "Draft a new release"

#### 7b. Configure release

**Tag**: `v0.02-final`
**Target**: `main`
**Release title**: `v0.02-final - T4/0.01% Production Freeze with Complete Verification Infrastructure`

**Description**:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.789012.svg)](https://doi.org/10.5281/zenodo.789012)

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

```
Dominguez, G. (2025). LUKHΛS AI — T4/0.01% Infrastructure (v0.02-final)
[Computer software]. Zenodo. https://doi.org/10.5281/zenodo.789012
```

### 🔐 Verification

```bash
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
git checkout v0.02-final
sha256sum -c T4_FINAL_SIGNATURE.sha256
make validate-t4-strict
```

### 📊 Baseline Metrics

- **Modules**: 149 (100% documented)
- **Coverage**: 83.9% (125/149 modules)
- **Health Score**: 20.3/100 (baseline)
- **Validation**: 8/8 checks passing

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

**Published to Zenodo**: https://zenodo.org/record/789012
```

#### 7c. Attach release artifacts

**Upload these files**:
- [ ] `RELEASE_MANIFEST.json`
- [ ] `T4_FINAL_SIGNATURE.sha256`
- [ ] `docs/releases/v0.02-final-RELEASE_NOTES.md`
- [ ] `docs/T4_CLOSURE_BRIEF.md`
- [ ] `docs/T4_INFRASTRUCTURE_SUMMARY.md`
- [ ] `docs/_generated/META_REGISTRY.json`

#### 7d. Publish release

1. Check "Set as the latest release"
2. Click "Publish release" 🎉

**Verification**:
- Release appears on main repository page
- All 6 artifacts downloadable
- DOI badge visible
- Tag `v0.02-final` created

**Status**: ⬜ Not started | ✅ Complete

---

## ✅ Post-Publication Verification

After completing all 7 steps:

### 1. Verify Zenodo record
- [ ] Visit Zenodo record URL
- [ ] Download all 6 files
- [ ] Verify checksums match local copies

### 2. Verify GitHub release
- [ ] Visit GitHub release page
- [ ] Download all 6 artifacts
- [ ] Verify they match Zenodo files

### 3. Test external verification
```bash
# Fresh clone as external user would do
cd /tmp
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
git checkout v0.02-final
sha256sum -c T4_FINAL_SIGNATURE.sha256
# Expected: All OK

make validate-t4-strict
# Expected: 8/8 checks passing
```

### 4. Verify citation information
- [ ] DOI badge shows in README
- [ ] Citation block in release notes has correct DOI
- [ ] Zenodo record shows correct metadata
- [ ] Related identifiers link to GitHub

---

## 🎓 Success Criteria

Publication is complete when:

- ✅ Zenodo DOI obtained and active
- ✅ All 6 artifacts uploaded to Zenodo
- ✅ GitHub release published with artifacts
- ✅ DOI badge added to README
- ✅ Release notes updated with citation
- ✅ Metadata committed and pushed
- ✅ External verification tested successfully

---

## 📞 Troubleshooting

### Issue: Zenodo upload fails

**Solution**: See [ZENODO_UPLOAD_GUIDE.md](../../scripts/release/ZENODO_UPLOAD_GUIDE.md) troubleshooting section

### Issue: Checksums don't match

**Solution**:
1. Do NOT proceed to Zenodo
2. Run `make freeze-verify` for details
3. Investigate integrity violation
4. Fix issues and restart from Step 1

### Issue: Validation fails (not 8/8)

**Solution**:
1. Review failure details from `make validate-t4-strict`
2. Fix underlying issues
3. Re-run until all checks pass
4. Only proceed when 8/8 passing

---

## 📝 Execution Log

Track your progress:

| Step | Description | Status | Date | Notes |
|------|-------------|--------|------|-------|
| 1 | Checkout v0.02-final | ⬜ | | |
| 2 | Verify signatures | ⬜ | | |
| 3 | Run validation | ⬜ | | |
| 4 | Upload to Zenodo | ⬜ | | DOI: |
| 5 | Update docs with DOI | ⬜ | | |
| 6 | Commit metadata | ⬜ | | |
| 7 | Create GitHub release | ⬜ | | |

---

**Last Updated**: 2025-10-05
**Version**: 1.0.0
**For Release**: v0.02-final
