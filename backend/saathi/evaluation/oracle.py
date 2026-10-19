"""Compare rule-generated verb forms with an independent Pāṇinian derivation engine (vidyut).

Only forms that this repository *generates by rule* are compared (thematic present system, future,
conditional, passive, causative). Forms that are listed from vidyut (athematic tables, perfect) would
only confirm themselves, so they are excluded.

The oracle is itself imperfect software: a disagreement means "look here", not "the engine is wrong".
"""
from __future__ import annotations
from collections import Counter, defaultdict

from .. import verbs

try:  # vidyut is an optional development dependency
    from vidyut.prakriya import (Dhatu, Gana, Lakara, Pada, Prayoga, Purusha, Sanadi, Vacana, Vyakarana)
    HAVE_VIDYUT = True
except Exception:  # pragma: no cover
    HAVE_VIDYUT = False

LAKARA = {"lat": "Lat", "lan": "Lan", "lot": "Lot", "vidhilin": "VidhiLin", "lrt": "Lrt", "lrn": "Lrn"}
P_SUFFIX = {"tip", "tas", "Ji", "sip", "Tas", "Ta", "mip", "vas", "mas"}
A_SUFFIX = {"ta", "AtAm", "Ja", "TAs", "ATAm", "Dvam", "iw", "vahi", "mahi"}


def _gana(g: int):
    return {1: Gana.Bhvadi, 2: Gana.Adadi, 3: Gana.Juhotyadi, 4: Gana.Divadi, 5: Gana.Svadi, 6: Gana.Tudadi,
            7: Gana.Rudhadi, 8: Gana.Tanadi, 9: Gana.Kryadi, 10: Gana.Curadi}[g]


def _voice(prakriya) -> str:
    for step in prakriya.history:
        if len(step.result) >= 2:
            last = step.result[-1]
            if last in P_SUFFIX:
                return "P"
            if last in A_SUFFIX:
                return "A"
    return "P"


def oracle_cells(aup: str, gana: int, lakara: str, prayoga: str = "act", causative: bool = False) -> dict[str, list[set[str]]]:
    """{'P': [9 sets], 'A': [9 sets]} of forms derived by vidyut."""
    v = Vyakarana()
    d = Dhatu.mula(aup, _gana(gana), sanadi=[Sanadi.Ric] if causative else None)
    out = {"P": [set() for _ in range(9)], "A": [set() for _ in range(9)]}
    pr = Prayoga.Karmani if prayoga == "pass" else Prayoga.Kartari
    lak = getattr(Lakara, LAKARA[lakara])
    pers = [(Purusha.Prathama, Vacana.Eka), (Purusha.Prathama, Vacana.Dvi), (Purusha.Prathama, Vacana.Bahu),
            (Purusha.Madhyama, Vacana.Eka), (Purusha.Madhyama, Vacana.Dvi), (Purusha.Madhyama, Vacana.Bahu),
            (Purusha.Uttama, Vacana.Eka), (Purusha.Uttama, Vacana.Dvi), (Purusha.Uttama, Vacana.Bahu)]
    for i, (pur, vac) in enumerate(pers):
        for r in v.derive(Pada.Tinanta(dhatu=d, prayoga=pr, lakara=lak, purusha=pur, vacana=vac)):
            out["A" if prayoga == "pass" else _voice(r)][i].add(r.text)
    # vidyut also lists the final-d (pausa) variants of -t forms; those are sandhi, not different forms
    for v_ in out.values():
        for cell in v_:
            for f in [f for f in cell if f.endswith("d") and f[:-1] + "t" in cell]:
                cell.discard(f)
    return out


CATEGORIES = [("act", t) for t in ("lat", "lan", "lot", "vidhilin", "lrt", "lrn")] + \
             [("mid", t) for t in ("lat", "lan", "lot", "vidhilin", "lrt", "lrn")] + \
             [("pass", t) for t in ("lat", "lan", "lot", "vidhilin")] + \
             [("cau-act", t) for t in ("lat", "lan", "lot", "vidhilin", "lrt")] + \
             [("cau-mid", t) for t in ("lat", "lan", "lot", "vidhilin", "lrt")]


def run_oracle_eval(limit: int | None = None, gana_filter=(1, 4, 6, 10), max_examples: int = 40) -> dict:
    if not HAVE_VIDYUT:
        raise RuntimeError("vidyut is not installed (pip install vidyut)")
    stats = Counter()
    by_cat: dict[str, Counter] = defaultdict(Counter)
    examples: list[dict] = []
    roots = [v for v in verbs.load_verbs() if v.gana in gana_filter]
    if limit:
        roots = roots[:limit]
    raw = {e["k"]: e["a"] for e in __import__("json").loads(verbs.DATA.read_text(encoding="utf-8"))["entries"]}
    for v in roots:
        aup = raw[v.key]
        cache: dict = {}
        for voice, tense in CATEGORIES:
            mine = verbs.forms(v, voice, tense)
            if not mine:
                continue
            pk = "P" if voice in ("act", "cau-act") else "A"
            ck = (voice.startswith("cau"), voice == "pass", tense)
            try:
                if ck not in cache:
                    cache[ck] = oracle_cells(aup, v.gana, tense, "pass" if voice == "pass" else "act", voice.startswith("cau"))
                theirs = cache[ck][pk]
            except Exception:
                stats["oracle_error"] += 1
                continue
            for i, cell in enumerate(mine):
                ours, ref = set(cell), theirs[i]
                cat = f"{voice}/{tense}"
                stats["compared"] += 1
                by_cat[cat]["compared"] += 1
                if ours == ref:
                    stats["agree"] += 1
                    by_cat[cat]["agree"] += 1
                elif ours and ref and ours <= ref:
                    stats["oracle_has_more_variants"] += 1
                    by_cat[cat]["more_variants"] += 1
                elif not ref:
                    stats["oracle_empty"] += 1
                    by_cat[cat]["oracle_empty"] += 1
                else:
                    stats["mismatch"] += 1
                    by_cat[cat]["mismatch"] += 1
                    if len(examples) < max_examples:
                        examples.append({"root": v.root, "gana": v.gana, "cell": f"{cat}[{verbs.PN[i]}]",
                                         "engine": sorted(ours), "oracle": sorted(ref)})
    c = stats["compared"] or 1
    return {
        "roots_checked": len(roots), "compared": stats["compared"], "agreement": stats["agree"] / c,
        "agree_or_subset": (stats["agree"] + stats["oracle_has_more_variants"]) / c,
        "engine_only": stats["oracle_empty"], "oracle_only": stats["oracle_has_more_variants"],
        "mismatches": stats["mismatch"], "oracle_errors": stats["oracle_error"],
        "by_category": {k: dict(v) for k, v in sorted(by_cat.items())}, "examples": examples,
    }


