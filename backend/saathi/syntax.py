"""Sentence-level analysis: agreement-based disambiguation, kāraka roles, learner-error checks.

This is a small *heuristic* layer on top of the morphological analyzer. It resolves
ambiguity only where agreement constraints decide it, and otherwise reports the
remaining ambiguity honestly instead of guessing.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .morph import Analysis, TokenAnalysis, get_analyzer, conjugate, CASE_EN, NUM_EN
from .translit import tokenize_devanagari, to_slp1, slp1_to_dev, detect_script, slp1_to_iast

NOMINAL = ("noun", "adj", "pron", "ppp", "ktavatu", "prap", "pmp", "gdv")

ROLE_BY_CASE = {
    2: ("karman", "object / goal (accusative)"),
    3: ("karaṇa", "instrument / means (instrumental)"),
    4: ("sampradāna", "recipient / purpose (dative)"),
    5: ("apādāna", "source / separation (ablative)"),
    6: ("sambandha", "relation, 'of' (genitive)"),
    7: ("adhikaraṇa", "location / time (locative)"),
    8: ("sambodhana", "address (vocative)"),
}


@dataclass
class TokenRole:
    token: str
    slp: str
    chosen: Analysis | None
    alternatives: list[Analysis]
    role: str = ""
    role_note: str = ""
    status: str = "unresolved"      # resolved | disambiguated | ambiguous | unresolved
    splits: list[list[str]] = field(default_factory=list)


@dataclass
class SentenceAnalysis:
    text: str
    tokens: list[TokenRole]
    predicate: TokenRole | None
    issues: list[dict]              # {"severity", "message", "suggestion"}
    notes: list[str]

    def to_dict(self) -> dict:
        def a2d(a: Analysis | None):
            if a is None:
                return None
            return {"surface": slp1_to_dev(a.surface), "lemma": a.lemma_display(), "pos": a.pos_label(),
                    "features": a.features_en(), "gloss": a.gloss}
        return {
            "text": self.text,
            "tokens": [{
                "token": t.token, "status": t.status, "role": t.role, "analysis": a2d(t.chosen),
                "other_readings": [a2d(a) for a in t.alternatives if a != t.chosen][:4],
                "possible_sandhi_splits": [[slp1_to_dev(w) for w in sp] for sp in t.splits[:3]],
            } for t in self.tokens],
            "issues": self.issues, "notes": self.notes,
        }


def _num_ok(a: Analysis, number: str) -> bool:
    return a.number == number


def analyze_sentence(text: str) -> SentenceAnalysis:
    an = get_analyzer()
    toks = tokenize_devanagari(text)
    if not toks and text.strip():
        # allow roman input
        script = detect_script(text)
        toks = [slp1_to_dev(to_slp1(w, script)) for w in text.replace("|", " ").replace(".", " ").split()]
    results: list[TokenAnalysis] = [an.analyze(t) for t in toks]
    roles = [TokenRole(r.token, r.slp, None, list(r.analyses), splits=r.splits) for r in results]
    issues: list[dict] = []
    notes: list[str] = []

    # ---- 1. find the predicate -----------------------------------------------------
    # With a wide verb lexicon many nouns also look like verb forms (rāmaḥ = √rā, 1pl). Prefer tokens that can
    # only be verbs; fall back to ambiguous ones only when there is no unambiguous finite verb.
    def only_verb(r):
        return bool(r.alternatives) and all(a.pos == "verb" for a in r.alternatives)
    strong = [i for i, r in enumerate(roles) if only_verb(r)]
    weak = [i for i, r in enumerate(roles) if not only_verb(r) and any(a.pos == "verb" for a in r.alternatives)]
    finite = strong or ([weak[-1]] if weak else [])
    if finite and not strong and any(t.pos in ("ppp",) for r in roles for t in r.alternatives):
        finite = []                         # ambiguous 'verb' readings but a participle predicate is available
    for i, r in enumerate(roles):           # on non-predicate tokens, nominal readings beat verb readings
        if i not in finite and any(a.pos != "verb" for a in r.alternatives):
            r.alternatives = [a for a in r.alternatives if a.pos != "verb"]
    ppp_idx = [i for i, r in enumerate(roles) if any(a.pos == "ppp" for a in r.alternatives)]
    pred_i = None
    verb_a: Analysis | None = None
    if finite:
        pred_i = finite[-1] if len(finite) == 1 else finite[-1]
        cands = [a for a in roles[pred_i].alternatives if a.pos == "verb"]
        verb_a = cands[0] if len(cands) == 1 else None
        roles[pred_i].alternatives = cands or roles[pred_i].alternatives
        if len(finite) > 1:
            notes.append("More than one finite verb found; treating the last as the main predicate.")
    elif ppp_idx:
        pred_i = ppp_idx[-1]

    # ---- 2. subject / agent selection -------------------------------------------------
    subj_i = None
    obj_i = None
    agent_i = None
    if pred_i is not None and roles[pred_i].alternatives and roles[pred_i].alternatives[0].pos == "verb":
        vcands = roles[pred_i].alternatives
        vnum = {a.number for a in vcands}
        vper = {a.person for a in vcands}
        noms = []
        for i, r in enumerate(roles):
            if i == pred_i:
                continue
            for a in r.alternatives:
                if a.pos in NOMINAL and a.case == 1:
                    ok_num = a.number in vnum
                    ok_per = (a.person in vper) if a.person else (3 in vper)
                    if ok_num and ok_per:
                        noms.append((i, a))
        # prefer pronoun/noun that agrees; first in sentence order
        if noms:
            subj_i = noms[0][0]
            strict = {i for i, _ in noms
                      if all(x.case == 1 for x in roles[i].alternatives if x.pos in NOMINAL)}
            if len(strict) > 1:
                notes.append("Several nominatives agree with the verb; the first was taken as subject.")
            roles[subj_i].chosen = noms[0][1]
            roles[subj_i].alternatives = [a for a in roles[subj_i].alternatives if a.case == 1] or roles[subj_i].alternatives
            roles[subj_i].role = "kartā"
            roles[subj_i].role_note = "agent / subject (nominative, agrees with the verb)"
        else:
            notes.append("No overt subject agrees with the verb; Sanskrit often leaves it implicit "
                         f"({'he/she/it' if 3 in vper else 'I/you'} from the verb ending).")
    elif pred_i is not None:  # participle predicate
        pa = [a for a in roles[pred_i].alternatives if a.pos == "ppp"]
        has_instrumental = any(any(a.case == 3 and a.pos in NOMINAL for a in r.alternatives)
                               for i, r in enumerate(roles) if i != pred_i)
        # transitivity is only known for the core roots; for others an instrumental agent suggests a passive participle
        transitive = any(a.transitive for a in pa) or (any(a.transitive is None for a in pa) and has_instrumental)
        for i, r in enumerate(roles):
            if i == pred_i:
                continue
            if any(a.pos in NOMINAL and a.case == 3 for a in r.alternatives) and transitive and agent_i is None:
                agent_i = i
                r.chosen = next(a for a in r.alternatives if a.case == 3)
                r.alternatives = [a for a in r.alternatives if a.case == 3]
                r.role = "kartā (via instrumental)"
                r.role_note = "agent of a passive/participial construction (kartari tṛtīyā)"
        for i, r in enumerate(roles):
            if i in (pred_i, agent_i):
                continue
            for a in r.alternatives:
                if a.pos in NOMINAL and a.case in (1, 2) and a.case == 1:
                    for p in pa:
                        if p.number == a.number and p.gender == a.gender:
                            subj_i = i
                            r.chosen = a
                            r.alternatives = [x for x in r.alternatives if x.case == 1] or r.alternatives
                            r.role = "karman (subject of passive)" if transitive else "kartā (agent of intransitive participle)"
                            r.role_note = "nominative agreeing with the participle in gender and number"
                            agreeing = [p for p in pa if p.case == 1 and p.number == a.number and p.gender == a.gender]
                            if agreeing:
                                roles[pred_i].alternatives = agreeing
                                roles[pred_i].chosen = agreeing[0]
                                roles[pred_i].role = "kriyā (participial predicate)"
                                roles[pred_i].status = "disambiguated"
                            break
                if subj_i == i:
                    break
        notes.append("Participle predicate (kta): for transitive verbs the agent is instrumental and the "
                     "nominative object agrees with the participle; for intransitive verbs the nominative is the agent.")

    # ---- 3. remaining tokens -----------------------------------------------------------
    for i, r in enumerate(roles):
        if r.chosen is not None:
            r.status = "disambiguated" if len(r.alternatives) > 1 else "resolved"
            continue
        if not r.alternatives:
            r.status = "unresolved"
            continue
        a_list = r.alternatives
        if pred_i == i:
            if len(a_list) == 1:
                r.chosen = a_list[0]
                r.status = "resolved"
                r.role = "kriyā (predicate)"
            else:
                r.chosen = a_list[0]
                r.status = "ambiguous"
                r.role = "kriyā (predicate)"
            continue
        # if a subject exists, a nom/acc-ambiguous neuter is read as accusative (object)
        pool = a_list
        if subj_i is not None or agent_i is not None:
            acc = [a for a in a_list if a.case == 2]
            nonnom = [a for a in a_list if a.case != 1]
            if acc and any(a.case == 1 for a in a_list):
                pool = nonnom
        elif pred_i is not None:
            pass
        r.alternatives = pool
        chosen = pool[0]
        r.chosen = chosen
        distinct = {(a.case, a.number, a.gender, a.lemma, a.pos) for a in pool}
        r.status = "resolved" if len(distinct) == 1 else "ambiguous"
        if chosen.pos == "indecl":
            r.role = "avyaya"
            r.role_note = chosen.gloss
        elif chosen.case in ROLE_BY_CASE:
            nm, desc = ROLE_BY_CASE[chosen.case]
            r.role, r.role_note = nm, desc
            if chosen.case == 2 and verb_a and verb_a.root == "gam":
                r.role_note = "goal of motion (accusative with a verb of going)"
        elif chosen.case == 1:
            r.role = "prathamā (nominative)"
            r.role_note = "nominative: subject, or predicate nominal"

    # ---- 4. learner-error checks ---------------------------------------------------------
    issues += _check_agreement(roles, pred_i, subj_i)
    for r in roles:
        if r.status == "unresolved":
            msg = f"'{r.token}' is not in the built-in lexicon."
            sugg = an.suggest(r.token)
            if r.splits:
                parts = " + ".join(slp1_to_dev(w) for w in r.splits[0])
                msg += f" It may be a sandhi compound: {parts}."
            issues.append({"severity": "info", "message": msg,
                           "suggestion": ("Did you mean: " + ", ".join(slp1_to_dev(s) for s in sugg)) if sugg else ""})
    if any(r.slp == "ca" for r in roles) and sum(1 for r in roles if r.chosen and r.chosen.case == 1) >= 2:
        notes.append("Coordinated subject with च: two subjects take a dual verb, three or more a plural verb.")
        notes = [n for n in notes if not n.startswith("No overt subject")]
    if any("agreement" in i["message"] for i in issues):
        notes = [n for n in notes if not n.startswith("No overt subject")]
    return SentenceAnalysis(text, roles, roles[pred_i] if pred_i is not None else None, issues, notes)


def _check_agreement(roles: list[TokenRole], pred_i, subj_i) -> list[dict]:
    out: list[dict] = []
    if pred_i is None or subj_i is not None:
        return out
    pred = roles[pred_i]
    if not pred.alternatives or pred.alternatives[0].pos != "verb":
        return out
    v = pred.alternatives[0]
    noms_n = sum(1 for i, r in enumerate(roles) if i != pred_i and any(a.case == 1 and a.pos in NOMINAL for a in r.alternatives))
    if any(r.slp == "ca" for r in roles) and noms_n >= 2:
        return out  # coordinated subject ("A and B"): the verb is dual/plural, so skip the singular-subject check
    for i, r in enumerate(roles):
        if i == pred_i or not r.alternatives:
            continue
        nominal = [a for a in r.alternatives if a.pos in NOMINAL]
        if not nominal or len(nominal) != len(r.alternatives):
            continue
        # only nominative / vocative readings: it cannot be an object or adjunct
        if not all(a.case in (1, 8) for a in nominal) or not any(a.case == 1 for a in nominal):
            continue
        a = next(x for x in nominal if x.case == 1)
        want_p = a.person or 3
        diffs = []
        if v.number != a.number:
            diffs.append(f"number ({NUM_EN[a.number]} subject vs {NUM_EN[v.number]} verb)")
        if v.person != want_p:
            diffs.append(f"person ({want_p} vs {v.person})")
        if not diffs:
            continue
        try:
            fix = conjugate(v.root, v.tense)[(want_p, a.number)]
        except KeyError:
            fix = None
        sev = "error" if all(x.case == 1 for x in nominal) else "warning"
        hedge = "" if sev == "error" else " (if it is the subject and not a vocative)"
        out.append({"severity": sev,
                    "message": f"Subject–verb agreement{hedge}: '{r.token}' and '{pred.token}' disagree in "
                               + " and ".join(diffs) + ".",
                    "suggestion": f"Use: {slp1_to_dev(fix)}" if fix else ""})
        break
    return out


def classify_error_free(text: str) -> bool:
    return not any(i["severity"] == "error" for i in analyze_sentence(text).issues)
