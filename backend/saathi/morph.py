"""Paradigm-based morphology: generation and analysis (SLP1 internally).

Every form is *generated* from the lexicon by explicit rules, then inverted into
an analysis index. An analysis is therefore only reported if the form is derivable
from a known stem/root, which makes the output verifiable (no guessing).
"""
from __future__ import annotations
import difflib
from dataclasses import dataclass, field, replace
from functools import lru_cache

from . import lexicon as lx
from .sandhi import Splitter, restore_finals
from .translit import VOWELS, to_slp1, slp1_to_dev, slp1_to_iast, detect_script

CASES = [1, 2, 3, 4, 5, 6, 7, 8]
NUMBERS = ["sg", "du", "pl"]
CASE_EN = {1: "nominative", 2: "accusative", 3: "instrumental", 4: "dative",
           5: "ablative", 6: "genitive", 7: "locative", 8: "vocative"}
CASE_SA = {1: "प्रथमा", 2: "द्वितीया", 3: "तृतीया", 4: "चतुर्थी",
           5: "पञ्चमी", 6: "षष्ठी", 7: "सप्तमी", 8: "सम्बोधन"}
NUM_EN = {"sg": "singular", "du": "dual", "pl": "plural"}
NUM_SA = {"sg": "एकवचन", "du": "द्विवचन", "pl": "बहुवचन"}
GEN_EN = {"m": "masculine", "f": "feminine", "n": "neuter"}
GEN_SA = {"m": "पुंलिङ्ग", "f": "स्त्रीलिङ्ग", "n": "नपुंसकलिङ्ग"}
PERSON_EN = {1: "1st person", 2: "2nd person", 3: "3rd person"}
PERSON_SA = {1: "उत्तम", 2: "मध्यम", 3: "प्रथम"}
TENSE_EN = {"lat": "present (laṭ)", "lan": "imperfect (laṅ)", "lot": "imperative (loṭ)",
            "vidhilin": "optative (vidhiliṅ)", "lrt": "future (lṛṭ)"}
TENSE_SA = {"lat": "लट्", "lan": "लङ्", "lot": "लोट्", "vidhilin": "विधिलिङ्", "lrt": "लृट्"}
TENSES = list(TENSE_EN)
TENSE_ALL_EN = {**TENSE_EN, "lrn": "conditional (lṛṅ)", "lit": "perfect (liṭ)", "lun": "aorist (luṅ)", "lut": "periphrastic future (luṭ)"}
TENSE_ALL_SA = {**TENSE_SA, "lrn": "लृङ्", "lit": "लिट्", "lun": "लुङ्", "lut": "लुट्"}

ENCLITICS = {"mA", "me", "nO", "naH", "te", "vAm", "vaH", "tvA"}


