"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : institution_manager.py                         │
│ DESCRIPTION : Handle symbolic LucasID institution onboarding │
│ TYPE        : Institution/Enterprise Manager                 │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from fastapi import APIRouter, Form, HTTPException
from backend.app.id_generator import generate_lucas_id, generate_username_slug
from backend.app.emailer import send_welcome_email

router = APIRouter()

@router.post("/institution/signup")
def institution_signup(organization_name: str = Form(...), email: str = Form(...)):
    """
    Create a symbolic LucasID for an institution (ENT or EDU).
    """
    username_slug = generate_username_slug(organization_name)
    lukhas_id_code = generate_lucas_id(entity_type="ENT", org_name=organization_name)

    # Placeholder QRGLYMPH URL
    qrglyph_url = f"https://lukhasid.io/assets/qrglyphs/{username_slug}.png"

    # Send welcome email
    send_welcome_email(to_email=email, username=username_slug, lukhas_id_code=lukhas_id_code, qrglyph_url=qrglyph_url)

    # Simulate DB insert (to replace with real DB session later)
    print(f"✅ New Institution LucasID created: {lukhas_id_code} for {username_slug} (ENT)")

    return {
        "message": "Institution signup successful",
        "identity_legacy_code": lukhas_id_code,
        "username_slug": username_slug,
        "qrglyph_url": qrglyph_url
    }
