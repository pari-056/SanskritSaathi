"""CLI:  python -m saathi.evaluation [fetch|corpus|oracle|all] ..."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from . import fetch as fetch_mod, report as rep
from .corpus import run_corpus_eval

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "reports"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="saathi.evaluation", description=__doc__)
    ap.add_argument("command", choices=["fetch", "corpus", "oracle", "all"])
    ap.add_argument("--ud", nargs="*", help="CoNLL-U files (default: the downloaded UD Sanskrit treebanks)")
    ap.add_argument("--out", default=str(DEFAULT_OUT / "latest.json"))
    ap.add_argument("--md", default=str(DEFAULT_OUT / "latest.md"))
    ap.add_argument("--baseline", help="earlier JSON report to compare against")
    ap.add_argument("--only-ufal", action="store_true", help="skip the Vedic treebank (non-classical forms)")
    a = ap.parse_args(argv)

    if a.command == "fetch":
        for p in fetch_mod.fetch_all(force=True):
            print("downloaded", p)
        return 0

    report: dict = {"lexicon": {"forms": 0, "stems": 0}, "corpora": {}}
    if a.command in ("corpus", "all"):
        paths = a.ud or [str(p) for p in fetch_mod.fetch_all()]
        if a.only_ufal:
            paths = [p for p in paths if "ufal" in Path(p).name]
        report = run_corpus_eval(paths)
    if a.command in ("oracle", "all"):
        from .oracle import run_oracle_eval, run_participle_eval
        report["oracle"] = run_oracle_eval()
        report["oracle"]["participles"] = run_participle_eval(300)
        if "lexicon" not in report or not report["lexicon"]["forms"]:
            from .. import morph
            an = morph.get_analyzer()
            report["lexicon"] = {"forms": an.n_forms, "stems": len(an.stems)}
    baseline = json.loads(Path(a.baseline).read_text(encoding="utf-8")) if a.baseline else None
    rep.save(report, a.out, a.md, baseline)
    print(Path(a.md).read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
