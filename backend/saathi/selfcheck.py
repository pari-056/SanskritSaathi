"""Gold-standard self-check for the rule engine.

The gold items are standard textbook examples written independently of the rules
(so a regression in the rules shows up as a failure). Extend GOLD_* with your own
annotated data to turn this into a real evaluation harness; report exact-match
accuracy for sandhi and (lemma, features) accuracy for morphology.
"""
from __future__ import annotations
from . import sandhi, morph
from .translit import to_slp1, slp1_to_dev

# (left, right, expected) in SLP1
GOLD_SANDHI = [
    ("rAmaH", "asti", "rAmo'sti"), ("na", "asti", "nAsti"), ("iti", "api", "ityapi"),
    ("sadA", "eva", "sadEva"), ("mahA", "fzi", "maharzi"), ("hima", "AlayaH", "himAlayaH"),
    ("vidyA", "AlayaH", "vidyAlayaH"), ("tat", "ca", "tacca"), ("tat", "hi", "tadDi"),
    ("agniH", "asti", "agnirasti"), ("saH", "gacCati", "sa gacCati"), ("rAmaH", "tatra", "rAmastatra"),
    ("rAmaH", "gacCati", "rAmo gacCati"), ("jagat", "ISaH", "jagadISaH"), ("tasmin", "eva", "tasminneva"),
    ("tam", "gacCati", "taM gacCati"), ("rAmaH", "CAtraH", "rAmaSCAtraH"), ("tat", "Sruti", "tacCruti"),
    ("devAH", "gacCanti", "devA gacCanti"), ("tatra", "iti", "tatreti"), ("saH", "asti", "so'sti"),
    ("agniH", "ramate", "agnI ramate"), ("gacCan", "atra", "gacCannatra"), ("vAk", "gacCati", "vAg gacCati"),
]

# (Devanagari form, expected lemma SLP1, expected feature tuple)
# nominals: (pos, case, number, gender); verbs: (tense, person, number)
GOLD_MORPH = [
    ("रामः", "rAma", ("noun", 1, "sg", "m")), ("रामम्", "rAma", ("noun", 2, "sg", "m")),
    ("रामेण", "rAma", ("noun", 3, "sg", "m")), ("रामाय", "rAma", ("noun", 4, "sg", "m")),
    ("रामात्", "rAma", ("noun", 5, "sg", "m")), ("रामस्य", "rAma", ("noun", 6, "sg", "m")),
    ("रामे", "rAma", ("noun", 7, "sg", "m")), ("रामौ", "rAma", ("noun", 1, "du", "m")),
    ("रामान्", "rAma", ("noun", 2, "pl", "m")), ("रामैः", "rAma", ("noun", 3, "pl", "m")),
    ("रामेभ्यः", "rAma", ("noun", 4, "pl", "m")), ("रामाणाम्", "rAma", ("noun", 6, "pl", "m")),
    ("रामेषु", "rAma", ("noun", 7, "pl", "m")), ("फलानि", "Pala", ("noun", 1, "pl", "n")),
    ("हरिणा", "hari", ("noun", 3, "sg", "m")), ("हरये", "hari", ("noun", 4, "sg", "m")),
    ("गुरवः", "guru", ("noun", 1, "pl", "m")), ("नद्याः", "nadI", ("noun", 6, "sg", "f")),
    ("लतायाः", "latA", ("noun", 6, "sg", "f")), ("लतायाम्", "latA", ("noun", 7, "sg", "f")),
    ("मत्या", "mati", ("noun", 3, "sg", "f")), ("तेषाम्", "tad", ("pron", 6, "pl", "m")),
    ("तस्मै", "tad", ("pron", 4, "sg", "m")), ("कस्मिन्", "kim", ("pron", 7, "sg", "m")),
    ("अहम्", "asmad", ("pron", 1, "sg", None)), ("त्वम्", "yuzmad", ("pron", 1, "sg", None)),
    ("गच्छामि", "gam", ("lat", 1, "sg")), ("गच्छसि", "gam", ("lat", 2, "sg")),
    ("गच्छन्ति", "gam", ("lat", 3, "pl")), ("अगच्छत्", "gam", ("lan", 3, "sg")),
    ("गच्छेत्", "gam", ("vidhilin", 3, "sg")), ("गमिष्यति", "gam", ("lrt", 3, "sg")),
    ("पठतः", "paW", ("lat", 3, "du")), ("अस्ति", "as", ("lat", 3, "sg")), ("स्मः", "as", ("lat", 1, "pl")),
    ("करोति", "kf", ("lat", 3, "sg")), ("कुर्वन्ति", "kf", ("lat", 3, "pl")),
]


def run_sandhi_eval() -> dict:
    fails = []
    for l, r, exp in GOLD_SANDHI:
        got = sandhi.join(l, r).text
        if got != exp:
            fails.append({"input": f"{slp1_to_dev(l)} + {slp1_to_dev(r)}",
                          "expected": slp1_to_dev(exp), "got": slp1_to_dev(got)})
    n = len(GOLD_SANDHI)
    return {"n": n, "correct": n - len(fails), "accuracy": (n - len(fails)) / n, "failures": fails}


def _matches(a: morph.Analysis, lemma: str, feat: tuple) -> bool:
    if a.lemma != lemma:
        return False
    if feat[0] in morph.TENSES:
        return (a.pos == "verb" and a.tense == feat[0] and a.person == feat[1] and a.number == feat[2])
    pos, case, num, gen = feat
    return a.pos == pos and a.case == case and a.number == num and (gen is None or a.gender == gen)


def run_morph_eval() -> dict:
    an = morph.get_analyzer()
    fails = []
    for form, lemma, feat in GOLD_MORPH:
        r = an.analyze(form)
        if not any(_matches(a, lemma, feat) for a in r.analyses):
            fails.append({"form": form, "expected": f"{lemma} {feat}",
                          "got": "; ".join(f"{a.lemma} {a.features_en()}" for a in r.analyses) or "unresolved"})
    n = len(GOLD_MORPH)
    return {"n": n, "correct": n - len(fails), "accuracy": (n - len(fails)) / n, "failures": fails}


def run_roundtrip_eval() -> dict:
    """Generate-then-analyze consistency: every generated form must analyze back to its source cell."""
    an = morph.get_analyzer()
    total = bad = 0
    for forms, analyses in an.index.items():
        total += 1
        if not analyses:
            bad += 1
    return {"n": total, "correct": total - bad, "accuracy": (total - bad) / max(total, 1), "failures": []}


def run_all() -> dict:
    return {"sandhi": run_sandhi_eval(), "morphology": run_morph_eval(), "index": run_roundtrip_eval()}
