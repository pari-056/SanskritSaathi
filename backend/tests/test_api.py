import json
from conftest import signup
from fastapi.testclient import TestClient


# ---------------- auth ----------------
def test_register_login_logout_me(client):
    u = signup(client)
    assert u["email"] == "a@example.com" and "password" not in json.dumps(u)
    assert client.get("/api/auth/me").json()["display_name"] == "Asha"
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    r = client.post("/api/auth/login", json={"email": "A@Example.com", "password": "correct-horse"})
    assert r.status_code == 200 and client.get("/api/auth/me").status_code == 200


def test_cookie_is_httponly_and_samesite(client):
    r = client.post("/api/auth/register", json={"email": "c@example.com", "password": "password123", "display_name": "C"})
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_validation_and_duplicates(client):
    assert client.post("/api/auth/register", json={"email": "nope", "password": "longenough1", "display_name": "x"}).status_code == 422
    assert client.post("/api/auth/register", json={"email": "a@example.com", "password": "short", "display_name": "x"}).status_code == 422
    signup(client)
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "another-pass1", "display_name": "B"})
    assert r.status_code == 409


def test_wrong_password_is_generic_and_rate_limited(client):
    signup(client)
    client.post("/api/auth/logout")
    for _ in range(8):
        r = client.post("/api/auth/login", json={"email": "a@example.com", "password": "bad-password"})
        assert r.status_code == 401 and r.json()["detail"] == "Incorrect email or password."
    assert client.post("/api/auth/login", json={"email": "a@example.com", "password": "bad-password"}).status_code == 429
    # unknown user gives the same message
    r = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "whatever1"})
    assert r.status_code == 401 and r.json()["detail"] == "Incorrect email or password."


def test_csrf_header_required(client):
    bare = TestClient(client.app)  # no X-Requested-With
    r = bare.post("/api/auth/login", json={"email": "a@example.com", "password": "x"})
    assert r.status_code == 403


def test_password_hash_not_plaintext(client):
    signup(client)
    from app.db import get_engine
    from sqlalchemy import text
    with get_engine().connect() as c:
        h = c.execute(text("select password_hash from users")).scalar()
    assert h.startswith("scrypt$") and "correct-horse" not in h


def test_password_reset_flow(client, monkeypatch):
    signup(client)
    client.post("/api/auth/logout")
    sent = {}
    import app.routers.auth as auth_mod
    monkeypatch.setattr(auth_mod, "send_email", lambda to, subj, body: sent.update(to=to, body=body))
    assert client.post("/api/auth/forgot", json={"email": "nobody@example.com"}).status_code == 200
    assert not sent  # no email for unknown accounts, same response
    assert client.post("/api/auth/forgot", json={"email": "a@example.com"}).status_code == 200
    token = sent["body"].split("token=")[1].split()[0]
    assert client.post("/api/auth/reset", json={"token": token, "password": "brand-new-pass"}).status_code == 200
    assert client.post("/api/auth/reset", json={"token": token, "password": "again-again1"}).status_code == 400  # single use
    assert client.post("/api/auth/login", json={"email": "a@example.com", "password": "correct-horse"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "a@example.com", "password": "brand-new-pass"}).status_code == 200


def test_change_password_and_delete_account(client):
    signup(client)
    assert client.post("/api/auth/change-password", json={"current_password": "wrong", "new_password": "newpassword1"}).status_code == 400
    assert client.post("/api/auth/change-password", json={"current_password": "correct-horse", "new_password": "newpassword1"}).status_code == 204
    assert client.post("/api/auth/delete-account", json={"password": "nope"}).status_code == 400
    assert client.post("/api/auth/delete-account", json={"password": "newpassword1"}).status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/login", json={"email": "a@example.com", "password": "newpassword1"}).status_code == 401


def test_endpoints_require_login(client):
    for path in ("/api/levels", "/api/progress", "/api/flashcards/queue", "/api/lab/stems", "/api/script/chart"):
        assert client.get(path).status_code == 401, path


# ---------------- course content ----------------
def test_levels_and_lessons(user, client):
    lv = client.get("/api/levels").json()
    assert [l["level"] for l in lv] == [1, 2, 3, 4] and sum(len(l["lessons"]) for l in lv) == 28
    les = client.get("/api/lessons/1.4").json()
    assert les["title"] and les["vocab"][0]["iast"] and les["next"] == "1.5" and les["prev"] == "1.3"
    assert client.get("/api/lessons/9.9").status_code == 404
    assert client.post("/api/lessons/1.4/open").status_code == 204
    assert client.get("/api/lessons/1.4").json()["state"]["opened"] is True


