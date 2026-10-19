"""Corpus-level evaluation: morphological coverage/accuracy and sandhi (segmentation) on UD treebanks."""
from __future__ import annotations
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

from .. import morph, sandhi
from ..translit import dev_to_slp1, slp1_to_dev
from .conllu import Sent, read_conllu
from .ud_map import analysis_matches, gold_kind, lemma_slp

SKIP_KINDS = {"punct", "compound-member"}


def _file_info(path: Path) -> dict:
    h = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return {"file": path.name, "sha256_16": h}


def _norm_surface(s: str) -> str:
    return dev_to_slp1(s).replace(" ", "").replace(".", "")


def evaluate_morphology(sents: list[Sent], analyzer: morph.MorphAnalyzer | None = None, top_oov: int = 40) -> dict:
    an = analyzer or morph.get_analyzer()
    cache: dict[str, morph.TokenAnalysis] = {}
    per = defaultdict(lambda: Counter())
    oov_lemmas: Counter = Counter()
    oov_forms: Counter = Counter()
    ambiguity: list[int] = []
    failures: list[dict] = []
    total = Counter()
    for s in sents:
        for t in s.tokens:
            kind = gold_kind(t)
            if kind in SKIP_KINDS:
                total["skipped_" + kind.replace("-", "_")] += 1
                continue
            if t.form not in cache:
                cache[t.form] = an.analyze(t.form)
            r = cache[t.form]
            c = per[kind]
            c["n"] += 1
            total["n"] += 1
            if r.analyses:
                c["covered"] += 1
                ambiguity.append(len(r.analyses))
                lem = feat = False
                for a in r.analyses:
                    l_ok, f_ok = analysis_matches(a, t)
                    lem |= l_ok
                    feat |= f_ok
                c["lemma"] += int(lem)
                c["full"] += int(feat)
                if not feat and len(failures) < 60:
                    failures.append({"form": t.form, "gold": f"{t.lemma} {t.upos} {t.feats}",
                                     "got": "; ".join(f"{a.lemma_label()} {a.features_en()}" for a in r.analyses[:3]),
                                     "lemma_ok": lem})
            else:
                oov_lemmas[(lemma_slp(t.lemma), kind)] += 1
                oov_forms[t.form] += 1

    def rate(c, k):
        return round(c[k] / c["n"], 4) if c["n"] else 0.0

    by_kind = {k: {"n": c["n"], "coverage": rate(c, "covered"), "lemma_recall": rate(c, "lemma"),
                   "full_recall": rate(c, "full")} for k, c in sorted(per.items())}
    n = total["n"]
    cov = sum(c["covered"] for c in per.values())
    lem = sum(c["lemma"] for c in per.values())
    full = sum(c["full"] for c in per.values())
    return {
        "tokens_evaluated": n,
        "skipped": {k: v for k, v in total.items() if k.startswith("skipped_")},
        "coverage": round(cov / n, 4) if n else 0.0,
        "lemma_recall": round(lem / n, 4) if n else 0.0,
        "full_recall": round(full / n, 4) if n else 0.0,
        "precision_on_covered": round(full / cov, 4) if cov else 0.0,
        "mean_analyses_per_covered_token": round(sum(ambiguity) / len(ambiguity), 2) if ambiguity else 0.0,
        "by_kind": by_kind,
        "top_oov_lemmas": [{"lemma": slp1_to_dev(l), "kind": k, "count": c} for (l, k), c in oov_lemmas.most_common(top_oov)],
        "example_failures": failures[:25],
    }


_STOPS = "kKgGcCjJwWqQtTdDpPbB"


def _norm(s: str) -> str:
    """Orthographic normalisation for comparing sandhi output with corpus spelling:
    no avagraha/spaces, and a nasal before a stop counts as anusvāra (saṃ-kṣepa = saṅkṣepa)."""
    s = s.replace("'", "").replace(" ", "")
    return re.sub(rf"[NYRnm](?=[{_STOPS}])", "M", s)


