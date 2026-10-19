# Evaluating the Sanskrit engine

The harness measures the rule engine on **real annotated text** and checks generated verb forms against an **independent
derivation engine**, so improvements can be shown with numbers instead of examples.

```bash
cd backend
pip install -r requirements-dev.txt           # includes vidyut (oracle only)
python -m saathi.evaluation fetch              # downloads UD Sanskrit-UFAL and Sanskrit-Vedic (CC BY-SA 4.0)
python -m saathi.evaluation corpus --only-ufal # morphology + sandhi on classical text
python -m saathi.evaluation oracle             # generated verb forms and participles vs vidyut (about 1-2 min)
python -m saathi.evaluation all --baseline reports/baseline_v0.json   # everything, with before/after table
```
Reports are written to `backend/reports/latest.{json,md}`. `baseline_v0.*` is the engine before the verb work.
A regression gate in `tests/test_evaluation.py` fails if coverage or sandhi recall drops (it skips when the corpus is absent).

## What is measured
| Metric | Meaning |
|---|---|
| **Coverage** | share of evaluated tokens that get at least one analysis |
| **Lemma recall / full recall** | a returned analysis has the gold lemma / the gold lemma *and* every modelled feature (case, number, gender; tense, person, number, voice) |
| **Correct reading present (of covered)** | among covered tokens, how often a right reading is among the candidates (ambiguity is not penalised; see mean analyses per token) |
| **Sandhi rule recall** | the forward sandhi rules rebuild the corpus surface string from the gold word forms (independent of the lexicon) |
| **Splitter coverage / exact match** | the lexicon-constrained splitter proposes a split / returns the gold segmentation |
| **Oracle agreement** | rule-generated verb cells identical to vidyut's output |

Evaluated tokens exclude punctuation and compound members (which are bare stems). Verbal lemmas are compared loosely (vowel length,
final -a, prefix+root written as one word) because UD lemma conventions for verbs vary.

## Results (UD Sanskrit-UFAL, classical Pañcatantra text; 1,434 evaluated tokens)
| | Baseline (19 hand-typed roots) | Now (2,229 roots) |
|---|---|---|
| Token coverage | 38.9% | **58.0%** |
| Finite verbs: coverage | 32.8% | **98.9%** |
| Finite verbs: full recall* | 30.5% | **94.9%** |
| Gerunds: coverage | 17.1% | **97.1%** |
| Infinitives: coverage (5 tokens) | 40.0% | 80.0% |
| Participles: coverage | 17.8% | **82.2%** |
| Sandhi rule recall | 91.9% | **92.3%** (a real bug, t+j, was found and fixed) |
| Nouns: coverage | 15.7% | 22.4% (noun lexicon unchanged; the gain comes from participle/gerundive stems that happen to be nouns, e.g. सुता, जातः; some readings are coincidental, such as राज्यम् read as a gerundive) |

\* Coverage figures do not depend on the matcher. After the baseline was recorded, lemma matching for *verbs* was made more tolerant
(vowel length, final -a, prefix+root written as one word), so part of the lemma/full-recall gain is a measurement change, not an engine change.

Verb forms vs oracle: **387,621** rule-generated cells compared; **99.96%** identical, 144 cells where vidyut lists an extra optional
variant, 30 disagreements (21 are a vidyut inconsistency for √aj, 9 a vidyut missing-augment bug for the passive imperfect of √vas).
Participle declensions: 34,944 cells, 0 mismatches.

## Reading the numbers honestly
* **The remaining coverage gap is nouns and pronouns**, not verbs: consonant stems (rājan, nāman), names, idam/adas, indeclinables.
  `top_oov_lemmas` in the report ranks the missing lemmas.
* Some "misses" are annotation conventions (UD lemmas such as `पश्` for √dṛś, typos, compound members); the metric cannot see those.
* **Tuning risk:** general linguistic rules (che-ca, ṣatva, t+j assimilation, stacked prefixes, aorist, gerundives) were added after
  inspecting failures on the UFAL test file, which is the only classical file available. The lexicon itself was not selected from the
  corpus (all Dhātupāṭha roots were added). Still, treat the UFAL numbers as optimistic and re-measure on a held-out text.
* vidyut is itself imperfect software; agreement with it is strong evidence, not proof.
* Not yet covered: prefix-conditioned ātmanepada (saṃgacchate, adhīte, ādatte), benedictive and Vedic moods, nominal stems beyond
  a/ā/i/ī/u, compounds, and sandhi splitting of words outside the lexicon.