# ---------------- quizzes ----------------
def _answer_all(client, quiz, correct=True):
    for q in quiz["questions"]:
        # find the right index by probing: first answer a wrong option? answers are single-shot, so use a second quiz-free trick:
        r = client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": q["index"], "pick": 0}).json()
        yield r


def test_quiz_flow_grades_on_server_and_awards_xp(user, client):
    quiz = client.post("/api/quizzes", json={"kind": "lesson", "lesson_id": "1.1"}).json()
    assert quiz["total"] == 8 and "answer_idx" not in json.dumps(quiz) and "explanation" not in json.dumps(quiz)
    # can't finish early
    assert client.post(f"/api/quizzes/{quiz['id']}/finish").status_code == 400
    # answer each question once with option 0, then learn the correct index from feedback
    first = {}
    for q in quiz["questions"]:
        r = client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": q["index"], "pick": 0}).json()
        first[q["index"]] = r
        # repeating the answer must NOT change the stored result
        again = client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": q["index"], "pick": r["correct_index"]}).json()
        assert again["correct"] == r["correct"] and again["picked"] == 0
    expected = sum(1 for r in first.values() if r["correct"])
    res = client.post(f"/api/quizzes/{quiz['id']}/finish").json()
    assert res["correct"] == expected and res["total"] == 8
    assert res["xp"] >= expected * 5
    # idempotent finish
    assert client.post(f"/api/quizzes/{quiz['id']}/finish").json() == res
    assert client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": 0, "pick": 0}).status_code == 409
    prog = client.get("/api/progress").json()
    assert prog["xp"] == res["xp"]


def _perfect(client, quiz):
    """Answer correctly: query a throwaway copy? Not possible, so read the truth from the DB (test-only)."""
    import json as j
    from app.db import get_engine
    from sqlalchemy import text
    with get_engine().connect() as c:
        qs = j.loads(c.execute(text("select questions from quiz_sessions where id=:i"), {"i": quiz["id"]}).scalar())
    for q in quiz["questions"]:
        client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": q["index"], "pick": qs[q["index"]]["answer_idx"]})


def test_perfect_quiz_completes_lesson_and_badges(user, client):
    quiz = client.post("/api/quizzes", json={"kind": "lesson", "lesson_id": "1.2"}).json()
    _perfect(client, quiz)
    res = client.post(f"/api/quizzes/{quiz['id']}/finish").json()
    assert res["passed"] and res["newly_completed"] and res["correct"] == res["total"]
    lv = client.get("/api/levels").json()
    assert next(l for l in lv[0]["lessons"] if l["id"] == "1.2")["completed"] is True
    badges = {b["id"] for b in client.get("/api/progress").json()["badges"]}
    assert {"first_lesson", "perfect"} <= badges


def test_daily_challenge_bonus_once(user, client):
    client.post("/api/lessons/1.1/open")
    for _ in range(2):
        quiz = client.post("/api/quizzes", json={"kind": "daily"}).json()
        _perfect(client, quiz)
        res = client.post(f"/api/quizzes/{quiz['id']}/finish").json()
        if _ == 0:
            assert res["daily_bonus"] == 30
        else:
            assert "daily_bonus" not in res


def test_placement_saves_recommendation(user, client):
    quiz = client.post("/api/quizzes", json={"kind": "placement"}).json()
    assert quiz["total"] == 16
    _perfect(client, quiz)
    res = client.post(f"/api/quizzes/{quiz['id']}/finish").json()
    assert res["placement"]["recommended_level"] == 4 and res["xp"] == 0
    assert client.get("/api/progress").json()["placement"]["recommended_level"] == 4


def test_quiz_isolated_between_users(user, client):
    quiz = client.post("/api/quizzes", json={"kind": "lesson", "lesson_id": "1.1"}).json()
    client.post("/api/auth/logout")
    signup(client, "b@example.com", "another-pass1", "Bo")
    assert client.post(f"/api/quizzes/{quiz['id']}/answer", json={"index": 0, "pick": 0}).status_code == 404
    assert client.post(f"/api/quizzes/{quiz['id']}/finish").status_code == 404


