import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'t.db'}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-test-secret-key-0123456789")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("WARM_ENGINE", "0")
    monkeypatch.setenv("FRONTEND_DIST", str(tmp_path / "nodist"))
    from app.config import get_settings
    from app.db import reset_engine
    from app.security import limiter
    get_settings.cache_clear()
    reset_engine()
    limiter.reset()
    from app.main import create_app
    app = create_app()
    with TestClient(app, headers={"X-Requested-With": "saathi"}) as c:
        yield c
    reset_engine()
    get_settings.cache_clear()


def signup(client, email="a@example.com", password="correct-horse", name="Asha"):
    r = client.post("/api/auth/register", json={"email": email, "password": password, "display_name": name})
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def user(client):
    return signup(client)


def play_quiz(client, qid, questions, pick_correct=True, answers=None):
    """Answer every question (correct if pick_correct) using the server's feedback to learn the right index."""
    results = []
    for q in questions:
        probe = client.post(f"/api/quizzes/{qid}/answer", json={"index": q["index"], "pick": 0}).json()
        results.append(probe)
    return results
