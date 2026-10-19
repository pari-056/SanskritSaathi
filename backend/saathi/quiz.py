"""Quiz assembly: lesson quizzes, daily challenge, mixed review and placement test."""
from __future__ import annotations
import random
from datetime import date

from .content import LESSONS, BY_ID
from .lessonbase import Lesson
from . import practice, script
from .practice import Question

_GEN = {**practice.GENERATORS, **script.SCRIPT_GENERATORS}


def _from_tuple(lesson: Lesson, tup: tuple, rng: random.Random) -> Question:
    prompt, correct, wrongs, expl = tup
    opts = [correct] + list(wrongs)
    rng.shuffle(opts)
    return Question("mcq", f"lesson:{lesson.id}", prompt, opts, opts.index(correct), set(), expl,
                    level=lesson.level, source=lesson.id)


def _generated(spec: tuple, rng: random.Random, lesson: Lesson | None = None) -> Question:
    kind, kwargs = spec
    kw = {k: (tuple(v) if isinstance(v, list) and k in ("cases", "tenses", "numbers") else v) for k, v in kwargs.items()}
    q = _GEN[kind](rng, **kw)
    if lesson:
        q.level, q.source = lesson.level, lesson.id
    return q


def lesson_handwritten(lesson: Lesson, rng: random.Random) -> list[Question]:
    return [_from_tuple(lesson, t, rng) for t in lesson.questions]


def lesson_generated(lesson: Lesson, n: int, rng: random.Random) -> list[Question]:
    if not lesson.drills:
        return []
    qs, seen = [], set()
    for k in range(n * 6):
        if len(qs) >= n:
            break
        q = _generated(lesson.drills[k % len(lesson.drills)], rng, lesson)
        if q.prompt not in seen:
            seen.add(q.prompt)
            qs.append(q)
    return qs


def lesson_quiz(lesson: Lesson, rng: random.Random | None = None, total: int = 8) -> list[Question]:
    rng = rng or random.Random()
    hand = lesson_handwritten(lesson, rng)
    rng.shuffle(hand)
    hand = hand[: max(4, total - 3)] if lesson.drills else hand[:total]
    gen = lesson_generated(lesson, total - len(hand), rng)
    qs = hand + gen
    rng.shuffle(qs)
    return qs[:total]


def lesson_practice(lesson: Lesson, rng: random.Random | None = None, n: int = 6) -> list[Question]:
    rng = rng or random.Random()
    return lesson_generated(lesson, n, rng)


def _rng_for_day(name: str, d: date | None = None) -> random.Random:
    d = d or date.today()
    return random.Random(f"{name}:{d.isoformat()}")


def daily_challenge(progress, n: int = 10) -> list[Question]:
    rng = _rng_for_day(str(progress.data.get("seed", progress.data["name"])))
    opened = [BY_ID[i] for i in progress.data["lessons"] if i in BY_ID]
    pool = opened or [l for l in LESSONS if l.level == 1][:3]
    qs: list[Question] = []
    for _ in range(n * 3):
        if len(qs) >= n:
            break
        l = rng.choice(pool)
        if l.drills and rng.random() < 0.5:
            q = _generated(rng.choice(l.drills), rng, l)
        else:
            q = _from_tuple(l, rng.choice(l.questions), rng)
        if all(q.prompt != x.prompt for x in qs):
            qs.append(q)
    return qs


def review_quiz(level: int | None, n: int = 10, rng: random.Random | None = None, weak_first=None) -> list[Question]:
    rng = rng or random.Random()
    pool = [l for l in LESSONS if level is None or l.level <= level]
    qs: list[Question] = []
    tries = 0
    while len(qs) < n and tries < n * 6:
        tries += 1
        l = rng.choice(pool)
        if l.drills and rng.random() < 0.45:
            q = _generated(rng.choice(l.drills), rng, l)
        else:
            q = _from_tuple(l, rng.choice(l.questions), rng)
        if all(q.prompt != x.prompt for x in qs):
            qs.append(q)
    return qs


def placement_test(per_level: int = 4, rng: random.Random | None = None) -> list[Question]:
    rng = rng or random.Random()
    qs: list[Question] = []
    for lv in (1, 2, 3, 4):
        pool = [(l, t) for l in LESSONS if l.level == lv for t in l.questions]
        rng.shuffle(pool)
        for l, t in pool[:per_level]:
            qs.append(_from_tuple(l, t, rng))
    return qs


def placement_result(qs: list[Question], log: list[tuple]) -> dict:
    """log: [(question_index, picked_index, correct_bool)]."""
    per = {lv: [0, 0] for lv in (1, 2, 3, 4)}
    for i, _pick, ok in log:
        lv = qs[i].level
        per[lv][1] += 1
        per[lv][0] += int(ok)
    acc = {lv: (c / t if t else 0.0) for lv, (c, t) in per.items()}
    rec = 1
    for lv in (1, 2, 3):
        if acc[lv] >= 0.6:
            rec = lv + 1
        else:
            break
    return {"accuracy": acc, "recommended_level": rec, "counts": per}