def test_progress_is_per_user(user, client):
    quiz = client.post("/api/quizzes", json={"kind": "lesson", "lesson_id": "1.1"}).json()
    _perfect(client, quiz)
    client.post(f"/api/quizzes/{quiz['id']}/finish")
    assert client.get("/api/progress").json()["xp"] > 0
    client.post("/api/auth/logout")
    signup(client, "b@example.com", "another-pass1", "Bo")
    assert client.get("/api/progress").json()["xp"] == 0


def test_script_and_review_quizzes(user, client):
    q = client.post("/api/quizzes", json={"kind": "script", "n": 5, "script_kinds": ["vowel", "matra"]}).json()
    assert q["total"] == 5
    q = client.post("/api/quizzes", json={"kind": "review", "level": 3, "n": 6}).json()
    assert q["total"] == 6
    assert client.post("/api/quizzes", json={"kind": "lesson"}).status_code == 404
    assert client.post("/api/quizzes", json={"kind": "bogus"}).status_code == 422


# ---------------- flashcards / progress ----------------
def test_flashcards_cycle(user, client):
    assert client.get("/api/flashcards/queue").json()["cards"] == []
    client.post("/api/lessons/1.4/open")
    q = client.get("/api/flashcards/queue?new=3").json()
    assert 0 < len(q["cards"]) <= 3
    cid = q["cards"][0]["id"]
    r = client.post("/api/flashcards/review", json={"card_id": cid, "grade": "good"}).json()
    assert r["box"] == 1
    assert client.post("/api/flashcards/review", json={"card_id": "nope", "grade": "good"}).status_code == 404
    assert client.post("/api/flashcards/review", json={"card_id": cid, "grade": "meh"}).status_code == 422


def test_export_import(user, client):
    client.post("/api/lessons/1.1/open")
    data = client.get("/api/progress/export").json()
    assert "1.1" in data["lessons"]
    assert client.post("/api/progress/import", json={"bogus": 1}).status_code == 400
    data["xp"] = 999
    assert client.post("/api/progress/import", json=data).status_code == 200
    assert client.get("/api/progress").json()["xp"] == 999


# ---------------- lab ----------------
def test_lab_endpoints(user, client):
    s = client.post("/api/lab/sentence", json={"text": "अहं गच्छति"}).json()
    assert any(i["severity"] == "error" and "गच्छामि" in i["suggestion"] for i in s["issues"])
    w = client.post("/api/lab/word", json={"text": "गच्छन्ति"}).json()
    assert w["found"] and "गम्" in w["analyses"][0]["lemma"]
    j = client.post("/api/lab/sandhi/join", json={"first": "रामः", "second": "अस्ति"}).json()
    assert j["result"]["devanagari"] == "रामोऽस्ति"
    sp = client.post("/api/lab/sandhi/split", json={"text": "तत्रेति"}).json()
    assert ["तत्र", "इति"] in sp["splits"]
    t = client.post("/api/lab/transliterate", json={"text": "rAmaH"}).json()
    assert t["devanagari"] == "रामः" and t["iast"] == "rāmaḥ"
    stems = client.get("/api/lab/stems").json()
    assert stems["n_forms"] > 3000
    p = client.get("/api/lab/paradigm", params={"key": "rAma"}).json()
    assert p["tables"][0]["rows"][2]["sg"] == "रामेण"
    v = client.get("/api/lab/paradigm", params={"key": "√gam", "tense": "lan"}).json()
    assert v["rows"][0]["sg"] == "अगच्छत्"
    assert client.get("/api/lab/paradigm", params={"key": "zzz"}).status_code == 404
    sc = client.get("/api/lab/selfcheck").json()
    assert sc["sandhi"]["accuracy"] == 1.0 and sc["morphology"]["accuracy"] == 1.0
    assert client.get("/api/script/chart").json()["vowels"][0]["iast"] == "a"


# ---------------- tutor ----------------
def test_tutor_demo_mode(user, client):
    r = client.post("/api/tutor/chat", json={"messages": [{"role": "user", "content": "decline राम"}]}).json()
    assert r["demo"] is True and "रामेण" in r["reply"]
    assert client.get("/api/tutor/status").json()["ai_enabled"] is False
    assert client.post("/api/tutor/chat", json={"messages": [{"role": "assistant", "content": "x"}]}).status_code == 422


