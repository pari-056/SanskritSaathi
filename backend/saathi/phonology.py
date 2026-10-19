"""Small shared phonological helpers (retroflexion, s→ṣ), used by nominal and verbal morphology."""
from __future__ import annotations
from .translit import VOWELS

_NATVA_TRIGGERS = set("rzfF")
_NATVA_PASS = set(VOWELS) | set("hyv" "kKgGN" "pPbBm" "M")


def natva(form: str, from_idx: int = 0) -> str:
    """Retroflex n → ṇ after r/ṣ/ṛ/ṝ when only 'transparent' sounds intervene and the n is
    followed by a vowel or n/m/y/v. Only n at index >= from_idx can change."""
    chars = list(form)
    for i in range(from_idx, len(chars)):
        if chars[i] != "n" or i + 1 >= len(chars) or chars[i + 1] not in VOWELS + "nmyv":
            continue
        for j in range(i - 1, -1, -1):
            c = chars[j]
            if c in _NATVA_TRIGGERS:
                chars[i] = "R"
                break
            if c not in _NATVA_PASS:
                break
    return "".join(chars)
