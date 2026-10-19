"""Flashcard deck built from the lexicon and the lessons' vocabulary."""
from __future__ import annotations
import random
from dataclasses import dataclass

from . import lexicon as lx
from .content import LESSONS
from .translit import dev_to_slp1, slp1_to_dev, slp1_to_iast
from .morph import conjugate


@dataclass(frozen=True)
class Card:
    id: str
    dev: str
    iast: str
    gloss: str
    kind: str          # lesson | noun | verb | adj | indecl
    level: int
    source: str = ""   # lesson id, if any


def _iast(dev: str) -> str:
    return slp1_to_iast(dev_to_slp1(dev))


def lesson_cards() -> list[Card]:
    cards = []
    for l in LESSONS:
        for dev, gloss in l.vocab:
            cards.append(Card(f"L:{dev}", dev, _iast(dev), gloss, "lesson", l.level, l.id))
    return cards


def lexicon_cards() -> list[Card]:
    cards = []
    for stem, cls, gender, gloss in lx.NOUNS:
        g = {"m": "m.", "f": "f.", "n": "n."}[gender]
        dev = slp1_to_dev(stem)
        cards.append(Card(f"N:{stem}", dev, slp1_to_iast(stem), f"{gloss} ({g})", "noun", 2))
    for stem, gloss, fems in lx.ADJECTIVES:
        cards.append(Card(f"A:{stem}", slp1_to_dev(stem), slp1_to_iast(stem), f"{gloss} (adj.)", "adj", 2))
    for root, gloss, *_ in lx.VERBS:
        form = conjugate(root, "lat")[(3, "sg")]
        cards.append(Card(f"V:{root}", slp1_to_dev(form), slp1_to_iast(form), f"{gloss} (√{slp1_to_dev(root)})", "verb", 1))
    for form, gloss in lx.INDECLINABLES:
        cards.append(Card(f"I:{form}", slp1_to_dev(form), slp1_to_iast(form), f"{gloss}", "indecl", 2))
    return cards


_ALL: dict[str, Card] | None = None


def all_cards() -> dict[str, Card]:
    global _ALL
    if _ALL is None:
        _ALL = {}
        for c in lesson_cards() + lexicon_cards():
            _ALL.setdefault(c.id, c)
    return _ALL


def unlocked_new_cards(progress, include_lexicon: bool, limit: int = 10) -> list[Card]:
    """New (never reviewed) cards: vocabulary of lessons the learner has opened, plus optionally the lexicon."""
    known = progress.known_card_ids()
    opened = set(progress.data["lessons"])
    out = [c for c in all_cards().values()
           if c.id not in known and ((c.kind == "lesson" and c.source in opened) or (include_lexicon and c.kind != "lesson"))]
    return out[:limit]


def session_queue(progress, include_lexicon: bool = False, new_limit: int = 8) -> list[Card]:
    cards = all_cards()
    due = [cards[cid] for cid in progress.due_card_ids() if cid in cards]
    return due + unlocked_new_cards(progress, include_lexicon, new_limit)


def distractors(card: Card, n: int = 3, rng: random.Random | None = None) -> list[str]:
    rng = rng or random
    pool = [c.gloss for c in all_cards().values() if c.gloss != card.gloss]
    return rng.sample(pool, n)
