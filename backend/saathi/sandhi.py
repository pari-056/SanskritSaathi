"""Rule-based external sandhi (joining) and lexicon-constrained splitting.

All strings are SLP1. The rule set covers the common textbook rules:
vowel sandhi, visarga sandhi, and the main final-consonant rules. It is a
transparent rule engine, not a full Pāṇinian implementation: compound-internal
(antaraṅga) sandhi, internal sandhi and many lexical exceptions are out of scope.

Splitting is *lexicon-constrained*: a split is proposed only when every part is
a known surface form, so coverage equals the size of the supplied form set.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from functools import lru_cache
from .translit import VOWELS, CONSONANTS

_VOICED_CONS = set("gGjJqQdDbB" + "NYRnm" + "yrlvh")
_INITIALS = list(VOWELS) + list(CONSONANTS)
_VOICE_OF = {"k": "g", "w": "q", "t": "d", "p": "b"}
_NASAL_OF = {"k": "N", "w": "R", "t": "n", "p": "m"}


@dataclass(frozen=True)
class Junction:
    """How the end of the left word and the start of the right word change.

    joined = left[:-drop] + left_tail + (" " if not fuse else "") + right_head + right[1:]
    """
    drop: int
    left_tail: str
    right_head: str
    fuse: bool
    rule: str


@dataclass
class JoinResult:
    text: str
    rule: str
    alternatives: list[tuple[str, str]] = field(default_factory=list)  # (text, rule)


def _J(drop, tail, head, fuse, rule) -> Junction:
    return Junction(drop, tail, head, fuse, rule)


def junctions(left: str, c: str) -> list[Junction]:
    """All sandhi outcomes for `left` followed by a word starting with `c`.

    The first element is the primary (most standard) outcome.
    """
    if not left or not c:
        return []
    l = left[-1]
    prev = left[-2] if len(left) > 1 else ""

    # ---- vowel + vowel -----------------------------------------------------
    if l in VOWELS and c in VOWELS:
        if l in "aA" and c in "aA":
            return [_J(1, "A", "", True, "a/ā + a/ā → ā (savarṇa-dīrgha)")]
        if l in "iI" and c in "iI":
            return [_J(1, "I", "", True, "i/ī + i/ī → ī (savarṇa-dīrgha)")]
        if l in "uU" and c in "uU":
            return [_J(1, "U", "", True, "u/ū + u/ū → ū (savarṇa-dīrgha)")]
        if l in "fF" and c in "fF":
            return [_J(1, "F", "", True, "ṛ + ṛ → ṝ (savarṇa-dīrgha)")]
        if l in "aA":
            if c in "iI":
                return [_J(1, "e", "", True, "a/ā + i/ī → e (guṇa)")]
            if c in "uU":
                return [_J(1, "o", "", True, "a/ā + u/ū → o (guṇa)")]
            if c in "fF":
                return [_J(1, "ar", "", True, "a/ā + ṛ → ar (guṇa)")]
            if c in "eE":
                return [_J(1, "E", "", True, "a/ā + e/ai → ai (vṛddhi)")]
            if c in "oO":
                return [_J(1, "O", "", True, "a/ā + o/au → au (vṛddhi)")]
        if l in "iI":
            return [_J(1, "y", c, True, "i/ī + vowel → y + vowel (yaṇ)")]
        if l in "uU":
            return [_J(1, "v", c, True, "u/ū + vowel → v + vowel (yaṇ)")]
        if l in "fF":
            return [_J(1, "r", c, True, "ṛ + vowel → r + vowel (yaṇ)")]
        if l == "e":
            if c == "a":
                return [_J(0, "", "'", True, "e + a → e ' (pūrvarūpa, avagraha)")]
            return [_J(1, "ay", c, True, "e + vowel → ay + vowel (ayādi)"),
                    _J(0, "", c, False, "e + vowel → hiatus (y dropped; common in running text)")]
        if l == "o":
            if c == "a":
                return [_J(0, "", "'", True, "o + a → o ' (pūrvarūpa, avagraha)")]
            return [_J(1, "av", c, True, "o + vowel → av + vowel (ayādi)"),
                    _J(0, "", c, False, "o + vowel → hiatus (v dropped; common in running text)")]
        if l == "E":
            return [_J(1, "Ay", c, True, "ai + vowel → āy + vowel (ayādi)"),
                    _J(0, "", c, False, "ai + vowel → hiatus")]
        if l == "O":
            return [_J(1, "Av", c, True, "au + vowel → āv + vowel (ayādi)"),
                    _J(0, "", c, False, "au + vowel → hiatus")]
        return []

    # ---- visarga ---------------------------------------------------------------
    if l == "H":
        if left in ("saH", "eSaH"):
            if c == "a":
                return [_J(2, "o", "'", True, "saḥ/eṣaḥ + a → so/eṣo ' (o + avagraha)")]
            return [_J(1, "", c, False, "saḥ/eṣaḥ loses visarga before any other sound (etattadoḥ sulopaḥ)")]
        if prev == "a":
            if c == "a":
                return [_J(2, "o", "'", True, "aḥ + a → o ' (avagraha)")]
            if c in VOWELS:
                return [_J(1, "", c, False, "aḥ + vowel → a (visarga drops; hiatus)")]
            if c in _VOICED_CONS:
                return [_J(2, "o", c, False, "aḥ + voiced consonant → o")]
        elif prev == "A":
            if c in VOWELS or c in _VOICED_CONS:
                return [_J(1, "", c, False, "āḥ + vowel/voiced → ā (visarga drops)")]
        elif prev in "iIuUfeEoO":
            if c == "r":
                if prev in "iu":
                    return [_J(2, prev.upper(), c, False,
                               "iḥ/uḥ + r → ī/ū + r (visarga drops, vowel lengthens)")]
                return [_J(1, "", c, False, "visarga + r → visarga drops")]
            if c in VOWELS:
                return [_J(1, "r", c, True, "iḥ/uḥ etc. + vowel → r + vowel")]
            if c in _VOICED_CONS:
                return [_J(1, "r", c, False, "iḥ/uḥ etc. + voiced consonant → r")]
        # unvoiced following sound (all preceding vowels)
        if c in "kKpP":
            return [_J(0, "", c, False, "visarga stays before k/kh/p/ph")]
        if c in "cC":
            return [_J(1, "S", c, True, "visarga + c/ch → ś")]
        if c in "wW":
            return [_J(1, "z", c, True, "visarga + ṭ/ṭh → ṣ")]
        if c in "tT":
            return [_J(1, "s", c, True, "visarga + t/th → s")]
        if c in "Szs":
            return [_J(0, "", c, False, "visarga stays before sibilants (assimilation is optional)")]
        return [_J(0, "", c, False, "no change")]

    # ---- final consonants ----------------------------------------------------
    if l == "m":
        if c in VOWELS:
            return [_J(0, "", c, True, "m + vowel → m joins the vowel"),
                    _J(0, "", c, False, "m + vowel (written separately)")]
        homorganic = {**{x: "N" for x in "kKgG"}, **{x: "Y" for x in "cCjJ"}, **{x: "R" for x in "wWqQ"}, **{x: "n" for x in "tTdD"}}
        alts = [_J(1, homorganic[c], c, True, f"final m + {c} → homorganic nasal (alternative to anusvāra)")] if c in homorganic else []
        return [_J(1, "M", c, False, "final m + consonant → ṃ (anusvāra)")] + alts

    if l in "kwtp":
        v = _VOICE_OF[l]
        if c == "h":
            return [_J(1, v, _aspirate(v), True, f"{l} + h → {v} + {_aspirate(v)} (optional aspiration of h)"),
                    _J(1, v, "h", False, f"{l} + h → {v} h")]
        if l == "t":                       # dental t assimilates to a following palatal, retroflex or l (before generic voicing)
            if c in "cC":
                return [_J(1, "c", c, True, "t + c/ch → c")]
            if c in "jJ":
                return [_J(1, "j", c, True, "t + j/jh → j")]
            if c in "wW":
                return [_J(1, "w", c, True, "t + ṭ/ṭh → ṭ")]
            if c in "qQ":
                return [_J(1, "q", c, True, "t + ḍ/ḍh → ḍ")]
            if c == "l":
                return [_J(1, "l", c, True, "t + l → l")]
            if c == "S":
                return [_J(1, "c", "C", True, "t + ś → c + ch"),
                        _J(1, "c", "S", True, "t + ś → c + ś")]
        if c in "nm":
            nasal = _NASAL_OF[l]
            return [_J(1, nasal, c, True, f"{l} + nasal → {nasal} + nasal (anunāsika)"),
                    _J(1, v, c, False, f"{l} + nasal → {v} + nasal")]
        if c in VOWELS or c in _VOICED_CONS:
            return [_J(1, v, c, c in VOWELS, f"final {l} + voiced sound → {v}")]
        return [_J(0, "", c, False, "no change")]

    if l in "Nn" and prev and prev in "aiuf" and c in VOWELS:
        return [_J(1, l + l, c, True, f"short vowel + final {l} + vowel → {l} doubles")]
    if l == "n":
        if c in "cC":
            return [_J(1, "MS", c, True, "n + c/ch → ṃś + c/ch")]
        if c in "wW":
            return [_J(1, "Mz", c, True, "n + ṭ/ṭh → ṃṣ + ṭ/ṭh")]
        if c in "tT":
            return [_J(1, "Ms", c, True, "n + t/th → ṃs + t/th")]
        if c in "jJ":
            return [_J(1, "Y", c, True, "n + j/jh → ñ + j/jh")]
        if c in "qQ":
            return [_J(1, "R", c, True, "n + ḍ/ḍh → ṇ + ḍ/ḍh")]
    return [_J(0, "", c, False, "no change")]


def _aspirate(v: str) -> str:
    return {"g": "G", "q": "Q", "d": "D", "b": "B"}[v]


def _apply(left: str, right: str, j: Junction, spaced: bool) -> str:
    l = left[: len(left) - j.drop] + j.left_tail
    r = j.right_head + right[1:]
    return l + (" " if (not j.fuse and spaced and r) else "") + r


def join(left: str, right: str, spaced: bool = True) -> JoinResult:
    """Join two SLP1 words with external sandhi.

    `spaced=True` writes a space where the two words stay visually separate
    (e.g. rAmo gacCati); `spaced=False` always concatenates.
    """
    left, right = left.strip(), right.strip()
    if not left or not right:
        raise ValueError("Both words are required.")
    js = junctions(left, right[0])
    if not js:
        return JoinResult(left + " " + right, "no rule available")
    main, *rest = js
    alts = [(_apply(left, right, j, spaced), j.rule) for j in rest]
    return JoinResult(_apply(left, right, main, spaced), main.rule, alts)


def join_words(words: list[str], spaced: bool = True) -> tuple[str, list[str]]:
    """Left-to-right sandhi across several words. Returns (text, rules applied)."""
    if not words:
        return "", []
    out, rules = words[0], []
    for w in words[1:]:
        last = out.split(" ")[-1]
        prefix = out[: len(out) - len(last)]
        r = join(last, w, spaced)
        out = prefix + r.text
        rules.append(r.rule)
    return out, rules


# ---------------------------------------------------------------------------
# Splitting (reverse of the rules above), constrained by a known-form set
# ---------------------------------------------------------------------------

class Splitter:
    """Propose sandhi splits whose parts are all in `known` (SLP1 surface forms)."""

    def __init__(self, known):
        self.known = frozenset(w for w in known if w)
        # Sandhi only alters the last two characters of the left word, so index
        # candidates by everything before that.
        self._by_stem: dict[str, list[str]] = {}
        for w in self.known:
            self._by_stem.setdefault(w[:-2], []).append(w)
        self._cache: dict[tuple[str, int], tuple[tuple[str, ...], ...]] = {}

    def split(self, s: str, max_parts: int = 4, limit: int = 12) -> list[list[str]]:
        """Segmentations of `s` (spaces ignored) into >= 2 known words."""
        s = s.replace(" ", "")
        out = sorted((list(r) for r in self._seg(s, max_parts)), key=lambda p: (len(p), p))
        return [p for p in out if len(p) > 1][:limit]

    def _seg(self, s: str, depth: int) -> tuple[tuple[str, ...], ...]:
        key = (s, depth)
        if key in self._cache:
            return self._cache[key]
        results: set[tuple[str, ...]] = set()
        if s in self.known:
            results.add((s,))
        if depth > 1 and len(s) > 1:
            for p in range(len(s) + 1):
                for left in self._by_stem.get(s[:p], ()):
                    for c in _INITIALS:
                        for j in junctions(left, c):
                            head = left[: len(left) - j.drop] + j.left_tail + j.right_head
                            if not s.startswith(head):
                                continue
                            rest = c + s[len(head):]
                            if rest == s or len(rest) < 2 and rest not in self.known:
                                continue
                            for tail in self._seg(rest, depth - 1):
                                results.add((left,) + tail)
        out = tuple(sorted(results))
        self._cache[key] = out
        return out


# ---------------------------------------------------------------------------
# Restoring pre-sandhi finals of a *separate* token (for analysis of running text)
# ---------------------------------------------------------------------------

def restore_finals(token: str) -> list[tuple[str, str]]:
    """Possible underlying forms of a token whose final sound may have changed
    by sandhi with the *following* word. Returns (candidate, explanation)."""
    out: list[tuple[str, str]] = []
    if not token:
        return out
    t = token
    last = t[-1]
    if t.startswith("'"):
        out.append(("a" + t[1:], "initial avagraha stands for a-"))
    if last == "o":
        out.append((t[:-1] + "aH", "o ← aḥ before voiced sound or avagraha"))
    if last == "a":
        out.append((t + "H", "a ← aḥ before a vowel other than a"))
    if last == "A":
        out.append((t + "H", "ā ← āḥ before vowel/voiced sound"))
    if last == "r":
        out.append((t[:-1] + "H", "r ← ḥ (iḥ/uḥ etc. before voiced sound)"))
    if last in "Szs" and len(t) > 1:
        out.append((t[:-1] + "H", f"{last} ← ḥ before c/ṭ/t"))
    if last in "gqdb":
        inv = {v: k for k, v in _VOICE_OF.items()}
        out.append((t[:-1] + inv[last], f"{last} ← final {inv[last]} before voiced sound"))
    if last == "M":
        out.append((t[:-1] + "m", "ṃ ← final m before a consonant"))
    if last == "c":
        out.append((t[:-1] + "t", "c ← final t before c/ch"))
    if last == "n":
        out.append((t[:-1] + "t", "n ← final t before a nasal"))
    if last in "IU" and len(t) > 1:
        out.append((t[:-1] + last.lower() + "H", "ī/ū ← iḥ/uḥ before r"))
    return out
