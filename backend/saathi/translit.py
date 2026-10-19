"""Script conversion: Devanagari <-> SLP1 <-> IAST <-> Harvard-Kyoto.

SLP1 is the internal representation: one ASCII character per phoneme, which
makes sandhi and morphology rules simple string operations.
"""
from __future__ import annotations
import re

# ---- SLP1 inventory -------------------------------------------------------
VOWELS = "aAiIuUfFxXeEoO"
SHORT_VOWELS = "aiufx"
CONSONANTS = "kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL"
VOICELESS = "kKcCwWtTpPSzs"
NASALS = "NYRnm"
VOICED = "gGjJqQdDbB" + NASALS + "yrlvh"

_DEV_VOWELS = {
    "अ": "a", "आ": "A", "इ": "i", "ई": "I", "उ": "u", "ऊ": "U", "ऋ": "f", "ॠ": "F",
    "ऌ": "x", "ॡ": "X", "ए": "e", "ऐ": "E", "ओ": "o", "औ": "O",
}
_DEV_MATRAS = {
    "ा": "A", "ि": "i", "ी": "I", "ु": "u", "ू": "U", "ृ": "f", "ॄ": "F",
    "ॢ": "x", "ॣ": "X", "े": "e", "ै": "E", "ो": "o", "ौ": "O",
}
_DEV_CONS = {
    "क": "k", "ख": "K", "ग": "g", "घ": "G", "ङ": "N",
    "च": "c", "छ": "C", "ज": "j", "झ": "J", "ञ": "Y",
    "ट": "w", "ठ": "W", "ड": "q", "ढ": "Q", "ण": "R",
    "त": "t", "थ": "T", "द": "d", "ध": "D", "न": "n",
    "प": "p", "फ": "P", "ब": "b", "भ": "B", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "श": "S", "ष": "z", "स": "s", "ह": "h",
    "ळ": "L",
}
_DEV_MISC = {"ं": "M", "ः": "H", "ँ": "~", "ऽ": "'", "।": ".", "॥": "..", "ॐ": "oM"}
_DEV_DIGITS = {chr(0x966 + i): str(i) for i in range(10)}
VIRAMA = "्"
NUKTA = "़"

_SLP_TO_DEV_VOW = {v: k for k, v in _DEV_VOWELS.items()}
_SLP_TO_MATRA = {v: k for k, v in _DEV_MATRAS.items()}
_SLP_TO_DEV_CONS = {v: k for k, v in _DEV_CONS.items()}
_SLP_TO_DEV_MISC = {"M": "ं", "H": "ः", "~": "ँ", "'": "ऽ", ".": "।", "..": "॥"}

# ---- IAST ----------------------------------------------------------------
_SLP_TO_IAST = {
    "a": "a", "A": "ā", "i": "i", "I": "ī", "u": "u", "U": "ū", "f": "ṛ", "F": "ṝ",
    "x": "ḷ", "X": "ḹ", "e": "e", "E": "ai", "o": "o", "O": "au", "M": "ṃ", "H": "ḥ", "~": "m̐",
    "k": "k", "K": "kh", "g": "g", "G": "gh", "N": "ṅ", "c": "c", "C": "ch", "j": "j", "J": "jh",
    "Y": "ñ", "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "t": "t", "T": "th", "d": "d",
    "D": "dh", "n": "n", "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m", "y": "y", "r": "r",
    "l": "l", "v": "v", "S": "ś", "z": "ṣ", "s": "s", "h": "h", "L": "ḻ", "'": "'", ".": "|", "..": "||",
}
_IAST_TO_SLP = {v: k for k, v in _SLP_TO_IAST.items() if k not in (".",)}
_IAST_TO_SLP["|"] = "."
_IAST_TO_SLP["||"] = ".."
_IAST_TO_SLP["ṁ"] = "M"
_IAST_TO_SLP["|"] = "."

# ---- Harvard-Kyoto --------------------------------------------------------
_SLP_TO_HK = {
    "a": "a", "A": "A", "i": "i", "I": "I", "u": "u", "U": "U", "f": "R", "F": "RR", "x": "lR", "X": "lRR",
    "e": "e", "E": "ai", "o": "o", "O": "au", "M": "M", "H": "H", "~": "~",
    "k": "k", "K": "kh", "g": "g", "G": "gh", "N": "G", "c": "c", "C": "ch", "j": "j", "J": "jh",
    "Y": "J", "w": "T", "W": "Th", "q": "D", "Q": "Dh", "R": "N", "t": "t", "T": "th", "d": "d",
    "D": "dh", "n": "n", "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m", "y": "y", "r": "r",
    "l": "l", "v": "v", "S": "z", "z": "S", "s": "s", "h": "h", "L": "L", "'": "'", ".": "|", "..": "||",
}
_HK_TO_SLP = {v: k for k, v in _SLP_TO_HK.items()}

_IAST_MARKS = set("āīūṛṝḷḹṃṁḥśṣṭḍṇñṅḻĀĪŪṚṜŚṢṬḌṆÑṄ")