def rebuild_variants(parts: list[str], limit: int = 64) -> list[str]:
    """All strings the forward sandhi rules can produce for these words (alternatives included)."""
    states = [("", parts[0])]            # (text emitted so far, text of the left word not yet emitted)
    for nxt in parts[1:]:
        new = []
        for emitted, pending in states:
            full = pending if len(pending) > 1 else pending
            for j in sandhi.junctions(full, nxt[0]) or [sandhi.Junction(0, "", nxt[0], False, "none")]:
                d = min(j.drop, len(pending))
                new.append((emitted + pending[: len(pending) - d] + j.left_tail + j.right_head, nxt[1:]))
        states = new[:limit]
    return [e + p for e, p in states]


def _core(w: str) -> str:
    return w if w and w[-1] in "aAiIuUfFxXeEoO" else w[:-1]


def evaluate_segmentation(sents: list[Sent], analyzer: morph.MorphAnalyzer | None = None) -> dict:
    """Two tests on multiword tokens (surface string → gold word forms):

    * rule recall: can the forward sandhi rules (any listed alternative) rebuild the surface string
      from the gold parts? Independent of the lexicon, so it measures the rules themselves. The last
      two characters are not compared because they depend on the *next* word.
    * split accuracy: does the lexicon-constrained splitter return the gold segmentation?
    """
    an = analyzer or morph.get_analyzer()
    n = rule_ok = covered = split_ok = 0
    fails: list[dict] = []
    junction_fail: Counter = Counter()
    for s in sents:
        for m in s.mwts:
            parts = [p.form for p in m.parts]
            if len(parts) < 2:
                continue
            n += 1
            surface = dev_to_slp1(m.form).replace(".", "")
            slp_parts = [dev_to_slp1(p) for p in parts]
            ns = _norm(surface)
            cut = lambda x: x[:-2] if len(x) > 4 else x
            ok = any(cut(_norm(v)) == cut(ns) for v in rebuild_variants(slp_parts))
            rule_ok += int(ok)
            if not ok:
                if len(fails) < 40:
                    fails.append({"surface": m.form, "gold_parts": parts,
                                  "rules_give": slp1_to_dev(rebuild_variants(slp_parts)[0])})
                for a, b in zip(slp_parts, slp_parts[1:]):
                    piece = sandhi.join(a, b, spaced=False).text
                    if _norm(piece[max(0, len(a) - 3):]).split(b[1:] or " ")[0] not in ns:
                        junction_fail[(a[-1], b[0])] += 1
            splits = an.splitter.split(_norm(surface))
            if splits:
                covered += 1
                gold = [_core(w) for w in slp_parts]
                if any([_core(w) for w in sp] == gold for sp in splits):
                    split_ok += 1
    top_fail = [{"junction": f"{slp1_to_dev(a)}|{slp1_to_dev(b)}", "failures": c}
                for (a, b), c in junction_fail.most_common(12) if c]
    return {
        "multiword_tokens": n,
        "rule_recall": round(rule_ok / n, 4) if n else 0.0,
        "splitter_coverage": round(covered / n, 4) if n else 0.0,
        "splitter_exact_match": round(split_ok / n, 4) if n else 0.0,
        "splitter_precision_on_covered": round(split_ok / covered, 4) if covered else 0.0,
        "most_failing_junctions": top_fail,
        "example_rule_failures": fails[:15],
    }


def run_corpus_eval(paths: list[str | Path], top_oov: int = 40) -> dict:
    an = morph.get_analyzer()
    out = {"lexicon": {}, "corpora": {}}
    for p in paths:
        p = Path(p)
        sents = read_conllu(p)
        out["corpora"][p.name] = {
            **_file_info(p), "sentences": len(sents),
            "morphology": evaluate_morphology(sents, an, top_oov),
            "segmentation": evaluate_segmentation(sents, an),
        }
    vl = an.verb_layer.stats()
    out["lexicon"] = {"forms": an.n_forms, "stems": len(an.stems), **{f"verb_{k}": v for k, v in vl.items()}}
    return out
