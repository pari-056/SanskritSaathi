"""Gemini integration (google-genai SDK).

Three ways the LLM is used, all grounded by the deterministic engine:
  1. chat_reply: tutor chat. The learner's Sanskrit is pre-analysed by the rule engine and the
     analysis is passed to Gemini as context; Gemini may also call verified tools
     (automatic function calling).
  2. analyze_sentence_ai: structured JSON analysis (schema-constrained), then cross-checked
     token-by-token against the rule-based analyzer.
  3. one-shot generation (role-plays, explanations).
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

from . import tools as _tools
from .morph import get_analyzer
from .syntax import analyze_sentence
from .translit import detect_script, slp1_to_dev, to_slp1, tokenize_devanagari

DEFAULT_MODEL = "gemini-3.8-flash"
MODEL_PRESETS = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.6-flash",
                 "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]


# ---------------------------------------------------------------------------
# Client / errors
# ---------------------------------------------------------------------------

def make_client(api_key: str):
    from google import genai
    return genai.Client(api_key=api_key)


def friendly_error(e: Exception) -> str:
    """Human-readable message. Never includes the API key."""
    code = getattr(e, "code", None)
    msg = str(getattr(e, "message", "") or e)
    low = msg.lower()
    if code in (400, 401, 403) and ("api key" in low or "api_key" in low or "permission" in low or code in (401, 403)):
        return ("Gemini rejected the API key or permissions. Check `GEMINI_API_KEY`, that the Gemini API is "
                "enabled for the key's project, and that the key has no restrictions blocking this app.")
    if code == 404:
        return ("Gemini could not find that model name. Pick another model in the sidebar "
                "(e.g. `gemini-flash-latest`) or check the current model list in Google AI Studio.")
    if code == 429:
        return "Gemini rate limit or quota reached. Wait a moment, or choose a lighter model (Flash-Lite)."
    if code and int(code) >= 500:
        return "Gemini is temporarily unavailable. Please try again in a moment."
    if code == 400:
        return f"Gemini rejected the request: {msg[:300]}"
    return f"Couldn't reach Gemini ({type(e).__name__}). Check your internet connection and API key."


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def tutor_system_prompt(level: str, focus: str, language: str, tools_on: bool, extra: str = "") -> str:
    tool_rules = (
        "You can call verified linguistic tools (word/sentence analysis, sandhi join/split, paradigms, "
        "transliteration). Use them to CHECK any declined/conjugated form, sandhi result or parse before "
        "you assert it. If a tool reports a form is not in its lexicon, you may still answer from your own "
        "knowledge but say it is unverified. If a tool and your memory disagree, trust the tool and say so."
        if tools_on else
        "You have no tools. When unsure of a form, say so rather than guessing."
    )
    return f"""You are Sanskrit Saathi, a careful Sanskrit tutor and computational-linguistics assistant.
Learner level: {level}. Today's focus: {focus}. Explanation language: {language}.

Teaching style
- Teach through short interactive dialogue; end with one small follow-up task the learner can answer.
- Show Sanskrit in Devanagari with IAST when helpful, a natural translation, and a word-by-word gloss.
- Give grammatical notes only where justified: vibhakti, vacana, liṅga, puruṣa, lakāra, dhātu, kāraka, sandhi, samāsa.
- If the learner writes Sanskrit, correct it gently, say exactly what changed and why, then show the corrected sentence.
- Keep Sanskrit complexity matched to the learner's level. Default to bilingual Sanskrit + English unless asked otherwise.

Accuracy rules
- Sanskrit is morphologically rich and ambiguous. Separate certain facts from plausible readings; never invent a definitive parse.
- Do not claim you ran a parser or tool unless you actually called one.
- Distinguish classical Sanskrit from Vedic usage when it matters.
- {tool_rules}
- A block labelled 'RULE-ENGINE NOTES' may be attached to the learner's message. It comes from a deterministic analyzer
  with a small lexicon: treat its positive findings as reliable and its 'not in lexicon' items as merely unknown.

