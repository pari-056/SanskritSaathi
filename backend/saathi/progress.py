"""Learner progress: XP, streaks, lesson results, flashcard schedule, badges.

Stored as JSON on disk (one file per learner name) so progress survives restarts when the
app runs locally. On ephemeral hosting use the export/import buttons in the sidebar.
"""
from __future__ import annotations
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

BOX_DAYS = [0, 1, 2, 4, 8, 16, 32]   # Leitner intervals by box
XP_PER_LEVEL = 150
DAILY_GOAL_XP = 30
PASS_MARK = 0.7

BADGES = {
    "first_lesson": ("🌱 First steps", "Complete your first lesson"),
    "script_ready": ("🔤 Script reader", "Complete the three script lessons"),
    "level1": ("🏅 Foundations complete", "Complete every Level 1 lesson"),
    "sandhi_sage": ("🔗 Sandhi sage", "Complete the three sandhi lessons"),
    "perfect": ("💯 Perfect quiz", "Score 100% on a quiz"),
    "streak3": ("🔥 3-day streak", "Study three days in a row"),
    "streak7": ("🔥 7-day streak", "Study seven days in a row"),
    "cards50": ("🗂️ Card collector", "Review 50 flashcards"),
    "scholar": ("🎓 Pāṇini's apprentice", "Complete all 28 lessons"),
}


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip() or "learner")[:40]


def default_dir() -> Path:
    return Path(os.getenv("SAATHI_DATA_DIR", Path.home() / ".sanskrit_saathi"))


def _blank(name: str) -> dict:
    return {"name": name, "xp": 0, "streak": 0, "best_streak": 0, "last_day": None,
            "xp_by_day": {}, "lessons": {}, "cards": {}, "cards_reviewed": 0, "weights": {},
            "badges": [], "placement": None, "quizzes_taken": 0}


