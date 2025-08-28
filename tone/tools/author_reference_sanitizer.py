#!/usr/bin/env python3
"""
Author Reference Sanitizer

Auto-sanitizer that replaces author references with stance-based alternatives.
Used as a safety net for content that needs to be cleaned of author attributions.
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
    r"\bJulia Cameron\b": "creative coaching",

    # Additional patterns for common phrases
    r"\bKeats['']?\s*(concept|notion|idea|principle)\s*of\s*Negative\s*Capability\b":
        "concept of negative capability",
    r"\bFollowing\s*Keats\b": "Following the principle of",
    r"\bAs\s*Keats\s*(said|wrote|noted)\b": "As the saying goes",
    r"\bKeats['']?\s*(letter|writing)\b": "historical correspondence",
    r"\bShakespearean\s*tragedy\b": "classical tragedy",
    r"\bFreudian\s*(analysis|approach|method)\b": "depth-psychology \\1",
    r"\bEinsteinian\s*(wonder|curiosity)\b": "cosmic \\1",
    r"\bZen\s*(tradition|practice|teaching)\b": "contemplative \\1",
    r"\bTaoist\s*(principle|wisdom|approach)\b": "flow-oriented \\1"
}


def sanitize(text: str) -> str:
    """Sanitize text by replacing author references with stance descriptions"""
    output = text
    for pattern, replacement in REPLACEMENTS.items():
        output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
    return output


def sanitize_file(file_path: str) -> tuple[str, int]:
    """Sanitize a file and return the cleaned content with replacement count"""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        sanitized_content = sanitize(original_content)

        # Count replacements by comparing original vs sanitized
        replacement_count = 0
        for pattern in REPLACEMENTS.keys():
            original_matches = len(re.findall(pattern, original_content, re.IGNORECASE))
            sanitized_matches = len(re.findall(pattern, sanitized_content, re.IGNORECASE))
            replacement_count += (original_matches - sanitized_matches)

        return sanitized_content, replacement_count

    except Exception as e:
        return f"Error reading file: {e}", 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sanitize content by removing author references")
    parser.add_argument("input_file", nargs="?", help="Input file to sanitize (default: stdin)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--in-place", action="store_true", help="Modify file in-place")
    parser.add_argument("--report", action="store_true", help="Show replacement report")

    args = parser.parse_args()

    # Read input
    if args.input_file:
        content, replacement_count = sanitize_file(args.input_file)
        if "Error reading file:" in content:
            print(content, file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        original_content = sys.stdin.read()
        content = sanitize(original_content)

        # Count replacements
        replacement_count = 0
        for pattern in REPLACEMENTS.keys():
            original_matches = len(re.findall(pattern, original_content, re.IGNORECASE))
            sanitized_matches = len(re.findall(pattern, content, re.IGNORECASE))
            replacement_count += (original_matches - sanitized_matches)

    # Write output
    if args.in_place and args.input_file:
        with open(args.input_file, "w", encoding="utf-8") as f:
            f.write(content)
        if args.report:
            print(f"✅ Sanitized {args.input_file}: {replacement_count} replacements made")
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        if args.report:
            print(f"✅ Sanitized content written to {args.output}: {replacement_count} replacements made")
    else:
        print(content)
        if args.report:
            print(f"✅ {replacement_count} replacements made", file=sys.stderr)


if __name__ == "__main__":
    main()
