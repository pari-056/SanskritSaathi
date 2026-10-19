"""Flashcards, progress summary, script chart."""
from __future__ import annotations
import json

from fastapi import APIRouter, Depends, HTTPException

from saathi import script, vocab
from saathi.content import LESSONS
from saathi.progress import BADGES, DAILY_GOAL_XP
from ..deps import ProgressHandle, progress_handle
from ..schemas import ReviewIn

router = APIRouter(prefix="/api", tags=["learning"])


def _card(c: vocab.Card) -> dict:
    return {"id": c.id, "sanskrit": c.dev, "iast": c.iast, "meaning": c.gloss, "kind": c.kind}


@router.get("/flashcards/queue")
def queue(lexicon: bool = False, new: int = 8, h: ProgressHandle = Depends(progress_handle)):
    new = max(0, min(new, 30))
    cards = vocab.session_queue(h.p, lexicon, new)
    due = len(h.p.due_card_ids())
    return {"cards": [_card(c) for c in cards], "due": due, "new": max(len(cards) - due, 0), "mastered": h.p.mastered()}


@router.post("/flashcards/review")
def review(body: ReviewIn, h: ProgressHandle = Depends(progress_handle)):
    if body.card_id not in vocab.all_cards():
        raise HTTPException(404, "Unknown card")
    h.p.review_card(body.card_id, body.grade)
    h.commit()
    c = h.p.card(body.card_id)
    return {"box": c["box"], "due": c["due"]}


@router.get("/progress")
def summary(h: ProgressHandle = Depends(progress_handle)):
    p = h.p
    lvl, into, per = p.level()
    ids = [l.id for l in LESSONS]
    nxt = p.next_lesson(ids)
    weights = sorted(({"skill": k, "weight": round(v, 2)} for k, v in p.weights.items()), key=lambda r: -r["weight"])
    return {
        "display_name": h.user.display_name, "xp": p.data["xp"], "level": lvl, "xp_into_level": into, "xp_per_level": per,
        "streak": p.effective_streak(), "best_streak": p.data["best_streak"], "xp_today": p.xp_today(),
        "daily_goal": DAILY_GOAL_XP, "daily_done": p.data.get("daily_done") == p.today().isoformat(),
        "cards_due": len(p.due_card_ids()), "cards_mastered": p.mastered(),
        "lessons_completed": sum(1 for i in ids if p.is_complete(i)), "lessons_total": len(ids),
        "next_lesson": nxt, "placement": p.data.get("placement"),
        "badges": [{"id": b, "title": BADGES[b][0], "description": BADGES[b][1]} for b in p.data["badges"] if b in BADGES],
        "all_badges": [{"id": k, "title": v[0], "description": v[1], "earned": k in p.data["badges"]} for k, v in BADGES.items()],
        "skills": weights,
    }


@router.get("/progress/export")
def export(h: ProgressHandle = Depends(progress_handle)):
    return h.p.data


@router.post("/progress/import")
def import_progress(data: dict, h: ProgressHandle = Depends(progress_handle)):
    if "xp" not in data or not isinstance(data.get("lessons"), dict):
        raise HTTPException(400, "This doesn't look like a Sanskrit Saathi progress file.")
    if len(json.dumps(data)) > 500_000:
        raise HTTPException(413, "File too large.")
    from saathi.progress import _blank
    h.p.data = {**_blank(h.user.display_name), **data, "name": h.user.display_name, "seed": str(h.user.id)}
    h.commit()
    return {"ok": True}


@router.get("/script/chart")
def chart(_: ProgressHandle = Depends(progress_handle)):
    c = script.letter_chart()
    return {"vowels": [{"sanskrit": d, "iast": i} for d, i in c["vowels"]],
            "vargas": [{"name": n, "letters": [{"sanskrit": d, "iast": i} for d, i in row]} for n, row in c["vargas"]],
            "marks": [{"sanskrit": d, "iast": i} for d, i in c["marks"]],
            "matras": [{"sanskrit": "क" + m, "iast": script.iast_of("क" + m)} for m in script.MATRAS],
            "words": [{"sanskrit": w, "iast": script.iast_of(w)} for w in script.WORDS]}