class Progress:
    def __init__(self, name: str = "Learner", directory: Path | None = None, persist: bool = True):
        self.dir = Path(directory) if directory else default_dir()
        self.persist = persist
        self.data = _blank(name)
        self.path = self.dir / f"progress_{_safe(name)}.json"
        self.load()

    @classmethod
    def from_data(cls, name: str, data: dict | None) -> "Progress":
        """In-memory progress backed by a dict (the web app stores it in the database)."""
        p = cls(name, persist=False)
        if data:
            p.data.update(data)
        return p

    # -- storage ----------------------------------------------------------------
    def load(self):
        if self.persist and self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        if not self.persist:
            return
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception:
            pass  # read-only hosting: progress simply stays in memory

    def export_json(self) -> str:
        return json.dumps(self.data, ensure_ascii=False, indent=1)

    def import_json(self, text: str):
        loaded = json.loads(text)
        if not isinstance(loaded, dict) or "xp" not in loaded:
            raise ValueError("Not a Sanskrit Saathi progress file")
        self.data = {**_blank(self.data["name"]), **loaded, "name": self.data["name"]}
        self.save()

    # -- xp / streak ----------------------------------------------------------------
    def today(self) -> date:
        return date.today()

    def touch_day(self):
        t = self.today()
        last = self.data["last_day"]
        if last == t.isoformat():
            return
        if last and date.fromisoformat(last) == t - timedelta(days=1):
            self.data["streak"] += 1
        else:
            self.data["streak"] = 1
        self.data["best_streak"] = max(self.data["best_streak"], self.data["streak"])
        self.data["last_day"] = t.isoformat()

    def effective_streak(self) -> int:
        last = self.data["last_day"]
        if not last:
            return 0
        gap = (self.today() - date.fromisoformat(last)).days
        return self.data["streak"] if gap <= 1 else 0

    def add_xp(self, n: int):
        self.touch_day()
        self.data["xp"] += n
        k = self.today().isoformat()
        self.data["xp_by_day"][k] = self.data["xp_by_day"].get(k, 0) + n
        self._check_badges()
        self.save()

    def xp_today(self) -> int:
        return self.data["xp_by_day"].get(self.today().isoformat(), 0)

    def level(self) -> tuple[int, int, int]:
        xp = self.data["xp"]
        lvl = xp // XP_PER_LEVEL + 1
        return lvl, xp % XP_PER_LEVEL, XP_PER_LEVEL

    # -- lessons -----------------------------------------------------------------------
    def open_lesson(self, lid: str):
        self.data["lessons"].setdefault(lid, {"best": 0.0, "attempts": 0, "completed": False})
        self.save()

    def lesson_state(self, lid: str) -> dict | None:
        return self.data["lessons"].get(lid)

    def is_complete(self, lid: str) -> bool:
        return bool((self.data["lessons"].get(lid) or {}).get("completed"))

    def record_quiz(self, lid: str | None, correct: int, total: int) -> dict:
        """Returns {'xp': int, 'passed': bool, 'newly_completed': bool}."""
        score = correct / max(total, 1)
        xp = correct * 5 + (10 if score == 1.0 and total >= 3 else 0)
        newly = False
        passed = score >= PASS_MARK
        self.data["quizzes_taken"] += 1
        if lid:
            st = self.data["lessons"].setdefault(lid, {"best": 0.0, "attempts": 0, "completed": False})
            st["attempts"] += 1
            st["best"] = max(st["best"], round(score, 3))
            if passed and not st["completed"]:
                st["completed"] = True
                newly = True
                xp += 20
        if score == 1.0 and total >= 3 and "perfect" not in self.data["badges"]:
            self.data["badges"].append("perfect")
        self.add_xp(xp)
        return {"xp": xp, "passed": passed, "newly_completed": newly}

    def level_progress(self, level: int, lesson_ids: list[str]) -> tuple[int, int]:
        done = sum(1 for i in lesson_ids if self.is_complete(i))
        return done, len(lesson_ids)

    def next_lesson(self, all_ids: list[str]) -> str | None:
        for i in all_ids:
            if not self.is_complete(i):
                return i
        return None

    # -- flashcards (Leitner) ----------------------------------------------------------------
    def card(self, cid: str) -> dict | None:
        return self.data["cards"].get(cid)

    def review_card(self, cid: str, grade: str):
        """grade: 'again' | 'good' | 'easy'."""
        c = self.data["cards"].setdefault(cid, {"box": 0, "due": self.today().isoformat(), "seen": 0})
        c["seen"] += 1
        if grade == "again":
            c["box"] = 0
        elif grade == "good":
            c["box"] = min(c["box"] + 1, len(BOX_DAYS) - 1)
        else:
            c["box"] = min(c["box"] + 2, len(BOX_DAYS) - 1)
        c["due"] = (self.today() + timedelta(days=BOX_DAYS[c["box"]])).isoformat()
        self.data["cards_reviewed"] += 1
        self.add_xp(1)

    def due_card_ids(self) -> list[str]:
        t = self.today().isoformat()
        return sorted((cid for cid, c in self.data["cards"].items() if c["due"] <= t),
                      key=lambda cid: self.data["cards"][cid]["due"])

    def known_card_ids(self) -> set[str]:
        return set(self.data["cards"])

    def mastered(self) -> int:
        return sum(1 for c in self.data["cards"].values() if c["box"] >= 4)

    # -- badges -------------------------------------------------------------------------------
    def _check_badges(self):
        from .content import LESSONS
        b = self.data["badges"]
        done = {l.id for l in LESSONS if self.is_complete(l.id)}

        def add(k):
            if k not in b:
                b.append(k)
        if done:
            add("first_lesson")
        if {"1.1", "1.2", "1.3"} <= done:
            add("script_ready")
        if {l.id for l in LESSONS if l.level == 1} <= done:
            add("level1")
        if {"3.5", "3.6", "3.7"} <= done:
            add("sandhi_sage")
        if self.data["streak"] >= 3:
            add("streak3")
        if self.data["streak"] >= 7:
            add("streak7")
        if self.data["cards_reviewed"] >= 50:
            add("cards50")
        if len(done) == len(LESSONS):
            add("scholar")

    # -- adaptive weights shared with practice.Scheduler ---------------------------------------
    @property
    def weights(self) -> dict:
        return self.data["weights"]
