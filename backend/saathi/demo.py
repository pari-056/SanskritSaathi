"""Offline 'demo mode' replies. No API key needed: powered entirely by the rule engine."""
from __future__ import annotations
import random
import re

from . import morph, sandhi, tools
from .practice import Scheduler, q_declension, q_conjugation
from .syntax import analyze_sentence
from .translit import convert, detect_script, slp1_to_dev, slp1_to_iast, to_slp1

_DEV = re.compile(r"[\u0900-\u097F]+")


def _analysis_md(text: str) -> str:
    sa = analyze_sentence(text)
    if not sa.tokens:
        return ""
    lines = ["**शब्दार्थाः · Word-by-word (rule-based)**", "",
             "| Word | Lemma | Analysis | Role |", "|---|---|---|---|"]
    for t in sa.tokens:
        if t.chosen:
            alt = " *(ambiguous)*" if t.status == "ambiguous" else ""
            lines.append(f"| {t.token} | {t.chosen.lemma_display()} | {t.chosen.pos_label()}: "
                         f"{t.chosen.features_en() or t.chosen.gloss}{alt} | {t.role or '—'} |")
        else:
            lines.append(f"| {t.token} | — | not in lexicon | — |")
    out = "\n".join(lines)
    for i in sa.issues:
        icon = {"error": "❌", "warning": "⚠️"}.get(i["severity"], "ℹ️")
        out += f"\n\n{icon} {i['message']} {i['suggestion']}"
    for n in sa.notes:
        out += f"\n\n*{n}*"
    return out


def _table_md(lemma: str, tense: str = "lat") -> str:
    d = tools.get_paradigm(lemma, tense)
    if not d.get("found"):
        return f"I don't have **{lemma}** in the built-in lexicon yet."
    rows = ["| Form | Value |", "|---|---|"]
    for k, v in d["forms"].items():
        val = v["devanagari"] if isinstance(v, dict) else " / ".join(v)
        rows.append(f"| {k} | {val} |")
    title = d.get("root") or d.get("lemma")
    return f"**{title}** — {d['meaning']}\n\n" + "\n".join(rows)


def demo_reply(prompt: str, level: str = "Beginner", focus: str = "Conversation") -> str:
    p = prompt.strip()
    low = p.lower()
    if not p:
        return "कृपया किञ्चित् लिखतु।\nPlease type a question or a Sanskrit sentence."
    m = re.match(r"(?:decline|forms of|paradigm of)\s+(\S+)", low)
    if m:
        return _table_md(p.split()[-1] if p.split()[0].lower() in ("decline", "paradigm") and len(p.split()) > 1 else m.group(1))
    m = re.match(r"conjugate\s+(\S+)(?:\s+(lat|lan|lot|vidhilin|lrt))?", low)
    if m:
        return _table_md(m.group(1), m.group(2) or "lat")
    m = re.match(r"transliterate\s+(.+)", p, re.I)
    if m:
        t = m.group(1)
        return (f"**Devanagari:** {convert(t, 'devanagari')}\n\n**IAST:** {convert(t, 'iast')}\n\n"
                f"**Harvard-Kyoto:** {convert(t, 'hk')}")
    if "+" in p and _DEV.search(p):
        a, b = [x.strip() for x in p.split("+", 1)]
        r = tools.sandhi_join(a, b)
        if "result" in r:
            return f"**{a} + {b} → {r['result']['devanagari']}** ({r['result']['iast']})\n\nRule: {r['rule']}"
    if any(x in low for x in ["introduce myself", "my name", "स्वपरिचय"]):
        return ("**स्वपरिचयः · Introducing yourself**\n\n- नमस्ते! = Hello!\n- मम नाम ___ अस्ति। = My name is ___.\n"
                "- अहं छात्रः / छात्रा अस्मि। = I am a student.\n- अहं संस्कृतं पठामि। = I study Sanskrit.\n\n"
                "**Your turn:** Fill in your name: मम नाम ___ अस्ति।")
    if _DEV.search(p):
        md = _analysis_md(p)
        if md:
            return md + "\n\n*Demo mode: results come from the built-in lexicon. Add a Gemini API key for open-ended tutoring.*"
    if any(x in low for x in ["exercise", "quiz", "अभ्यास", "practice"]):
        rng = random.Random()
        q = q_declension(rng) if rng.random() < .5 else q_conjugation(rng)
        return ("**अभ्यासः · Quick practice**\n\n" + q.prompt + "\n\n"
                + "\n".join(f"{i + 1}. {o}" for i, o in enumerate(q.options))
                + f"\n\n*Answer: {q.explanation}*")
    if re.search(r"\b(hello|hi)\b", low) or "नमस्ते" in p:
        return ("नमस्ते! 🙏 अद्य वयं संस्कृतेन सम्भाषणं कुर्मः।\n\nLet's practise together. "
                "Try saying: **मम नाम ___ अस्ति।** (My name is ___.)")
    if any(x in low for x in ["help", "what can you do"]):
        return ("In demo mode I can: analyse any Devanagari sentence (type or paste it), "
                "`decline राम`, `conjugate गम् lan`, `transliterate rAmaH`, join sandhi (`रामः + अस्ति`), "
                "and give practice questions. Add a Gemini API key for open-ended tutoring.")
    return ("उत्तमम्, अभ्यासं कुर्मः! 🌱\n\nI'm in **demo mode**: paste a Devanagari sentence to analyse it, or try "
            "`decline राम`, `conjugate गम्`, `रामः + अस्ति`. Add a Gemini API key to enable open-ended tutoring.")