def test_tutor_ai_mode_quota_and_error_mapping(user, client, monkeypatch):
    from app.config import get_settings
    import app.ai as ai
    import app.routers.tutor as tutor
    from saathi import llm
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("AI_DAILY_LIMIT", "2")
    get_settings.cache_clear()
    monkeypatch.setattr(ai, "_client", lambda key: object())
    calls = {}

    def fake_chat(client_, model, msgs, level, focus, language, use_tools, extra):
        calls["extra"] = extra
        return llm.ChatResult("उत्तमम्!", ["analyze_sanskrit_word(word='x')"])
    monkeypatch.setattr(llm, "chat_reply", fake_chat)
    body = {"messages": [{"role": "user", "content": "hi"}], "lesson_id": "1.1"}
    r = client.post("/api/tutor/chat", json=body).json()
    assert r["reply"] == "उत्तमम्!" and r["demo"] is False and r["remaining"] == 1 and "Lesson 1.1" in calls["extra"]
    assert client.post("/api/tutor/chat", json=body).json()["remaining"] == 0
    assert client.post("/api/tutor/chat", json=body).status_code == 429

    get_settings.cache_clear()
    monkeypatch.setenv("AI_DAILY_LIMIT", "50")
    get_settings.cache_clear()
    def boom(*a, **k):
        raise RuntimeError("down")
    monkeypatch.setattr(llm, "chat_reply", boom)
    assert client.post("/api/tutor/chat", json=body).status_code == 502


def test_health_and_security_headers(client):
    r = client.get("/api/health")
    assert r.json() == {"status": "ok"} and r.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]


def test_spa_is_served_and_cannot_read_outside_dist(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<div id='root'></div>")
    (dist / "assets" / "app.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("TOP SECRET")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'s.db'}")
    monkeypatch.setenv("SECRET_KEY", "x" * 40)
    monkeypatch.setenv("FRONTEND_DIST", str(dist))
    from app.config import get_settings
    from app.db import reset_engine
    get_settings.cache_clear(); reset_engine()
    from app.main import create_app
    with TestClient(create_app()) as c:
        assert "root" in c.get("/learn/1.1").text            # SPA fallback
        assert c.get("/assets/app.js").status_code == 200
        assert c.get("/api/nope").status_code == 404           # API 404s stay JSON
        for p in ("/../secret.txt", "/%2e%2e/secret.txt", "/..%2fsecret.txt"):
            assert "TOP SECRET" not in c.get(p).text
    reset_engine(); get_settings.cache_clear()


def test_production_requires_secret_key(monkeypatch):
    from app.config import get_settings
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    get_settings.cache_clear()
    import pytest
    with pytest.raises(RuntimeError):
        get_settings()
    get_settings.cache_clear()


def test_verb_explorer(user, client):
    r = client.get("/api/lab/verbs", params={"q": "गम्"}).json()
    assert r["total"] >= 1 and any(x["gana"] == 1 and x["iast"] == "gam" for x in r["results"])
    key = next(x["key"] for x in r["results"] if x["gana"] == 1)
    t = client.get(f"/api/lab/verbs/{key}", params={"voice": "act", "tense": "lan"}).json()
    assert t["rows"][0]["sg"] == "अगच्छत्" and "kta" in " ".join(t["principal_parts"]).lower() or t["principal_parts"]
    assert "pass" in t["available"] and any(x["id"] == "lit" for x in t["available"]["act"])
    m = client.get("/api/lab/verbs", params={"q": "laB"}).json()["results"][0]["key"]
    mid = client.get(f"/api/lab/verbs/{m}", params={"voice": "mid", "tense": "lat"}).json()
    assert mid["rows"][0]["sg"] == "लभते"
    assert client.get("/api/lab/verbs/99.9999").status_code == 404
    assert client.get(f"/api/lab/verbs/{key}", params={"voice": "zzz"}).status_code == 400
    assert client.get("/api/lab/verbs", params={"q": ""}).status_code in (400, 422)


def test_word_endpoint_handles_prefixed_and_ambiguous_forms(user, client):
    w = client.post("/api/lab/word", json={"text": "आगच्छति"}).json()
    assert w["found"] and any("A" in a["lemma"] or "आ" in a["lemma"] for a in w["analyses"])
    assert len(w["analyses"]) <= 40 and w["total"] >= len(w["analyses"])
