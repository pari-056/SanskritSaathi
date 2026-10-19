from __future__ import annotations
import logging
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import current_user
from ..mailer import send_email
from ..models import ResetToken, User, utcnow
from ..schemas import (ChangePasswordIn, DeleteAccountIn, ForgotIn, LoginIn, RegisterIn, ResetIn, UserOut)
from ..security import (COOKIE_NAME, DUMMY_HASH, create_session_token, hash_password, hash_token, limiter,
                        verify_password)

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = logging.getLogger("saathi.auth")


def _ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    return (fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown"))


def _set_cookie(response: Response, user_id: int):
    s = get_settings()
    response.set_cookie(COOKIE_NAME, create_session_token(user_id), max_age=s.session_days * 86400, httponly=True,
                        secure=s.cookie_secure, samesite="lax", path="/")


def _out(u: User) -> UserOut:
    return UserOut(id=u.id, email=u.email, display_name=u.display_name)


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: RegisterIn, request: Request, response: Response, db: Session = Depends(get_db)):
    if not limiter.check(f"reg:{_ip(request)}", 10, 3600):
        raise HTTPException(429, "Too many sign-ups from this address. Try again later.")
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists. Try signing in.")
    user = User(email=email, password_hash=hash_password(body.password), display_name=body.display_name)
    db.add(user)
    db.commit()
    _set_cookie(response, user.id)
    return _out(user)


@router.post("/login", response_model=UserOut)
def login(body: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    email = body.email.lower()
    if not limiter.check(f"login:{_ip(request)}:{email}", 8, 900):
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes and try again.")
    user = db.scalar(select(User).where(User.email == email))
    ok = verify_password(body.password, user.password_hash if user else DUMMY_HASH)
    if not user or not ok or not user.is_active:
        raise HTTPException(401, "Incorrect email or password.")
    _set_cookie(response, user.id)
    return _out(user)


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return _out(user)


@router.post("/forgot")
def forgot(body: ForgotIn, request: Request, db: Session = Depends(get_db)):
    generic = {"message": "If an account exists for that email, a reset link has been sent."}
    if not limiter.check(f"forgot:{_ip(request)}", 5, 3600):
        raise HTTPException(429, "Too many requests. Try again later.")
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user and user.is_active:
        raw = secrets.token_urlsafe(32)
        db.add(ResetToken(user_id=user.id, token_hash=hash_token(raw), expires_at=utcnow() + timedelta(hours=1)))
        db.commit()
        link = f"{get_settings().app_base_url.rstrip('/')}/reset-password?token={raw}"
        send_email(user.email, "Reset your Sanskrit Saathi password",
                   f"Hello {user.display_name},\n\nUse this link within one hour to choose a new password:\n{link}\n\n"
                   "If you didn't ask for this, you can ignore this email.")
    return generic


@router.post("/reset")
def reset(body: ResetIn, db: Session = Depends(get_db)):
    row = db.scalar(select(ResetToken).where(ResetToken.token_hash == hash_token(body.token)))
    now = utcnow()
    if not row or row.used or row.expires_at.replace(tzinfo=row.expires_at.tzinfo or now.tzinfo) < now:
        raise HTTPException(400, "This reset link is invalid or has expired.")
    user = db.get(User, row.user_id)
    user.password_hash = hash_password(body.password)
    row.used = True
    db.commit()
    return {"message": "Password updated. You can sign in now."}


@router.post("/change-password", status_code=204)
def change_password(body: ChangePasswordIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect.")
    user.password_hash = hash_password(body.new_password)
    db.commit()


@router.post("/delete-account", status_code=204)
def delete_account(body: DeleteAccountIn, response: Response, user: User = Depends(current_user),
                   db: Session = Depends(get_db)):
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(400, "Password is incorrect.")
    from ..models import AiUsage, ProgressRow, QuizSession
    for model in (ProgressRow, QuizSession, ResetToken, AiUsage):
        for row in db.scalars(select(model).where(model.user_id == user.id)):
            db.delete(row)
    db.delete(user)
    db.commit()
    response.delete_cookie(COOKIE_NAME, path="/")
