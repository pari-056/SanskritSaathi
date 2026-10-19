import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from saathi.evaluation import report
from saathi.evaluation.conllu import read_conllu
from saathi.evaluation.corpus import evaluate_morphology, evaluate_segmentation, rebuild_variants
from saathi.evaluation.fetch import DEFAULT_DIR

SAMPLE = """# sent_id = t1
# text = रामो गच्छति।
1\tरामः\tराम\tPROPN\t_\tCase=Nom|Gender=Masc|Number=Sing\t2\tnsubj\t_\t_
2\tगच्छति\tगम्\tVERB\t_\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t0\troot\t_\t_
3\t।\t।\tPUNCT\t_\t_\t2\tpunct\t_\t_

# sent_id = t2
# text = अज्ञातशब्दः
1-2\tरामोऽस्ति\t_\t_\t_\t_\t_\t_\t_\t_
1\tरामः\tराम\tPROPN\t_\tCase=Nom|Gender=Masc|Number=Sing\t0\troot\t_\t_
2\tअस्ति\tअस्\tAUX\t_\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t1\tcop\t_\t_
3\tज्ञान्ज्ञः\tज्ञान्ज्ञ\tNOUN\t_\tCase=Nom|Gender=Masc|Number=Sing\t0\troot\t_\t_

"""


@pytest.fixture()
def sample(tmp_path):
    p = tmp_path / "s.conllu"
    p.write_text(SAMPLE, encoding="utf-8")
    return read_conllu(p)


def test_conllu_reader(sample):
    assert len(sample) == 2
    s = sample[0]
    assert [t.form for t in s.tokens] == ["रामः", "गच्छति", "।"]
    assert s.tokens[1].feats["Tense"] == "Pres"
    m = sample[1].mwts[0]
    assert m.form == "रामोऽस्ति" and [p.form for p in m.parts] == ["रामः", "अस्ति"]


def test_morphology_metrics_on_tiny_corpus(sample):
    r = evaluate_morphology(sample)
    assert r["tokens_evaluated"] == 5                        # punctuation is skipped
    assert r["coverage"] == pytest.approx(4 / 5, abs=1e-3)     # the made-up word is not covered
    assert r["full_recall"] == pytest.approx(4 / 5, abs=1e-3)
    assert r["by_kind"]["verb-finite"]["full_recall"] == 1.0
    assert r["top_oov_lemmas"][0]["kind"] == "noun"


def test_rebuild_variants_include_alternatives():
    assert "yAvajjIvaM" in rebuild_variants(["yAvat", "jIvaM"])
    assert any(v.startswith("evaYca") for v in rebuild_variants(["evam", "ca"]))


def test_segmentation_metrics_run(sample):
    r = evaluate_segmentation(sample)
    assert r["multiword_tokens"] == 1
    assert r["rule_recall"] == 1.0                          # रामः + अस्ति → रामोऽस्ति


def test_report_comparison_and_markdown():
    base = {"lexicon": {"forms": 1, "stems": 1}, "corpora": {"c": {"sentences": 1, "sha256_16": "x",
            "morphology": {"coverage": .4, "lemma_recall": .3, "full_recall": .3, "precision_on_covered": .8, "tokens_evaluated": 10,
                           "skipped": {}, "mean_analyses_per_covered_token": 1, "by_kind": {}, "top_oov_lemmas": []},
            "segmentation": {"rule_recall": .9, "splitter_coverage": .1, "splitter_exact_match": .05, "multiword_tokens": 3,
                             "most_failing_junctions": []}}}}
    import copy
    new = copy.deepcopy(base)
    new["corpora"]["c"]["morphology"]["coverage"] = .6
    rows = {r["metric"]: r for r in report.compare(new, base)}
    assert rows["c:morphology.coverage"]["delta"] == pytest.approx(0.2)
    assert "Change since baseline" in report.to_markdown(new, base)


# ---- regression gate on the real treebank (skipped when the corpus has not been downloaded) ------------------
UFAL = DEFAULT_DIR / "sa_ufal-ud-test.conllu"


@pytest.mark.skipif(not UFAL.exists(), reason="run: python -m saathi.evaluation fetch")
def test_real_corpus_regression_gate():
    sents = read_conllu(UFAL)
    m = evaluate_morphology(sents)
    s = evaluate_segmentation(sents)
    assert m["coverage"] >= 0.55
    assert m["by_kind"]["verb-finite"]["coverage"] >= 0.95
    assert m["by_kind"]["verb-finite"]["full_recall"] >= 0.90
    assert m["by_kind"]["gerund"]["coverage"] >= 0.90
    assert s["rule_recall"] >= 0.90