Keep answers focused and pedagogical; avoid filler.
{('Current lesson context (the learner is studying this right now; stay consistent with it):' + chr(10) + extra) if extra else ''}"""


def build_analysis_context(user_text: str) -> str:
    """Compact rule-engine notes for the learner's Sanskrit (empty string if none)."""
    try:
        script = detect_script(user_text)
        has_sanskrit = script in ("devanagari", "iast") and bool(user_text.strip())
        if not has_sanskrit:
            return ""
        if script == "iast":
            user_text = slp1_to_dev(to_slp1(user_text, "iast"))
        sa = analyze_sentence(user_text)
        if not sa.tokens:
            return ""
        lines = []
        for t in sa.tokens:
            if t.chosen:
                alt = f" (+{len(t.alternatives) - 1} other reading(s))" if len(t.alternatives) > 1 else ""
                lines.append(f"- {t.token}: {t.chosen.lemma_display()} · {t.chosen.pos_label()} · "
                             f"{t.chosen.features_en() or t.chosen.gloss}{alt}"
                             + (f" · role: {t.role}" if t.role else ""))
            else:
                lines.append(f"- {t.token}: not in lexicon")
        for i in sa.issues:
            lines.append(f"- {i['severity'].upper()}: {i['message']} {i['suggestion']}".strip())
        return "RULE-ENGINE NOTES (deterministic, limited lexicon):\n" + "\n".join(lines)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def _to_contents(messages: list[dict], extra_context: str = ""):
    from google.genai import types
    turns: list[tuple[str, str]] = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        text = m["content"]
        if turns and turns[-1][0] == role:
            turns[-1] = (role, turns[-1][1] + "\n\n" + text)
        else:
            turns.append((role, text))
    while turns and turns[0][0] == "model":  # API expects the conversation to start with the user
        turns.pop(0)
    if extra_context and turns and turns[-1][0] == "user":
        turns[-1] = ("user", turns[-1][1] + "\n\n" + extra_context)
    return [types.Content(role=r, parts=[types.Part.from_text(text=t)]) for r, t in turns]


def _gen_config(model: str, **kw):
    from google.genai import types
    if model.startswith("gemini-2"):
        kw.setdefault("temperature", 0.4)
    return types.GenerateContentConfig(**kw)


def _tool_calls(response) -> list[str]:
    calls = []
    try:
        for content in getattr(response, "automatic_function_calling_history", None) or []:
            for part in content.parts or []:
                fc = getattr(part, "function_call", None)
                if fc:
                    args = ", ".join(f"{k}={v!r}" for k, v in (fc.args or {}).items())
                    calls.append(f"{fc.name}({args})")
    except Exception:
        pass
    return calls


@dataclass
class ChatResult:
    text: str
    tool_calls: list[str] = field(default_factory=list)


def chat_reply(client, model: str, messages: list[dict], level: str, focus: str, language: str,
               use_tools: bool = True, extra_system: str = "") -> ChatResult:
    from google.genai import types
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    ctx = build_analysis_context(last_user)
    cfg_kwargs = dict(system_instruction=tutor_system_prompt(level, focus, language, use_tools, extra_system))
    if use_tools:
        cfg_kwargs["tools"] = _tools.GEMINI_TOOLS
        cfg_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(maximum_remote_calls=8)
    response = client.models.generate_content(
        model=model, contents=_to_contents(messages, ctx), config=_gen_config(model, **cfg_kwargs))
    text = getattr(response, "text", None)
    if not text:
        reason = ""
        try:
            reason = str(response.candidates[0].finish_reason)
        except Exception:
            pass
        text = f"I couldn't produce a response{' (' + reason + ')' if reason else ''}. Please rephrase and try again."
    return ChatResult(text, _tool_calls(response))


