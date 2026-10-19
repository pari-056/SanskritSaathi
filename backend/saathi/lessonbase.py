"""Lesson data model shared by all content modules."""
from __future__ import annotations
from dataclasses import dataclass, field

LEVELS = {
    1: ("प्रारम्भः", "Foundations", "A1", "Script, sounds, first sentences"),
    2: ("अभ्यासः", "Elementary", "A2", "Cases, tenses, agreement"),
    3: ("मध्यमः", "Intermediate", "B1", "More stems, participles, sandhi, kāraka"),
    4: ("उन्नतम्", "Advanced", "B2+", "Compounds, voice, derivation, Pāṇini, meter, computation"),
}


@dataclass
class Lesson:
    id: str
    level: int
    unit: str
    title: str
    title_sa: str
    minutes: int
    summary: str
    body: str                                   # markdown
    vocab: list = field(default_factory=list)   # (devanagari, gloss)
    examples: list = field(default_factory=list)  # (devanagari sentence, translation)
    questions: list = field(default_factory=list)  # (prompt, correct, [wrongs], explanation)
    drills: list = field(default_factory=list)  # (generator kind, kwargs)
