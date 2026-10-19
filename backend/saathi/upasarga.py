"""Verbal prefixes (upasargas): forward junction and reversal, used to recognise prefixed verbs.

The reverse direction only proposes candidates; every proposal is accepted only if joining the prefix
to the candidate verb form reproduces the token exactly, so the analysis is sound (it can miss forms,
for example roots that undergo ṣatva, but it does not invent them).
"""
from __future__ import annotations
import re

from . import sandhi
from .phonology import natva
from .translit import VOWELS

PREFIXES = ["A", "ati", "adDi", "anu", "apa", "api", "aBi", "ava", "ni", "pari", "pra", "prati", "vi", "sam", "ud", "upa"]
GLOSS = {"A": "toward, up to", "ati": "beyond", "adDi": "over, upon", "anu": "after, along", "apa": "away",
         "api": "upon, over", "aBi": "toward", "ava": "down", "ni": "down, into", "pari": "around",
         "pra": "forth, forward", "prati": "back, against", "vi": "apart, away", "sam": "together", "ud": "up",
         "upa": "near, toward"}
_STOPS = "kKgGcCjJwWqQtTdDpPbB"


def norm(s: str) -> str:
    """Spelling normalisation: nasal before a stop = anusvāra; avagraha dropped."""
    s = s.replace("'", "")
    return re.sub(rf"[NYRnm](?=[{_STOPS}])", "M", s)


# roots whose initial s becomes ṣ after an upasarga ending in i/u (8.3.65–8.3.70): sthā, stu, sic, sev, sad, sidh …
SATVA_ROOTS = {"sTA", "stu", "sic", "sev", "sad", "siD", "saYj", "svaYj", "stamB", "su", "sU", "so"}


def join(prefix: str, form: str, root: str | None = None) -> str:
    """Prefix + verb form (SLP1). `root` enables ṣatva (abhi + sTA… → abhizTA…)."""
    c = form[0]
    if root in SATVA_ROOTS and prefix[-1] in "iu" and c == "s":
        rest = form[1:]
        if rest[:1] in ("t", "T", "n"):                    # ṣ makes a following dental retroflex: sT → ṣṭh
            rest = {"t": "w", "T": "W", "n": "R"}[rest[0]] + rest[1:]
        form = "z" + rest
    if prefix == "sam":
        res = "sam" + form if c in VOWELS else "saM" + form
    elif prefix == "ud":
        res = sandhi.join("ut", form, spaced=False).text
    elif prefix[-1] in "aAiIuU" and c in VOWELS:
        if prefix[-1] in "aA" and c == "f":
            res = prefix[:-1] + "Ar" + form[1:]
        else:
            res = sandhi.join(prefix, form, spaced=False).text
    else:
        res = prefix + form
    return natva(res, len(prefix)) if any(ch in prefix for ch in "rzf") else res


_MERGES = [("A", ["a", "A"]), ("e", ["i", "I"]), ("o", ["u", "U"]), ("E", ["e", "E"]), ("O", ["o", "O"]),
           ("ar", ["f"]), ("Ar", ["f", "F"])]


def candidates(token: str) -> list[tuple[str, str]]:
    """(prefix, rest-of-word) proposals for a token."""
    out: list[tuple[str, str]] = []
    for p in PREFIXES:
        starts = {"sam": ["saM", "sam", "saN", "saY", "saR", "san"], "ud": ["ud", "ut"]}.get(p, [p])
        for s in starts:
            if token.startswith(s) and len(token) > len(s) + 1:
                out.append((p, token[len(s):]))
        if p[-1] in "aA":
            stem = p[:-1]
            for surf, restored in _MERGES:
                if token.startswith(stem + surf) and len(token) > len(stem + surf):
                    for r in restored:
                        out.append((p, r + token[len(stem + surf):]))
        if p[-1] in "iI" and token.startswith(p[:-1] + "y") and len(token) > len(p) + 1 and token[len(p)] in VOWELS:
            out.append((p, token[len(p):]))
    expanded = []
    for p, rest in out:
        expanded.append((p, rest))
        if p[-1] in "iu" and rest.startswith("z"):
            back = {"w": "t", "W": "T", "R": "n"}
            expanded.append((p, "s" + rest[1:]))
            if rest[1:2] in back:
                expanded.append((p, "s" + back[rest[1]] + rest[2:]))
        if "R" in rest and any(ch in p for ch in "rzf"):
            expanded.append((p, rest.replace("R", "n")))
    return list(dict.fromkeys(expanded))


def verify(prefix: str, rest: str, token: str, root: str | None = None) -> bool:
    return norm(join(prefix, rest, root)) == norm(token)
