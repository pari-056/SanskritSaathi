"""Minimal CoNLL-U reader (enough for UD Sanskrit: tokens, multiword tokens, features, MISC)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Tok:
    id: str
    form: str
    lemma: str
    upos: str
    feats: dict[str, str]
    misc: dict[str, str]
    head: str = "_"
    deprel: str = "_"


@dataclass
class MWT:
    start: int
    end: int
    form: str
    parts: list[Tok] = field(default_factory=list)


@dataclass
class Sent:
    sent_id: str
    text: str
    tokens: list[Tok]
    mwts: list[MWT]


def _kv(s: str) -> dict[str, str]:
    if s in ("_", ""):
        return {}
    out = {}
    for item in s.split("|"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
    return out


def read_conllu(path: str | Path) -> list[Sent]:
    sents: list[Sent] = []
    meta: dict[str, str] = {}
    toks: list[Tok] = []
    mwts: list[MWT] = []

    def flush():
        nonlocal meta, toks, mwts
        if toks:
            by_id = {t.id: t for t in toks}
            for m in mwts:
                m.parts = [by_id[str(i)] for i in range(m.start, m.end + 1) if str(i) in by_id]
            sents.append(Sent(meta.get("sent_id", f"s{len(sents)}"), meta.get("text", ""), toks, mwts))
        meta, toks, mwts = {}, [], []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                flush()
                continue
            if line.startswith("#"):
                m = re.match(r"#\s*(\w+)\s*=\s*(.*)", line)
                if m:
                    meta[m.group(1)] = m.group(2)
                continue
            c = line.split("\t")
            if len(c) != 10 or "." in c[0]:
                continue
            if re.fullmatch(r"\d+-\d+", c[0]):
                a, b = c[0].split("-")
                mwts.append(MWT(int(a), int(b), c[1]))
                continue
            toks.append(Tok(c[0], c[1], c[2], c[3], _kv(c[5]), _kv(c[9]), c[6], c[7]))
    flush()
    return sents
