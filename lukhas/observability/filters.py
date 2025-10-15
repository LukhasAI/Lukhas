import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_TOKEN = re.compile(r"\b(sk-[A-Za-z0-9]{6,})\b")


def redact_pii(text: str) -> str:
    text = _EMAIL.sub("[redacted@email]", text)
    text = _TOKEN.sub("[redacted_token]", text)
    return text
