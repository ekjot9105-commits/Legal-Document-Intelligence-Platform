import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Redaction:
    category: str
    replacement: str


PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("email", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    ("phone", re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)"), "[REDACTED_PHONE]"),
    ("pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE), "[REDACTED_PAN]"),
    ("aadhaar", re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"), "[REDACTED_ID]"),
)


def redact_pii(text: str) -> tuple[str, list[Redaction]]:
    """Replace common direct identifiers before text enters an AI or analytics boundary."""
    redactions: list[Redaction] = []
    redacted = text
    for category, pattern, replacement in PATTERNS:
        redacted, count = pattern.subn(replacement, redacted)
        redactions.extend(Redaction(category, replacement) for _ in range(count))
    return redacted, redactions
