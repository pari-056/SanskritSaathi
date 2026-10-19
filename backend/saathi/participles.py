"""Declension of verbal adjectives: -a participles (kta, tavya, anīya, śānac) and -at / -vat stems (śatṛ, ktavatu)."""
from __future__ import annotations
from .morph import decline  # noqa: E402  (nominal paradigms live in morph)

CASES = range(1, 9)


def decline_at(stem: str, gender: str, fem_weak: bool = False, vat: bool = False) -> dict:
    """Stems in -at (present active participle, e.g. gacCat) and -vat (e.g. gatavat).

    The strong stem inserts n (gacCant-); the weak stem is the bare -at stem. `fem_weak` also yields the
    feminine in -atī (class 6 tudatī) besides -antī.
    """
    assert stem.endswith("at")
    weak, strong = stem, stem[:-2] + "ant"
    nom_m = stem[:-2] + ("An" if vat else "an")
    voc_m = stem[:-2] + "an"
    d_stem = stem[:-1] + "d"          # before bh-: gacCad-
    if gender == "m":
        r = {
            (1, "sg"): [nom_m], (1, "du"): [strong + "O"], (1, "pl"): [strong + "aH"],
            (2, "sg"): [strong + "am"], (2, "du"): [strong + "O"], (2, "pl"): [weak + "aH"],
            (8, "sg"): [voc_m], (8, "du"): [strong + "O"], (8, "pl"): [strong + "aH"],
        }
    elif gender == "n":
        # neuter dual: -antī (and optionally -atī) for śatṛ participles; only -atī for -vat/-mat stems
        nd = [weak + "I"] if vat else [strong + "I"] + ([weak + "I"] if fem_weak else [])
        r = {
            (1, "sg"): [weak], (1, "du"): nd, (1, "pl"): [strong + "i"],
            (2, "sg"): [weak], (2, "du"): nd, (2, "pl"): [strong + "i"],
            (8, "sg"): [weak], (8, "du"): nd, (8, "pl"): [strong + "i"],
        }
    else:
        out: dict = {}
        for fs in ([strong] + ([weak] if fem_weak else [])):
            for k, v in decline(fs + "I", "I", "f").items():
                out.setdefault(k, [])
                out[k] += [x for x in v if x not in out[k]]
        return out
    r.update({
        (3, "sg"): [weak + "A"], (3, "du"): [d_stem + "ByAm"], (3, "pl"): [d_stem + "BiH"],
        (4, "sg"): [weak + "e"], (4, "du"): [d_stem + "ByAm"], (4, "pl"): [d_stem + "ByaH"],
        (5, "sg"): [weak + "aH"], (5, "du"): [d_stem + "ByAm"], (5, "pl"): [d_stem + "ByaH"],
        (6, "sg"): [weak + "aH"], (6, "du"): [weak + "oH"], (6, "pl"): [weak + "Am"],
        (7, "sg"): [weak + "i"], (7, "du"): [weak + "oH"], (7, "pl"): [weak + "su"],
    })
    return r


def decline_vat_fem(stem: str) -> dict:
    """ktavatu feminine: gatavatI (nadī type)."""
    return decline(stem + "I", "I", "f")


def adjective_forms(stem: str) -> dict:
    """Three-gender -a adjective: {(gender, case, number): [forms]} (feminine in -ā)."""
    out: dict = {}
    for g, cls, st in (("m", "a", stem), ("n", "a", stem), ("f", "A", stem[:-1] + "A")):
        for (c, n), forms in decline(st, cls, g).items():
            out[(g, c, n)] = forms
    return out


def forms_for(kind: str, stem: str, fem_weak: bool = False) -> dict:
    """{(gender, case, number): [forms]} for a derived stem of the given kind."""
    if kind in ("kta", "ckta", "tavya", "anIya", "SAnac", "ya"):
        return adjective_forms(stem)
    out: dict = {}
    for g in "mnf":
        if g == "f" and kind == "ktavatu":
            tbl = decline_vat_fem(stem[:-2] + "at")   # gatavatI
        else:
            tbl = decline_at(stem, g, fem_weak, vat=(kind == "ktavatu"))
        for (c, n), forms in tbl.items():
            out[(g, c, n)] = forms
    return out
