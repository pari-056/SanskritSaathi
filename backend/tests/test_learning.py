import random, sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from datetime import timedelta
from saathi import quiz, script, vocab
from saathi.content import LESSONS, BY_ID
from saathi.progress import Progress


def test_curriculum_shape():
    assert len(LESSONS) == 28 and len(BY_ID) == 28
    assert {l.level for l in LESSONS} == {1, 2, 3, 4}
    for l in LESSONS:
        assert l.body and l.questions and l.summary
        for prompt, correct, wrongs, expl in l.questions:
            opts = [correct] + list(wrongs)
            assert len(set(opts)) == len(opts), (l.id, prompt)
            assert expl


def test_every_lesson_quiz_is_valid():
    rng = random.Random(7)
    for l in LESSONS:
        qs = quiz.lesson_quiz(l, rng)
        assert qs
        for q in qs:
            assert 0 <= q.answer_idx < len(q.options) and len(set(q.options)) == len(q.options)


def test_script_generators():
    rng = random.Random(1)
    for g in script.SCRIPT_GENERATORS.values():
        for _ in range(25):
            q = g(rng)
            assert q.options[q.answer_idx] and len(set(q.options)) == len(q.options)
    assert script.iast_of("क्ष") == "kṣa" and script.iast_of("ऋ") == "ṛ"


def test_progress_xp_streak_and_lessons():
    p = Progress("t", tempfile.mkdtemp())
    p.open_lesson("1.1")
    r = p.record_quiz("1.1", 4, 5)
    assert r["passed"] and r["newly_completed"] and p.is_complete("1.1")
    r2 = p.record_quiz("1.2", 1, 5)
    assert not r2["passed"] and not p.is_complete("1.2")
    assert p.data["streak"] == 1 and "first_lesson" in p.data["badges"]
    # persistence
    p2 = Progress("t", p.dir)
    assert p2.is_complete("1.1") and p2.data["xp"] == p.data["xp"]


def test_streak_rollover():
    p = Progress("s", tempfile.mkdtemp(), persist=False)
    d0 = p.today()
    p.today = lambda: d0
    p.add_xp(5)
    p.today = lambda: d0 + timedelta(days=1)
    p.add_xp(5)
    assert p.data["streak"] == 2
    p.today = lambda: d0 + timedelta(days=4)
    assert p.effective_streak() == 0


def test_leitner_schedule():
    p = Progress("c", tempfile.mkdtemp(), persist=False)
    p.review_card("x", "good")
    assert p.card("x")["box"] == 1
    p.review_card("x", "easy")
    assert p.card("x")["box"] == 3
    p.review_card("x", "again")
    assert p.card("x")["box"] == 0 and "x" in p.due_card_ids()


def test_deck_and_placement():
    assert len(vocab.all_cards()) > 200
    qs = quiz.placement_test(rng=random.Random(3))
    assert len(qs) == 16
    all_right = [(i, q.answer_idx, True) for i, q in enumerate(qs)]
    assert quiz.placement_result(qs, all_right)["recommended_level"] == 4
    all_wrong = [(i, 0, False) for i, q in enumerate(qs)]
    assert quiz.placement_result(qs, all_wrong)["recommended_level"] == 1


def test_daily_challenge_is_deterministic():
    p = Progress("d", tempfile.mkdtemp(), persist=False)
    a = [q.prompt for q in quiz.daily_challenge(p)]
    b = [q.prompt for q in quiz.daily_challenge(p)]
    assert a == b and len(a) == 10