@dataclass(frozen=True)
class Analysis:
    surface: str                 # SLP1 surface form
    lemma: str                   # SLP1 stem / root / indeclinable
    pos: str                     # noun adj pron verb ppp indecl gerund infinitive
    gloss: str = ""
    case: int | None = None
    number: str | None = None
    gender: str | None = None
    person: int | None = None
    tense: str | None = None
    root: str | None = None
    transitive: bool | None = None
    note: str = ""
    voice: str | None = None        # act | mid | pass (verbs)
    causative: bool = False
    prefix: str = ""                # upasarga, e.g. "A" in āgacchati

    # -- display helpers -----------------------------------------------------
    def features_en(self) -> str:
        bits = []
        if self.pos == "verb":
            bits += [TENSE_ALL_EN[self.tense], PERSON_EN[self.person], NUM_EN[self.number]]
            if self.voice in ("mid", "pass"):
                bits.append({"mid": "middle voice", "pass": "passive"}[self.voice])
            if self.causative:
                bits.append("causative")
        elif self.pos in ("noun", "adj", "pron", "ppp", "ktavatu", "prap", "pmp", "gdv"):
            if self.gender:
                bits.append(GEN_EN[self.gender])
            if self.person:
                bits.append(PERSON_EN[self.person])
            bits += [CASE_EN[self.case], NUM_EN[self.number]]
        return ", ".join(bits)

    def features_sa(self) -> str:
        bits = []
        if self.pos == "verb":
            bits += [TENSE_ALL_SA[self.tense], PERSON_SA[self.person] + " पुरुष", NUM_SA[self.number]]
        elif self.pos in ("noun", "adj", "pron", "ppp", "ktavatu", "prap", "pmp", "gdv"):
            if self.gender:
                bits.append(GEN_SA[self.gender])
            if self.person:
                bits.append(PERSON_SA[self.person] + " पुरुष")
            bits += [CASE_SA[self.case] + " विभक्ति", NUM_SA[self.number]]
        return ", ".join(bits)

    def pos_label(self) -> str:
        return {"noun": "noun", "adj": "adjective", "pron": "pronoun", "verb": "finite verb",
                "ppp": "past passive participle (kta)", "indecl": "indeclinable (avyaya)",
                "gerund": "gerund (ktvā / lyap)", "infinitive": "infinitive (tumun)",
                "ktavatu": "past active participle (ktavatu)", "prap": "present active participle (śatṛ)",
                "pmp": "present middle participle (śānac)", "gdv": "gerundive (tavya / anīya)"}[self.pos]

    def lemma_label(self) -> str:
        """SLP1 label (internal)."""
        pre = self.prefix + "-" if self.prefix else ""
        return pre + ("√" + self.lemma if self.pos in ("verb", "gerund", "infinitive") else self.lemma)

    def lemma_display(self) -> str:
        """Devanagari (+ IAST) label for display, e.g. '√गम् (gam)' or 'राम (rāma)'."""
        root = self.pos in ("verb", "gerund", "infinitive")
        dev, ia = slp1_to_dev(self.lemma), slp1_to_iast(self.lemma)
        if self.pos == "indecl":
            return dev
        pre = (slp1_to_dev(self.prefix) + "-") if self.prefix else ""
        return pre + ("√" if root else "") + dev + f" ({ia})"


# ---------------------------------------------------------------------------
# Retroflexion (natva) and s -> z
# ---------------------------------------------------------------------------
from .phonology import natva as _natva  # noqa: E402


def _zu(stem: str) -> str:
    """Locative plural -su: becomes -zu after any vowel other than a/ā."""
    return stem + ("zu" if stem[-1] in "iIuUfFeEoO" else "su")


# ---------------------------------------------------------------------------
# Nominal paradigms. Each returns {(case, number): [forms]}
# ---------------------------------------------------------------------------

def _tbl(rows: dict) -> dict:
    out = {}
    for case, (sg, du, pl) in rows.items():
        for n, v in zip(NUMBERS, (sg, du, pl)):
            out[(case, n)] = [v] if isinstance(v, str) else list(v)
    return out


