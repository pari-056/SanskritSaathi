"""Map Universal Dependencies annotation onto this engine's analysis inventory."""
from __future__ import annotations
import re

from ..morph import Analysis
from ..translit import dev_to_slp1, to_slp1
from .conllu import Tok

CASE = {"Nom": 1, "Acc": 2, "Ins": 3, "Dat": 4, "Abl": 5, "Gen": 6, "Loc": 7, "Voc": 8}
NUM = {"Sing": "sg", "Dual": "du", "Plur": "pl"}
GEN = {"Masc": "m", "Fem": "f", "Neut": "n"}


def lemma_slp(lemma: str) -> str:
    """UD lemma (Devanagari) → SLP1; keeps only the root of 'prefix-root' lemmas."""
    last = lemma.split("-")[-1]
    s = to_slp1(re.sub(r"[0-9]+", "", last))
    return s


def lemma_prefixes(lemma: str) -> list[str]:
    parts = lemma.split("-")
    return [to_slp1(p) for p in parts[:-1]]


def gold_tense(f: dict) -> str | None:
    if f.get("Aspect") == "Perf":
        return "lit"
    mood, tense = f.get("Mood"), f.get("Tense")
    if mood == "Imp":
        return "lot"
    if mood == "Opt":
        return "vidhilin"
    if mood == "Jus":
        return "jus"
    if tense == "Fut":
        return "lrt"
    if tense == "Imp":
        return "lan"
    if tense == "Pres" and mood in (None, "Ind"):
        return "lat"
    if tense == "Past":
        return "lun"           # UD marks the aorist (and unspecified past) as Past
    return None


VOICE = {"Act": "act", "Mid": "mid", "Pass": "pass"}


def gold_kind(t: Tok) -> str:
    """Coarse category used for the per-type breakdown and for choosing which features to compare."""
    f = t.feats
    if t.upos in ("PUNCT", "SYM"):
        return "punct"
    if f.get("Compound") == "Yes":
        return "compound-member"
    if t.upos in ("VERB", "AUX"):
        vf = f.get("VerbForm")
        if vf == "Fin":
            return "verb-finite"
        if vf == "Conv":
            return "gerund"
        if vf == "Inf":
            return "infinitive"
        if vf == "Part":
            return "participle"
        return "verb-other"
    if t.upos in ("NOUN", "PROPN"):
        return "noun"
    if t.upos in ("ADJ", "DET", "NUM"):
        return "adjective"
    if t.upos == "PRON":
        return "pronoun"
    return "indeclinable"          # ADV, PART, CCONJ, SCONJ, ADP, INTJ, X


def _loose(s: str) -> str:
    """UD lemma conventions for verbs vary (root vs present stem, vowel length): compare loosely."""
    s = s.translate(str.maketrans("AIUF", "aiuf"))
    return s[:-1] if len(s) > 2 and s.endswith("a") else s


def lemma_candidates(a: Analysis) -> set[str]:
    out = {a.lemma}
    if a.root:
        out.add(a.root)
        if a.prefix:                     # UD often writes the prefixed lemma as one word: samA-lok → samAlok
            out.add(a.prefix.replace("-", "") + a.root)
    return out


def analysis_matches(a: Analysis, t: Tok) -> tuple[bool, bool]:
    """(lemma matches, lemma and every modelled feature matches)."""
    gl = lemma_slp(t.lemma)
    full = to_slp1(re.sub(r"[0-9\-]+", "", t.lemma))      # whole lemma incl. prefixes, hyphens removed
    cands = lemma_candidates(a)
    lemma_ok = gl in cands or full in cands
    if not lemma_ok and a.root:           # verbal analyses: tolerate vowel length and a final -a
        lemma_ok = _loose(gl) in {_loose(c) for c in cands} or _loose(full) in {_loose(c) for c in cands}
    if not lemma_ok:
        return False, False
    f = t.feats
    kind = gold_kind(t)
    ok = True
    if kind in ("noun", "adjective", "pronoun") or (kind == "participle"):
        if "Case" in f and a.case is not None and CASE.get(f["Case"]) != a.case:
            ok = False
        if "Number" in f and a.number is not None and NUM.get(f["Number"]) != a.number:
            ok = False
        if "Gender" in f and a.gender is not None and GEN.get(f["Gender"]) != a.gender:
            ok = False
        if kind == "participle":
            pos_ok = a.pos in ("ppp", "prap", "ktavatu", "future-passive", "pap", "participle")
            ok = ok and pos_ok
    elif kind == "verb-finite":
        if a.pos != "verb":
            return True, False
        want = gold_tense(f)
        if want is not None and a.tense != want:
            ok = False
        if "Person" in f and str(a.person) != f["Person"]:
            ok = False
        if "Number" in f and NUM.get(f["Number"]) != a.number:
            ok = False
        if "Voice" in f:
            vs = {VOICE.get(v) for v in f["Voice"].split(",")}
            vs.discard(None)
            if vs and getattr(a, "voice", "act") not in vs and "Cau" not in f["Voice"]:
                ok = False
    elif kind == "gerund":
        ok = a.pos == "gerund"
    elif kind == "infinitive":
        ok = a.pos == "infinitive"
    return True, ok
