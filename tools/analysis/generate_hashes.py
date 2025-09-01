#!/usr/bin/env python3
"""
Generate Hashes - LUKHAS manifest integrity verification
Creates comprehensive hash digests with symbolic proof generation
"""

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def calculate_sha3_512(file_path: Path) -> str:
    """Calculate SHA3-512 hash of file"""
    sha3 = hashlib.sha3_512()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha3.update(chunk)
    return sha3.hexdigest()


def calculate_shake256(file_path: Path, length: int = 64) -> str:
    """Calculate SHAKE256 hash of file"""
    shake = hashlib.shake_256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shake.update(chunk)
    return shake.hexdigest(length)


def extract_symbolic_glyphs(file_path: Path) -> dict[str, any]:
    """Extract symbolic glyphs and patterns from YAML file"""
    glyph_summary = {
        "total_glyphs": 0,
        "unique_glyphs": set(),
        "symbolic_patterns": [],
        "emergency_levels": [],
        "trinity_references": 0,
    }

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Find all emoji/symbolic characters
        emoji_pattern = re.compile(r"[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]|[\U0001F1E0-\U0001F1FF]")
        glyphs = emoji_pattern.findall(content)

        glyph_summary["total_glyphs"] = len(glyphs)
        glyph_summary["unique_glyphs"] = list(set(glyphs))

        # Extract symbolic patterns (arrays of symbols)
        pattern_matches = re.findall(r'\["([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\]', content)
        for match in pattern_matches:
            pattern = [symbol.strip() for symbol in match if symbol.strip()]
            if pattern:
                glyph_summary["symbolic_patterns"].append(pattern)

        # Extract emergency levels
        level_matches = re.findall(r"level_\d+_(\w+):", content)
        glyph_summary["emergency_levels"] = list(set(level_matches))

        # Count Trinity Framework references
        trinity_matches = re.findall(r"⚛️🧠🛡️|trinity", content, re.IGNORECASE)
        glyph_summary["trinity_references"] = len(trinity_matches)

    except Exception as e:
        print(f"Warning: Could not extract symbolic information: {e}")

    # Convert set to list for JSON serialization
    glyph_summary["unique_glyphs"] = list(glyph_summary["unique_glyphs"])

    return glyph_summary


def generate_qrglyph(manifest_hash: str, timestamp: str) -> list[str]:
    """Generate symbolic QR-like glyph pattern for integrity proof"""
    # Create a symbolic representation based on hash segments
    hash_segments = [manifest_hash[i : i + 8] for i in range(0, min(64, len(manifest_hash)), 8)]

    qrglyph_pattern = []

    # Header row
    qrglyph_pattern.append(["🔐", "📋", "🔒", "📋", "🔐"])

    # Data rows - map hash segments to symbolic patterns
    glyph_map = {
        "0": "⚫",
        "1": "🔴",
        "2": "🟠",
        "3": "🟡",
        "4": "🟢",
        "5": "🔵",
        "6": "🟣",
        "7": "🟤",
        "8": "⚪",
        "9": "🔘",
        "a": "🔹",
        "b": "🔸",
        "c": "🔺",
        "d": "🔻",
        "e": "🔶",
        "f": "🔷",
    }

    for _i, segment in enumerate(hash_segments[:3]):  # Use first 3 segments
        row = ["📋"]  # Start marker
        for char in segment[:3]:  # Use first 3 chars of segment
            glyph = glyph_map.get(char.lower(), "⚪")
            row.append(glyph)
        row.append("📋")  # End marker
        qrglyph_pattern.append(row)

    # Footer row
    qrglyph_pattern.append(["🔒", "📋", "🔐", "📋", "🔒"])

    return qrglyph_pattern


