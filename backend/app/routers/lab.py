from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from saathi import morph, selfcheck, tools, verbs
from saathi.syntax import analyze_sentence
from saathi.translit import convert, detect_script, slp1_to_dev, slp1_to_iast, to_slp1
from ..deps import ProgressHandle, progress_handle
from ..schemas import JoinIn, SentenceIn, TranslitIn, WordIn

router = APIRouter(prefix="/api/lab", tags=["lab"])


@router.post("/sentence")
def sentence(body: SentenceIn, _: ProgressHandle = Depends(progress_handle)):
    sa = analyze_sentence(body.text)
    d = sa.to_dict()
    for row, t in zip(d["tokens"], sa.tokens):
        row["iast"] = slp1_to_iast(t.slp)
        row["alternatives"] = [{"lemma": a.lemma_display(), "pos": a.pos_label(), "features": a.features_en()}
                               for a in t.alternatives]
    return d


@router.post("/word")
def word(body: WordIn, _: ProgressHandle = Depends(progress_handle)):
    an = morph.get_analyzer()
    r = an.analyze(body.text.strip().split()[0])
    return {"found": r.resolved, "total": len(r.analyses),
            "analyses": [{"lemma": a.lemma_display(), "type": a.pos_label(), "features": a.features_en(),
                          "meaning": a.gloss, "note": a.note} for a in r.analyses[:40]],
            "splits": [[slp1_to_dev(w) for w in s] for s in r.splits[:4]],
            "suggestions": [slp1_to_dev(s) for s in an.suggest(body.text.strip().split()[0])]}


@router.post("/sandhi/join")
def join(body: JoinIn, _: ProgressHandle = Depends(progress_handle)):
    r = tools.sandhi_join(body.first, body.second)
    if "error" in r:
        raise HTTPException(400, r["error"])
    return r


@router.post("/sandhi/split")
def split(body: WordIn, _: ProgressHandle = Depends(progress_handle)):
    return tools.sandhi_split(body.text)


@router.post("/transliterate")
def transliterate(body: TranslitIn, _: ProgressHandle = Depends(progress_handle)):
    return {"detected": detect_script(body.text),
            **{t: convert(body.text, t) for t in ("devanagari", "iast", "hk", "slp1")}}


@router.get("/stems")
def stems(_: ProgressHandle = Depends(progress_handle)):
    an = morph.get_analyzer()
    out = []
    for k, v in an.stems.items():
        if v["kind"] in ("noun", "adj", "pron", "pron12", "verb", "ppp"):
            base = k.lstrip("√")
            out.append({"key": k, "label": ("√" if k.startswith("√") else "") + slp1_to_dev(base) + f" ({slp1_to_iast(base)})",
                        "meaning": v["gloss"], "kind": v["kind"]})
    return {"stems": out, "n_forms": an.n_forms, "tenses": [{"id": t, "label": morph.TENSE_EN[t]} for t in morph.TENSES]}


@router.get("/paradigm")
def paradigm(key: str, tense: str = "lat", _: ProgressHandle = Depends(progress_handle)):
    an = morph.get_analyzer()
    if key not in an.stems:
        raise HTTPException(404, "Unknown stem")
    meta = an.stems[key]
    if meta["kind"] == "verb":
        if tense not in morph.TENSES:
            raise HTTPException(400, "Unknown tense")
        tbl = morph.conjugate(meta["root"], tense)
        m = morph.root_meta(meta["root"])
        return {"kind": "verb", "title": "√" + slp1_to_dev(meta["root"]), "meaning": meta["gloss"],
                "rows": [{"person": p, "person_sa": morph.PERSON_SA[p], **{n: slp1_to_dev(tbl[(p, n)]) for n in morph.NUMBERS}}
                         for p in (3, 2, 1)],
                "extras": {"participle": slp1_to_dev(m["ppp"]) if m["ppp"] else None,
                           "gerund": slp1_to_dev(m["gerund"]) if m["gerund"] else None,
                           "infinitive": slp1_to_dev(m["infinitive"]) if m["infinitive"] else None}}
    pt = morph.paradigm_table(key)
    tables = []
    for g, tbl in pt["tables"].items():
        cases = [c for c in morph.CASES if (c, "sg") in tbl]
        tables.append({"gender": g, "gender_label": morph.GEN_EN.get(g, "") if g else "",
                       "rows": [{"case": c, "case_sa": morph.CASE_SA[c], "case_en": morph.CASE_EN[c],
                                 **{n: " / ".join(slp1_to_dev(f) for f in tbl[(c, n)]) for n in morph.NUMBERS}} for c in cases]})
    return {"kind": pt["kind"], "title": slp1_to_dev(key), "meaning": pt["gloss"], "tables": tables}