def one_shot(client, model: str, prompt: str, level: str, focus: str, language: str, extra_system: str = "") -> str:
    return chat_reply(client, model, [{"role": "user", "content": prompt}], level, focus, language,
                      use_tools=False, extra_system=extra_system).text


# ---------------------------------------------------------------------------
# Structured analysis + cross-check against the rule engine
# ---------------------------------------------------------------------------

class TokenGloss(BaseModel):
    surface: str = Field(description="The word exactly as it appears, in Devanagari")
    lemma: str = Field(description="Dictionary form in Devanagari (noun stem like राम, or verb root like गम्)")
    part_of_speech: str = Field(description="noun, pronoun, adjective, verb, participle, indeclinable, etc.")
    gloss: str = Field(description="Short English meaning")
    features: str = Field(description="Case/number/gender, or tense/person/number, or other grammatical features")
    confidence: Literal["high", "medium", "low"]


class SentenceAnalysisAI(BaseModel):
    devanagari: str
    iast: str
    translation: str = Field(description="Natural English translation")
    sandhi_notes: list[str] = Field(description="Sandhi that was applied in the text, with the pre-sandhi forms")
    tokens: list[TokenGloss]
    syntax_notes: list[str] = Field(description="Kāraka relations, agreement, word order, compounds")
    ambiguities: list[str] = Field(description="Genuine alternative readings; empty if none")
    learner_tip: str


@dataclass
class CheckedToken:
    token: TokenGloss
    verdict: str      # "verified" | "disagrees" | "ai-only"
    detail: str


def _norm_lemma(s: str) -> str:
    slp = to_slp1(s.replace("√", "").replace("-", "").strip())
    slp = re.sub(r"[HmM]$", "", slp)
    return slp


def crosscheck(tokens: list[TokenGloss]) -> list[CheckedToken]:
    an = get_analyzer()
    out: list[CheckedToken] = []
    for t in tokens:
        r = an.analyze(t.surface)
        if not r.analyses:
            out.append(CheckedToken(t, "ai-only", "Not covered by the built-in lexicon, so unverified."))
            continue
        want = _norm_lemma(t.lemma)
        have = {re.sub(r"[HmM]$", "", a.lemma) for a in r.analyses} | {a.lemma for a in r.analyses}
        have_stems = {a.lemma for a in r.analyses}
        if want in have or want + "a" in have or any(h.startswith(want) and len(h) - len(want) <= 1 for h in have_stems):
            out.append(CheckedToken(t, "verified", "Lemma matches the rule-based analyzer."))
        else:
            reads = ", ".join(sorted({a.lemma_display() for a in r.analyses}))
            out.append(CheckedToken(t, "disagrees", f"Analyzer reads this as: {reads}."))
    return out


def analyze_sentence_ai(client, model: str, sentence: str, level: str, language: str) -> tuple[SentenceAnalysisAI, list[CheckedToken]]:
    ctx = build_analysis_context(sentence)
    prompt = (f"Analyse this Sanskrit sentence for a {level} learner. Explanations in: {language}.\n"
              f"Sentence: {sentence}\n\n{ctx}\n\n"
              "Return the analysis as JSON matching the schema. List one token entry per word in sentence order. "
              "Mark confidence honestly; use 'low' where several readings are plausible.")
    system = ("You are a careful Sanskrit grammarian. Prefer classical Pāṇinian analysis. "
              "Never invent forms; if unsure, lower the confidence and list the ambiguity.")
    response = client.models.generate_content(
        model=model, contents=prompt,
        config=_gen_config(model, system_instruction=system, response_mime_type="application/json",
                           response_schema=SentenceAnalysisAI))
    parsed = getattr(response, "parsed", None)
    if not isinstance(parsed, SentenceAnalysisAI):
        parsed = SentenceAnalysisAI.model_validate_json(response.text)
    return parsed, crosscheck(parsed.tokens)
