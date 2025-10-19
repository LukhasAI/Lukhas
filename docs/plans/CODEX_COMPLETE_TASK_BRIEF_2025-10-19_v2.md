---
title: Codex Agent - Complete Task Brief v2 (Post-Phase 5B) - PRODUCTION GRADE
date: 2025-10-19
version: 2.0
status: ready-for-execution
priority: critical
assigned: Codex Agent / GitHub Copilot
estimated_time: 6-8 hours
complexity: critical (2,262 files, deterministic, rollback-safe)
---

# Codex Agent - Complete Task Brief v2 (PRODUCTION GRADE)

**Created**: 2025-10-19
**Version**: 2.0 (with safety gates, determinism, rollback)
**Status**: Ready for Execution
**Priority**: CRITICAL
**Estimated Time**: 6-8 hours
**Complexity**: CRITICAL (2,262 files, multi-phase regeneration with canary gates)
**Context**: Post-Phase 5B directory flattening

---

## ⚠️ CRITICAL SAFETY REQUIREMENTS

This is a **PRODUCTION-GRADE** manifest regeneration affecting 2,262 files. The following safety gates are **MANDATORY**:

1. ✅ **Determinism**: Rule/canon digests pinned and verified
2. ✅ **Canary Gate**: 10% stratified sample approved before full run
3. ✅ **Rollback**: Git worktree + atomic writes + per-file backups
4. ✅ **Owner/Contract Parity**: Zero tolerance for accidental data loss
5. ✅ **Promotion Ceilings**: Hard limits prevent regex overreach
6. ✅ **Path Guards**: Reject legacy `lukhas/` paths, quarantine, etc.
7. ✅ **Round-trip Validation**: 2-pass read-write-read verification
8. ✅ **Human-in-Loop**: Approval gates at canary and pre-merge stages

**FAIL FAST**: Any safety violation aborts the entire run.

---

## 🎯 Mission

Execute Phase 4 manifest regeneration with validated star assignment rules across 1,571+ existing manifests, ensuring architectural alignment, contract compliance, and **zero data loss**.

---

## 📊 Current State

### Repository Structure (Post-Phase 5B)
```
Lukhas/
├── consciousness/          # Production consciousness modules
├── identity/              # Production identity modules
├── governance/            # Production governance modules
├── memory/               # Production memory modules
├── core/                 # Core integration modules (253 files)
├── labs/                 # Development lane (was candidate/, 2,877 files)
├── manifests/            # ALL manifests mirror code structure (FLAT)
│   ├── consciousness/
│   ├── identity/
│   ├── labs/
│   └── ...
├── matriz/               # MATRIZ cognitive engine
└── api/                  # Public API layer
```

**CRITICAL PATH RULES**:
- ✅ Correct: `manifests/consciousness/core/module.manifest.json`
- ❌ FATAL: `manifests/lukhas/consciousness/core/module.manifest.json`
- ❌ FATAL: Any uppercase, `..`, or `./` in paths
- ❌ FATAL: `quarantine/`, `build/`, `dist/`, `.venv/`, `node_modules/`

### Current Metrics
```
Total Python Packages:  1,953
Current Manifests:      1,571
Coverage:              80.4%
Target (99%):          1,934
Gap:                     363 manifests
```

### Star Distribution (Current - NEEDS REBALANCING)
```
Supporting: ~1,335 (~85%)  ← Too high, placeholder star
Flow:       ~100 (~6%)
Trail:      ~80 (~5%)
Other:      ~56 (~4%)
```

### Star Distribution (Target After Phase 4)
```
Supporting: ~1,160-1,350 (~60-70%)  ← Healthier balance
Flow:       ~230-290 (~12-15%)
Trail:      ~155-232 (~8-12%)
Watch:      ~97-155 (~5-8%)
Anchor:     ~58-97 (~3-5%)
Other:      ~39-97 (~2-5%)
```

---

## 📋 PRE-FLIGHT CHECKLIST (Run These First)

### Step 0.1: Pin Rule & Canon Digests (MANDATORY)

**Objective**: Lock star rules, star canon, and schema to specific versions to prevent "silent drift"

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Compute and pin digests
python3 - <<'PY'
import json, hashlib, pathlib

def sha256_file(path):
    """Compute SHA256 digest of a file."""
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

