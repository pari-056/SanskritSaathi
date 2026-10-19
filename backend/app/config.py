"""Settings from environment variables (see .env.example)."""
from __future__ import annotations
import logging
import os
import secrets
from functools import lru_cache

from pydantic import BaseModel

log = logging.getLogger("saathi")


def _bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


class Settings(BaseModel):
    env: str = "development"
    secret_key: str
    database_url: str = "sqlite:///./saathi.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    cors_origins: list[str] = ["http://localhost:5173"]
    cookie_secure: bool = False
    session_days: int = 14
    ai_daily_limit: int = 60
    frontend_dist: str = "../frontend/dist"
    app_base_url: str = "http://localhost:5173"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Sanskrit Saathi <no-reply@localhost>"

    @property
    def production(self) -> bool:
        return self.env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "development")
    key = os.getenv("SECRET_KEY", "")
    if not key:
        if env == "production":
            raise RuntimeError("SECRET_KEY must be set in production (use: python -c \"import secrets;print(secrets.token_urlsafe(48))\")")
        key = secrets.token_urlsafe(48)
        log.warning("SECRET_KEY not set: using a temporary key. Sessions will reset when the server restarts.")
    return Settings(
        env=env,
        secret_key=key,
        database_url=os.getenv("DATABASE_URL", "sqlite:///./saathi.db"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        cors_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()],
        cookie_secure=_bool("COOKIE_SECURE", env == "production"),
        session_days=int(os.getenv("SESSION_DAYS", "14")),
        ai_daily_limit=int(os.getenv("AI_DAILY_LIMIT", "60")),
        frontend_dist=os.getenv("FRONTEND_DIST", "../frontend/dist"),
        app_base_url=os.getenv("APP_BASE_URL", "http://localhost:5173"),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from=os.getenv("SMTP_FROM", "Sanskrit Saathi <no-reply@localhost>"),
    )
