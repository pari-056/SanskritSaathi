from __future__ import annotations
import json

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .db import get_db
from .models import ProgressRow, User, utcnow
from .security import COOKIE_NAME, decode_session_token
from saathi.progress import Progress


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    uid = decode_session_token(token) if token else None
    user = db.get(User, uid) if uid else None
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Not signed in")
    return user


class ProgressHandle:
    """Loads a user's progress from the DB, and writes it back with commit()."""

    def __init__(self, db: Session, user: User):
        self.db, self.user = db, user
        self.row = db.get(ProgressRow, user.id)
        data = json.loads(self.row.data) if self.row and self.row.data else {}
        self.p = Progress.from_data(user.display_name, data)
        self.p.data["name"] = user.display_name
        self.p.data["seed"] = str(user.id)

    def commit(self):
        payload = json.dumps(self.p.data, ensure_ascii=False)
        if self.row is None:
            self.row = ProgressRow(user_id=self.user.id, data=payload)
            self.db.add(self.row)
        else:
            self.row.data = payload
            self.row.updated_at = utcnow()
        self.db.commit()


def progress_handle(user: User = Depends(current_user), db: Session = Depends(get_db)) -> ProgressHandle:
    return ProgressHandle(db, user)