# Compute digests for critical config files
digests = {
    "star_rules.json": sha256_file("configs/star_rules.json"),
    "star_canon.json": sha256_file("packages/star_canon_py/star_canon/star_canon.json"),
    "schema.json": sha256_file("schemas/matriz_module_compliance.schema.json"),
}

# Write digests to audit file
path = pathlib.Path("docs/audits/phase4_digests.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(digests, indent=2) + "\n")

print("✅ Pinned configuration digests:")
print(json.dumps(digests, indent=2))
PY
```

**Success Criteria**:
- `docs/audits/phase4_digests.json` created
- Contains SHA256 for star_rules.json, star_canon.json, schema.json

---

### Step 0.2: Sync Star Canon Consistency (MANDATORY)

**Objective**: Ensure emoji and IDs match across all star canon sources

**Canonical Star Definitions** (use these EXACTLY):
```json
{
  "stars": [
    {"id": "Anchor", "emoji": "⚓", "domain": "Core Infrastructure"},
    {"id": "Flow", "emoji": "🌊", "domain": "Consciousness"},
    {"id": "Trail", "emoji": "✦", "domain": "Memory"},
    {"id": "Watch", "emoji": "🛡️", "domain": "Guardian/Governance"},
    {"id": "Horizon", "emoji": "🔭", "domain": "Vision/Perception"},
    {"id": "Oracle", "emoji": "🔮", "domain": "Quantum/Prediction"},
    {"id": "Living", "emoji": "🌱", "domain": "Bio-inspired"},
    {"id": "Drift", "emoji": "🌙", "domain": "Dream/Creativity"},
    {"id": "Supporting", "emoji": "🔧", "domain": "Infrastructure/Utilities"}
  ]
}
```

**Verification**:
```bash
# Check star canon consistency
python3 - <<'PY'
import json
from pathlib import Path

files = [
    "configs/star_rules.json",
    "packages/star_canon_py/star_canon/star_canon.json",
]

stars_by_file = {}
for f in files:
    if Path(f).exists():
        data = json.loads(Path(f).read_text())
        stars_by_file[f] = data.get("stars", [])

# Verify consistency
base_stars = stars_by_file.get(files[0], [])
for f, stars in stars_by_file.items():
    if stars != base_stars:
        print(f"❌ MISMATCH: {f}")
        print(f"   Expected: {base_stars}")
        print(f"   Got: {stars}")
        exit(1)

print("✅ Star canon consistent across all files")
PY
```

---

### Step 0.3: Create Rollback Worktree (MANDATORY)

**Objective**: Fast rollback if regeneration fails

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create git worktree for instant rollback
git worktree add ../Lukhas-manifests-prephase4 HEAD

echo "✅ Rollback worktree created at ../Lukhas-manifests-prephase4"
echo "To rollback: cp -r ../Lukhas-manifests-prephase4/manifests/ ./manifests/"
```

---

### Step 0.4: Backup Manifests (MANDATORY)

**Objective**: Two-tier backup (snapshot + worktree)

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create timestamped backup
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p .backups/manifests_${timestamp}
cp -r manifests/ .backups/manifests_${timestamp}/

echo "✅ Backed up 1,571 manifests to .backups/manifests_${timestamp}/"

# Record backup metadata
cat > .backups/manifests_${timestamp}/backup_metadata.json <<EOF
{
  "timestamp": "${timestamp}",
  "manifest_count": $(find manifests -name "module.manifest.json" | wc -l),
  "git_commit": "$(git rev-parse HEAD)",
  "git_branch": "$(git branch --show-current)",
  "phase": "phase4_pre_regeneration"
}
EOF
```

---

### Step 0.5: Configure Promotion Ceilings (MANDATORY)

**Objective**: Prevent runaway promotions from regex overreach

```bash
# Add promotion limits to star_rules.json
python3 - <<'PY'
import json
from pathlib import Path

rules_path = Path("configs/star_rules.json")
rules = json.loads(rules_path.read_text())

# Add promotion ceilings
rules["limits"] = {
    "max_promotions_run": 800,          # Total promotions per run
    "max_promotions_per_star": 200,     # Per-star ceiling
    "max_stars_per_module": 2,          # No module gets >2 stars
    "min_supporting_percentage": 55.0   # At least 55% stay Supporting
}

# Write back
rules_path.write_text(json.dumps(rules, indent=2) + "\n")
print("✅ Added promotion ceilings to star_rules.json")
PY
```

---

### Step 0.6: Build Exception List (RECOMMENDED)

**Objective**: Explicit overrides for edge cases

```bash
# Create star_rules_exceptions.json
cat > configs/star_rules_exceptions.json <<'EOF'
{
  "do_not_promote": [
    "labs/deprecated/*",
    "experiments/*"
  ],
  "force_promote": {
    "consciousness/qualia/core": {
      "star": "Flow",
      "reason": "Architectural cornerstone of consciousness processing"
    },
    "governance/guardian/constitutional": {
      "star": "Watch",
      "reason": "Constitutional AI enforcement"
    }
  }
}
EOF

echo "✅ Created star_rules_exceptions.json"
```

---

## 📋 Task 4.1: Regenerate Existing Manifests with Star Promotions (CANARY GATED)

**Priority**: CRITICAL
**Time**: 3-4 hours (includes canary)
**Files**: 1,571 existing manifests
**Objective**: Apply validated star assignment rules with promotion ceilings

---

### Phase 4.1.1: Build Canary Set (10% Stratified Sample)

**Objective**: Test on representative 10% before full run

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Build stratified 10% canary set
python3 - <<'PY'
import json, random
from pathlib import Path
from collections import defaultdict

manifests = list(Path("manifests").rglob("module.manifest.json"))

# Stratify by top-level directory
by_dir = defaultdict(list)
for m in manifests:
    top_dir = m.parts[1] if len(m.parts) > 2 else "root"
    by_dir[top_dir].append(str(m))

# Sample 10% from each stratum
canary = []
for top_dir, paths in by_dir.items():
    sample_size = max(1, int(len(paths) * 0.10))
    canary.extend(random.sample(paths, sample_size))

# Always include critical paths
critical_paths = [
    "core/",
    "matriz/",
    "identity/",
    "governance/",
    "consciousness/qualia/",
    "memory/fold/"
]

for critical in critical_paths:
    for m in manifests:
        if critical in str(m) and str(m) not in canary:
            canary.append(str(m))
            if len(canary) >= len(manifests) * 0.10:
                break

# Write canary list
Path("docs/audits/phase4_canary_list.txt").write_text("\n".join(sorted(canary)) + "\n")

print(f"✅ Canary set: {len(canary)} manifests (~{len(canary)/len(manifests)*100:.1f}%)")
print(f"   Critical paths: {sum(1 for c in canary if any(cp in c for cp in critical_paths))}")
PY
```

---

### Phase 4.1.2: Run Canary Regeneration

**Objective**: Regenerate canary set with full safety checks

```bash
# Create canary runner script
cat > scripts/phase4_run_set.sh <<'EOF'
#!/bin/bash
set -euo pipefail

manifest_list="$1"

while IFS= read -r manifest_path; do
  # Extract module path from manifest path
  # manifests/consciousness/core/module.manifest.json -> consciousness/core
  module_path=$(echo "$manifest_path" | sed 's|^manifests/||; s|/module.manifest.json$||')

  echo "Processing: $module_path"

  python scripts/generate_module_manifests.py \
    --module-path "$module_path" \
    --schema-version 1.1.0 \
    --rules-digest "$(jq -r '.["star_rules.json"]' docs/audits/phase4_digests.json)" \
    --canon-digest "$(jq -r '.["star_canon.json"]' docs/audits/phase4_digests.json)" \
    --star-from-rules \
    --star-confidence-min 0.70 \
    --preserve-tier \
    --preserve-owner \
    --preserve-contracts \
    --atomic-write \
    --roundtrip-verify \
    --reject-legacy-prefix "lukhas/" \
    --exclude "quarantine/*" \
    --exclude ".venv/*" \
    --exclude "node_modules/*" \
    --write \
    --verbose

done < "$manifest_list"
EOF

chmod +x scripts/phase4_run_set.sh

# Run canary
bash scripts/phase4_run_set.sh docs/audits/phase4_canary_list.txt
```

---

### Phase 4.1.3: Canary Analysis & Approval Gate

**Objective**: Human review of canary results before full run

```bash
# Analyze canary results
python3 - <<'PY'
import json
from pathlib import Path
from collections import Counter

canary_paths = Path("docs/audits/phase4_canary_list.txt").read_text().splitlines()

before_stars = Counter()
after_stars = Counter()
promotions = []

for manifest_path in canary_paths:
    m = Path(manifest_path)
    if not m.exists():
        continue

    data = json.loads(m.read_text())
    stars = data.get("constellation", {}).get("stars", [])

    for star in stars:
        after_stars[star] += 1

    # Check backup for "before" state
    # (simplified - assumes backup exists)

# Generate canary report
report = {
    "canary_count": len(canary_paths),
    "star_distribution_after": dict(after_stars),
    "promotions": promotions[:20],  # Top 20
    "status": "PENDING_APPROVAL"
}

Path("docs/audits/phase4_canary_report.json").write_text(json.dumps(report, indent=2))

print("📊 Canary Report:")
print(f"   Manifests processed: {len(canary_paths)}")
print(f"   Star distribution:")
for star, count in after_stars.most_common():
    print(f"      {star}: {count}")
print()
print("🚦 MANUAL REVIEW REQUIRED")
print("   1. Review docs/audits/phase4_canary_report.json")
print("   2. Check star distribution is reasonable")
print("   3. Verify no accidental data loss (owner/tier/contracts)")
print("   4. If approved, run:")
print("      echo 'approved' > docs/audits/phase4_canary_approved.txt")
PY
```

**STOP HERE**: Human must review canary report and approve before continuing.

**Approval Command** (run only after review):
```bash
echo "approved" > docs/audits/phase4_canary_approved.txt
```

---

### Phase 4.1.4: Verify Canary Approval (HARD GATE)

```bash
# Check for approval file
if [ ! -f docs/audits/phase4_canary_approved.txt ]; then
  echo "❌ FATAL: Canary not approved. Aborting."
  echo "   Review docs/audits/phase4_canary_report.json and approve if safe."
  exit 1
fi

echo "✅ Canary approved. Proceeding with full regeneration."
```

---

### Phase 4.1.5: Full Regeneration (Parallel, Chunked, Resumable)

**Objective**: Regenerate all 1,571 manifests with parallelism and resume capability

```bash
# Find all existing manifests
find manifests -name "module.manifest.json" -type f > /tmp/all_manifests.txt

echo "Found $(wc -l < /tmp/all_manifests.txt) manifests"

# Split into chunks of 200
split -l 200 /tmp/all_manifests.txt /tmp/mchunk_

# Initialize state tracking
mkdir -p .phase4
echo '{"completed": []}' > .phase4/state.json

# Run chunks in parallel (4 workers)
ls /tmp/mchunk_* | parallel -j 4 "bash scripts/phase4_run_chunk.sh {}"
```

**Chunk Runner** (with resume capability):
```bash
cat > scripts/phase4_run_chunk.sh <<'EOF'
#!/bin/bash
set -euo pipefail

chunk_file="$1"
state_file=".phase4/state.json"

while IFS= read -r manifest_path; do
  # Check if already processed
  if jq -e --arg p "$manifest_path" '.completed | index($p)' "$state_file" > /dev/null 2>&1; then
    echo "⏭️  Skipping (already done): $manifest_path"
    continue
  fi

  # Process manifest
  module_path=$(echo "$manifest_path" | sed 's|^manifests/||; s|/module.manifest.json$||')

  python scripts/generate_module_manifests.py \
    --module-path "$module_path" \
    --schema-version 1.1.0 \
    --rules-digest "$(jq -r '.["star_rules.json"]' docs/audits/phase4_digests.json)" \
    --canon-digest "$(jq -r '.["star_canon.json"]' docs/audits/phase4_digests.json)" \
    --star-from-rules \
    --star-confidence-min 0.70 \
    --preserve-tier \
    --preserve-owner \
    --preserve-contracts \
    --atomic-write \
    --roundtrip-verify \
    --reject-legacy-prefix "lukhas/" \
    --exclude "quarantine/*" \
    --exclude ".venv/*" \
    --exclude "node_modules/*" \
    --write \
    --verbose

  # Mark as completed
  jq --arg p "$manifest_path" '.completed += [$p]' "$state_file" > "$state_file.tmp"
  mv "$state_file.tmp" "$state_file"

done < "$chunk_file"
EOF

chmod +x scripts/phase4_run_chunk.sh
```

---

### Phase 4.1.6: Validation (MANDATORY)

```bash
# Round-trip validation for all regenerated manifests
python scripts/validate_module_manifests.py --strict --roundtrip

# Contract reference validation
python scripts/validate_contract_refs.py

# Owner/contract parity check
python3 - <<'PY'
import json
from pathlib import Path

manifests = list(Path("manifests").rglob("module.manifest.json"))
backup_dir = sorted(Path(".backups").glob("manifests_*"))[-1]

mismatches = []

for m in manifests:
    backup_path = backup_dir / m.relative_to(".")

    if not backup_path.exists():
        continue

    current = json.loads(m.read_text())
    backup = json.loads(backup_path.read_text())

    # Check owner parity
    current_owner = current.get("module", {}).get("owner")
    backup_owner = backup.get("module", {}).get("owner")

    if current_owner != backup_owner:
        mismatches.append({
            "path": str(m),
            "field": "owner",
            "before": backup_owner,
            "after": current_owner
        })

    # Check contracts parity
    current_contracts = current.get("contracts", [])
    backup_contracts = backup.get("contracts", [])

    if current_contracts != backup_contracts:
        mismatches.append({
            "path": str(m),
            "field": "contracts",
            "before": backup_contracts,
            "after": current_contracts
        })

if mismatches:
    print(f"❌ PARITY VIOLATIONS: {len(mismatches)}")
    for mm in mismatches[:10]:
        print(f"   {mm}")
    exit(1)

print("✅ Owner/contract parity: 100% preserved")
PY

# Promotion ceiling check
python3 - <<'PY'
import json
from pathlib import Path
from collections import Counter

rules = json.loads(Path("configs/star_rules.json").read_text())
limits = rules.get("limits", {})

manifests = list(Path("manifests").rglob("module.manifest.json"))
backup_dir = sorted(Path(".backups").glob("manifests_*"))[-1]

promotions = Counter()
total_promotions = 0

for m in manifests:
    backup_path = backup_dir / m.relative_to(".")

    if not backup_path.exists():
        continue

    current = json.loads(m.read_text())
    backup = json.loads(backup_path.read_text())

    current_stars = set(current.get("constellation", {}).get("stars", []))
    backup_stars = set(backup.get("constellation", {}).get("stars", []))

    if current_stars != backup_stars:
        new_stars = current_stars - backup_stars
        for star in new_stars:
            if star != "Supporting":
                promotions[star] += 1
                total_promotions += 1

max_total = limits.get("max_promotions_run", 999999)
max_per_star = limits.get("max_promotions_per_star", 999999)

if total_promotions > max_total:
    print(f"❌ CEILING EXCEEDED: {total_promotions} promotions > {max_total} limit")
    exit(1)

for star, count in promotions.items():
    if count > max_per_star:
        print(f"❌ CEILING EXCEEDED: {star} has {count} promotions > {max_per_star} limit")
        exit(1)

print(f"✅ Promotion ceilings respected: {total_promotions} total promotions")
for star, count in promotions.most_common():
    print(f"   {star}: {count}")
PY
```

---

## 📋 Task 4.2: Generate Missing Manifests (99% Coverage)

**Priority**: HIGH
**Time**: 1-2 hours
**Files**: 363 new manifests
**Objective**: Achieve 99% coverage with same safety controls

```bash
# Find orphan packages
find . -name "__init__.py" -type f \
  -not -path "./.venv/*" \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./quarantine/*" \
  -not -path "./build/*" \
  -not -path "./dist/*" | \
  awk -F/ '{path=""; for(i=2; i<=NF-1; i++) {if(path) path=path"/"$i; else path=$i}; print path}' | \
  sort -u > /tmp/all_packages.txt

find manifests -name "module.manifest.json" | \
  sed 's|^manifests/||; s|/module.manifest.json$||' | \
  sort -u > /tmp/manifested_packages.txt

comm -23 /tmp/all_packages.txt /tmp/manifested_packages.txt > /tmp/orphans.txt

echo "Orphan packages: $(wc -l < /tmp/orphans.txt)"

# Generate manifests for orphans (with same safety flags)
while IFS= read -r orphan_path; do
  echo "Generating manifest for: $orphan_path"

  python scripts/generate_module_manifests.py \
    --module-path "$orphan_path" \
    --schema-version 1.1.0 \
    --rules-digest "$(jq -r '.["star_rules.json"]' docs/audits/phase4_digests.json)" \
    --canon-digest "$(jq -r '.["star_canon.json"]' docs/audits/phase4_digests.json)" \
    --star-from-rules \
    --star-confidence-min 0.70 \
    --atomic-write \
    --roundtrip-verify \
    --reject-legacy-prefix "lukhas/" \
    --exclude "quarantine/*" \
    --exclude ".venv/*" \
    --exclude "node_modules/*" \
    --write \
    --verbose

done < /tmp/orphans.txt

# Validate final coverage
python3 -c "
from pathlib import Path

all_packages = len([
    p for p in Path('.').rglob('__init__.py')
    if '.venv' not in str(p)
    and 'node_modules' not in str(p)
    and 'quarantine' not in str(p)
    and 'build' not in str(p)
    and 'dist' not in str(p)
])

manifests = len(list(Path('manifests').rglob('module.manifest.json')))
coverage = (manifests / all_packages) * 100

print(f'Coverage: {coverage:.2f}%')
assert coverage >= 99.0, f'Coverage {coverage:.2f}% < 99% target'
print('✅ 99% coverage achieved')
"
```

---

## 📋 Task 4.3: Generate Audit Artifacts (MANDATORY)

**Priority**: CRITICAL
**Time**: 30 min
**Objective**: Comprehensive observability and audit trail

```bash
# Generate all audit artifacts
python3 - <<'PY'
import json
from pathlib import Path
from collections import Counter, defaultdict

manifests = list(Path("manifests").rglob("module.manifest.json"))
backup_dir = sorted(Path(".backups").glob("manifests_*"))[-1]

# Before/after star distribution
before_stars = Counter()
after_stars = Counter()
promotions = []
rule_hits = defaultdict(int)

for m in manifests:
    # After state
    data = json.loads(m.read_text())
    stars = data.get("constellation", {}).get("stars", [])
    tier = data.get("module", {}).get("tier", "Unknown")

    for star in stars:
        after_stars[star] += 1

    # Before state (if exists in backup)
    backup_path = backup_dir / m.relative_to(".")
    if backup_path.exists():
        backup_data = json.loads(backup_path.read_text())
        backup_stars = set(backup_data.get("constellation", {}).get("stars", []))
        current_stars = set(stars)

        new_stars = current_stars - backup_stars
        if new_stars:
            for star in new_stars:
                promotions.append({
                    "path": str(m.relative_to("manifests")),
                    "from": list(backup_stars),
                    "to": list(current_stars),
                    "promoted_to": star,
                    "tier": tier,
                    "confidence": data.get("constellation", {}).get("confidence", 0.0)
                })

        for star in backup_stars:
            before_stars[star] += 1

# Write artifacts
Path("docs/audits/phase4_star_distribution_before.json").write_text(
    json.dumps(dict(before_stars), indent=2)
)

Path("docs/audits/phase4_star_distribution_after.json").write_text(
    json.dumps(dict(after_stars), indent=2)
)

# Promotions CSV
import csv
with open("docs/audits/phase4_promotions.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["path", "from", "to", "promoted_to", "tier", "confidence"])
    writer.writeheader()
    writer.writerows(promotions)

print(f"✅ Generated audit artifacts:")
print(f"   - phase4_star_distribution_before.json")
print(f"   - phase4_star_distribution_after.json")
print(f"   - phase4_promotions.csv ({len(promotions)} promotions)")
PY
```

---

## ✅ FINAL ACCEPTANCE CRITERIA (All Must Pass)

### Configuration & Determinism
- [ ] Rule & canon digests pinned in `docs/audits/phase4_digests.json`
- [ ] Generator runs with `--rules-digest` and `--canon-digest` flags
- [ ] Schema version locked to 1.1.0 across all manifests
- [ ] Star canon emoji & IDs consistent across schema, rules, and canon package

### Safety Gates
- [ ] Canary ACK file exists: `docs/audits/phase4_canary_approved.txt`
- [ ] Git worktree created at `../Lukhas-manifests-prephase4`
- [ ] Manifest backup in `.backups/manifests_<timestamp>/`
- [ ] Promotion ceilings configured in `configs/star_rules.json`

### Execution & Validation
- [ ] Coverage ≥ 99% (1,934+ manifests)
- [ ] All manifests pass `validate_module_manifests.py --strict --roundtrip`
- [ ] All contract references valid (100% T1 coverage maintained)
- [ ] Owner/contract parity = 100% for pre-existing manifests
- [ ] Promotions ≤ configured ceilings (total and per-star)
- [ ] No legacy `lukhas/` paths in any manifest
- [ ] Star distribution reasonable (55-70% Supporting)

### Audit Artifacts (All Generated)
- [ ] `docs/audits/phase4_digests.json`
- [ ] `docs/audits/phase4_canary_list.txt`
- [ ] `docs/audits/phase4_canary_report.json`
- [ ] `docs/audits/phase4_canary_approved.txt`
- [ ] `docs/audits/phase4_star_distribution_before.json`
- [ ] `docs/audits/phase4_star_distribution_after.json`
- [ ] `docs/audits/phase4_promotions.csv`

### Documentation
- [ ] CONSTELLATION_TOP.md updated with new distribution
- [ ] Phase 4 audit report created: `docs/audits/phase4_manifest_regeneration_2025-10-19.md`
- [ ] Metrics dashboard script created: `scripts/constellation_metrics.py`

---

## 📝 Commit Message Template

```
feat(manifests): Phase 4 complete - 1,934 manifests with deterministic star promotions

Problem:
- 1,571 manifests had placeholder "Supporting" stars (85%)
- 363 Python packages lacked manifests (80.4% coverage)
- Star assignment rules validated but not applied at scale
- No safety gates for 2,262-file operation

Solution:
- Implemented production-grade regeneration with canary gates
- Pinned rule/canon digests for determinism (SHA256)
- Created rollback worktree + atomic writes + per-file backups
- Applied 0.70 confidence threshold with promotion ceilings
- Generated 363 new manifests for orphan packages
- All manifests validated with 2-pass round-trip checks

Impact:
- Coverage: 80.4% → 99.0% (1,571 → 1,934 manifests)
- Star promotions: XXX modules (within ceilings)
- Distribution: XX% Supporting, XX% Flow, XX% Trail, XX% other
- Owner/contract parity: 100% preserved
- Zero data loss, full audit trail
- Constellation framework fully mapped

Phase 4 COMPLETE. Ready for API integration (Phase 2).

Audit artifacts:
- docs/audits/phase4_digests.json
- docs/audits/phase4_promotions.csv
- docs/audits/phase4_star_distribution_{before,after}.json

🤖 Generated with Codex Agent

Co-Authored-By: Codex <noreply@github.com>
```

---

## 🔗 Reference Documents

**Essential Reading** (READ IN ORDER):
1. [AGENTS.md](../../AGENTS.md) - Repository structure (NOTE: May reference old `lukhas/` paths)
2. [configs/star_rules.json](../../configs/star_rules.json) - Star assignment rules
3. [packages/star_canon_py/star_canon/star_canon.json](../../packages/star_canon_py/star_canon/star_canon.json) - Canonical star definitions
4. [docs/audits/star_rules_validation_2025-10-19.md](../audits/star_rules_validation_2025-10-19.md) - Rules validation report

**Tools & Scripts**:
- `scripts/generate_module_manifests.py` - Manifest generator (MUST support new flags)
- `scripts/validate_module_manifests.py` - Schema validator
- `scripts/validate_contract_refs.py` - Contract validator
- `scripts/phase4_run_set.sh` - Canary/chunk runner (created in this task)

**Previous Work**:
- PR #433: Phase 5B manifest relocation (Copilot)
- PR #434: Context file enhancements (Jules)
- PR #438: Contract hardening (Copilot)

---

## 🚀 Quick Start Checklist

```bash
# 1. Read all reference docs (30 min)
# 2. Verify environment
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git pull origin main
python --version  # Verify 3.9+

# 3. Run Pre-Flight Checklist (Steps 0.1-0.6)
# 4. Run Canary (Phase 4.1.1-4.1.3)
# 5. GET HUMAN APPROVAL for canary
# 6. Run Full Regeneration (Phase 4.1.4-4.1.6)
# 7. Generate Missing Manifests (Task 4.2)
# 8. Generate Audit Artifacts (Task 4.3)
# 9. Validate ALL acceptance criteria
# 10. Create PR or commit to main
```

---

**Status**: Ready for execution (v2 - production-grade)
**Complexity**: CRITICAL (deterministic, rollback-safe, canary-gated)
**Estimated Completion**: 6-8 hours
**Human Gates**: 2 (canary approval, pre-merge review)

---

*This is a PRODUCTION-GRADE task brief with zero-tolerance safety requirements. Do not skip any step marked MANDATORY.*

— Claude Code (LUKHAS Core Team)
