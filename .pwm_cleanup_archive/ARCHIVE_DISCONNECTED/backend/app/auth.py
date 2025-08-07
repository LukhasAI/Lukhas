

"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : auth.py                                        │
│ DESCRIPTION : LucasID symbolic login and token issuance      │
│ TYPE        : Authentication API                             │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from fastapi import APIRouter, HTTPException, Form
from backend.app.id_generator import generate_lucas_id, generate_username_slug
from backend.app.emailer import send_welcome_email

router = APIRouter()

@router.post("/auth/signup")
def signup(full_name: str = Form(...), email: str = Form(...), entity_type: str = Form("USR")):
    """
    Create a new LucasID symbolic user and send a welcome email.
    """
    username_slug = generate_username_slug(full_name)
    lukhas_id_code = generate_lucas_id(entity_type=entity_type)

    # Placeholder QRGLYMPH URL (to be replaced with real QR generator)
    qrglyph_url = f"https://lukhasid.io/assets/qrglyphs/{username_slug}.png"

    # Send welcome email
    send_welcome_email(to_email=email, username=username_slug, lukhas_id_code=lukhas_id_code, qrglyph_url=qrglyph_url)

    # Simulate database creation (to replace with real DB session later)
    print(f"✅ New LucasID created: {lukhas_id_code} for {username_slug} ({entity_type})")

    return {
        "message": "Signup successful",
        "identity_legacy_code": lukhas_id_code,
        "username_slug": username_slug,
        "qrglyph_url": qrglyph_url
    }