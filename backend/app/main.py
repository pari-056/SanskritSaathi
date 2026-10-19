from __future__ import annotations
import logging
import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings
from .db import init_db
from .routers import auth, content, lab, learning, quizzes, tutor

logging.basicConfig(level=logging.INFO)
CSRF_HEADER = "x-requested-with"


class SecurityMiddleware(BaseHTTPMiddleware):
    """CSRF guard for the cookie session + standard security headers."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api") and request.method not in ("GET", "HEAD", "OPTIONS"):
            if request.headers.get(CSRF_HEADER) != "saathi":
                return JSONResponse({"detail": "Missing CSRF header"}, status_code=403)
        resp = await call_next(request)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if not request.url.path.startswith(("/docs", "/redoc", "/openapi")):
            resp.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
        return resp


def _warm_engine():
    """Build the verb index in the background so the first learner request is not slow (about 2 s, ~210 MB)."""
    try:
        from saathi import morph
        an = morph.get_analyzer()
        an.verb_layer  # noqa: B018
        an.splitter    # noqa: B018
    except Exception:
        logging.getLogger("saathi").exception("engine warm-up failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if os.getenv("WARM_ENGINE", "1") != "0":
        threading.Thread(target=_warm_engine, daemon=True, name="engine-warm").start()
    yield


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="Sanskrit Saathi API", version="1.0.0", lifespan=lifespan,
                  docs_url=None if s.production else "/docs", redoc_url=None, openapi_url=None if s.production else "/openapi.json")
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origins, allow_credentials=True,
                       allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "X-Requested-With"])
    for r in (auth.router, content.router, quizzes.router, learning.router, lab.router, tutor.router):
        app.include_router(r)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    dist = Path(s.frontend_dist)
    if not dist.is_absolute():
        dist = (Path(__file__).resolve().parent.parent / dist).resolve()
    if (dist / "index.html").exists():
        if (dist / "assets").exists():
            app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            if path.startswith("api/"):
                return JSONResponse({"detail": "Not found"}, status_code=404)
            f = (dist / path).resolve()
            if path and f.is_file() and dist in f.parents:
                return FileResponse(f)
            return FileResponse(dist / "index.html")
    return app


app = create_app()
