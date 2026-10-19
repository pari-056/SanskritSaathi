"""Verb analysis layer: turns the verb engine (verbs.py), participles and prefixes into Analysis objects."""
from __future__ import annotations
from dataclasses import replace
from functools import lru_cache

from . import participles, upasarga, verbs
from .morph import Analysis, NUM_EN
from .translit import slp1_to_dev

# English glosses for the core roots (matched by root and gaṇa so homonymous roots keep their own meaning)
CORE = {
    ("gam", 1): ("go", False), ("paW", 1): ("read, recite", True), ("liK", 6): ("write", True),
    ("KAd", 1): ("eat", True), ("vad", 1): ("speak, say", True), ("BU", 1): ("be, become", False),
    ("pA", 1): ("drink", True), ("dfS", 1): ("see", True), ("sTA", 1): ("stand", False), ("pac", 1): ("cook", True),
    ("nI", 1): ("lead, carry", True), ("smf", 1): ("remember", True), ("vas", 1): ("dwell, live", False),
    ("has", 1): ("laugh", False), ("cal", 1): ("move, walk", False), ("DAv", 1): ("run", False),
    ("praC", 6): ("ask", True), ("as", 2): ("be, exist", False), ("kf", 8): ("do, make", True),
    ("dA", 3): ("give", True), ("jYA", 9): ("know", True), ("han", 2): ("strike, kill", True),
    ("Sru", 1): ("hear", True), ("i", 2): ("go", False), ("yA", 2): ("go, travel", False),
    ("vac", 2): ("speak", True), ("BF", 1): ("bear, carry", True), ("kram", 1): ("step, go", False),
    ("jan", 4): ("be born", False), ("man", 4): ("think", True), ("labh", 1): ("obtain", True),
    ("laB", 1): ("obtain", True), ("sev", 1): ("serve", True), ("vft", 1): ("exist, turn", False),
    ("cint", 10): ("think", True), ("kaT", 10): ("tell", True), ("pUj", 10): ("worship", True),
    ("rakz", 1): ("protect", True), ("tyaj", 1): ("abandon", True), ("yaj", 1): ("sacrifice, worship", True),
    ("Sru", 5): ("hear", True), ("dA", 1): ("give", True),
}
VERB_PADA_LABEL = {"act": "active", "mid": "middle", "pass": "passive", "cau-act": "causative", "cau-mid": "causative (middle)"}
TENSE_IDS = verbs.TENSES


def _gloss(v: verbs.Verb) -> tuple[str, bool | None]:
    if (v.root, v.gana) in CORE:
        g, tr = CORE[(v.root, v.gana)]
        return g, tr
    return ("‘" + slp1_to_dev(v.meaning) + "’ (Dhātupāṭha)") if v.meaning else "", None


def _merge(items: list[Analysis]) -> list[Analysis]:
    """One analysis per distinct grammatical reading; glosses of homonymous roots are joined."""
    seen: dict[tuple, Analysis] = {}
    for a in items:
        k = (a.lemma, a.root, a.pos, a.case, a.number, a.gender, a.person, a.tense, a.voice, a.causative, a.prefix, a.surface)
        if k in seen:
            old = seen[k]
            if a.gloss and a.gloss not in old.gloss:
                g = (old.gloss + " / " + a.gloss) if old.gloss else a.gloss
                seen[k] = replace(old, gloss=g[:160])
            if old.transitive is None and a.transitive is not None:
                seen[k] = replace(seen[k], transitive=a.transitive)
        else:
            seen[k] = a
    return list(seen.values())


