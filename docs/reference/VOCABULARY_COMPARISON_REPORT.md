# Vocabulary Files Comparison Report

## Directory Structure Analysis

### Main Vocabulary Locations
1. **branding/unified/vocabularies/** - Consolidated location (recommended)
2. **core/symbolic/** - Mixed with other symbolic code files
3. **symbolic/vocabularies/** - Dedicated vocabulary directory
4. **core/symbolic_legacy/vocabularies/** - Legacy vocabulary files

## File Comparison Results

### Duplicate Files (safe to consolidate)
Files that are identical except for TAG comments:
- bio_vocabulary.py
- dream_vocabulary.py
- identity_vocabulary.py
- voice_vocabulary.py
- vision_vocabulary.py

### Unique Files by Directory

#### symbolic/vocabularies (unique files):
- emotion_vocabulary.py
- vocabulary_template.py
- usage_examples.py

#### core/symbolic_legacy/vocabularies:
- emotion_vocabulary.py (different from symbolic version)
- vocabulary_template.py (different from symbolic version)

## Recommendations

1. **Keep unified location**: branding/unified/vocabularies/
2. **Preserve unique files**: Don't delete directories with unique content
3. **Update imports**: Change Python imports to use unified location
4. **Document differences**: Keep this report for reference

## Safe Actions

✅ Safe to remove:
- Exact duplicates (same content, same size)

⚠️ Keep for now:
- Files with real differences
- Directories with unique files

❌ Do not remove:
- branding/unified/vocabularies/ (consolidated location)
- Any file currently imported by active code
