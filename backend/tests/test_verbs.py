import random
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from saathi import morph, upasarga, verbs
from saathi.translit import dev_to_slp1, slp1_to_dev

AN = morph.get_analyzer()
BY_ROOT: dict = {}
for _v in verbs.load_verbs():
    BY_ROOT.setdefault((_v.root, _v.gana), _v)


def cells(root, gana, voice, tense):
    return [c[0] for c in verbs.forms(BY_ROOT[(root, gana)], voice, tense)]


def readings(word_dev: str):
    return {(a.root, a.pos, a.tense, a.person, a.number, a.voice, a.prefix, a.causative) for a in AN.analyze(word_dev).analyses}


# ---- generated paradigms: textbook forms ----------------------------------------------------
def test_parasmaipada_paradigm():
    assert cells("gam", 1, "act", "lat") == ["gacCati", "gacCataH", "gacCanti", "gacCasi", "gacCaTaH", "gacCaTa", "gacCAmi", "gacCAvaH", "gacCAmaH"]
    assert cells("gam", 1, "act", "lan")[:3] == ["agacCat", "agacCatAm", "agacCan"]
    assert cells("gam", 1, "act", "lot")[:4] == ["gacCatu", "gacCatAm", "gacCantu", "gacCa"]
    assert cells("gam", 1, "act", "vidhilin")[:3] == ["gacCet", "gacCetAm", "gacCeyuH"]
    assert cells("gam", 1, "act", "lrt")[0] == "gamizyati"


def test_atmanepada_paradigm():
    assert cells("laB", 1, "mid", "lat") == ["laBate", "laBete", "laBante", "laBase", "laBeTe", "laBaDve", "laBe", "laBAvahe", "laBAmahe"]
    assert cells("laB", 1, "mid", "lan") == ["alaBata", "alaBetAm", "alaBanta", "alaBaTAH", "alaBeTAm", "alaBaDvam", "alaBe", "alaBAvahi", "alaBAmahi"]
    assert cells("laB", 1, "mid", "lot") == ["laBatAm", "laBetAm", "laBantAm", "laBasva", "laBeTAm", "laBaDvam", "laBE", "laBAvahE", "laBAmahE"]
    assert cells("laB", 1, "mid", "vidhilin") == ["laBeta", "laBeyAtAm", "laBeran", "laBeTAH", "laBeyATAm", "laBeDvam", "laBeya", "laBevahi", "laBemahi"]


def test_passive_and_causative():
    assert cells("gam", 1, "pass", "lat")[0] == "gamyate"
    assert cells("kf", 8, "pass", "lat")[0] == "kriyate"
    assert cells("dA", 3, "pass", "lat")[0] == "dIyate"
    assert cells("gam", 1, "cau-act", "lat")[0] == "gamayati"
    assert cells("kf", 8, "cau-act", "lat")[0] == "kArayati"
    assert cells("gam", 1, "pass", "lan")[0] == "agamyata"


def test_augment_rules():
    assert verbs.augment("gacCa") == "agacCa"
    assert verbs.augment("Ikza") == "Ekza"           # a + ī → ai
    assert verbs.augment("ucya") == "Ocya"
    assert verbs.augment("fcCa") == "ArcCa"
    assert verbs.augment("Cada") == "acCada"         # che ca


def test_listed_forms():
    assert "jagAma" in cells("gam", 1, "act", "lit")
    assert "baBUva" in cells("BU", 1, "act", "lit")
    assert "cakAra" in cells("kf", 8, "act", "lit")
    assert "agamat" in cells("gam", 1, "act", "lun")
    assert cells("as", 2, "act", "lat")[:3] == ["asti", "staH", "santi"]
    assert cells("kf", 8, "act", "lat")[2] == "kurvanti"
    assert cells("Sru", 1, "act", "lat")[0] == "SfRoti"        # irregular present of a gaṇa-1 root


