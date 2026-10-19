from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=60)

    @field_validator("display_name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Display name is required")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    password: str = Field(min_length=8, max_length=128)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountIn(BaseModel):
    password: str = Field(max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str


class QuizStartIn(BaseModel):
    kind: Literal["lesson", "practice", "daily", "review", "placement", "script"]
    lesson_id: str | None = None
    level: int | None = Field(default=None, ge=1, le=4)
    n: int = Field(default=10, ge=3, le=25)
    script_kinds: list[Literal["vowel", "consonant", "matra", "conjunct"]] | None = None


class AnswerIn(BaseModel):
    index: int = Field(ge=0, le=50)
    pick: int = Field(ge=0, le=10)


class ExplainIn(BaseModel):
    index: int = Field(ge=0, le=50)


class ReviewIn(BaseModel):
    card_id: str = Field(max_length=80)
    grade: Literal["again", "good", "easy"]


class WordIn(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class SentenceIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class JoinIn(BaseModel):
    first: str = Field(min_length=1, max_length=60)
    second: str = Field(min_length=1, max_length=60)


class TranslitIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatIn(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)
    lesson_id: str | None = None
    level: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    focus: Literal["Conversation", "Grammar", "Vocabulary", "Translation", "Computational linguistics"] = "Conversation"
    language: Literal["English with Sanskrit", "Mostly Sanskrit", "English"] = "English with Sanskrit"
    use_tools: bool = True

    @field_validator("messages")
    @classmethod
    def _last_is_user(cls, v):
        if v[-1].role != "user":
            raise ValueError("The last message must be from the user")
        return v