def _greedy_tokens(text: str, table: dict[str, str]) -> list[tuple[str, bool]]:
    """Greedy longest-match tokenizer. Returns (symbol, matched) pairs."""
    keys = sorted(table, key=len, reverse=True)
    maxlen = len(keys[0]) if keys else 1
    out: list[tuple[str, bool]] = []
    i = 0
    while i < len(text):
        for n in range(min(maxlen, len(text) - i), 0, -1):
            chunk = text[i:i + n]
            if chunk in table:
                out.append((table[chunk], True))
                i += n
                break
        else:
            out.append((text[i], False))
            i += 1
    return out


def detect_script(text: str) -> str:
    """Return 'devanagari', 'iast', or 'hk' (plain ASCII roman, treated as Harvard-Kyoto)."""
    if re.search(r"[\u0900-\u097F]", text):
        return "devanagari"
    if any(ch in _IAST_MARKS for ch in text):
        return "iast"
    return "hk"


def dev_to_slp1(text: str) -> str:
    out: list[str] = []
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch == NUKTA:
            i += 1
            continue
        if ch in _DEV_CONS:
            out.append(_DEV_CONS[ch])
            j = i + 1
            while j < n and text[j] == NUKTA:
                j += 1
            if j < n and text[j] == VIRAMA:
                i = j + 1
                continue
            if j < n and text[j] in _DEV_MATRAS:
                out.append(_DEV_MATRAS[text[j]])
                i = j + 1
                continue
            out.append("a")
            i = j
            continue
        if ch in _DEV_VOWELS:
            out.append(_DEV_VOWELS[ch])
        elif ch in _DEV_MISC:
            out.append(_DEV_MISC[ch])
        elif ch in _DEV_DIGITS:
            out.append(_DEV_DIGITS[ch])
        elif ch in (VIRAMA,) or ch in _DEV_MATRAS:
            pass  # stray combining mark
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def slp1_to_dev(text: str) -> str:
    out: list[str] = []
    prev_cons = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "." and text[i:i + 2] == "..":
            if prev_cons:
                out.append(VIRAMA)
            out.append("॥")
            prev_cons = False
            i += 2
            continue
        if ch in _SLP_TO_DEV_CONS:
            if prev_cons:
                out.append(VIRAMA)
            out.append(_SLP_TO_DEV_CONS[ch])
            prev_cons = True
        elif ch in VOWELS:
            if prev_cons:
                if ch != "a":
                    out.append(_SLP_TO_MATRA[ch])
                prev_cons = False
            else:
                out.append(_SLP_TO_DEV_VOW[ch])
        else:
            if prev_cons:
                out.append(VIRAMA)
                prev_cons = False
            out.append(_SLP_TO_DEV_MISC.get(ch, ch))
        i += 1
    if prev_cons:
        out.append(VIRAMA)
    return "".join(out)


def iast_to_slp1(text: str) -> str:
    text = text.replace("ṁ", "ṃ")
    return "".join(sym if ok else sym for sym, ok in _greedy_tokens(text, _IAST_TO_SLP))


def slp1_to_iast(text: str) -> str:
    out = []
    i = 0
    while i < len(text):
        if text[i:i + 2] == "..":
            out.append("||")
            i += 2
            continue
        out.append(_SLP_TO_IAST.get(text[i], text[i]))
        i += 1
    return "".join(out)


def hk_to_slp1(text: str) -> str:
    return "".join(sym for sym, _ in _greedy_tokens(text, _HK_TO_SLP))


def slp1_to_hk(text: str) -> str:
    out = []
    i = 0
    while i < len(text):
        if text[i:i + 2] == "..":
            out.append("||")
            i += 2
            continue
        out.append(_SLP_TO_HK.get(text[i], text[i]))
        i += 1
    return "".join(out)


def to_slp1(text: str, script: str | None = None) -> str:
    script = script or detect_script(text)
    if script == "devanagari":
        return dev_to_slp1(text)
    if script == "iast":
        return iast_to_slp1(text)
    if script == "hk":
        return hk_to_slp1(text)
    if script == "slp1":
        return text
    raise ValueError(f"Unknown script: {script}")


def from_slp1(text: str, script: str) -> str:
    if script == "devanagari":
        return slp1_to_dev(text)
    if script == "iast":
        return slp1_to_iast(text)
    if script == "hk":
        return slp1_to_hk(text)
    if script == "slp1":
        return text
    raise ValueError(f"Unknown script: {script}")


def convert(text: str, target: str, source: str | None = None) -> str:
    """Convert between scripts. `source` is auto-detected when omitted."""
    return from_slp1(to_slp1(text, source), target)


def dev(slp: str) -> str:
    return slp1_to_dev(slp)


def iast(slp: str) -> str:
    return slp1_to_iast(slp)


def tokenize_devanagari(text: str) -> list[str]:
    """Split on whitespace and punctuation, keeping Devanagari words."""
    return re.findall(r"[\u0900-\u0963\u0966-\u097F]+", text)
