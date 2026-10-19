"""Build saathi/data/verbs.json from the Dhātupāṭha using the vidyut Pāṇinian derivation engine.

Development-time tool (the app itself does NOT need vidyut). It records, for every root:
  * principal parts (present / future / passive / causative stems, kta, tumun, ktvā, tavya, anīya)
  * for athematic roots (gaṇas 2, 3, 5, 7, 8, 9): complete laṭ/laṅ/loṭ/vidhiliṅ tables
  * the perfect (liṭ) tables for every root

    pip install vidyut
    python tools/build_verb_lexicon.py            # downloads the Dhātupāṭha TSV if needed

vidyut is MIT-licensed (https://github.com/ambuda-org/vidyut). The generated data is verified
against this repository's own rule engine in tests/test_verbs.py.
"""
from __future__ import annotations
import json
import sys
import urllib.request
from pathlib import Path

from vidyut.prakriya import (Dhatu, Gana, Krt, Lakara, Linga, Pada, Pratipadika, Prayoga, Purusha, Sanadi,
                             Vacana, Vibhakti, Vyakarana)

ROOT = Path(__file__).resolve().parents[1]
TSV_URL = "https://raw.githubusercontent.com/ambuda-org/vidyut/main/vidyut-prakriya/data/dhatupatha.tsv"
TSV = ROOT / "data" / "dhatupatha.tsv"
OUT = ROOT / "saathi" / "data" / "verbs.json"

GANA = {1: Gana.Bhvadi, 2: Gana.Adadi, 3: Gana.Juhotyadi, 4: Gana.Divadi, 5: Gana.Svadi, 6: Gana.Tudadi,
        7: Gana.Rudhadi, 8: Gana.Tanadi, 9: Gana.Kryadi, 10: Gana.Curadi}
PERSONS = [(Purusha.Prathama, Vacana.Eka), (Purusha.Prathama, Vacana.Dvi), (Purusha.Prathama, Vacana.Bahu),
           (Purusha.Madhyama, Vacana.Eka), (Purusha.Madhyama, Vacana.Dvi), (Purusha.Madhyama, Vacana.Bahu),
           (Purusha.Uttama, Vacana.Eka), (Purusha.Uttama, Vacana.Dvi), (Purusha.Uttama, Vacana.Bahu)]
PARA = {"tip", "tas", "Ji", "sip", "Tas", "Ta", "mip", "vas", "mas", "ṇal", "Ral", "atus", "us", "thal", "Ratus", "Rus"}
V = Vyakarana()


def ensure_tsv() -> list[list[str]]:
    if not TSV.exists():
        TSV.parent.mkdir(parents=True, exist_ok=True)
        TSV.write_bytes(urllib.request.urlopen(TSV_URL, timeout=60).read())
    return [l.rstrip("\n").split("\t") for l in TSV.read_text(encoding="utf-8").splitlines()][1:]


def voice_of(prakriya) -> str | None:
    """'P' or 'A' from the tiṅ suffix that was attached (look for the first 9-suffix term)."""
    for step in prakriya.history:
        if len(step.result) >= 2:
            last = step.result[-1]
            if last in ("tip", "tas", "Ji", "sip", "Tas", "Ta", "mip", "vas", "mas"):
                return "P"
            if last in ("ta", "AtAm", "Ja", "TAs", "ATAm", "Dvam", "iw", "vahi", "mahi"):
                return "A"
            if last in ("tip", "la~w"):
                continue
    return None


def tin(d, lak, pn, prayoga=Prayoga.Kartari) -> dict[str, list[str]]:
    out: dict[str, set[str]] = {"P": set(), "A": set()}
    pur, vac = pn
    for r in V.derive(Pada.Tinanta(dhatu=d, prayoga=prayoga, lakara=lak, purusha=pur, vacana=vac)):
        v = voice_of(r)
        out[v or "P"].add(r.text)
    # vidyut also lists final-d (pausa) variants of -t forms; they are sandhi, not separate forms
    for k, vals in out.items():
        for f in [f for f in vals if f.endswith("d") and f[:-1] + "t" in vals]:
            vals.discard(f)
    return {k: sorted(v) for k, v in out.items() if v}


def clean_root(aup: str, gana) -> str | None:
    d = Dhatu.mula(aup, gana)
    rs = V.derive(Pada.Tinanta(dhatu=d, prayoga=Prayoga.Kartari, lakara=Lakara.Lat, purusha=Purusha.Prathama, vacana=Vacana.Eka))
    for r in rs:
        for step in r.history:
            if len(step.result) == 2:
                return step.result[0]
    return None