def decline(stem: str, cls: str, gender: str) -> dict:
    """Regular declension. cls in a, A, i, I, u. gender in m, f, n."""
    b = stem[:-1]
    if cls == "a":
        r = {
            1: (b + "aH", b + "O", b + "AH"),
            2: (b + "am", b + "O", b + "An"),
            3: (b + "ena", b + "AByAm", b + "EH"),
            4: (b + "Aya", b + "AByAm", b + "eByaH"),
            5: (b + "At", b + "AByAm", b + "eByaH"),
            6: (b + "asya", b + "ayoH", b + "AnAm"),
            7: (b + "e", b + "ayoH", b + "ezu"),
            8: (b + "a", b + "O", b + "AH"),
        }
        if gender == "n":
            r[1] = (b + "am", b + "e", b + "Ani")
            r[2] = (b + "am", b + "e", b + "Ani")
            r[8] = (b + "a", b + "e", b + "Ani")
    elif cls == "A":
        r = {
            1: (stem, b + "e", stem + "H"),
            2: (stem + "m", b + "e", stem + "H"),
            3: (b + "ayA", stem + "ByAm", stem + "BiH"),
            4: (b + "AyE", stem + "ByAm", stem + "ByaH"),
            5: (b + "AyAH", stem + "ByAm", stem + "ByaH"),
            6: (b + "AyAH", b + "ayoH", stem + "nAm"),
            7: (b + "AyAm", b + "ayoH", stem + "su"),
            8: (b + "e", b + "e", stem + "H"),
        }
    elif cls == "i":
        if gender == "m":
            r = {
                1: (stem + "H", b + "I", b + "ayaH"),
                2: (stem + "m", b + "I", b + "In"),
                3: (stem + "nA", stem + "ByAm", stem + "BiH"),
                4: (b + "aye", stem + "ByAm", stem + "ByaH"),
                5: (b + "eH", stem + "ByAm", stem + "ByaH"),
                6: (b + "eH", b + "yoH", b + "InAm"),
                7: (b + "O", b + "yoH", stem + "su"),
                8: (b + "e", b + "I", b + "ayaH"),
            }
        else:
            r = {
                1: (stem + "H", b + "I", b + "ayaH"),
                2: (stem + "m", b + "I", b + "IH"),
                3: (b + "yA", stem + "ByAm", stem + "BiH"),
                4: ([b + "aye", b + "yE"], stem + "ByAm", stem + "ByaH"),
                5: ([b + "eH", b + "yAH"], stem + "ByAm", stem + "ByaH"),
                6: ([b + "eH", b + "yAH"], b + "yoH", b + "InAm"),
                7: ([b + "O", b + "yAm"], b + "yoH", stem + "su"),
                8: (b + "e", b + "I", b + "ayaH"),
            }
    elif cls == "I":
        r = {
            1: (stem, b + "yO", b + "yaH"),
            2: (stem + "m", b + "yO", stem + "H"),
            3: (b + "yA", stem + "ByAm", stem + "BiH"),
            4: (b + "yE", stem + "ByAm", stem + "ByaH"),
            5: (b + "yAH", stem + "ByAm", stem + "ByaH"),
            6: (b + "yAH", b + "yoH", stem + "nAm"),
            7: (b + "yAm", b + "yoH", stem + "su"),
            8: (b + "i", b + "yO", b + "yaH"),
        }
    elif cls == "u":
        r = {
            1: (stem + "H", b + "U", b + "avaH"),
            2: (stem + "m", b + "U", b + "Un"),
            3: (stem + "nA", stem + "ByAm", stem + "BiH"),
            4: (b + "ave", stem + "ByAm", stem + "ByaH"),
            5: (b + "oH", stem + "ByAm", stem + "ByaH"),
            6: (b + "oH", b + "voH", b + "UnAm"),
            7: (b + "O", b + "voH", stem + "su"),
            8: (b + "o", b + "U", b + "avaH"),
        }
    else:
        raise ValueError(f"Unsupported class {cls!r}")
    t = _tbl(r)
    out = {}
    for k, forms in t.items():
        fixed = []
        for f in forms:
            if f.endswith("su") and k[1] == "pl" and k[0] == 7:
                f = _zu(f[:-2])
            fixed.append(_natva(f, max(len(stem) - 1, 0)))
        out[k] = fixed
    return out


def decline_pronoun_a(stem: str, masc_nom: str, fem_nom: str, neut_nom: str) -> dict:
    """Sarvanāman paradigm (tad, etad, kim, yad, sarva, anya, eka). Returns
    {gender: {(case, number): [forms]}} with no vocative."""
    b = stem[:-1]
    m = {
        1: (masc_nom, b + "O", b + "e"), 2: (b + "am", b + "O", b + "An"),
        3: (b + "ena", b + "AByAm", b + "EH"), 4: (b + "asmE", b + "AByAm", b + "eByaH"),
        5: (b + "asmAt", b + "AByAm", b + "eByaH"), 6: (b + "asya", b + "ayoH", b + "ezAm"),
        7: (b + "asmin", b + "ayoH", b + "ezu"),
    }
    n = dict(m)
    n[1] = (neut_nom, b + "e", b + "Ani")
    n[2] = (neut_nom, b + "e", b + "Ani")
    f = {
        1: (fem_nom, b + "e", b + "AH"), 2: (b + "Am", b + "e", b + "AH"),
        3: (b + "ayA", b + "AByAm", b + "ABiH"), 4: (b + "asyE", b + "AByAm", b + "AByaH"),
        5: (b + "asyAH", b + "AByAm", b + "AByaH"), 6: (b + "asyAH", b + "ayoH", b + "AsAm"),
        7: (b + "asyAm", b + "ayoH", b + "Asu"),
    }
    res = {}
    for g, rows in (("m", m), ("f", f), ("n", n)):
        t = _tbl(rows)
        res[g] = {k: [_natva(x, max(len(stem) - 1, 0)) for x in v] for k, v in t.items()}
    return res


