from __future__ import annotations
import json
from pathlib import Path

HEADLINE = [("morphology", "coverage"), ("morphology", "lemma_recall"), ("morphology", "full_recall"),
            ("morphology", "precision_on_covered"), ("segmentation", "rule_recall"),
            ("segmentation", "splitter_coverage"), ("segmentation", "splitter_exact_match")]


def headline(report: dict) -> dict:
    out = {}
    for corpus, r in report["corpora"].items():
        for sec, key in HEADLINE:
            if sec == "segmentation" and not r[sec].get("multiword_tokens"):
                continue                       # nothing to measure (e.g. the Vedic treebank has no multiword tokens)
            out[f"{corpus}:{sec}.{key}"] = r[sec][key]
    return out


def compare(new: dict, old: dict) -> list[dict]:
    a, b = headline(new), headline(old)
    return [{"metric": k, "before": b.get(k), "after": v, "delta": round(v - b[k], 4) if k in b else None}
            for k, v in a.items()]


def to_markdown(report: dict, baseline: dict | None = None) -> str:
    lx = report["lexicon"]
    extra = (f" · verb layer: **{lx['verb_roots']:,}** roots, **{lx['verb_finite_forms']:,}** finite forms, "
             f"{lx['verb_derived_stems']:,} participle/gerundive stems") if "verb_roots" in lx else ""
    lines = ["# Sanskrit Saathi evaluation report", "",
             f"Engine lexicon: **{lx['forms']:,}** indexed forms · **{lx['stems']:,}** core stems/roots{extra}", ""]
    for name, r in report["corpora"].items():
        m, s = r["morphology"], r["segmentation"]
        lines += [f"## {name}", f"{r['sentences']} sentences · {m['tokens_evaluated']} evaluated tokens "
                  f"(skipped: {m['skipped']}) · sha256[:16] `{r['sha256_16']}`", "",
                  "### Morphological analysis", "",
                  f"* Coverage (token has ≥1 analysis): **{m['coverage']:.1%}**",
                  f"* Lemma recall: **{m['lemma_recall']:.1%}** · full recall (lemma + features): **{m['full_recall']:.1%}**",
                  f"* Correct reading present among the analyses of covered tokens: **{m['precision_on_covered']:.1%}**",
                  f"* Mean analyses per covered token (ambiguity): {m['mean_analyses_per_covered_token']}", "",
                  "| Type | Tokens | Coverage | Lemma recall | Full recall |", "|---|---|---|---|---|"]
        for k, v in m["by_kind"].items():
            lines.append(f"| {k} | {v['n']} | {v['coverage']:.1%} | {v['lemma_recall']:.1%} | {v['full_recall']:.1%} |")
        lines += ["", "Most frequent uncovered lemmas (best candidates to add next):", ""]
        lines.append(", ".join(f"{o['lemma']} ({o['kind']}, {o['count']})" for o in m["top_oov_lemmas"][:25]) or "none")
        lines += ["", "### Sandhi / segmentation", "",
                  f"* Multiword tokens: {s['multiword_tokens']}",
                  ] + ([f"* **Sandhi rule recall** (rules rebuild the gold surface from gold parts): **{s['rule_recall']:.1%}**",
                        f"* Splitter coverage: {s['splitter_coverage']:.1%} · exact match: **{s['splitter_exact_match']:.1%}**", ""]
                       if s["multiword_tokens"] else ["* This treebank has no multiword tokens, so sandhi is not evaluated on it.", ""])
        if s["most_failing_junctions"]:
            lines.append("Junctions where the rules disagree with the corpus: " +
                         ", ".join(f"{j['junction']} ×{j['failures']}" for j in s["most_failing_junctions"]))
            lines.append("")
    if "oracle" in report:
        o = report["oracle"]
        lines += ["## Verb forms vs. independent Pāṇinian oracle (vidyut)", "",
                  f"* Forms compared: {o['compared']:,} · **agreement {o['agreement']:.2%}** · "
                  f"engine-only {o['engine_only']} · oracle-only {o['oracle_only']} · mismatches {o['mismatches']}", ""]
        if o.get("participles"):
            p_ = o["participles"]
            lines += [f"* Participle declensions (śatṛ, ktavatu, kta; masculine and neuter): {p_['compared']:,} cells compared, "
                      f"**{p_['agreement']:.1%} identical**, {p_['agree_or_subset']:.1%} identical or a subset of the oracle's optional variants, "
                      f"{p_['mismatches']} mismatches", ""]
    if baseline:
        lines += ["## Change since baseline", "", "| Metric | Before | After | Δ |", "|---|---|---|---|"]
        for row in compare(report, baseline):
            d = "" if row["delta"] is None else f"{row['delta']:+.1%}"
            b = "" if row["before"] is None else f"{row['before']:.1%}"
            lines.append(f"| {row['metric']} | {b} | {row['after']:.1%} | {d} |")
        lines.append("")
    return "\n".join(lines)


def save(report: dict, json_path: str | Path, md_path: str | Path | None = None, baseline: dict | None = None):
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if md_path:
        Path(md_path).write_text(to_markdown(report, baseline), encoding="utf-8")