# ---------------------------------------------------------------------------
# Participles (rule-generated declensions) vs the oracle
# ---------------------------------------------------------------------------

def _subanta(v, d, krt, linga, vibhakti, vacana) -> set[str]:
    from vidyut.prakriya import Pratipadika
    try:
        out = {r.text for r in v.derive(Pada.Subanta(pratipadika=Pratipadika.krdanta(d, krt), linga=linga,
                                                     vibhakti=vibhakti, vacana=vacana))}
    except Exception:
        return set()
    return {f for f in out if not (f.endswith("d") and f[:-1] + "t" in out)}   # drop pausa variants


def run_participle_eval(limit: int = 150, seed: int = 1) -> dict:
    """Compare the declension of śatṛ, śānac, kta and ktavatu forms with vidyut for a random sample of roots."""
    import json
    import random
    from vidyut.prakriya import Krt, Linga, Vibhakti
    from .. import participles
    if not HAVE_VIDYUT:
        raise RuntimeError("vidyut is not installed")
    raw = {e["k"]: e["a"] for e in json.loads(verbs.DATA.read_text(encoding="utf-8"))["entries"]}
    vs = [v for v in verbs.load_verbs() if v.gana in (1, 4, 6, 10)]
    random.Random(seed).shuffle(vs)
    V = Vyakarana()
    vib = [Vibhakti.Prathama, Vibhakti.Dvitiya, Vibhakti.Trtiya, Vibhakti.Caturthi, Vibhakti.Panchami,
           Vibhakti.Sasthi, Vibhakti.Saptami]
    lingas = {"m": Linga.Pum, "n": Linga.Napumsaka}   # feminine -ī forms from vidyut are mis-aligned for participles, so they are not compared
    numbers = [("sg", Vacana.Eka), ("du", Vacana.Dvi), ("pl", Vacana.Bahu)]
    stats = Counter()
    examples = []
    subset_examples: list = []
    kinds = [("Satf", Krt.Satf), ("ktavatu", Krt.ktavatu), ("kta", Krt.kta)]
    n = 0
    for v in vs:
        if n >= limit:
            break
        n += 1
        d = Dhatu.mula(raw[v.key], _gana(v.gana))
        for kind, krt in kinds:
            stems = {"Satf": [s[:-1] + "at" for s in (v.pres.get("P", "") or "").split("|") if s.endswith("a")],
                     "ktavatu": [k[:-1] + "avat" for k in v.kta], "kta": list(v.kta)}[kind]
            if not stems:
                continue
            for stem in stems[:1]:
                mine = participles.forms_for(kind, stem, v.gana == 6 and kind == "Satf")
                for g, linga in lingas.items():
                    for ci, vb in enumerate(vib, start=1):
                        for num, vac in numbers:
                            ours = set(mine.get((g, ci, num), []))
                            ref = _subanta(V, d, krt, linga, vb, vac)
                            if not ref or not ours:
                                continue
                            stats["compared"] += 1
                            stats[f"{kind}:compared"] += 1
                            if ours == ref:
                                stats["agree"] += 1
                                stats[f"{kind}:agree"] += 1
                            elif ours <= ref:
                                stats["engine_subset"] += 1
                                if len(subset_examples) < 12:
                                    subset_examples.append({"root": v.root, "kind": kind, "cell": f"{g}/{ci}/{num}",
                                                            "engine": sorted(ours), "oracle": sorted(ref)})
                            elif ref <= ours:
                                stats["engine_superset"] += 1
                            else:
                                stats["mismatch"] += 1
                                if len(examples) < 20:
                                    examples.append({"root": v.root, "kind": kind, "cell": f"{g}/{ci}/{num}",
                                                     "engine": sorted(ours), "oracle": sorted(ref)})
    c = stats["compared"] or 1
    return {"roots": n, "compared": stats["compared"], "agreement": stats["agree"] / c,
            "agree_or_subset": (stats["agree"] + stats["engine_subset"]) / c,
            "engine_superset": stats["engine_superset"], "engine_subset": stats["engine_subset"],
            "mismatches": stats["mismatch"],
            "by_kind": {k: stats[f"{k}:agree"] / max(stats[f"{k}:compared"], 1) for k, _ in kinds}, "examples": examples,
            "subset_examples": subset_examples}