# First- and second-person pronouns (suppletive); alternatives after "|" are enclitic.
ASMAD = {
    1: ("aham", "AvAm", "vayam"), 2: ("mAm|mA", "AvAm|nO", "asmAn|naH"),
    3: ("mayA", "AvAByAm", "asmABiH"), 4: ("mahyam|me", "AvAByAm|nO", "asmaByam|naH"),
    5: ("mat", "AvAByAm", "asmat"), 6: ("mama|me", "AvayoH|nO", "asmAkam|naH"),
    7: ("mayi", "AvayoH", "asmAsu"),
}
YUZMAD = {
    1: ("tvam", "yuvAm", "yUyam"), 2: ("tvAm|tvA", "yuvAm|vAm", "yuzmAn|vaH"),
    3: ("tvayA", "yuvAByAm", "yuzmABiH"), 4: ("tuByam|te", "yuvAByAm|vAm", "yuzmaByam|vaH"),
    5: ("tvat", "yuvAByAm", "yuzmat"), 6: ("tava|te", "yuvayoH|vAm", "yuzmAkam|vaH"),
    7: ("tvayi", "yuvayoH", "yuzmAsu"),
}


def _pron12(table: dict) -> dict:
    out = {}
    for case, row in table.items():
        for n, v in zip(NUMBERS, row):
            out[(case, n)] = v.split("|")
    return out


# ---------------------------------------------------------------------------
# Verb paradigms. Key: (person, number) -> form
# ---------------------------------------------------------------------------
PN = [(3, "sg"), (3, "du"), (3, "pl"), (2, "sg"), (2, "du"), (2, "pl"), (1, "sg"), (1, "du"), (1, "pl")]


def _row(forms: list[str]) -> dict:
    return dict(zip(PN, forms))


def conjugate_thematic(pres: str, tense: str, fut: str | None = None) -> dict:
    """Parasmaipada forms for a thematic (a-ending) stem."""
    if tense == "lrt":
        stem = fut
    else:
        stem = pres
    b = stem[:-1]
    if tense in ("lat", "lrt"):
        forms = [stem + "ti", stem + "taH", b + "anti", stem + "si", stem + "TaH", stem + "Ta",
                 b + "Ami", b + "AvaH", b + "AmaH"]
    elif tense == "lan":
        a = "a" + stem
        ab = "a" + b
        forms = [a + "t", a + "tAm", ab + "an", a + "H", a + "tam", a + "ta",
                 a + "m", ab + "Ava", ab + "Ama"]
    elif tense == "lot":
        forms = [stem + "tu", stem + "tAm", b + "antu", stem, stem + "tam", stem + "ta",
                 b + "Ani", b + "Ava", b + "Ama"]
    elif tense == "vidhilin":
        forms = [b + "et", b + "etAm", b + "eyuH", b + "eH", b + "etam", b + "eta",
                 b + "eyam", b + "eva", b + "ema"]
    else:
        raise ValueError(tense)
    forms = [_natva(f, len(b)) for f in forms]
    return _row(forms)


AS_TABLE = {
    "lat": ["asti", "staH", "santi", "asi", "sTaH", "sTa", "asmi", "svaH", "smaH"],
    "lan": ["AsIt", "AstAm", "Asan", "AsIH", "Astam", "Asta", "Asam", "Asva", "Asma"],
    "lot": ["astu", "stAm", "santu", "eDi", "stam", "sta", "asAni", "asAva", "asAma"],
    "vidhilin": ["syAt", "syAtAm", "syuH", "syAH", "syAtam", "syAta", "syAm", "syAva", "syAma"],
}
KF_TABLE = {
    "lat": ["karoti", "kurutaH", "kurvanti", "karozi", "kuruTaH", "kuruTa", "karomi", "kurvaH", "kurmaH"],
    "lan": ["akarot", "akurutAm", "akurvan", "akaroH", "akurutam", "akuruta", "akaravam", "akurva", "akurma"],
    "lot": ["karotu", "kurutAm", "kurvantu", "kuru", "kurutam", "kuruta", "karavARi", "karavAva", "karavAma"],
    "vidhilin": ["kuryAt", "kuryAtAm", "kuryuH", "kuryAH", "kuryAtam", "kuryAta", "kuryAm", "kuryAva", "kuryAma"],
}


def conjugate(root: str, tense: str) -> dict:
    """Return {(person, number): form} for a root in the lexicon."""
    if root == "as":
        if tense == "lrt":
            return conjugate("BU", "lrt")
        return _row(AS_TABLE[tense])
    if root == "kf":
        if tense == "lrt":
            return conjugate_thematic("", "lrt", "karizya")
        return _row(KF_TABLE[tense])
    for r, _g, pres, fut, *_ in lx.VERBS:
        if r == root:
            return conjugate_thematic(pres, tense, fut)
    raise KeyError(f"Unknown root {root!r}")


