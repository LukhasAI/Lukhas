from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class PIIHit:
    kind: str
    value: str
    span: tuple[int, int]


_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6})")
_IPv4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b")
_IPv6 = re.compile(r"\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")  # US-style; customize per jurisdiction
_CC = re.compile(r"\b(?:\d[ -]*?){13,19}\b")  # candidate; will Luhn-check

_NAME_HINT = re.compile(r"\b(Name|Full Name|First Name|Last Name)\b:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)")


def _luhn(cc: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", cc)]
    if len(digits) < 13:
        return False
    total = 0
    odd = True
    for d in reversed(digits):
        if odd:
            total += d
        else:
            k = d * 2
            total += k - 9 if k > 9 else k
        odd = not odd
    return total % 10 == 0


def detect_pii(text: str) -> list[PIIHit]:
    hits: list[PIIHit] = []
    for m in _EMAIL.finditer(text):
        hits.append(PIIHit("email", m.group(0), (m.start(), m.end())))
    for m in _PHONE.finditer(text):
        val = m.group(0)
        if len(re.sub(r"\D", "", val)) >= 7:
            hits.append(PIIHit("phone", val, (m.start(), m.end())))
    for m in _IPv4.finditer(text):
        hits.append(PIIHit("ip_v4", m.group(0), (m.start(), m.end())))
    for m in _IPv6.finditer(text):
        hits.append(PIIHit("ip_v6", m.group(0), (m.start(), m.end())))
    for m in _SSN.finditer(text):
        hits.append(PIIHit("ssn_like", m.group(0), (m.start(), m.end())))
    for m in _CC.finditer(text):
        cc = m.group(0)
        if _luhn(cc):
            hits.append(PIIHit("credit_card", cc, (m.start(), m.end())))
    for m in _NAME_HINT.finditer(text):
        hits.append(PIIHit("name_hint", m.group(2), (m.start(2), m.end(2))))
    return hits


def mask_pii(text: str, hits: Iterable[PIIHit], strategy: str = "hash") -> str:
    masked = text
    # replace from end to keep spans valid
    for h in sorted(hits, key=lambda x: x.span[0], reverse=True):
        replacement = f"[{h.kind.upper()}]"
        masked = masked[: h.span[0]] + replacement + masked[h.span[1] :]
    return masked