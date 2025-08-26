# tools/ci/owners_from_codeowners.py
from pathlib import Path
import re

def parse_codeowners(text: str):
    rules = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        if len(parts) >= 2:
            pattern, owners = parts[0], parts[1:]
            rules.append((pattern, owners))
    return rules

def owners_for(path: str, rules):
    from fnmatch import fnmatch
    hits = []
    for pattern, owners in rules:
        # Handle CODEOWNERS patterns properly
        if pattern.startswith("/"):
            # Absolute path from repo root
            pattern = pattern[1:]
        if pattern.endswith("/"):
            # Directory pattern
            pattern = pattern + "*"
        
        # Check if path matches pattern
        if "*" in pattern or "?" in pattern:
            if fnmatch(path, pattern):
                hits = owners  # last match wins (GitHub semantics)
        elif pattern in path:
            hits = owners  # substring match for simple patterns
    return hits

def map_files_to_owners(files, codeowners_path="CODEOWNERS"):
    p = Path(codeowners_path)
    if not p.exists(): return {}
    rules = parse_codeowners(p.read_text())
    out = {}
    for f in files:
        out[f] = owners_for(f, rules)
    return out