def known_roots() -> list[str]:
    return [v[0] for v in lx.VERBS] + list(lx.IRREGULAR_VERB_META)


def root_meta(root: str) -> dict:
    """Metadata for a root: gloss, transitive, ppp, gerund, infinitive."""
    if root in lx.IRREGULAR_VERB_META:
        g, tr, ppp, ger, inf = lx.IRREGULAR_VERB_META[root]
        return dict(gloss=g, transitive=tr, ppp=ppp, gerund=ger, infinitive=inf)
    for r, g, pres, fut, tr, ppp, ger, inf in lx.VERBS:
        if r == root:
            return dict(gloss=g, transitive=tr, ppp=ppp, gerund=ger, infinitive=inf)
    raise KeyError(root)


# ---------------------------------------------------------------------------
# Index construction & analysis
# ---------------------------------------------------------------------------

class MorphAnalyzer:
    def __init__(self):
        self.index: dict[str, set[Analysis]] = {}
        self.stems: dict[str, dict] = {}      # lemma -> metadata (for paradigm browsing)
        self._build()
        self._vl = None
        self._splitter = None

    # -- build ----------------------------------------------------------------
    def _add(self, a: Analysis):
        self.index.setdefault(a.surface, set()).add(a)

    def _add_nominal(self, stem, cls, gender, gloss, pos, root=None, transitive=None):
        for (case, num), forms in decline(stem, cls, gender).items():
            for f in forms:
                self._add(Analysis(f, stem, pos, gloss, case, num, gender, root=root, transitive=transitive))

    def _build(self):
        for stem, cls, gender, gloss in lx.NOUNS:
            self.stems[stem] = dict(kind="noun", cls=cls, gender=gender, gloss=gloss)
            self._add_nominal(stem, cls, gender, gloss, "noun")

        for stem, gloss, fems in lx.ADJECTIVES:
            self.stems[stem] = dict(kind="adj", cls="a", gender="mfn", gloss=gloss, fems=fems)
            self._add_nominal(stem, "a", "m", gloss, "adj")
            self._add_nominal(stem, "a", "n", gloss, "adj")
            for fs in fems:
                self._add_nominal(fs, "I" if fs.endswith("I") else "A", "f", gloss, "adj")

        for stem, lemma, gloss, mn, fn, nn in lx.PRONOUNS_A:
            self.stems[lemma] = dict(kind="pron", stem=stem, gender="mfn", gloss=gloss,
                                     special=(mn, fn, nn))
            for g, tbl in decline_pronoun_a(stem, mn, fn, nn).items():
                for (case, num), forms in tbl.items():
                    for f in forms:
                        self._add(Analysis(f, lemma, "pron", gloss, case, num, g))
        for lemma, tbl, person, gloss in (("asmad", ASMAD, 1, "I, we"), ("yuzmad", YUZMAD, 2, "you")):
            self.stems[lemma] = dict(kind="pron12", gloss=gloss, person=person)
            for (case, num), forms in _pron12(tbl).items():
                for f in forms:
                    self._add(Analysis(f, lemma, "pron", gloss, case, num, None, person=person,
                                       note="enclitic (unstressed) form" if f in ENCLITICS else ""))

        for root in known_roots():
            meta = root_meta(root)
            self.stems["√" + root] = dict(kind="verb", root=root, **meta)
            if meta["ppp"]:
                ppp = meta["ppp"]
                gloss = f"past participle of √{root} ({meta['gloss']})"
                self.stems[ppp] = dict(kind="ppp", root=root, gender="mfn", gloss=gloss)

        for form, gloss in lx.INDECLINABLES:
            self._add(Analysis(form, form, "indecl", gloss))

    # -- analyze ------------------------------------------------------------------
    @property
    def verb_layer(self):
        """Wide-coverage verb analysis (built on first use: about 5 s and 60 MB)."""
        if self._vl is None:
            from .verblayer import VerbLayer
            self._vl = VerbLayer()
        return self._vl

    @property
    def splitter(self) -> Splitter:
        if self._splitter is None:
            known = set(self.index) | set(self.verb_layer.fidx) | set(self.verb_layer.plain)
            self._splitter = Splitter(known)
        return self._splitter

    def _direct(self, slp: str) -> list[Analysis]:
        found = set(self.index.get(slp, ())) | set(self.verb_layer.base(slp))
        return sorted(found, key=_sort_key)

    def lookup_slp(self, slp: str) -> list[Analysis]:
        found = self._direct(slp)
        if not found and slp.endswith("M"):
            found = [replace(a, note=a.note or "written with anusvāra for final m") for a in self._direct(slp[:-1] + "m")]
        return found

    def analyze(self, token: str, script: str | None = None) -> "TokenAnalysis":
        script = script or detect_script(token)
        slp = to_slp1(token, script)
        slp = slp.replace(".", "").strip()
        direct = self.lookup_slp(slp)
        analyses = list(direct)
        if not direct:
            analyses = sorted(self.verb_layer.prefixed(slp), key=_sort_key)
        restored: list[Analysis] = []
        if not analyses:
            for cand, why in restore_finals(slp):
                found = self.lookup_slp(cand) or sorted(self.verb_layer.prefixed(cand), key=_sort_key)
                for a in found:
                    restored.append(replace(a, surface=slp, note=(a.note + "; " if a.note else "") + "sandhi-restored: " + why))
            analyses = sorted(set(restored), key=_sort_key)
        splits = []
        if not analyses:
            splits = self.splitter.split(slp)
        return TokenAnalysis(token, slp, analyses, splits, bool(restored))

    def suggest(self, token: str, n: int = 3) -> list[str]:
        slp = to_slp1(token)
        return difflib.get_close_matches(slp, list(self.index), n=n, cutoff=0.78)

    @property
    def n_forms(self) -> int:
        return len(self.index) + (len(self._vl.fidx) + len(self._vl.plain) if self._vl else 0)


