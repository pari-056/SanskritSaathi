"""Deterministic, auto-graded practice generated from the paradigm engine.

Correctness never depends on an LLM: every question's answer is a generated form.
A tiny adaptive scheduler re-weights question types the learner misses.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

from . import morph, sandhi
from .translit import to_slp1, slp1_to_dev, slp1_to_iast, detect_script
from . import lexicon as lx


@dataclass
class Question:
    kind: str                     # decl | conj | identify | sandhi
    key: str                      # adaptive-weight bucket, e.g. "case:3"
    prompt: str
    options: list[str]            # display strings (Devanagari)
    answer_idx: int
    answers_slp: set[str]         # accepted answers for typed mode (SLP1)
    explanation: str
    hint: str = ""
    level: int = 0
    source: str = ""


def _norm(user_text: str) -> str:
    t = user_text.strip().replace("।", "").replace("|", "")
    return to_slp1(t).strip()


def check_typed(q: Question, user_text: str) -> bool:
    n = _norm(user_text)
    cands = {n, n[:-1] + "m" if n.endswith("M") else n}
    return bool(cands & q.answers_slp)


def _opts(correct: str, pool: list[str], rng: random.Random, k: int = 4) -> tuple[list[str], int]:
    pool = [p for p in dict.fromkeys(pool) if p != correct]
    rng.shuffle(pool)
    opts = [correct] + pool[: k - 1]
    rng.shuffle(opts)
    return opts, opts.index(correct)


_NOUN_STEMS = [n for n in lx.NOUNS]

CASE_PROMPT = {1: "nominative", 2: "accusative", 3: "instrumental", 4: "dative",
               5: "ablative", 6: "genitive", 7: "locative"}


def q_declension(rng: random.Random, cases=(1, 2, 3, 4, 5, 6, 7), classes=None, numbers=None) -> Question:
    pool_stems = [n for n in _NOUN_STEMS if not classes or n[1] in classes] or _NOUN_STEMS
    stem, cls, gender, gloss = rng.choice(pool_stems)
    case = rng.choice(list(cases))
    num = rng.choice(list(numbers)) if numbers else rng.choice(["sg", "pl"] if rng.random() < 0.7 else ["sg", "du", "pl"])
    tbl = morph.decline(stem, cls, gender)
    ans = tbl[(case, num)]
    pool = [f for k, forms in tbl.items() for f in forms if k != (case, num)]
    pool = [p for p in pool if p not in ans]
    correct = ans[0]
    opts, idx = _opts(correct, pool, rng)
    return Question(
        "decl", f"case:{case}",
        f"Give the **{morph.CASE_EN[case]} {morph.NUM_EN[num]}** of **{slp1_to_dev(stem)}** "
        f"({slp1_to_iast(stem)}, {gloss}, {morph.GEN_EN[gender]}).",
        [slp1_to_dev(o) for o in opts], idx, set(ans),
        f"{slp1_to_dev(stem)} → {morph.CASE_SA[case]} {morph.NUM_SA[num]}: **{' / '.join(slp1_to_dev(a) for a in ans)}**.",
        hint=f"{morph.CASE_SA[case]} विभक्ति, {morph.NUM_SA[num]}",
    )


def q_conjugation(rng: random.Random, tenses=("lat",), roots=None) -> Question:
    root = rng.choice(list(roots) if roots else known_practice_roots())
    tense = rng.choice(list(tenses))
    tbl = morph.conjugate(root, tense)
    (p, n), form = rng.choice(list(tbl.items()))
    pool = [f for k, f in tbl.items() if k != (p, n)]
    opts, idx = _opts(form, pool, rng)
    meta = morph.root_meta(root)
    return Question(
        "conj", f"tense:{tense}",
        f"Give the **{morph.TENSE_EN[tense]}, person {p}, {morph.NUM_EN[n]}** of **√{slp1_to_dev(root)}** "
        f"({meta['gloss']}).",
        [slp1_to_dev(o) for o in opts], idx, {form},
        f"√{slp1_to_dev(root)}, {morph.TENSE_SA[tense]}, {morph.PERSON_SA[p]} पुरुष, {morph.NUM_SA[n]}: **{slp1_to_dev(form)}**.",
        hint=f"{morph.PERSON_SA[p]} पुरुष · {morph.NUM_SA[n]}",
    )


def known_practice_roots() -> list[str]:
    return [v[0] for v in lx.VERBS] + ["as", "kf"]


def q_identify(rng: random.Random, cases=(3, 4, 5, 6, 7), classes=None) -> Question:
    pool_stems = [n for n in _NOUN_STEMS if not classes or n[1] in classes] or _NOUN_STEMS
    stem, cls, gender, gloss = rng.choice(pool_stems)
    tbl = morph.decline(stem, cls, gender)
    case = rng.choice(list(cases))
    num = rng.choice(["sg", "pl"])
    form = tbl[(case, num)][0]
    an = morph.get_analyzer()
    readings = {(a.case, a.number) for a in an.lookup_slp(form) if a.lemma == stem}
    correct_label = f"{morph.CASE_EN[case]} {morph.NUM_EN[num]}"
    labels = [f"{morph.CASE_EN[c]} {morph.NUM_EN[n]}" for c in (2, 3, 4, 5, 6, 7) for n in ("sg", "pl")
              if (c, n) not in readings]
    opts, idx = _opts(correct_label, labels, rng)
    others = sorted(f"{morph.CASE_EN[c]} {morph.NUM_EN[n]}" for c, n in readings if (c, n) != (case, num))
    extra = f" (also: {', '.join(others)})" if others else ""
    return Question("identify", f"case:{case}",
                    f"What case and number is **{slp1_to_dev(form)}** (from {slp1_to_dev(stem)}, {gloss})?",
                    opts, idx, set(), f"{slp1_to_dev(form)} is {correct_label}{extra}.",
                    hint="Look at the ending.")


_SANDHI_PAIRS = [("rAmaH", "asti"), ("na", "asti"), ("iti", "api"), ("sadA", "eva"), ("agniH", "asti"),
                 ("saH", "gacCati"), ("rAmaH", "gacCati"), ("tat", "ca"), ("tat", "gacCati"),
                 ("phalam", "asti"), ("devAH", "gacCanti"), ("tatra", "iti"), ("mahA", "fzi"),
                 ("vidyA", "AlayaH"), ("tam", "gacCati"), ("rAmaH", "tatra"), ("hima", "AlayaH")]


_SANDHI_KIND = {
    "vowel": [("na", "asti"), ("iti", "api"), ("sadA", "eva"), ("tatra", "iti"), ("mahA", "fzi"), ("vidyA", "AlayaH"), ("hima", "AlayaH")],
    "visarga": [("rAmaH", "asti"), ("agniH", "asti"), ("saH", "gacCati"), ("rAmaH", "gacCati"), ("devAH", "gacCanti"), ("rAmaH", "tatra")],
    "consonant": [("tat", "ca"), ("tat", "gacCati"), ("phalam", "asti"), ("tam", "gacCati"), ("tasmin", "eva"), ("jagat", "ISaH")],
}


def q_sandhi(rng: random.Random, kinds=None) -> Question:
    pairs = [p for k in (kinds or []) for p in _SANDHI_KIND.get(k, [])] or _SANDHI_PAIRS
    l, r = rng.choice(pairs)
    res = sandhi.join(l, r)
    correct = res.text
    pool = [l + " " + r, l + r]
    # plausible wrong answers: apply the junction rule that belongs to a *different* initial sound
    for c2 in rng.sample(sandhi._INITIALS, 8):
        if c2 == r[0]:
            continue
        for j in sandhi.junctions(l, c2)[:1]:
            pool.append(l[: len(l) - j.drop] + j.left_tail + ("" if j.fuse else " ") + r)
    pool = [p for p in dict.fromkeys(pool) if p != correct and p.replace(" ", "") != correct.replace(" ", "")]
    opts, idx = _opts(correct, pool, rng)
    return Question("sandhi", "sandhi",
                    f"Join with sandhi: **{slp1_to_dev(l)} + {slp1_to_dev(r)}**",
                    [slp1_to_dev(o) for o in opts], idx, {correct, correct.replace(" ", "")},
                    f"{slp1_to_dev(l)} + {slp1_to_dev(r)} → **{slp1_to_dev(correct)}** — {res.rule}.",
                    hint="Look at the last sound of the first word and the first sound of the second.")


GENERATORS = {
    "decl": q_declension, "conj": q_conjugation, "identify": q_identify, "sandhi": q_sandhi,
}
KEYS = {
    "decl": [f"case:{c}" for c in range(1, 8)], "conj": ["tense:lat"], "identify": [f"case:{c}" for c in range(1, 8)],
    "sandhi": ["sandhi"],
}


class Scheduler:
    """Weights per skill key; misses raise a key's weight, hits lower it."""

    def __init__(self, weights: dict | None = None):
        self.w: dict[str, float] = weights if weights is not None else {}

    def record(self, key: str, correct: bool):
        cur = self.w.get(key, 1.0)
        self.w[key] = max(0.3, cur * 0.7) if correct else min(5.0, cur * 1.6)

    def next(self, kind: str, rng: random.Random | None = None, max_tries: int = 40, **kw) -> Question:
        rng = rng or random.Random()
        gen = GENERATORS[kind]
        for _ in range(max_tries):
            q = gen(rng, **kw)
            if rng.random() < min(1.0, self.w.get(q.key, 1.0) / 2.0):
                return q
        return q

    def weakest(self, n: int = 3) -> list[tuple[str, float]]:
        return sorted(((k, v) for k, v in self.w.items() if v > 1.0), key=lambda kv: -kv[1])[:n]
