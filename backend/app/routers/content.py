from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from saathi.content import BY_ID, LESSONS
from saathi.lessonbase import LEVELS
from saathi.translit import dev_to_slp1, slp1_to_iast
from ..deps import ProgressHandle, progress_handle

router = APIRouter(prefix="/api", tags=["course"])


def _iast(dev: str) -> str:
    return slp1_to_iast(dev_to_slp1(dev))


def _state(p, lid: str) -> dict:
    s = p.lesson_state(lid) or {}
    return {"opened": lid in p.data["lessons"], "completed": bool(s.get("completed")),
            "best": s.get("best", 0.0), "attempts": s.get("attempts", 0)}


@router.get("/levels")
def levels(h: ProgressHandle = Depends(progress_handle)):
    p = h.p
    out = []
    for lv, (sa, en, cefr, desc) in LEVELS.items():
        lessons = [{"id": l.id, "title": l.title, "title_sa": l.title_sa, "unit": l.unit, "minutes": l.minutes,
                    "summary": l.summary, **_state(p, l.id)} for l in LESSONS if l.level == lv]
        out.append({"level": lv, "title_sa": sa, "title": en, "cefr": cefr, "description": desc,
                    "completed": sum(1 for x in lessons if x["completed"]), "lessons": lessons})
    return out


@router.get("/lessons/{lesson_id}")
def lesson(lesson_id: str, h: ProgressHandle = Depends(progress_handle)):
    l = BY_ID.get(lesson_id)
    if not l:
        raise HTTPException(404, "Lesson not found")
    ids = [x.id for x in LESSONS]
    i = ids.index(l.id)
    return {
        "id": l.id, "level": l.level, "unit": l.unit, "title": l.title, "title_sa": l.title_sa, "minutes": l.minutes,
        "summary": l.summary, "body": l.body,
        "vocab": [{"sanskrit": d, "iast": _iast(d), "meaning": g} for d, g in l.vocab],
        "examples": [{"sanskrit": s, "iast": _iast(s) if "→" not in s and "+" not in s else "", "translation": t,
                      "analysable": "→" not in s and "+" not in s} for s, t in l.examples],
        "has_practice": bool(l.drills), "prev": ids[i - 1] if i > 0 else None,
        "next": ids[i + 1] if i + 1 < len(ids) else None, "state": _state(h.p, l.id),
    }


@router.post("/lessons/{lesson_id}/open", status_code=204)
def open_lesson(lesson_id: str, h: ProgressHandle = Depends(progress_handle)):
    if lesson_id not in BY_ID:
        raise HTTPException(404, "Lesson not found")
    h.p.open_lesson(lesson_id)
    h.commit()