def _sort_key(a: Analysis):
    order = {"verb": 0, "pron": 1, "noun": 2, "adj": 3, "ppp": 4, "ktavatu": 4, "prap": 4, "pmp": 4, "gdv": 4,
             "gerund": 5, "infinitive": 6, "indecl": 7}
    return (order[a.pos], a.lemma, a.case or 0, a.number or "", a.gender or "", a.tense or "", a.person or 0)


@dataclass
class TokenAnalysis:
    token: str
    slp: str
    analyses: list[Analysis]
    splits: list[list[str]] = field(default_factory=list)
    via_sandhi_restoration: bool = False

    @property
    def resolved(self) -> bool:
        return bool(self.analyses)


@lru_cache(maxsize=1)
def get_analyzer() -> MorphAnalyzer:
    return MorphAnalyzer()


def paradigm_table(stem: str) -> dict:
    """Display-ready paradigm for a noun/adjective/participle stem or a root.
    Returns {'kind', 'title', 'rows': [...]}; used by the UI and the LLM tools."""
    an = get_analyzer()
    key = stem if stem in an.stems else "√" + stem if ("√" + stem) in an.stems else None
    if key is None:
        raise KeyError(stem)
    meta = an.stems[key]
    if meta["kind"] == "verb":
        root = meta["root"]
        rows = []
        for tense in TENSES:
            tbl = conjugate(root, tense)
            rows.append({"tense": tense, "forms": {pn: f for pn, f in tbl.items()}})
        return {"kind": "verb", "title": "√" + root, "gloss": meta["gloss"], "rows": rows}
    if meta["kind"] == "pron":
        tables = decline_pronoun_a(meta["stem"], *meta["special"])
        return {"kind": "pron", "title": key, "gloss": meta["gloss"], "tables": tables}
    if meta["kind"] == "pron12":
        tbl = _pron12(ASMAD if key == "asmad" else YUZMAD)
        return {"kind": "pron12", "title": key, "gloss": meta["gloss"], "tables": {None: tbl}}
    if meta["kind"] == "noun":
        return {"kind": "noun", "title": key, "gloss": meta["gloss"],
                "tables": {meta["gender"]: decline(key, meta["cls"], meta["gender"])}}
    # adjective or participle: three genders
    tables = {"m": decline(key, "a", "m")}
    fems = meta.get("fems") or [key[:-1] + "A"]
    tables["f"] = decline(fems[0], "I" if fems[0].endswith("I") else "A", "f")
    tables["n"] = decline(key, "a", "n")
    return {"kind": meta["kind"], "title": key, "gloss": meta["gloss"], "tables": tables}