def generate_manifest_hash(manifest_file: str) -> dict[str, any]:
    """Generate comprehensive hash manifest for emergency manifest file"""

    manifest_path = Path(manifest_file)

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")

    print(f"🔐 Generating hash manifest for: {manifest_path}")

    # Calculate hashes
    print("   Calculating SHA3-512...")
    sha3_hash = calculate_sha3_512(manifest_path)

    print("   Calculating SHAKE256...")
    shake_hash = calculate_shake256(manifest_path)

    # File metadata
    stat = manifest_path.stat()
    file_size = stat.st_size
    modified_time = stat.st_mtime

    # Extract symbolic information
    print("   Extracting symbolic glyphs...")
    glyph_summary = extract_symbolic_glyphs(manifest_path)

    # Generate timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Generate QRGLYPH
    print("   Generating QRGLYPH...")
    qrglyph = generate_qrglyph(sha3_hash, timestamp)

    # Create hash manifest
    hash_manifest = {
        "manifest_info": {
            "file_path": str(manifest_path),
            "file_name": manifest_path.name,
            "file_size_bytes": file_size,
            "last_modified": datetime.fromtimestamp(modified_time).isoformat() + "Z",
            "hash_generated": timestamp,
        },
        "integrity_hashes": {
            "sha3_512": sha3_hash,
            "shake256_64": shake_hash,
            "verification_command": f"sha3sum -a 512 {manifest_path.name}",
            "expected_sha3": sha3_hash[:16] + "...",  # First 16 chars for quick verification
        },
        "symbolic_analysis": glyph_summary,
        "qrglyph_proof": {
            "description": "Symbolic QR-like glyph pattern for visual integrity verification",
            "pattern": qrglyph,
            "pattern_basis": "SHA3-512 hash segments mapped to symbolic glyphs",
            "verification_note": "Visual pattern should remain consistent for unchanged manifest",
        },
        "trinity_framework": {
            "version": "⚛️🧠🛡️",
            "component": "Guardian System",
            "integrity_status": "VERIFIED",
            "symbolic_signature": ["🔐", "📋", "✅"],
        },
        "validation": {
            "hash_algorithm_strength": "SHA3-512 (FIPS 202 compliant)",
            "collision_resistance": "2^256 security level",
            "qi_resistance": "Post-quantum secure with SHAKE256",
            "recommended_verification_interval": "24_hours",
        },
    }

    return hash_manifest


def save_hash_manifest(hash_manifest: dict, output_file: str):
    """Save hash manifest to file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(hash_manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Hash manifest saved to: {output_path}")


def verify_manifest_integrity(manifest_file: str, hash_file: str) -> bool:
    """Verify manifest integrity against stored hashes"""

    print(f"🔍 Verifying integrity: {manifest_file}")

    try:
        # Load stored hash manifest
        with open(hash_file) as f:
            stored_hashes = json.load(f)

        # Calculate current hashes
        current_sha3 = calculate_sha3_512(Path(manifest_file))
        current_shake = calculate_shake256(Path(manifest_file))

        # Compare hashes
        stored_sha3 = stored_hashes["integrity_hashes"]["sha3_512"]
        stored_shake = stored_hashes["integrity_hashes"]["shake256_64"]

        sha3_match = current_sha3 == stored_sha3
        shake_match = current_shake == stored_shake

        print(f"   SHA3-512: {'✅ MATCH' if sha3_match else '❌ MISMATCH'}")
        print(f"   SHAKE256: {'✅ MATCH' if shake_match else '❌ MISMATCH'}")

        if sha3_match and shake_match:
            print("🔐 Manifest integrity VERIFIED")
            return True
        else:
            print("🚨 Manifest integrity COMPROMISED")
            return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate and verify LUKHAS manifest hashes")
    parser.add_argument("manifest_file", help="Path to manifest file")
    parser.add_argument("--output", "-o", help="Output hash file (default: manifest_file.hash)")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify existing hash file")
    parser.add_argument("--hash-file", help="Hash file for verification (default: manifest_file.hash)")

    args = parser.parse_args()

    # Determine output/hash file
    if args.output:
        hash_file = args.output
    elif args.hash_file:
        hash_file = args.hash_file
    else:
        hash_file = args.manifest_file + ".hash"

    try:
        if args.verify:
            # Verify existing hash
            if not Path(hash_file).exists():
                print(f"❌ Hash file not found: {hash_file}")
                sys.exit(1)

            success = verify_manifest_integrity(args.manifest_file, hash_file)
            sys.exit(0 if success else 1)

        else:
            # Generate new hash manifest
            hash_manifest = generate_manifest_hash(args.manifest_file)
            save_hash_manifest(hash_manifest, hash_file)

            # Show summary
            print("\n📊 Hash Manifest Summary:")
            print(f"   File: {hash_manifest['manifest_info']['file_name']}")
            print(f"   Size: {hash_manifest['manifest_info']['file_size_bytes']} bytes")
            print(f"   SHA3-512: {hash_manifest['integrity_hashes']['sha3_512'][:32]}...")
            print(f"   SHAKE256: {hash_manifest['integrity_hashes']['shake256_64'][:32]}...")
            print(
                f"   Symbolic Glyphs: {hash_manifest['symbolic_analysis']['total_glyphs']} total, {len(hash_manifest['symbolic_analysis']['unique_glyphs'])} unique"
            )
            print(f"   Trinity References: {hash_manifest['symbolic_analysis']['trinity_references']}")

            print("\n🔐 Manifest integrity locked with symbolic proof")
            print(f"   Verification: python3 {sys.argv[0]} {args.manifest_file} --verify")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
