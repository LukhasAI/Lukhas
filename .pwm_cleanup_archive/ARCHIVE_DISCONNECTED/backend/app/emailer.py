"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : emailer.py                                     │
│ DESCRIPTION : Send symbolic LUKHASID emails via Brevo SMTP    │
│ TYPE        : SMTP Utility                                   │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import os
import smtplib
from email.mime.text import MIMEText

from .email_templates import generate_welcome_email

# Load config from environment variables for security
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SENDER = os.getenv("SMTP_SENDER", "hello@lukhasid.io")


def send_welcome_email(to_email, username, lukhas_id_code, qrglyph_url):
    """
    Sends a symbolic welcome email with the user's LUKHASID and QRGLYMPH.
    """
    # Check that required environment variables are set
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError(
            "SMTP_USERNAME and SMTP_PASSWORD environment variables must be set"
        )

    html_content = generate_welcome_email(username, lukhas_id_code, qrglyph_url)
    msg = MIMEText(html_content, "html")
    msg["Subject"] = "🌌 Welcome to LUKHASiD"
    msg["From"] = SMTP_SENDER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Welcome email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed to send to {to_email}: {e}")
        return False
