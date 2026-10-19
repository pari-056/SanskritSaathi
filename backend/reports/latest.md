# Sanskrit Saathi evaluation report

Engine lexicon: **403,374** indexed forms · **169** core stems/roots · verb layer: **2,229** roots, **394,485** finite forms, 12,254 participle/gerundive stems

## sa_ufal-ud-test.conllu
230 sentences · 1434 evaluated tokens (skipped: {'skipped_compound_member': 214, 'skipped_punct': 195}) · sha256[:16] `8e956d19e67e96d8`

### Morphological analysis

* Coverage (token has ≥1 analysis): **58.0%**
* Lemma recall: **50.8%** · full recall (lemma + features): **48.4%**
* Correct reading present among the analyses of covered tokens: **83.4%**
* Mean analyses per covered token (ambiguity): 2.07

| Type | Tokens | Coverage | Lemma recall | Full recall |
|---|---|---|---|---|
| adjective | 159 | 40.2% | 35.2% | 35.2% |
| gerund | 35 | 97.1% | 88.6% | 82.9% |
| indeclinable | 278 | 75.9% | 69.4% | 69.4% |
| infinitive | 5 | 80.0% | 80.0% | 80.0% |
| noun | 509 | 22.4% | 18.3% | 16.9% |
| participle | 101 | 82.2% | 73.3% | 54.5% |
| pronoun | 170 | 86.5% | 62.9% | 60.6% |
| verb-finite | 177 | 98.9% | 96.0% | 94.9% |

Most frequent uncovered lemmas (best candidates to add next):

नामन् (noun, 12), राजन् (noun, 12), यथा (indeclinable, 11), इदम् (adjective, 8), वरम् (indeclinable, 8), इदम् (pronoun, 7), तथा (indeclinable, 7), ब्राह्मण (noun, 6), चिद् (indeclinable, 6), दमनक (noun, 5), भद्र (noun, 5), भवत् (pronoun, 5), चिद् (adjective, 4), मध्य (noun, 4), पिङ्गलक (noun, 4), करटक (noun, 4), तावत् (indeclinable, 4), कौलिक (noun, 4), पञ्चतन्त्र (noun, 3), त्रि (adjective, 3), बहु (noun, 3), महत् (adjective, 3), अदस् (pronoun, 3), कथामुख (noun, 2), कुमार (noun, 2)

### Sandhi / segmentation

* Multiword tokens: 259
* **Sandhi rule recall** (rules rebuild the gold surface from gold parts): **92.3%**
* Splitter coverage: 10.8% · exact match: **7.7%**

Junctions where the rules disagree with the corpus: अ|म् ×2, आ|ए ×1, ं|ष् ×1, अ|ज् ×1, इ|अ ×1, म्|आ ×1, अ|प् ×1, र्|ए ×1, म्|भ् ×1, ह्|अ ×1, ः|उ ×1

## sa_vedic-ud-test.conllu
2709 sentences · 19600 evaluated tokens (skipped: {'skipped_compound_member': 1019}) · sha256[:16] `242546c3d6709c7c`

### Morphological analysis

* Coverage (token has ≥1 analysis): **51.3%**
* Lemma recall: **39.5%** · full recall (lemma + features): **38.4%**
* Correct reading present among the analyses of covered tokens: **74.9%**
* Mean analyses per covered token (ambiguity): 2.03

| Type | Tokens | Coverage | Lemma recall | Full recall |
|---|---|---|---|---|
| adjective | 1862 | 18.4% | 12.0% | 10.6% |
| gerund | 318 | 87.4% | 55.0% | 55.0% |
| indeclinable | 4350 | 63.1% | 51.9% | 51.9% |
| infinitive | 22 | 27.3% | 13.6% | 13.6% |
| noun | 6496 | 20.3% | 15.8% | 14.5% |
| participle | 824 | 72.3% | 56.0% | 44.7% |
| pronoun | 2742 | 81.5% | 55.4% | 55.1% |
| verb-other | 2986 | 84.6% | 69.2% | 69.2% |

Most frequent uncovered lemmas (best candidates to add next):

इदम् (pronoun, 257), वै (indeclinable, 209), अ (indeclinable, 95), एनद् (pronoun, 94), ह (indeclinable, 79), आ (indeclinable, 69), पशु (noun, 67), यथा (indeclinable, 60), इन्द्र (noun, 59), यज्ञ (noun, 53), उ (indeclinable, 50), सु (indeclinable, 49), ब्रह्मन् (noun, 48), राजन् (noun, 47), अप् (noun, 46), वाच् (noun, 45), स्वाहा (indeclinable, 44), रूप (noun, 44), मनस् (noun, 43), सोम (noun, 41), एतद् (pronoun, 39), गो (noun, 37), काम (noun, 37), दिव् (noun, 37), अभि (indeclinable, 37)

### Sandhi / segmentation

* Multiword tokens: 0
* This treebank has no multiword tokens, so sandhi is not evaluated on it.

## Verb forms vs. independent Pāṇinian oracle (vidyut)

* Forms compared: 387,621 · **agreement 99.96%** · engine-only 0 · oracle-only 144 · mismatches 30

* Participle declensions (śatṛ, ktavatu, kta; masculine and neuter): 34,944 cells compared, **95.0% identical**, 100.0% identical or a subset of the oracle's optional variants, 0 mismatches

## Change since baseline

| Metric | Before | After | Δ |
|---|---|---|---|
| sa_ufal-ud-test.conllu:morphology.coverage | 38.9% | 58.0% | +19.1% |
| sa_ufal-ud-test.conllu:morphology.lemma_recall | 33.7% | 50.8% | +17.1% |
| sa_ufal-ud-test.conllu:morphology.full_recall | 33.1% | 48.4% | +15.3% |
| sa_ufal-ud-test.conllu:morphology.precision_on_covered | 85.0% | 83.4% | -1.5% |
| sa_ufal-ud-test.conllu:segmentation.rule_recall | 91.9% | 92.3% | +0.4% |
| sa_ufal-ud-test.conllu:segmentation.splitter_coverage | 7.0% | 10.8% | +3.9% |
| sa_ufal-ud-test.conllu:segmentation.splitter_exact_match | 5.0% | 7.7% | +2.7% |
| sa_vedic-ud-test.conllu:morphology.coverage |  | 51.3% |  |
| sa_vedic-ud-test.conllu:morphology.lemma_recall |  | 39.5% |  |
| sa_vedic-ud-test.conllu:morphology.full_recall |  | 38.4% |  |
| sa_vedic-ud-test.conllu:morphology.precision_on_covered |  | 74.9% |  |
