"""Devanagari trainer: letter charts and auto-generated reading drills."""
from __future__ import annotations
import random

from .practice import Question, _opts
from .translit import dev_to_slp1, slp1_to_iast, slp1_to_dev

VOWELS_DEV = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ॠ", "ऌ", "ए", "ऐ", "ओ", "औ"]
MATRAS = ["", "ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ"]
VARGAS = [
    ("Guttural (कण्ठ्य)", ["क", "ख", "ग", "घ", "ङ"]),
    ("Palatal (तालव्य)", ["च", "छ", "ज", "झ", "ञ"]),
    ("Retroflex (मूर्धन्य)", ["ट", "ठ", "ड", "ढ", "ण"]),
    ("Dental (दन्त्य)", ["त", "थ", "द", "ध", "न"]),
    ("Labial (ओष्ठ्य)", ["प", "फ", "ब", "भ", "म"]),
    ("Semivowels (अन्तःस्थ)", ["य", "र", "ल", "व"]),
    ("Sibilants & h (ऊष्म)", ["श", "ष", "स", "ह"]),
]
CONSONANTS_DEV = [c for _, row in VARGAS for c in row]
CONJUNCTS = ["क्ष", "ज्ञ", "त्र", "श्र", "क्त", "त्य", "स्त", "द्ध", "न्द", "र्म", "प्र", "ष्ट", "स्थ", "ण्ड", "त्स", "ङ्क"]
WORDS = ["संस्कृतम्", "विद्या", "धर्मः", "कृष्णः", "क्षेत्रम्", "ज्ञानम्", "मित्रम्", "पुस्तकम्", "विद्यालयः", "गच्छति",
         "पठति", "सुन्दरम्", "अस्ति", "नमस्ते", "राजा", "बुद्धिः", "श्रीः", "प्रश्नः", "स्वागतम्", "शास्त्रम्"]


def iast_of(dev: str) -> str:
    return slp1_to_iast(dev_to_slp1(dev))


def letter_chart() -> dict:
    def row(chars):
        return [(c, iast_of(c)) for c in chars]
    return {
        "vowels": row(VOWELS_DEV),
        "vargas": [(name, row(chars)) for name, chars in VARGAS],
        "marks": [("ं", "ṃ anusvāra"), ("ः", "ḥ visarga"), ("्", "virāma"), ("ऽ", "avagraha")],
    }


def _mcq(prompt, correct, pool, rng, explanation, key, hint=""):
    opts, idx = _opts(correct, pool, rng)
    return Question("script", key, prompt, opts, idx, set(), explanation, hint)


def q_vowel(rng: random.Random) -> Question:
    c = rng.choice(VOWELS_DEV)
    ans = iast_of(c)
    if rng.random() < 0.5:
        return _mcq(f"What is the IAST for **{c}**?", ans, [iast_of(x) for x in VOWELS_DEV], rng,
                    f"{c} is *{ans}*.", "script:vowel")
    return _mcq(f"Which letter is **{ans}**?", c, VOWELS_DEV, rng, f"{ans} is written {c}.", "script:vowel")


def q_consonant(rng: random.Random) -> Question:
    c = rng.choice(CONSONANTS_DEV)
    ans = iast_of(c)
    mode = rng.random()
    if mode < 0.4:
        return _mcq(f"What is the IAST for **{c}**?", ans, [iast_of(x) for x in CONSONANTS_DEV], rng,
                    f"{c} is *{ans}*.", "script:consonant")
    if mode < 0.7:
        return _mcq(f"Which letter is **{ans}**?", c, CONSONANTS_DEV, rng, f"{ans} is written {c}.", "script:consonant")
    name, row = next((n, r) for n, r in VARGAS if c in r)
    return _mcq(f"**{c}** belongs to which class?", name, [n for n, _ in VARGAS], rng,
                f"{c} is in the {name} class.", "script:consonant")


def q_matra(rng: random.Random) -> Question:
    c = rng.choice(CONSONANTS_DEV[:25])
    m = rng.choice(MATRAS)
    word = c + m
    ans = iast_of(word)
    pool = [iast_of(c + x) for x in MATRAS if x != m]
    return _mcq(f"Read: **{word}**", ans, pool, rng, f"{word} = *{ans}*.", "script:matra",
                hint="Consonant + vowel sign")


def q_conjunct(rng: random.Random) -> Question:
    if rng.random() < 0.5:
        w = rng.choice(WORDS)
        ans = iast_of(w)
        pool = [iast_of(x) for x in WORDS]
        return _mcq(f"Read: **{w}**", ans, pool, rng, f"{w} = *{ans}*.", "script:conjunct")
    c = rng.choice(CONJUNCTS)
    ans = iast_of(c)
    pool = [iast_of(x) for x in CONJUNCTS]
    return _mcq(f"Read the conjunct: **{c}**", ans, pool, rng, f"{c} = *{ans}*.", "script:conjunct")


SCRIPT_GENERATORS = {"script_vowel": q_vowel, "script_consonant": q_consonant,
                     "script_matra": q_matra, "script_conjunct": q_conjunct}
