"""Verified linguistic tools. Used by the UI directly and exposed to Gemini as
callable functions (automatic function calling), so the model can *check* forms
instead of recalling them from memory.

All functions take/return plain JSON-serialisable types and never raise.
"""
from __future__ import annotations
from . import morph, sandhi
from .syntax import analyze_sentence
from .translit import convert, detect_script, slp1_to_dev, slp1_to_iast, to_slp1

_COVERAGE = ("Coverage note: results come from a small built-in lexicon and rule engine. "
             "'Not found' means 'not covered', not 'incorrect'.")


def _fmt(slp: str) -> dict:
    return {"devanagari": slp1_to_dev(slp), "iast": slp1_to_iast(slp)}


def analyze_sanskrit_word(word: str) -> dict:
    """Morphologically analyse one Sanskrit word using a rule-based analyzer.

    Args:
        word: A single Sanskrit word in Devanagari, IAST, or Harvard-Kyoto roman.

    Returns:
        A dict with every analysis found (lemma, part of speech, case/number/gender or
        tense/person/number) or an empty list if the form is outside the lexicon.
    """
    try:
        r = morph.get_analyzer().analyze(word)
        return {
            "word": word, "found": bool(r.analyses), "coverage_note": _COVERAGE,
            "analyses": [{"lemma": a.lemma_display(),
                          "pos": a.pos_label(), "features": a.features_en(), "gloss": a.gloss,
                          "note": a.note} for a in r.analyses],
            "possible_sandhi_splits": [[slp1_to_dev(w) for w in sp] for sp in r.splits[:3]],
        }
    except Exception as e:  # pragma: no cover - defensive
        return {"error": f"{type(e).__name__}: {e}"}


def analyze_sanskrit_sentence(sentence: str) -> dict:
    """Analyse a Sanskrit sentence: per-token morphology, agreement-based disambiguation,
    kāraka (semantic role) labels, and learner-error checks such as subject-verb agreement.

    Args:
        sentence: Sanskrit text in Devanagari (preferred) or roman transliteration.
    """
    try:
        out = analyze_sentence(sentence).to_dict()
        out["coverage_note"] = _COVERAGE
        return out
    except Exception as e:  # pragma: no cover
        return {"error": f"{type(e).__name__}: {e}"}


def sandhi_join(first_word: str, second_word: str) -> dict:
    """Join two Sanskrit words with external sandhi (vowel, visarga, consonant rules).

    Args:
        first_word: The first word in its pausal form (e.g. रामः).
        second_word: The following word (e.g. अस्ति).
    """
    try:
        r = sandhi.join(to_slp1(first_word), to_slp1(second_word))
        return {"result": _fmt(r.text), "rule": r.rule,
                "alternatives": [{"result": _fmt(t), "rule": ru} for t, ru in r.alternatives]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def sandhi_split(text: str) -> dict:
    """Propose sandhi splits of a fused Sanskrit string. Every proposed part is a form known
    to the built-in lexicon, so an empty result means 'no split found in the lexicon'.

    Args:
        text: A fused Sanskrit string such as रामोऽस्ति or तत्रेति.
    """
    try:
        sp = morph.get_analyzer().splitter.split(to_slp1(text))
        return {"splits": [[slp1_to_dev(w) for w in s] for s in sp], "coverage_note": _COVERAGE}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def get_paradigm(lemma: str, tense: str = "lat") -> dict:
    """Return the full declension of a noun/adjective/pronoun stem, or the conjugation of a verb root.

    Args:
        lemma: A stem or root in Devanagari/IAST/HK, e.g. राम, लता, गम् (root), gam, कृ.
        tense: For verb roots only: one of lat (present), lan (imperfect), lot (imperative),
            vidhilin (optative), lrt (future).
    """
    try:
        slp = to_slp1(lemma).rstrip("H")
        an = morph.get_analyzer()
        candidates = [slp, slp.rstrip("m"), slp.rstrip("M"), slp + "a" if not slp.endswith("a") else slp]
        key = next((c for c in candidates if c in an.stems or ("√" + c) in an.stems), None)
        if key is None:
            return {"found": False, "coverage_note": _COVERAGE}
        meta = an.stems.get(key) or an.stems["√" + key]
        if meta["kind"] == "verb":
            root = meta["root"]
            if tense not in morph.TENSES:
                tense = "lat"
            tbl = morph.conjugate(root, tense)
            return {"found": True, "root": "√" + slp1_to_dev(root), "meaning": meta["gloss"],
                    "tense": morph.TENSE_EN[tense],
                    "forms": {f"person {p}, {morph.NUM_EN[n]}": _fmt(f) for (p, n), f in tbl.items()}}
        t = morph.paradigm_table(key)
        out = {}
        for g, tbl in t["tables"].items():
            label = morph.GEN_EN.get(g, "") if g else ""
            for (c, n), forms in tbl.items():
                out[f"{label} {morph.CASE_EN[c]} {morph.NUM_EN[n]}".strip()] = [slp1_to_dev(f) for f in forms]
        return {"found": True, "lemma": key, "meaning": t["gloss"], "forms": out}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def transliterate(text: str, target_script: str) -> dict:
    """Convert Sanskrit text between scripts.

    Args:
        text: Text in Devanagari, IAST, or Harvard-Kyoto (auto-detected).
        target_script: One of devanagari, iast, hk, slp1.
    """
    try:
        if target_script not in ("devanagari", "iast", "hk", "slp1"):
            return {"error": "target_script must be devanagari, iast, hk, or slp1"}
        return {"detected_source": detect_script(text), "result": convert(text, target_script)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


GEMINI_TOOLS = [analyze_sanskrit_word, analyze_sanskrit_sentence, sandhi_join, sandhi_split,
                get_paradigm, transliterate]