@router.get("/selfcheck")
def selfcheck_run(_: ProgressHandle = Depends(progress_handle)):
    return selfcheck.run_all()


# ---------------------------------------------------------------------------
# Verb explorer (2,200+ roots from the Dhātupāṭha)
# ---------------------------------------------------------------------------
GANA_NAMES = {1: "bhvādi", 2: "adādi", 3: "juhotyādi", 4: "divādi", 5: "svādi", 6: "tudādi", 7: "rudhādi",
              8: "tanādi", 9: "kryādi", 10: "curādi"}
VOICE_LABELS = {"act": "Active (parasmaipada)", "mid": "Middle (ātmanepada)", "pass": "Passive",
                "cau-act": "Causative (parasmaipada)", "cau-mid": "Causative (ātmanepada)"}


def _verb_summary(v) -> dict:
    return {"key": v.key, "root": slp1_to_dev(v.root), "iast": slp1_to_iast(v.root), "gana": v.gana,
            "gana_name": GANA_NAMES[v.gana], "meaning": slp1_to_dev(v.meaning) if v.meaning else "",
            "padas": v.padas}


@router.get("/verbs")
def search_verbs(q: str, _: ProgressHandle = Depends(progress_handle)):
    q = q.strip()
    if not q or len(q) > 40:
        raise HTTPException(400, "Enter a root such as गम्, gam or paW")
    slp = to_slp1(q).rstrip("H")
    hits = [v for v in verbs.load_verbs() if v.root == slp] or [v for v in verbs.load_verbs() if v.root.startswith(slp)]
    return {"results": [_verb_summary(v) for v in hits[:30]], "total": len(hits)}


@router.get("/verbs/{key}")
def verb_table(key: str, voice: str = "act", tense: str = "lat", _: ProgressHandle = Depends(progress_handle)):
    v = next((x for x in verbs.load_verbs() if x.key == key), None)
    if not v:
        raise HTTPException(404, "Unknown root")
    if voice not in verbs.VOICES or tense not in verbs.TENSES:
        raise HTTPException(400, "Unknown voice or tense")
    available = {vo: [t for t in verbs.TENSES if any(verbs.forms(v, vo, t))] for vo in verbs.VOICES}
    available = {vo: ts for vo, ts in available.items() if ts}
    cells = verbs.forms(v, voice, tense)
    rows = []
    for p in (3, 2, 1):
        row = {"person": p, "person_sa": morph.PERSON_SA[p]}
        for n in morph.NUMBERS:
            i = verbs.PN.index((p, n))
            row[n] = " / ".join(slp1_to_dev(f) for f in cells[i]) if cells else ""
        rows.append(row)

    def stems(vals):
        return [slp1_to_dev(x) for x in vals]
    return {
        **_verb_summary(v), "voice": voice, "tense": tense, "rows": rows,
        "available": {vo: [{"id": t, "label": morph.TENSE_ALL_EN[t]} for t in ts] for vo, ts in available.items()},
        "voice_labels": {vo: VOICE_LABELS[vo] for vo in available},
        "principal_parts": {"past participle (kta)": stems(v.kta), "gerund (ktvā)": stems(v.ktvA),
                            "infinitive": stems(v.tumun), "gerund with prefix (lyap)": stems(v.lyap),
                            "gerundive (tavya)": stems(v.tavya), "gerundive (anīya)": stems(v.anIya),
                            "gerundive (-ya)": stems(v.ya)},
        "athematic_or_listed": v.athematic,
    }
