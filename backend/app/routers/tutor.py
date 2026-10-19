from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from saathi import llm
from saathi.content import BY_ID
from saathi.demo import demo_reply
from ..ai import ai_client_or_none, consume_ai_quota
from ..config import get_settings
from ..db import get_db
from ..deps import ProgressHandle, progress_handle
from ..schemas import ChatIn, SentenceIn

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def lesson_context(lid: str | None) -> str:
    l = BY_ID.get(lid or "")
    return f"Lesson {l.id} ({l.title}, level {l.level}): {l.summary}\n\n{l.body[:2800]}" if l else ""


@router.get("/status")
def status(_: ProgressHandle = Depends(progress_handle)):
    s = get_settings()
    return {"ai_enabled": bool(s.gemini_api_key), "model": s.gemini_model if s.gemini_api_key else None,
            "daily_limit": s.ai_daily_limit}


@router.post("/chat")
def chat(body: ChatIn, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    client = ai_client_or_none()
    msgs = [m.model_dump() for m in body.messages]
    if client is None:
        return {"reply": demo_reply(msgs[-1]["content"], body.level, body.focus), "tool_calls": [], "demo": True,
                "remaining": None}
    remaining = consume_ai_quota(db, h.user)
    try:
        res = llm.chat_reply(client, get_settings().gemini_model, msgs, body.level, body.focus, body.language,
                             body.use_tools, lesson_context(body.lesson_id))
    except Exception as e:
        raise HTTPException(502, llm.friendly_error(e))
    return {"reply": res.text, "tool_calls": res.tool_calls, "demo": False, "remaining": remaining}


@router.post("/analyze")
def analyze(body: SentenceIn, h: ProgressHandle = Depends(progress_handle), db: Session = Depends(get_db)):
    """Gemini's structured parse of a sentence, cross-checked against the rule engine."""
    client = ai_client_or_none()
    if client is None:
        raise HTTPException(503, "The AI tutor isn't configured on this server.")
    consume_ai_quota(db, h.user)
    try:
        parsed, checks = llm.analyze_sentence_ai(client, get_settings().gemini_model, body.text, "Beginner",
                                                 "English with Sanskrit")
    except Exception as e:
        raise HTTPException(502, llm.friendly_error(e))
    return {"analysis": parsed.model_dump(),
            "checks": [{"surface": c.token.surface, "verdict": c.verdict, "detail": c.detail} for c in checks]}