class VerbLayer:
    def __init__(self):
        self.verbs = verbs.load_verbs()
        self.fidx = verbs.finite_index()
        self.plain: dict[str, list[tuple[int, str]]] = {}    # ktvA / tumun surface → (verb idx, kind)
        self.lyap: dict[str, list[int]] = {}
        self.stems: dict[str, list[tuple[int, str]]] = {}    # derived adjective stems → (verb idx, kind)
        for v in self.verbs:
            for f in v.ktvA:
                self.plain.setdefault(f, []).append((v.idx, "gerund"))
            for f in v.tumun:
                self.plain.setdefault(f, []).append((v.idx, "infinitive"))
            for f in v.lyap:
                self.lyap.setdefault(f, []).append(v.idx)
            for k in v.kta:
                self.stems.setdefault(k, []).append((v.idx, "kta"))
                self.stems.setdefault(k[:-1] + "avat", []).append((v.idx, "ktavatu"))
            for k in v.ckta:
                self.stems.setdefault(k, []).append((v.idx, "ckta"))
            for f in v.cktvA:
                self.plain.setdefault(f, []).append((v.idx, "cgerund"))
            for f in v.ctumun:
                self.plain.setdefault(f, []).append((v.idx, "cinfinitive"))
            for f in v.clyap:
                self.lyap.setdefault(f, []).append(~v.idx)      # ~idx marks the causative
            for k in v.prap:
                self.stems.setdefault(k, []).append((v.idx, "Satf"))
            for k in v.pmp:
                self.stems.setdefault(k, []).append((v.idx, "SAnac"))
            for k in v.tavya:
                self.stems.setdefault(k, []).append((v.idx, "tavya"))
            for k in v.anIya:
                self.stems.setdefault(k, []).append((v.idx, "anIya"))
            for k in v.ya:
                self.stems.setdefault(k, []).append((v.idx, "ya"))
            if not v.athematic:                       # thematic participles are built by rule
                st = v.pres.get("P")
                for s in (st.split("|") if st else []):
                    if s.endswith("a"):
                        self.stems.setdefault(s[:-1] + "at", []).append((v.idx, "Satf"))
                st = v.pres.get("A")
                for s in (st.split("|") if st else []):
                    if s.endswith("a"):
                        self.stems.setdefault(s[:-1] + "amAna", []).append((v.idx, "SAnac"))

    # -- builders ------------------------------------------------------------------
    def _verb_analysis(self, surface: str, v: verbs.Verb, lemma: str | None = None, **kw) -> Analysis:
        g, tr = _gloss(v)
        return Analysis(surface, lemma or v.root, kw.pop("pos"), g, root=v.root, transitive=tr, **kw)

    def finite(self, slp: str) -> list[Analysis]:
        out = []
        for code in self.fidx.get(slp, ()):
            idx, vi, ti, pn = verbs.unpack(code)
            v = self.verbs[idx]
            voice = verbs.VOICES[vi]
            p, n = verbs.PN[pn]
            out.append(self._verb_analysis(slp, v, pos="verb", number=n, person=p, tense=verbs.TENSES[ti],
                                           voice=voice.replace("cau-", ""), causative=voice.startswith("cau")))
        return out

    def indeclinable(self, slp: str) -> list[Analysis]:
        out = []
        for i, kind in self.plain.get(slp, ()):
            cau = kind.startswith("c")
            out.append(self._verb_analysis(slp, self.verbs[i], pos=kind[1:] if cau else kind, causative=cau))
        return out

    @lru_cache(maxsize=4096)
    def _forms(self, kind: str, stem: str, fem_weak: bool):
        return participles.forms_for(kind, stem, fem_weak)

    def nominal(self, slp: str) -> list[Analysis]:
        n = len(slp)
        cands = set()
        for i in range(max(2, n - 9), n):
            pre = slp[:i]
            cands.update((pre, pre + "a", pre + "at"))
            if pre.endswith("ant") or pre.endswith("vant"):
                cands.add(pre[:-2] + "t")
        if slp.endswith("n"):
            cands.add(slp[:-1] + "t")
        if slp.endswith("An"):
            cands.add(slp[:-2] + "at")
        out = []
        pos_of = {"ckta": "ppp", "kta": "ppp", "ktavatu": "ktavatu", "Satf": "prap", "SAnac": "pmp", "tavya": "gdv", "anIya": "gdv", "ya": "gdv"}
        for st in cands:
            for idx, kind in self.stems.get(st, ()):
                v = self.verbs[idx]
                weak = v.gana == 6 and kind == "Satf"
                for (g, c, num), fs in self._forms(kind, st, weak).items():
                    if slp in fs:
                        out.append(self._verb_analysis(slp, v, lemma=st, pos=pos_of[kind], case=c, number=num, gender=g,
                                                       causative=kind == "ckta"))
        return out

    def base(self, slp: str) -> list[Analysis]:
        return _merge(self.finite(slp) + self.indeclinable(slp) + self.nominal(slp))

    def _plain_or_prefixed(self, slp: str, depth: int) -> list[Analysis]:
        items = self.finite(slp) + self.indeclinable(slp) + self.nominal(slp)
        for idx in self.lyap.get(slp, ()):
            cau = idx < 0
            items.append(self._verb_analysis(slp, self.verbs[~idx if cau else idx], pos="gerund", causative=cau))
        items = [a for a in items if a.pos != "gerund" or slp in self.lyap or depth == 0]
        if depth > 0:
            items += self.prefixed(slp, depth - 1, nested=True)
        return items

    def prefixed(self, slp: str, depth: int = 1, nested: bool = False) -> list[Analysis]:
        """Analyses of prefix + verb(-derived) word; up to depth+1 stacked prefixes. Sound by construction:
        the prefix join must rebuild the token exactly."""
        out = []
        for p, rest in upasarga.candidates(slp):
            for a in self._plain_or_prefixed(rest, depth):
                if a.pos == "gerund" and a.prefix == "" and rest not in self.lyap:
                    continue
                if not upasarga.verify(p, rest, slp, a.root):
                    continue
                pre = p + "-" + a.prefix if a.prefix else p
                out.append(replace(a, surface=slp, prefix=pre))
        return out if nested else _merge(out)

    # -- reporting -----------------------------------------------------------------------
    def stats(self) -> dict:
        return {"roots": len(self.verbs), "finite_forms": len(self.fidx), "derived_stems": len(self.stems)}