def strip_end(forms: list[str], ends: tuple[str, ...]) -> str | None:
    """All stems (variants joined by '|', first listed first) obtained by removing the 3sg ending."""
    out = []
    for f in forms:
        for e in ends:
            if f.endswith(e):
                st = f[: -len(e)]
                if st not in out:
                    out.append(st)
                break
    return "|".join(out) if out else None


def krd_nom(d, krt) -> str | None:
    """Nominative singular masculine(s), '|'-joined when the grammar allows several."""
    rs = V.derive(Pada.Subanta(pratipadika=Pratipadika.krdanta(d, krt), linga=Linga.Pum,
                               vibhakti=Vibhakti.Prathama, vacana=Vacana.Eka))
    out = list(dict.fromkeys(r.text for r in rs))
    return "|".join(out) if out else None


def avyaya(d, krt) -> str | None:
    rs = V.derive(Pada.make_avyaya(Pratipadika.krdanta(d, krt)))
    out = list(dict.fromkeys(r.text for r in rs))
    return "|".join(out) if out else None


def build_entry(code: str, aup: str, artha: str) -> dict | None:
    g = int(code[:2])
    gana = GANA[g]
    try:
        d = Dhatu.mula(aup, gana)
        root = clean_root(aup, gana)
        if not root:
            return None
        e: dict = {"k": code, "r": root, "g": g, "a": aup, "m": artha.strip()}
        lat = tin(d, Lakara.Lat, PERSONS[0])
        if not lat:
            return None
        e["pada"] = "".join(sorted(lat)).replace("AP", "PA")
        athematic = g in (2, 3, 5, 7, 8, 9)
        if not athematic:
            probe = {v_: strip_end(lat[v_], ("ti",) if v_ == "P" else ("te",)) for v_ in lat}
            if any(not st or not all(x.endswith("a") for x in st.split("|")) for st in probe.values()):
                athematic = True      # irregular present stem (e.g. Sru → SfRoti): list the paradigm instead
        if not athematic:
            ps, fs = {}, {}
            for v, ends in (("P", ("ti",)), ("A", ("te",))):
                if v in lat:
                    s = strip_end(lat[v], ends)
                    if s:
                        ps[v] = s
                    fu = tin(d, Lakara.Lrt, PERSONS[0]).get(v)
                    if fu:
                        fs[v] = strip_end(fu, ends)
            e["pres"], e["fut"] = ps, fs
        else:
            tables = {}
            for tag, lak in (("lat", Lakara.Lat), ("lan", Lakara.Lan), ("lot", Lakara.Lot), ("vid", Lakara.VidhiLin)):
                per = {"P": [], "A": []}
                for pn in PERSONS:
                    cell = tin(d, lak, pn)
                    for v in ("P", "A"):
                        per[v].append("|".join(cell.get(v, [])))
                tables[tag] = {v: c for v, c in per.items() if any(c)}
            e["tbl"] = tables
            fu = tin(d, Lakara.Lrt, PERSONS[0])
            e["fut"] = {v: strip_end(f, ("ti", "te")) for v, f in fu.items()}
        # passive & causative (3sg laṭ)
        ps = tin(d, Lakara.Lat, PERSONS[0], Prayoga.Karmani)
        if ps.get("A"):
            e["pass"] = strip_end(ps["A"], ("te",))
        dc = Dhatu.mula(aup, gana, sanadi=[Sanadi.Ric])
        ca = tin(dc, Lakara.Lat, PERSONS[0])
        e["cau"] = {v: strip_end(f, ("ti" if v == "P" else "te",)) for v, f in ca.items()}
        # causative derivatives (kta, ktvā, lyap via prefix ā, tumun)
        try:
            ck = krd_nom(dc, Krt.kta)
            if ck:
                e["ckta"] = "|".join(x[:-1] for x in ck.split("|") if x.endswith("aH"))
            for tag, krt in (("cktvA", Krt.ktvA), ("ctumun", Krt.tumun)):
                a_ = avyaya(dc, krt)
                if a_:
                    e[tag] = a_
            if root[0] not in "aAiIuUfFxXeEoO":
                lp = avyaya(Dhatu.mula(aup, gana, sanadi=[Sanadi.Ric], prefixes=["A"]), Krt.ktvA)
                vs = [x[1:] for x in (lp or "").split("|") if x.startswith("A") and not x.endswith("tvA")]
                if vs:
                    e["clyap"] = "|".join(vs)
        except Exception:
            pass
        # present participles of athematic roots (thematic ones are built by rule): stems from the accusative singular
        if athematic:
            try:
                accs = [r.text for r in V.derive(Pada.Subanta(pratipadika=Pratipadika.krdanta(d, Krt.Satf), linga=Linga.Pum,
                                                              vibhakti=Vibhakti.Dvitiya, vacana=Vacana.Eka))]
                st = []
                for a_ in accs:
                    x = a_[:-4] + "at" if a_.endswith("antam") else (a_[:-2] if a_.endswith("atam") else None)
                    if x and x not in st:
                        st.append(x)
                if st:
                    e["prap"] = "|".join(st)
                sn = krd_nom(d, Krt.SAnac)
                if sn:
                    e["pmp"] = "|".join(x[:-1] for x in sn.split("|") if x.endswith("aH"))
            except Exception:
                pass
        # periphrastic future (luṭ)
        lut = {"P": [], "A": []}
        for pn in PERSONS:
            cell = tin(d, Lakara.Lut, pn)
            for v_ in ("P", "A"):
                lut[v_].append("|".join(cell.get(v_, [])))
        e["lut"] = {v_: c for v_, c in lut.items() if any(c)}
        # nominal / indeclinable derivatives
        ya = []
        for krt in (Krt.yat, Krt.Ryat, Krt.kyap):
            n = krd_nom(d, krt)
            if n:
                ya += [x[:-1] for x in n.split("|") if x.endswith("aH") and x[:-1] not in ya]
        if ya:
            e["ya"] = "|".join(ya)
        for tag, krt in (("kta", Krt.kta), ("tavya", Krt.tavyat), ("anIya", Krt.anIyar)):
            n = krd_nom(d, krt)
            if n:
                stems = [x[:-1] for x in n.split("|") if x.endswith("aH")]
                if stems:
                    e[tag] = "|".join(stems)
        for tag, krt in (("ktvA", Krt.ktvA), ("tumun", Krt.tumun)):
            a = avyaya(d, krt)
            if a:
                e[tag] = a
        # aorist
        lun = {"P": [], "A": []}
        for pn in PERSONS:
            cell = tin(d, Lakara.Lun, pn)
            for v_ in ("P", "A"):
                lun[v_].append("|".join(cell.get(v_, [])))
        e["lun"] = {v_: c for v_, c in lun.items() if any(c)}
        # gerund of prefixed verbs (lyap): derive with the prefix ā and strip it; vowel-initial roots merge with ā, so skip them
        try:
            vowel_initial = root[0] in "aAiIuUfFxXeEoO"
            pre, strip = (("sam", ("sam", "saM", "saY", "saR", "saN", "san")) if vowel_initial else ("A", ("A",)))
            lp = avyaya(Dhatu.mula(aup, gana, prefixes=[pre]), Krt.ktvA)
            if lp:
                vs = []
                for x in lp.split("|"):
                    for st in strip:
                        if x.startswith(st) and not x.endswith("tvA"):
                            r_ = x[len(st):]
                            if r_ and r_ not in vs and (not vowel_initial or r_[0] in "aAiIuUfFxXeEoO"):
                                vs.append(r_)
                            break
                if vs:
                    e["lyap"] = "|".join(vs)
        except Exception:
            pass
        # perfect
        lit = {"P": [], "A": []}
        for pn in PERSONS:
            cell = tin(d, Lakara.Lit, pn)
            for v in ("P", "A"):
                lit[v].append("|".join(cell.get(v, [])))
        e["lit"] = {v: c for v, c in lit.items() if any(c)}
        return e
    except Exception as ex:  # a few roots are not derivable; they are simply left out
        print("skip", code, aup, type(ex).__name__, str(ex)[:60], file=sys.stderr)
        return None


def main():
    rows = ensure_tsv()
    entries, seen = [], set()
    for code, aup, artha in rows:
        e = build_entry(code, aup, artha)
        if e:
            entries.append(e)
    meta = {"source": "Dhatupatha (ashtadhyayi.com data) derived with vidyut-prakriya (MIT)",
            "count": len(entries)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "entries": entries}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} with {len(entries)} roots ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
