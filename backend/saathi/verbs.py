"""Wide-coverage verb system.

Data (saathi/data/verbs.json, built by tools/build_verb_lexicon.py) gives each Dhātupāṭha root its
principal parts. This module turns them into forms:

* thematic roots (gaṇas 1, 4, 6, 10): every form is generated here by explicit rules from the
  present / future / passive / causative stems, in both padas;
* athematic roots (gaṇas 2, 3, 5, 7, 8, 9): the listed laṭ/laṅ/loṭ/vidhiliṅ paradigms, plus rule-generated
  future and conditional;
* perfect (liṭ): listed paradigms for every root;
* participles (kta, ktavatu, śatṛ, śānac, tavya, anīya), gerunds and infinitives;
* prefixed verbs (upasarga + verb): recognised by reversing the prefix junction and re-checking by
  rebuilding the surface form.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .phonology import natva
from .translit import VOWELS

DATA = Path(__file__).parent / "data" / "verbs.json"
PN = [(3, "sg"), (3, "du"), (3, "pl"), (2, "sg"), (2, "du"), (2, "pl"), (1, "sg"), (1, "du"), (1, "pl")]
VOICES = ["act", "mid", "pass", "cau-act", "cau-mid"]
TENSES = ["lat", "lan", "lot", "vidhilin", "lrt", "lrn", "lit", "lun", "lut"]
_DATA_TENSE = {"lat": "lat", "lan": "lan", "lot": "lot", "vid": "vidhilin"}


# ---------------------------------------------------------------------------
# Rule-based generation for thematic stems
# ---------------------------------------------------------------------------

def augment(stem: str) -> str:
    """The past-tense prefix a-, merged (vṛddhi) with a vowel-initial stem."""
    c = stem[0]
    if c == "C":                      # che ca: ch after the short vowel a- doubles (a + ccha → accha)
        return "acC" + stem[1:]
    if c not in VOWELS:
        return "a" + stem
    rest = stem[1:]
    if c in "aA":
        return "A" + rest
    if c in "iIeE":
        return "E" + rest
    if c in "uUoO":
        return "O" + rest
    if c in "fF":
        return "Ar" + rest
    return "a" + stem


def thematic_cells(stem: str, pada: str, tense: str) -> list[list[str]]:
    """thematic() as nine variant lists; adds the optional imperative endings in -tāt (3sg and 2sg, parasmaipada)."""
    out = [[x] for x in thematic(stem, pada, tense)]
    if pada == "P" and tense == "lot":
        out[0].append(stem + "tAt")
        out[3].append(stem + "tAt")
    return out


def thematic(stem: str, pada: str, tense: str) -> list[str]:
    """Nine forms (3sg 3du 3pl 2sg 2du 2pl 1sg 1du 1pl) for a stem ending in -a.

    pada is 'P' (parasmaipada) or 'A' (ātmanepada, also used for the passive).
    tense: lat, lan, lot, vidhilin, lrt (stem = future stem), lrn (stem = future stem).
    """
    if not stem or stem[-1] != "a":
        raise ValueError(f"thematic stem must end in -a: {stem!r}")
    s, b = stem, stem[:-1]
    if tense in ("lan", "lrn"):
        a = augment(s)
        ab = a[:-1]
        if pada == "P":
            f = [a + "t", a + "tAm", ab + "an", a + "H", a + "tam", a + "ta", a + "m", ab + "Ava", ab + "Ama"]
        else:
            f = [a + "ta", ab + "etAm", ab + "anta", a + "TAH", ab + "eTAm", a + "Dvam", ab + "e", ab + "Avahi", ab + "Amahi"]
        return [natva(x, len(ab)) for x in f]
    if pada == "P":
        if tense in ("lat", "lrt"):
            f = [s + "ti", s + "taH", b + "anti", s + "si", s + "TaH", s + "Ta", b + "Ami", b + "AvaH", b + "AmaH"]
        elif tense == "lot":
            f = [s + "tu", s + "tAm", b + "antu", s, s + "tam", s + "ta", b + "Ani", b + "Ava", b + "Ama"]
        elif tense == "vidhilin":
            f = [b + "et", b + "etAm", b + "eyuH", b + "eH", b + "etam", b + "eta", b + "eyam", b + "eva", b + "ema"]
        else:
            raise ValueError(tense)
    else:
        if tense in ("lat", "lrt"):
            f = [s + "te", b + "ete", b + "ante", s + "se", b + "eTe", s + "Dve", b + "e", b + "Avahe", b + "Amahe"]
        elif tense == "lot":
            f = [s + "tAm", b + "etAm", b + "antAm", s + "sva", b + "eTAm", s + "Dvam", b + "E", b + "AvahE", b + "AmahE"]
        elif tense == "vidhilin":
            f = [b + "eta", b + "eyAtAm", b + "eran", b + "eTAH", b + "eyATAm", b + "eDvam", b + "eya", b + "evahi", b + "emahi"]
        else:
            raise ValueError(tense)
    return [natva(x, len(b)) for x in f]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Verb:
    idx: int
    key: str
    root: str
    gana: int
    meaning: str
    padas: str
    pres: dict
    fut: dict
    passive: str | None
    cau: dict
    kta: tuple
    tavya: tuple
    anIya: tuple
    ktvA: tuple
    tumun: tuple
    lyap: tuple
    tbl: dict | None
    lit: dict
    ya: tuple = ()
    lun: dict | None = None
    lut: dict | None = None
    ckta: tuple = ()
    cktvA: tuple = ()
    ctumun: tuple = ()
    clyap: tuple = ()
    prap: tuple = ()
    pmp: tuple = ()

    @property
    def athematic(self) -> bool:
        return self.tbl is not None


def _split(v) -> tuple:
    return tuple(v.split("|")) if v else ()


@lru_cache(maxsize=1)
def load_verbs() -> tuple[Verb, ...]:
    raw = json.loads(DATA.read_text(encoding="utf-8"))["entries"]
    out = []
    for i, e in enumerate(raw):
        out.append(Verb(i, e["k"], e["r"], e["g"], e.get("m", ""), e.get("pada", "P"), e.get("pres", {}),
                        e.get("fut", {}), e.get("pass"), e.get("cau", {}), _split(e.get("kta")), _split(e.get("tavya")),
                        _split(e.get("anIya")), _split(e.get("ktvA")), _split(e.get("tumun")), _split(e.get("lyap")),
                        e.get("tbl"), e.get("lit", {}), _split(e.get("ya")), e.get("lun", {}), e.get("lut", {}),
                        _split(e.get("ckta")), _split(e.get("cktvA")), _split(e.get("ctumun")), _split(e.get("clyap")),
                        _split(e.get("prap")), _split(e.get("pmp"))))
    return tuple(out)


def _pada_key(voice: str) -> str:
    return "P" if voice in ("act", "cau-act") else "A"


def _merge(parts: list[list[list[str]]]) -> list[list[str]]:
    """Combine the paradigms of several stem variants cell by cell."""
    out: list[list[str]] = [[] for _ in range(9)]
    for part in parts:
        for i, cell in enumerate(part):
            for f in cell:
                if f not in out[i]:
                    out[i].append(f)
    return out


def forms(v: Verb, voice: str, tense: str) -> list[list[str]]:
    """Nine cells, each a list of accepted variants (possibly empty if the form is not available)."""
    def over(stem_field, fn):
        stems = stem_field.split("|") if stem_field else []
        return _merge([fn(s) for s in stems]) if stems else []
    try:
        if voice == "act" or voice == "mid":
            pk = _pada_key(voice)
            if tense in ("lit", "lun", "lut"):
                cells = ({"lit": v.lit, "lun": v.lun, "lut": v.lut}[tense] or {}).get(pk)
                return [c.split("|") if c else [] for c in cells] if cells else []
            if tense in ("lrt", "lrn"):
                return over(v.fut.get(pk), lambda s: thematic_cells(s, pk, tense))
            if v.athematic:
                tag = {"lat": "lat", "lan": "lan", "lot": "lot", "vidhilin": "vid"}[tense]
                cells = (v.tbl.get(tag) or {}).get(pk)
                return [c.split("|") if c else [] for c in cells] if cells else []
            return over(v.pres.get(pk), lambda s: thematic_cells(s, pk, tense))
        if voice == "pass":
            if tense in ("lat", "lan", "lot", "vidhilin"):
                return over(v.passive, lambda s: thematic_cells(s, "A", tense))
            return []
        if voice in ("cau-act", "cau-mid"):
            pk = _pada_key(voice)
            st = v.cau.get(pk)
            if not st or tense in ("lit", "lun", "lut"):
                return []
            if tense in ("lrt", "lrn"):
                return over(st, lambda s: thematic_cells(s[:-1] + "izya", pk, tense))
            return over(st, lambda s: thematic_cells(s, pk, tense))
    except ValueError:
        return []
    return []


# ---------------------------------------------------------------------------
# Index of every finite form: surface → list of packed (entry, voice, tense, person/number) codes
# ---------------------------------------------------------------------------

def pack(idx: int, voice: int, tense: int, pn: int) -> int:
    return ((idx * 5 + voice) * 16 + tense) * 9 + pn


def unpack(code: int) -> tuple[int, int, int, int]:
    code, pn = divmod(code, 9)
    code, tense = divmod(code, 16)
    idx, voice = divmod(code, 5)
    return idx, voice, tense, pn


@lru_cache(maxsize=1)
def finite_index() -> dict[str, list[int]]:
    idx: dict[str, list[int]] = {}
    for v in load_verbs():
        for vi, voice in enumerate(VOICES):
            for ti, tense in enumerate(TENSES):
                cells = forms(v, voice, tense)
                for pn, variants in enumerate(cells):
                    for f in variants:
                        if f:
                            idx.setdefault(f, []).append(pack(v.idx, vi, ti, pn))
    return idx
