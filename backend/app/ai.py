"""Server-side Gemini access with a per-user daily quota (the API key never reaches the browser)."""
from __future__ import annotations
from datetime import date
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .config import get_settings
from .models import AiUsage, User


@lru_cache(maxsize=1)
def _client(key: str):
    from saathi import llm
    return llm.make_client(key)


def ai_client_or_none():
    key = get_settings().gemini_api_key
    return _client(key) if key else None


def consume_ai_quota(db: Session, user: User) -> int:
    """Count one AI call for today; raise 429 when the daily limit is used up. Returns remaining calls."""
    limit = get_settings().ai_daily_limit
    today = date.today().isoformat()
    row = db.get(AiUsage, (user.id, today))
    if row is None:
        row = AiUsage(user_id=user.id, day=today, count=0)
        db.add(row)
    if row.count >= limit:
        raise HTTPException(429, f"Daily AI limit reached ({limit} requests). It resets tomorrow.")
    row.count += 1
    db.commit()
    return limit - row.count
