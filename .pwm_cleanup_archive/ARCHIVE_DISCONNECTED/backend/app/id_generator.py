"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : id_generator.py                                │
│ DESCRIPTION : Generator for symbolic LUKHASID identity codes  │
│ TYPE        : Utility Function                               │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import random
import string


def generate_lukhas_id(entity_type="USR", org_name=None):
    """
    Generate a symbolic Lukhas_ID code like:
    Lukhas_ID#USR-OPENAI-8124-GR9X
    """
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    random_number = random.randint(1000, 9999)

    code = f"Lukhas_ID#{entity_type}"
    if org_name:
        clean_name = org_name.strip().upper().replace(" ", "")
        code += f"-{clean_name}"
    code += f"-{random_number}-{suffix}"
    return code


def generate_username_slug(full_name):
    """
    Create a URL-safe slug for personalized user page:
    'John Smith' -> 'johnsmith'
    """
    return full_name.strip().lower().replace(" ", "")


def assign_badge(tier):
    """
    Assign a symbolic tier badge.
    """
    badges = {
        0: "⚫ TIER 0 — Guest",
        1: "🟢 TIER 1 — Observer",
        2: "🔵 TIER 2 — Supporter",
        3: "🟣 TIER 3 — Contributor",
        4: "🔴 TIER 4 — Arbiter",
        5: "✨ TIER 5 — Architect",
    }
    return badges.get(tier, "❔ Unknown Tier")


def generate_full_identity(
    name, entity_type="USR", org_name="LUKHAS", tier=0, signature="🧠"
):
    """
    Generate a full symbolic identity block.
    """
    lukhas_id = generate_lukhas_id(entity_type=entity_type, org_name=org_name)
    slug = generate_username_slug(name)
    badge = assign_badge(tier)

    identity = {
        "identity_legacy": lukhas_id,
        "name": name,
        "slug": slug,
        "tier": tier,
        "badge": badge,
        "symbolic_signature": signature,
    }
    return identity
