"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : qrglyph_generator.py                           │
│ DESCRIPTION : Generate QRGLYMPH symbolic identity visuals    │
│ TYPE        : Visual QR Code Generator                       │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from pathlib import Path

import qrcode

QR_OUTPUT_DIR = "static/qrglyphs"


def generate_qrglyph(username_slug: str, lukhas_id_code: str) -> str:
    """
    Generate a QRGLYMPH image that encodes the user's Lukhas_ID code.
    """
    Path(QR_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    qr_data = f"https://lukhasid.io/{username_slug} | {lukhas_id_code}"
    qr = qrcode.make(qr_data)
    qr_path = f"{QR_OUTPUT_DIR}/{username_slug}.png"
    qr.save(qr_path)

    print(f"🔳 QRGLYMPH generated: {qr_path}")
    return qr_path