# ---- analysis ---------------------------------------------------------------------------------
@pytest.mark.parametrize("word,expect", [
    ("गच्छति", ("gam", "verb", "lat", 3, "sg", "act", "", False)),
    ("लभन्ते", ("laB", "verb", "lat", 3, "pl", "mid", "", False)),
    ("गम्यते", ("gam", "verb", "lat", 3, "sg", "pass", "", False)),
    ("गमयति", ("gam", "verb", "lat", 3, "sg", "act", "", True)),
    ("जगाम", ("gam", "verb", "lit", 3, "sg", "act", "", False)),
    ("आगच्छति", ("gam", "verb", "lat", 3, "sg", "act", "A", False)),
    ("उपागच्छत्", ("gam", "verb", "lan", 3, "sg", "act", "upa", False)),
    ("व्यगच्छत्", ("gam", "verb", "lan", 3, "sg", "act", "vi", False)),
    ("संगच्छन्ति", ("gam", "verb", "lat", 3, "pl", "act", "sam", False)),
])
def test_finite_and_prefixed_analysis(word, expect):
    assert expect in readings(word), (word, sorted(readings(word))[:6])


def test_prefix_forms_round_trip():
    assert ("pra", "praRayati") == ("pra", upasarga.join("pra", "nayati"))
    assert upasarga.join("aBi", "sTAya", root="sTA") == "aBizWAya"
    assert upasarga.join("ud", "gacCati") == "udgacCati"
    assert upasarga.join("upa", "agacCat") == "upAgacCat"
    assert upasarga.join("A", "fcCati") == "ArcCati"


def test_prefix_satva_and_natva_recognised():
    assert any(a.root == "nI" and a.prefix == "pra" for a in AN.analyze("प्रणयति").analyses)
    assert any(a.root == "sTA" and a.prefix == "anu" for a in AN.analyze("अनुष्ठीयते").analyses), "ṣatva after anu-"
    assert any(a.root == "sTA" and a.pos == "gerund" and a.prefix == "aBi" for a in AN.analyze("अभिष्ठाय").analyses)


def test_participles_gerunds_infinitives():
    pos = lambda w: {(a.root, a.pos) for a in AN.analyze(w).analyses}
    assert ("gam", "ppp") in pos("गतः") and ("gam", "ktavatu") in pos("गतवान्")
    assert ("gam", "prap") in pos("गच्छन्") and ("gam", "gerund") in pos("गत्वा") and ("gam", "infinitive") in pos("गन्तुम्")
    assert ("gam", "gdv") in pos("गन्तव्यः") and ("gam", "gdv") in pos("गमनीयः")
    assert ("laB", "pmp") in pos("लभमानः")
    assert ("gam", "gerund") in pos("आगम्य")
    assert ("dfS", "infinitive") in pos("द्रष्टुम्")


def test_unrelated_words_are_not_hallucinated():
    assert not AN.analyze("क्ष्ज्ञ").analyses
    assert not AN.analyze("ब्लोग").analyses


def test_generated_forms_analyse_back_to_their_source():
    rng = random.Random(0)
    fidx = verbs.finite_index()
    surfaces = rng.sample(sorted(fidx), 400)
    for s in surfaces:
        want = {verbs.load_verbs()[verbs.unpack(c)[0]].root for c in fidx[s]}
        got = {a.root for a in AN.analyze(slp1_to_dev(s)).analyses}
        assert want & got, (s, want, got)


# ---- independent oracle (optional dependency) --------------------------------------------------------
vidyut = pytest.importorskip("vidyut", reason="pip install vidyut to run the oracle checks")


def test_generated_forms_agree_with_oracle():
    from saathi.evaluation.oracle import run_oracle_eval
    r = run_oracle_eval(limit=120)
    assert r["compared"] > 5000
    assert r["agree_or_subset"] >= 0.995, r["examples"][:5]
    assert r["mismatches"] <= 5


def test_participle_declensions_agree_with_oracle():
    from saathi.evaluation.oracle import run_participle_eval
    r = run_participle_eval(120)
    assert r["mismatches"] == 0, r["examples"][:3]
