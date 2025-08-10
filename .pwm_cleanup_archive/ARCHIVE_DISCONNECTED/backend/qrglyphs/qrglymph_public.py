"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : qrglymph_public.py                                        │
│ 🧾 DESCRIPTION : Public Qrglyph generator for symbolic identity sharing    │
│ 🧩 TYPE        : Lukhas-ID Utility      🔧 VERSION: v0.1.0                  │
│ 🖋️ AUTHOR      : Gonzalo Dominguez     📅 UPDATED: 2025-04-29              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - cryptography                                                          │
│   - segno (for QR code generation)                                       │
│   - requests or ipfshttpclient (for IPFS upload)                         │
│   - json, base64, pathlib                                                 │
└────────────────────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 🔍 USAGE GUIDE (for qrglymph_public.py)
#
# Generates a symbolic Qrglyph:
# 1. Encrypts your payload (e.g., image, document)
# 2. Uploads to IPFS or mock cloud
# 3. Generates a QR code pointing to encrypted IPFS link
# 4. Optionally overlays on a Lottie animation
#
# 💻 CLI EXAMPLE:
# python qrglymph_public.py --payload myfile.pdf --output outpath/
#
# ============================================================================
import argparse
import base64
import json
import os
from pathlib import Path

import segno  # QR code generator
from cryptography.fernet import Fernet

# import requests  # for real IPFS upload if using web3.storage or Pinata

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_OUTPUT = "./output"
MOCK_IPFS_GATEWAY = "https://demo-ipfs.io/ipfs/"


# ─────────────────────────────────────────────────────────────────────────────
# ENCRYPTION UTILS
# ─────────────────────────────────────────────────────────────────────────────
def generate_key():
    return Fernet.generate_key()


def encrypt_file(file_path, key):
    with open(file_path, "rb") as f:
        data = f.read()
    encrypted = Fernet(key).encrypt(data)
    return encrypted


def save_encrypted_file(encrypted_data, output_path):
    with open(output_path, "wb") as f:
        f.write(encrypted_data)


# ─────────────────────────────────────────────────────────────────────────────
# IPFS MOCK (Replace with real API if needed)
# ─────────────────────────────────────────────────────────────────────────────
def mock_ipfs_upload(encrypted_data, filename="payload.enc"):
    # Save locally, then pretend we uploaded to IPFS
    ipfs_hash = base64.urlsafe_b64encode(os.urandom(12)).decode("utf-8").rstrip("=")
    ipfs_link = f"{MOCK_IPFS_GATEWAY}{ipfs_hash}"
    return ipfs_link


# ─────────────────────────────────────────────────────────────────────────────
# QR CODE GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_qr_code(data, output_path):
    qr = segno.make(data)
    qr.save(os.path.join(output_path, "qrglyph_qr.png"))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────
def create_qrglyph(payload_path, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    key = generate_key()
    encrypted = encrypt_file(payload_path, key)
    encrypted_file_path = os.path.join(output_dir, "payload.enc")
    save_encrypted_file(encrypted, encrypted_file_path)

    ipfs_link = mock_ipfs_upload(encrypted, "payload.enc")
    qr_data = json.dumps({"ipfs": ipfs_link, "key": key.decode()})
    generate_qr_code(qr_data, output_dir)
    print(f"✅ Qrglyph created: {ipfs_link}")
    print("🔑 Decryption key saved in QR or separately as needed.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a public Qrglyph.")
    parser.add_argument("--payload", required=True, help="Path to payload file.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output directory.")
    args = parser.parse_args()

    create_qrglyph(args.payload, args.output)
