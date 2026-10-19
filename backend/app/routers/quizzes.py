from __future__ import annotations
import json
import random
import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from saathi import practice, quiz, script
from saathi.content import BY_ID
from ..db import get_db
from ..deps import ProgressHandle, progress_handle
from ..models import QuizSession
from ..ai import ai_client_or_none, consume_ai_quota
from ..config import get_settings
from ..schemas import AnswerIn, ExplainIn, QuizStartIn

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


def _ser(q: practice.Question) -> dict:
    d = asdict(q)
    d["answers_slp"] = []
    return d


def _public(i: int, q: dict) -> dict:
    return {"index": i, "prompt": q["prompt"], "options": q["options"], "hint": q.get("hint", "")}


def _own(db: Session, h: ProgressHandle, qid: str) -> QuizSession:
    s = db.get(QuizSession, qid)
    if not s or s.user_id != h.user.id:
        raise HTTPException(404, "Quiz not found")
    return s


@router.post("", status_code=201)
def start(body: QuizStartIn, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    rng = random.Random()
    lesson = None
    if body.kind in ("lesson", "practice"):
        lesson = BY_ID.get(body.lesson_id or "")
        if not lesson:
            raise HTTPException(404, "Lesson not found")
    if body.kind == "lesson":
        qs = quiz.lesson_quiz(lesson, rng)
    elif body.kind == "practice":
        qs = quiz.lesson_practice(lesson, rng)
        if not qs:
            raise HTTPException(400, "This lesson has no generated practice.")
    elif body.kind == "daily":
        qs = quiz.daily_challenge(h.p, 10)
    elif body.kind == "review":
        qs = quiz.review_quiz(body.level or 2, body.n, rng)
    elif body.kind == "placement":
        qs = quiz.placement_test(rng=rng)
    else:  # script drills
        gens = {"vowel": script.q_vowel, "consonant": script.q_consonant, "matra": script.q_matra,
                "conjunct": script.q_conjunct}
        chosen = [gens[k] for k in (body.script_kinds or list(gens))]
        qs, seen = [], set()
        for _ in range(body.n * 8):
            if len(qs) >= body.n:
                break
            q = rng.choice(chosen)(rng)
            if q.prompt not in seen:
                seen.add(q.prompt)
                qs.append(q)
    if not qs:
        raise HTTPException(400, "No questions available.")
    s = QuizSession(id=str(uuid.uuid4()), user_id=h.user.id, kind=body.kind,
                    lesson_id=lesson.id if lesson and body.kind == "lesson" else None,
                    questions=json.dumps([_ser(q) for q in qs], ensure_ascii=False))
    db.add(s)
    db.commit()
    return {"id": s.id, "kind": s.kind, "lesson_id": s.lesson_id, "total": len(qs),
            "questions": [_public(i, _ser(q)) for i, q in enumerate(qs)]}


@router.post("/{qid}/answer")
def answer(qid: str, body: AnswerIn, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    s = _own(db, h, qid)
    qs = json.loads(s.questions)
    log = json.loads(s.log)
    if s.finished:
        raise HTTPException(409, "Quiz already finished")
    if body.index >= len(qs):
        raise HTTPException(400, "No such question")
    q = qs[body.index]
    if body.pick >= len(q["options"]):
        raise HTTPException(400, "No such option")
    key = str(body.index)
    if key not in log:  # first answer counts; repeats just return the stored feedback
        ok = body.pick == q["answer_idx"]
        log[key] = {"pick": body.pick, "ok": ok}
        s.log = json.dumps(log)
        practice.Scheduler(h.p.weights).record(q["key"], ok)
        h.commit()  # commits the session row change too (same db session)
    rec = log[key]
    return {"correct": rec["ok"], "picked": rec["pick"], "correct_index": q["answer_idx"], "explanation": q["explanation"]}


@router.post("/{qid}/explain")
def explain(qid: str, body: ExplainIn, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    s = _own(db, h, qid)
    qs, log = json.loads(s.questions), json.loads(s.log)
    key = str(body.index)
    if key not in log:
        raise HTTPException(400, "Answer the question first.")
    client = ai_client_or_none()
    if client is None:
        raise HTTPException(503, "The AI tutor isn't configured on this server.")
    consume_ai_quota(db, h.user)
    q, rec = qs[body.index], log[key]
    from saathi import llm
    try:
        text = llm.one_shot(client, get_settings().gemini_model,
                            f"A learner answered a Sanskrit quiz question wrongly. Question: {q['prompt']}\n"
                            f"They chose: {q['options'][rec['pick']]}\nCorrect: {q['options'][q['answer_idx']]}\n"
                            f"Standard explanation: {q['explanation']}\n"
                            "Explain briefly and kindly why their choice is wrong and how to remember the right one.",
                            "Beginner", "Grammar", "English with Sanskrit")
    except Exception as e:
        raise HTTPException(502, llm.friendly_error(e))
    return {"explanation": text}


@router.post("/{qid}/finish")
def finish(qid: str, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    s = _own(db, h, qid)
    if s.finished and s.result:
        return json.loads(s.result)
    qs, log = json.loads(s.questions), json.loads(s.log)
    if len(log) < len(qs):
        raise HTTPException(400, f"Answer all questions first ({len(log)}/{len(qs)} answered).")
    correct = sum(1 for v in log.values() if v["ok"])
    total = len(qs)
    p = h.p
    out: dict = {"correct": correct, "total": total}
    if s.kind == "placement":
        res = quiz.placement_result([practice.Question(**{**q, "answers_slp": set()}) for q in qs],
                                    [(int(i), v["pick"], v["ok"]) for i, v in log.items()])
        res["accuracy"] = {str(k): v for k, v in res["accuracy"].items()}
        res["counts"] = {str(k): v for k, v in res["counts"].items()}
        p.data["placement"] = res
        out.update(xp=0, passed=True, newly_completed=False, placement=res)
    else:
        rec = p.record_quiz(s.lesson_id, correct, total)
        out.update(rec)
        if s.kind == "daily":
            from datetime import date
            today = date.today().isoformat()
            if p.data.get("daily_done") != today:
                p.data["daily_done"] = today
                p.add_xp(30)
                out["xp"] += 30
                out["daily_bonus"] = 30
    out["missed"] = [{"prompt": qs[int(i)]["prompt"], "chosen": qs[int(i)]["options"][v["pick"]],
                      "correct": qs[int(i)]["options"][qs[int(i)]["answer_idx"]],
                      "explanation": qs[int(i)]["explanation"]} for i, v in sorted(log.items(), key=lambda kv: int(kv[0]))
                     if not v["ok"]]
    s.finished = True
    s.result = json.dumps(out, ensure_ascii=False)
    h.commit()
    return out
