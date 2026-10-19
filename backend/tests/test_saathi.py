import random
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from saathi import llm, morph, practice, sandhi, selfcheck, tools
from saathi.syntax import analyze_sentence
from saathi.translit import dev_to_slp1, slp1_to_dev, convert, detect_script


# ---- transliteration -------------------------------------------------------
@pytest.mark.parametrize("t", ["रामः विद्यालयं गच्छति।", "संस्कृतम्", "कृष्ण", "श्रीमद्भगवद्गीता", "ऋषिः", "क्ष ज्ञ"])
def test_devanagari_roundtrip(t):
    assert slp1_to_dev(dev_to_slp1(t)) == t


def test_scripts():
    assert convert("rāmaḥ", "devanagari") == "रामः"
    assert convert("rAmaH", "iast") == "rāmaḥ"
    assert detect_script("rāma") == "iast" and detect_script("rAma") == "hk"


# ---- sandhi / morphology gold sets ------------------------------------------
def test_gold_sandhi():
    r = selfcheck.run_sandhi_eval()
    assert not r["failures"], r["failures"]


def test_gold_morphology():
    r = selfcheck.run_morph_eval()
    assert not r["failures"], r["failures"]


def test_natva_and_su():
    assert morph.decline("rAma", "a", "m")[(3, "sg")] == ["rAmeRa"]
    assert morph.decline("kfzRa", "a", "m")[(3, "sg")] == ["kfzRena"]  # retroflex N blocks natva
    assert morph.decline("hari", "i", "m")[(7, "pl")] == ["harizu"]


def test_split_roundtrip():
    an = morph.get_analyzer()
    assert ["rAmaH", "asti"] in an.splitter.split("rAmo'sti")
    assert ["tatra", "iti"] in an.splitter.split("tatreti")


# ---- syntax -----------------------------------------------------------------
def test_agreement_error_and_fix():
    sa = analyze_sentence("अहं गच्छति")
    assert any(i["severity"] == "error" and "गच्छामि" in i["suggestion"] for i in sa.issues)


def test_passive_participle_roles():
    sa = analyze_sentence("रामेण फलं खादितम्")
    roles = [t.role for t in sa.tokens]
    assert roles[0].startswith("kartā") and roles[1].startswith("karman")
    c = sa.tokens[2].chosen
    assert (c.case, c.number, c.gender) == (1, "sg", "n")  # participle agrees with फलम्, not masc. accusative


def test_clean_sentence_has_no_issues():
    assert analyze_sentence("रामः विद्यालयं गच्छति").issues == []


# ---- practice ---------------------------------------------------------------
def test_questions_are_answerable():
    rng = random.Random(0)
    for kind, gen in practice.GENERATORS.items():
        for _ in range(30):
            q = gen(rng)
            assert q.options[q.answer_idx]
            assert len(set(q.options)) == len(q.options)


# ---- Gemini layer with a fake client (no network) ---------------------------
class _Resp:
    def __init__(self, text):
        self.text, self.automatic_function_calling_history, self.parsed = text, [], None


class _Models:
    def __init__(self, text): self.text, self.kw = text, None
    def generate_content(self, **kw):
        self.kw = kw
        return _Resp(self.text)


class _Client:
    def __init__(self, text): self.models = _Models(text)


def test_chat_reply_builds_grounded_request():
    c = _Client("ok")
    msgs = [{"role": "assistant", "content": "hi"}, {"role": "user", "content": "रामः गच्छन्ति"}]
    res = llm.chat_reply(c, "gemini-3.8-flash", msgs, "Beginner", "Grammar", "English", use_tools=True)
    assert res.text == "ok"
    contents = c.models.kw["contents"]
    assert contents[0].role == "user"                       # leading assistant turn dropped
    assert "RULE-ENGINE NOTES" in contents[-1].parts[0].text  # analyzer context attached
    assert c.models.kw["config"].tools                        # verified tools exposed


def test_structured_analysis_and_crosscheck():
    js = ('{"devanagari":"रामः गच्छति","iast":"rāmaḥ gacchati","translation":"Rama goes.","sandhi_notes":[],'
          '"tokens":[{"surface":"रामः","lemma":"राम","part_of_speech":"noun","gloss":"Rama","features":"nom sg m","confidence":"high"},'
          '{"surface":"गच्छति","lemma":"चल्","part_of_speech":"verb","gloss":"goes","features":"","confidence":"high"},'
          '{"surface":"xyzzy","lemma":"xyzzy","part_of_speech":"noun","gloss":"?","features":"","confidence":"low"}],'
          '"syntax_notes":[],"ambiguities":[],"learner_tip":"tip"}')
    parsed, checks = llm.analyze_sentence_ai(_Client(js), "gemini-3.8-flash", "रामः गच्छति", "Beginner", "English")
    assert [c.verdict for c in checks[:2]] == ["verified", "disagrees"]


def test_friendly_error_hides_key():
    class E(Exception):
        code = 403
        message = "API key not valid: AIza-SECRET"
    assert "AIza" not in llm.friendly_error(E())


def test_tools_never_raise():
    for f, args in [(tools.analyze_sanskrit_word, ("???",)), (tools.sandhi_join, ("", "x")),
                    (tools.get_paradigm, ("nonexistent",)), (tools.transliterate, ("a", "klingon"))]:
        assert isinstance(f(*args), dict)
