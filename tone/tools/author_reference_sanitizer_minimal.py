#!/usr/bin/env python3
"""
Author Reference Sanitizer (Minimal)

Simple sanitizer for replacing author references with stance-based alternatives.
"""

import re
import sys

REPLACEMENTS = {
    r"\bKeats(ian)?\b": "poetic yet grounded",
    r"\bMacbeth\b": "tragic grandeur",
    r"\bShakespeare(an)?\b": "classical dramatic",
    r"\bFreud(ian)?\b": "depth-psychology",
    r"\bEinstein(ian)?\b": "cosmic curiosity",
    r"\bZen\b": "attentive presence",
    r"\bTao(ism|ist)?\b": "flow-oriented wisdom",
    r"\bRick Rubin\b": "contemporary creative practice",
    r"\bNachmanovitch\b": "improvisational arts",
    r"\bJulia Cameron\b": "creative coaching"
}

def sanitize(text: str) -> str:
    out = text
    for pat, repl in REPLACEMENTS.items():
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    return out

if __name__ == "__main__":
    print(sanitize(sys.stdin.read()))
